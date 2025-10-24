# src/ - Pipeline de Datos para FitScore

Scripts R para obtener, procesar y analizar datos del Club América y calcular FitScore de jugadores.

---

## 📋 Pipeline Completo

### 1. `01_initial_edar.R` ⭐ START HERE
**Propósito**: Descarga datos del Club América (temporada 2024/2025)

**Inputs**:
- Credenciales StatsBomb (`.statsbomb_credentials`)
- Liga MX Apertura 2024/2025

**Outputs**:
```
data/teams/America/
├── matches_2024_2025.csv
├── lineups_2024_2025.parquet
├── events_2024_2025.parquet
└── minutes_played_2024_2025.parquet
```

**Ejecución**:
```bash
Rscript src/01_initial_edar.R
```

**Tiempo**: ~5-10 minutos

---

### 2a. `02a_calculate_team_aggregates.R`
**Propósito**: Calcular métricas agregadas de equipos y crear benchmarks P90

**Inputs**:
- Datos de 19 equipos en `data/teams/`
- Cada equipo debe tener: `events.parquet`, `lineups.parquet`, `minutes_played.parquet`

**Outputs**:
```
data/processed/
├── america_dna_profile.json      # DNA táctico del América
└── liga_mx_benchmarks_p90.json   # Percentil 90 de 19 equipos
```

**Métricas calculadas**:
- Progressive passes, carries
- xA, key passes, shot assists
- xG, shots, goals
- Tackles, interceptions, pressures
- Pass completion %, touches
- Dribbles successful

**Ejecución**:
```bash
Rscript src/02a_calculate_team_aggregates.R
```

**Tiempo**: ~3-5 minutos

---

### 2b. `02b_calculate_scouting_pool.R`
**Propósito**: Calcular métricas individuales de jugadores de los 18 equipos de scouting

**Inputs**:
- Datos de 18 equipos en `data/teams/` (excluye América)

**Outputs**:
```
data/processed/
└── scouting_pool_all_metrics.csv  # Métricas de todos los jugadores (18 equipos)
```

**Filtros aplicados**:
- Mínimo 270 minutos jugados
- Excluye porteros
- Solo jugadores con posición primaria definida

**Métricas per 90** (p90):
- progressive_passes_p90, progressive_carries_p90
- xA_p90, key_passes_p90, shot_assists_p90
- xG_p90, shots_p90, goals_p90
- tackles_p90, interceptions_p90, pressures_p90
- pass_completion_pct, touches_att_third_p90
- dribbles_successful_p90, dribbles_p90

**Ejecución**:
```bash
Rscript src/02b_calculate_scouting_pool.R
```

**Tiempo**: ~5-8 minutos

---

### 3. `03_define_america_dna.R`
**Propósito**: Definir DNA táctico del Club América en 6 dimensiones

**Inputs**:
- `data/processed/america_dna_profile.json` (creado por 02a)
- `data/processed/liga_mx_benchmarks_p90.json` (creado por 02a)

**Outputs**:
- Actualiza `america_dna_profile.json` con:
  - Scores por dimensión (0-100)
  - Overall DNA score
  - Tactical identity
  - Strengths y weaknesses

**6 Dimensiones**:
1. **Progression** (pases/carries progresivos)
2. **Creation** (xA, pases clave)
3. **Finishing** (xG, tiros, goles)
4. **Pressing** (presiones p90)
5. **Possession** (% pases, toques)
6. **Dribbling** (regates exitosos)

**Cálculo de Score**:
```r
Score = (Métrica del América / Benchmark P90) × 100
```

**Ejecución**:
```bash
Rscript src/03_define_america_dna.R
```

**Tiempo**: < 1 minuto

---

### 4. `04_calculate_fit_score.R` ✅ FINAL STEP
**Propósito**: Calcular FitScore para cada jugador del pool de scouting

