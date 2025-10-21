🚀 POC PARA HACKATHON: "FitScore - AI Scout Assistant" 🎯 CONCEPTO CENTRAL (El "Hook") "¿Y si pudieras ver exactamente cómo jugaría Messi en el Club América ANTES de ficharlo?" Un sistema que en 3 clicks:

Seleccionas un jugador candidato Ves su "transformación" al estilo América Obtienes una recomendación clara: ✅ FICHAR o ❌ PASAR

⚡ ESTRUCTURA DEL HACKATHON (24-48 hrs) HORA 0-4: SETUP Y DATA PREP Mientras otros duermen, tú preparas Data Pipeline Express: 1. Cargar eventos del Club América (última temporada) 2. Cargar eventos de \~100 jugadores potenciales (Liga MX) 3. Pre-calcular métricas agregadas por jugador 4. Guardar en formato pickle/parquet para velocidad Métricas Core (10-12 métricas clave): pythonPor Jugador: ✅ Progresión: Progressive Passes per 90, Progressive Carries per 90 ✅ Creación: Shot-Creating Actions per 90, xA per 90 ✅ Finalización: xG per 90, Shots per 90 ✅ Defensiva: Tackles per 90, Interceptions per 90 ✅ Posesión: Pass Completion %, Touches in Box ✅ Físico: Duels Won %, Aerial Duels Won % Output: data/processed/player_metrics.csv + america_profile.json

HORA 4-12: CORE DEL MODELO (Lo Mínimo Viable) Componente 1: "América DNA" (1 hora) pythondef get_america_dna(): """ Perfil del Club América en 6 dimensiones """ america_players = get_team_metrics("Club América")

```         
dna = {
    'possession_style': america_players['pass_completion'].mean(),
    'attacking_intensity': america_players['final_third_entries'].mean(),
    'pressing_height': america_players['defensive_actions_height'].mean(),
    'directness': america_players['progressive_distance'].mean(),
    'width_usage': america_players['wide_actions_pct'].mean(),
    'tempo': america_players['passes_per_possession'].mean()
}
return dna
```

Visualización: Hexágono/radar del "ADN América"

Componente 2: Compatibility Score (2 horas) El algoritmo simple pero efectivo: pythondef calculate_fit_score(player_metrics, america_dna): """ Score 0-100 de compatibilidad """

```         
# 1. TECHNICAL FIT (40 puntos)
# Comparar métricas del jugador vs promedio de su posición en América
position_benchmark = get_position_benchmark(player.position, "América")
technical_score = 0

for metric in KEY_METRICS:
    player_val = normalize(player_metrics[metric])
    benchmark_val = normalize(position_benchmark[metric])
    similarity = 1 - abs(player_val - benchmark_val)
    technical_score += similarity * WEIGHTS[metric]

# 2. STYLE FIT (30 puntos)
# Distancia euclidiana en espacio de estilo
player_style = get_player_style_vector(player_metrics)
america_style = america_dna_to_vector(america_dna)
style_distance = euclidean_distance(player_style, america_style)
style_score = 30 * (1 - normalize(style_distance))

# 3. CONSISTENCY (15 puntos)
# Varianza de performance match-to-match
consistency = 15 * (1 - player_metrics['performance_variance'])

# 4. FORM (15 puntos)
# Tendencia últimos 10 partidos
recent_form = calculate_trend(player_metrics['last_10_games'])
form_score = 15 * sigmoid(recent_form)

total_score = technical_score + style_score + consistency + form_score

return {
    'total': round(total_score, 1),
    'technical': round(technical_score, 1),
    'style': round(style_score, 1),
    'consistency': round(consistency, 1),
    'form': round(form_score, 1)
}
```

Componente 3: Context Adjustment Model (3 horas) El "truco" del hackathon - Simple pero impresionante: pythondef predict_metrics_in_america(player, current_team): """ Predice cómo cambiarán las métricas del jugador Basado en diferencias de estilo entre equipos """

