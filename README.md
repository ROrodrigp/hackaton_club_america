# 🦅 Club América - Sistema de Scouting con DNA Táctico y FitScore

**ISAC Sports Analytics Hackathon 2025** | Liga MX + StatsBomb 360 Data

---

## 🚀 Aplicación en Vivo

<div align="center">

### 👉 [**VER APLICACIÓN INTERACTIVA**](https://hackatonclubamerica-h6my7qwtxbf7nf6gvbgem3.streamlit.app) 👈

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://hackatonclubamerica-h6my7qwtxbf7nf6gvbgem3.streamlit.app/Buscar_Jugador)

**Explora el sistema completo de análisis táctico y recomendaciones de jugadores**

</div>

---

## 📋 Resumen Ejecutivo

Sistema de análisis y recomendación de jugadores que prioriza la **compatibilidad táctica** sobre estadísticas individuales, respondiendo: **"¿Qué jugador encaja mejor en el equipo y por qué?"**

### ¿Qué hace?

1. **Analiza el DNA táctico del Club América** en 6 dimensiones fundamentales
2. **Evalúa jugadores de 18 equipos** de Liga MX mediante un algoritmo de FitScore
3. **Predice compatibilidad** entre jugadores y el estilo de juego del América
4. **Presenta recomendaciones** a través de una aplicación web interactiva

---

## 🎯 El Algoritmo FitScore

### Fórmula
```
FitScore = (60% × DNA Match) + (30% × Gap Filling) + (10% × Role Fit)
```

### Componentes

#### 1. **DNA Match (60%)** - Similitud Táctica
Similitud coseno entre el perfil táctico del jugador y el Club América en 6 dimensiones:
- 📈 **Progression**: Avance del balón (pases/conducciones progresivas)
- 🎨 **Creation**: Generación de ocasiones (xA, pases clave)
- ⚽ **Finishing**: Calidad de finalización (xG, tiros)
- 💪 **Pressing**: Intensidad defensiva (presiones p90)
- 🎯 **Possession**: Control del balón (% pases completados)
- ⚡ **Dribbling**: Capacidad de regate (regates exitosos)

#### 2. **Gap Filling (30%)** - Llenado de Brechas
Evalúa qué tanto el jugador fortalece las áreas débiles del equipo (dimensiones < P95).

#### 3. **Role Fit (10%)** - Compatibilidad Posicional
Compatibilidad del jugador con las necesidades posicionales del América.

### Interpretación

| FitScore | Categoría | Acción |
|----------|-----------|--------|
| 95-100 | ⭐ Elite | Fichaje prioritario |
| 90-95 | ✅ Fuerte | Fichaje recomendado |
| 85-90 | ⚠️ Bueno | Evaluación profunda |
| < 85 | ❌ Bajo | No recomendado |

---

## 📊 Datos y Cobertura

### Fuente
- **StatsBomb 360** event data
- Temporada **2024/2025 Apertura**
- **19 equipos** de Liga MX (18 scouting + América)

### Pool de Scouting (18 equipos)
Atlas, Atlético San Luis, Cruz Azul, Guadalajara, Juárez, Mazatlán, Monterrey, Necaxa, Pachuca, Puebla, Pumas, Querétaro, Santos Laguna, Tigres UANL, Toluca, León, San Luis, Tijuana

### Criterios de Filtrado
- **Mínimo**: 270 minutos jugados (~3 partidos completos)
- **Jugadores de campo**: Porteros excluidos del análisis
- **Métricas normalizadas**: Todas per 90 minutos (p90)

### Benchmarks
- **Percentil 90 (P90)** calculado sobre los 19 equipos
- Representa nivel "elite" de Liga MX
- Score ≥ 95 = fortaleza distintiva

---

## 🚀 La Aplicación Web

### Acceso
```bash
cd app
streamlit run streamlit_app.py
```

### Módulos

#### 🏠 **Inicio**
- Overview del sistema
- Estadísticas del pool de scouting
- Metodología FitScore

#### 🧬 **DNA Club América**
- Análisis detallado de las 6 dimensiones tácticas
- Radar charts comparando vs P90 de Liga MX
- Identificación de fortalezas y áreas de mejora
- Métricas subyacentes por dimensión

#### ⚽ **Recomendaciones**
- **Top 20**: Jugadores más compatibles
- **Worst 20**: Jugadores con baja compatibilidad
- Filtros por equipo, posición, FitScore
- Análisis detallado por jugador:
  - FitScore breakdown (DNA Match, Gap Filling, Role Fit)
  - Radar chart comparativo
  - Rankings en el pool
  - Métricas posicionales clave
  - Justificación de la recomendación

#### 🔍 **Buscar Jugador**
- Búsqueda de cualquier jugador del pool
- Filtros por equipo y posición
- Mismo análisis completo que Recomendaciones
- Ideal para evaluación de jugadores específicos

---

## 🏗️ Estructura del Proyecto

```
hackaton_club_america/
├── app/                           # Aplicación Streamlit
│   ├── streamlit_app.py           # Página principal
│   ├── pages/
│   │   ├── 1_🧬_DNA_Club_America.py
│   │   ├── 2_⚽_Player_Recommendations.py
│   │   └── 3_🔍_Buscar_Jugador.py
│   └── utils/
│       ├── data_loader.py         # Carga de datos
│       ├── styling.py             # CSS y tema
│       └── visualizations.py      # Gráficas Plotly
│
├── data/
│   ├── processed/
│   │   ├── america_dna_profile.json
│   │   ├── liga_mx_benchmarks_p90.json
│   │   ├── scouting_pool_all_metrics.csv
│   │   ├── top_recommendations.csv
│   │   ├── worst_recommendations.csv
│   │   └── player_fit_scores.json
│   │
│   └── teams/                     # Datos por equipo (18 equipos)
│       ├── America/
│       ├── Atlas/
│       ├── Tigres_UANL/
│       └── ... (15 más)
│
├── src/                           # Pipeline de datos (R)
│   ├── 01_initial_edar.R          # Descarga datos América
│   ├── 02a_calculate_team_aggregates.R
│   ├── 02b_calculate_scouting_pool.R
│   ├── 03_define_america_dna.R
│   └── 04_calculate_fit_score.R
│
├── README.md                      # Este archivo
└── CLAUDE.md                      # Instrucciones para Claude Code
```

