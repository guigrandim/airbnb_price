from pathlib import Path

import streamlit as st

from modeling.inference import load_artifact, predict_reference


ROOT_DIR = Path(__file__).resolve().parent
ARTIFACT_PATH = ROOT_DIR / "models" / "airbnb_amsterdam_price_v2.pkl"


@st.cache_resource(show_spinner=False)
def _load_model_artifact(artifact_path):
    """Carrega o pipeline uma vez e o reutiliza entre interações do Streamlit."""
    return load_artifact(artifact_path)


def _optional_number(label, key, minimum=None, maximum=None, step=1, help_text=None):
    if any(isinstance(value, float) for value in (minimum, maximum, step) if value is not None):
        minimum = float(minimum) if minimum is not None else None
        maximum = float(maximum) if maximum is not None else None
        step = float(step)
    else:
        minimum = int(minimum) if minimum is not None else None
        maximum = int(maximum) if maximum is not None else None
        step = int(step)
    return st.number_input(
        label,
        min_value=minimum,
        max_value=maximum,
        value=None,
        step=step,
        key=key,
        placeholder="Sem informação",
        help=help_text,
    )


def _format_eur(value):
    formatted = f"{value:,.2f}"
    formatted = formatted.replace(",", "_").replace(".", ",").replace("_", ".")
    return f"€ {formatted}"


def _boolean_field(label, key):
    choice = st.selectbox(label, ["Sim", "Não", "Sem informação"], key=key)
    return {"Sim": "t", "Não": "f", "Sem informação": None}[choice]