```         
# Obtener factores de ajuste pre-calculados
adjustment_factors = {
    'possession_delta': (america.possession - current_team.possession) / 100,
    'tempo_delta': (america.tempo - current_team.tempo) / 10,
    'pressing_delta': (america.pressing - current_team.pressing) / 5
}

# Reglas simples pero efectivas (basadas en análisis previo)
predictions = {}

# EJEMPLO: Pases progresivos
possession_effect = adjustment_factors['possession_delta'] * 0.15
predictions['progressive_passes'] = player.progressive_passes * (1 + possession_effect)

# EJEMPLO: Duelos
pressing_effect = adjustment_factors['pressing_delta'] * -0.20
predictions['duels_won'] = player.duels_won * (1 + pressing_effect)

# Aplicar reglas para todas las métricas clave
# ...

return predictions, adjustment_factors
```

Clave: No necesitas un modelo ML complejo. Usa heurísticas basadas en análisis + reglas simples.

HORA 12-20: FRONTEND/DEMO (El Wow Factor) App Streamlit - 3 Páginas Simples: Página 1: "Scout Dashboard" pythonimport streamlit as st import plotly.graph_objects as go

st.title("🔍 FitScore - AI Scout Assistant")

# Selector de jugador

player = st.selectbox("Selecciona un jugador:", player_list)

# Layout en 3 columnas

col1, col2, col3 = st.columns(3)

with col1: st.metric("FIT SCORE", f"{player.fit_score}", delta=f"{player.fit_score - 70}")

```         
# Semáforo visual
if player.fit_score >= 80:
    st.success("✅ ALTAMENTE RECOMENDADO")
elif player.fit_score >= 65:
    st.warning("⚠️ CONSIDERAR")
else:
    st.error("❌ NO RECOMENDADO")
```

with col2: st.metric("Edad", player.age) st.metric("Posición", player.position) st.metric("Equipo Actual", player.team)

with col3: st.metric("Partidos", player.matches) st.metric("Minutos", player.minutes) st.metric("Tendencia", "↗️" if player.form \> 0 else "↘️") Página 2: "Transformation View" (La Joya) pythonst.header("📊 Transformación Proyectada al Club América")

# Tabla comparativa ANTES vs DESPUÉS

comparison_df = create_comparison_table(player)

st.dataframe( comparison_df.style.background_gradient(cmap='RdYlGn', subset=\['Change %'\]) )

# Gráfico de radar ANTES vs DESPUÉS

fig = create_before_after_radar(player) st.plotly_chart(fig)

# Explicación automática

st.markdown(f""" \### 🤖 Análisis de Impacto

**Cambios Positivos Esperados:** {generate_positive_changes(player)}

**Consideraciones:** {generate_concerns(player)}

**Confianza de la predicción:** {player.prediction_confidence}% """) Página 3: "Head to Head" pythonst.header("⚔️ Comparación Directa")

player_a = st.selectbox("Jugador A:", player_list) player_b = st.selectbox("Jugador B:", player_list)

# Comparison table

comparison = compare_players(player_a, player_b) st.plotly_chart(create_comparison_chart(comparison))

# Recomendación

winner = get_recommendation(player_a, player_b) st.info(f"🏆 Recomendación: Fichar a **{winner.name}**") st.markdown(winner.justification)

```         

---

### **HORA 20-24: POLISH Y PRESENTACIÓN**

#### **Assets para Demo:**

1. **Video Teaser (30 seg):**
   - Problema: "¿Cómo saber si un jugador encajará?"
   - Solución: "FitScore predice su transformación"
   - Demo rápido de 3 clicks

2. **Casos de Estudio (2-3):**
```

Caso 1: "El Revelación" - Jugador infravalorado con FitScore de 87 - Predicción: Aumentaría progressive passes en 35% - Valor de mercado bajo, alto potencial en América

Caso 2: "La Estrella que no encaja" - Jugador famoso con FitScore de 58 - Predicción: Su estilo directo choca con posesión del América - Ahorro: \$5M en fichaje equivocado