---

## 🛠️ Instalación y Uso

### Requisitos

#### Python (App)
```bash
pip install streamlit pandas plotly numpy
```

#### R (Pipeline de datos)
```r
install.packages(c("tidyverse", "arrow", "jsonlite"))
devtools::install_github("statsbomb/StatsBombR")
```

### Ejecución

#### 1. Ejecutar Pipeline Completo (Opcional - ya ejecutado)
```bash
# Pipeline de datos R
Rscript src/01_initial_edar.R
Rscript src/02a_calculate_team_aggregates.R
Rscript src/02b_calculate_scouting_pool.R
Rscript src/03_define_america_dna.R
Rscript src/04_calculate_fit_score.R
```

#### 2. Lanzar Aplicación
```bash
# Desde el directorio raíz
streamlit run app/streamlit_app.py

# O desde app/
cd app
streamlit run streamlit_app.py
```

La app se abrirá en `http://localhost:8501`

---

## 🔐 Configuración de Credenciales

Las credenciales de StatsBomb están externalizadas por seguridad:

```bash
# 1. Copiar archivo de ejemplo
cp .statsbomb_credentials.example .statsbomb_credentials

# 2. Editar con credenciales reales
# Formato:
# username=tu_usuario@email.com
# password=tu_password
```

⚠️ **El archivo `.statsbomb_credentials` está en `.gitignore` y NUNCA debe commitearse.**

---

## 📈 Casos de Uso

1. **Planificación de fichajes**: Identificar jugadores compatibles para próxima ventana de transferencias
2. **Análisis competitivo**: Evaluar jugadores de equipos rivales
3. **Evaluación táctica**: Entender cómo un jugador cambiaría el balance del equipo
4. **Scouting proactivo**: Descubrir valor oculto antes de que sea obvio en el mercado
5. **Comparación posicional**: Encontrar el mejor jugador por posición específica

---

## 🎯 Valor del Sistema

### 1. Decisiones Basadas en Contexto
No busca "el mejor jugador", sino **el que mejor encaja** en el Club América.

### 2. Identificación de Valor Oculto
Descubre jugadores subestimados con alta compatibilidad táctica.

### 3. Reduce Riesgo de Fichajes
Minimiza probabilidad de contratar jugadores que no se adapten al sistema.

### 4. Enfoque Holístico
Combina similitud táctica + mejora estratégica + pragmatismo posicional.

### 5. Transparencia y Justificación
Cada recomendación incluye análisis detallado y visualizaciones del "por qué".

---

## 🏆 Criterios de Evaluación (Hackathon)

| Criterio | Peso | Cómo lo cumple FitScore |
|----------|------|------------------------|
| **Innovación** | 15% | ✅ Algoritmo de compatibilidad táctica (DNA Match + Gap Filling) |
| **Precisión & Metodología** | 20% | ✅ StatsBomb 360 + métricas normalizadas + benchmarks P90 |
| **Relevancia Scouting** | 25% | ✅ Responde directamente "¿Encaja este jugador?" |
| **Comunicación** | 10% | ✅ App interactiva + visualizaciones claras |
| **Técnicas Visuales** | 10% | ✅ Radar charts + rankings + tablas interactivas |
| **KPIs** | 15% | ✅ FitScore = métrica única y accionable |

---

## 📚 Recursos

### StatsBomb
- [StatsBombR Tutorial](https://www.hudl.com/blog/using-hudl-statsbomb-free-data-in-r)
- [StatsBomb Python](https://github.com/statsbomb/statsbombpy)
- [Event Data Specification](https://statsbomb.com/)

### Métricas Clave
- **xG**: Probabilidad de que un tiro termine en gol
- **xA**: Suma del xG de tiros creados por pases del jugador
- **Progressive Pass**: Pase que avanza ≥10 yardas hacia portería rival
- **Progressive Carry**: Acarreo que avanza ≥10 yardas hacia portería

---

## 📝 Limitaciones y Próximos Pasos

### Limitaciones Actuales
- Solo temporada 2024/2025 Apertura
- Sin datos de contexto de oponente (dificultad de rivales)
- No considera lesiones, edad, o valor de mercado

### Mejoras Futuras
- Análisis multi-temporal (tendencias de rendimiento)
- Integración de datos de mercado y salarios
- Modelo de "chemistry" entre jugadores
- Optimización de formaciones completas
- Predicción de adaptación temporal (curva de aprendizaje)

---

## 📄 Licencia

- Datos: **StatsBomb** bajo licencia de hackathon
- Código: MIT License

---

## 📧 Información del Hackathon

- **Evento**: ISAC Sports Analytics Hackathon 2025
- **Presentado por**: Club América
- **Fecha de entrega**: 22 de octubre, 2025
- **Presentación final**: 6 de noviembre, 2025

---

<div align="center">

**🦅 Hecho con datos y pasión por el fútbol ⚽**

*"No fichamos jugadores. Fichamos el fit perfecto."*

</div>
