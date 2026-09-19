import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# 1. Page Configuration & Data Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="Executive Sales & Marketing Dashboard",
    layout="wide"
)

df = pd.read_csv("Sales_Marketing_cleaned.csv")

# ---------------------------------------------------------
# Data Cleaning & Human-Readable Mapping (0/1 -> Descriptive Text)
# ---------------------------------------------------------
if 'churn' in df.columns:
    df['churn_label'] = df['churn'].map({0: 'Active Customer', 1: 'Churned Customer'})
if 'is_premium_user' in df.columns:
    df['premium_label'] = df['is_premium_user'].map({0: 'Standard User', 1: 'Premium User'})
if 'discount_used' in df.columns:
    df['discount_label'] = df['discount_used'].map({0: 'No Discount', 1: 'Discount Applied'})
if 'refund_requested' in df.columns:
    df['refund_label'] = df['refund_requested'].map({0: 'No Refund', 1: 'Refund Requested'})

# ---------------------------------------------------------
# 2. Sidebar Navigation (Business-Oriented Category Names)
# ---------------------------------------------------------
st.sidebar.title("Navigation & Filters")

main_page = st.sidebar.selectbox(
    'Select Dashboard Section:',
    [
        '1. Executive Summary & Core KPIs',
        '2. Customer Engagement & Financials',
        '3. Retention, Churn & Demographics',
        '4. Payment Gateways & Spending Trends',
        '5. Customer Satisfaction & Support Impact'
    ]
)

st.sidebar.markdown("---")

sub_page = None

if main_page == '1. Executive Summary & Core KPIs':
    sub_page = st.sidebar.radio('Select View:', ['Key Metrics Overview', 'Demographic Distributions'])

elif main_page == '2. Customer Engagement & Financials':
    sub_page = st.sidebar.radio('Select View:', ['Website Visits vs Total Spent', 'Tenure Days vs Lifetime Value', 'Acquisition Channel ROI'])

elif main_page == '3. Retention, Churn & Demographics':
    sub_page = st.sidebar.radio('Select View:', ['Gender & Country Churn Analysis', 'Subscription Plans & Payment Methods', 'Discounts & Refund Impact on Churn'])

elif main_page == '4. Payment Gateways & Spending Trends':
    sub_page = st.sidebar.radio('Select View:', ['Spending by Gender & Payment Method', 'Support Tickets & Delivery Delays by Churn Status'])

elif main_page == '5. Customer Satisfaction & Support Impact':
    sub_page = st.sidebar.radio('Select View:', ['Satisfaction Score Breakdown', 'Satisfaction vs Support Tickets'])

st.sidebar.markdown("---")
st.sidebar.subheader("Global Data Filters")

countries = ["All"] + list(df['country'].dropna().unique()) if 'country' in df.columns else ["All"]
selected_country = st.sidebar.selectbox("Country:", countries)

sub_types = ["All"] + list(df['subscription_type'].dropna().unique()) if 'subscription_type' in df.columns else ["All"]
selected_sub = st.sidebar.selectbox("Subscription Type:", sub_types)

if selected_country != "All":
    df = df[df['country'] == selected_country]
if selected_sub != "All":
    df = df[df['subscription_type'] == selected_sub]


