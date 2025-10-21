#!/usr/bin/env Rscript
# ==============================================================================
# DEFINE AMÉRICA DNA - TACTICAL PROFILE
# ==============================================================================
#
# Propósito: Definir el "ADN táctico" del Club América en 6 dimensiones
#            para identificar qué tipo de jugadores encajan mejor
#
# Input:
#   - data/processed/player_metrics_2024_2025.parquet
#   - data/processed/team_aggregates_2024_2025.json
#
# Output:
#   - data/processed/america_dna_profile.json
#
# ==============================================================================

# Load required libraries
suppressPackageStartupMessages({
  library(arrow)
  library(tidyverse)
  library(jsonlite)
})

# Helper function to print section headers
print_section <- function(title) {
  cat("\n")
  cat(paste(rep("=", 80), collapse = ""), "\n")
  cat(sprintf("  %s\n", title))
  cat(paste(rep("=", 80), collapse = ""), "\n\n")
}

# ==============================================================================
# SETUP
# ==============================================================================

print_section("CLUB AMÉRICA DNA CALCULATOR")

cat("📂 Loading data...\n")

# Load player metrics
player_metrics <- read_parquet("data/processed/player_metrics_2024_2025.parquet")
cat(sprintf("   ✓ Player metrics loaded: %d players\n", nrow(player_metrics)))

# Load team aggregates
team_agg <- read_json("data/processed/team_aggregates_2024_2025.json")
cat(sprintf("   ✓ Team aggregates loaded\n"))

# ==============================================================================
# DIMENSION 1: PROGRESSION
# ==============================================================================

print_section("DIMENSION 1: PROGRESSION")

cat("🏃 Analyzing ball progression capabilities...\n\n")

progression_metrics <- list(
  progressive_passes_p90 = team_agg$avg_progressive_passes_p90,
  progressive_carries_p90 = team_agg$avg_progressive_carries_p90,
  touches_att_third_p90 = team_agg$avg_touches_att_third_p90
)

# Normalize to 0-100 scale (based on Liga MX benchmarks)
# High progression teams: 15+ progressive passes, 4+ carries, 40+ touches
progression_score <- (
  min(progression_metrics$progressive_passes_p90 / 15, 1) * 40 +
  min(progression_metrics$progressive_carries_p90 / 4, 1) * 30 +
  min(progression_metrics$touches_att_third_p90 / 40, 1) * 30
) * 100

# Classify strength
progression_strength <- case_when(
  progression_score >= 85 ~ "Elite",
  progression_score >= 70 ~ "High",
  progression_score >= 55 ~ "Above Average",
  progression_score >= 40 ~ "Average",
  TRUE ~ "Below Average"
)

cat(sprintf("   Progression Score: %.1f/100 (%s)\n", progression_score, progression_strength))
cat(sprintf("   • Progressive passes p90: %.2f\n", progression_metrics$progressive_passes_p90))
cat(sprintf("   • Progressive carries p90: %.2f\n", progression_metrics$progressive_carries_p90))
cat(sprintf("   • Touches attacking third p90: %.2f\n", progression_metrics$touches_att_third_p90))

# ==============================================================================
# DIMENSION 2: CREATION
# ==============================================================================

print_section("DIMENSION 2: CREATION")

cat("🎨 Analyzing chance creation...\n\n")

creation_metrics <- list(
  xA_p90 = team_agg$avg_xA_p90,
  shot_assists_p90 = team_agg$avg_shot_assists_p90,
  key_passes_p90 = team_agg$avg_key_passes_p90
)

# Normalize to 0-100 scale
# Top creative teams: 0.10+ xA, 1.0+ shot assists, 0.8+ key passes
creation_score <- (
  min(creation_metrics$xA_p90 / 0.10, 1) * 50 +
  min(creation_metrics$shot_assists_p90 / 1.0, 1) * 30 +
  min(creation_metrics$key_passes_p90 / 0.8, 1) * 20
) * 100

creation_strength <- case_when(
  creation_score >= 85 ~ "Elite",
  creation_score >= 70 ~ "High",
  creation_score >= 55 ~ "Above Average",
  creation_score >= 40 ~ "Average",
  TRUE ~ "Below Average"
)

cat(sprintf("   Creation Score: %.1f/100 (%s)\n", creation_score, creation_strength))
cat(sprintf("   • Expected Assists (xA) p90: %.4f\n", creation_metrics$xA_p90))
cat(sprintf("   • Shot assists p90: %.2f\n", creation_metrics$shot_assists_p90))
cat(sprintf("   • Key passes p90: %.2f\n", creation_metrics$key_passes_p90))

