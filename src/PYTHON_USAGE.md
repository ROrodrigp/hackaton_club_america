# 🐍 Usando los Datos en Python

Los datos están guardados en formato Parquet, lo que los hace totalmente compatibles con Python. Aquí tienes una guía rápida.

## 📦 Instalación de Dependencias

```bash
pip install pandas pyarrow
```

## 📖 Carga Básica de Datos

```python
import pandas as pd
import json

# Cargar datos
events = pd.read_parquet("data/processed/america_events_2024_2025.parquet")
matches = pd.read_csv("data/processed/america_matches_2024_2025.csv")
lineups = pd.read_parquet("data/processed/america_lineups_2024_2025.parquet")

print(f"Events: {len(events):,} rows")
print(f"Matches: {len(matches):,} rows")
print(f"Lineups: {len(lineups):,} rows")
```

## 🔧 Manejo de Columnas JSON

Las columnas que en R eran listas (como `location`, `pass.end_location`, `shot.freeze_frame`) se guardan como **JSON strings** en Parquet. Necesitas parsearlas:

### Ejemplo 1: Extraer coordenadas de location

```python
# Ver datos raw
print(events['location'].head())
# Output: ['[60.5, 40.2]', '[65.3, 38.1]', ...]

# Parsear JSON a listas
events['location_parsed'] = events['location'].apply(
    lambda x: json.loads(x) if pd.notna(x) else None
)

# Extraer X, Y
events['location_x'] = events['location_parsed'].apply(
    lambda x: x[0] if x else None
)
events['location_y'] = events['location_parsed'].apply(
    lambda x: x[1] if x else None
)

# Ver resultado
print(events[['location', 'location_x', 'location_y']].head())
```

### Ejemplo 2: Coordenadas de fin de pase

```python
# Solo para eventos de tipo "Pass"
passes = events[events['type.name'] == 'Pass'].copy()

# Parsear end_location
passes['pass_end_parsed'] = passes['pass.end_location'].apply(
    lambda x: json.loads(x) if pd.notna(x) else None
)

passes['pass_end_x'] = passes['pass_end_parsed'].apply(
    lambda x: x[0] if x else None
)
passes['pass_end_y'] = passes['pass_end_parsed'].apply(
    lambda x: x[1] if x else None
)

# Calcular distancia del pase
import numpy as np

passes['pass_distance'] = np.sqrt(
    (passes['pass_end_x'] - passes['location_x'])**2 +
    (passes['pass_end_y'] - passes['location_y'])**2
)

print(passes[['player.name', 'pass_distance']].head(10))
```

### Ejemplo 3: Freeze frames (datos 360)

```python
# Solo tiros con freeze frame
shots = events[events['type.name'] == 'Shot'].copy()

# Parsear freeze_frame
shots['freeze_frame_parsed'] = shots['shot.freeze_frame'].apply(
    lambda x: json.loads(x) if pd.notna(x) else None
)

# Ver posiciones de jugadores en un tiro
sample_shot = shots.iloc[0]
freeze_frame = sample_shot['freeze_frame_parsed']

if freeze_frame:
    print(f"Jugadores en el momento del tiro: {len(freeze_frame)}")
    for player in freeze_frame[:3]:  # Mostrar 3 primeros
        print(f"  - Posición: ({player['location'][0]}, {player['location'][1]})")
        print(f"    Teammate: {player.get('teammate', 'N/A')}")
```

## 📊 Función Helper para Limpiar Eventos

