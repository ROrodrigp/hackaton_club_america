"""
Club América - Player Recommendations Page
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import (
    load_top_recommendations,
    load_worst_recommendations,
    load_scouting_pool,
    load_america_dna,
    load_player_fit_scores
)
from utils.styling import get_custom_css, CLUB_AMERICA_COLORS, get_score_color
from utils.visualizations import create_comparison_radar

# Page config
st.set_page_config(
    page_title="Recomendaciones de Jugadores",
    page_icon="⚽",
    layout="wide"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================

try:
    top_20 = load_top_recommendations()
    worst_20 = load_worst_recommendations()
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

st.title("⚽ Recomendaciones de Jugadores")
st.markdown("### Sistema de FitScore para Club América")
st.markdown("---")

# Overview metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="👥 Pool de Jugadores",
        value=f"{len(scouting_pool)}",
        delta="18 equipos"
    )

with col2:
    st.metric(
        label="✅ Top Recomendados",
        value="20",
        delta=f"Avg FitScore: {top_20['fit_score'].mean():.1f}"
    )

with col3:
    st.metric(
        label="❌ Jugadores a Evitar",
        value="20",
        delta=f"Avg FitScore: {worst_20['fit_score'].mean():.1f}"
    )

with col4:
    best_player = top_20.iloc[0]
    st.metric(
        label="🏆 Mejor FitScore",
        value=f"{best_player['fit_score']:.1f}",
        delta=best_player['player_name']
    )

st.markdown("---")

# Info box
st.info("""
**📊 FitScore Algorithm:**
`FitScore = (60% × DNA Match) + (30% × Gap Filling) + (10% × Role Fit)`

