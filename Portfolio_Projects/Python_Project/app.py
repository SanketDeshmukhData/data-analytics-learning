"""EV Adoption Behavior Analytics Dashboard"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="EV Adoption Behavior Dashboard",
    page_icon="🔋",
    layout="wide",
)

ADOPTION_ORDER = ["Low", "Medium", "High"]
COLOR_MAP = {"Low": "#e74c3c", "Medium": "#f39c12", "High": "#2ecc71"}
DATA_PATH = Path(__file__).parent / "ev_adoption_cleaned.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["ev_adoption_likelihood"] = pd.Categorical(
        df["ev_adoption_likelihood"], categories=ADOPTION_ORDER, ordered=True
    )
    return df


df = load_data()

# --- Sidebar filters ---
st.sidebar.header("Filters")

city_filter = st.sidebar.multiselect(
    "City type",
    options=sorted(df["city_type"].unique()),
    default=sorted(df["city_type"].unique()),
)

vehicle_filter = st.sidebar.multiselect(
    "Current vehicle type",
    options=sorted(df["current_vehicle_type"].unique()),
    default=sorted(df["current_vehicle_type"].unique()),
)

income_min, income_max = int(df["annual_income"].min()), int(df["annual_income"].max())
income_range = st.sidebar.slider(
    "Annual income range",
    min_value=income_min,
    max_value=income_max,
    value=(income_min, income_max),
)

home_charging_filter = st.sidebar.multiselect(
    "Home charging available",
    options=df["home_charging_available"].unique().tolist(),
    default=df["home_charging_available"].unique().tolist(),
    format_func=lambda x: "Yes" if x == 1 else "No",
)

filtered_df = df[
    (df["city_type"].isin(city_filter))
    & (df["current_vehicle_type"].isin(vehicle_filter))
    & (df["annual_income"].between(income_range[0], income_range[1]))
    & (df["home_charging_available"].isin(home_charging_filter))
]

st.sidebar.markdown(f"**{len(filtered_df):,}** customers match current filters")

# --- Header + KPIs ---
st.title("🔋 EV Adoption Behavior Analytics Dashboard")
st.caption(
    "Which customer segments are most likely to adopt EVs, and why — "
    "for Business Managers, Marketing, and Product Strategy teams."
)

if filtered_df.empty:
    st.warning(
        "No customers match the current filter selection. Adjust filters in the sidebar."
    )
    st.stop()

pct_high = (filtered_df["ev_adoption_likelihood"] == "High").mean() * 100
avg_income = filtered_df["annual_income"].mean()
avg_range_anxiety = filtered_df["range_anxiety_score"].mean()

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Customers (filtered)", f"{len(filtered_df):,}")
kpi2.metric("% High adoption likelihood", f"{pct_high:.1f}%")
kpi3.metric("Avg. annual income", f"₹{avg_income:,.0f}")

st.divider()

tab_demo, tab_econ, tab_infra, tab_psych, tab_synth = st.tabs(
    [
        "👥 Demographics",
        "💰 Economics",
        "🔌 Infrastructure & Range",
        "🧠 Psychology & Awareness",
        "🎯 Best-Fit Segments",
    ]
)

# --- Demographics ---
with tab_demo:
    st.subheader("Demographic Profile")
    col1, col2 = st.columns(2)

    with col1:
        fig_age = px.box(
            filtered_df,
            x="ev_adoption_likelihood",
            y="age",
            category_orders={"ev_adoption_likelihood": ADOPTION_ORDER},
            color="ev_adoption_likelihood",
            color_discrete_map=COLOR_MAP,
            title="Age by Adoption Likelihood",
        )
        st.plotly_chart(fig_age, use_container_width=True)

    with col2:
        fig_income = px.box(
            filtered_df,
            x="ev_adoption_likelihood",
            y="annual_income",
            category_orders={"ev_adoption_likelihood": ADOPTION_ORDER},
            color="ev_adoption_likelihood",
            color_discrete_map=COLOR_MAP,
            title="Income by Adoption Likelihood",
        )
        st.plotly_chart(fig_income, use_container_width=True)

    city_props = (
        (
            pd.crosstab(
                filtered_df["city_type"],
                filtered_df["ev_adoption_likelihood"],
                normalize="index",
            )[ADOPTION_ORDER]
            * 100
        )
        .reset_index()
        .melt(id_vars="city_type", var_name="ev_adoption_likelihood", value_name="pct")
    )

    fig_city = px.bar(
        city_props,
        x="city_type",
        y="pct",
        color="ev_adoption_likelihood",
        category_orders={"ev_adoption_likelihood": ADOPTION_ORDER},
        color_discrete_map=COLOR_MAP,
        title="Adoption Likelihood % by City Type",
        labels={"pct": "% of customers"},
    )
    st.plotly_chart(fig_city, use_container_width=True)

    st.caption("Income and city type separate adoption groups more clearly than age.")

# --- Economics ---
with tab_econ:
    st.subheader("Cost Comparison: Fuel vs. Charging")

    cost_by_group = (
        filtered_df.groupby("ev_adoption_likelihood", observed=True)[
            ["fuel_expense_per_month", "monthly_charging_cost"]
        ]
        .mean()
        .reindex(ADOPTION_ORDER)
        .reset_index()
        .melt(
            id_vars="ev_adoption_likelihood", var_name="cost_type", value_name="amount"
        )
    )

    fig_cost = px.bar(
        cost_by_group,
        x="ev_adoption_likelihood",
        y="amount",
        color="cost_type",
        barmode="group",
        category_orders={"ev_adoption_likelihood": ADOPTION_ORDER},
        title="Avg Monthly Fuel vs. Charging Cost, by Adoption Likelihood",
        labels={
            "amount": "₹ per month",
            "ev_adoption_likelihood": "Adoption likelihood",
        },
    )
    st.plotly_chart(fig_cost, use_container_width=True)

    avg_savings = (
        filtered_df["fuel_expense_per_month"] - filtered_df["monthly_charging_cost"]
    ).mean()
    st.metric(
        "Avg. potential monthly savings by switching to EV", f"₹{avg_savings:,.0f}"
    )

    st.caption(
        "Cost savings are broadly similar across all three adoption groups in this data, "
        "so cost alone doesn't distinguish likely adopters — a departure from published EV "
        "adoption research, where total cost of ownership is typically a stronger driver."
    )

# --- Infrastructure & Range ---
with tab_infra:
    st.subheader("Infrastructure & Range")
    col1, col2 = st.columns(2)

    with col1:
        fig_dist = px.box(
            filtered_df,
            x="ev_adoption_likelihood",
            y="nearest_charging_station_km",
            category_orders={"ev_adoption_likelihood": ADOPTION_ORDER},
            color="ev_adoption_likelihood",
            color_discrete_map=COLOR_MAP,
            title="Distance to Nearest Station (actual km)",
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    with col2:
        fig_anx = px.box(
            filtered_df,
            x="ev_adoption_likelihood",
            y="range_anxiety_score",
            category_orders={"ev_adoption_likelihood": ADOPTION_ORDER},
            color="ev_adoption_likelihood",
            color_discrete_map=COLOR_MAP,
            title="Range Anxiety Score (perceived)",
        )
        st.plotly_chart(fig_anx, use_container_width=True)

    home_props = (
        (
            pd.crosstab(
                filtered_df["home_charging_available"],
                filtered_df["ev_adoption_likelihood"],
                normalize="index",
            )[ADOPTION_ORDER]
            * 100
        )
        .reset_index()
        .melt(
            id_vars="home_charging_available",
            var_name="ev_adoption_likelihood",
            value_name="pct",
        )
    )
    home_props["home_charging_available"] = home_props["home_charging_available"].map(
        {0: "No", 1: "Yes"}
    )

    fig_home = px.bar(
        home_props,
        x="home_charging_available",
        y="pct",
        color="ev_adoption_likelihood",
        category_orders={"ev_adoption_likelihood": ADOPTION_ORDER},
        color_discrete_map=COLOR_MAP,
        title="Adoption Likelihood % by Home Charging Availability",
        labels={
            "pct": "% of customers",
            "home_charging_available": "Home charging available",
        },
    )
    st.plotly_chart(fig_home, use_container_width=True)

    st.caption(
        "Perceived range anxiety separates adoption groups more sharply than actual distance "
        "to the nearest station — perception appears to be a bigger barrier than physical access."
    )

# --- Psychology & Awareness ---
with tab_psych:
    st.subheader("Psychology & Awareness")

    score_cols = [
        "environmental_awareness_score",
        "technology_affinity_score",
        "range_anxiety_score",
        "battery_replacement_concern",
        "ev_knowledge_score",
        "government_incentive_awareness",
    ]
    target_numeric = filtered_df["ev_adoption_likelihood"].cat.codes
    correlations = (
        filtered_df[score_cols].corrwith(target_numeric).sort_values().reset_index()
    )
    correlations.columns = ["factor", "correlation"]

    fig_corr = px.bar(
        correlations,
        x="correlation",
        y="factor",
        orientation="h",
        title="Correlation of Readiness Scores with Adoption Likelihood",
        color="correlation",
        color_continuous_scale="Purples",
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    exp_props = (
        (
            pd.crosstab(
                filtered_df["previous_ev_experience"],
                filtered_df["ev_adoption_likelihood"],
                normalize="index",
            )[ADOPTION_ORDER]
            * 100
        )
        .reset_index()
        .melt(
            id_vars="previous_ev_experience",
            var_name="ev_adoption_likelihood",
            value_name="pct",
        )
    )
    exp_props["previous_ev_experience"] = exp_props["previous_ev_experience"].map(
        {0: "No prior experience", 1: "Prior experience"}
    )

    fig_exp = px.bar(
        exp_props,
        x="previous_ev_experience",
        y="pct",
        color="ev_adoption_likelihood",
        category_orders={"ev_adoption_likelihood": ADOPTION_ORDER},
        color_discrete_map=COLOR_MAP,
        title="Adoption Likelihood % by Previous EV Experience",
        labels={"pct": "% of customers", "previous_ev_experience": ""},
    )
    st.plotly_chart(fig_exp, use_container_width=True)

# --- Best-fit segments ---
with tab_synth:
    st.subheader("Best-Fit Customer Segments")
    st.caption(
        "Segments below require at least 200 customers, to avoid ranking on small, unreliable groups."
    )

    segment_summary = (
        filtered_df.groupby(
            ["city_type", "current_vehicle_type", "home_charging_available"],
            observed=True,
        )
        .agg(
            segment_size=("ev_adoption_likelihood", "size"),
            pct_high=("ev_adoption_likelihood", lambda x: (x == "High").mean() * 100),
        )
        .reset_index()
    )
    segment_summary = segment_summary[segment_summary["segment_size"] >= 200]

    if segment_summary.empty:
        st.warning(
            "No segment has 200+ customers under the current filters — widen your filter selection."
        )
    else:
        top_segments = segment_summary.sort_values("pct_high", ascending=False).head(10)
        top_segments["home_charging_available"] = top_segments[
            "home_charging_available"
        ].map({0: "No home charging", 1: "Home charging"})
        top_segments["segment_label"] = (
            top_segments["city_type"]
            + " / "
            + top_segments["current_vehicle_type"]
            + " / "
            + top_segments["home_charging_available"]
        )

        fig_seg = px.bar(
            top_segments.sort_values("pct_high"),
            x="pct_high",
            y="segment_label",
            orientation="h",
            title="Top Segments by % High Adoption Likelihood (min. 200 customers)",
            labels={
                "pct_high": "% High adoption likelihood",
                "segment_label": "Segment",
            },
            color="pct_high",
            color_continuous_scale="Greens",
            hover_data=["segment_size"],
        )
        st.plotly_chart(fig_seg, use_container_width=True)

        st.dataframe(
            top_segments[
                [
                    "city_type",
                    "current_vehicle_type",
                    "home_charging_available",
                    "segment_size",
                    "pct_high",
                ]
            ]
            .rename(
                columns={"pct_high": "% High adoption", "segment_size": "Segment size"}
            )
            .reset_index(drop=True),
            use_container_width=True,
        )

st.divider()
st.caption(
    "Data: global EV adoption behavior dataset (50,000 rows, synthetic). "
    "Cost and incentive-awareness findings diverge from published EV adoption research — "
    "see project notes for details."
)
