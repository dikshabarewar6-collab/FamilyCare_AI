"""
Plotly Interactive Data Visualizations and 3D Visual Experience.
Crafted with soft lavender, teal, sky blue, and healthcare glassmorphic aesthetics.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import config

PLOT_TEMPLATE = "plotly_white"
FONT_FAMILY = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

def create_checkin_trend_chart(daily_df: pd.DataFrame) -> go.Figure:
    """Create interactive line/area chart showing daily check-in completion vs missed."""
    if daily_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No check-in data available yet", showarrow=False, font=dict(size=14, color="#64748B"))
        fig.update_layout(template=PLOT_TEMPLATE, height=320)
        return fig

    fig = go.Figure()

    # Completed Check-ins Area
    fig.add_trace(go.Scatter(
        x=daily_df["date"],
        y=daily_df["completed"],
        mode="lines+markers",
        name="Completed ('I'm Okay')",
        line=dict(color="#0D9488", width=3, shape="spline"),
        marker=dict(size=7, color="#0D9488"),
        fill="tozeroy",
        fillcolor="rgba(45, 212, 191, 0.15)"
    ))

    # Missed Check-ins Bar
    if "missed" in daily_df.columns and daily_df["missed"].sum() > 0:
        fig.add_trace(go.Bar(
            x=daily_df["date"],
            y=daily_df["missed"],
            name="Missed Check-In",
            marker=dict(color="#EF4444", opacity=0.8)
        ))

    fig.update_layout(
        template=PLOT_TEMPLATE,
        height=340,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title=None, showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(title="Check-Ins", showgrid=True, gridcolor="#F1F5F9", dtick=1),
        font=dict(family=FONT_FAMILY)
    )
    return fig

def create_medication_adherence_chart(med_df: pd.DataFrame) -> go.Figure:
    """Create horizontal bar chart of adherence percentages per medication."""
    if med_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No medication logs available yet", showarrow=False, font=dict(size=14, color="#64748B"))
        fig.update_layout(template=PLOT_TEMPLATE, height=280)
        return fig

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=med_df["medication"],
        x=med_df["adherence_pct"],
        orientation="h",
        name="Adherence %",
        marker=dict(
            color=med_df["adherence_pct"],
            colorscale=[[0, "#EF4444"], [0.7, "#F59E0B"], [1.0, "#10B981"]],
            line=dict(color="white", width=1.5)
        ),
        text=[f"{pct}%" for pct in med_df["adherence_pct"]],
        textposition="auto"
    ))

    fig.update_layout(
        template=PLOT_TEMPLATE,
        height=280,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(title="Adherence Rate (%)", range=[0, 105], showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(title=None),
        font=dict(family=FONT_FAMILY)
    )
    return fig

def create_task_donut_chart(cat_df: pd.DataFrame) -> go.Figure:
    """Create modern donut chart showing category distribution of care tasks."""
    if cat_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No care tasks recorded", showarrow=False, font=dict(size=14, color="#64748B"))
        fig.update_layout(template=PLOT_TEMPLATE, height=260)
        return fig

    colors = ["#7052E6", "#0D9488", "#0284C7", "#F59E0B", "#10B981"]

    fig = go.Figure(data=[go.Pie(
        labels=cat_df["category"],
        values=cat_df["count"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="white", width=2)),
        textinfo="label+percent"
    )])

    fig.update_layout(
        template=PLOT_TEMPLATE,
        height=260,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        font=dict(family=FONT_FAMILY)
    )
    return fig

def create_3d_activity_scatter(df_3d: pd.DataFrame) -> go.Figure:
    """
    Create an interactive 3D Scatter Visual Landscape:
    X: Day of the Week (Mon=0 to Sun=6)
    Y: Check-In Hour of Day (e.g. 8.5 = 8:30 AM)
    Z: Delay from 9:00 AM target window (in minutes)
    Enables families to visually inspect elderly morning rhythm stability in 3D!
    """
    if df_3d.empty or "actual_hour" not in df_3d.columns:
        fig = go.Figure()
        fig.add_annotation(text="No 3D activity data available", showarrow=False, font=dict(size=14, color="#64748B"))
        fig.update_layout(template=PLOT_TEMPLATE, height=450)
        return fig

    weekday_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    hover_texts = []
    for _, row in df_3d.iterrows():
        delay_val = round(row.get("delay_mins", 0), 1)
        delay_str = f"+{delay_val}m late" if delay_val > 0 else f"{abs(delay_val)}m early"
        h_str = f"{int(row['actual_hour'])}:{int((row['actual_hour'] % 1)*60):02d}"
        hover_texts.append(
            f"<b>{row.get('weekday', 'Day')}</b><br>"
            f"Time: {h_str}<br>"
            f"Variance: {delay_str}<br>"
            f"Status: {row.get('status', 'Checked In')}"
        )

    fig = go.Figure(data=[go.Scatter3d(
        x=df_3d["weekday_num"],
        y=df_3d["actual_hour"],
        z=df_3d["delay_mins"],
        mode="markers",
        marker=dict(
            size=8,
            color=df_3d["delay_mins"],
            colorscale="Viridis",
            colorbar=dict(title=dict(text="Variance (mins)", font=dict(size=11)), thickness=14, len=0.7),
            opacity=0.88,
            line=dict(color="white", width=1)
        ),
        text=hover_texts,
        hoverinfo="text"
    )])

    # Reference plane at Scheduled 9:00 AM (Y = 9.0)
    x_grid, z_grid = np.meshgrid([0, 6], [-30, 60])
    y_target = np.full_like(x_grid, 9.0)
    fig.add_trace(go.Surface(
        x=x_grid,
        y=y_target,
        z=z_grid,
        showscale=False,
        opacity=0.2,
        colorscale=[[0, "#9B86EE"], [1, "#9B86EE"]],
        name="Scheduled Target (9:00 AM)"
    ))

    fig.update_layout(
        template=PLOT_TEMPLATE,
        height=480,
        margin=dict(l=10, r=10, t=10, b=10),
        scene=dict(
            xaxis=dict(
                title="Day of Week",
                tickvals=list(range(7)),
                ticktext=weekday_labels,
                backgroundcolor="rgba(248, 250, 252, 0.5)",
                gridcolor="#E2E8F0"
            ),
            yaxis=dict(
                title="Check-In Hour (24h)",
                backgroundcolor="rgba(248, 250, 252, 0.5)",
                gridcolor="#E2E8F0"
            ),
            zaxis=dict(
                title="Variance (Minutes)",
                backgroundcolor="rgba(248, 250, 252, 0.5)",
                gridcolor="#E2E8F0"
            ),
            camera=dict(
                eye=dict(x=1.6, y=-1.6, z=1.3)
            )
        ),
        font=dict(family=FONT_FAMILY)
    )
    return fig
