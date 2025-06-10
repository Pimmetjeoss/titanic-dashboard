# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
import logging

# VERBETERING: Logging configureren voor betere debugging in Streamlit Cloud logs.
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- PAGINA CONFIGURATIE ---
st.set_page_config(
    page_title="🚢 Titanic Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATABASE CONNECTIE ---
# VERBETERING: Duidelijke docstring die het doel en de caching uitlegt.
# @st.cache_resource zorgt ervoor dat de connectie slechts één keer wordt gemaakt en hergebruikt.
@st.cache_resource
def init_supabase() -> Client | None:
    """
    Initializeert en retourneert de Supabase client.
    Credentials worden uit Streamlit Secrets gehaald.
    Retourneert None bij een fout.
    """
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        # Log de fout voor debugging en toon een duidelijke melding aan de gebruiker.
        logging.error(f"Fout bij initialiseren Supabase connectie: {e}")
        st.error("❌ Verbinding met de database is mislukt. Controleer de Supabase secrets in Streamlit Cloud.")
        return None

# --- DATA LADEN EN OPSCHONEN ---
# VERBETERING: Duidelijke docstring. @st.cache_data slaat het resultaat (de DataFrame) op.
@st.cache_data(ttl=600)
def load_data(_supabase_client: Client) -> pd.DataFrame | None:
    """
    Laadt de data van de Supabase tabel 'Passengers'.
    Retourneert een Pandas DataFrame of None bij een fout.
    
    Args:
        _supabase_client: De actieve Supabase client.
    """
    if _supabase_client is None:
        return None

    try:
        with st.spinner("📊 Data wordt geladen vanuit de database..."):
            # AANPASSING: Typefout gecorrigeerd. 'Passegners' -> 'Passengers'. Dit was de hoofdzaak van het probleem!
            response = _supabase_client.table("Passengers").select("*").execute()
            
            # Controleer of er wel data is
            if not response.data:
                st.warning("⚠️ De tabel 'Passengers' bevat geen data.")
                return None
            
            df = pd.DataFrame(response.data)
            logging.info(f"Successfully loaded {len(df)} records from Supabase.")
            
            # Data opschonen
            df = clean_data(df)
            return df

    except Exception as e:
        # VERBETERING: Log de specifieke database-error. Dit is essentieel voor debugging.
        logging.error(f"Fout bij het laden van data uit Supabase: {e}")
        st.error(f"❌ Fout bij het laden van data. Controleer of de tabel 'Passengers' bestaat en toegankelijk is.")
        return None

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Maakt de DataFrame schoon en converteert datatypes."""
    # VERBETERING: Robuuster gemaakt door te checken of kolommen bestaan.
    if 'survived' in df.columns:
        df['survived'] = pd.to_numeric(df['survived'], errors='coerce').fillna(0).astype(int)
    if 'pclass' in df.columns:
        df['pclass'] = pd.to_numeric(df['pclass'], errors='coerce').fillna(0).astype(int)
    if 'age' in df.columns:
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
        df['age'].fillna(df['age'].median(), inplace=True)
    if 'fare' in df.columns:
        df['fare'] = pd.to_numeric(df['fare'], errors='coerce')
        df['fare'].fillna(df['fare'].median(), inplace=True)
    if 'sex' in df.columns:
        df['sex'] = df['sex'].astype(str).str.lower().str.strip()
    if 'embarked' in df.columns:
        df['embarked'] = df['embarked'].astype(str).str.upper().str.strip()
        df['embarked'].fillna('Unknown', inplace=True)
    return df

# --- UI COMPONENTEN (Functies voor de interface) ---

def display_metrics(df: pd.DataFrame):
    """Toont de belangrijkste statistieken in kolommen."""
    st.subheader("📈 Belangrijkste Statistieken")
    col1, col2, col3, col4 = st.columns(4)
    
    total_passengers = len(df)
    survivors = len(df[df['survived'] == 1]) if 'survived' in df.columns else 0
    
    col1.metric("Totaal Passagiers", f"{total_passengers:,}")
    
    survival_rate = (survivors / total_passengers * 100) if total_passengers > 0 else 0
    col2.metric("Overlevingspercentage", f"{survival_rate:.1f}%")
    
    avg_age = df['age'].mean() if 'age' in df.columns and df['age'].notna().any() else 0
    col3.metric("Gemiddelde Leeftijd", f"{avg_age:.1f}" if avg_age > 0 else "N/A")

    avg_fare = df['fare'].mean() if 'fare' in df.columns and df['fare'].notna().any() else 0
    col4.metric("Gemiddelde Fare", f"${avg_fare:.2f}" if avg_fare > 0 else "N/A")

def display_charts(df: pd.DataFrame):
    """Toont de verschillende grafieken."""
    col1, col2 = st.columns(2)
    with col1:
        if 'pclass' in df.columns and 'survived' in df.columns:
            st.subheader("📊 Overleving per Klasse")
            survival_by_class = df.groupby(['pclass', 'survived']).size().unstack(fill_value=0)
            fig = px.bar(survival_by_class, barmode='stack', labels={'value': 'Aantal Passagiers', 'pclass': 'Klasse'},
                         color_discrete_map={0: '#E76F51', 1: '#2A9D8F'}, title="Overleving per Klasse (0=Overleden, 1=Overleefd)")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if 'sex' in df.columns:
            st.subheader("👥 Gender Verdeling")
            gender_counts = df['sex'].value_counts()
            fig = px.pie(values=gender_counts.values, names=[g.title() for g in gender_counts.index], 
                         title="Gender Verdeling", color_discrete_map={'Male': '#87CEEB', 'Female': '#FFB6C1'})
            st.plotly_chart(fig, use_container_width=True)
            
    if 'age' in df.columns and 'survived' in df.columns:
        st.subheader("👶 Leeftijd vs. Overleving")
        fig = px.histogram(df, x='age', color='survived', nbins=50,
                           labels={'survived': 'Status', 'age': 'Leeftijd'}, 
                           color_discrete_map={0: '#E76F51', 1: '#2A9D8F'}, title="Verdeling van Leeftijd en Overleving")
        st.plotly_chart(fig, use_container_width=True)

def display_dataframe(df: pd.DataFrame):
    """Toont een doorzoekbaar voorbeeld van de data."""
    st.subheader("📋 Data Voorbeeld")
    with st.expander("Bekijk de gefilterde data"):
        st.dataframe(df, use_container_width=True)

# --- HOOFD APPLICATIE ---
def main():
    """De hoofd-functie die de app runt."""
    st.title("🚢 Titanic Passagiers Dashboard")
    st.markdown("Een interactief dashboard om de data van de Titanic-passagiers te verkennen.")
    st.markdown("---")

    # Stap 1: Maak verbinding en laad data
    supabase = init_supabase()
    df = load_data(supabase)

    # Stap 2: Stop de app als data laden mislukt
    if df is None:
        st.warning("De app kan niet worden geladen omdat de data ontbreekt.")
        st.info("💡 Mogelijke oplossingen: Controleer de Supabase URL/KEY in je secrets en verifieer de tabelnaam 'Passengers'.")
        st.stop() # Stopt de uitvoering van het script

    st.success(f"✅ Data succesvol geladen: {len(df):,} passagiers gevonden.")

    # Stap 3: Bouw de sidebar met filters
    st.sidebar.header("🔍 Filters")
    
    selected_class = st.sidebar.selectbox("🎫 Klasse", ['Alle'] + sorted(df['pclass'].unique()))
    selected_gender = st.sidebar.selectbox("👤 Gender", ['Alle'] + [g.title() for g in df['sex'].unique()])
    age_range = st.sidebar.slider("👶 Leeftijd", int(df['age'].min()), int(df['age'].max()), (int(df['age'].min()), int(df['age'].max())))
    
    # Stap 4: Pas filters toe
    filtered_df = df[
        (df['pclass'] == selected_class if selected_class != 'Alle' else True) &
        (df['sex'] == selected_gender.lower() if selected_gender != 'Alle' else True) &
        (df['age'].between(age_range[0], age_range[1]))
    ]
    
    st.sidebar.markdown(f"**📊 Gefilterde passagiers: {len(filtered_df):,}**")
    
    # Stap 5: Toon de UI-elementen
    if filtered_df.empty:
        st.warning("⚠️ Geen passagiers gevonden met de huidige filterinstellingen.")
    else:
        display_metrics(filtered_df)
        st.markdown("---")
        display_charts(filtered_df)
        st.markdown("---")
        display_dataframe(filtered_df)

    # Footer
    st.markdown("---")
    st.markdown("<div style='text-align: center;'>Gemaakt met 💙 door een data liefhebber</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
