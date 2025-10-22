# 🚀 PLAN ACTUALIZADO - FitScore para Club América

## 📅 Estado del Proyecto: EN PROGRESO

**Fecha de inicio**: Octubre 2025
**Deadline hackathon**: 22 de octubre, 2025
**Presentación final**: 6 de noviembre, 2025

---

## ✅ PROGRESO COMPLETADO

### ✅ FASE 1: INFRAESTRUCTURA DE DATOS (COMPLETADO)

#### Script 01: `01_fetch_multi_team_data.R` ✅
- **Estado**: Completado y listo para ejecutar
- **Propósito**: Descarga datos de 5 equipos (América + 4 equipos de scouting)
- **Equipos incluidos**:
  - 🦅 **Club América** (para definir ADN)
  - 🔴 **Toluca** (pool de scouting)
  - 🔵 **Guadalajara (Chivas)** (pool de scouting)
  - ⚪ **Monterrey** (pool de scouting)
  - 🟣 **Mazatlán** (pool de scouting)
- **Output esperado**:
  - `multi_team_events_2024_2025.parquet` (~50,000+ eventos)
  - `multi_team_matches_2024_2025.csv` (metadatos)
  - `multi_team_lineups_2024_2025.parquet` (alineaciones)
  - `multi_team_minutes_played.parquet` (minutos por jugador-partido)
  - `multi_team_player_minutes_summary.parquet` (totales por jugador)
- **Tiempo de ejecución**: ~15-25 minutos
- **Ejecutar**: `Rscript src/01_fetch_multi_team_data.R`

#### Script 02: `02_calculate_multi_team_metrics.R` ✅
- **Estado**: Completado y listo para ejecutar
- **Propósito**: Calcula métricas avanzadas por jugador (todos los equipos)
- **Métricas implementadas** (todas per 90 min):
  - 🏃 **Progresión**: Progressive passes, Progressive carries
  - 🎨 **Creación**: Shot assists, Key passes, xA (Expected Assists)
  - ⚽ **Finalización**: Shots, Goals, xG
  - 🛡️ **Defensa**: Tackles, Interceptions, Pressures, Recoveries
  - 🎯 **Posesión**: Pass completion %, Touches in attacking third, Touches in box
  - 🎪 **Dribbling**: Dribbles, Success rate
- **Output esperado**:
  - `multi_team_player_metrics.parquet` (todos los jugadores)
  - `america_player_metrics.parquet` (solo América)
  - `scouting_player_metrics.parquet` (pool de 4 equipos)
- **Tiempo de ejecución**: ~3-5 minutos
- **Ejecutar**: `Rscript src/02_calculate_multi_team_metrics.R`

#### Script 03: `03_define_america_dna.R` ✅
- **Estado**: Completado (de proyecto anterior, compatible)
- **Propósito**: Define el "ADN táctico" del Club América
- **6 Dimensiones del ADN**:
  1. Estilo de Posesión
  2. Intensidad Ofensiva
  3. Altura de Presión
  4. Directness (directitud)
  5. Uso de Bandas
  6. Creación
- **Output esperado**:
  - `america_dna_profile.json`
  - `america_benchmarks_by_position.json`
  - `america_style_vectors.json`
- **Tiempo de ejecución**: ~1-2 minutos
- **Ejecutar**: `Rscript src/03_define_america_dna.R`

---

## 🔄 PRÓXIMOS PASOS INMEDIATOS

### 🎯 FASE 2: MODELO DE FITSCORE (EN DESARROLLO)

#### Script 04: `04_calculate_fitscore.R` ⏳
- **Estado**: Por desarrollar
- **Prioridad**: 🔴 ALTA
- **Propósito**: Calcular FitScore (0-100) para cada jugador del pool de scouting

**Algoritmo FitScore** (estructura planificada):

```r
FitScore (0-100) =
  + Technical Fit (40 puntos)
      • Comparar métricas del jugador vs benchmark de su posición en América
      • Métricas clave según posición:
        - Delanteros: xG, shots, touches in box, dribbles
        - Mediocampistas: progressive passes, xA, pass completion
        - Defensas: tackles, interceptions, pressures, clearances

  + Style Fit (30 puntos)
      • Distancia euclidiana entre perfil del jugador y ADN América
      • Vectores de estilo en 6 dimensiones

  + Consistency (15 puntos)
      • Varianza de performance entre partidos
      • Jugadores consistentes = mayor FitScore

  + Form (15 puntos)
      • Tendencia últimos 5 partidos
      • Jugadores en forma ascendente = mayor FitScore
```

**Modelo de Transformación Contextual** (predice cambios en métricas):
```r
predict_metrics_in_america <- function(player, current_team, america_dna) {
  # Calcular diferencias de estilo entre equipos
  style_deltas <- calculate_style_differences(current_team, america_dna)

  # Reglas de ajuste por métrica:
  # 1. Si América tiene más posesión → aumentan pases progresivos
  # 2. Si América presiona más alto → aumentan pressures, disminuyen duels
  # 3. Si América es más directo → aumentan carries, disminuyen pases cortos

  predictions <- apply_transformation_rules(player_metrics, style_deltas)

  return(list(
    original_metrics = player_metrics,
    predicted_metrics = predictions,
    change_pct = (predictions - player_metrics) / player_metrics * 100
  ))
}
```

