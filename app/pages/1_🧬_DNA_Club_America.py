"""
Club América - DNA Analysis Page
"""
import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import load_america_dna, load_benchmarks
from utils.styling import get_custom_css, CLUB_AMERICA_COLORS, get_score_color
from utils.visualizations import create_radar_chart, create_horizontal_bar_chart

# Page config
st.set_page_config(
    page_title="DNA Club América",
    page_icon="🧬",
    layout="wide"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================

try:
    dna_data = load_america_dna()
    benchmarks = load_benchmarks()
except Exception as e:
    st.error(f"❌ Error cargando datos: {e}")
    st.stop()

dimensions = dna_data['dimensions']
overall_score = dna_data.get('overall_score', 0)

# ============================================================================
# HEADER
# ============================================================================

st.title("🧬 Club América - DNA Táctico")
st.markdown(f"### Temporada {dna_data['season']}")
st.markdown("---")

# ============================================================================
# OVERALL SCORE
# ============================================================================

col1, col2, col3 = st.columns([2, 3, 2])

with col1:
    st.markdown("")

with col2:
    # Large overall score metric
    score_color = get_score_color(overall_score, thresholds={'high': 95, 'medium': 90})

    st.markdown(f"""
    <div class='dark-card' style='text-align: center; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h1 class='gold-text' style='margin: 0; font-size: 4rem;'>
            {overall_score:.1f}
        </h1>
        <h3>DNA Score Global</h3>
        <p class='gold-text' style='margin: 5px 0; font-size: 1.2rem;'>
            {dna_data.get('tactical_identity', 'Elite tactical profile')}
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("")

st.markdown("---")

# ============================================================================
# DIMENSION SCORES
# ============================================================================

st.markdown("## 📊 Scores por Dimensión")
st.markdown("")

# Display metrics in columns
col1, col2, col3 = st.columns(3)

dim_list = [
    ('progression', 'Progression', '📈'),
    ('creation', 'Creation', '🎨'),
    ('finishing', 'Finishing', '⚽'),
    ('pressing', 'Pressing', '💪'),
    ('possession', 'Possession', '🎯'),
    ('dribbling', 'Dribbling', '⚡')
]

for idx, (key, name, emoji) in enumerate(dim_list):
    col = [col1, col2, col3][idx % 3]

    score = dimensions[key]['score']
    strength = dimensions[key]['strength']

    with col:
        # Determine delta text
        if score >= 95:
            delta = "⭐ Elite"
            delta_color = "normal"
        elif score >= 90:
            delta = "✅ Fortaleza"
            delta_color = "normal"
        elif score >= 85:
            delta = "📈 Bueno"
            delta_color = "normal"
        else:
            delta = "⚠️ Mejora"
            delta_color = "inverse"

        st.metric(
            label=f"{emoji} {name}",
            value=f"{score:.1f}",
            delta=delta,
            delta_color=delta_color
        )

st.markdown("---")

# ============================================================================
# RADAR CHART
# ============================================================================

st.markdown("## 🎯 Perfil Táctico Visual")

col1, col2 = st.columns([3, 2])

with col1:
    # Radar chart
    radar_fig = create_radar_chart(dimensions)
    st.plotly_chart(radar_fig, use_container_width=True)

with col2:
    st.markdown("### 📖 Interpretación")
    st.markdown("")

    st.markdown("""
    El **radar chart** muestra el perfil táctico del Club América comparado
    con el **Percentil 90** de Liga MX (línea gris punteada).

    **Áreas que sobresalen del benchmark:**
    - Indican **superioridad táctica**
    - Fortalezas del equipo

    **Áreas dentro del benchmark:**
    - Indican **oportunidades de mejora**
    - Prioridades para fichajes
    """)

    # Show weaknesses
    weaknesses = [(k, v['score']) for k, v in dimensions.items() if v['score'] < 95]
    weaknesses.sort(key=lambda x: x[1])

    if weaknesses:
        st.markdown("#### 🔧 Áreas Prioritarias:")
        for dim_key, score in weaknesses[:2]:
            dim_name = dim_key.capitalize()
            st.markdown(f"- **{dim_name}**: {score:.1f}/100")

st.markdown("---")

# ============================================================================
# BAR CHART
# ============================================================================

st.markdown("## 📊 Ranking de Dimensiones")

bar_fig = create_horizontal_bar_chart(dimensions)
st.plotly_chart(bar_fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# DETAILED METRICS BY DIMENSION
# ============================================================================

st.markdown("## 🔍 Métricas Subyacentes por Dimensión")
st.markdown("Expande cada dimensión para ver las métricas que la componen y cómo se comparan con los benchmarks.")
st.markdown("")

for key, name, emoji in dim_list:
    dim_data = dimensions[key]
    score = dim_data['score']
    metrics = dim_data['metrics']
    description = dim_data.get('description', '')

    # Color based on score
    score_color = get_score_color(score, thresholds={'high': 95, 'medium': 85})

    with st.expander(f"{emoji} **{name}** - {score:.1f}/100", expanded=False):

        st.markdown(f"**Descripción:** {description}")
        st.markdown("")

        # Show metrics in columns
        metric_items = list(metrics.items())
        n_cols = min(3, len(metric_items))
        cols = st.columns(n_cols)

        for idx, (metric_name, value) in enumerate(metric_items):
            col = cols[idx % n_cols]

            with col:
                # Format metric name
                display_name = metric_name.replace('_', ' ').title()

                # Format value based on magnitude
                value_str = f"{value:.4f}" if value < 1 else f"{value:.2f}"

                # Get benchmark if available
                benchmark_key = metric_name
                if benchmark_key in benchmarks:
                    benchmark_val = benchmarks[benchmark_key]
                    benchmark_str = f"{benchmark_val:.4f}" if benchmark_val < 1 else f"{benchmark_val:.2f}"
                    pct_of_benchmark = (value / benchmark_val * 100) if benchmark_val > 0 else 0

                    st.markdown(f"""
                    **{display_name}**
                    - Valor: `{value_str}`
                    - Benchmark P90: `{benchmark_str}`
                    - % del benchmark: `{pct_of_benchmark:.1f}%`
                    """)
                else:
                    st.markdown(f"""
                    **{display_name}**
                    - Valor: `{value_str}`
                    """)

        st.markdown("")

        # Interpretation
        if score >= 95:
            st.success(f"✅ **Elite**: {name} es una fortaleza distintiva del equipo")
        elif score >= 90:
            st.info(f"📈 **Fuerte**: {name} está por encima del promedio de la liga")
        elif score >= 85:
            st.warning(f"⚠️ **Bueno**: {name} tiene margen de mejora")
        else:
            st.error(f"🔧 **Prioritario**: {name} requiere refuerzo inmediato")

st.markdown("---")

# ============================================================================
# TACTICAL SUMMARY
# ============================================================================

st.markdown("## 📝 Resumen Táctico")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💪 Fortalezas Clave")

    strengths = [(k, v['score']) for k, v in dimensions.items() if v['score'] >= 95]
    strengths.sort(key=lambda x: x[1], reverse=True)

    if strengths:
        for dim_key, score in strengths:
            dim_name = dim_key.capitalize()
            dim_desc = dimensions[dim_key].get('description', '')
            st.markdown(f"""
            **{dim_name}** ({score:.1f}/100)
            - {dim_desc}
            - Mantener y capitalizar esta ventaja
            """)
    else:
        st.info("Todas las dimensiones están en nivel bueno pero sin dominancia clara (90-95)")

with col2:
    st.markdown("### 🎯 Recomendaciones de Fichajes")

    weaknesses = [(k, v['score']) for k, v in dimensions.items() if v['score'] < 95]
    weaknesses.sort(key=lambda x: x[1])

    if weaknesses:
        st.markdown("**Priorizar jugadores que aporten en:**")
        for dim_key, score in weaknesses[:3]:
            dim_name = dim_key.capitalize()
            dim_desc = dimensions[dim_key].get('description', '')
            st.markdown(f"""
            **{dim_name}** (Score actual: {score:.1f})
            - {dim_desc}
            - Gap: {95 - score:.1f} puntos vs elite
            """)
    else:
        st.success("✅ Equipo balanceado en todas las dimensiones. Buscar jugadores versátiles.")

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>
    🧬 DNA Analysis basado en StatsBomb 360 data | Benchmarks P90 de 19 equipos<br>
    Temporada 2024/2025 | Liga MX
    </small>
</div>
""", unsafe_allow_html=True)
