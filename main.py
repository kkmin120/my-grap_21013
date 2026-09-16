import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Movie Data Graphs",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Movie Data Graphs")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    df["일관객"] = pd.to_numeric(
        df["일관객"],
        errors="coerce"
    )

    return df


df = load_data()


# Graph 1
st.divider()
st.header("Graph 1. Daily Audience by Movie")

movie_list = sorted(df["영화명"].dropna().unique())

selected_movie = st.selectbox(
    "Select a movie",
    movie_list
)

movie_df = df[df["영화명"] == selected_movie].copy()
movie_df = movie_df.sort_values("날짜")

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"{selected_movie} - Daily Audience",
    labels={
        "날짜": "Date",
        "일관객": "Daily Audience"
    }
)

fig1.update_traces(
    hovertemplate=
    "Date: %{x|%Y-%m-%d}<br>"
    "Audience: %{y:,}"
)

fig1.update_layout(
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y-%m-%d"
    ),
    yaxis=dict(
        tickformat=","
    ),
    height=500
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# Graph 2
st.divider()
st.header("Graph 2. Top 5 Movies by Total Audience")

top5_movies = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
    .head(5)
)

top5_movie_names = top5_movies["영화명"].tolist()

top5_df = df[
    df["영화명"].isin(top5_movie_names)
].copy()

top5_df = top5_df.sort_values(
    ["날짜", "영화명"]
)

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="Top 5 Movies by Total Audience",
    labels={
        "날짜": "Date",
        "일관객": "Daily Audience",
        "영화명": "Movie"
    }
)

fig2.update_traces(
    hovertemplate=
    "Movie: %{fullData.name}<br>"
    "Date: %{x|%Y-%m-%d}<br>"
    "Audience: %{y:,}"
)

fig2.update_layout(
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y-%m-%d"
    ),
    yaxis=dict(
        tickformat=","
    ),
    legend=dict(
        title="Movie",
        itemclick="toggle",
        itemdoubleclick="toggleothers"
    ),
    height=600
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# Graph 3
st.divider()
st.header("Graph 3. Daily Total Audience of Top 10")

daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

top3_days = (
    daily_total
    .sort_values("일관객", ascending=False)
    .head(3)
)

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="Daily Total Audience of Top 10",
    labels={
        "날짜": "Date",
        "일관객": "Total Audience"
    }
)

fig3.update_traces(
    hovertemplate=
    "Date: %{x|%Y-%m-%d}<br>"
    "Total Audience: %{y:,}"
)

for _, row in top3_days.iterrows():
    fig3.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=(
            f"{row['날짜'].strftime('%Y-%m-%d')}<br>"
            f"{row['일관객']:,}"
        ),
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-50
    )

fig3.update_layout(
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y-%m-%d"
    ),
    yaxis=dict(
        tickformat=","
    ),
    height=600
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# Graph 4
st.divider()
st.header("Graph 4. Top 10 Movies by Total Audience")

movie_summary = (
    df.groupby("영화명")
    .agg(
        total_audience=("일관객", "sum"),
        days_in_top10=("날짜", "nunique")
    )
    .reset_index()
)

top10_movies = (
    movie_summary
    .sort_values("total_audience", ascending=False)
    .head(10)
    .copy()
)

top10_movies = top10_movies.sort_values(
    "total_audience",
    ascending=True
)

fig4 = px.bar(
    top10_movies,
    x="total_audience",
    y="영화명",
    orientation="h",
    title="Top 10 Movies by Total Audience",
    labels={
        "영화명": "Movie",
        "total_audience": "Total Audience"
    },
    custom_data=["days_in_top10"]
)

fig4.update_traces(
    hovertemplate=
    "Movie: %{y}<br>"
    "Total Audience: %{x:,}<br>"
    "Days in Top 10: %{customdata[0]}"
)

fig4.update_layout(
    xaxis=dict(
        tickformat=","
    ),
    yaxis=dict(
        categoryorder="array",
        categoryarray=top10_movies["영화명"].tolist()
    ),
    height=600
)

st.plotly_chart(
    fig4,
    use_container_width=True
)


# Graph 5
st.divider()
st.header("Graph 5. Monthly × Weekly Audience Heatmap")

df["month"] = df["날짜"].dt.month

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

weekday_map = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}

df["weekday"] = df["날짜"].dt.weekday.map(weekday_map)

monthly_weekday = (
    df.groupby(["month", "weekday"], as_index=False)["일관객"]
    .sum()
)

monthly_weekday["weekday"] = pd.Categorical(
    monthly_weekday["weekday"],
    categories=weekday_order,
    ordered=True
)

monthly_weekday = monthly_weekday.sort_values(
    ["month", "weekday"]
)

fig5 = px.density_heatmap(
    monthly_weekday,
    x="weekday",
    y="month",
    z="일관객",
    title="Monthly × Weekly Audience Heatmap",
    labels={
        "month": "Month",
        "weekday": "Day of Week",
        "일관객": "Total Audience"
    },
    category_orders={
        "weekday": weekday_order,
        "month": list(range(1, 13))
    },
    color_continuous_scale="Blues"
)

fig5.update_traces(
    hovertemplate=
    "%{y} / %{x}<br>"
    "Total Audience: %{z:,}"
)

fig5.update_layout(
    height=600
)

st.plotly_chart(
    fig5,
    use_container_width=True
)


# Graph 6
st.divider()
st.header("Graph 6")

st.info("Coming soon.")
