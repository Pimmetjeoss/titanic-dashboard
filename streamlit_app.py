import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from st_supabase_connection import SupabaseConnection
from typing import Optional
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🚢 Titanic Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ff6b6b;
    }
    .stSelectbox > div > div {
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Initialize connection with error handling
@st.cache_resource
def init_connection():
    """Initialize Supabase connection with error handling."""
    try:
        return st.connection("supabase", type=SupabaseConnection)
    except Exception as e:
        logger.error(f"Failed to initialize connection: {e}")
        st.error("❌ Verbinding met database mislukt. Controleer je configuratie.")
        return None

# Load and process data with comprehensive error handling
@st.cache_data(ttl=600)
def load_data() -> Optional[pd.DataFrame]:
    """Load data from Supabase with data validation and cleaning."""
    conn = init_connection()
    if conn is None:
        return None
    
    try:
        with st.spinner("📊 Data laden..."):
            data = conn.query('SELECT * FROM "Passegners"', ttl=600).execute()
            
            if not data.data:
                st.warning("⚠️ Geen data gevonden in de database.")
                return None
            
            df = pd.DataFrame(data.data)
            
            # Data validation and cleaning
            if df.empty:
                st.warning("⚠️ Database is leeg.")
                return None
            
            # Clean and convert data types
            df = clean_data(df)
            
            logger.info(f"Successfully loaded {len(df)} records")
            return df
            
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        st.error(f"❌ Error bij het laden van data: {str(e)}")
        return None

@st.cache_data(ttl=300)
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare data for analysis."""
    try:
        # Convert data types
        df['survived'] = pd.to_numeric(df['survived'], errors='coerce').fillna(0).astype(int)
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
        df['fare'] = pd.to_numeric(df['fare'], errors='coerce')
        df['pclass'] = pd.to_numeric(df['pclass'], errors='coerce').astype(int)
        
        # Clean string columns
        df['sex'] = df['sex'].astype(str).str.lower().str.strip()
        df['embarked'] = df['embarked'].astype(str).str.upper().str.strip()
        
        # Handle missing values
        df['age'].fillna(df['age'].median(), inplace=True)
        df['fare'].fillna(df['fare'].median(), inplace=True)
        df['embarked'].fillna('Unknown', inplace=True)
        
        # Remove invalid rows
        df = df[df['pclass'].isin([1, 2, 3])]
        df = df[df['survived'].isin([0, 1])]
        
        return df
        
    except Exception as e:
        logger.error(f"Error cleaning data: {e}")
        st.error("❌ Error bij het schoonmaken van data")
        return df

@st.cache_data(ttl=60)
def filter_data(df: pd.DataFrame, class_filter: str, gender_filter: str, age_range: tuple) -> pd.DataFrame:
    """Apply filters to the dataset with caching."""
    filtered_df = df.copy()
    
    if class_filter != 'Alle':
        filtered_df = filtered_df[filtered_df['pclass'] == class_filter]
    
    if gender_filter != 'Alle':
        filtered_df = filtered_df[filtered_df['sex'] == gender_filter.lower()]
    
    filtered_df = filtered_df[
        (filtered_df['age'] >= age_range[0]) & 
        (filtered_df['age'] <= age_range[1])
    ]
    
    return filtered_df

def create_survival_chart(filtered_df: pd.DataFrame):
    """Create survival by class chart with error handling."""
    try:
        if filtered_df.empty:
            st.warning("Geen data om weer te geven")
            return
        
        survival_by_class = filtered_df.groupby(['pclass', 'survived']).size().unstack(fill_value=0)
        
        if survival_by_class.empty:
            st.warning("Geen survival data beschikbaar")
            return
        
        fig = px.bar(
            survival_by_class,
            title="Overleving per Klasse",
            labels={'value': 'Aantal', 'pclass': 'Klasse', 'survived': 'Overleefd'},
            color_discrete_map={0: '#ff7f7f', 1: '#7fbf7f'}
        )
        fig.update_layout(
            xaxis_title="Klasse",
            yaxis_title="Aantal Passagiers",
            legend_title="Overleefd"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        logger.error(f"Error creating survival chart: {e}")
        st.error("Error bij het maken van survival grafiek")

def create_gender_chart(filtered_df: pd.DataFrame):
    """Create gender distribution chart with error handling."""
    try:
        if filtered_df.empty:
            st.warning("Geen data om weer te geven")
            return
            
        gender_counts = filtered_df['sex'].value_counts()
        
        if gender_counts.empty:
            st.warning("Geen gender data beschikbaar")
            return
        
        fig = px.pie(
            values=gender_counts.values,
            names=[g.title() for g in gender_counts.index],
            title="Gender Verdeling",
            color_discrete_map={'Male': '#87CEEB', 'Female': '#FFB6C1'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        logger.error(f"Error creating gender chart: {e}")
        st.error("Error bij het maken van gender grafiek")

def display_metrics(df: pd.DataFrame):
    """Display key metrics with error handling."""
    try:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Passagiers", f"{len(df):,}")
        
        with col2:
            if len(df) > 0:
                survivors = len(df[df['survived'] == 1])
                survival_rate = (survivors / len(df) * 100)
                st.metric("Overlevingspercentage", f"{survival_rate:.1f}%")
            else:
                st.metric("Overlevingspercentage", "N/A")
        
        with col3:
            if len(df) > 0 and df['age'].notna().any():
                avg_age = df['age'].mean()
                st.metric("Gemiddelde Leeftijd", f"{avg_age:.1f}")
            else:
                st.metric("Gemiddelde Leeftijd", "N/A")
        
        with col4:
            if len(df) > 0 and df['fare'].notna().any():
                avg_fare = df['fare'].mean()
                st.metric("Gemiddelde Fare", f"${avg_fare:.2f}")
            else:
                st.metric("Gemiddelde Fare", "N/A")
                
    except Exception as e:
        logger.error(f"Error displaying metrics: {e}")
        st.error("Error bij het weergeven van statistieken")

# Main application
def main():
    """Main application logic."""
    # Title and description
    st.title("🚢 Titanic Passenger Dashboard")
    st.markdown("**Een professioneel dashboard om de Titanic data te verkennen**")
    st.markdown("---")
    
    # Load data
    df = load_data()
    
    if df is None:
        st.error("❌ Kan geen verbinding maken met de database.")
        st.info("💡 Controleer je Supabase configuratie in secrets.toml")
        st.code("""
# .streamlit/secrets.toml
[connections.supabase]
SUPABASE_URL = "your_url_here"
SUPABASE_KEY = "your_key_here"
        """)
        st.stop()
    
    # Success message
    st.success(f"✅ Data succesvol geladen: {len(df):,} passagiers")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    st.sidebar.markdown("Gebruik deze filters om de data te verkennen")
    
    # Class filter
    classes = ['Alle'] + sorted(df['pclass'].unique().tolist())
    selected_class = st.sidebar.selectbox(
        "🎫 Passenger Class", 
        classes,
        help="Filter op passenger klasse"
    )
    
    # Gender filter
    genders = ['Alle'] + [g.title() for g in sorted(df['sex'].unique().tolist())]
    selected_gender = st.sidebar.selectbox(
        "👤 Gender", 
        genders,
        help="Filter op gender"
    )
    
    # Age range filter
    if df['age'].notna().any():
        min_age, max_age = int(df['age'].min()), int(df['age'].max())
        age_range = st.sidebar.slider(
            "👶 Leeftijd Range",
            min_value=min_age,
            max_value=max_age,
            value=(min_age, max_age),
            help="Selecteer leeftijd bereik"
        )
    else:
        age_range = (0, 100)
        st.sidebar.warning("Geen leeftijd data beschikbaar")
    
    # Apply filters
    filtered_df = filter_data(df, selected_class, selected_gender.lower() if selected_gender != 'Alle' else 'Alle', age_range)
    
    # Display filtered count
    st.sidebar.markdown(f"**📊 Gefilterde passagiers: {len(filtered_df):,}**")
    
    if len(filtered_df) == 0:
        st.warning("⚠️ Geen data gevonden met de huidige filters. Probeer andere filter instellingen.")
        st.stop()
    
    # Display metrics
    display_metrics(filtered_df)
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Overleving per Klasse")
        create_survival_chart(filtered_df)
    
    with col2:
        st.subheader("👥 Gender Verdeling")
        create_gender_chart(filtered_df)
    
    # Age distribution
    st.subheader("📈 Leeftijd Verdeling")
    try:
        if not filtered_df.empty and filtered_df['age'].notna().any():
            fig = px.histogram(
                filtered_df,
                x='age',
                color='survived',
                title="Leeftijd Verdeling per Overleving",
                labels={'survived': 'Overleefd', 'age': 'Leeftijd', 'count': 'Aantal'},
                color_discrete_map={0: '#ff7f7f', 1: '#7fbf7f'}
            )
            fig.update_layout(
                xaxis_title="Leeftijd",
                yaxis_title="Aantal Passagiers"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Geen leeftijd data beschikbaar voor visualisatie")
    except Exception as e:
        logger.error(f"Error creating age distribution chart: {e}")
        st.error("Error bij het maken van leeftijd grafiek")
    
    # Data preview
    st.subheader("📋 Data Voorbeeld")
    try:
        display_columns = ['name', 'age', 'sex', 'pclass', 'survived', 'fare', 'embarked']
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        
        if available_columns:
            st.dataframe(
                filtered_df[available_columns].head(10),
                use_container_width=True
            )
            
            # Download option
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download gefilterde data als CSV",
                data=csv,
                file_name=f"titanic_filtered_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Geen bekende kolommen gevonden voor weergave")
            
    except Exception as e:
        logger.error(f"Error displaying data preview: {e}")
        st.error("Error bij het weergeven van data voorbeeld")
    
    # Footer
    st.markdown("---")
    st.markdown("**🔧 Dashboard gemaakt met Streamlit & Supabase | 📊 Data updates elke 10 minuten**")

if __name__ == "__main__":
    main()
