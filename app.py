from pathlib import Path
import json

import streamlit as st
import altair as alt
import pandas as pd

from modeling.inference import load_artifact, predict_reference


ROOT_DIR = Path(__file__).resolve().parent
ARTIFACT_PATH = ROOT_DIR / "models" / "airbnb_amsterdam_price_l1.pkl"


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

# Aplica superfícies escuras e contraste consistente aos controles.
st.markdown("""
<style>
.stApp {background:#101820;color:#e8edf0;color-scheme:dark}
.block-container {max-width:1180px;padding-top:2rem}
[data-testid="stHeader"] {background:#101820}
h1,h2,h3,[data-testid="stWidgetLabel"],[data-testid="stMetricValue"] {color:#f1f5f7!important}
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] strong {color:#dce4e9}
[data-testid="stCaptionContainer"] p {color:#a8b8c5!important}
[data-testid="stForm"],[data-testid="stMetric"],[data-testid="stExpander"] {background:#19252f;border:1px solid #334553;border-radius:12px}
[data-testid="stForm"] {padding:1.2rem}
[data-testid="InputInstructions"] {display:none!important}
[data-testid="stMetric"] {padding:1rem}
input,textarea,[data-baseweb="select"] > div {background:#223340!important;color:#f1f5f7!important;-webkit-text-fill-color:#f1f5f7!important}
input::placeholder {color:#9aaebd!important;-webkit-text-fill-color:#9aaebd!important}
[data-baseweb="popover"],[role="listbox"] {background:#223340!important;color:#f1f5f7!important}
[data-testid="stFormSubmitButton"] button {background:#d99662;color:#101820;border:0;font-weight:600}
[data-testid="stFormSubmitButton"] button p {color:#101820!important}
.hero h1 {font-family:Georgia,serif;font-size:2.5rem;line-height:1.15}
.hero p {max-width:600px;color:#a8b8c5}
</style>
""", unsafe_allow_html=True)
hero_text, hero_image = st.columns([1.5, 1], vertical_alignment="center")
with hero_text:
    st.markdown('<div class="hero"><h1>Encontre uma referência para sua diária</h1><p>Veja como o preço da reserva se compara a imóveis com características semelhantes em Amsterdam.</p></div>', unsafe_allow_html=True)
    st.caption("Demonstração com preços de dezembro de 2018")
with hero_image:
    banner_path = ROOT_DIR / "assets" / "amsterdam-night.png"
    if banner_path.exists():
        st.image(str(banner_path), width="stretch")

artifact = None
try:
    artifact = _load_model_artifact(str(ARTIFACT_PATH))
except FileNotFoundError:
    st.error(
        "O modelo pickle não foi encontrado. Execute as células de exportação da Etapa 11 no notebook."
    )
except (ValueError, RuntimeError, AttributeError, ImportError) as error:
    st.error(f"Não foi possível carregar o modelo: {error}")


with st.expander("Sobre esta estimativa"):
    st.write("LightGBM com perda absoluta | 36 atributos | MAPE de 23,30% em validação cruzada no desenvolvimento. Demonstração retrospectiva com dados de 2018.")
with st.container(border=True):
    st.subheader("Seu imóvel")
    st.caption("Preencha o que souber. Você pode deixar os campos opcionais em branco.")

    with st.form("listing_form"):
        st.markdown("**Imóvel**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            room_type_choice = st.selectbox(
                "Tipo de acomodação",
                ["Entire home/apt", "Private room", "Shared room", "Outro"],
                format_func=lambda value: {"Entire home/apt": "Espaço inteiro", "Private room": "Quarto privativo", "Shared room": "Quarto compartilhado", "Outro": "Outro"}[value],
                key="room_type_choice",
            )
            room_type = (
                st.text_input("Informe o tipo", key="room_type_other")
                if room_type_choice == "Outro"
                else room_type_choice
            )
        with col_b:
            property_type = st.selectbox("Tipo do imóvel", ["Apartment", "House", "Condominium", "Loft", "Townhouse", "Boat", "Other"], format_func=lambda value: {"Apartment": "Apartamento", "House": "Casa", "Condominium": "Condomínio", "Loft": "Loft", "Townhouse": "Casa geminada", "Boat": "Barco", "Other": "Outro"}[value], accept_new_options=True)
        with col_c:
            accommodates = st.number_input(
                "Capacidade de hóspedes", min_value=1, max_value=100, value=2, step=1
            )

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            bedrooms = _optional_number("Quartos", "bedrooms", 0, 50, 1)
        with col_b:
            bathrooms = _optional_number("Banheiros", "bathrooms", 0, 50, 0.5)
        with col_c:
            beds = _optional_number("Camas", "beds", 0, 100, 1)

        st.markdown("**Localização**")
        # Usa o centro aproximado do bairro para preencher a localização.
        neighbourhood_locations = json.loads(
            (ROOT_DIR / "assets" / "amsterdam-neighbourhoods.json").read_text(encoding="utf-8")
        )
        neighbourhood_options = list(neighbourhood_locations)
        neighbourhood = st.selectbox(
            "Bairro", neighbourhood_options,
            index=neighbourhood_options.index("Centrum-West"),
            key="neighbourhood_choice",
        )
        latitude = neighbourhood_locations[neighbourhood]["latitude"]
        longitude = neighbourhood_locations[neighbourhood]["longitude"]
        st.caption("Usamos uma localização aproximada pelo bairro para estimar a diária.")

        with st.expander("Mais detalhes do anúncio (opcional)"):
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

        st.markdown("**Qual é o preço da reserva?**")
        price_announced = st.number_input(
            "Preço por noite (€)", min_value=0.0, value=None, step=1.0,
            key="price_announced_eur", placeholder="Informe a diária"
        )
        submitted = st.form_submit_button(
            "Comparar preço", type="primary", width="stretch"
        )