st.set_page_config(
    page_title="Preço de referência | Amsterdam",
    page_icon="⌂",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root { --canal: #18384a; --tijolo: #c76b4b; --papel: #f5f2ec; }
    .block-container { max-width: 1320px; padding-top: 2.2rem; }
    .hero { padding: 1.4rem 0 1.6rem 1.4rem; border-left: 5px solid var(--tijolo); }
    .hero h1 { color: var(--canal); font-family: Georgia, serif; font-size: 2.55rem; }
    .hero p { max-width: 690px; color: #45545b; font-size: 1.04rem; }
    .note { background: var(--papel); padding: 1rem 1.15rem; border-radius: 8px; }
    div[data-testid="stMetric"] { background: var(--papel); padding: .8rem; border-radius: 8px; }
    </style>
    <div class="hero">
      <h1>Preço de referência para seu anúncio</h1>
      <p>Uma estimativa baseada em anúncios de Amsterdam no snapshot de dezembro de 2018.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

artifact = None
try:
    artifact = _load_model_artifact(str(ARTIFACT_PATH))
except FileNotFoundError:
    st.error(
        "O modelo pickle não foi encontrado. Execute as células de exportação da Etapa 11 no notebook."
    )
except (ValueError, RuntimeError, AttributeError, ImportError) as error:
    st.error(f"Não foi possível carregar o modelo: {error}")

info_column, form_column = st.columns([0.8, 1.5], gap="large")

with info_column:
    st.subheader("Como interpretar")
    st.markdown(
        """
        <div class="note">
        O valor é uma referência indicativa para o snapshot histórico. Ele não estima
        o preço ótimo, reservas futuras ou receita causada por uma alteração.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    st.metric("MAPE no teste histórico", "25,98%")
    st.caption(
        "A faixa empírica teve cobertura menor entre anúncios caros e anúncios sem histórico de avaliações."
    )
    st.warning(
        "Use apenas para demonstração. O modelo e os dados são de 2018 e o teste histórico já havia sido observado no projeto."
    )
    st.caption("Pipeline V2 · LightGBM · snapshot de 06/12/2018")

with form_column:
    st.subheader("Dados do anúncio")
    st.caption("Preencha os campos conhecidos. Os opcionais em branco serão tratados pelo pipeline.")

    with st.form("listing_form"):
        st.markdown("**Imóvel**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            room_type_choice = st.selectbox(
                "Tipo de acomodação",
                ["Entire home/apt", "Private room", "Shared room", "Outro"],
                key="room_type_choice",
            )
            room_type = (
                st.text_input("Informe o tipo", key="room_type_other")
                if room_type_choice == "Outro"
                else room_type_choice
            )
        with col_b:
            property_type = st.text_input("Tipo do imóvel", value="Apartment")
        with col_c:
            accommodates = st.number_input(
                "Hóspedes comportados", min_value=1, max_value=100, value=2, step=1
            )

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            bedrooms = _optional_number("Quartos", "bedrooms", 0, 50, 1)
        with col_b:
            bathrooms = _optional_number("Banheiros", "bathrooms", 0, 50, 0.5)
        with col_c:
            beds = _optional_number("Camas", "beds", 0, 100, 1)

        st.markdown("**Localização**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            neighbourhood = st.text_input(
                "Bairro oficial", value="Centrum-West", help="Aceita categorias inéditas."
            )
        with col_b:
            latitude = _optional_number("Latitude", "latitude", -90, 90, 0.0001)
        with col_c:
            longitude = _optional_number("Longitude", "longitude", -180, 180, 0.0001)

        st.markdown("**Anfitrião**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            superhost = _boolean_field("Superhost", "host_is_superhost")
            host_since = st.text_input("Anfitrião desde (AAAA-MM-DD)", value="2015-01-01")
        with col_b:
            host_listings_count = _optional_number(
                "Anúncios do anfitrião", "host_listings_count", 0, 100000, 1
            )
            identity_verified = _boolean_field(
                "Identidade verificada", "host_identity_verified"
            )
        with col_c:
            calculated_host_listings_count = _optional_number(
                "Anúncios ativos do anfitrião", "calculated_host_listings_count", 0, 100000, 1
            )
            has_profile_pic = _boolean_field("Foto de perfil", "host_has_profile_pic")

        st.markdown("**Avaliações**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            number_of_reviews = _optional_number(
                "Avaliações totais", "number_of_reviews", 0, 1000000, 1
            )
            reviews_last_365d = _optional_number(
                "Avaliações nos últimos 12 meses", "reviews_last_365d", 0, 10000, 1
            )
        with col_b:
            reviews_per_month = _optional_number(
                "Avaliações por mês", "reviews_per_month", 0, 10000, 0.1
            )
            review_scores_rating = _optional_number(
                "Nota média (escala de 0 a 100)", "review_scores_rating", 0, 100, 1
            )
        with col_c:
            last_review_date = st.text_input(
                "Última avaliação (AAAA-MM-DD)",
                value="2018-11-15",
                help="Informe a data disponível no snapshot histórico.",
            )

        st.markdown("**Disponibilidade e regras**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            minimum_nights = _optional_number(
                "Mínimo de noites", "minimum_nights", 1, 10000, 1
            )
            instant_bookable = _boolean_field("Reserva instantânea", "instant_bookable")
        with col_b:
            maximum_nights = _optional_number(
                "Máximo de noites", "maximum_nights", 1, 10000, 1
            )
            availability_365 = _optional_number(
                "Noites disponíveis no calendário (0–365)", "availability_365", 0, 365, 1
            )
        with col_c:
            guests_included = _optional_number(
                "Hóspedes incluídos", "guests_included", 0, 100, 1
            )
            bed_type_choice = st.selectbox(
                "Tipo de cama", ["Real Bed", "Pull-out Sofa", "Futon", "Airbed", "Couch", "Outro"]
            )
            bed_type = (
                st.text_input("Informe o tipo de cama")
                if bed_type_choice == "Outro"
                else bed_type_choice
            )

        st.markdown("**Taxas e cancelamento**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            extra_people = _optional_number(
                "Taxa por hóspede extra (€)", "extra_people", 0, 10000, 1
            )
        with col_b:
            cleaning_fee = _optional_number(
                "Taxa de limpeza (€)", "cleaning_fee", 0, 10000, 1
            )
        with col_c:
            cancellation_choice = st.selectbox(
                "Política de cancelamento",
                ["flexible", "moderate", "strict_14_with_grace_period", "super_strict_60", "Outro"],
            )
            cancellation_policy = (
                st.text_input("Informe a política")
                if cancellation_choice == "Outro"
                else cancellation_choice
            )

        st.markdown("**Comparação opcional**")
        col_a, col_b = st.columns(2)
        with col_a:
            price_announced = _optional_number(
                "Preço anunciado atual (€)", "price_announced_eur", 0, 100000, 1
            )
        with col_b:
            scenario_nights = _optional_number(
                "Noites vendidas no cenário (0–365)",
                "scenario_nights",
                0,
                365,
                1,
                "Usado somente para uma conta ilustrativa com noites constantes.",
            )

        submitted = st.form_submit_button(
            "Calcular referência", type="primary", use_container_width=True
        )

if submitted:
    if artifact is None:
        st.error("O artefato do modelo está indisponível. Confira a exportação no notebook.")
    elif room_type_choice == "Outro" and not room_type.strip():
        st.error("Informe o tipo de acomodação.")
    elif bed_type_choice == "Outro" and not bed_type.strip():
        st.error("Informe o tipo de cama.")
    elif cancellation_choice == "Outro" and not cancellation_policy.strip():
        st.error("Informe a política de cancelamento.")
    else:
        listing_input = {
            "room_type": room_type,
            "property_type": property_type,
            "accommodates": accommodates,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "neighbourhood_cleansed": neighbourhood,
            "latitude": latitude,
            "longitude": longitude,
            "host_is_superhost": superhost,
            "host_since": host_since or None,
            "host_listings_count": host_listings_count,
            "number_of_reviews": number_of_reviews,
            "reviews_per_month": reviews_per_month,
            "review_scores_rating": review_scores_rating,
            "minimum_nights": minimum_nights,
            "maximum_nights": maximum_nights,
            "availability_365": availability_365,
            "instant_bookable": instant_bookable,
            "last_review_date": last_review_date or None,
            "reviews_last_365d": reviews_last_365d,
            "beds": beds,
            "bed_type": bed_type,
            "guests_included": guests_included,
            "extra_people": extra_people,
            "cleaning_fee": cleaning_fee,
            "cancellation_policy": cancellation_policy,
            "calculated_host_listings_count": calculated_host_listings_count,
            "host_identity_verified": identity_verified,
            "host_has_profile_pic": has_profile_pic,
        }
        try:
            result = predict_reference(artifact, listing_input)
            st.divider()
            st.subheader("Resultado para o snapshot histórico")
            if result["price_reference_eur"] is None:
                st.warning("O modelo não gerou uma referência positiva para estes dados.")
            else:
                result_left, result_right = st.columns([1, 1])
                with result_left:
                    st.metric("Preço de referência por noite", _format_eur(result["price_reference_eur"]))
                    st.caption(result["status"].capitalize())
                with result_right:
                    st.metric(
                        "Faixa empírica central de 90%",
                        f"{_format_eur(result['interval_lower_eur'])} – {_format_eur(result['interval_upper_eur'])}",
                    )
                    st.caption("A cobertura observada variou entre segmentos e não é uma garantia individual.")

                if price_announced is not None:
                    if price_announced <= 0:
                        st.error("O preço anunciado deve ser maior que zero para calcular a diferença.")
                    else:
                        gap_eur = result["price_reference_eur"] - price_announced
                        gap_pct = 100 * gap_eur / price_announced
                        gap_a, gap_b = st.columns(2)
                        gap_a.metric("Diferença por noite", _format_eur(gap_eur))
                        gap_b.metric("Diferença percentual", f"{gap_pct:.1f}%")
                        if scenario_nights is not None:
                            scenario_delta = gap_eur * scenario_nights
                            st.info(
                                f"Cenário bruto para o anfitrião: {scenario_nights:.0f} noites constantes "
                                f"resultariam em {_format_eur(scenario_delta)} de diferença de GMV. "
                                "Supõe aplicação integral do preço de referência e não inclui reação da demanda, "
                                "monetização ou custos. Não é receita do Airbnb nem retorno observado."
                            )
            st.caption(
                "A estimativa usa atributos do snapshot de 06/12/2018. Mudanças de mercado, oferta ou regulação desde então não são refletidas."
            )
        except ValueError as error:
            st.error(str(error))
