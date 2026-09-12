import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, dash_table

CSV_PATH = os.environ.get("CSV_PATH", "student_digital_life.csv")

TIME_COLUMNS = [
    "study_hours_per_day",
    "smartphone_usage_hours",
    "social_media_hours",
    "gaming_hours",
    "streaming_hours",
    "sleep_hours",
    "exercise_hours",
]
TIME_LABELS = {
    "study_hours_per_day": "Study",
    "smartphone_usage_hours": "Smartphone",
    "social_media_hours": "Social Media",
    "gaming_hours": "Gaming",
    "streaming_hours": "Streaming",
    "sleep_hours": "Sleep",
    "exercise_hours": "Exercise",
}

DIGITAL_COLUMNS = ["social_media_hours", "gaming_hours", "streaming_hours"]

CORR_COLUMNS = [
    "study_hours_per_day",
    "smartphone_usage_hours",
    "social_media_hours",
    "gaming_hours",
    "streaming_hours",
    "sleep_hours",
    "exercise_hours",
    "class_attendance_percent",
    "assignment_completion_percent",
    "caffeine_intake_cups",
    "motivation_level",
    "final_exam_score",
]


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)


    df["digital_fingerprint"] = (
        df[DIGITAL_COLUMNS]
        .idxmax(axis=1)
        .str.replace("_hours", "", regex=False)
        .str.replace("_", " ")
        .str.title()
    )

    
    df["performance_profile"] = pd.cut(
        df["study_hours_per_day"],
        bins=[-1, 4, float("inf")],
        labels=["Lower Study Time", "Higher Study Time"],
    )
    df["score_profile"] = pd.cut(
        df["final_exam_score"],
        bins=[-1, 60, float("inf")],
        labels=["Lower Score", "Higher Score"],
    )
    df["student_profile"] = (
        df["performance_profile"].astype(str) + " + " + df["score_profile"].astype(str)
    )

    return df


df_raw = load_data(CSV_PATH)

GENDERS = sorted(df_raw["gender"].dropna().unique())
MENTAL_HEALTH = sorted(df_raw["mental_health_status"].dropna().unique())
PARENT_EDU = sorted(df_raw["parent_education_level"].dropna().unique())
INTERNET_QUALITY = sorted(df_raw["internet_quality"].dropna().unique())
AGE_MIN, AGE_MAX = int(df_raw["age"].min()), int(df_raw["age"].max())


app = Dash(__name__, title="Student Digital Life Dashboard")
server = app.server  

CARD_STYLE = {
    "background": "#ffffff",
    "borderRadius": "12px",
    "padding": "18px 20px",
    "boxShadow": "0 1px 3px rgba(0,0,0,0.08)",
    "marginBottom": "20px",
}

COLORS = {
    "bg": "#f4f6f9",
    "accent": "#5b6ee1",
    "text": "#1f2430",
    "muted": "#6b7280",
}


def kpi_card(id_prefix, label):
    return html.Div(
        [
            html.Div(label, style={"fontSize": "13px", "color": COLORS["muted"], "fontWeight": "500"}),
            html.Div(id=f"{id_prefix}-value", style={"fontSize": "28px", "fontWeight": "700", "color": COLORS["text"]}),
        ],
        style={**CARD_STYLE, "textAlign": "center", "flex": "1", "minWidth": "160px"},
    )


def filter_dropdown(id_, options, label):
    return html.Div(
        [
            html.Label(label, style={"fontSize": "13px", "fontWeight": "600", "color": COLORS["muted"]}),
            dcc.Dropdown(
                id=id_,
                options=[{"label": o, "value": o} for o in options],
                value=[],
                multi=True,
                placeholder=f"All {label.lower()}",
                style={"marginTop": "4px"},
            ),
        ],
        style={"flex": "1", "minWidth": "200px"},
    )