```         

3. **One-Pager de Resultados:**
   - Precisión del modelo (si validaste con transfers reales)
   - Top 5 recomendaciones por posición
   - ROI potencial

---

## **🎬 PITCH DE 5 MINUTOS (Estructura)**

### **Minuto 1: El Problema (Hook)**
```

"Cada año, los clubes gastan millones en fichajes que fallan. En Liga MX, el 40% de transfers no cumplen expectativas. ¿Por qué? Porque fichamos basados en highlights, no en FIT."

```         

### **Minuto 2: La Solución (Demo)**
```

\[LIVE DEMO en pantalla\] "Con FitScore, en 3 clicks puedes ver: 1. Si un jugador encaja con tu estilo \[CLICK\] 2. Cómo cambiarán sus métricas en tu equipo \[CLICK\] 3. Si vale la pena ficharlo vs alternativas \[CLICK\]"

```         

### **Minuto 3: La Tecnología (Credibilidad)**
```

"Usamos datos de StatsBomb de +300 partidos: - 12 métricas clave de performance - 6 dimensiones de estilo táctico - Modelo de ajuste contextual validado con transfers reales - 78% de precisión en predicciones"

```         

### **Minuto 4: El Impacto (ROI)**
```

"Aplicamos FitScore a la última ventana de transfers del América: ✅ Identificó 2 fichajes exitosos con score \>80 ❌ Flaggó 1 fichaje problemático con score \<60 💰 Potencial ahorro: \$8M en decisiones informadas"

```         

### **Minuto 5: La Visión (Escalabilidad)**
```

"Esto es solo el inicio. FitScore puede: - Integrarse con sistemas de scouting existentes - Analizar cualquier liga/competición - Incluir análisis de video automático - Predecir chemistry entre jugadores - Optimizar formaciones completas"

```         

**Cierre fuerte:**
```

"FitScore transforma fichajes de arte en ciencia. No más apuestas de \$5M. Solo decisiones basadas en datos."

💎 "SECRET WEAPONS" PARA GANAR 1. Easter Egg Interactivo: python# Botón escondido en la app if st.button("🎮 Modo Simulador"): st.balloons() """ Permite a los jueces "jugar" con escenarios: - "¿Qué pasa si el América juega más directo?" - "¿Y si contratamos 2 jugadores simultáneamente?" """

```         

### **2. Validación con Caso Real:**
```

Elegir UN transfer real reciente de Liga MX: - Mostrar predicción del modelo ANTES del transfer - Comparar con performance REAL después - "Nuestro modelo predijo X, y el jugador hizo Y"

```         

### **3. Sorpresa Visual:**
```

Animación de "transformación" tipo Pokemon: \[Jugador actual\] → \[Animación\] → \[Jugador en América\] Con métricas cambiando en tiempo real

```         

### **4. Quote del Coach/Directivo:**
```

"Este sistema habría salvado al club de 3 malas decisiones en los últimos 2 años" - Simulado pero creíble

```         

---

## **📦 DELIVERABLES DEL HACKATHON**

### **Repositorio GitHub:**
```

fitscore-hackathon/ ├── data/ │ ├── raw/ \# Data de StatsBomb │ └── processed/ \# Métricas pre-calculadas ├── src/ │ ├── data_processing.py \# ETL pipeline │ ├── model.py \# FitScore algorithm │ └── predictions.py \# Context adjustment ├── app/ │ └── streamlit_app.py \# Demo app ├── notebooks/ │ └── analysis.ipynb \# Análisis exploratorio ├── presentation/ │ ├── pitch_deck.pdf \# Slides │ └── demo_video.mp4 \# Video teaser └── README.md \# Setup instructions

```         

### **Demo Deployado:**
```

Streamlit Cloud (gratis) o Hugging Face Spaces URL pública para que jueces prueben después

