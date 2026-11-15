"""Transformação de entradas e inferência do modelo V2 de preços."""

from __future__ import annotations

import pickle
import platform
from datetime import date, datetime
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
from typing import Any, Mapping

import lightgbm
import numpy as np
import pandas as pd
import sklearn


FEATURE_COLUMNS = [
    "room_type",
    "property_type",
    "accommodates",
    "bedrooms",
    "bathrooms",
    "neighbourhood_cleansed",
    "latitude",
    "longitude",
    "host_is_superhost",
    "host_listings_count",
    "number_of_reviews",
    "reviews_per_month",
    "review_scores_rating",
    "minimum_nights",
    "maximum_nights",
    "availability_365",
    "instant_bookable",
    "host_tenure_years",
    "reviews_last_365d",
    "days_since_last_review",
    "has_review_history",
    "rating_missing",
    "review_rate_missing",
    "distance_to_geo_reference_km",
    "is_studio",
    "beds",
    "bed_type",
    "guests_included",
    "extra_people",
    "cleaning_fee",
    "cancellation_policy",
    "calculated_host_listings_count",
    "host_identity_verified",
    "host_has_profile_pic",
    "beds_per_guest",
    "bathrooms_per_guest",
]

CATEGORICAL_COLUMNS = {
    "room_type",
    "property_type",
    "neighbourhood_cleansed",
    "host_is_superhost",
    "instant_bookable",
    "bed_type",
    "cancellation_policy",
    "host_identity_verified",
    "host_has_profile_pic",
}


def _is_missing(value: Any) -> bool:
    """Verifica se um valor escalar representa ausência."""
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _as_number(value: Any, field_name: str) -> float:
    """Converte campos numéricos e preserva ausência para o pipeline."""
    if _is_missing(value) or value == "":
        return np.nan
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field_name} precisa ser numérico.") from error
    if not np.isfinite(number):
        raise ValueError(f"{field_name} precisa ser um número finito.")
    return number


def _as_date(value: Any, field_name: str) -> date | None:
    """Interpreta datas ISO e valores date/datetime opcionais."""
    if _is_missing(value) or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError as error:
        raise ValueError(f"{field_name} deve usar uma data válida no formato AAAA-MM-DD.") from error


def _as_category(value: Any) -> Any:
    """Preserva categorias conhecidas e inéditas, deixando vazios como nulos."""
    if _is_missing(value):
        return np.nan
    text = str(value).strip()
    return text if text else np.nan


