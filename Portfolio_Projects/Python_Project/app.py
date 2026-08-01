"""EV Adoption Behavior Analytics Dashboard"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="EV Adoption Behavior Dashboard",
    page_icon="🔋",
    layout="wide",
)

ADOPTION_ORDER = ["Low", "Medium", "High"]
COLOR_MAP = {"Low": "#e74c3c", "Medium": "#f5a623", "High": "#3ddc97"}
PLOT_TEMPLATE = "plotly_dark"
DATA_PATH = Path(__file__).parent / "ev_adoption_cleaned.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["ev_adoption_likelihood"] = pd.Categorical(
        df["ev_adoption_likelihood"], categories=ADOPTION_ORDER, ordered=True
    )

    # Composite/derived features -- combine correlated raw scores into single,
    # sharper signals instead of treating each one as equally important.
    df["awareness_composite"] = df[
        [
            "environmental_awareness_score",
            "technology_affinity_score",
            "government_incentive_awareness",
        ]
    ].mean(axis=1)
    df["anxiety_minus_knowledge"] = df["range_anxiety_score"] - df["ev_knowledge_score"]

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

st.markdown("")
ov1, ov2 = st.columns(2)

with ov1:
    split_counts = (
        filtered_df["ev_adoption_likelihood"]
        .value_counts()
        .reindex(ADOPTION_ORDER)
        .reset_index()
    )
    split_counts.columns = ["Likelihood", "Count"]
    fig_split = px.pie(
        split_counts,
        names="Likelihood",
        values="Count",
        hole=0.62,
        color="Likelihood",
        color_discrete_map=COLOR_MAP,
        template=PLOT_TEMPLATE,
        title="Adoption Likelihood Split",
    )
    fig_split.update_traces(textinfo="percent+label")
    st.plotly_chart(fig_split, use_container_width=True)

with ov2:
    # Diverging bar: compare High-adopter vs Low-adopter averages on the factors
    # that matter most, including the composite features -- one bar extends right
    # (High), the other left (Low, plotted as a negative value), so the visual gap
    # between the two tips shows how much a factor actually separates the groups.
    compare_cols = {
        "EV Knowledge": "ev_knowledge_score",
        "Awareness Composite": "awareness_composite",
        "Range Anxiety (lower = better)": "range_anxiety_score",
        "Anxiety − Knowledge Gap (lower = better)": "anxiety_minus_knowledge",
    }
    diverge_rows = []
    for label, col in compare_cols.items():
        high_val = filtered_df.loc[
            filtered_df["ev_adoption_likelihood"] == "High", col
        ].mean()
        low_val = filtered_df.loc[
            filtered_df["ev_adoption_likelihood"] == "Low", col
        ].mean()
        diverge_rows.append({"Factor": label, "High": high_val, "Low": low_val})
    diverge_df = pd.DataFrame(diverge_rows)

    fig_diverge = go.Figure()
    fig_diverge.add_bar(
        name="High Adopters",
        y=diverge_df["Factor"],
        x=diverge_df["High"],
        orientation="h",
        marker_color=COLOR_MAP["High"],
    )
    fig_diverge.add_bar(
        name="Low Adopters",
        y=diverge_df["Factor"],
        x=-diverge_df["Low"],
        orientation="h",
        marker_color=COLOR_MAP["Low"],
    )
    fig_diverge.update_layout(
        barmode="overlay",
        template=PLOT_TEMPLATE,
        legend_title="",
        xaxis_title="← Low Adopters   |   High Adopters →",
        title="What Actually Separates Adopters From Skeptics",
    )
    st.plotly_chart(fig_diverge, use_container_width=True)
    st.caption("The anxiety-knowledge gap shows the widest split of any single factor.")

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
            template=PLOT_TEMPLATE,
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
            template=PLOT_TEMPLATE,
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
        template=PLOT_TEMPLATE,
        title="Adoption Likelihood % by City Type",
        labels={"pct": "% of customers"},
    )
    st.plotly_chart(fig_city, use_container_width=True)

    # Income boxplot above shows spread; this shows the adoption RATE directly per
    # bracket, which is a more actionable "where's the cutoff" view for targeting.
    income_bracket_df = filtered_df.copy()
    income_bracket_df["income_bracket"] = pd.cut(
        income_bracket_df["annual_income"],
        bins=[0, 25000, 40000, 60000, 90000, float("inf")],
        labels=["<25k", "25k-40k", "40k-60k", "60k-90k", "90k+"],
    )
    bracket_rate = (
        income_bracket_df.groupby("income_bracket", observed=True)[
            "ev_adoption_likelihood"
        ]
        .apply(lambda s: (s == "High").mean() * 100)
        .reindex(["<25k", "25k-40k", "40k-60k", "60k-90k", "90k+"])
        .reset_index()
    )
    bracket_rate.columns = ["income_bracket", "pct_high"]

    fig_bracket = px.line(
        bracket_rate,
        x="income_bracket",
        y="pct_high",
        markers=True,
        text="pct_high",
        template=PLOT_TEMPLATE,
        color_discrete_sequence=[COLOR_MAP["High"]],
        title="% High Adoption by Income Bracket",
        labels={"income_bracket": "Income bracket", "pct_high": "% High adoption"},
    )
    fig_bracket.update_traces(
        texttemplate="%{text:.1f}%", textposition="top center", line=dict(width=3)
    )
    fig_bracket.update_yaxes(range=[0, 100])
    st.plotly_chart(fig_bracket, use_container_width=True)

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
        template=PLOT_TEMPLATE,
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
            template=PLOT_TEMPLATE,
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
            template=PLOT_TEMPLATE,
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
        template=PLOT_TEMPLATE,
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

    col3, col4 = st.columns(2)

    with col3:
        # Interaction: does public accessibility compound with home charging, or does
        # having one make the other redundant?
        access_df = filtered_df.copy()
        access_df["accessibility_band"] = pd.cut(
            access_df["charging_station_accessibility"],
            bins=[0, 4, 7, 10],
            labels=["Low", "Medium", "High"],
            include_lowest=True,
        )
        access_df["home_charging_label"] = access_df["home_charging_available"].map(
            {0: "No", 1: "Yes"}
        )
        access_rate = (
            access_df.groupby(
                ["accessibility_band", "home_charging_label"], observed=True
            )["ev_adoption_likelihood"]
            .apply(lambda s: (s == "High").mean() * 100)
            .reset_index(name="pct_high")
        )
        fig_access = px.bar(
            access_rate,
            x="accessibility_band",
            y="pct_high",
            color="home_charging_label",
            barmode="group",
            template=PLOT_TEMPLATE,
            color_discrete_map={"No": COLOR_MAP["Low"], "Yes": COLOR_MAP["High"]},
            title="Charging Accessibility × Home Charging",
            labels={
                "accessibility_band": "Public accessibility",
                "pct_high": "% High adoption",
                "home_charging_label": "Home charging",
            },
        )
        st.plotly_chart(fig_access, use_container_width=True)
        st.caption(
            "Public accessibility and home charging compound — the two together beat either alone."
        )

    with col4:
        # Cost vs. energy usage -- same energy consumption can still mean different
        # charging cost, since electricity price itself varies by region/provider.
        fig_cost_energy = px.scatter(
            filtered_df,
            x="monthly_energy_consumption_kwh",
            y="monthly_charging_cost",
            color="electricity_cost_per_kwh",
            template=PLOT_TEMPLATE,
            trendline="ols",
            color_continuous_scale="Viridis",
            opacity=0.5,
            title="Charging Cost vs. Energy Consumption",
            labels={
                "monthly_energy_consumption_kwh": "Monthly energy (kWh)",
                "monthly_charging_cost": "Monthly charging cost (₹)",
                "electricity_cost_per_kwh": "₹/kWh",
            },
        )
        st.plotly_chart(fig_cost_energy, use_container_width=True)
        st.caption(
            "Cost rises with energy use, but the electricity rate (color) explains why similar usage can cost different amounts."
        )

# --- Psychology & Awareness ---
with tab_psych:
    st.subheader("Psychology & Awareness")

    # Correlation ranking now includes the two composite features alongside the
    # 6 raw scores, so we can see whether combining correlated signals actually
    # produces a stronger single predictor than any individual score.
    score_cols = [
        "environmental_awareness_score",
        "technology_affinity_score",
        "range_anxiety_score",
        "battery_replacement_concern",
        "ev_knowledge_score",
        "government_incentive_awareness",
        "awareness_composite",
        "anxiety_minus_knowledge",
    ]
    target_numeric = filtered_df["ev_adoption_likelihood"].cat.codes
    correlations = (
        filtered_df[score_cols].corrwith(target_numeric).sort_values().reset_index()
    )
    correlations.columns = ["factor", "correlation"]
    is_composite = correlations["factor"].isin(
        ["awareness_composite", "anxiety_minus_knowledge"]
    )

    fig_corr = px.bar(
        correlations,
        x="correlation",
        y="factor",
        orientation="h",
        title="Correlation of Readiness Scores with Adoption Likelihood",
        template=PLOT_TEMPLATE,
        color=is_composite.map({True: "Composite", False: "Raw score"}),
        color_discrete_map={"Composite": "#8B7CF6", "Raw score": "#5A5F73"},
        labels={"color": ""},
    )
    st.plotly_chart(fig_corr, use_container_width=True)
    st.caption(
        "The anxiety-knowledge gap and awareness composite (highlighted) combine several "
        "correlated raw scores into one signal each — both rank among the strongest predictors."
    )

    # Interaction matrix: does knowledge offset anxiety, or do they act independently?
    matrix_df = filtered_df.copy()
    matrix_df["Anxiety"] = pd.cut(
        matrix_df["range_anxiety_score"],
        bins=[0, 3, 7, 10],
        labels=["Low", "Medium", "High"],
        include_lowest=True,
    )
    matrix_df["Knowledge"] = pd.cut(
        matrix_df["ev_knowledge_score"],
        bins=[0, 3, 7, 10],
        labels=["Low", "Medium", "High"],
        include_lowest=True,
    )
    matrix = (
        matrix_df.groupby(["Anxiety", "Knowledge"], observed=True)[
            "ev_adoption_likelihood"
        ]
        .apply(lambda s: (s == "High").mean() * 100)
        .unstack()
        .reindex(index=["High", "Medium", "Low"], columns=["Low", "Medium", "High"])
    )
    fig_matrix = px.imshow(
        matrix,
        text_auto=".0f",
        template=PLOT_TEMPLATE,
        aspect="auto",
        color_continuous_scale=[[0, "#e74c3c"], [0.5, "#1B1F2B"], [1, "#3ddc97"]],
        labels=dict(color="% High Adoption"),
        title="Range Anxiety × EV Knowledge — % High Adoption",
    )
    fig_matrix.update_layout(xaxis_title="EV Knowledge", yaxis_title="Range Anxiety")
    st.plotly_chart(fig_matrix, use_container_width=True)
    st.caption(
        "Knowledge offsets anxiety more than anxiety alone predicts adoption: high-anxiety "
        "customers with high knowledge still convert at a meaningful rate, while "
        "high-anxiety/low-knowledge customers barely convert at all."
    )

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
        template=PLOT_TEMPLATE,
        title="Adoption Likelihood % by Previous EV Experience",
        labels={"pct": "% of customers", "previous_ev_experience": ""},
    )
    st.plotly_chart(fig_exp, use_container_width=True)
    st.caption(
        "Prior EV experience is a real but moderate lever — smaller than the anxiety-knowledge gap above."
    )

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
            template=PLOT_TEMPLATE,
            color="pct_high",
            color_continuous_scale=["#5A5F73", "#3ddc97"],
            hover_data=["segment_size"],
        )
        st.plotly_chart(fig_seg, use_container_width=True)
        st.caption(
            "Urban, home-charging-enabled segments dominate the top of this ranking across vehicle types."
        )

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
