#!/usr/bin/env Rscript
# ==============================================================================
# CALCULATE TEAM AGGREGATES - SCOUTING TEAMS
# ==============================================================================
#
# Propósito: Calcular agregados por equipo (promedios de métricas)
#            para los 9 equipos de scouting
#
# Input:
#   - data/processed/scouting_pool_all_metrics.parquet
#
# Output:
#   - data/processed/toluca/team_aggregates.json
#   - data/processed/guadalajara/team_aggregates.json
#   - data/processed/monterrey/team_aggregates.json
#   - data/processed/mazatlan/team_aggregates.json
#   - data/processed/cruz_azul/team_aggregates.json
#   - data/processed/tigres/team_aggregates.json
#   - data/processed/leon/team_aggregates.json
#   - data/processed/atlas/team_aggregates.json
#   - data/processed/puebla/team_aggregates.json
#   - data/processed/all_teams_aggregates.json (los 10 equipos combinados)
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

# Helper function to normalize team names
normalize_team_name <- function(team_name) {
  team_name %>%
    str_to_lower() %>%
    str_replace_all("á", "a") %>%
    str_replace_all("é", "e") %>%
    str_replace_all("í", "i") %>%
    str_replace_all("ó", "o") %>%
    str_replace_all("ú", "u") %>%
    str_replace_all("[^a-z0-9]+", "_") %>%
    str_replace_all("^_|_$", "")
}

# ==============================================================================
# SETUP
# ==============================================================================

print_section("TEAM AGGREGATES CALCULATOR - SCOUTING TEAMS")

cat("📂 Loading scouting pool data...\n")

# Load scouting pool
scouting_pool <- read_parquet("data/processed/scouting_pool_all_metrics.parquet")
cat(sprintf("   ✓ Loaded %d players from scouting pool\n", nrow(scouting_pool)))

# Get unique teams
teams <- unique(scouting_pool$team.name)
cat(sprintf("\n   Teams found: %d\n", length(teams)))
for (team in teams) {
  cat(sprintf("      • %s\n", team))
}

# ==============================================================================
# CALCULATE TEAM AGGREGATES
# ==============================================================================

print_section("CALCULATE AGGREGATES BY TEAM")

all_team_aggregates <- list()

for (team_name in teams) {

  cat("\n")
  cat(paste(rep("-", 80), collapse = ""), "\n")
  cat(sprintf("  Processing: %s\n", team_name))
  cat(paste(rep("-", 80), collapse = ""), "\n\n")

  # Filter players from this team
  team_players <- scouting_pool %>%
    filter(team.name == team_name)

  cat(sprintf("   Players: %d\n", nrow(team_players)))
  cat(sprintf("   Total minutes: %.0f\n", sum(team_players$total_minutes, na.rm = TRUE)))

  # Calculate team aggregates (average of all players)
  team_agg <- list(
    team_name = team_name,
    season = "2024/2025",

    # Progression
    avg_progressive_passes_p90 = mean(team_players$progressive_passes_p90, na.rm = TRUE),
    avg_progressive_carries_p90 = mean(team_players$progressive_carries_p90, na.rm = TRUE),

    # Creation
    avg_shot_assists_p90 = mean(team_players$shot_assists_p90, na.rm = TRUE),
    avg_key_passes_p90 = mean(team_players$key_passes_p90, na.rm = TRUE),
    avg_xA_p90 = mean(team_players$xA_p90, na.rm = TRUE),

    # Finishing
    avg_shots_p90 = mean(team_players$shots_p90, na.rm = TRUE),
    avg_xG_p90 = mean(team_players$xG_p90, na.rm = TRUE),

    # Defense
    avg_tackles_p90 = mean(team_players$tackles_p90, na.rm = TRUE),
    avg_interceptions_p90 = mean(team_players$interceptions_p90, na.rm = TRUE),
    avg_pressures_p90 = mean(team_players$pressures_p90, na.rm = TRUE),

    # Possession
    avg_pass_completion_pct = mean(team_players$pass_completion_pct, na.rm = TRUE),
    avg_touches_att_third_p90 = mean(team_players$touches_att_third_p90, na.rm = TRUE),

    # Dribbling
    avg_dribbles_p90 = mean(team_players$dribbles_p90, na.rm = TRUE),
    avg_dribbles_successful_p90 = mean(team_players$dribbles_successful_p90, na.rm = TRUE),
    avg_dribble_success_pct = mean(team_players$dribble_success_pct, na.rm = TRUE),

    # Metadata
    total_players = nrow(team_players),
    total_minutes = sum(team_players$total_minutes, na.rm = TRUE),
    total_matches = sum(team_players$matches_played, na.rm = TRUE)
  )

  # Show key metrics
  cat("\n   Key Metrics:\n")
  cat(sprintf("      Progressive passes p90: %.2f\n", team_agg$avg_progressive_passes_p90))
  cat(sprintf("      xA p90: %.4f\n", team_agg$avg_xA_p90))
  cat(sprintf("      xG p90: %.4f\n", team_agg$avg_xG_p90))
  cat(sprintf("      Pass completion: %.2f%%\n", team_agg$avg_pass_completion_pct))
  cat(sprintf("      Pressures p90: %.2f\n", team_agg$avg_pressures_p90))

  # Save to team directory
  team_dir <- file.path("data/processed", normalize_team_name(team_name))

  # Create directory if it doesn't exist
  dir.create(team_dir, recursive = TRUE, showWarnings = FALSE)

  output_file <- file.path(team_dir, "team_aggregates.json")
  write_json(team_agg, output_file, pretty = TRUE, auto_unbox = TRUE)

  cat(sprintf("\n   💾 Saved to: %s\n", output_file))

  # Add to combined list
  all_team_aggregates[[team_name]] <- team_agg
}

