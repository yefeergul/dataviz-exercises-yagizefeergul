"""
Lecture 9 Exercise - World Happiness Dashboard
==============================================

Run with:
    streamlit run lecture09_exercise_final_working.py

Dashboard purpose (REQUIRED):
# PURPOSE: This dashboard helps users explore global happiness scores, compare regions,
# and understand how socioeconomic factors such as GDP relate to national well-being.

BBD colour rule:
# COLOUR TYPE comments are written next to each chart's colour argument.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ------------------------------------------------------------
# Page configuration must be near the top of the Streamlit app
# ------------------------------------------------------------
st.set_page_config(
    page_title="Global Well-being Monitor",
    page_icon="📊",
    layout="wide",
)


# ------------------------------------------------------------
# Data loading
# ------------------------------------------------------------
@st.cache_data
def get_clean_data() -> pd.DataFrame:
    """Load and clean the World Happiness 2023 dataset."""

    app_folder = Path(__file__).resolve().parent

    csv_candidates = [
        app_folder / "world_happiness_2023.csv",
        app_folder / "data" / "world_happiness_2023.csv",
    ]

    csv_path = None

    for candidate in csv_candidates:
        if candidate.exists():
            csv_path = candidate
            break

    if csv_path is None:
        st.error(
            "CSV file not found. Put 'world_happiness_2023.csv' in the same folder "
            "as this Python file, or inside a 'data' folder."
        )
        st.stop()

    raw_data = pd.read_csv(csv_path)

    raw_data.columns = [
        "Country",
        "Region",
        "Score",
        "GDP",
        "Social_Support",
        "Life_Expectancy",
        "Freedom",
        "Generosity",
        "Corruption",
    ]

    return raw_data


data_pool = get_clean_data()
global_mean = data_pool["Score"].mean()


# ------------------------------------------------------------
# Simple visual styling
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
    }
    [data-testid="metric-container"] {
        background-color: #FAFAFA;
        border: 1px solid #E0E0E0;
        padding: 0.8rem 1rem;
        border-radius: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# TASK 1: Title and caption
# ------------------------------------------------------------
st.title("📊 Global Well-being & Happiness Monitor")

st.write(
    "An interactive exploration of socioeconomic factors and their relationship "
    "with global life satisfaction scores."
)

st.divider()


# ------------------------------------------------------------
# TASK 2: Sidebar filters
# ------------------------------------------------------------
with st.sidebar:
    st.subheader("Data Controls")

    all_regions = ["All"] + sorted(data_pool["Region"].unique().tolist())

    target_region = st.selectbox(
        "Filter by Geographic Region:",
        all_regions,
    )

    max_display = st.slider(
        "Number of top countries to display:",
        min_value=5,
        max_value=30,
        value=15,
    )


if target_region == "All":
    filtered = data_pool.copy()
else:
    filtered = data_pool[data_pool["Region"] == target_region]


view_data = filtered.nlargest(max_display, "Score")


# ------------------------------------------------------------
# TASK 3: KPI row - 3 st.metric() cards
# ------------------------------------------------------------
active_count = len(view_data)

if active_count > 0:
    zone_mean = view_data["Score"].mean()
    mean_variance = zone_mean - global_mean

    top_row = view_data.sort_values("Score", ascending=False).iloc[0]
    top_nation = top_row["Country"]
    top_score = top_row["Score"]
else:
    zone_mean = 0
    mean_variance = 0
    top_nation = "None"
    top_score = 0


metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.metric(
        label="Countries Shown",
        value=active_count,
    )

with metric_col2:
    st.metric(
        label="Average Score",
        value=f"{zone_mean:.2f}",
        delta=f"{mean_variance:+.2f} vs Global",
    )

with metric_col3:
    st.metric(
        label="Highest Ranked Nation",
        value=top_nation,
        delta=f"Score: {top_score:.2f}",
    )


st.divider()


# ------------------------------------------------------------
# TASK 4: Two-column layout - two charts
# ------------------------------------------------------------
left_panel, right_panel = st.columns([3, 2])


with left_panel:
    st.markdown("### Countries with the Highest Happiness Scores")

    bar_data = view_data.sort_values("Score", ascending=True)

    fig_bars = px.bar(
        bar_data,
        x="Score",
        y="Country",
        orientation="h",
        color="Score",  # COLOUR TYPE: sequential
        color_continuous_scale="Blues",
        labels={
            "Score": "Happiness Index (0-10)",
            "Country": "",
        },
        title="Top countries show stronger happiness scores",
    )

    fig_bars.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Arial",
            color="black",
        ),
        title_font=dict(
            color="black",
            size=16,
        ),
        xaxis=dict(
            range=[0, 8.5],
            showgrid=True,
            gridcolor="#EFEFEF",
            tickfont=dict(color="black"),
            title_font=dict(color="black"),
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color="black", size=12),
            title_font=dict(color="black"),
        ),
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=50, b=10),
    )

    st.plotly_chart(fig_bars, use_container_width=True)


with right_panel:
    st.markdown("### GDP and Happiness Move Together")

    fig_scatter = px.scatter(
        filtered,
        x="GDP",
        y="Score",
        hover_name="Country",
        color="Region",  # COLOUR TYPE: categorical
        color_discrete_sequence=px.colors.qualitative.Dark2,
        labels={
            "GDP": "Gross Domestic Product (Log)",
            "Score": "Happiness Score",
            "Region": "Region",
        },
        title="Countries with higher GDP often report higher happiness",
    )

    fig_scatter.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Arial",
            color="black",
        ),
        title_font=dict(
            color="black",
            size=16,
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#EFEFEF",
            tickfont=dict(color="black"),
            title_font=dict(color="black"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#EFEFEF",
            tickfont=dict(color="black"),
            title_font=dict(color="black"),
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="left",
            x=0,
            font=dict(color="black"),
            title_font=dict(color="black"),
        ),
        margin=dict(l=10, r=10, t=50, b=10),
    )

    st.plotly_chart(fig_scatter, use_container_width=True)


# ------------------------------------------------------------
# EXTENSION: Third chart using a DIVERGING colour scale
# ------------------------------------------------------------
st.divider()

st.markdown("### Selected Countries Compared with the Global Average")

extension_data = view_data.copy()
extension_data["Difference_from_Global"] = extension_data["Score"] - global_mean

fig_diverging = px.bar(
    extension_data.sort_values("Difference_from_Global", ascending=True),
    x="Difference_from_Global",
    y="Country",
    orientation="h",
    color="Difference_from_Global",  # COLOUR TYPE: diverging
    color_continuous_scale="RdBu",
    color_continuous_midpoint=0,
    labels={
        "Difference_from_Global": "Difference from Global Average",
        "Country": "",
    },
    title="Positive values show countries above the global happiness average",
)

fig_diverging.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(
        family="Arial",
        color="black",
    ),
    title_font=dict(
        color="black",
        size=16,
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor="#EFEFEF",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="black",
        tickfont=dict(color="black"),
        title_font=dict(color="black"),
    ),
    yaxis=dict(
        showgrid=False,
        tickfont=dict(color="black", size=12),
        title_font=dict(color="black"),
    ),
    coloraxis_colorbar=dict(
        title_font=dict(color="black"),
        tickfont=dict(color="black"),
    ),
    margin=dict(l=10, r=10, t=50, b=10),
)

fig_diverging.add_vline(
    x=0,
    line_width=2,
    line_dash="dash",
    annotation_text="Global average midpoint",
    annotation_position="top right",
    annotation_font_color="black",
)

st.plotly_chart(fig_diverging, use_container_width=True)