app.layout = html.Div(
    style={"backgroundColor": COLORS["bg"], "fontFamily": "Inter, 'Segoe UI', sans-serif", "padding": "24px 32px", "minHeight": "100vh"},
    children=[
        html.Div(
            [
                html.H1("Student Digital Life Dashboard", style={"margin": "0 0 4px 0", "color": COLORS["text"]}),
                html.P(
                    "Study habits, screen time, and academic performance across the student dataset.",
                    style={"margin": 0, "color": COLORS["muted"]},
                ),
            ],
            style={"marginBottom": "24px"},
        ),

     
        html.Div(
            [
                filter_dropdown("filter-gender", GENDERS, "Gender"),
                filter_dropdown("filter-mental-health", MENTAL_HEALTH, "Mental Health"),
                filter_dropdown("filter-parent-edu", PARENT_EDU, "Parent Education"),
                filter_dropdown("filter-internet", INTERNET_QUALITY, "Internet Quality"),
                html.Div(
                    [
                        html.Label("Age Range", style={"fontSize": "13px", "fontWeight": "600", "color": COLORS["muted"]}),
                        dcc.RangeSlider(
                            id="filter-age",
                            min=AGE_MIN,
                            max=AGE_MAX,
                            step=1,
                            value=[AGE_MIN, AGE_MAX],
                            marks={AGE_MIN: str(AGE_MIN), AGE_MAX: str(AGE_MAX)},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                    ],
                    style={"flex": "1.4", "minWidth": "220px", "paddingTop": "2px"},
                ),
            ],
            style={**CARD_STYLE, "display": "flex", "gap": "24px", "flexWrap": "wrap", "alignItems": "flex-start"},
        ),

      
        html.Div(
            [
                kpi_card("kpi-students", "Students"),
                kpi_card("kpi-study", "Avg Study Hrs/Day"),
                kpi_card("kpi-sleep", "Avg Sleep Hrs/Day"),
                kpi_card("kpi-screen", "Avg Screen Hrs/Day"),
                kpi_card("kpi-score", "Avg Exam Score"),
            ],
            style={"display": "flex", "gap": "16px", "flexWrap": "wrap"},
        ),

        
        html.Div(
            [
                html.Div(dcc.Graph(id="chart-activity-bar"), style={**CARD_STYLE, "flex": "1", "minWidth": "420px"}),
                html.Div(dcc.Graph(id="chart-smartphone-study"), style={**CARD_STYLE, "flex": "1", "minWidth": "420px"}),
            ],
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
        ),

        
        html.Div(
            [
                html.Div(dcc.Graph(id="chart-digital-pie"), style={**CARD_STYLE, "flex": "1", "minWidth": "380px"}),
                html.Div(dcc.Graph(id="chart-study-hist"), style={**CARD_STYLE, "flex": "1.4", "minWidth": "420px"}),
            ],
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
        ),

        
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("Digital fingerprint comparison for students studying ", style={"color": COLORS["muted"], "fontSize": "13px"}),
                                dcc.RangeSlider(
                                    id="filter-study-band",
                                    min=0,
                                    max=float(np.ceil(df_raw["study_hours_per_day"].max())),
                                    step=0.5,
                                    value=[4, 5],
                                    marks=None,
                                    tooltip={"placement": "bottom", "always_visible": True},
                                ),
                            ]
                        ),
                        dcc.Graph(id="chart-fingerprint-box"),
                    ],
                    style={**CARD_STYLE, "flex": "1", "minWidth": "420px"},
                ),
                html.Div(dcc.Graph(id="chart-corr-heatmap"), style={**CARD_STYLE, "flex": "1", "minWidth": "420px"}),
            ],
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
        ),

       
        html.Div(
            [
                html.Div(dcc.Graph(id="chart-study-score"), style={**CARD_STYLE, "flex": "1", "minWidth": "420px"}),
                html.Div(dcc.Graph(id="chart-lifestyle-map"), style={**CARD_STYLE, "flex": "1", "minWidth": "420px"}),
            ],
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
        ),

        
        html.Div(
            [
                html.Div(dcc.Graph(id="chart-profiles"), style={**CARD_STYLE, "flex": "1", "minWidth": "420px"}),
                html.Div(dcc.Graph(id="chart-profile-radar"), style={**CARD_STYLE, "flex": "1", "minWidth": "420px"}),
            ],
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
        ),

    
        html.Div(
            [
                html.H3("Filtered Data", style={"marginTop": 0, "color": COLORS["text"]}),
                dash_table.DataTable(
                    id="data-table",
                    page_size=10,
                    style_table={"overflowX": "auto"},
                    style_cell={"fontFamily": "Inter, sans-serif", "fontSize": "13px", "padding": "6px"},
                    style_header={"fontWeight": "600", "backgroundColor": "#eef0f6"},
                ),
            ],
            style=CARD_STYLE,
        ),

        html.Div(
            "Built with Plotly Dash · data: student_digital_life.csv",
            style={"textAlign": "center", "color": COLORS["muted"], "fontSize": "12px", "marginTop": "8px"},
        ),
    ],
)


def apply_filters(gender, mental_health, parent_edu, internet, age_range):
    dff = df_raw.copy()
    if gender:
        dff = dff[dff["gender"].isin(gender)]
    if mental_health:
        dff = dff[dff["mental_health_status"].isin(mental_health)]
    if parent_edu:
        dff = dff[dff["parent_education_level"].isin(parent_edu)]
    if internet:
        dff = dff[dff["internet_quality"].isin(internet)]
    dff = dff[(dff["age"] >= age_range[0]) & (dff["age"] <= age_range[1])]
    return dff


FILTER_INPUTS = [
    Input("filter-gender", "value"),
    Input("filter-mental-health", "value"),
    Input("filter-parent-edu", "value"),
    Input("filter-internet", "value"),
    Input("filter-age", "value"),
]

