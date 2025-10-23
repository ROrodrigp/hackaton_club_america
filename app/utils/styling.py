"""
Styling utilities for Club América Streamlit app
"""

# Club América official colors
CLUB_AMERICA_COLORS = {
    'primary': '#041E42',      # Navy blue
    'secondary': '#FFC629',    # Gold/Yellow
    'accent': '#FFFFFF',       # White
    'success': '#28a745',      # Green for positive metrics
    'warning': '#ffc107',      # Yellow for neutral
    'danger': '#dc3545',       # Red for negative metrics
}


def get_custom_css():
    """
    Get custom CSS for Club América branding

    Returns:
        str: CSS styles
    """
    return f"""
    <style>
    /* Main app styling */
    .stApp {{
        background-color: #f8f9fa;
    }}

    /* Keep the navigation - it's not actually duplicate, it's the only working nav */

    /* Headers */
    h1 {{
        color: {CLUB_AMERICA_COLORS['primary']};
        font-weight: 700;
    }}

    h2, h3 {{
        color: {CLUB_AMERICA_COLORS['primary']};
    }}

    /* Metrics */
    [data-testid="stMetricValue"] {{
        font-size: 2rem;
        color: {CLUB_AMERICA_COLORS['primary']};
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {CLUB_AMERICA_COLORS['primary']};
    }}

    [data-testid="stSidebar"] * {{
        color: {CLUB_AMERICA_COLORS['accent']} !important;
    }}

    /* Buttons */
    .stButton>button {{
        background-color: {CLUB_AMERICA_COLORS['secondary']};
        color: {CLUB_AMERICA_COLORS['primary']};
        border: none;
        font-weight: 600;
    }}

    .stButton>button:hover {{
        background-color: #e6b023;
        border: none;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2rem;
    }}

    .stTabs [data-baseweb="tab"] {{
        font-size: 1.1rem;
        font-weight: 600;
    }}

    /* Dataframes */
    .dataframe {{
        font-size: 0.9rem;
    }}
    </style>
    """


def get_score_color(score, thresholds={'high': 90, 'medium': 80}):
    """
    Get color based on score thresholds

    Args:
        score: Numeric score
        thresholds: Dict with 'high' and 'medium' threshold values

    Returns:
        str: Hex color code
    """
    if score >= thresholds['high']:
        return CLUB_AMERICA_COLORS['success']
    elif score >= thresholds['medium']:
        return CLUB_AMERICA_COLORS['warning']
    else:
        return CLUB_AMERICA_COLORS['danger']


def format_metric_delta(value, is_positive_good=True):
    """
    Format metric delta with appropriate color

    Args:
        value: Delta value
        is_positive_good: Whether positive values are good (default True)

    Returns:
        tuple: (formatted_value, color)
    """
    if value > 0:
        color = 'normal' if is_positive_good else 'inverse'
        return f"+{value:.2f}", color
    elif value < 0:
        color = 'inverse' if is_positive_good else 'normal'
        return f"{value:.2f}", color
    else:
        return "0.00", 'off'