- **DNA Match**: Similitud táctica entre jugador y Club América
- **Gap Filling**: Qué tanto fortalece las áreas débiles del equipo
- **Role Fit**: Compatibilidad posicional y estilo de juego
""")

st.markdown("---")

# ============================================================================
# TABS: TOP 20 vs WORST 20
# ============================================================================

tab1, tab2 = st.tabs(["✅ Top 20: Jugadores Recomendados", "❌ Top 20: Jugadores a Evitar"])

# ============================================================================
# TAB 1: TOP 20 RECOMMENDED
# ============================================================================

with tab1:
    st.markdown("## ⭐ Top 20 Recomendaciones")
    st.markdown("Los jugadores con mejor FitScore para reforzar al Club América")
    st.markdown("")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        # Team filter
        all_teams = sorted(top_20['team'].unique())
        selected_teams = st.multiselect(
            "🏟️ Filtrar por Equipo",
            options=all_teams,
            default=all_teams,
            key="top_teams"
        )

    with col2:
        # Position filter
        all_positions = sorted(top_20['position'].unique())
        selected_positions = st.multiselect(
            "📍 Filtrar por Posición",
            options=all_positions,
            default=all_positions,
            key="top_positions"
        )

    with col3:
        # FitScore filter
        min_fitscore = st.slider(
            "⭐ FitScore Mínimo",
            min_value=float(top_20['fit_score'].min()),
            max_value=float(top_20['fit_score'].max()),
            value=float(top_20['fit_score'].min()),
            step=0.1,
            key="top_fitscore"
        )

    # Filter data
    filtered_top = top_20[
        (top_20['team'].isin(selected_teams)) &
        (top_20['position'].isin(selected_positions)) &
        (top_20['fit_score'] >= min_fitscore)
    ]

    st.markdown(f"**Mostrando {len(filtered_top)} de {len(top_20)} jugadores**")
    st.markdown("")

    # Display table
    if len(filtered_top) > 0:
        # Prepare display dataframe
        display_df = filtered_top[[
            'rank', 'player_name', 'team', 'position',
            'fit_score', 'dna_match', 'gap_filling'
        ]].copy()

        # Rename columns for display
        display_df.columns = [
            'Rank', 'Jugador', 'Equipo', 'Posición',
            'FitScore', 'DNA Match', 'Gap Filling'
        ]

        # Round numeric columns
        display_df['FitScore'] = display_df['FitScore'].round(2)
        display_df['DNA Match'] = display_df['DNA Match'].round(2)
        display_df['Gap Filling'] = display_df['Gap Filling'].round(2)

        # Color coding function
        def color_fitscore(val):
            if val >= 95:
                color = CLUB_AMERICA_COLORS['success']
            elif val >= 90:
                color = CLUB_AMERICA_COLORS['warning']
            else:
                color = CLUB_AMERICA_COLORS['danger']
            return f'background-color: {color}; color: white; font-weight: bold;'

        # Style the dataframe
        styled_df = display_df.style.applymap(
            color_fitscore,
            subset=['FitScore']
        ).format({
            'FitScore': '{:.2f}',
            'DNA Match': '{:.2f}',
            'Gap Filling': '{:.2f}'
        })

        st.dataframe(
            styled_df,
            use_container_width=True,
            height=400,
            hide_index=True
        )

        st.markdown("---")

        # Player selection for details
        st.markdown("### 👤 Detalles del Jugador")

        selected_player_name = st.selectbox(
            "Selecciona un jugador para ver detalles",
            options=filtered_top['player_name'].tolist(),
            key="selected_top_player"
        )

        if selected_player_name:
            player_data = filtered_top[filtered_top['player_name'] == selected_player_name].iloc[0]

            # Display player card
            col1, col2 = st.columns([1, 2])

            with col1:
                # Player info card
                st.markdown(f"""
                <div style='padding: 20px; background-color: {CLUB_AMERICA_COLORS['primary']};
                            border-radius: 10px; color: white;'>
                    <h2 style='color: {CLUB_AMERICA_COLORS['secondary']}; margin: 0;'>
                        {player_data['player_name']}
                    </h2>
                    <p style='font-size: 1.1rem; margin: 10px 0;'>
                        🏟️ {player_data['team']}<br>
                        📍 {player_data['position']}<br>
                        ⏱️ {player_data['minutes']:.0f} minutos<br>
                        🎮 {player_data['matches']:.0f} partidos
                    </p>
                    <hr style='border-color: {CLUB_AMERICA_COLORS['secondary']};'>
                    <h1 style='color: {CLUB_AMERICA_COLORS['secondary']}; text-align: center; margin: 10px 0;'>
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

            # Why recommend
            st.markdown("#### ✅ ¿Por qué ficharlo?")
            st.success(player_data['why_recommend'])

            st.markdown("---")

            # Get player detailed data
            player_full_data = player_dna_lookup.get(selected_player_name)

            if player_full_data:
                # ============================================================
                # RADAR CHART COMPARISON
                # ============================================================
                st.markdown("### 📊 Comparación de DNA: Jugador vs Club América")

                radar_fig = create_comparison_radar(
                    player_dna=player_full_data['player_dna'],
                    team_dna=dna_data['dimensions'],
                    player_name=selected_player_name
                )
                st.plotly_chart(radar_fig, use_container_width=True)

                # Interpretation
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**💪 Dimensiones Compatibles:**")
                    compatible = []
                    for dim in ['progression', 'creation', 'finishing', 'pressing', 'possession', 'dribbling']:
                        player_score = player_full_data['player_dna'][dim]
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
                        player_score = player_full_data['player_dna'][dim]
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
                    player_dna = player_full_data['player_dna']
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

                    # Get player's key metrics from scouting pool
                    player_pool_data = scouting_pool[
                        scouting_pool['player.name'] == selected_player_name
                    ]

                    if not player_pool_data.empty:
                        player_metrics = player_pool_data.iloc[0]

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

    else:
        st.warning("No hay jugadores que coincidan con los filtros seleccionados.")

# ============================================================================
# TAB 2: WORST 20
# ============================================================================