# ==============================================================================
# DIMENSION 3: FINISHING
# ==============================================================================

print_section("DIMENSION 3: FINISHING")

cat("⚽ Analyzing finishing quality...\n\n")

finishing_metrics <- list(
  xG_p90 = team_agg$avg_xG_p90,
  shots_p90 = team_agg$avg_shots_p90
)

# Calculate shot quality (xG per shot)
shot_quality <- finishing_metrics$xG_p90 / finishing_metrics$shots_p90

# Normalize to 0-100 scale
# Elite finishers: 0.15+ xG p90, 0.12+ xG per shot
finishing_score <- (
  min(finishing_metrics$xG_p90 / 0.15, 1) * 60 +
  min(shot_quality / 0.12, 1) * 40
) * 100

finishing_strength <- case_when(
  finishing_score >= 85 ~ "Elite",
  finishing_score >= 70 ~ "High",
  finishing_score >= 55 ~ "Above Average",
  finishing_score >= 40 ~ "Average",
  TRUE ~ "Below Average"
)

cat(sprintf("   Finishing Score: %.1f/100 (%s)\n", finishing_score, finishing_strength))
cat(sprintf("   • Expected Goals (xG) p90: %.4f\n", finishing_metrics$xG_p90))
cat(sprintf("   • Shots p90: %.2f\n", finishing_metrics$shots_p90))
cat(sprintf("   • Shot quality (xG/shot): %.4f\n", shot_quality))

# ==============================================================================
# DIMENSION 4: PRESSING
# ==============================================================================

print_section("DIMENSION 4: PRESSING")

cat("🛡️  Analyzing defensive intensity...\n\n")

pressing_metrics <- list(
  pressures_p90 = team_agg$avg_pressures_p90,
  tackles_p90 = team_agg$avg_tackles_p90,
  interceptions_p90 = team_agg$avg_interceptions_p90
)

# Normalize to 0-100 scale
# High pressing teams: 14+ pressures, 1.5+ tackles, 0.8+ interceptions
pressing_score <- (
  min(pressing_metrics$pressures_p90 / 14, 1) * 60 +
  min(pressing_metrics$tackles_p90 / 1.5, 1) * 20 +
  min(pressing_metrics$interceptions_p90 / 0.8, 1) * 20
) * 100

pressing_strength <- case_when(
  pressing_score >= 85 ~ "Elite",
  pressing_score >= 70 ~ "High",
  pressing_score >= 55 ~ "Above Average",
  pressing_score >= 40 ~ "Average",
  TRUE ~ "Below Average"
)

cat(sprintf("   Pressing Score: %.1f/100 (%s)\n", pressing_score, pressing_strength))
cat(sprintf("   • Pressures p90: %.2f\n", pressing_metrics$pressures_p90))
cat(sprintf("   • Tackles p90: %.2f\n", pressing_metrics$tackles_p90))
cat(sprintf("   • Interceptions p90: %.2f\n", pressing_metrics$interceptions_p90))

# ==============================================================================
# DIMENSION 5: POSSESSION
# ==============================================================================

print_section("DIMENSION 5: POSSESSION")

cat("🎯 Analyzing possession quality...\n\n")

possession_metrics <- list(
  pass_completion_pct = team_agg$avg_pass_completion_pct,
  touches_att_third_p90 = team_agg$avg_touches_att_third_p90
)

# Normalize to 0-100 scale
# Top possession teams: 85%+ completion, 40+ touches in att third
possession_score <- (
  min(possession_metrics$pass_completion_pct / 85, 1) * 60 +
  min(possession_metrics$touches_att_third_p90 / 40, 1) * 40
) * 100

possession_strength <- case_when(
  possession_score >= 85 ~ "Elite",
  possession_score >= 70 ~ "High",
  possession_score >= 55 ~ "Above Average",
  possession_score >= 40 ~ "Average",
  TRUE ~ "Below Average"
)

cat(sprintf("   Possession Score: %.1f/100 (%s)\n", possession_score, possession_strength))
cat(sprintf("   • Pass completion: %.2f%%\n", possession_metrics$pass_completion_pct))
cat(sprintf("   • Touches attacking third p90: %.2f\n", possession_metrics$touches_att_third_p90))