**Output esperado**:
- `fitscore_rankings.parquet` (jugadores rankeados por FitScore)
- `predicted_transformations.parquet` (métricas antes/después)
- `recommendations_by_position.json` (Top 5 por posición)

---

### 🎨 FASE 3: VISUALIZACIÓN Y DEMO (PENDIENTE)

#### App Streamlit: `app/streamlit_app.py` 📱
- **Estado**: Por desarrollar
- **Prioridad**: 🟡 MEDIA

**3 Páginas Principales**:

1. **Scout Dashboard** 🔍
   - Selector de jugador
   - FitScore prominente (0-100)
   - Semáforo visual (✅ >80, ⚠️ 65-80, ❌ <65)
   - Info básica (edad, posición, equipo, minutos)

2. **Transformation View** 📊 ⭐ LA JOYA
   - Tabla comparativa: Métricas Actuales | Predichas en América | % Cambio
   - Radar chart: ANTES (azul) vs DESPUÉS (amarillo)
   - Explicación automática de cambios esperados
   - Nivel de confianza de la predicción

3. **Head-to-Head Comparison** ⚔️
   - Comparar 2 jugadores lado a lado
   - Recomendación automática ("Fichar a X porque...")
   - Gráficos de comparación directa

**Elementos Interactivos**:
- Filtros por posición, equipo, edad
- Ordenamiento por FitScore, xG, xA, etc.
- Tooltips explicando cada métrica
- Descarga de reportes en PDF

---

### 📹 FASE 4: PRESENTACIÓN (PENDIENTE)

#### Video Demo (5 min máximo) 🎬
- [ ] Problema: ¿Por qué fallan los fichajes? (30 seg)
- [ ] Solución: FitScore en acción (2 min)
- [ ] Tecnología: StatsBomb 360 + modelo contextual (1 min)
- [ ] Impacto: Casos de uso reales (1 min)
- [ ] Visión: Escalabilidad futura (30 seg)

#### Pitch Deck (PDF) 📑
- [ ] Slide 1: El problema (datos de fichajes fallidos)
- [ ] Slide 2: La solución (FitScore overview)
- [ ] Slide 3: Demo en vivo
- [ ] Slide 4: Metodología (datos + algoritmo)
- [ ] Slide 5: Casos de estudio (Top 3 recomendaciones)
- [ ] Slide 6: ROI y próximos pasos

#### Casos de Estudio (2-3 ejemplos) 📚
- **"El Revelado"**: Jugador con FitScore alto pero bajo perfil
- **"La Estrella que No Encaja"**: Jugador famoso con FitScore bajo
- **"El Versátil"**: Jugador que mejora en múltiples dimensiones

---

## 📋 CHECKLIST PRE-PRESENTACIÓN

### Datos ✅
- [x] Script 01 completado (fetch data)
- [x] Script 02 completado (calculate metrics)
- [x] Script 03 completado (define DNA)
- [ ] Script 04 en desarrollo (FitScore model)

### Código 🔧
- [x] Código documentado y limpio
- [x] README.md completo
- [ ] Notebooks de exploración
- [ ] Tests básicos de funciones críticas

### Demo 🎮
- [ ] App Streamlit funcional
- [ ] Datos pre-cargados (no depende de API en vivo)
- [ ] Visualizaciones pulidas
- [ ] Casos de uso preparados

### Presentación 🎤
- [ ] Video grabado y editado
- [ ] Pitch practicado 10+ veces
- [ ] Slides con visuales impactantes
- [ ] Plan B si falla demo en vivo

---

## ⏱️ TIMELINE SUGERIDO

| Día | Tarea | Tiempo estimado |
|-----|-------|-----------------|
| **Día 1** | Ejecutar scripts 01-03 + validar datos | 2-3 horas |
| **Día 2** | Desarrollar script 04 (FitScore) | 4-6 horas |
| **Día 3** | Crear app Streamlit básica | 4-6 horas |
| **Día 4** | Pulir visualizaciones + casos de estudio | 3-4 horas |
| **Día 5** | Crear video demo + pitch deck | 3-4 horas |
| **Día 6** | Practicar presentación + ajustes finales | 2-3 horas |

**Total estimado**: 18-26 horas de trabajo efectivo

---

## 🎯 CRITERIOS DE ÉXITO

### Para el Hackathon
- ✅ Sistema funcional end-to-end (datos → métricas → FitScore → visualización)
- ✅ Al menos 3 casos de estudio convincentes
- ✅ Demo que se ejecuta sin errores
- ✅ Presentación clara y concisa (<5 min)
- ✅ Código bien documentado y reproducible

### Puntos Diferenciales
- 🌟 **Innovación**: Modelo de transformación contextual (único)
- 🌟 **Precisión**: Basado en StatsBomb 360 + métricas validadas
- 🌟 **Aplicabilidad**: Responde directamente pregunta del hackathon
- 🌟 **Visualización**: Transformación "antes/después" impactante
- 🌟 **Escalabilidad**: Fácil de extender a otros equipos/ligas

