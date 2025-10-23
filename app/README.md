# 🦅 Club América - Streamlit Scouting App

App interactiva para análisis de DNA táctico y recomendaciones de fichajes.

## 📦 Instalación

```bash
# Desde el directorio app/
pip install -r requirements.txt
```

## 🚀 Ejecutar la App

```bash
# Desde el directorio raíz del proyecto (hackaton_club_america/)
streamlit run app/streamlit_app.py
```

La app se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📂 Estructura

```
app/
├── streamlit_app.py              # Home page
├── pages/
│   ├── 1_🧬_DNA_Club_America.py    # Análisis DNA
│   └── 2_⚽_Player_Recommendations.py # Top 20 + Worst 20
├── utils/
│   ├── data_loader.py            # Carga de datos
│   ├── styling.py                # Estilos y colores
│   └── visualizations.py         # Gráficos (próximo)
├── requirements.txt              # Dependencias
└── README.md                     # Este archivo
```

## 📊 Páginas

### 🏠 Home
- Overview general del análisis
- Métricas clave (DNA score, jugadores analizados, equipos)
- Insights de fortalezas y debilidades
- Metodología del sistema

### 🧬 DNA Club América
- Radar chart de 6 dimensiones
- Bar charts por dimensión
- Métricas subyacentes detalladas
- Interpretación táctica

### ⚽ Recomendaciones
- Top 20 jugadores recomendados
- Top 20 jugadores a evitar
- Filtros interactivos (equipo, posición, FitScore)
- Detalles por jugador (DNA, Gap Filling, Role Fit)
- Visualizaciones comparativas

## 🎨 Colores Club América

- **Primary**: #041E42 (Navy blue)
- **Secondary**: #FFC629 (Gold)
- **Accent**: #FFFFFF (White)

## 📝 Notas

- La app carga datos desde `data/processed/` y `outputs/`
- Ejecuta los scripts R y Python antes de correr la app
- Las páginas están en `pages/` y se muestran automáticamente en el sidebar
