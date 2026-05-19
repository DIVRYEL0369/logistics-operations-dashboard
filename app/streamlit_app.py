import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Logistics Operations Dashboard",
    page_icon="🚚",
    layout="wide"
)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def load_data():

    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"

    loads = pd.read_csv(DATA_DIR / "loads.csv")

    trips = pd.read_csv(DATA_DIR / "trips.csv")

    delivery_events = pd.read_csv(DATA_DIR / "delivery_events.csv")

    fuel_purchases = pd.read_csv(DATA_DIR / "fuel_purchases.csv")

    maintenance = pd.read_csv(DATA_DIR / "maintenance_records.csv")

    return loads, trips, delivery_events, fuel_purchases, maintenance


loads, trips, delivery_events, fuel_purchases, maintenance = load_data()

# ---------------------------------------------------
# DATA PREP
# ---------------------------------------------------

loads['load_date'] = pd.to_datetime(loads['load_date'])

loads['month_name'] = loads['load_date'].dt.month_name()

month_order = [
    'January', 'February', 'March', 'April',
    'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December'
]

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

st.sidebar.title("📊 Dashboard Filters")

selected_load_types = st.sidebar.multiselect(
    "Select Load Type",
    options=loads['load_type'].unique(),
    default=loads['load_type'].unique()
)

selected_booking_types = st.sidebar.multiselect(
    "Select Booking Type",
    options=loads['booking_type'].unique(),
    default=loads['booking_type'].unique()
)

selected_months = st.sidebar.multiselect(
    "Select Months",
    options=month_order,
    default=month_order
)

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------

filtered_loads = loads[
    (loads['load_type'].isin(selected_load_types)) &
    (loads['booking_type'].isin(selected_booking_types)) &
    (loads['month_name'].isin(selected_months))
]

# ---------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------

total_revenue = filtered_loads['revenue'].sum()

total_loads = filtered_loads['load_id'].nunique()

total_trips = trips['trip_id'].nunique()

avg_mpg = trips['average_mpg'].mean()

on_time_rate = delivery_events['on_time_flag'].mean() * 100

fuel_cost = fuel_purchases['total_cost'].sum()

maintenance_cost = maintenance['total_cost'].sum()

avg_idle_time = trips['idle_time_hours'].mean()

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("🚚 Logistics Operations Dashboard")

st.markdown(
    """
    ### Operational Intelligence & Fleet Performance Analytics

    Monitor logistics revenue, delivery performance,
    maintenance trends, fuel costs, and customer insights.
    """
)

st.divider()

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Revenue",
    f"${total_revenue:,.0f}"
)

col2.metric(
    "Total Loads",
    f"{total_loads:,}"
)

col3.metric(
    "Total Trips",
    f"{total_trips:,}"
)

col4.metric(
    "Average MPG",
    f"{avg_mpg:.2f}"
)

col5, col6, col7, col8 = st.columns(4)

col5.metric(
    "On-Time Rate",
    f"{on_time_rate:.2f}%"
)

col6.metric(
    "Fuel Cost",
    f"${fuel_cost:,.0f}"
)

col7.metric(
    "Maintenance Cost",
    f"${maintenance_cost:,.0f}"
)

col8.metric(
    "Avg Idle Time",
    f"{avg_idle_time:.2f} hrs"
)

st.divider()

# ---------------------------------------------------
# REVENUE ANALYTICS
# ---------------------------------------------------

st.header("📈 Revenue Analytics")

col_a, col_b = st.columns(2)

# ---------------------------------------------------
# Revenue by Load Type
# ---------------------------------------------------

