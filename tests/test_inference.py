import unittest
from pathlib import Path

import numpy as np

from modeling.inference import build_features, load_artifact, predict_reference


FEATURES = [
    "room_type", "property_type", "accommodates", "bedrooms", "bathrooms",
    "neighbourhood_cleansed", "latitude", "longitude", "host_is_superhost",
    "host_listings_count", "number_of_reviews", "reviews_per_month",
    "review_scores_rating", "minimum_nights", "maximum_nights", "availability_365",
    "instant_bookable", "host_tenure_years", "reviews_last_365d",
    "days_since_last_review", "has_review_history", "rating_missing",
    "review_rate_missing", "distance_to_geo_reference_km", "is_studio", "beds",
    "bed_type", "guests_included", "extra_people", "cleaning_fee",
    "cancellation_policy", "calculated_host_listings_count", "host_identity_verified",
    "host_has_profile_pic", "beds_per_guest", "bathrooms_per_guest",
]


def make_listing():
    return {
        "room_type": "Entire home/apt",
        "property_type": "Apartment",
        "accommodates": 4,
        "bedrooms": 2,
        "bathrooms": 1.5,
        "neighbourhood_cleansed": "Centrum-West",
        "latitude": 52.3702,
        "longitude": 4.8952,
        "host_is_superhost": "t",
        "host_since": "2014-02-17",
        "host_listings_count": 2,
        "number_of_reviews": 50,
        "reviews_per_month": 1.4,
        "review_scores_rating": 95,
        "minimum_nights": 2,
        "maximum_nights": 30,
        "availability_365": 100,
        "instant_bookable": "f",
        "last_review_date": "2018-11-15",
        "reviews_last_365d": 10,
        "beds": 3,
        "bed_type": "Real Bed",
        "guests_included": 2,
        "extra_people": 20,
        "cleaning_fee": 25,
        "cancellation_policy": "moderate",
        "calculated_host_listings_count": 2,
        "host_identity_verified": "t",
        "host_has_profile_pic": "t",
    }


def make_manifest():
    return {
        "features": FEATURES,
        "snapshot_date": "2018-12-06",
        "geographic_reference": (52.3544265, 4.9169995),
    }


class BuildFeaturesTests(unittest.TestCase):
    def test_builds_ordered_36_features_and_snapshot_derivations(self):
        frame = build_features(make_listing(), make_manifest())
        row = frame.iloc[0]

        self.assertEqual(list(frame.columns), FEATURES)
        self.assertEqual(frame.shape, (1, 36))
        self.assertAlmostEqual(row["host_tenure_years"], 1753 / 365.25)
        self.assertEqual(row["days_since_last_review"], 21)
        self.assertEqual(row["has_review_history"], 1)
        self.assertEqual(row["rating_missing"], 0)
        self.assertEqual(row["review_rate_missing"], 0)
        self.assertEqual(row["is_studio"], 0)
        self.assertAlmostEqual(row["beds_per_guest"], 0.75)
        self.assertAlmostEqual(row["bathrooms_per_guest"], 0.375)

    def test_preserves_missing_optional_values_and_marks_review_missingness(self):
        listing = make_listing()
        listing.update({
            "host_since": None,
            "last_review_date": None,
            "reviews_last_365d": 0,
            "reviews_per_month": None,
            "review_scores_rating": None,
            "latitude": None,
            "longitude": None,
        })

        row = build_features(listing, make_manifest()).iloc[0]

        self.assertTrue(np.isnan(row["host_tenure_years"]))
        self.assertTrue(np.isnan(row["days_since_last_review"]))
        self.assertEqual(row["has_review_history"], 0)
        self.assertEqual(row["rating_missing"], 1)
        self.assertEqual(row["review_rate_missing"], 1)
        self.assertTrue(np.isnan(row["distance_to_geo_reference_km"]))

    def test_accepts_unseen_categorical_values_for_pipeline_encoder(self):
        listing = make_listing()
        listing["property_type"] = "Space Capsule"
        listing["neighbourhood_cleansed"] = "Nieuwe Buurt"

        row = build_features(listing, make_manifest()).iloc[0]

        self.assertEqual(row["property_type"], "Space Capsule")
        self.assertEqual(row["neighbourhood_cleansed"], "Nieuwe Buurt")

    def test_rejects_dates_after_the_historical_snapshot(self):
        listing = make_listing()
        listing["last_review_date"] = "2018-12-07"

        with self.assertRaisesRegex(ValueError, "posterior ao snapshot"):
            build_features(listing, make_manifest())


class SavedModelInferenceTests(unittest.TestCase):
    def test_saved_pipeline_generates_reference_and_empirical_interval(self):
        project_root = Path(__file__).resolve().parents[1]
        artifact = load_artifact(
            project_root / "models" / "airbnb_amsterdam_price_v2.pkl"
        )

        result = predict_reference(artifact, make_listing())

        self.assertGreater(result["price_reference_eur"], 0)
        self.assertGreaterEqual(result["interval_lower_eur"], 0)
        self.assertGreater(result["interval_upper_eur"], result["interval_lower_eur"])
        self.assertEqual(list(result["features"].columns), FEATURES)

    def test_rejects_zero_accommodates_to_prevent_invalid_ratios(self):
        listing = make_listing()
        listing["accommodates"] = 0

        with self.assertRaisesRegex(ValueError, "accommodates deve ser maior que zero"):
            build_features(listing, make_manifest())


if __name__ == "__main__":
    unittest.main()
