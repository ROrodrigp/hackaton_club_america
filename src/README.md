# src/ - Pipeline de Datos para FitScore

Este directorio contiene los scripts R para obtener, procesar y analizar los datos del Club América.

## 📋 Pipeline Order

### 1. `01_fetch_america_dna_data.R` ⭐ START HERE
**Propósito**: Descarga TODOS los datos necesarios para el análisis del Club América (temporada 2024/2025 únicamente)

**Output**:
```
data/processed/
├── america_matches_2024_2025.csv                    # Partidos del América
├── america_events_2024_2025.parquet                 # TODOS los eventos (limpiados) ⭐
├── america_events_2024_2025_sample.csv              # Sample para inspección
├── america_lineups_2024_2025.parquet                # Alineaciones ⭐
├── america_minutes_played_2024_2025.parquet         # Minutos por jugador-partido ⭐ NEW
├── america_player_minutes_summary.parquet           # Minutos totales por jugador ⭐ NEW
└── america_events_360_sample.parquet                # Datos 360 (muestra) ⭐
```

**Formato Parquet**: Compatible con R y Python, comprimido, rápido. ¡Perfecto para análisis multi-lenguaje!

**⚠️ IMPORTANTE**: Este script ahora también calcula los **minutos jugados** usando `get.minutesplayed()` ANTES de guardar a Parquet. Esto es necesario porque la función requiere estructura de datos frescos de StatsBomb y no funciona correctamente después de la conversión a Parquet.

**Tiempo estimado**: 5-10 minutos

**Cómo ejecutar**:
```r
source("src/01_fetch_america_dna_data.R")
```

O desde terminal:
```bash
Rscript src/01_fetch_america_dna_data.R
```

---

### 2. `02_calculate_player_metrics.R` ✅
**Propósito**: Calcular métricas avanzadas por jugador (Progressive Passes, xG, Tackles, etc.)

**Input**:
- `america_events_2024_2025.parquet` (eventos)
- `america_player_minutes_summary.parquet` (minutos pre-calculados) ⭐
- `america_lineups_2024_2025.parquet` (posiciones)

**Output**:
```
data/processed/
├── player_metrics_2024_2025.parquet       # Métricas por jugador (12 métricas clave)
└── team_aggregates_2024_2025.json         # Estadísticas agregadas del equipo
```

**Nota**: Los minutos jugados ya vienen calculados del script 01, evitando problemas con Parquet.

---

### 3. `03_define_america_dna.R` (Por crear)
**Propósito**: Definir el "ADN" del Club América en 6 dimensiones tácticas

**Output**:
```
data/processed/
└── america_dna_profile.json               # Perfil táctico del América
```

---

### 4. `04_fitscore_model.R` (Por crear)
**Propósito**: Modelo de compatibilidad de jugadores con el América

---

## 🎯 Datos Obtenidos

### Eventos (`america_events_2024_2025.parquet`)
Todos los eventos de todos los partidos del América en 2024/2025:
- Pases (con xA, probabilidad de éxito, etc.)
- Tiros (con xG)
- Duelos, intercepciones, tackles
- Carries (conducciones)
- **OBV** (On-Ball Value) - Valor agregado por acción
- **Formato**: Parquet (R + Python compatible)

### Matches (`america_matches_2024_2025.csv`)
Información de cada partido:
- Resultado, goles
- Rival, estadio
- Árbitro
- Estado de datos 360
- **Formato**: CSV (universal)

### Lineups (`america_lineups_2024_2025.parquet`)
Alineaciones de cada partido:
- Jugadores titulares y suplentes
- Posiciones
- Minutos jugados
- **Formato**: Parquet (R + Python compatible)

### 360 Data (`america_events_360_sample.parquet`)
Posiciones de todos los jugadores en cada evento:
- Coordenadas X, Y de cada jugador
- ¿Es compañero/rival/portero?
- Contexto táctico completo
- **Formato**: Parquet (R + Python compatible)