TEMPLATE = "plotly_white"
ACCENT_SCALE = px.colors.sequential.Blues



@app.callback(
    Output("kpi-students-value", "children"),
    Output("kpi-study-value", "children"),
    Output("kpi-sleep-value", "children"),
    Output("kpi-screen-value", "children"),
    Output("kpi-score-value", "children"),
    FILTER_INPUTS,
)
def update_kpis(gender, mental_health, parent_edu, internet, age_range):
    dff = apply_filters(gender, mental_health, parent_edu, internet, age_range)
    if dff.empty:
        return "0", "-", "-", "-", "-"
    screen_hours = dff[["smartphone_usage_hours", "social_media_hours", "gaming_hours", "streaming_hours"]].sum(axis=1)
    return (
        f"{len(dff):,}",
        f"{dff['study_hours_per_day'].mean():.2f}",
        f"{dff['sleep_hours'].mean():.2f}",
        f"{screen_hours.mean():.2f}",
        f"{dff['final_exam_score'].mean():.1f}",
    )



@app.callback(Output("chart-activity-bar", "figure"), FILTER_INPUTS)
def update_activity_bar(gender, mental_health, parent_edu, internet, age_range):
    dff = apply_filters(gender, mental_health, parent_edu, internet, age_range)
    means = dff[TIME_COLUMNS].mean().reindex(TIME_COLUMNS)
    fig = px.bar(
        x=[TIME_LABELS[c] for c in TIME_COLUMNS],
        y=means.values,
        color=means.values,
        color_continuous_scale=ACCENT_SCALE,
        labels={"x": "Daily Activity", "y": "Average Hours/Day"},
        title="Where Does a Student Spend the Day?",
    )
    fig.update_layout(template=TEMPLATE, coloraxis_showscale=False, margin=dict(t=50, l=10, r=10, b=10))
    return fig



@app.callback(Output("chart-smartphone-study", "figure"), FILTER_INPUTS)
def update_smartphone_scatter(gender, mental_health, parent_edu, internet, age_range):
    dff = apply_filters(gender, mental_health, parent_edu, internet, age_range)
    fig = px.scatter(
        dff,
        x="smartphone_usage_hours",
        y="study_hours_per_day",
        opacity=0.35,
        color_discrete_sequence=[COLORS["accent"]],
        labels={"smartphone_usage_hours": "Smartphone Usage (Hrs/Day)", "study_hours_per_day": "Study Hours/Day"},
        title="Does More Smartphone Time Mean Less Study Time?",
        trendline="ols",
    )
    fig.update_layout(template=TEMPLATE, margin=dict(t=50, l=10, r=10, b=10))
    return fig



@app.callback(Output("chart-digital-pie", "figure"), FILTER_INPUTS)
def update_digital_pie(gender, mental_health, parent_edu, internet, age_range):
    dff = apply_filters(gender, mental_health, parent_edu, internet, age_range)
    means = dff[DIGITAL_COLUMNS].mean()
    fig = px.pie(
        names=[TIME_LABELS[c] for c in DIGITAL_COLUMNS],
        values=means.values,
        hole=0.45,
        title="What Makes Up a Student's Digital Life?",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(template=TEMPLATE, margin=dict(t=50, l=10, r=10, b=10))
    return fig



@app.callback(Output("chart-study-hist", "figure"), FILTER_INPUTS)
def update_study_hist(gender, mental_health, parent_edu, internet, age_range):
    dff = apply_filters(gender, mental_health, parent_edu, internet, age_range)
    fig = px.histogram(
        dff,
        x="study_hours_per_day",
        nbins=30,
        color_discrete_sequence=[COLORS["accent"]],
        labels={"study_hours_per_day": "Study Hours per Day"},
        title="How Are Study Hours Distributed?",
        marginal="box",
    )
    fig.update_layout(template=TEMPLATE, yaxis_title="Number of Students", margin=dict(t=50, l=10, r=10, b=10))
    return fig



@app.callback(
    Output("chart-fingerprint-box", "figure"),
    FILTER_INPUTS + [Input("filter-study-band", "value")],
)
def update_fingerprint_box(gender, mental_health, parent_edu, internet, age_range, study_band):
    dff = apply_filters(gender, mental_health, parent_edu, internet, age_range)
    lo, hi = study_band
    band = dff[(dff["study_hours_per_day"] >= lo) & (dff["study_hours_per_day"] < hi)]
    fig = px.box(
        band,
        x="digital_fingerprint",
        y="final_exam_score",
        color="digital_fingerprint",
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={"digital_fingerprint": "Dominant Digital Activity", "final_exam_score": "Final Exam Score"},
        title=f"Same Study Hours ({lo}-{hi}h), Different Digital Lives · n={len(band)}",
    )
    fig.update_layout(template=TEMPLATE, showlegend=False, margin=dict(t=50, l=10, r=10, b=10))
    return fig


@app.callback(Output("chart-corr-heatmap", "figure"), FILTER_INPUTS)
def update_corr_heatmap(gender, mental_health, parent_edu, internet, age_range):
    dff = apply_filters(gender, mental_health, parent_edu, internet, age_range)
    corr = dff[CORR_COLUMNS].corr()
    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale="RdBu",
            zmid=0,
            text=np.round(corr.values, 2),
            texttemplate="%{text}",
            textfont={"size": 9},
        )
    )
    fig.update_layout(
        title="What Is Associated With Final Exam Score?",
        template=TEMPLATE,
        margin=dict(t=50, l=10, r=10, b=10),
    )
    return fig