if submitted:
    if artifact is None:
        st.error("O artefato do modelo está indisponível. Confira a exportação no notebook.")
    elif price_announced is None or price_announced <= 0:
        st.error("Informe um preço por noite maior que zero.")
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
            if result["price_reference_eur"] is None:
                st.warning("Não foi possível estimar uma diária positiva para estes dados.")
            else:
                st.session_state["price_comparison"] = {
                    "result": result, "announced": price_announced
                }
        except ValueError as error:
            st.error(str(error))

# Mostra a última comparação calculada e a diferença sobre a referência.
comparison = st.session_state.get("price_comparison")
if comparison is not None:
    prediction = comparison["result"]
    reference = prediction["price_reference_eur"]
    announced = comparison["announced"]
    difference = announced - reference
    difference_pct = 100 * difference / reference
    st.divider()
    st.subheader("Como está o preço?")
    if difference_pct < -25:
        st.success("Muito abaixo da referência · Preço bastante atrativo.")
    elif difference_pct < -10:
        st.success("Abaixo da referência · Preço atrativo.")
    elif difference_pct <= 10:
        st.info("Perto da referência · Preço alinhado.")
    elif difference_pct <= 25:
        st.warning("Acima da referência · Vale comparar outras opções.")
    else:
        st.warning("Muito acima da referência · Vale procurar opções mais baratas.")

    paid_column, reference_column, gap_column = st.columns(3)
    paid_column.metric("Preço informado por noite", _format_eur(announced))
    reference_column.metric("Referência por noite", _format_eur(reference))
    direction = "a mais" if difference > 0 else "a menos" if difference < 0 else "de diferença"
    gap_column.metric(f"Você paga {direction}", _format_eur(abs(difference)))
    if difference_pct == 0:
        st.write("O preço informado é igual à referência.")
    else:
        position = "acima" if difference_pct > 0 else "abaixo"
        st.write(f"O preço informado está {abs(difference_pct):.1f}% {position} da referência.")
    st.caption("Comparação com preços de dezembro de 2018. Confira datas, taxas e condições da reserva antes de decidir.")
    st.subheader("Barra menor = preço menor")
    chart_data = pd.DataFrame({
        "Preço": ["Preço informado", "Referência"],
        "Euros": [announced, reference],
        "Valor": [_format_eur(announced), _format_eur(reference)]
    })
    base = alt.Chart(chart_data).encode(
        y=alt.Y("Preço:N", sort=["Preço informado", "Referência"], title=None),
        x=alt.X("Euros:Q", title="€ por noite · menos ← → mais", scale=alt.Scale(domain=[0, max(announced, reference) * 1.3])),
        tooltip=["Preço", "Valor"]
    )
    bars = base.mark_bar(size=36, cornerRadiusEnd=5).encode(
        color=alt.Color("Preço:N", legend=None, scale=alt.Scale(domain=["Preço informado", "Referência"], range=["#d99662", "#7fb8cc"]))
    )
    labels = base.mark_text(align="left", dx=8, color="#e8edf0", fontSize=16).encode(text="Valor:N")
    st.altair_chart((bars + labels).properties(height=180), width="stretch")
    with st.expander("Entenda a comparação"):
        st.write("Comparamos a diária que você informou com uma estimativa baseada em anúncios de imóveis com características semelhantes.")
        st.write(f"Para este imóvel, a referência é {_format_eur(reference)} por noite. Você informou {_format_eur(announced)}.")
        st.write(f"Isso dá {_format_eur(abs(difference))} {direction} por noite.")
        st.markdown(
            "- **Preço atrativo:** a diária está abaixo da referência.\n"
            "- **Preço alinhado:** a diária está perto da referência.\n"
            "- **Vale comparar outras opções:** a diária está acima da referência."
        )
        st.write("No gráfico, uma barra mais curta significa um preço menor. Os valores escritos ao lado mostram quanto custa cada diária.")
        st.write(f"A estimativa tem uma margem de variação, de {_format_eur(prediction['interval_lower_eur'])} a {_format_eur(prediction['interval_upper_eur'])}. O preço de um imóvel específico pode ficar fora dessa faixa.")
        st.caption("Os avisos consideram apenas o preço. Confira também as taxas, as condições da reserva e se a acomodação atende ao que você precisa. A comparação usa preços de dezembro de 2018.")
    st.caption("Ao alterar os dados, clique em Comparar preço para atualizar o resultado.")