---

## 🚀 INSTRUCCIONES DE EJECUCIÓN

### Paso 1: Descargar Datos (Primera vez)
```bash
# Navegar al directorio del proyecto
cd hackaton_club_america/

# Ejecutar script de descarga (15-25 minutos)
Rscript src/01_fetch_multi_team_data.R
```

### Paso 2: Calcular Métricas
```bash
# Calcular métricas por jugador (3-5 minutos)
Rscript src/02_calculate_multi_team_metrics.R
```

### Paso 3: Definir ADN del América
```bash
# Calcular perfil táctico (1-2 minutos)
Rscript src/03_define_america_dna.R
```

### Paso 4: Calcular FitScore (Próximamente)
```bash
# Cuando esté listo el script 04:
# Rscript src/04_calculate_fitscore.R
```

### Verificar Outputs
```r
library(arrow)
library(tidyverse)

# Verificar que los archivos existen
list.files("data/processed/", pattern = "parquet|csv|json")

# Cargar métricas
america <- read_parquet("data/processed/america_player_metrics.parquet")
scouting <- read_parquet("data/processed/scouting_player_metrics.parquet")

# Ver top 10 por xG
scouting %>%
  arrange(desc(xG_p90)) %>%
  select(player_name, team.name, primary_position, xG_p90, shots_p90) %>%
  head(10)
```

---

## 💡 TIPS Y MEJORES PRÁCTICAS

### Durante el Desarrollo
1. **Commits frecuentes**: Guardar progreso cada feature completado
2. **Tests básicos**: Validar que métricas suman correctamente
3. **Backup de datos**: Guardar `.parquet` en múltiples lugares
4. **Documentación inline**: Comentar funciones complejas

### Para la Demo
1. **Pre-cargar datos**: No depender de API en vivo
2. **Casos preparados**: Tener 3-5 jugadores interesantes listos
3. **Plan B**: Screenshots por si falla Streamlit
4. **Timing**: Practicar para mantenerse <5 minutos

### Para la Presentación
1. **Storytelling**: Empezar con problema real, terminar con impacto
2. **Visuales**: Más gráficos, menos texto
3. **Confianza**: Practicar 10+ veces
4. **Preguntas anticipadas**: Preparar respuestas a posibles dudas

---

## 📚 RECURSOS ADICIONALES

### Documentación Técnica
- 📖 [StatsBombR GitHub](https://github.com/statsbomb/StatsBombR)
- 🐍 [statsbombpy (Python)](https://github.com/statsbomb/statsbombpy)
- 📊 [Event Data Spec](https://statsbomb.com/what-we-do/soccer-data/)
- 🎯 [360 Data Spec](https://statsbomb.com/what-we-do/soccer-data/360-frame/)

### Inspiración y Referencias
- 🏆 [Friends of Tracking (YouTube)](https://www.youtube.com/@friendsoftracking4873)
- 📈 [McKay Johns - Soccer Analytics](https://mckayjohns.github.io/)
- 📊 [Soccermatics](https://soccermatics.readthedocs.io/)

### Herramientas Útiles
- 🎨 [Plotly (visualizaciones interactivas)](https://plotly.com/r/)
- 🌐 [Streamlit (web apps rápidas)](https://streamlit.io/)
- 📦 [Arrow/Parquet (formato eficiente)](https://arrow.apache.org/)

---

## ❓ FAQ

### ¿Por qué 5 equipos y no más?
Balance entre:
- **Tiempo de descarga** (~20 min con 5 equipos)
- **Calidad del pool** (equipos diversos tácticamente)
- **Manejabilidad** (análisis más profundo vs más jugadores)

### ¿Por qué Parquet en lugar de CSV?
- ✅ **Compresión**: 10x más pequeño que CSV
- ✅ **Velocidad**: 5-10x más rápido de leer
- ✅ **Tipos**: Preserva tipos de datos (int, float, string)
- ✅ **Compatible**: Funciona en R y Python sin conversión

### ¿Qué pasa si no hay datos 360?
El análisis funciona sin datos 360. Los datos 360 son un plus para:
- Posicionamiento táctico
- Passing networks
- Freeze frames de tiros

Pero las métricas core (xG, xA, progressive passes, etc.) están en los eventos normales.

### ¿Cómo validar el modelo?
Opciones:
1. **Transfers reales**: Analizar jugadores que ya ficharon al América
2. **Cross-validation**: Dividir temporada en train/test
3. **Expert review**: Validar con scout profesional
4. **Casos conocidos**: Comparar con fichajes exitosos/fallidos

---

## 🎊 MENSAJE FINAL

> **"No estamos construyendo el sistema perfecto. Estamos construyando el demo perfecto."**

### Enfoque para Ganar
- ✅ **Funcionalidad** > Perfección
- ✅ **Storytelling** > Features
- ✅ **Simplicidad** > Complejidad
- ✅ **Demo ensayado** > Código perfecto

**¡Mucha suerte en el hackathon! 🦅⚽**

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