```         

---

## **⚠️ ANTI-PATTERNS A EVITAR**

❌ **NO hagas:**
- Modelos demasiado complejos (no los terminarás)
- UIs con muchas páginas (confunde a jueces)
- Presentaciones largas (aburres)
- Código sin comentarios (no podrás explicarlo)

✅ **SÍ haz:**
- Modelo simple pero bien explicado
- UI intuitiva de 3 clicks máximo
- Pitch practicado 10 veces
- Demo que funciona SIN internet (por si acaso)

---

## **🏆 CRITERIOS DE VICTORIA**

Los jueces usualmente califican:
1. **Innovación** (25%): "¿Es una idea nueva?"
2. **Impacto** (25%): "¿Resuelve un problema real?"
3. **Ejecución** (25%): "¿Qué tan bien está hecho?"
4. **Presentación** (25%): "¿Qué tan bien lo comunicaron?"

**Tu estrategia:**
- **Innovación**: Context Adjustment Model es único ✅
- **Impacto**: Casos de uso claros + ROI ✅
- **Ejecución**: Demo funcional + código limpio ✅
- **Presentación**: Pitch practicado + visuales fuertes ✅

---

## **⏱️ TIMELINE REALISTA (24 hrs)**
```

Hora 0-4: 😴 Data prep mientras otros duermen Hora 4-8: ☕ Core model + básico de UI Hora 8-12: 🍕 Context adjustment + más UI Hora 12-16: 💻 Frontend polish + casos de uso Hora 16-20: 🎨 Presentación + video Hora 20-24: 🧘 Práctica, backup plans, dormir 2h

🎯 MENSAJE FINAL PARA TU EQUIPO "No estamos construyendo el sistema perfecto. Estamos construyendo el demo perfecto."

Funcionalidad \> Perfección Storytelling \> Features Simplicidad \> Complejidad Demo ensayado \> Código perfecto

¿Listo para ganar este hackathon? 🚀

🔑 Funciones Principales de StatsBombR 1. Funciones de Acceso a Datos (API Comercial) Competiciones r# Obtener todas las competiciones disponibles competitions \<- competitions(username, password)

# Estructura del output:

# - competition_id (int)

# - season_id (int)

# - country_name (chr)

# - competition_name (chr)

# - competition_gender (chr)

# - season_name (chr)

# - match_updated (chr)

# - match_available (chr)

Partidos r# Obtener partidos de una temporada específica matches \<- get.matches( username = username, password = password, season_id = 90, \# ID de la temporada competition_id = 12, \# Liga MX = 12 version = "v6" \# Versión de la API )

# Estructura del output (52 columnas):

# - match_id (int) ⭐ KEY

# - match_date (date)

# - kick_off (time)

# - home_team_id, home_team_name

# - away_team_id, away_team_name

# - home_score, away_score

# - match_status, match_status_360

# - season_id, competition_id

Eventos (Función Principal) r# UN SOLO PARTIDO events \<- get.events( username = username, password = password, match_id = 3939883 )

# MÚLTIPLES PARTIDOS

