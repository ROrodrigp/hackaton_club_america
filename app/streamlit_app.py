"""
Club América - DNA Analysis & Player Scouting System
Streamlit App - Home Page
"""
import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.data_loader import (
    load_america_dna,
    load_benchmarks,
    load_scouting_pool,
    load_top_recommendations,
    load_worst_recommendations
)
from utils.styling import get_custom_css, CLUB_AMERICA_COLORS

# Page config
st.set_page_config(
    page_title="Club América - DNA Analysis & Scouting",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    # Logo - try local image first, fallback to emoji
    logo_path = Path(__file__).parent / "assets" / "club_america_logo.png"
    if logo_path.exists():
        st.image(str(logo_path), width=150)
    else:
        st.markdown("# 🦅")

    st.title("Club América")
    st.markdown("### Scouting System")
    st.markdown("---")
    st.markdown("**Temporada:** 2024/2025")
    st.markdown("**Liga:** Liga MX")

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.title("🦅 Club América - Player Scouting System")
st.markdown("### Análisis de DNA Táctico y Recomendaciones de Fichajes")
st.markdown("---")

# Load data
try:
    dna_data = load_america_dna()
    benchmarks = load_benchmarks()
    scouting_pool = load_scouting_pool()

    # Try to load recommendations (might not exist yet)
    try:
        top_20 = load_top_recommendations()
        worst_20 = load_worst_recommendations()
        recommendations_available = True
    except FileNotFoundError:
        recommendations_available = False
        st.warning("⚠️ Recomendaciones no disponibles. Ejecuta el script 04_calculate_fit_score.py primero.")

except Exception as e:
    st.error(f"❌ Error cargando datos: {e}")
    st.stop()

# ============================================================================
# OVERVIEW METRICS
# ============================================================================

st.markdown("## 📈 Overview del Análisis")
st.markdown("")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Use overall_score from DNA data or calculate from dimensions
    if 'overall_score' in dna_data:
        avg_dna = dna_data['overall_score']
    else:
        # Calculate average DNA score
        dna_scores = dna_data['dimensions']
        avg_dna = sum([
            dna_scores['progression']['score'],
            dna_scores['creation']['score'],
            dna_scores['finishing']['score'],
            dna_scores['pressing']['score'],
            dna_scores['possession']['score'],
            dna_scores['dribbling']['score']
        ]) / 6

    st.metric(
        label="🧬 DNA Score Promedio",
        value=f"{avg_dna:.1f}/100",
        delta="Elite" if avg_dna >= 90 else "Bueno"
    )

with col2:
    num_players = len(scouting_pool)
    st.metric(
        label="👥 Jugadores Analizados",
        value=f"{num_players}",
        delta="18 equipos"
    )

with col3:
    num_teams = scouting_pool['team.name'].nunique()
    st.metric(
        label="🏟️ Equipos Scouting",
        value=f"{num_teams}",
        delta="Liga MX completa"
    )

with col4:
    if recommendations_available:
        st.metric(
            label="⭐ Recomendaciones",
            value="Disponibles",
            delta="Top 20 + Worst 20"
        )
    else:
        st.metric(
            label="⭐ Recomendaciones",
            value="Pendientes",
            delta="Ejecuta script 04"
        )

st.markdown("---")

# ============================================================================
# QUICK INSIGHTS
# ============================================================================

st.markdown("## 🎯 Insights Clave")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💪 Fortalezas del Club América")

    # Get dimensions
    dimensions = dna_data['dimensions']

    # Get top 3 dimensions
    dimension_scores = [
        ('Finishing', dimensions['finishing']['score']),
        ('Creation', dimensions['creation']['score']),
        ('Progression', dimensions['progression']['score']),
        ('Possession', dimensions['possession']['score']),
        ('Dribbling', dimensions['dribbling']['score']),
        ('Pressing', dimensions['pressing']['score'])
    ]
    dimension_scores.sort(key=lambda x: x[1], reverse=True)

    for i, (dim, score) in enumerate(dimension_scores[:3], 1):
        st.markdown(f"""
        **{i}. {dim}** - `{score:.1f}/100`
        - {'⭐ Elite' if score >= 95 else '✅ Fortaleza'}
        """)

with col2:
    st.markdown("### 🔧 Áreas de Mejora")

    # Get dimensions below 95 (weaknesses) and sort by score ascending (worst first)
    weaknesses = [d for d in dimension_scores if d[1] < 95]
    weaknesses.sort(key=lambda x: x[1])  # Sort ascending (lowest scores first)

    if weaknesses:
        for i, (dim, score) in enumerate(weaknesses[:3], 1):  # Show top 3 weaknesses
            st.markdown(f"""
            **{i}. {dim}** - `{score:.1f}/100`
            - {'⚠️ Área prioritaria' if score < 90 else '📈 Puede mejorar'}
            """)
    else:
        st.markdown("✅ **No hay debilidades significativas**")
        st.markdown("El equipo es elite en todas las dimensiones (>95)")

st.markdown("---")

# ============================================================================
# METHODOLOGY
# ============================================================================

st.markdown("## 🔬 Metodología")

with st.expander("📖 ¿Cómo funciona el sistema?", expanded=False):
    st.markdown("""
    ### 1. DNA Profiling

    Analizamos 6 dimensiones tácticas del Club América usando datos de StatsBomb:

    - **Progression**: Capacidad de avanzar el balón (pases/conducciones progresivas)
    - **Creation**: Generación de ocasiones (xA, pases clave, asistencias al tiro)
    - **Finishing**: Calidad de finalización (xG, tiros, calidad de tiros)
    - **Pressing**: Intensidad defensiva sin balón (presiones p90)
    - **Possession**: Control del balón (% pases completados, toques en tercio atacante)
    - **Dribbling**: Capacidad de regate (regates exitosos, % éxito)

    Cada dimensión se compara con el **Percentil 90 de Liga MX** (benchmarks de 19 equipos).

    ---

    ### 2. FitScore Algorithm

    Para cada jugador del scouting pool (18 equipos), calculamos un **FitScore** que combina:

    ```
    FitScore = (60% × DNA Match) + (30% × Gap Filling) + (10% × Role Fit)
    ```

    - **DNA Match (60%)**: Similitud coseno entre el DNA del jugador y el DNA de América
    - **Gap Filling (30%)**: Qué tanto el jugador fortalece las áreas débiles del equipo
    - **Role Fit (10%)**: Compatibilidad posicional y estilo de juego

    ---

    ### 3. Data Sources

    - **StatsBomb 360**: Datos de eventos de Liga MX 2024/2025
    - **Métricas per 90**: Todas normalizadas a 90 minutos
    - **Filtro de minutos**: Mínimo 270 minutos jugados
    - **Exclusiones**: Porteros (análisis solo para jugadores de campo)

    ---

    ### 4. Benchmarks

    - **P90**: Percentil 90 de 19 equipos (18 scouting + América)
    - **Threshold Elite**: Score > 95
    - **Threshold Fortaleza**: Score > 90
    - **Threshold Debilidad**: Score < 95 (para identificar gaps)
    """)

st.markdown("---")

# ============================================================================
# NEXT STEPS
# ============================================================================

st.markdown("## 🚀 Próximos Pasos")

st.info("""
👉 **Explora las páginas del menú lateral:**

1. **🧬 DNA Club América** - Análisis detallado del perfil táctico del equipo
2. **⚽ Recomendaciones** - Top 20 fichajes recomendados y jugadores a evitar

Cada página incluye visualizaciones interactivas y análisis detallado.
""")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>
    🦅 Club América - Scouting System | Temporada 2024/2025<br>
    Powered by StatsBomb Data | ISAC Hackathon 2025
    </small>
</div>
""", unsafe_allow_html=True)