# ==============================================================================
# DIMENSION 6: DRIBBLING
# ==============================================================================

print_section("DIMENSION 6: DRIBBLING")

cat("🎨 Analyzing 1v1 capabilities...\n\n")

dribbling_metrics <- list(
  dribbles_p90 = team_agg$avg_dribbles_p90,
  dribbles_successful_p90 = team_agg$avg_dribbles_successful_p90,
  dribble_success_pct = team_agg$avg_dribble_success_pct
)

# Normalize to 0-100 scale
# Dribble-heavy teams: 2.0+ dribbles, 1.2+ successful, 65%+ success rate
dribbling_score <- (
  min(dribbling_metrics$dribbles_p90 / 2.0, 1) * 40 +
  min(dribbling_metrics$dribbles_successful_p90 / 1.2, 1) * 35 +
  min(dribbling_metrics$dribble_success_pct / 65, 1) * 25
) * 100

dribbling_strength <- case_when(
  dribbling_score >= 85 ~ "Elite",
  dribbling_score >= 70 ~ "High",
  dribbling_score >= 55 ~ "Above Average",
  dribbling_score >= 40 ~ "Average",
  TRUE ~ "Below Average"
)

cat(sprintf("   Dribbling Score: %.1f/100 (%s)\n", dribbling_score, dribbling_strength))
cat(sprintf("   • Dribbles p90: %.2f\n", dribbling_metrics$dribbles_p90))
cat(sprintf("   • Successful dribbles p90: %.2f\n", dribbling_metrics$dribbles_successful_p90))
cat(sprintf("   • Dribble success rate: %.2f%%\n", dribbling_metrics$dribble_success_pct))

# ==============================================================================
# GENERATE DNA PROFILE
# ==============================================================================

print_section("GENERATE DNA PROFILE")

cat("🧬 Creating Club América tactical DNA profile...\n\n")

# Calculate overall tactical score
overall_score <- mean(c(
  progression_score,
  creation_score,
  finishing_score,
  pressing_score,
  possession_score,
  dribbling_score
))

# Identify top 3 strengths
dimension_scores <- c(
  Progression = progression_score,
  Creation = creation_score,
  Finishing = finishing_score,
  Pressing = pressing_score,
  Possession = possession_score,
  Dribbling = dribbling_score
)

top_strengths <- names(sort(dimension_scores, decreasing = TRUE))[1:3]
weaknesses <- names(sort(dimension_scores, decreasing = FALSE))[1:2]

# Generate tactical identity description
tactical_identity <- case_when(
  pressing_score >= 80 & possession_score >= 75 ~
    "High-pressing possession team with strong vertical progression",
  pressing_score >= 80 & progression_score >= 80 ~
    "Aggressive high-pressing team with fast vertical transitions",
  possession_score >= 80 & creation_score >= 70 ~
    "Possession-dominant creative team",
  progression_score >= 80 ~
    "Direct vertical team with quick progression",
  TRUE ~ "Balanced tactical approach"
)

cat(sprintf("   Overall DNA Score: %.1f/100\n", overall_score))
cat(sprintf("   Tactical Identity: %s\n\n", tactical_identity))

cat("   Top 3 Strengths:\n")
for (i in 1:3) {
  cat(sprintf("      %d. %s (%.1f/100)\n", i, top_strengths[i],
              dimension_scores[top_strengths[i]]))
}

cat("\n   Areas for Improvement:\n")
for (i in 1:2) {
  cat(sprintf("      %d. %s (%.1f/100)\n", i, weaknesses[i],
              dimension_scores[weaknesses[i]]))
}

# ==============================================================================
# IDEAL PLAYER PROFILE
# ==============================================================================

print_section("IDEAL PLAYER PROFILE")

cat("👤 Defining ideal player characteristics for América...\n\n")

# Must-have attributes (based on top strengths)
must_have <- c()
if ("Pressing" %in% top_strengths) {
  must_have <- c(must_have, "High work rate and pressing intensity")
}
if ("Possession" %in% top_strengths) {
  must_have <- c(must_have, "High pass completion rate (>80%)")
}
if ("Progression" %in% top_strengths) {
  must_have <- c(must_have, "Ability to progress the ball vertically")
}

