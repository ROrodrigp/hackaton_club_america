"""
Styling utilities for Club América Streamlit app
"""

# Club América official colors - Extended palette
CLUB_AMERICA_COLORS = {
    # Primary colors
    'primary': '#041E42',           # Navy blue (Official)
    'primary_light': '#0A2F5F',     # Lighter navy
    'primary_dark': '#021528',      # Darker navy

    # Secondary colors
    'secondary': '#FFC629',         # Gold/Yellow (Official)
    'secondary_light': '#FFD966',   # Lighter gold
    'secondary_dark': '#E6B023',    # Darker gold

    # Accent colors
    'accent': '#FFFFFF',            # White
    'accent_gray': '#F8F9FA',       # Light gray background
    'text_gray': '#6C757D',         # Gray for secondary text

    # Semantic colors
    'success': '#28A745',           # Green for positive metrics
    'success_light': '#D4EDDA',     # Light green background
    'warning': '#FFC107',           # Yellow for neutral
    'warning_light': '#FFF3CD',     # Light yellow background
    'danger': '#DC3545',            # Red for negative metrics
    'danger_light': '#F8D7DA',      # Light red background
    'info': '#17A2B8',              # Blue for info
    'info_light': '#D1ECF1',        # Light blue background
}


def get_custom_css():
    """
    Get custom CSS for Club América branding

    Returns:
        str: CSS styles
    """
    return f"""
    <style>
    /* ========================================
       GENERAL APP STYLING
       ======================================== */

    /* Main app background - solid light gray for better readability */
    .stApp {{
        background-color: {CLUB_AMERICA_COLORS['accent_gray']};
    }}

    /* Main content has white background */
    .main {{
        background-color: white;
        border-radius: 10px;
        margin: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }}

    /* Remove empty elements */
    [data-testid="stSidebar"] p:empty,
    [data-testid="stSidebar"] > div > div:empty {{
        display: none;
    }}

    /* ========================================
       TYPOGRAPHY
       ======================================== */

    /* Main headers - Navy with golden underline effect */
    h1 {{
        color: {CLUB_AMERICA_COLORS['primary']} !important;
        font-weight: 800 !important;
        font-size: 2.5rem !important;
        letter-spacing: -0.5px;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid {CLUB_AMERICA_COLORS['secondary']};
    }}

    h2 {{
        color: {CLUB_AMERICA_COLORS['primary']} !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }}

    h3 {{
        color: {CLUB_AMERICA_COLORS['primary_light']} !important;
        font-weight: 600 !important;
        font-size: 1.3rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.8rem !important;
    }}

    h4 {{
        color: {CLUB_AMERICA_COLORS['primary_light']} !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }}

    /* Paragraph spacing and color */
    p {{
        line-height: 1.6;
        margin-bottom: 1rem;
        color: #212529 !important;
    }}

    /* General text color for better readability */
    body, .stMarkdown {{
        color: #212529;
    }}

    /* Strong text */
    strong {{
        color: {CLUB_AMERICA_COLORS['primary']} !important;
        font-weight: 700;
    }}

    /* ========================================
       SIDEBAR
       ======================================== */

    /* Sidebar with gradient background */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {CLUB_AMERICA_COLORS['primary']} 0%, {CLUB_AMERICA_COLORS['primary_light']} 100%);
        padding-top: 2rem !important;
    }}

    /* Sidebar text - better contrast */
    [data-testid="stSidebar"] * {{
        color: {CLUB_AMERICA_COLORS['accent']} !important;
    }}

    /* Sidebar links hover effect */
    [data-testid="stSidebar"] a:hover {{
        background-color: {CLUB_AMERICA_COLORS['secondary']} !important;
        color: {CLUB_AMERICA_COLORS['primary']} !important;
        border-radius: 5px;
        transition: all 0.3s ease;
    }}

    /* ========================================
       METRICS & CARDS
       ======================================== */

    /* Metric values - larger and golden */
    [data-testid="stMetricValue"] {{
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: {CLUB_AMERICA_COLORS['primary']} !important;
    }}

    /* Metric labels */
    [data-testid="stMetricLabel"] {{
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: {CLUB_AMERICA_COLORS['text_gray']} !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* Metric delta */
    [data-testid="stMetricDelta"] {{
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }}

    /* ========================================
       BUTTONS & INTERACTIVE ELEMENTS
       ======================================== */

    /* Primary buttons */
    .stButton>button {{
        background: linear-gradient(135deg, {CLUB_AMERICA_COLORS['secondary']} 0%, {CLUB_AMERICA_COLORS['secondary_dark']} 100%);
        color: {CLUB_AMERICA_COLORS['primary']} !important;
        border: none;
        font-weight: 700;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .stButton>button:hover {{
        background: linear-gradient(135deg, {CLUB_AMERICA_COLORS['secondary_dark']} 0%, {CLUB_AMERICA_COLORS['secondary']} 100%);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }}

    /* ========================================
       TABS
       ======================================== */

    /* Tab list spacing */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2rem;
        border-bottom: 2px solid {CLUB_AMERICA_COLORS['secondary']};
        padding-bottom: 0;
    }}

    /* Individual tabs */
    .stTabs [data-baseweb="tab"] {{
        font-size: 1.1rem;
        font-weight: 700;
        color: {CLUB_AMERICA_COLORS['text_gray']};
        padding: 0.75rem 1.5rem;
        border-radius: 8px 8px 0 0;
        transition: all 0.3s ease;
    }}

    /* Active tab */
    .stTabs [aria-selected="true"] {{
        background-color: {CLUB_AMERICA_COLORS['secondary']} !important;
        color: {CLUB_AMERICA_COLORS['primary']} !important;
    }}

    /* Tab hover effect */
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: {CLUB_AMERICA_COLORS['secondary_light']};
        color: {CLUB_AMERICA_COLORS['primary']};
    }}

    /* ========================================
       TABLES & DATAFRAMES
       ======================================== */

    /* Dataframe styling */
    .dataframe {{
        font-size: 0.95rem;
        border-radius: 8px;
        overflow: hidden;
    }}

    /* Dataframe headers */
    .dataframe thead tr th {{
        background-color: {CLUB_AMERICA_COLORS['primary']} !important;
        color: {CLUB_AMERICA_COLORS['accent']} !important;
        font-weight: 700;
        padding: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.85rem;
    }}

    /* Dataframe rows hover effect */
    .dataframe tbody tr:hover {{
        background-color: {CLUB_AMERICA_COLORS['secondary_light']} !important;
        transition: background-color 0.2s ease;
    }}

    /* Dataframe cell text - ensure it's visible */
    .dataframe tbody td {{
        color: {CLUB_AMERICA_COLORS['primary']} !important;
        font-weight: 500;
    }}

    /* ========================================
       EXPANDERS
       ======================================== */

    /* Expander headers */
    .streamlit-expanderHeader {{
        background-color: {CLUB_AMERICA_COLORS['accent_gray']};
        border-left: 4px solid {CLUB_AMERICA_COLORS['secondary']};
        font-weight: 600;
        border-radius: 4px;
        padding: 0.75rem !important;
    }}

    .streamlit-expanderHeader:hover {{
        background-color: {CLUB_AMERICA_COLORS['secondary_light']};
    }}

    /* ========================================
       ALERTS & MESSAGES
       ======================================== */

    /* Success messages */
    .stSuccess {{
        background-color: {CLUB_AMERICA_COLORS['success_light']} !important;
        border-left: 4px solid {CLUB_AMERICA_COLORS['success']} !important;
        border-radius: 4px;
        padding: 1rem !important;
    }}

    /* Info messages */
    .stInfo {{
        background-color: {CLUB_AMERICA_COLORS['info_light']} !important;
        border-left: 4px solid {CLUB_AMERICA_COLORS['info']} !important;
        border-radius: 4px;
        padding: 1rem !important;
    }}

    /* Warning messages */
    .stWarning {{
        background-color: {CLUB_AMERICA_COLORS['warning_light']} !important;
        border-left: 4px solid {CLUB_AMERICA_COLORS['warning']} !important;
        border-radius: 4px;
        padding: 1rem !important;
    }}

    /* Error messages */
    .stError {{
        background-color: {CLUB_AMERICA_COLORS['danger_light']} !important;
        border-left: 4px solid {CLUB_AMERICA_COLORS['danger']} !important;
        border-radius: 4px;
        padding: 1rem !important;
    }}

    /* ========================================
       PROGRESS BARS
       ======================================== */

    /* Progress bar container */
    .stProgress > div > div > div > div {{
        background-color: {CLUB_AMERICA_COLORS['secondary']} !important;
    }}

    /* ========================================
       SELECTBOX & INPUTS
       ======================================== */

    /* Selectbox styling */
    .stSelectbox label {{
        font-weight: 600;
        color: {CLUB_AMERICA_COLORS['primary']};
    }}

    /* Multiselect */
    .stMultiSelect label {{
        font-weight: 600;
        color: {CLUB_AMERICA_COLORS['primary']};
    }}

    /* Slider */
    .stSlider label {{
        font-weight: 600;
        color: {CLUB_AMERICA_COLORS['primary']};
    }}

    /* ========================================
       SPACING & LAYOUT
       ======================================== */

    /* Main content container */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }}

    /* Section dividers */
    hr {{
        margin-top: 2rem !important;
        margin-bottom: 2rem !important;
        border: none;
        border-top: 2px solid {CLUB_AMERICA_COLORS['secondary']};
        opacity: 0.3;
    }}

    /* Column spacing */
    [data-testid="column"] {{
        padding: 0.5rem;
    }}

    /* ========================================
       CUSTOM CLASSES
       ======================================== */

    /* Card-like containers */
    .metric-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border-left: 4px solid {CLUB_AMERICA_COLORS['secondary']};
        margin-bottom: 1rem;
    }}

    /* Highlight boxes */
    .highlight-box {{
        background: linear-gradient(135deg, {CLUB_AMERICA_COLORS['secondary_light']} 0%, {CLUB_AMERICA_COLORS['accent']} 100%);
        padding: 1.5rem;
        border-radius: 8px;
        border: 2px solid {CLUB_AMERICA_COLORS['secondary']};
        margin: 1rem 0;
    }}

    /* Dark background cards - FORCE white/gold text */
    .dark-card {{
        background-color: {CLUB_AMERICA_COLORS['primary']};
    }}

    .dark-card h1,
    .dark-card h2,
    .dark-card h3,
    .dark-card h4,
    .dark-card p,
    .dark-card span,
    .dark-card div {{
        color: white !important;
    }}

    .dark-card .gold-text {{
        color: {CLUB_AMERICA_COLORS['secondary']} !important;
    }}

    /* Red background cards - FORCE white text */
    .danger-card {{
        background-color: {CLUB_AMERICA_COLORS['danger']};
    }}

    .danger-card h1,
    .danger-card h2,
    .danger-card h3,
    .danger-card h4,
    .danger-card p,
    .danger-card span,
    .danger-card div {{
        color: white !important;
    }}

    /* ========================================
       TEXT & LIST IMPROVEMENTS
       ======================================== */

    /* List items */
    li {{
        color: #212529;
        margin-bottom: 0.5rem;
    }}

    /* Code and inline code */
    code {{
        background-color: {CLUB_AMERICA_COLORS['accent_gray']};
        color: {CLUB_AMERICA_COLORS['primary']};
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
        font-weight: 600;
    }}

    /* Blockquotes */
    blockquote {{
        border-left: 4px solid {CLUB_AMERICA_COLORS['secondary']};
        padding-left: 1rem;
        color: {CLUB_AMERICA_COLORS['text_gray']};
        font-style: italic;
    }}
    </style>
    """


