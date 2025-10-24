"""
Club América - Player Search Page
Search any player from the scouting pool and view detailed analysis
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import (
    load_scouting_pool,
    load_america_dna,
    load_player_fit_scores
)
from utils.styling import get_custom_css, CLUB_AMERICA_COLORS
from utils.visualizations import create_comparison_radar

# Page config
st.set_page_config(
    page_title="Buscar Jugador",
    page_icon="🔍",
    layout="wide"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================

try:
    scouting_pool = load_scouting_pool()
    dna_data = load_america_dna()
    player_fit_scores = load_player_fit_scores()
except Exception as e:
    st.error(f"❌ Error cargando datos: {e}")
    st.stop()

# Create lookup dictionary for player DNA scores
player_dna_lookup = {
    player['player_name']: player
    for player in player_fit_scores['players']
}

# ============================================================================
# HEADER
# ============================================================================

st.title("🔍 Búsqueda de Jugadores")
st.markdown("### Explora cualquier jugador del pool de scouting")
st.markdown("---")

# Overview stats
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="👥 Jugadores Disponibles",
        value=f"{len(scouting_pool)}",
        delta="18 equipos"
    )

with col2:
    st.metric(
        label="🏟️ Equipos",
        value=f"{scouting_pool['team.name'].nunique()}",
        delta="Liga MX"
    )

with col3:
    st.metric(
        label="📍 Posiciones",
        value=f"{scouting_pool['primary_position'].nunique()}",
        delta="Todas cubiertas"
    )

st.markdown("---")

# ============================================================================
# SEARCH INTERFACE
# ============================================================================

st.markdown("## 🎯 Buscar Jugador")

# Search options
col1, col2 = st.columns([2, 1])

with col2:
    # Filter by team (FIRST - to filter player list)
    all_teams = ['Todos'] + sorted(scouting_pool['team.name'].unique().tolist())
    selected_team = st.selectbox(
        "Filtrar por equipo",
        options=all_teams,
        help="Filtra jugadores por equipo"
    )

# Apply team filter to player list
if selected_team != 'Todos':
    filtered_pool = scouting_pool[scouting_pool['team.name'] == selected_team]
    available_players = sorted(filtered_pool['player.name'].unique().tolist())
    st.info(f"📊 {len(available_players)} jugadores disponibles en {selected_team}")
else:
    available_players = sorted(scouting_pool['player.name'].unique().tolist())

with col1:
    # Search by name (uses filtered list)
    selected_player = st.selectbox(
        "Selecciona un jugador",
        options=available_players,
        index=None,
        placeholder="Escribe o selecciona el nombre de un jugador...",
        help="Busca por nombre de jugador en el pool de scouting"
    )

st.markdown("---")

# ============================================================================
# PLAYER DETAILS
# ============================================================================

if selected_player:
    # Get player data from fit scores
    player_fit_data = player_dna_lookup.get(selected_player)

    if not player_fit_data:
        st.error(f"❌ No se encontró información de FitScore para {selected_player}")
        st.stop()

    # Get player data from scouting pool
    player_pool_data = scouting_pool[scouting_pool['player.name'] == selected_player]

    if player_pool_data.empty:
        st.error(f"❌ No se encontró información del jugador {selected_player}")
        st.stop()

    player_metrics = player_pool_data.iloc[0]

    # Build player data dict
    player_data = {
        'player_name': selected_player,
        'team': player_metrics['team.name'],
        'position': player_metrics['primary_position'],
        'minutes': player_metrics['total_minutes'],
        'matches': player_metrics['matches_played'],
        'fit_score': player_fit_data['fit_score'],
        'dna_match': player_fit_data['dna_match_score'],
        'gap_filling': player_fit_data['gap_filling_score']
    }

    # ============================================================
    # PLAYER CARD & FITSCORE
    # ============================================================

    st.markdown(f"## 👤 {selected_player}")

    col1, col2 = st.columns([1, 2])

    with col1:
        # Player info card
        st.markdown(f"""
        <div class='dark-card' style='padding: 20px; border-radius: 10px;'>
            <h2 class='gold-text' style='margin: 0;'>
                {player_data['player_name']}
            </h2>
            <p style='font-size: 1.1rem; margin: 10px 0;'>
                🏟️ {player_data['team']}<br>
                📍 {player_data['position']}<br>
                ⏱️ {player_data['minutes']:.0f} minutos<br>
                🎮 {player_data['matches']:.0f} partidos
            </p>
            <hr style='border-color: {CLUB_AMERICA_COLORS['secondary']};'>
            <h1 class='gold-text' style='text-align: center; margin: 10px 0;'>
                {player_data['fit_score']:.1f}
            </h1>
            <p style='text-align: center; font-size: 1.2rem; margin: 0;'>FitScore</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # FitScore breakdown
        st.markdown("#### 📊 Desglose de FitScore")

        # DNA Match
        st.markdown(f"**🧬 DNA Match:** `{player_data['dna_match']:.2f}/100`")
        st.progress(player_data['dna_match'] / 100)

        # Gap Filling
        st.markdown(f"**🎯 Gap Filling:** `{player_data['gap_filling']:.2f}/100`")
        st.progress(player_data['gap_filling'] / 100)

        # Role Fit (calculate from formula)
        role_fit = (player_data['fit_score'] -
                   (0.6 * player_data['dna_match']) -
                   (0.3 * player_data['gap_filling'])) / 0.1

        st.markdown(f"**💼 Role Fit:** `{role_fit:.2f}/100`")
        st.progress(role_fit / 100)

        st.markdown("")

    # Analysis
    st.markdown("#### 📋 Análisis del Jugador")

    # Generate analysis based on FitScore
    if player_data['fit_score'] >= 95:
        st.success(f"""
        ✅ **Excelente fichaje potencial**

        {selected_player} tiene un FitScore de {player_data['fit_score']:.1f}, indicando alta compatibilidad
        con el estilo de juego del Club América. Su perfil táctil se alinea muy bien con las necesidades del equipo.
        """)
    elif player_data['fit_score'] >= 90:
        st.info(f"""
        📈 **Buen fichaje potencial**

        {selected_player} muestra compatibilidad sólida con FitScore de {player_data['fit_score']:.1f}.
        Podría adaptarse bien al sistema táctico del Club América.
        """)
    elif player_data['fit_score'] >= 85:
        st.warning(f"""
        ⚠️ **Fichaje con reservas**

        {selected_player} tiene un FitScore moderado de {player_data['fit_score']:.1f}.
        Requiere evaluación más profunda antes de considerar su fichaje.
        """)
    else:
        st.error(f"""
        ❌ **No recomendado**

        {selected_player} presenta bajo FitScore de {player_data['fit_score']:.1f}.
        Su perfil no se alinea bien con las necesidades del Club América.
        """)

    st.markdown("---")

    # ============================================================
    # RADAR CHART COMPARISON
    # ============================================================
    st.markdown("### 📊 Comparación de DNA: Jugador vs Club América")

    radar_fig = create_comparison_radar(
        player_dna=player_fit_data['player_dna'],
        team_dna=dna_data['dimensions'],
        player_name=selected_player
    )
    st.plotly_chart(radar_fig, use_container_width=True)

    # Interpretation
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**💪 Dimensiones Compatibles:**")
        compatible = []
        for dim in ['progression', 'creation', 'finishing', 'pressing', 'possession', 'dribbling']:
            player_score = player_fit_data['player_dna'][dim]
            team_score = dna_data['dimensions'][dim]['score']
            if player_score >= 90 and team_score >= 90:
                compatible.append(f"- **{dim.capitalize()}**: Ambos elite")
        if compatible:
            for item in compatible:
                st.markdown(item)
        else:
            st.markdown("- Perfil complementario al equipo")

    with col2:
        st.markdown("**🎯 Aportes al Equipo:**")
        contributions = []
        for dim in ['progression', 'creation', 'finishing', 'pressing', 'possession', 'dribbling']:
            player_score = player_fit_data['player_dna'][dim]
            team_score = dna_data['dimensions'][dim]['score']
            if player_score > team_score + 5:
                diff = player_score - team_score
                contributions.append(f"- **{dim.capitalize()}**: +{diff:.1f} puntos")
        if contributions:
            for item in contributions[:3]:
                st.markdown(item)
        else:
            st.markdown("- Mantiene el nivel del equipo")

    st.markdown("---")

    # ============================================================
    # RANKINGS
    # ============================================================
    st.markdown("### 🏆 Rankings en el Pool de Scouting")

    # Calculate rankings
    all_fit_scores = [p['fit_score'] for p in player_fit_scores['players']]
    player_rank = sorted(all_fit_scores, reverse=True).index(player_data['fit_score']) + 1

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Ranking General",
            value=f"#{player_rank}",
            delta=f"Top {(player_rank/len(all_fit_scores)*100):.1f}%"
        )

    with col2:
        # Top dimension
        player_dna = player_fit_data['player_dna']
        top_dim = max(player_dna.items(), key=lambda x: x[1])
        st.metric(
            label="Dimensión Más Fuerte",
            value=top_dim[0].capitalize(),
            delta=f"{top_dim[1]:.1f}/100"
        )

    with col3:
        # DNA Match ranking
        all_dna_matches = [p['dna_match_score'] for p in player_fit_scores['players']]
        dna_rank = sorted(all_dna_matches, reverse=True).index(player_data['dna_match']) + 1
        st.metric(
            label="DNA Match Rank",
            value=f"#{dna_rank}",
            delta=f"{player_data['dna_match']:.1f}/100"
        )

    with col4:
        # Gap Filling ranking
        all_gap_fills = [p['gap_filling_score'] for p in player_fit_scores['players']]
        gap_rank = sorted(all_gap_fills, reverse=True).index(player_data['gap_filling']) + 1
        st.metric(
            label="Gap Filling Rank",
            value=f"#{gap_rank}",
            delta=f"{player_data['gap_filling']:.1f}/100"
        )

    st.markdown("---")

    # ============================================================
    # POSITIONAL ANALYSIS
    # ============================================================
    st.markdown("### 📍 Análisis Posicional")

    # Get players in same position
    same_position = [
        p for p in player_fit_scores['players']
        if p['position'] == player_data['position']
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Posición:** {player_data['position']}")
        st.markdown(f"**Jugadores en esta posición:** {len(same_position)}")

        if len(same_position) > 1:
            # Position ranking
            position_scores = [p['fit_score'] for p in same_position]
            position_rank = sorted(position_scores, reverse=True).index(player_data['fit_score']) + 1

            st.markdown(f"**Ranking en posición:** #{position_rank} de {len(same_position)}")

            # Average FitScore in position
            avg_position_score = sum(position_scores) / len(position_scores)
            diff_from_avg = player_data['fit_score'] - avg_position_score

            if diff_from_avg > 0:
                st.success(f"✅ {diff_from_avg:.1f} puntos por encima del promedio de la posición")
            else:
                st.info(f"📊 {abs(diff_from_avg):.1f} puntos por debajo del promedio de la posición")

    with col2:
        st.markdown("**🎯 Métricas Clave para la Posición:**")

        # Position-specific metrics
        if 'Midfield' in player_data['position'] or 'Mid' in player_data['position']:
            st.markdown(f"- Progressive passes p90: **{player_metrics['progressive_passes_p90']:.2f}**")
            st.markdown(f"- Key passes p90: **{player_metrics['key_passes_p90']:.2f}**")
            st.markdown(f"- Pressures p90: **{player_metrics['pressures_p90']:.2f}**")
        elif 'Forward' in player_data['position'] or 'Wing' in player_data['position']:
            st.markdown(f"- xG p90: **{player_metrics['xG_p90']:.4f}**")
            st.markdown(f"- Shots p90: **{player_metrics['shots_p90']:.2f}**")
            st.markdown(f"- Dribbles successful p90: **{player_metrics['dribbles_successful_p90']:.2f}**")
        elif 'Back' in player_data['position'] or 'Def' in player_data['position']:
            st.markdown(f"- Tackles p90: **{player_metrics['tackles_p90']:.2f}**")
            st.markdown(f"- Interceptions p90: **{player_metrics['interceptions_p90']:.2f}**")
            st.markdown(f"- Pass completion: **{player_metrics['pass_completion_pct']:.1f}%**")
        else:
            st.markdown(f"- Progressive passes p90: **{player_metrics['progressive_passes_p90']:.2f}**")
            st.markdown(f"- xA p90: **{player_metrics['xA_p90']:.4f}**")
            st.markdown(f"- Pressures p90: **{player_metrics['pressures_p90']:.2f}**")

    st.markdown("---")

    # ============================================================
    # DIMENSION BREAKDOWN
    # ============================================================
    st.markdown("### 🧬 Breakdown de Dimensiones DNA")

    col1, col2, col3 = st.columns(3)

    dimensions = ['progression', 'creation', 'finishing', 'pressing', 'possession', 'dribbling']
    emojis = ['📈', '🎨', '⚽', '💪', '🎯', '⚡']

    for idx, (dim, emoji) in enumerate(zip(dimensions, emojis)):
        col = [col1, col2, col3][idx % 3]

        player_score = player_fit_data['player_dna'][dim]
        team_score = dna_data['dimensions'][dim]['score']
        diff = player_score - team_score

        with col:
            st.markdown(f"**{emoji} {dim.capitalize()}**")
            st.markdown(f"- Jugador: `{player_score:.1f}/100`")
            st.markdown(f"- Club América: `{team_score:.1f}/100`")

            if diff > 5:
                st.markdown(f"- 🟢 **+{diff:.1f}** vs equipo")
            elif diff < -5:
                st.markdown(f"- 🔴 **{diff:.1f}** vs equipo")
            else:
                st.markdown(f"- 🟡 **{diff:+.1f}** vs equipo")

            st.markdown("")

else:
    st.info("👆 Selecciona un jugador para ver su análisis detallado")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>
    🔍 Búsqueda de Jugadores | Pool completo de scouting<br>
    Powered by StatsBomb Data | ISAC Hackathon 2025
    </small>
</div>
""", unsafe_allow_html=True)
