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
    load_america_dna
)
from utils.styling import get_custom_css, CLUB_AMERICA_COLORS, get_score_color

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
except Exception as e:
    st.error(f"❌ Error cargando datos: {e}")
    st.stop()

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