---

## 💡 Carga Rápida de Datos

### En R:
```r
library(arrow)
library(tidyverse)

# Cargar todos los datos procesados
events <- read_parquet("data/processed/america_events_2024_2025.parquet")
matches <- read_csv("data/processed/america_matches_2024_2025.csv")
lineups <- read_parquet("data/processed/america_lineups_2024_2025.parquet")
minutes <- read_parquet("data/processed/america_player_minutes_summary.parquet")

# Ver estructura
glimpse(events)
glimpse(matches)
glimpse(lineups)
glimpse(minutes)
```

### En Python:
```python
import pandas as pd

# Cargar todos los datos procesados
events = pd.read_parquet("data/processed/america_events_2024_2025.parquet")
matches = pd.read_csv("data/processed/america_matches_2024_2025.csv")
lineups = pd.read_parquet("data/processed/america_lineups_2024_2025.parquet")
minutes = pd.read_parquet("data/processed/america_player_minutes_summary.parquet")

# Ver estructura
print(events.info())
print(matches.info())
print(lineups.info())
print(minutes.info())

# Nota: Las columnas que eran listas en R están como JSON strings
# Para usarlas en Python:
import json
events['location_parsed'] = events['location'].apply(lambda x: json.loads(x) if pd.notna(x) else None)
```

---

## 🔑 Columnas Clave en Events

### Identificación
- `match_id`: ID del partido
- `id`: ID único del evento
- `index`: Orden en el partido

### Temporal
- `minute`, `second`: Tiempo del evento
- `ElapsedTime`: Tiempo transcurrido (added by allclean)

### Espacial
- `location.x`, `location.y`: Coordenadas (0-120, 0-80)
- `pass.end_location.x`, `pass.end_location.y`: Fin del pase

### Táctico
- `type.name`: Tipo de evento ("Pass", "Shot", "Carry", etc.)
- `player.name`, `team.name`: Quién y qué equipo
- `position.name`: Posición del jugador
- `under_pressure`: Si estaba presionado

### Métricas Avanzadas
- `obv_total_net`: On-Ball Value (⭐ IMPORTANTE)
- `pass.pass_success_probability`: Dificultad del pase
- `shot.statsbomb_xg`: Expected Goals
- `pass.goal_assist`, `pass.shot_assist`: Asistencias

---

## ⚠️ Notas Importantes

1. **Formato Parquet**: Todos los archivos principales usan Parquet para compatibilidad R/Python. Las columnas tipo lista se convierten a JSON strings.

2. **Minutos Jugados**: Se calculan en el script 01 usando `get.minutesplayed()` ANTES de guardar a Parquet. Esto es crítico porque la función requiere estructura de datos frescos de StatsBomb. El script 02 usa estos minutos pre-calculados.

3. **Datos 360**: Por defecto solo descarga una muestra. Para obtener TODOS los datos 360, descomenta el loop al final del script 01.

4. **Parallel Processing**: En Windows, puedes usar `parallel = TRUE` en `allevents()` y `alllineups()` para acelerar.

5. **Tiempo de ejecución**: La primera vez toma ~10 minutos. Los datos se guardan localmente para reutilización.

6. **Tamaño de archivos** (Parquet comprimido):
   - Events: ~20-40 MB (vs ~50-100 MB en RDS)
   - Lineups: ~1-2 MB
   - Minutes: ~50-100 KB ⭐ NEW
   - 360 data completo: ~200-400 MB (vs ~500 MB - 1 GB en RDS)

7. **Dependencias**: Asegúrate de tener instalado el paquete `arrow`:
   ```r
   install.packages("arrow")
   ```
   En Python:
   ```bash
   pip install pyarrow pandas
   ```

---

## 🚀 Siguiente Paso

Una vez que hayas ejecutado `01_fetch_america_dna_data.R`, continúa con:

```r
source("src/02_calculate_player_metrics.R")
```

¿Listo para comenzar? 🦅