# =========================================================
# SECTION 1: Executive Summary & Core KPIs
# =========================================================
if main_page == '1. Executive Summary & Core KPIs':
    st.title('Executive Summary & Core KPIs')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"${df['total_spent'].sum():,.0f}")
    with col2:
        st.metric("Avg Lifetime Value (LTV)", f"${df['lifetime_value'].mean():,.1f}")
    with col3:
        churn_rate = (df['churn'].mean() * 100) if 'churn' in df.columns else 0
        st.metric("Overall Churn Rate", f"{churn_rate:.1f}%")
    with col4:
        st.metric("Avg Satisfaction Score", f"{df['satisfaction_score'].mean():,.2f} / 5")

    st.markdown("---")

    if sub_page == 'Key Metrics Overview':
        st.info("Use the sidebar options to explore customer behavior and financial metrics.")
        c1, c2 = st.columns(2)
        with c1:
            prem_spend = df.groupby('premium_label')['total_spent'].mean().reset_index()
            fig_prem = px.bar(
                prem_spend, x='premium_label', y='total_spent', text_auto='.2f',
                title='Average Spending by Premium Status',
                color='premium_label', template="plotly_white",
                labels={'premium_label': 'User Tier', 'total_spent': 'Avg Total Spent ($)'}
            )
            st.plotly_chart(fig_prem, use_container_width=True)

        with c2:
            age_spend = df.groupby('age')['total_spent'].mean().reset_index()
            fig_age = px.line(
                age_spend, x='age', y='total_spent',
                title='Average Spending Trend by Customer Age',
                labels={'age': 'Customer Age', 'total_spent': 'Avg Total Spent ($)'},
                template="plotly_white"
            )
            st.plotly_chart(fig_age, use_container_width=True)

    elif sub_page == 'Demographic Distributions':
        fig_demo = px.histogram(
            df, x='age', color='premium_label', barmode='group',
            title='Customer Age Distribution by Premium Status',
            labels={'age': 'Customer Age', 'premium_label': 'User Tier'},
            template="plotly_white"
        )
        st.plotly_chart(fig_demo, use_container_width=True)


# =========================================================
# SECTION 2: Customer Engagement & Financials
# =========================================================
elif main_page == '2. Customer Engagement & Financials':
    st.title('Customer Engagement & Financial Analysis')

    if sub_page == "Website Visits vs Total Spent":
        col1, col2 = st.columns(2)
        with col1:
            df['visits_group'] = pd.cut(df['total_visits'], bins=4, labels=['1-8 Visits', '9-16 Visits', '17-24 Visits', '25+ Visits'])
            visits_spend = df.groupby(['visits_group', 'churn_label'], observed=False)['total_spent'].mean().reset_index()

            fig_bar_visits = px.bar(
                visits_spend, x='visits_group', y='total_spent', color='churn_label',
                barmode='group', text_auto='.1f',
                title='Average Spent ($) by Visit Groups & Retention Status',
                labels={'visits_group': 'Visits Category', 'total_spent': 'Avg Total Spent ($)', 'churn_label': 'Customer Status'},
                template="plotly_white"
            )
            st.plotly_chart(fig_bar_visits, use_container_width=True)

        with col2:
            visits_spending = df.groupby('total_visits')['total_spent'].mean().reset_index()
            fig_line1 = px.line(
                visits_spending, x='total_visits', y='total_spent',
                title='Average Total Spent Trend by Exact Visit Count',
                labels={'total_visits': 'Total Visits', 'total_spent': 'Avg Total Spent ($)'},
                template="plotly_white"
            )
            st.plotly_chart(fig_line1, use_container_width=True)

    elif sub_page == "Tenure Days vs Lifetime Value":
        df['tenure_bins'] = pd.cut(df['customer_tenure_days'], bins=4, labels=['New (<3 Months)', 'Established (3-6 Months)', 'Loyal (6-12 Months)', 'VIP (12+ Months)'])
        tenure_ltv = df.groupby(['tenure_bins', 'churn_label'], observed=False)['lifetime_value'].mean().reset_index()

        fig_tenure_ltv = px.bar(
            tenure_ltv, x='tenure_bins', y='lifetime_value', color='churn_label',
            barmode='group', text_auto='.1f',
            title='Average Lifetime Value (LTV) by Tenure Groups & Status',
            labels={'tenure_bins': 'Tenure Group', 'lifetime_value': 'Avg LTV ($)', 'churn_label': 'Customer Status'},
            template="plotly_white"
        )
        st.plotly_chart(fig_tenure_ltv, use_container_width=True)

    elif sub_page == "Acquisition Channel ROI":
        mkt_roi = df.groupby('acquisition_channel')[['marketing_spend_per_user', 'lifetime_value']].mean().reset_index()
        fig_roi = px.bar(
            mkt_roi, x='acquisition_channel', y=['marketing_spend_per_user', 'lifetime_value'],
            barmode='group', text_auto='.1f',
            title='Marketing Spend per User vs Lifetime Value (LTV) by Channel',
            labels={'acquisition_channel': 'Acquisition Channel', 'value': 'Amount ($)', 'variable': 'Metric'},
            template="plotly_white"
        )
        st.plotly_chart(fig_roi, use_container_width=True)


