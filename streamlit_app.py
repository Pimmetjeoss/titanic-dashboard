import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

# Page configuration
st.set_page_config(
    page_title="CONTIWEB Delivery Schedule",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        color: white;
        font-weight: bold;
        text-align: center;
    }
    .status-in-stock { background-color: #28a745; }
    .status-released { background-color: #17a2b8; }
    .status-planned { background-color: #ffc107; color: black; }
    .status-created { background-color: #6c757d; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_delivery_data():
    """Load data from PostgreSQL database"""
    try:
        # Initialize connection
        conn = st.connection("postgresql", type="sql")
        
        # Load main delivery data
        df = conn.query("""
            SELECT 
                ds.*,
                mg.description as mrp_group_description
            FROM delivery_schedule ds
            LEFT JOIN mrp_groups mg ON ds.mrp_group = mg.group_code
            ORDER BY ds.ship_date, ds.customer
        """, ttl="10m")
        
        return df
        
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        st.info("Make sure your PostgreSQL database is running and secrets are configured correctly.")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_summary_stats():
    """Load summary statistics"""
    try:
        conn = st.connection("postgresql", type="sql")
        
        # Status summary
        status_stats = conn.query("""
            SELECT 
                status,
                COUNT(*) as project_count,
                COUNT(CASE WHEN ship_date IS NOT NULL THEN 1 END) as with_ship_date
            FROM delivery_schedule
            GROUP BY status
            ORDER BY project_count DESC
        """, ttl="10m")
        
        # Customer summary
        customer_stats = conn.query("""
            SELECT 
                customer,
                country,
                COUNT(*) as total_projects,
                MIN(ship_date) as next_delivery,
                MAX(ship_date) as last_delivery
            FROM delivery_schedule
            WHERE ship_date IS NOT NULL
            GROUP BY customer, country
            ORDER BY total_projects DESC
            LIMIT 10
        """, ttl="10m")
        
        # Monthly deliveries
        monthly_stats = conn.query("""
            SELECT 
                EXTRACT(YEAR FROM ship_date) as year,
                EXTRACT(MONTH FROM ship_date) as month,
                COUNT(*) as deliveries_count
            FROM delivery_schedule
            WHERE ship_date IS NOT NULL
            GROUP BY EXTRACT(YEAR FROM ship_date), EXTRACT(MONTH FROM ship_date)
            ORDER BY year, month
        """, ttl="10m")
        
        return status_stats, customer_stats, monthly_stats
        
    except Exception as e:
        st.error(f"Failed to load summary stats: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def format_status_badge(status):
    """Create styled status badge"""
    status_class = f"status-{status.lower().replace(' ', '-')}"
    return f'<span class="status-badge {status_class}">{status}</span>'

def create_delivery_timeline_chart(df):
    """Create timeline chart for deliveries"""
    if df.empty or 'ship_date' not in df.columns:
        return go.Figure()
    
    # Filter data with valid ship dates
    df_timeline = df[df['ship_date'].notna()].copy()
    
    if df_timeline.empty:
        return go.Figure()
    
    # Create timeline chart
    fig = px.timeline(
        df_timeline,
        x_start="ship_date",
        x_end="ship_date",
        y="customer",
        color="status",
        hover_data=["wbs_element", "description", "country"],
        title="Delivery Timeline by Customer"
    )
    
    fig.update_layout(
        height=600,
        xaxis_title="Ship Date",
        yaxis_title="Customer"
    )
    
    return fig

def create_status_pie_chart(status_stats):
    """Create pie chart for project status"""
    if status_stats.empty:
        return go.Figure()
    
    fig = px.pie(
        status_stats,
        values='project_count',
        names='status',
        title='Projects by Status',
        color_discrete_map={
            'In stock': '#28a745',
            'Released': '#17a2b8', 
            'Planned': '#ffc107',
            'Created': '#6c757d'
        }
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def create_monthly_deliveries_chart(monthly_stats):
    """Create bar chart for monthly deliveries"""
    if monthly_stats.empty:
        return go.Figure()
    
    # Create month labels
    monthly_stats['month_label'] = monthly_stats.apply(
        lambda row: f"{calendar.month_abbr[int(row['month'])]} {int(row['year'])}", 
        axis=1
    )
    
    fig = px.bar(
        monthly_stats,
        x='month_label',
        y='deliveries_count',
        title='Planned Deliveries by Month',
        color='deliveries_count',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Deliveries"
    )
    
    return fig

# Main application
def main():
    # Header
    st.markdown('<h1 class="main-header">🏭 CONTIWEB Delivery Schedule Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading delivery data..."):
        df = load_delivery_data()
        status_stats, customer_stats, monthly_stats = load_summary_stats()
    
    if df.empty:
        st.warning("No data available. Please check your database connection.")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Status filter
    status_options = ['All'] + sorted(df['status'].dropna().unique().tolist())
    selected_status = st.sidebar.selectbox("Status", status_options)
    
    # Customer filter
    customer_options = ['All'] + sorted(df['customer'].dropna().unique().tolist())
    selected_customer = st.sidebar.selectbox("Customer", customer_options)
    
    # MRP Group filter
    mrp_options = ['All'] + sorted(df['mrp_group'].dropna().unique().tolist())
    selected_mrp = st.sidebar.selectbox("MRP Group", mrp_options)
    
    # Country filter
    country_options = ['All'] + sorted(df['country'].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox("Country", country_options)
    
    # Date range filter
    if 'ship_date' in df.columns and not df['ship_date'].isna().all():
        min_date = df['ship_date'].min()
        max_date = df['ship_date'].max()
        
        date_range = st.sidebar.date_input(
            "Ship Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    
    if selected_customer != 'All':
        filtered_df = filtered_df[filtered_df['customer'] == selected_customer]
    
    if selected_mrp != 'All':
        filtered_df = filtered_df[filtered_df['mrp_group'] == selected_mrp]
    
    if selected_country != 'All':
        filtered_df = filtered_df[filtered_df['country'] == selected_country]
    
    # Apply date filter if valid range selected
    if 'ship_date' in df.columns and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['ship_date'] >= pd.to_datetime(start_date)) &
            (filtered_df['ship_date'] <= pd.to_datetime(end_date))
        ]
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "📋 Projects", 
        "👥 Customers", 
        "📅 Timeline", 
        "📈 Analytics"
    ])
    
    with tab1:
        st.header("📊 Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_projects = len(filtered_df)
            st.metric("Total Projects", total_projects)
        
        with col2:
            in_stock = len(filtered_df[filtered_df['status'] == 'In stock'])
            st.metric("In Stock", in_stock)
        
        with col3:
            released = len(filtered_df[filtered_df['status'] == 'Released'])
            st.metric("Released", released)
        
        with col4:
            planned = len(filtered_df[filtered_df['status'] == 'Planned'])
            st.metric("Planned", planned)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if not status_stats.empty:
                fig_pie = create_status_pie_chart(status_stats)
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            if not monthly_stats.empty:
                fig_monthly = create_monthly_deliveries_chart(monthly_stats)
                st.plotly_chart(fig_monthly, use_container_width=True)
    
    with tab2:
        st.header("📋 Project Details")
        
        if not filtered_df.empty:
            # Project table with better formatting
            display_df = filtered_df[[
                'wbs_element', 'customer', 'country', 'status', 
                'description', 'ship_date', 'mrp_group', 'ts_text'
            ]].copy()
            
            # Format dates
            if 'ship_date' in display_df.columns:
                display_df['ship_date'] = pd.to_datetime(display_df['ship_date']).dt.strftime('%d.%m.%Y')
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "wbs_element": "WBS Element",
                    "customer": "Customer",
                    "country": "Country",
                    "status": "Status",
                    "description": "Description",
                    "ship_date": "Ship Date",
                    "mrp_group": "MRP Group",
                    "ts_text": "TS Text"
                }
            )
            
            # Download button
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"contiweb_delivery_schedule_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No projects match the selected filters.")
    
    with tab3:
        st.header("👥 Customer Analysis")
        
        if not customer_stats.empty:
            st.subheader("Top Customers by Project Count")
            
            # Customer metrics
            for _, row in customer_stats.head(5).iterrows():
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Customer", row['customer'])
                with col2:
                    st.metric("Country", row['country'])
                with col3:
                    st.metric("Total Projects", int(row['total_projects']))
                with col4:
                    next_delivery = row['next_delivery']
                    if pd.notna(next_delivery):
                        st.metric("Next Delivery", pd.to_datetime(next_delivery).strftime('%d.%m.%Y'))
                    else:
                        st.metric("Next Delivery", "N/A")
                
                st.divider()
        
        # Customer project distribution
        if not filtered_df.empty:
            customer_counts = filtered_df['customer'].value_counts().head(10)
            
            fig_customers = px.bar(
                x=customer_counts.values,
                y=customer_counts.index,
                orientation='h',
                title='Projects per Customer',
                labels={'x': 'Number of Projects', 'y': 'Customer'}
            )
            
            fig_customers.update_layout(height=500)
            st.plotly_chart(fig_customers, use_container_width=True)
    
    with tab4:
        st.header("📅 Delivery Timeline")
        
        if not filtered_df.empty:
            fig_timeline = create_delivery_timeline_chart(filtered_df)
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Upcoming deliveries
            st.subheader("🚚 Upcoming Deliveries (Next 30 Days)")
            today = datetime.now().date()
            next_month = today + timedelta(days=30)
            
            upcoming = filtered_df[
                (pd.to_datetime(filtered_df['ship_date']).dt.date >= today) &
                (pd.to_datetime(filtered_df['ship_date']).dt.date <= next_month)
            ].sort_values('ship_date')
            
            if not upcoming.empty:
                for _, row in upcoming.iterrows():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.write(f"**{row['customer']}**")
                        st.write(f"{row['wbs_element']}")
                    with col2:
                        st.write(f"{row['description']}")
                        st.write(f"Status: {row['status']}")
                    with col3:
                        ship_date = pd.to_datetime(row['ship_date'])
                        st.write(f"📅 {ship_date.strftime('%d.%m.%Y')}")
                    
                    st.divider()
            else:
                st.info("No deliveries scheduled in the next 30 days.")
    
    with tab5:
        st.header("📈 Analytics")
        
        # MRP Group distribution
        if not filtered_df.empty and 'mrp_group' in filtered_df.columns:
            mrp_counts = filtered_df['mrp_group'].value_counts()
            
            fig_mrp = px.pie(
                values=mrp_counts.values,
                names=mrp_counts.index,
                title='Projects by MRP Group'
            )
            
            st.plotly_chart(fig_mrp, use_container_width=True)
        
        # Country distribution
        if not filtered_df.empty:
            country_counts = filtered_df['country'].value_counts()
            
            fig_country = px.bar(
                x=country_counts.index,
                y=country_counts.values,
                title='Projects by Country',
                labels={'x': 'Country', 'y': 'Number of Projects'}
            )
            
            st.plotly_chart(fig_country, use_container_width=True)
        
        # Status by MRP Group heatmap
        if not filtered_df.empty and 'mrp_group' in filtered_df.columns:
            heatmap_data = filtered_df.groupby(['mrp_group', 'status']).size().unstack(fill_value=0)
            
            if not heatmap_data.empty:
                fig_heatmap = px.imshow(
                    heatmap_data.values,
                    x=heatmap_data.columns,
                    y=heatmap_data.index,
                    title='Project Status by MRP Group',
                    labels={'x': 'Status', 'y': 'MRP Group'},
                    color_continuous_scale='Blues'
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True)

if __name__ == "__main__":
    main()