# ==============================================================================
# LOAD AMÉRICA AGGREGATES
# ==============================================================================

print_section("LOAD AMÉRICA AGGREGATES")

cat("📂 Loading América team aggregates...\n")

# Check if América aggregates exist
america_agg_file <- "data/processed/team_aggregates_2024_2025.json"

if (file.exists(america_agg_file)) {
  america_agg <- read_json(america_agg_file)

  # Add team_name field if missing
  if (is.null(america_agg$team_name)) {
    america_agg$team_name <- "Club América"
  }

  cat(sprintf("   ✓ América aggregates loaded\n"))
  cat(sprintf("      Progressive passes p90: %.2f\n", america_agg$avg_progressive_passes_p90))
  cat(sprintf("      xA p90: %.4f\n", america_agg$avg_xA_p90))
  cat(sprintf("      xG p90: %.4f\n", america_agg$avg_xG_p90))

  # Add to combined list
  all_team_aggregates[["Club América"]] <- america_agg

} else {
  cat("   ⚠️  América aggregates not found at:\n")
  cat(sprintf("      %s\n", america_agg_file))
  cat("   Continuing with scouting teams only...\n")
}

# ==============================================================================
# CREATE COMBINED AGGREGATES FILE
# ==============================================================================

print_section("CREATE COMBINED AGGREGATES")

cat("🔗 Combining all team aggregates...\n")

# Convert to dataframe for easier analysis
all_teams_df <- bind_rows(
  lapply(names(all_team_aggregates), function(team_name) {
    agg <- all_team_aggregates[[team_name]]
    data.frame(
      team_name = team_name,
      avg_progressive_passes_p90 = agg$avg_progressive_passes_p90,
      avg_progressive_carries_p90 = agg$avg_progressive_carries_p90,
      avg_shot_assists_p90 = agg$avg_shot_assists_p90,
      avg_key_passes_p90 = agg$avg_key_passes_p90,
      avg_xA_p90 = agg$avg_xA_p90,
      avg_shots_p90 = agg$avg_shots_p90,
      avg_xG_p90 = agg$avg_xG_p90,
      avg_tackles_p90 = agg$avg_tackles_p90,
      avg_interceptions_p90 = agg$avg_interceptions_p90,
      avg_pressures_p90 = agg$avg_pressures_p90,
      avg_pass_completion_pct = agg$avg_pass_completion_pct,
      avg_touches_att_third_p90 = agg$avg_touches_att_third_p90,
      avg_dribbles_p90 = agg$avg_dribbles_p90,
      avg_dribbles_successful_p90 = agg$avg_dribbles_successful_p90,
      avg_dribble_success_pct = agg$avg_dribble_success_pct,
      total_players = agg$total_players
    )
  })
)

cat(sprintf("   ✓ Combined %d teams\n", nrow(all_teams_df)))

# Save combined dataframe as JSON
combined_output <- list(
  teams = all_team_aggregates,
  summary = all_teams_df,
  metadata = list(
    total_teams = length(all_team_aggregates),
    season = "2024/2025",
    generated_at = Sys.time()
  )
)

combined_file <- "data/processed/all_teams_aggregates.json"
write_json(combined_output, combined_file, pretty = TRUE, auto_unbox = TRUE)

cat(sprintf("\n   💾 Combined file saved to: %s\n", combined_file))

# ==============================================================================
# CALCULATE BENCHMARKS (PERCENTILES)
# ==============================================================================

print_section("CALCULATE BENCHMARKS (PERCENTILE 90)")

cat("📊 Calculating percentile 90 for each metric...\n\n")