# =========================================================
# SECTION 3: Retention, Churn & Demographics
# =========================================================
elif main_page == '3. Retention, Churn & Demographics':
    st.title('Retention, Churn & Demographic Breakdown')

    if sub_page == "Gender & Country Churn Analysis":
        col1, col2 = st.columns(2)
        with col1:
            gender_churn = df.groupby(['gender', 'churn_label']).size().reset_index(name='count')
            fig_g_churn = px.bar(
                gender_churn, x='gender', y='count', color='churn_label',
                barmode='group', text_auto=True,
                title='Customer Retention Count by Gender',
                labels={'gender': 'Gender', 'count': 'Customer Count', 'churn_label': 'Customer Status'},
                template="plotly_white"
            )
            st.plotly_chart(fig_g_churn, use_container_width=True)

        with col2:
            country_churn = df.groupby(['country', 'churn_label']).size().reset_index(name='count')
            fig_c_churn = px.bar(
                country_churn, x='country', y='count', color='churn_label',
                barmode='group', text_auto=True,
                title='Customer Retention Status by Country',
                labels={'country': 'Country', 'count': 'Customer Count', 'churn_label': 'Customer Status'},
                template="plotly_white"
            )
            st.plotly_chart(fig_c_churn, use_container_width=True)

    elif sub_page == "Subscription Plans & Payment Methods":
        fig_sub_pay = px.histogram(
            df, x='payment_method', color='subscription_type', barmode='group',
            text_auto=True, title='Subscription Plan Distribution Across Payment Gateways',
            labels={'payment_method': 'Payment Method', 'subscription_type': 'Subscription Type'},
            template="plotly_white"
        )
        st.plotly_chart(fig_sub_pay, use_container_width=True)

    elif sub_page == "Discounts & Refund Impact on Churn":
        col1, col2 = st.columns(2)
        with col1:
            disc_churn = df.groupby(['discount_label', 'churn_label']).size().reset_index(name='count')
            fig_disc = px.bar(
                disc_churn, x='discount_label', y='count', color='churn_label',
                barmode='group', text_auto=True,
                title='Discount Usage Impact on Retention',
                labels={'discount_label': 'Discount Status', 'count': 'Customer Count', 'churn_label': 'Customer Status'},
                template="plotly_white"
            )
            st.plotly_chart(fig_disc, use_container_width=True)

        with col2:
            ref_churn = df.groupby(['refund_label', 'churn_label']).size().reset_index(name='count')
            fig_ref = px.bar(
                ref_churn, x='refund_label', y='count', color='churn_label',
                barmode='group', text_auto=True,
                title='Refund Request Impact on Retention',
                labels={'refund_label': 'Refund Status', 'count': 'Customer Count', 'churn_label': 'Customer Status'},
                template="plotly_white"
            )
            st.plotly_chart(fig_ref, use_container_width=True)