@app.callback(Output("chart-study-score", "figure"), FILTER_INPUTS)
def update_study_score(gender, mental_health, parent_edu, internet, age_range):
    dff = apply_filters(gender, mental_health, parent_edu, internet, age_range)
    fig = px.scatter(
        dff,
        x="study_hours_per_day",
        y="final_exam_score",
        opacity=0.3,
        color_discrete_sequence=[COLORS["accent"]],
        trendline="ols",
        labels={"study_hours_per_day": "Study Hours/Day", "final_exam_score": "Final Exam Score"},
        title="The Strongest Relationship: Study Time vs Exam Score",
    )
    fig.update_layout(template=TEMPLATE, margin=dict(t=50, l=10, r=10, b=10))
    return fig



@app.callback(Output("chart-lifestyle-map", "figure"), FILTER_INPUTS)
def update_lifestyle_map(gender, mental_health, parent_edu, internet, age_range):
    dff = apply_filters(gender, mental_health, parent_edu, internet, age_range)
    fig = px.scatter(
        dff,
        x="study_hours_per_day",
        y="sleep_hours",
        color="final_exam_score",
        size="final_exam_score",
        opacity=0.5,
        color_continuous_scale="Viridis",
        labels={
            "study_hours_per_day": "Study Hours",
            "sleep_hours": "Sleep Hours",
            "final_exam_score": "Final Exam Score",
        },
        title="Student Lifestyle Map",
        hover_data=["age", "gender", "mental_health_status"],
    )
    fig.update_layout(template=TEMPLATE, margin=dict(t=50, l=10, r=10, b=10))
    return fig



@app.callback(Output("chart-profiles", "figure"), FILTER_INPUTS)
def update_profiles(gender, mental_health, parent_edu, internet, age_range):
    dff = apply_filters(gender, mental_health, parent_edu, internet, age_range)
    counts = dff["student_profile"].value_counts()
    fig = px.bar(
        x=counts.values,
        y=counts.index,
        orientation="h",
        color=counts.values,
        color_continuous_scale=ACCENT_SCALE,
        labels={"x": "Number of Students", "y": "Student Profile"},
        title="The Four Student Profiles",
    )
    fig.update_layout(template=TEMPLATE, coloraxis_showscale=False, margin=dict(t=50, l=10, r=10, b=10))
    return fig



PROFILE_FEATURES = [
    "study_hours_per_day",
    "smartphone_usage_hours",
    "sleep_hours",
    "exercise_hours",
    "class_attendance_percent",
    "assignment_completion_percent",
    "motivation_level",
]


@app.callback(Output("chart-profile-radar", "figure"), FILTER_INPUTS)
def update_profile_radar(gender, mental_health, parent_edu, internet, age_range):
    dff = apply_filters(gender, mental_health, parent_edu, internet, age_range)
    summary = dff.groupby("student_profile")[PROFILE_FEATURES].mean()


    norm = (summary - summary.min()) / (summary.max() - summary.min() + 1e-9)

    fig = go.Figure()
    for profile in norm.index:
        fig.add_trace(
            go.Scatterpolar(
                r=norm.loc[profile].values,
                theta=PROFILE_FEATURES,
                fill="toself",
                name=profile,
                opacity=0.6,
            )
        )
    fig.update_layout(
        title="Profile Comparison (normalized)",
        template=TEMPLATE,
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        margin=dict(t=50, l=10, r=10, b=10),
    )
    return fig



@app.callback(
    Output("data-table", "data"),
    Output("data-table", "columns"),
    FILTER_INPUTS,
)
def update_table(gender, mental_health, parent_edu, internet, age_range):
    dff = apply_filters(gender, mental_health, parent_edu, internet, age_range)
    display_cols = [c for c in df_raw.columns if c not in ("performance_profile", "score_profile")]
    dff = dff[display_cols].head(200)
    columns = [{"name": c, "id": c} for c in display_cols]
    return dff.to_dict("records"), columns


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)