```python
def clean_events(events_df):
    """
    Limpia y enriquece el dataframe de eventos para análisis en Python
    """
    df = events_df.copy()

    # 1. Parsear location
    df['location_parsed'] = df['location'].apply(
        lambda x: json.loads(x) if pd.notna(x) and x != 'null' else None
    )
    df['location_x'] = df['location_parsed'].apply(lambda x: x[0] if x else None)
    df['location_y'] = df['location_parsed'].apply(lambda x: x[1] if x else None)

    # 2. Parsear pass.end_location (solo pases)
    if 'pass.end_location' in df.columns:
        df['pass_end_parsed'] = df['pass.end_location'].apply(
            lambda x: json.loads(x) if pd.notna(x) and x != 'null' else None
        )
        df['pass_end_x'] = df['pass_end_parsed'].apply(lambda x: x[0] if x else None)
        df['pass_end_y'] = df['pass_end_parsed'].apply(lambda x: x[1] if x else None)

    # 3. Parsear shot.end_location (solo tiros)
    if 'shot.end_location' in df.columns:
        df['shot_end_parsed'] = df['shot.end_location'].apply(
            lambda x: json.loads(x) if pd.notna(x) and x != 'null' else None
        )
        df['shot_end_x'] = df['shot_end_parsed'].apply(lambda x: x[0] if x and len(x) > 0 else None)
        df['shot_end_y'] = df['shot_end_parsed'].apply(lambda x: x[1] if x and len(x) > 1 else None)
        df['shot_end_z'] = df['shot_end_parsed'].apply(lambda x: x[2] if x and len(x) > 2 else None)

    # 4. Crear timestamp completo
    df['timestamp_seconds'] = df['minute'] * 60 + df['second']

    return df

# Usar la función
events_clean = clean_events(events)
print(events_clean[['player.name', 'location_x', 'location_y']].head())
```

## 🎯 Ejemplos de Análisis

### Top 10 pasadores del América

```python
# Filtrar solo América
america_events = events_clean[events_clean['team.name'].str.contains('América', na=False)]

# Contar pases por jugador
passes_by_player = america_events[
    america_events['type.name'] == 'Pass'
].groupby('player.name').size().sort_values(ascending=False)

print("Top 10 Pasadores:")
print(passes_by_player.head(10))
```

### xG total por jugador

```python
# Tiros del América
america_shots = america_events[
    (america_events['type.name'] == 'Shot') &
    (america_events['shot.statsbomb_xg'].notna())
]

xg_by_player = america_shots.groupby('player.name')['shot.statsbomb_xg'].agg(['sum', 'count'])
xg_by_player.columns = ['Total_xG', 'Shots']
xg_by_player = xg_by_player.sort_values('Total_xG', ascending=False)

print("Top 10 por xG:")
print(xg_by_player.head(10))
```

### Mapa de calor de toques

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Filtrar jugador específico
player_name = "Henry Martín"  # Cambia por el jugador que quieras
player_events = america_events[
    (america_events['player.name'] == player_name) &
    (america_events['location_x'].notna())
]

# Crear heatmap
plt.figure(figsize=(12, 8))
plt.hexbin(player_events['location_x'],
           player_events['location_y'],
           gridsize=15,
           cmap='YlOrRd')
plt.colorbar(label='Número de acciones')
plt.xlim(0, 120)
plt.ylim(0, 80)
plt.title(f'Mapa de Calor - {player_name}')
plt.xlabel('Campo (X)')
plt.ylabel('Campo (Y)')
plt.show()
```

## 🔗 Integración con tu Pipeline

```python
# 1. Cargar datos
events = pd.read_parquet("data/processed/america_events_2024_2025.parquet")

# 2. Limpiar
events_clean = clean_events(events)

# 3. Calcular métricas por jugador
# (Esto lo harás en el siguiente script del pipeline)

# 4. Guardar resultados
player_metrics = calculate_player_metrics(events_clean)
player_metrics.to_parquet("data/processed/player_metrics_2024_2025.parquet")
```

## 📝 Notas Importantes

1. **JSON Parsing**: Siempre verifica que el valor no sea `None` o `'null'` antes de parsear
2. **Performance**: Para datasets grandes, considera usar `apply()` con `raw=True` o vectorización
3. **Tipos de datos**: Algunas columnas pueden venir como strings, convierte según necesites
4. **Valores faltantes**: StatsBomb usa `None`/`NaN` para valores no disponibles

## 🚀 Siguiente Paso

Una vez que domines la carga de datos en Python, puedes crear el script de métricas:

```python
# src/02_calculate_player_metrics.py
import pandas as pd
from helpers import clean_events, calculate_metrics

events = pd.read_parquet("data/processed/america_events_2024_2025.parquet")
events_clean = clean_events(events)

# Calcular métricas...
```

¿Listo para analizar? 🦅⚽
