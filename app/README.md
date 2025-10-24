# 🦅 Club América - Streamlit Scouting App

Aplicación web interactiva para análisis de DNA táctico y recomendaciones de fichajes basadas en FitScore.

---

## 📋 Descripción

Sistema de visualización interactivo que presenta:
- **DNA táctico del Club América** en 6 dimensiones
- **Recomendaciones de jugadores** (Top 20 / Worst 20) basadas en compatibilidad táctica
- **Búsqueda de jugadores** con análisis detallado de cualquier jugador del pool

---

## 🚀 Instalación

### Requisitos
```bash
pip install streamlit pandas plotly numpy
```

### Ejecutar App
```bash
# Desde el directorio app/
streamlit run streamlit_app.py

# O desde el directorio raíz del proyecto
streamlit run app/streamlit_app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

---

## 📁 Estructura

```
app/
├── streamlit_app.py              # Página principal (Inicio)
├── .streamlit/
│   └── config.toml               # Configuración de tema
├── pages/
│   ├── 1_🧬_DNA_Club_America.py  # Análisis DNA táctico
│   ├── 2_⚽_Player_Recommendations.py  # Top/Worst 20
│   └── 3_🔍_Buscar_Jugador.py    # Búsqueda de jugadores
└── utils/
    ├── data_loader.py            # Funciones de carga de datos
    ├── styling.py                # CSS personalizado y colores
    └── visualizations.py         # Gráficas Plotly (radars, barras)
```

---

## 🎨 Páginas

### 🏠 Inicio (`streamlit_app.py`)
- Overview del sistema FitScore
- Estadísticas del pool de scouting
- Fortalezas y áreas de mejora del Club América
- Metodología y próximos pasos

### 🧬 DNA Club América
- Score global de DNA táctico
- Scores individuales de 6 dimensiones:
  - Progression, Creation, Finishing
  - Pressing, Possession, Dribbling
- Radar charts y gráficas de barras
- Métricas subyacentes por dimensión
- Comparación con benchmarks P90 de Liga MX

### ⚽ Recomendaciones de Jugadores
**Top 20 Tab:**
- Jugadores con mayor FitScore
- Filtros por equipo, posición, FitScore mínimo
- Tabla interactiva ordenable
- Análisis detallado por jugador seleccionado

**Worst 20 Tab:**
- Jugadores con menor FitScore
- Mismos filtros y análisis que Top 20

**Análisis detallado incluye:**
- FitScore breakdown (DNA Match, Gap Filling, Role Fit)
- Radar chart comparativo jugador vs América
- Rankings en el pool de scouting
- Análisis posicional con métricas clave
- Justificación de la recomendación

### 🔍 Buscar Jugador
- Búsqueda de cualquier jugador del pool (18 equipos)
- Filtros por equipo y posición
- Mismo análisis completo que en Recomendaciones
- Ideal para evaluación de jugadores específicos

---

## 🎨 Tema y Estilo

La aplicación usa los colores oficiales del Club América:
- **Azul marino**: #041E42 (primary)
- **Dorado**: #FFC629 (secondary)
- **Blanco**: #FFFFFF (accent)

Configuración en `app/.streamlit/config.toml`

---

## 📊 Datos Requeridos

La app carga los siguientes archivos de `data/processed/`:

| Archivo | Descripción |
|---------|-------------|
| `america_dna_profile.json` | DNA táctico del Club América |
| `liga_mx_benchmarks_p90.json` | Benchmarks P90 de Liga MX |
| `scouting_pool_all_metrics.csv` | Métricas de 18 equipos |
| `top_recommendations.csv` | Top 20 jugadores recomendados |
| `worst_recommendations.csv` | Worst 20 jugadores |
| `player_fit_scores.json` | FitScores detallados de todos los jugadores |

Estos archivos son generados por los scripts R en `src/`.

---

## 🛠️ Desarrollo

### Agregar Nueva Página

1. Crear archivo en `app/pages/` con formato: `N_emoji_Nombre.py`
2. Configurar página:
```python
import streamlit as st

st.set_page_config(
    page_title="Tu Título",
    page_icon="🔥",
    layout="wide"
)

# Aplicar CSS personalizado
from utils.styling import get_custom_css
st.markdown(get_custom_css(), unsafe_allow_html=True)
```

### Usar Utilidades

```python
# Cargar datos
from utils.data_loader import load_america_dna, load_scouting_pool

dna_data = load_america_dna()
pool = load_scouting_pool()

# Crear visualizaciones
from utils.visualizations import create_radar_chart, create_comparison_radar

fig = create_radar_chart(dna_data['dimensions'])
st.plotly_chart(fig, use_container_width=True)

# Usar colores del Club América
from utils.styling import CLUB_AMERICA_COLORS

st.markdown(f"<h1 style='color: {CLUB_AMERICA_COLORS['primary']}'>Título</h1>",
            unsafe_allow_html=True)
```

---

## 🎯 Características Clave

- ✅ **Diseño responsivo** con layout wide
- ✅ **Tema personalizado** con colores del Club América
- ✅ **Visualizaciones interactivas** con Plotly
- ✅ **Filtros dinámicos** por equipo, posición, FitScore
- ✅ **Navegación multi-página** con menú lateral
- ✅ **Carga eficiente** de datos con caché
- ✅ **CSS personalizado** para componentes consistentes

---

## 📝 Notas

- La app asume que todos los archivos de datos están en `../data/processed/` relativo a `app/`
- Los gráficos usan colores consistentes del Club América
- Las métricas están pre-calculadas para rendimiento óptimo
- Los filtros son reactivos y actualizan instantáneamente

---

## 🐛 Troubleshooting

### Error: "File not found"
- Verifica que los archivos en `data/processed/` existen
- Ejecuta el pipeline de datos R primero (`src/`)

### Gráficas no se ven
- Verifica que `plotly` está instalado
- Intenta limpiar caché: botón "Clear cache" en el menú de Streamlit

### Estilos no se aplican
- Reinicia la app completamente
- Verifica que `utils/styling.py` está en el path

---

Para más información, ver el [README principal](../README.md) del proyecto.
