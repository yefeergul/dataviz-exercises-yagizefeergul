import streamlit as st
import pandas as pd
import plotly.express as px


# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CO2 Dashboard",
    page_icon="🌱",
    layout="wide"
)


# ── DATA ──────────────────────────────────────────────────────────────────────
# Streamlit reruns the script whenever a widget changes.
# @st.cache_data stores the loaded CSV and avoids reading it again and again.
@st.cache_data
def load_data():
    # The Python file and CSV file must be in the same folder.
    df = pd.read_csv("co2_emissions.csv")

    # Convert Year column into a real date column for date filtering.
    df["Date"] = pd.to_datetime(df["Year"].astype(str) + "-01-01")

    return df


df = load_data()


# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("🌱 CO2 Emissions Explorer")
st.caption("Source: Our World in Data — ourworldindata.org/co2-emissions")


# ── TASK 1: SIDEBAR WITH 5 WIDGETS ────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    # 1) Selectbox for Region, including "All"
    regions = ["All"] + sorted(df["Region"].dropna().unique().tolist())

    selected_region = st.selectbox(
        "Select Region",
        regions
    )

    # Chained filter: countries change according to selected region
    if selected_region == "All":
        region_df = df.copy()
    else:
        region_df = df[df["Region"] == selected_region]

    # 2) Multiselect for Countries
    available_countries = sorted(region_df["Country"].dropna().unique().tolist())

    selected_countries = st.multiselect(
        "Select Countries",
        available_countries,
        default=available_countries[:5]
    )

    # Guard: empty country selection
    if len(selected_countries) == 0:
        st.warning("Please select at least one country.")
        st.stop()

    # 3) Date input for date range
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()

    selected_dates = st.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Guard: incomplete date range
    if len(selected_dates) != 2:
        st.warning("Please select a complete start and end date.")
        st.stop()

    # Convert selected dates to pandas Timestamp before filtering
    start_date = pd.Timestamp(selected_dates[0])
    end_date = pd.Timestamp(selected_dates[1])

    # 4) Radio for Metric
    metric_options = {
        "Total CO2 (Mt)": "CO2_Mt",
        "CO2 per capita": "CO2_per_capita"
    }

    selected_metric_label = st.radio(
        "Select Metric",
        list(metric_options.keys())
    )

    selected_metric = metric_options[selected_metric_label]

    # 5) Checkbox for highlighting top emitter
    highlight_top = st.checkbox("Show only top emitter highlighted")


# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
filtered = df[
    (df["Country"].isin(selected_countries)) &
    (df["Date"] >= start_date) &
    (df["Date"] <= end_date)
].copy()

if selected_region != "All":
    filtered = filtered[filtered["Region"] == selected_region]

if filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()


# ── TASK 2: FILTER SUMMARY CAPTION ────────────────────────────────────────────
country_count = filtered["Country"].nunique()
record_count = len(filtered)

st.caption(
    f"{country_count} countries | {record_count} records | "
    f"Region: {selected_region} | "
    f"Date range: {start_date.year}–{end_date.year} | "
    f"Metric: {selected_metric_label}"
)


# ── EXTENSION: KPI ROW ABOVE THE CHARTS ───────────────────────────────────────
last_year = filtered["Year"].max()
first_year = filtered["Year"].min()

last_year_df = filtered[filtered["Year"] == last_year]
first_year_df = filtered[filtered["Year"] == first_year]

total_last_year = last_year_df[selected_metric].sum()
total_first_year = first_year_df[selected_metric].sum()

if total_first_year != 0:
    percent_change = ((total_last_year - total_first_year) / total_first_year) * 100
else:
    percent_change = 0

highest_country_last_year = (
    last_year_df.groupby("Country")[selected_metric]
    .sum()
    .idxmax()
)

kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric(
    label=f"Total {selected_metric_label} in {last_year}",
    value=f"{total_last_year:,.2f}"
)

kpi2.metric(
    label=f"% Change from {first_year} to {last_year}",
    value=f"{percent_change:.2f}%"
)

kpi3.metric(
    label=f"Highest in {last_year}",
    value=highest_country_last_year
)


# ── TASK 3: TWO CHARTS REACTING TO ALL FILTERS ────────────────────────────────
col_left, col_right = st.columns([2, 1])


with col_left:
    # Line chart
    # Colour type: categorical colour for countries.
    # If highlight is active, grey-and-highlight colour is used.

    line_df = filtered.copy()

    if highlight_top:
        top_country = (
            line_df.groupby("Country")[selected_metric]
            .sum()
            .idxmax()
        )

        line_df["Highlight"] = line_df["Country"].apply(
            lambda country: top_country if country == top_country else "Other countries"
        )

        color_map = {
            top_country: "#1f77b4",
            "Other countries": "lightgrey"
        }

        fig_line = px.line(
            line_df,
            x="Date",
            y=selected_metric,
            color="Highlight",
            line_group="Country",
            title=f"{top_country} is the highest emitter in the selected range",
            color_discrete_map=color_map,
            template="plotly_white"
        )

        # Label the highlighted country at the end of its line
        top_line = line_df[line_df["Country"] == top_country].sort_values("Date")

        if not top_line.empty:
            last_point = top_line.iloc[-1]

            fig_line.add_scatter(
                x=[last_point["Date"]],
                y=[last_point[selected_metric]],
                mode="text",
                text=[top_country],
                textposition="middle right",
                showlegend=False
            )

    else:
        fig_line = px.line(
            line_df,
            x="Date",
            y=selected_metric,
            color="Country",
            title=f"{selected_metric_label} trend over time for selected countries",
            template="plotly_white"
        )

    fig_line.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title=dict(
            font=dict(color="black", size=18)
        ),
        font=dict(color="black"),
        xaxis_title="Year",
        yaxis_title=selected_metric_label,
        legend_title_text="Country",
        legend=dict(
            font=dict(color="black"),
            title=dict(font=dict(color="black"))
        )
    )

    fig_line.update_xaxes(
        tickfont=dict(color="black"),
        title_font=dict(color="black"),
        gridcolor="lightgrey"
    )

    fig_line.update_yaxes(
        tickfont=dict(color="black"),
        title_font=dict(color="black"),
        gridcolor="lightgrey"
    )

    st.plotly_chart(fig_line, width="stretch")


with col_right:
    # Bar chart
    # Colour type: sequential colour based on emission value.

    bar_df = (
        filtered[filtered["Year"] == last_year]
        .groupby("Country", as_index=False)[selected_metric]
        .sum()
        .sort_values(selected_metric, ascending=False)
    )

    fig_bar = px.bar(
        bar_df,
        x=selected_metric,
        y="Country",
        orientation="h",
        color=selected_metric,
        title=f"Ranking in {last_year} by {selected_metric_label}",
        template="plotly_white"
    )

    fig_bar.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title=dict(
            font=dict(color="black", size=18)
        ),
        font=dict(color="black"),
        xaxis_title=selected_metric_label,
        yaxis_title="Country",
        coloraxis_showscale=False
    )

    fig_bar.update_xaxes(
        tickfont=dict(color="black"),
        title_font=dict(color="black"),
        gridcolor="lightgrey"
    )

    fig_bar.update_yaxes(
        autorange="reversed",
        tickfont=dict(color="black"),
        title_font=dict(color="black")
    )

    st.plotly_chart(fig_bar, width="stretch")