with tab2:
    st.markdown("## ⚠️ Top 20 Jugadores a Evitar")
    st.markdown("Los jugadores con menor compatibilidad con el estilo del Club América")
    st.markdown("")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        # Team filter
        all_teams_worst = sorted(worst_20['team'].unique())
        selected_teams_worst = st.multiselect(
            "🏟️ Filtrar por Equipo",
            options=all_teams_worst,
            default=all_teams_worst,
            key="worst_teams"
        )

    with col2:
        # Position filter
        all_positions_worst = sorted(worst_20['position'].unique())
        selected_positions_worst = st.multiselect(
            "📍 Filtrar por Posición",
            options=all_positions_worst,
            default=all_positions_worst,
            key="worst_positions"
        )

    with col3:
        # FitScore filter
        max_fitscore = st.slider(
            "⭐ FitScore Máximo",
            min_value=float(worst_20['fit_score'].min()),
            max_value=float(worst_20['fit_score'].max()),
            value=float(worst_20['fit_score'].max()),
            step=0.1,
            key="worst_fitscore"
        )

    # Filter data
    filtered_worst = worst_20[
        (worst_20['team'].isin(selected_teams_worst)) &
        (worst_20['position'].isin(selected_positions_worst)) &
        (worst_20['fit_score'] <= max_fitscore)
    ]

    st.markdown(f"**Mostrando {len(filtered_worst)} de {len(worst_20)} jugadores**")
    st.markdown("")

    # Display table
    if len(filtered_worst) > 0:
        # Prepare display dataframe
        display_df_worst = filtered_worst[[
            'rank', 'player_name', 'team', 'position',
            'fit_score', 'dna_match', 'gap_filling'
        ]].copy()

        # Rename columns for display
        display_df_worst.columns = [
            'Rank', 'Jugador', 'Equipo', 'Posición',
            'FitScore', 'DNA Match', 'Gap Filling'
        ]

        # Round numeric columns
        display_df_worst['FitScore'] = display_df_worst['FitScore'].round(2)
        display_df_worst['DNA Match'] = display_df_worst['DNA Match'].round(2)
        display_df_worst['Gap Filling'] = display_df_worst['Gap Filling'].round(2)

        # Color coding function (inverted for worst)
        def color_fitscore_worst(val):
            if val < 60:
                color = CLUB_AMERICA_COLORS['danger']
            elif val < 70:
                color = CLUB_AMERICA_COLORS['warning']
            else:
                color = CLUB_AMERICA_COLORS['success']
            return f'background-color: {color}; color: white; font-weight: bold;'

        # Style the dataframe
        styled_df_worst = display_df_worst.style.applymap(
            color_fitscore_worst,
            subset=['FitScore']
        ).format({
            'FitScore': '{:.2f}',
            'DNA Match': '{:.2f}',
            'Gap Filling': '{:.2f}'
        })

        st.dataframe(
            styled_df_worst,
            use_container_width=True,
            height=400,
            hide_index=True
        )

        st.markdown("---")

        # Player selection for details
        st.markdown("### 👤 Análisis del Jugador")

        selected_player_name_worst = st.selectbox(
            "Selecciona un jugador para ver por qué evitarlo",
            options=filtered_worst['player_name'].tolist(),
            key="selected_worst_player"
        )

        if selected_player_name_worst:
            player_data_worst = filtered_worst[
                filtered_worst['player_name'] == selected_player_name_worst
            ].iloc[0]

            # Display player card
            col1, col2 = st.columns([1, 2])

            with col1:
                # Player info card (red theme)
                st.markdown(f"""
                <div style='padding: 20px; background-color: #dc3545;
                            border-radius: 10px; color: white;'>
                    <h2 style='color: white; margin: 0;'>
                        {player_data_worst['player_name']}
                    </h2>
                    <p style='font-size: 1.1rem; margin: 10px 0;'>
                        🏟️ {player_data_worst['team']}<br>
                        📍 {player_data_worst['position']}<br>
                        ⏱️ {player_data_worst['minutes']:.0f} minutos<br>
                        🎮 {player_data_worst['matches']:.0f} partidos
                    </p>
                    <hr style='border-color: white;'>
                    <h1 style='color: white; text-align: center; margin: 10px 0;'>
                        {player_data_worst['fit_score']:.1f}
                    </h1>
                    <p style='text-align: center; font-size: 1.2rem; margin: 0;'>FitScore</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # FitScore breakdown
                st.markdown("#### 📊 Desglose de FitScore")

                # DNA Match
                st.markdown(f"**🧬 DNA Match:** `{player_data_worst['dna_match']:.2f}/100`")
                st.progress(player_data_worst['dna_match'] / 100)

                # Gap Filling
                st.markdown(f"**🎯 Gap Filling:** `{player_data_worst['gap_filling']:.2f}/100`")
                st.progress(player_data_worst['gap_filling'] / 100)

                # Role Fit
                role_fit_worst = (player_data_worst['fit_score'] -
                                 (0.6 * player_data_worst['dna_match']) -
                                 (0.3 * player_data_worst['gap_filling'])) / 0.1

                st.markdown(f"**💼 Role Fit:** `{role_fit_worst:.2f}/100`")
                st.progress(role_fit_worst / 100)

                st.markdown("")

            # Why avoid
            st.markdown("#### ❌ ¿Por qué evitarlo?")
            st.error(player_data_worst['why_avoid'])

            st.markdown("---")

            # Get player detailed data
            player_full_data_worst = player_dna_lookup.get(selected_player_name_worst)

            if player_full_data_worst:
                # ============================================================
                # RADAR CHART COMPARISON
                # ============================================================
                st.markdown("### 📊 Comparación de DNA: Jugador vs Club América")

                radar_fig_worst = create_comparison_radar(
                    player_dna=player_full_data_worst['player_dna'],
                    team_dna=dna_data['dimensions'],
                    player_name=selected_player_name_worst
                )
                st.plotly_chart(radar_fig_worst, use_container_width=True)

                # Interpretation (focusing on gaps)
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**⚠️ Dimensiones Débiles:**")
                    weak_dims = []
                    for dim in ['progression', 'creation', 'finishing', 'pressing', 'possession', 'dribbling']:
                        player_score = player_full_data_worst['player_dna'][dim]
                        if player_score < 70:
                            weak_dims.append(f"- **{dim.capitalize()}**: {player_score:.1f}/100")
                    if weak_dims:
                        for item in weak_dims[:3]:
                            st.markdown(item)
                    else:
                        st.markdown("- No hay debilidades críticas en DNA")

                with col2:
                    st.markdown("**📉 Gaps vs Club América:**")
                    gaps = []
                    for dim in ['progression', 'creation', 'finishing', 'pressing', 'possession', 'dribbling']:
                        player_score = player_full_data_worst['player_dna'][dim]
                        team_score = dna_data['dimensions'][dim]['score']
                        if team_score - player_score > 10:
                            diff = team_score - player_score
                            gaps.append(f"- **{dim.capitalize()}**: -{diff:.1f} puntos")
                    if gaps:
                        for item in gaps[:3]:
                            st.markdown(item)
                    else:
                        st.markdown("- Baja compatibilidad táctica general")

                st.markdown("---")

                # ============================================================
                # RANKINGS
                # ============================================================
                st.markdown("### 🏆 Rankings en el Pool de Scouting")

                # Calculate rankings
                all_fit_scores = [p['fit_score'] for p in player_fit_scores['players']]
                player_rank_worst = sorted(all_fit_scores, reverse=True).index(player_data_worst['fit_score']) + 1

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        label="Ranking General",
                        value=f"#{player_rank_worst}",
                        delta=f"Bottom {(100 - (player_rank_worst/len(all_fit_scores)*100)):.1f}%",
                        delta_color="inverse"
                    )

                with col2:
                    # Weakest dimension
                    player_dna_worst = player_full_data_worst['player_dna']
                    bottom_dim = min(player_dna_worst.items(), key=lambda x: x[1])
                    st.metric(
                        label="Dimensión Más Débil",
                        value=bottom_dim[0].capitalize(),
                        delta=f"{bottom_dim[1]:.1f}/100",
                        delta_color="inverse"
                    )

                with col3:
                    # DNA Match ranking
                    all_dna_matches = [p['dna_match_score'] for p in player_fit_scores['players']]
                    dna_rank_worst = sorted(all_dna_matches, reverse=True).index(player_data_worst['dna_match']) + 1
                    st.metric(
                        label="DNA Match Rank",
                        value=f"#{dna_rank_worst}",
                        delta=f"{player_data_worst['dna_match']:.1f}/100"
                    )

                with col4:
                    # Gap Filling ranking
                    all_gap_fills = [p['gap_filling_score'] for p in player_fit_scores['players']]
                    gap_rank_worst = sorted(all_gap_fills, reverse=True).index(player_data_worst['gap_filling']) + 1
                    st.metric(
                        label="Gap Filling Rank",
                        value=f"#{gap_rank_worst}",
                        delta=f"{player_data_worst['gap_filling']:.1f}/100",
                        delta_color="inverse"
                    )

                st.markdown("---")

                # ============================================================
                # POSITIONAL ANALYSIS
                # ============================================================
                st.markdown("### 📍 Análisis Posicional")

                # Get players in same position
                same_position_worst = [
                    p for p in player_fit_scores['players']
                    if p['position'] == player_data_worst['position']
                ]

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Posición:** {player_data_worst['position']}")
                    st.markdown(f"**Jugadores en esta posición:** {len(same_position_worst)}")

                    if len(same_position_worst) > 1:
                        # Position ranking
                        position_scores_worst = [p['fit_score'] for p in same_position_worst]
                        position_rank_worst = sorted(position_scores_worst, reverse=True).index(player_data_worst['fit_score']) + 1

                        st.markdown(f"**Ranking en posición:** #{position_rank_worst} de {len(same_position_worst)}")

                        # Average FitScore in position
                        avg_position_score_worst = sum(position_scores_worst) / len(position_scores_worst)
                        diff_from_avg_worst = player_data_worst['fit_score'] - avg_position_score_worst

                        if diff_from_avg_worst < 0:
                            st.error(f"❌ {abs(diff_from_avg_worst):.1f} puntos por debajo del promedio de la posición")
                        else:
                            st.info(f"📊 {diff_from_avg_worst:.1f} puntos por encima del promedio de la posición")

                with col2:
                    st.markdown("**📊 Métricas de la Posición:**")

                    # Get player's key metrics from scouting pool
                    player_pool_data_worst = scouting_pool[
                        scouting_pool['player.name'] == selected_player_name_worst
                    ]

                    if not player_pool_data_worst.empty:
                        player_metrics_worst = player_pool_data_worst.iloc[0]

                        # Position-specific metrics
                        if 'Midfield' in player_data_worst['position'] or 'Mid' in player_data_worst['position']:
                            st.markdown(f"- Progressive passes p90: **{player_metrics_worst['progressive_passes_p90']:.2f}**")
                            st.markdown(f"- Key passes p90: **{player_metrics_worst['key_passes_p90']:.2f}**")
                            st.markdown(f"- Pressures p90: **{player_metrics_worst['pressures_p90']:.2f}**")
                        elif 'Forward' in player_data_worst['position'] or 'Wing' in player_data_worst['position']:
                            st.markdown(f"- xG p90: **{player_metrics_worst['xG_p90']:.4f}**")
                            st.markdown(f"- Shots p90: **{player_metrics_worst['shots_p90']:.2f}**")
                            st.markdown(f"- Dribbles successful p90: **{player_metrics_worst['dribbles_successful_p90']:.2f}**")
                        elif 'Back' in player_data_worst['position'] or 'Def' in player_data_worst['position']:
                            st.markdown(f"- Tackles p90: **{player_metrics_worst['tackles_p90']:.2f}**")
                            st.markdown(f"- Interceptions p90: **{player_metrics_worst['interceptions_p90']:.2f}**")
                            st.markdown(f"- Pass completion: **{player_metrics_worst['pass_completion_pct']:.1f}%**")
                        else:
                            st.markdown(f"- Progressive passes p90: **{player_metrics_worst['progressive_passes_p90']:.2f}**")
                            st.markdown(f"- xA p90: **{player_metrics_worst['xA_p90']:.4f}**")
                            st.markdown(f"- Pressures p90: **{player_metrics_worst['pressures_p90']:.2f}**")

    else:
        st.warning("No hay jugadores que coincidan con los filtros seleccionados.")

st.markdown("---")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>
    ⚽ Recomendaciones basadas en FitScore Algorithm | Pool de 18 equipos de Liga MX<br>
    Temporada 2024/2025 | Datos de StatsBomb 360
    </small>
</div>
""", unsafe_allow_html=True)