with col_a:

    revenue_by_load = (
        filtered_loads.groupby('load_type')['revenue']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig1 = px.bar(
        revenue_by_load,
        x='load_type',
        y='revenue',
        color='load_type',
        text_auto='.2s',
        title='Revenue by Load Type'
    )

    fig1.update_layout(
        showlegend=False,
        xaxis_title='Load Type',
        yaxis_title='Revenue ($)'
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    st.info(
        "💡 Full truckload shipments generate the highest revenue contribution as both Dry Van and Refrigerated generates almost same income."
    )

# ---------------------------------------------------
# Revenue by Booking Type
# ---------------------------------------------------

with col_b:

    booking_revenue = (
        filtered_loads.groupby('booking_type')['revenue']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig2 = px.bar(
        booking_revenue,
        x='booking_type',
        y='revenue',
        color='booking_type',
        text_auto='.2s',
        title='Revenue by Booking Type'
    )

    fig2.update_layout(
        showlegend=False,
        xaxis_title='Booking Type',
        yaxis_title='Revenue ($)'
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.info(
        "Spot bookings appear to contribute more revenue than Contract loads, while Dedicated generates the overall highest revenue."
    )

st.divider()

# ---------------------------------------------------
# MONTHLY TREND ANALYSIS
# ---------------------------------------------------

st.header("📅 Monthly Trend Analysis")

monthly_revenue = (
    filtered_loads.groupby('month_name')['revenue']
    .sum()
    .reindex(month_order)
    .reset_index()
)

fig3 = px.line(
    monthly_revenue,
    x='month_name',
    y='revenue',
    markers=True,
    title='Monthly Revenue Trend'
)

fig3.update_traces(
    line=dict(width=4),
    marker=dict(size=10)
)

fig3.update_layout(
    xaxis_title='Month',
    yaxis_title='Revenue ($)'
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

peak_month = monthly_revenue.loc[
    monthly_revenue['revenue'].idxmax(),
    'month_name'
]

st.success(
    f"Peak operational revenue occurred in {peak_month}."
)

st.divider()

# ---------------------------------------------------
# DELIVERY PERFORMANCE
# ---------------------------------------------------

st.header("⏱ Delivery Performance")

col_c, col_d = st.columns(2)

# ---------------------------------------------------
# On-Time vs Late Deliveries
# ---------------------------------------------------

with col_c:

    delivery_status = (
        delivery_events['on_time_flag']
        .value_counts()
        .reset_index()
    )

    delivery_status.columns = [
        'Delivery Status',
        'Count'
    ]

    delivery_status['Delivery Status'] = [
        'On-Time',
        'Late'
    ]

    fig4 = px.bar(
        delivery_status,
        x='Delivery Status',
        y='Count',
        color='Delivery Status',
        text_auto=True,
        title='On-Time vs Late Deliveries',
        color_discrete_sequence=[
            'seagreen',
            'crimson'
        ]
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

    st.info(
        "High on-time performance indicates strong operational efficiency."
    )

# ---------------------------------------------------
# Detention Analysis
# ---------------------------------------------------

with col_d:

    state_detention = (
        delivery_events.groupby('location_state')['detention_minutes']
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig5 = px.bar(
        state_detention,
        x='location_state',
        y='detention_minutes',
        color='detention_minutes',
        text_auto='.2f',
        title='Top 10 States by Detention Time'
    )

    fig5.update_layout(
        xaxis_title='State',
        yaxis_title='Average Detention Minutes'
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

    st.warning(
        "States with high detention times like INDIANA and CALIFORNIA may indicate warehouse bottlenecks or scheduling inefficiencies."
    )

st.divider()

# ---------------------------------------------------
# COST ANALYTICS
# ---------------------------------------------------

st.header("💰 Cost Analytics")

col_e, col_f = st.columns(2)

# ---------------------------------------------------
# Maintenance Cost Analysis
# ---------------------------------------------------

with col_e:

    maintenance_by_type = (
        maintenance.groupby('maintenance_type')['total_cost']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig6 = px.bar(
        maintenance_by_type,
        x='maintenance_type',
        y='total_cost',
        color='maintenance_type',
        text_auto='.2s',
        title='Maintenance Cost by Type'
    )

    fig6.update_layout(
        showlegend=False,
        xaxis_title='Maintenance Type',
        yaxis_title='Cost ($)'
    )

    st.plotly_chart(
        fig6,
        use_container_width=True
    )

    st.info(
        "Preventive maintenance can reduce long-term repair expenses."
    )

# ---------------------------------------------------
# Fuel Cost Analysis
# ---------------------------------------------------

with col_f:

    fuel_by_state = (
        fuel_purchases.groupby('location_state')['total_cost']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig7 = px.bar(
        fuel_by_state,
        x='location_state',
        y='total_cost',
        color='total_cost',
        text_auto='.2s',
        title='Top 10 States by Fuel Cost'
    )

    fig7.update_layout(
        xaxis_title='State',
        yaxis_title='Fuel Cost ($)'
    )

    st.plotly_chart(
        fig7,
        use_container_width=True
    )

    st.warning(
        "States like TEXAS and TENNESSEE with elevated fuel costs may represent major logistics corridors."
    )

st.divider()

# ---------------------------------------------------
# CUSTOMER ANALYTICS
# ---------------------------------------------------

st.header("🏆 Customer Analytics")

top_customers = (
    filtered_loads.groupby('customer_id')['revenue']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig8 = px.bar(
    top_customers,
    x='customer_id',
    y='revenue',
    color='revenue',
    text_auto='.2s',
    title='Top 10 Customers by Revenue'
)

fig8.update_layout(
    xaxis_title='Customer ID',
    yaxis_title='Revenue ($)'
)

st.plotly_chart(
    fig8,
    use_container_width=True
)

st.success(
    "Top-performing customers drive a substantial share of company revenue."
)

st.divider()

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("---")

st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <h4> Developed By</h4>
        <p style='font-size:20px;'><strong>Divine Ejee</strong></p>
        <p>Data Analytics • Business Intelligence • Logistics Analytics</p>
        <p>Built with Streamlit, Pandas & Plotly</p>
    </div>
    """,
    unsafe_allow_html=True
)