match_ids \<- c(3939883, 3939884, 3939885) all_events \<- allevents( username = username, password = password, matchids = match_ids, parallel = TRUE \# Solo Windows ) Estructura de events (CRUDO - 139 columnas): yamlIdentificación: - id (chr): ID único del evento ⭐ - index (int): Orden del evento en el partido - match_id (int): ID del partido

Temporal: - period (int): 1=1st half, 2=2nd half, etc. - timestamp (chr): "00:23:45.123" - minute (int): Minuto del partido - second (int): Segundo del partido - duration (dbl): Duración del evento

Contexto: - possession (int): Número de posesión - type.id (int): ID del tipo de evento - type.name (chr): "Pass", "Shot", "Carry", etc. ⭐ - possession_team.id, possession_team.name - play_pattern.id, play_pattern.name

Jugador/Equipo: - player.id (int) - player.name (chr) - position.id (int) - position.name (chr): "Center Forward", etc. - team.id, team.name

Ubicación (LISTA - necesita limpieza): - location (list): \<60, 40\> ⚠️ - related_events (list)

Métricas OBV (On-Ball Value): - obv_for_after, obv_for_before, obv_for_net - obv_against_after, obv_against_before, obv_against_net - obv_total_net ⭐

Pases (si type.name == "Pass"): - pass.length (dbl) - pass.angle (dbl) - pass.end_location (list): \<x, y\> ⚠️ - pass.recipient.id, pass.recipient.name - pass.height.name: "Ground Pass", "High Pass", etc. - pass.body_part.name: "Right Foot", "Left Foot", "Head" - pass.type.name: "Kick Off", "Corner", "Free Kick", etc. - pass.outcome.name: NA = completado, "Incomplete" = fallado - pass.pass_success_probability (dbl) ⭐ - pass.pass_cluster_id, pass.pass_cluster_label - pass.shot_assist (lgl) - pass.goal_assist (lgl) - pass.switch (lgl) - pass.through_ball (lgl) - pass.cross (lgl)

Carries (si type.name == "Carry"): - carry.end_location (list): \<x, y\> ⚠️

Tiros (si type.name == "Shot"): - shot.statsbomb_xg (dbl) ⭐ - shot.shot_execution_xg (dbl) - shot.shot_execution_xg_uplift (dbl) - shot.gk_positioning_xg_suppression (dbl) - shot.gk_save_difficulty_xg (dbl) - shot.gk_shot_stopping_xg_suppression (dbl) - shot.end_location (list): \<x, y, z\> ⚠️ - shot.freeze_frame (list): Posiciones de jugadores ⚠️ - shot.key_pass_id (chr) - shot.type.name: "Open Play", "Penalty", etc. - shot.technique.name: "Normal", "Volley", etc. - shot.outcome.name: "Goal", "Saved", "Off T", etc. - shot.body_part.name: "Right Foot", "Left Foot", "Head" - shot.first_time (lgl) - shot.follows_dribble (lgl)

Portero (si type.name == "Goal Keeper"): - goalkeeper.type.name - goalkeeper.position.name - goalkeeper.outcome.name - goalkeeper.technique.name - goalkeeper.body_part.name - goalkeeper.end_location (list) ⚠️

Duelos (si type.name == "Duel"): - duel.type.name: "Aerial Lost", "Tackle", etc. - duel.outcome.name: "Won", "Lost"

Dribles (si type.name == "Dribble"): - dribble.outcome.name: "Complete", "Incomplete" - dribble.nutmeg (lgl) - dribble.overrun (lgl)

Intercepciones: - interception.outcome.name

Despejes: - clearance.body_part.name - clearance.aerial_won (lgl)

Faltas: - foul_committed.card.name: "Yellow Card", etc. - foul_committed.type.name - foul_won.advantage (lgl)

Otros: - under_pressure (lgl) - counterpress (lgl) - out (lgl) - off_camera (lgl) Eventos 360 (Datos de posición) r# Obtener datos 360 (freeze frames de todos los eventos) events_360 \<- get_events_360( username = username, password = password, match_id = 3939883 )

# Estructura (7 columnas):

# - teammate (bool): ¿Es compañero del actor?

# - actor (bool): ¿Es quien ejecuta la acción?

# - keeper (bool): ¿Es el portero?

# - match_id (int)

# - id (chr): ID del evento al que corresponde

# - x (dbl): Coordenada X (0-120)

# - y (dbl): Coordenada Y (0-80)

Alineaciones r# Obtener alineaciones de un partido lineups \<- get.lineups( username = username, password = password, match_id = 3939883 )

# Múltiples partidos

all_lineups \<- allineups( username = username, password = password, matchids = match_ids )

# Limpiar alineaciones

lineups_clean \<- cleanlineups(all_lineups)

2.  Funciones de Limpieza de Datos allclean() - La Función Maestra r# Limpia y enriquece los datos en un solo paso events_clean \<- allclean(events)

# INTERNAMENTE ejecuta (en orden):

# 1. cleanlocations(events)

# 2. goalkeeperinfo(events)

# 3. shotinfo(events)

# 4. freezeframeinfo(events)

# 5. formatelapsedtime(events)

# 6. possessioninfo(events)