# =========================================================
# SECTION 4: Payment Gateways & Spending Trends
# =========================================================
elif main_page == '4. Payment Gateways & Spending Trends':
    st.title('Payment Gateways & Spending Analysis')

    if sub_page == "Spending by Gender & Payment Method":
        col1, col2 = st.columns(2)
        with col1:
            gender_spending = df.groupby('gender')['total_spent'].mean().reset_index()
            fig_g_spend = px.bar(
                gender_spending, x='gender', y='total_spent', text_auto='.2f',
                title='Average Total Spent ($) by Gender',
                labels={'gender': 'Gender', 'total_spent': 'Avg Total Spent ($)'},
                template="plotly_white"
            )
            st.plotly_chart(fig_g_spend, use_container_width=True)

        with col2:
            pay_spend = df.groupby('payment_method')['total_spent'].mean().reset_index()
            fig_p_spent = px.bar(
                pay_spend, x='payment_method', y='total_spent', text_auto='.2f',
                title='Average Total Spent ($) by Payment Gateway',
                labels={'payment_method': 'Payment Gateway', 'total_spent': 'Avg Total Spent ($)'},
                template="plotly_white"
            )
            st.plotly_chart(fig_p_spent, use_container_width=True)

    elif sub_page == "Support Tickets & Delivery Delays by Churn Status":
        col1, col2 = st.columns(2)
        with col1:
            tickets_churn = df.groupby('churn_label')['support_tickets'].mean().reset_index()
            fig_t = px.bar(
                tickets_churn, x='churn_label', y='support_tickets', text_auto='.2f',
                title='Average Support Tickets Count by Churn Status',
                labels={'churn_label': 'Customer Status', 'support_tickets': 'Avg Support Tickets'},
                template="plotly_white"
            )
            st.plotly_chart(fig_t, use_container_width=True)

        with col2:
            delay_churn = df.groupby('churn_label')['delivery_delay_days'].mean().reset_index()
            fig_d = px.bar(
                delay_churn, x='churn_label', y='delivery_delay_days', text_auto='.2f',
                title='Average Delivery Delay (Days) by Churn Status',
                labels={'churn_label': 'Customer Status', 'delivery_delay_days': 'Avg Delay (Days)'},
                template="plotly_white"
            )
            st.plotly_chart(fig_d, use_container_width=True)


# =========================================================
# SECTION 5: Customer Satisfaction & Support Impact
# =========================================================
elif main_page == '5. Customer Satisfaction & Support Impact':
    st.title('Customer Satisfaction & Support Impact')

    if sub_page == "Satisfaction Score Breakdown":
        col1, col2 = st.columns(2)
        with col1:
            fig_sat_c = px.histogram(
                df, x='satisfaction_score', color='churn_label', barmode='group',
                text_auto=True, title='Satisfaction Score Distribution (1-5) by Retention Status',
                labels={'satisfaction_score': 'Satisfaction Score (1 to 5)', 'churn_label': 'Customer Status'},
                template="plotly_white"
            )
            st.plotly_chart(fig_sat_c, use_container_width=True)

        with col2:
            delay_satisfaction = df.groupby('satisfaction_score')['delivery_delay_days'].mean().reset_index()
            fig_sat_d = px.line(
                delay_satisfaction, x='satisfaction_score', y='delivery_delay_days',
                title='Average Delivery Delay Days by Satisfaction Score',
                labels={'satisfaction_score': 'Satisfaction Score (1 to 5)', 'delivery_delay_days': 'Avg Delay Days'},
                template="plotly_white"
            )
            st.plotly_chart(fig_sat_d, use_container_width=True)

    elif sub_page == "Satisfaction vs Support Tickets":
        sat_tickets = df.groupby(['support_tickets', 'churn_label'])['satisfaction_score'].mean().reset_index()
        fig_bar_sat = px.bar(
            sat_tickets, x='support_tickets', y='satisfaction_score', color='churn_label',
            barmode='group', text_auto='.2f',
            title='Average Satisfaction Score by Support Ticket Count & Status',
            labels={'support_tickets': 'Number of Support Tickets', 'satisfaction_score': 'Avg Satisfaction Score (1-5)', 'churn_label': 'Customer Status'},
            template="plotly_white"
        )
        st.plotly_chart(fig_bar_sat, use_container_width=True)
