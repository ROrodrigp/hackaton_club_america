"""
Visualization utilities for Club América Streamlit app
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from .styling import CLUB_AMERICA_COLORS, get_score_color


def create_radar_chart(dimensions_data, title="Club América DNA Profile"):
    """
    Create a radar chart for DNA dimensions

    Args:
        dimensions_data: Dict with dimension names as keys and score values
        title: Chart title

    Returns:
        plotly.graph_objects.Figure
    """
    # Extract dimension names and scores
    categories = []
    scores = []

    for dim_name, dim_data in dimensions_data.items():
        # Capitalize first letter
        display_name = dim_name.capitalize()
        categories.append(display_name)
        scores.append(dim_data['score'])

    # Add first point again to close the radar
    categories_closed = categories + [categories[0]]
    scores_closed = scores + [scores[0]]

    # Create figure
    fig = go.Figure()

    # Add América's DNA trace
    fig.add_trace(go.Scatterpolar(
        r=scores_closed,
        theta=categories_closed,
        fill='toself',
        name='Club América',
        line=dict(color=CLUB_AMERICA_COLORS['secondary'], width=3),
        fillcolor=f"rgba(255, 198, 41, 0.3)",  # Yellow with transparency
    ))

    # Add benchmark line at 100 (P90)
    fig.add_trace(go.Scatterpolar(
        r=[100] * len(categories_closed),
        theta=categories_closed,
        fill='toself',
        name='Benchmark P90',
        line=dict(color='gray', width=1, dash='dash'),
        fillcolor='rgba(128, 128, 128, 0.1)',
    ))

    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 110],
                showticklabels=True,
                ticks='outside',
                tickfont=dict(size=11),
                gridcolor='lightgray',
            ),
            angularaxis=dict(
                showticklabels=True,
                tickfont=dict(size=13, color=CLUB_AMERICA_COLORS['primary']),
            ),
            bgcolor='white',
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        title=dict(
            text=title,
            font=dict(size=18, color=CLUB_AMERICA_COLORS['primary']),
            x=0.5,
            xanchor='center'
        ),
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white',
    )

    return fig


def create_horizontal_bar_chart(dimensions_data, title="DNA Scores by Dimension"):
    """
    Create horizontal bar chart for dimension scores

    Args:
        dimensions_data: Dict with dimension names as keys and score values
        title: Chart title

    Returns:
        plotly.graph_objects.Figure
    """
    # Extract and sort data
    dim_names = []
    scores = []
    colors = []

    for dim_name, dim_data in dimensions_data.items():
        dim_names.append(dim_name.capitalize())
        score = dim_data['score']
        scores.append(score)
        colors.append(get_score_color(score, thresholds={'high': 95, 'medium': 85}))

    # Sort by score descending
    sorted_data = sorted(zip(dim_names, scores, colors), key=lambda x: x[1], reverse=True)
    dim_names_sorted = [x[0] for x in sorted_data]
    scores_sorted = [x[1] for x in sorted_data]
    colors_sorted = [x[2] for x in sorted_data]

    # Create figure
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=dim_names_sorted,
        x=scores_sorted,
        orientation='h',
        marker=dict(
            color=colors_sorted,
            line=dict(color=CLUB_AMERICA_COLORS['primary'], width=1)
        ),
        text=[f"{score:.1f}" for score in scores_sorted],
        textposition='outside',
        textfont=dict(size=13, color=CLUB_AMERICA_COLORS['primary']),
        hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}/100<extra></extra>',
    ))

    # Add threshold lines
    fig.add_vline(x=95, line_dash="dash", line_color=CLUB_AMERICA_COLORS['primary'],
                  line_width=2,
                  annotation_text="Elite (95)", annotation_position="top",
                  annotation=dict(font_size=12, font_color=CLUB_AMERICA_COLORS['primary']))
    fig.add_vline(x=90, line_dash="dot", line_color=CLUB_AMERICA_COLORS['primary'],
                  line_width=2,
                  annotation_text="Strong (90)", annotation_position="top",
                  annotation=dict(font_size=12, font_color=CLUB_AMERICA_COLORS['primary']))

    # Update layout
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color=CLUB_AMERICA_COLORS['primary']),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(
                text="Score",
                font=dict(size=14, color=CLUB_AMERICA_COLORS['primary'])
            ),
            range=[0, 105],
            showgrid=True,
            gridcolor='lightgray',
            tickfont=dict(size=12, color=CLUB_AMERICA_COLORS['primary']),
        ),
        yaxis=dict(
            title="",
            categoryorder='total ascending',
            tickfont=dict(size=14, color=CLUB_AMERICA_COLORS['primary'], family='Arial Black'),
        ),
        height=400,
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=False,
        margin=dict(l=120, r=40, t=80, b=40),  # Increase left margin for labels
    )

    return fig


def create_comparison_radar(player_dna, team_dna, player_name):
    """
    Create radar chart comparing player DNA vs team DNA

    Args:
        player_dna: Dict with player's dimension scores
        team_dna: Dict with team's dimension scores
        player_name: Name of the player

    Returns:
        plotly.graph_objects.Figure
    """
    categories = []
    player_scores = []
    team_scores = []

    dimension_names = ['progression', 'creation', 'finishing', 'pressing', 'possession', 'dribbling']

    for dim in dimension_names:
        categories.append(dim.capitalize())
        player_scores.append(player_dna.get(dim, 0))
        team_scores.append(team_dna[dim]['score'])

    # Close the radar
    categories_closed = categories + [categories[0]]
    player_scores_closed = player_scores + [player_scores[0]]
    team_scores_closed = team_scores + [team_scores[0]]

    # Create figure
    fig = go.Figure()

    # Add player trace
    fig.add_trace(go.Scatterpolar(
        r=player_scores_closed,
        theta=categories_closed,
        fill='toself',
        name=player_name,
        line=dict(color='#2ecc71', width=2),
        fillcolor='rgba(46, 204, 113, 0.2)',
    ))

    # Add team trace
    fig.add_trace(go.Scatterpolar(
        r=team_scores_closed,
        theta=categories_closed,
        fill='toself',
        name='Club América',
        line=dict(color=CLUB_AMERICA_COLORS['secondary'], width=2),
        fillcolor='rgba(255, 198, 41, 0.2)',
    ))

    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 110],
                showticklabels=True,
                ticks='outside',
                tickfont=dict(size=11),
                gridcolor='lightgray',
            ),
            angularaxis=dict(
                showticklabels=True,
                tickfont=dict(size=13, color=CLUB_AMERICA_COLORS['primary']),
            ),
            bgcolor='white',
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        height=400,
        title=dict(
            text=f"DNA Match: {player_name} vs Club América",
            font=dict(size=18, color=CLUB_AMERICA_COLORS['primary']),
            x=0.5,
            xanchor='center'
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )

    return fig


def create_scatter_plot(df, x_col, y_col, size_col=None, color_col=None,
                       hover_name=None, title=""):
    """
    Create scatter plot for exploring player pool

    Args:
        df: DataFrame with player data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        size_col: Optional column for bubble size
        color_col: Optional column for color coding
        hover_name: Column name to show on hover
        title: Chart title

    Returns:
        plotly.express Figure
    """
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size=size_col,
        color=color_col,
        hover_name=hover_name,
        title=title,
        labels={
            x_col: x_col.replace('_', ' ').title(),
            y_col: y_col.replace('_', ' ').title(),
        },
        color_discrete_sequence=px.colors.qualitative.Set2,
    )

    fig.update_layout(
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white',
    )

    return fig