def build_features(
    listing: Mapping[str, Any], manifest: Mapping[str, Any]
) -> pd.DataFrame:
    """Monta as 36 features aprovadas a partir de campos do anúncio."""
    features = manifest.get("features")
    if features != FEATURE_COLUMNS:
        raise ValueError("O manifesto não corresponde ao schema aprovado de 36 features.")

    snapshot = _as_date(manifest.get("snapshot_date"), "snapshot_date")
    reference = manifest.get("geographic_reference")
    if snapshot is None or reference is None or len(reference) != 2:
        raise ValueError("Manifesto sem snapshot ou referência geográfica válidos.")
    reference_latitude, reference_longitude = map(float, reference)

    numeric_source_fields = [
        "accommodates", "bedrooms", "bathrooms", "latitude", "longitude",
        "host_listings_count", "number_of_reviews", "reviews_per_month",
        "review_scores_rating", "minimum_nights", "maximum_nights",
        "availability_365", "reviews_last_365d", "beds", "guests_included",
        "extra_people", "cleaning_fee", "calculated_host_listings_count",
    ]
    numeric = {
        field: _as_number(listing.get(field), field)
        for field in numeric_source_fields
    }

    accommodates = numeric["accommodates"]
    if not np.isfinite(accommodates) or accommodates <= 0:
        raise ValueError("accommodates deve ser maior que zero.")

    host_since = _as_date(listing.get("host_since"), "host_since")
    last_review = _as_date(listing.get("last_review_date"), "last_review_date")
    if host_since is not None and host_since > snapshot:
        raise ValueError("host_since é posterior ao snapshot histórico.")
    if last_review is not None and last_review > snapshot:
        raise ValueError("last_review_date é posterior ao snapshot histórico.")
    recent_reviews = numeric["reviews_last_365d"]
    if np.isfinite(recent_reviews) and recent_reviews < 0:
        raise ValueError("reviews_last_365d não pode ser negativo.")
    if np.isfinite(recent_reviews) and recent_reviews > 0 and last_review is None:
        raise ValueError("Informe a última avaliação quando reviews_last_365d for maior que zero.")

    latitude = numeric["latitude"]
    longitude = numeric["longitude"]
    if np.isfinite(latitude) and not -90 <= latitude <= 90:
        raise ValueError("latitude deve estar entre -90 e 90 graus.")
    if np.isfinite(longitude) and not -180 <= longitude <= 180:
        raise ValueError("longitude deve estar entre -180 e 180 graus.")

    if np.isfinite(latitude) and np.isfinite(longitude):
        latitude_rad = radians(latitude)
        longitude_rad = radians(longitude)
        reference_latitude_rad = radians(reference_latitude)
        reference_longitude_rad = radians(reference_longitude)
        haversine = (
            sin((latitude_rad - reference_latitude_rad) / 2) ** 2
            + cos(latitude_rad)
            * cos(reference_latitude_rad)
            * sin((longitude_rad - reference_longitude_rad) / 2) ** 2
        )
        distance_km = 2 * 6371.0088 * asin(sqrt(min(1.0, max(0.0, haversine))))
    else:
        distance_km = np.nan

    bedrooms = numeric["bedrooms"]
    beds = numeric["beds"]
    bathrooms = numeric["bathrooms"]
    host_tenure = (
        (snapshot - host_since).days / 365.25 if host_since is not None else np.nan
    )
    days_since_last_review = (
        (snapshot - last_review).days if last_review is not None else np.nan
    )

    row = {
        "room_type": _as_category(listing.get("room_type")),
        "property_type": _as_category(listing.get("property_type")),
        "accommodates": accommodates,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "neighbourhood_cleansed": _as_category(
            listing.get("neighbourhood_cleansed")
        ),
        "latitude": latitude,
        "longitude": longitude,
        "host_is_superhost": _as_category(listing.get("host_is_superhost")),
        "host_listings_count": numeric["host_listings_count"],
        "number_of_reviews": numeric["number_of_reviews"],
        "reviews_per_month": numeric["reviews_per_month"],
        "review_scores_rating": numeric["review_scores_rating"],
        "minimum_nights": numeric["minimum_nights"],
        "maximum_nights": numeric["maximum_nights"],
        "availability_365": numeric["availability_365"],
        "instant_bookable": _as_category(listing.get("instant_bookable")),
        "host_tenure_years": host_tenure,
        "reviews_last_365d": recent_reviews,
        "days_since_last_review": days_since_last_review,
        "has_review_history": int(last_review is not None),
        "rating_missing": int(not np.isfinite(numeric["review_scores_rating"])),
        "review_rate_missing": int(not np.isfinite(numeric["reviews_per_month"])),
        "distance_to_geo_reference_km": distance_km,
        "is_studio": int(np.isfinite(bedrooms) and bedrooms == 0),
        "beds": beds,
        "bed_type": _as_category(listing.get("bed_type")),
        "guests_included": numeric["guests_included"],
        "extra_people": numeric["extra_people"],
        "cleaning_fee": numeric["cleaning_fee"],
        "cancellation_policy": _as_category(listing.get("cancellation_policy")),
        "calculated_host_listings_count": numeric[
            "calculated_host_listings_count"
        ],
        "host_identity_verified": _as_category(
            listing.get("host_identity_verified")
        ),
        "host_has_profile_pic": _as_category(listing.get("host_has_profile_pic")),
        "beds_per_guest": beds / accommodates if np.isfinite(beds) else np.nan,
        "bathrooms_per_guest": (
            bathrooms / accommodates if np.isfinite(bathrooms) else np.nan
        ),
    }
    frame = pd.DataFrame([[row[column] for column in features]], columns=features)
    for column in CATEGORICAL_COLUMNS:
        frame[column] = frame[column].astype(object)
    for column in set(features) - CATEGORICAL_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def load_artifact(path: str | Path) -> dict[str, Any]:
    """Carrega e confere o pickle versionado do projeto."""
    with Path(path).open("rb") as artifact_file:
        artifact = pickle.load(artifact_file)

    if not isinstance(artifact, dict) or not {"pipeline", "manifest"} <= set(artifact):
        raise ValueError("O pickle não contém pipeline e manifesto do modelo.")
    manifest = artifact["manifest"]
    if manifest.get("artifact_version") != "airbnb_amsterdam_price_v2":
        raise ValueError("Versão de artefato incompatível com o aplicativo.")
    if manifest.get("features") != FEATURE_COLUMNS:
        raise ValueError("A ordem de features no artefato não é compatível.")
    if list(artifact["pipeline"].feature_names_in_) != FEATURE_COLUMNS:
        raise ValueError("As features do pipeline divergem do manifesto.")
    if manifest.get("scikit_learn_version") != sklearn.__version__:
        raise RuntimeError("A versão local do scikit-learn diverge do artefato.")
    if manifest.get("lightgbm_version") != lightgbm.__version__:
        raise RuntimeError("A versão local do LightGBM diverge do artefato.")
    trained_python_major = manifest["python_version"].split(".")[0]
    if platform.python_version_tuple()[0] != trained_python_major:
        raise RuntimeError("A versão principal do Python diverge do artefato.")
    return artifact


def predict_reference(artifact: Mapping[str, Any], listing: Mapping[str, Any]) -> dict[str, Any]:
    """Gera referência indicativa e faixa empírica para um anúncio."""
    feature_frame = build_features(listing, artifact["manifest"])
    raw_prediction = float(artifact["pipeline"].predict(feature_frame)[0])
    if not np.isfinite(raw_prediction):
        raise ValueError("O modelo retornou uma previsão não finita.")

    lower_quantile, upper_quantile = artifact["manifest"][
        "residual_quantiles_05_95_eur"
    ]
    if raw_prediction <= 0:
        return {
            "prediction_raw_eur": raw_prediction,
            "price_reference_eur": None,
            "interval_lower_eur": None,
            "interval_upper_eur": None,
            "status": "sem referência positiva",
            "features": feature_frame,
        }

    return {
        "prediction_raw_eur": raw_prediction,
        "price_reference_eur": raw_prediction,
        "interval_lower_eur": max(0.0, raw_prediction + float(lower_quantile)),
        "interval_upper_eur": max(0.0, raw_prediction + float(upper_quantile)),
        "status": "referência indicativa",
        "features": feature_frame,
    }