# Calculate percentile 90 for all metrics (more strict than P85)
benchmarks <- list(
  # Progression
  progressive_passes_p90 = quantile(all_teams_df$avg_progressive_passes_p90, 0.90, na.rm = TRUE),
  progressive_carries_p90 = quantile(all_teams_df$avg_progressive_carries_p90, 0.90, na.rm = TRUE),

  # Creation
  xA_p90 = quantile(all_teams_df$avg_xA_p90, 0.90, na.rm = TRUE),
  shot_assists_p90 = quantile(all_teams_df$avg_shot_assists_p90, 0.90, na.rm = TRUE),
  key_passes_p90 = quantile(all_teams_df$avg_key_passes_p90, 0.90, na.rm = TRUE),

  # Finishing
  xG_p90 = quantile(all_teams_df$avg_xG_p90, 0.90, na.rm = TRUE),
  shots_p90 = quantile(all_teams_df$avg_shots_p90, 0.90, na.rm = TRUE),

  # Defense
  pressures_p90 = quantile(all_teams_df$avg_pressures_p90, 0.90, na.rm = TRUE),
  tackles_p90 = quantile(all_teams_df$avg_tackles_p90, 0.90, na.rm = TRUE),
  interceptions_p90 = quantile(all_teams_df$avg_interceptions_p90, 0.90, na.rm = TRUE),

  # Possession
  pass_completion_pct = quantile(all_teams_df$avg_pass_completion_pct, 0.90, na.rm = TRUE),
  touches_att_third_p90 = quantile(all_teams_df$avg_touches_att_third_p90, 0.90, na.rm = TRUE),

  # Dribbling
  dribbles_p90 = quantile(all_teams_df$avg_dribbles_p90, 0.90, na.rm = TRUE),
  dribbles_successful_p90 = quantile(all_teams_df$avg_dribbles_successful_p90, 0.90, na.rm = TRUE),
  dribble_success_pct = quantile(all_teams_df$avg_dribble_success_pct, 0.90, na.rm = TRUE)
)

cat("   Calculated benchmarks (Percentile 90):\n\n")
cat("   Progression:\n")
cat(sprintf("      • Progressive passes p90: %.2f\n", benchmarks$progressive_passes_p90))
cat(sprintf("      • Progressive carries p90: %.2f\n", benchmarks$progressive_carries_p90))
cat("\n   Creation:\n")
cat(sprintf("      • xA p90: %.4f\n", benchmarks$xA_p90))
cat(sprintf("      • Shot assists p90: %.2f\n", benchmarks$shot_assists_p90))
cat(sprintf("      • Key passes p90: %.2f\n", benchmarks$key_passes_p90))
cat("\n   Finishing:\n")
cat(sprintf("      • xG p90: %.4f\n", benchmarks$xG_p90))
cat(sprintf("      • Shots p90: %.2f\n", benchmarks$shots_p90))
cat("\n   Defense:\n")
cat(sprintf("      • Pressures p90: %.2f\n", benchmarks$pressures_p90))
cat(sprintf("      • Tackles p90: %.2f\n", benchmarks$tackles_p90))
cat(sprintf("      • Interceptions p90: %.2f\n", benchmarks$interceptions_p90))
cat("\n   Possession:\n")
cat(sprintf("      • Pass completion: %.2f%%\n", benchmarks$pass_completion_pct))
cat(sprintf("      • Touches att third p90: %.2f\n", benchmarks$touches_att_third_p90))
cat("\n   Dribbling:\n")
cat(sprintf("      • Dribbles p90: %.2f\n", benchmarks$dribbles_p90))
cat(sprintf("      • Successful dribbles p90: %.2f\n", benchmarks$dribbles_successful_p90))
cat(sprintf("      • Dribble success: %.2f%%\n", benchmarks$dribble_success_pct))

# Save benchmarks
benchmarks_file <- "data/processed/liga_mx_benchmarks_p90.json"
write_json(benchmarks, benchmarks_file, pretty = TRUE, auto_unbox = TRUE)

cat(sprintf("\n   💾 Benchmarks saved to: %s\n", benchmarks_file))

# ==============================================================================
# SUMMARY
# ==============================================================================

print_section("SUMMARY")

cat("✅ Team aggregates calculated successfully!\n\n")

cat("📊 Summary:\n")
cat(sprintf("   • Teams processed: %d\n", length(all_team_aggregates)))
cat(sprintf("   • Total players: %d\n", sum(all_teams_df$total_players)))

cat("\n📁 Files created:\n")
for (team_name in names(all_team_aggregates)) {
  team_dir <- file.path("data/processed", normalize_team_name(team_name))
  team_file <- file.path(team_dir, "team_aggregates.json")
  if (file.exists(team_file)) {
    cat(sprintf("   ✓ %s/team_aggregates.json\n", normalize_team_name(team_name)))
  }
}
cat(sprintf("\n   ✓ %s (combined)\n", combined_file))
cat(sprintf("   ✓ %s (benchmarks) ⭐\n", benchmarks_file))

cat("\n🎯 Next Steps:\n")
cat("   1. Script 03 will now use real Liga MX benchmarks\n")
cat("   2. DNA scores will be based on actual data, not estimates\n")
cat("   3. More accurate comparison between teams\n")

cat("\n💡 Quick comparison:\n")
cat("   library(jsonlite)\n")
cat("   all_teams <- read_json('data/processed/all_teams_aggregates.json')\n")
cat("   # Compare teams side by side\n")

cat("\n")
cat(paste(rep("=", 80), collapse = ""), "\n\n")