**Inputs**:
- `data/processed/america_dna_profile.json`
- `data/processed/scouting_pool_all_metrics.csv`
- `data/processed/liga_mx_benchmarks_p90.json`

**Outputs**:
```
data/processed/
├── player_fit_scores.json         # FitScores detallados
├── top_recommendations.csv        # Top 20 jugadores
└── worst_recommendations.csv      # Worst 20 jugadores
```

**Algoritmo FitScore**:
```
FitScore = (60% × DNA Match) + (30% × Gap Filling) + (10% × Role Fit)
```

Componentes:
1. **DNA Match**: Similitud coseno entre DNA del jugador y América
2. **Gap Filling**: Cuánto fortalece áreas débiles del equipo
3. **Role Fit**: Compatibilidad posicional

**Ejecución**:
```bash
Rscript src/04_calculate_fit_score.R
```

**Tiempo**: ~2-3 minutos

---

## 🚀 Ejecución Completa del Pipeline

```bash
# Paso 1: Descargar datos de América
Rscript src/01_initial_edar.R

# Paso 2a: Calcular agregados de equipos y benchmarks
Rscript src/02a_calculate_team_aggregates.R

# Paso 2b: Calcular métricas del scouting pool
Rscript src/02b_calculate_scouting_pool.R

# Paso 3: Definir DNA del América
Rscript src/03_define_america_dna.R

# Paso 4: Calcular FitScore
Rscript src/04_calculate_fit_score.R
```

**Tiempo total**: ~20-30 minutos

---

## 📦 Dependencias R

```r
# Instalar paquetes necesarios
install.packages(c(
  "tidyverse",    # Manipulación de datos
  "arrow",        # Formato Parquet
  "jsonlite",     # JSON I/O
  "lubridate"     # Fechas
))

# StatsBombR (desde GitHub)
devtools::install_github("statsbomb/StatsBombR")
```

---

## 🔐 Configuración de Credenciales

Antes de ejecutar, configurar credenciales de StatsBomb:

```bash
# 1. Copiar archivo de ejemplo
cp .statsbomb_credentials.example .statsbomb_credentials

# 2. Editar con credenciales reales
# Formato:
# username=tu_usuario@email.com
# password=tu_password
```

⚠️ **Este archivo está en `.gitignore` y NUNCA se commitea.**

---

## 📊 Flujo de Datos

```
StatsBomb API
     ↓
01_initial_edar.R → data/teams/America/
     ↓
02a_calculate_team_aggregates.R → america_dna_profile.json
                                 → liga_mx_benchmarks_p90.json
     ↓
02b_calculate_scouting_pool.R → scouting_pool_all_metrics.csv
     ↓
03_define_america_dna.R → america_dna_profile.json (actualizado)
     ↓
04_calculate_fit_score.R → player_fit_scores.json
                         → top_recommendations.csv
                         → worst_recommendations.csv
     ↓
Streamlit App (app/)
```

---

## 🛠️ Troubleshooting

### Error de autenticación StatsBomb
- Verifica que `.statsbomb_credentials` existe
- Confirma username y password correctos
- Sin espacios extra en el archivo

### Parquet no se puede leer
- Instala `arrow`: `install.packages("arrow")`
- Verifica versión compatible de R (>= 4.0)

### Métricas faltantes
- Asegúrate de que todos los equipos tienen datos completos
- Verifica filtro de minutos mínimos (270)
- Revisa exclusión de porteros

### Script se detiene
- Revisa que existan todos los inputs requeridos
- Verifica que los directorios `data/teams/` existen
- Checa permisos de escritura en `data/processed/`

---

## 📝 Notas

- Los scripts usan **Parquet** para eficiencia (compatible con Python)
- Todas las métricas están **normalizadas per 90 minutos**
- **Mínimo 270 minutos** para métricas confiables
- **Porteros excluidos** del análisis de FitScore
- Los benchmarks P90 representan el **nivel elite** de Liga MX

---

Para más información, ver el [README principal](../README.md) del proyecto.