# Nice-to-have attributes (areas for improvement)
nice_to_have <- c()
if ("Creation" %in% weaknesses) {
  nice_to_have <- c(nice_to_have, "High xA - Creative passing ability")
}
if ("Finishing" %in% weaknesses) {
  nice_to_have <- c(nice_to_have, "High shot quality (xG per shot)")
}
if ("Dribbling" %in% weaknesses) {
  nice_to_have <- c(nice_to_have, "1v1 dribbling ability (>60% success)")
}

cat("   Must-Have Attributes:\n")
for (attr in must_have) {
  cat(sprintf("      ✓ %s\n", attr))
}

cat("\n   Nice-to-Have Attributes:\n")
for (attr in nice_to_have) {
  cat(sprintf("      • %s\n", attr))
}

# ==============================================================================
# SAVE DNA PROFILE
# ==============================================================================

print_section("SAVE DNA PROFILE")

# Create comprehensive DNA profile
dna_profile <- list(
  team = "Club América",
  season = team_agg$season,
  overall_score = round(overall_score, 2),
  tactical_identity = tactical_identity,

  dimensions = list(
    progression = list(
      score = round(progression_score, 2),
      strength = progression_strength,
      metrics = progression_metrics,
      description = "Vertical ball progression towards opponent's goal"
    ),
    creation = list(
      score = round(creation_score, 2),
      strength = creation_strength,
      metrics = creation_metrics,
      description = "Ability to create goal-scoring opportunities"
    ),
    finishing = list(
      score = round(finishing_score, 2),
      strength = finishing_strength,
      metrics = c(finishing_metrics, list(shot_quality = shot_quality)),
      description = "Quality and volume of shooting opportunities"
    ),
    pressing = list(
      score = round(pressing_score, 2),
      strength = pressing_strength,
      metrics = pressing_metrics,
      description = "Defensive intensity and ball recovery"
    ),
    possession = list(
      score = round(possession_score, 2),
      strength = possession_strength,
      metrics = possession_metrics,
      description = "Ball control and circulation quality"
    ),
    dribbling = list(
      score = round(dribbling_score, 2),
      strength = dribbling_strength,
      metrics = dribbling_metrics,
      description = "1v1 take-on ability and success"
    )
  ),

  strengths = top_strengths,
  weaknesses = weaknesses,

  ideal_player_profile = list(
    must_have = must_have,
    nice_to_have = nice_to_have
  ),

  metadata = list(
    total_players_analyzed = team_agg$total_players,
    total_matches = team_agg$total_matches,
    generated_at = Sys.time()
  )
)

# Save to JSON
output_file <- "data/processed/america_dna_profile.json"
write_json(dna_profile, output_file, pretty = TRUE, auto_unbox = TRUE)

cat(sprintf("💾 DNA Profile saved to: %s\n", output_file))
cat(sprintf("   File size: %.1f KB\n", file.info(output_file)$size / 1024))

# ==============================================================================
# SUMMARY & VISUALIZATION DATA
# ==============================================================================

print_section("SUMMARY")

cat("✅ Club América DNA Profile successfully created!\n\n")

cat("📊 DNA Dimensions Summary:\n")
cat(sprintf("   Overall Score: %.1f/100\n\n", overall_score))

# Create radar chart data
cat("   Radar Chart Data (for visualization):\n")
dimensions_df <- data.frame(
  dimension = names(dimension_scores),
  score = as.numeric(dimension_scores)
) %>%
  arrange(desc(score))

dimensions_df %>%
  pwalk(function(dimension, score) {
    bar_length <- round(score / 5)
    bar <- paste(rep("█", bar_length), collapse = "")
    cat(sprintf("      %-12s %s %.1f\n",
                paste0(dimension, ":"), bar, score))
  })

cat("\n🎯 Tactical Identity:\n")
cat(sprintf("   %s\n", tactical_identity))

cat("\n🦅 Ideal Player for América:\n")
cat("   Must have:\n")
for (attr in must_have) {
  cat(sprintf("      ✓ %s\n", attr))
}

cat("\n🎯 Next Steps:\n")
cat("   1. Use DNA profile to define player compatibility scores\n")
cat("   2. Build FitScore model (04_fitscore_model.R)\n")
cat("   3. Recommend players from other Liga MX teams\n")
cat("   4. Visualize DNA profile (radar chart)\n")

cat("\n💡 Quick load:\n")
cat("   library(jsonlite)\n")
cat("   dna <- read_json('data/processed/america_dna_profile.json')\n")

cat("\n")
cat(paste(rep("=", 80), collapse = ""), "\n\n")