# Consistent emoji/icon system for the app
ICONS = {
    # DNA Dimensions
    'progression': '📈',
    'creation': '🎨',
    'finishing': '⚽',
    'pressing': '💪',
    'possession': '🎯',
    'dribbling': '⚡',

    # General
    'dna': '🧬',
    'player': '👤',
    'team': '🏟️',
    'position': '📍',
    'time': '⏱️',
    'matches': '🎮',
    'ranking': '🏆',
    'trophy': '🏆',
    'medal': '🥇',
    'star': '⭐',
    'eagle': '🦅',

    # Actions
    'recommend': '✅',
    'avoid': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'success': '✔️',
    'error': '🚫',

    # Analysis
    'radar': '📊',
    'chart': '📈',
    'comparison': '⚖️',
    'metrics': '📏',
    'target': '🎯',
    'insight': '💡',

    # Navigation
    'home': '🏠',
    'search': '🔍',
    'filter': '🔧',
    'download': '📥',
    'upload': '📤',

    # Status
    'elite': '⭐',
    'strong': '✅',
    'good': '📈',
    'weak': '📉',
    'priority': '🔴',
}


def get_dimension_icon(dimension_name):
    """
    Get consistent icon for DNA dimension

    Args:
        dimension_name: Name of the dimension

    Returns:
        str: Emoji icon
    """
    return ICONS.get(dimension_name.lower(), '📊')


def get_status_icon(status_text):
    """
    Get icon based on status text

    Args:
        status_text: Status string (e.g., 'Elite', 'Strong', 'Weak')

    Returns:
        str: Emoji icon
    """
    status_map = {
        'elite': ICONS['elite'],
        'strong': ICONS['strong'],
        'high': ICONS['strong'],
        'good': ICONS['good'],
        'medium': ICONS['info'],
        'weak': ICONS['weak'],
        'low': ICONS['weak'],
        'priority': ICONS['priority'],
    }
    return status_map.get(status_text.lower(), ICONS['info'])


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
