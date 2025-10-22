#!/usr/bin/env Rscript
# ==============================================================================
# CALCULATE SCOUTING PLAYER METRICS - 2024/2025
# ==============================================================================
#
# Propósito: Calcular métricas individuales por jugador de 9 equipos de scouting
#            Lee datos PARTICIONADOS por equipo y genera métricas
#
# Input (partitioned by team):
#   data/processed/{team}/events.parquet
#   data/processed/{team}/lineups.parquet
#   data/processed/{team}/minutes_played.parquet
#
# Output (partitioned by team):
#   data/processed/{team}/player_metrics.parquet
#
# Output (aggregated):
#   data/processed/scouting_pool_all_metrics.parquet
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

print_section("SCOUTING PLAYER METRICS CALCULATOR")

# Teams to process (same as script 01)
scouting_teams <- c(
  "Toluca",
  "Guadalajara",
  "Monterrey",
  "Mazatlán",
  "Cruz Azul",
  "Tigres",
  "León",
  "Atlas",
  "Puebla"
)

cat("🎯 Teams to process:\n")
for (team in scouting_teams) {
  cat(sprintf("   • %s\n", team))
}

# Minimum minutes threshold
min_minutes <- 270  # ~3 full games

# ==============================================================================
# STEP 1: PROCESS EACH TEAM
# ==============================================================================

print_section("STEP 1: CALCULATE METRICS PER TEAM")

all_team_metrics <- list()

for (team_name in scouting_teams) {

  cat("\n")
  cat(paste(rep("-", 80), collapse = ""), "\n")
  cat(sprintf("  Processing: %s\n", team_name))
  cat(paste(rep("-", 80), collapse = ""), "\n\n")

  team_dir <- file.path("data/processed", normalize_team_name(team_name))

  # Load data
  cat("   📂 Loading data...\n")

  events_file <- file.path(team_dir, "events.parquet")
  lineups_file <- file.path(team_dir, "lineups.parquet")
  minutes_file <- file.path(team_dir, "minutes_played.parquet")

  if (!file.exists(events_file)) {
    cat(sprintf("   ⚠️  Events file not found, skipping %s\n", team_name))
    next
  }

  events <- read_parquet(events_file)
  cat(sprintf("      ✓ Events: %s\n", format(nrow(events), big.mark = ",")))

  lineups <- read_parquet(lineups_file)
  cat(sprintf("      ✓ Lineups: %s\n", format(nrow(lineups), big.mark = ",")))

  minutes_played <- read_parquet(minutes_file)
  cat(sprintf("      ✓ Minutes: %s records\n", format(nrow(minutes_played), big.mark = ",")))

  # Filter events to this team only
  team_events <- events %>%
    filter(str_detect(team.name, regex(team_name, ignore_case = TRUE)))

  cat(sprintf("      ✓ Filtered events: %s\n", format(nrow(team_events), big.mark = ",")))

  # Get primary positions
  cat("\n   📋 Calculating primary positions...\n")

  lineup_positions <- lineups %>%
    select(match_id, player_name, team_name, positions)

  player_position_minutes <- minutes_played %>%
    left_join(lineup_positions,
              by = c("match_id", "player.name" = "player_name", "team.name" = "team_name")) %>%
    mutate(
      primary_position = map_chr(positions, function(pos_json) {
        if (is.na(pos_json) || pos_json == "null" || pos_json == "") {
          return(NA_character_)
        }

        tryCatch({
          pos_df <- jsonlite::fromJSON(pos_json)
          if (is.data.frame(pos_df) && nrow(pos_df) > 0) {
            return(pos_df$position[1])
          } else {
            return(NA_character_)
          }
        }, error = function(e) {
          return(NA_character_)
        })
      })
    ) %>%
    filter(!is.na(primary_position))

  primary_positions <- player_position_minutes %>%
    group_by(player.name, team.name, primary_position) %>%
    summarise(minutes_in_position = sum(MinutesPlayed, na.rm = TRUE), .groups = "drop") %>%
    group_by(player.name, team.name) %>%
    arrange(desc(minutes_in_position)) %>%
    slice(1) %>%
    ungroup() %>%
    select(player.name, team.name, primary_position, minutes_in_primary = minutes_in_position)

  # Aggregate minutes per player
  player_minutes <- minutes_played %>%
    group_by(player.id, player.name, team.name) %>%
    summarise(
      matches_played = n(),
      total_minutes = sum(MinutesPlayed, na.rm = TRUE),
      avg_minutes = mean(MinutesPlayed, na.rm = TRUE),
      times_subbed_on = sum(TimeOn > 0, na.rm = TRUE),
      times_subbed_off = sum(TimeOff < GameEnd, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    left_join(primary_positions, by = c("player.name", "team.name"))

  cat(sprintf("      ✓ Primary positions for %d players\n", nrow(player_minutes)))

  # Calculate metrics
  cat("\n   📊 Calculating metrics...\n")

  # Progressive passes
  progressive_passes <- team_events %>%
    filter(type.name == "Pass") %>%
    mutate(
      is_progressive = !is.na(location.x) & !is.na(pass.end_location.x) &
        (pass.end_location.x - location.x) >= 10
    ) %>%
    filter(is_progressive) %>%
    count(player.name, name = "progressive_passes")

  # Progressive carries
  progressive_carries <- team_events %>%
    filter(type.name == "Carry") %>%
    mutate(
      is_progressive = !is.na(location.x) & !is.na(carry.end_location.x) &
        (carry.end_location.x - location.x) >= 10
    ) %>%
    filter(is_progressive) %>%
    count(player.name, name = "progressive_carries")

  # Shot assists
  shot_assists <- team_events %>%
    filter(type.name == "Pass", !is.na(pass.shot_assist)) %>%
    count(player.name, name = "shot_assists")

  # Goal assists
  goal_assists <- team_events %>%
    filter(type.name == "Pass", !is.na(pass.goal_assist)) %>%
    count(player.name, name = "goal_assists")

  # Expected Assists (xA)
  shot_assist_passes <- team_events %>%
    filter(type.name == "Pass", !is.na(pass.shot_assist)) %>%
    arrange(match_id, index) %>%
    select(match_id, index, player.name, pass.recipient.name, id) %>%
    rename(passer = player.name, pass_index = index, pass_id = id)

  shots_with_xg <- team_events %>%
    filter(type.name == "Shot") %>%
    arrange(match_id, index) %>%
    select(match_id, index, player.name, shot.statsbomb_xg, id) %>%
    rename(shooter = player.name, shot_index = index, shot_id = id)

  xa_data <- shot_assist_passes %>%
    left_join(shots_with_xg,
              by = c("match_id" = "match_id", "pass.recipient.name" = "shooter"),
              relationship = "many-to-many") %>%
    filter(!is.na(shot_index), shot_index > pass_index, shot_index - pass_index <= 5) %>%
    group_by(match_id, pass_id) %>%
    arrange(shot_index) %>%
    slice(1) %>%
    ungroup()

  xa_stats <- xa_data %>%
    group_by(passer) %>%
    summarise(xA = sum(shot.statsbomb_xg, na.rm = TRUE), key_passes = n(), .groups = "drop") %>%
    rename(player.name = passer)

  # Shots and xG
  shots_stats <- team_events %>%
    filter(type.name == "Shot") %>%
    group_by(player.name) %>%
    summarise(
      shots = n(),
      shots_on_target = sum(!is.na(shot.outcome.name) &
                            shot.outcome.name %in% c("Goal", "Saved"), na.rm = TRUE),
      goals = sum(!is.na(shot.outcome.name) & shot.outcome.name == "Goal", na.rm = TRUE),
      xG = sum(shot.statsbomb_xg, na.rm = TRUE),
      .groups = "drop"
    )

  # Tackles
  tackles <- team_events %>%
    filter(type.name == "Duel", !is.na(duel.type.name),
           str_detect(duel.type.name, "Tackle")) %>%
    group_by(player.name) %>%
    summarise(
      tackles = n(),
      tackles_won = sum(!is.na(duel.outcome.name) & duel.outcome.name == "Won", na.rm = TRUE),
      .groups = "drop"
    )

  # Interceptions
  interceptions <- team_events %>%
    filter(type.name == "Interception") %>%
    count(player.name, name = "interceptions")

  # Pressures
  pressures <- team_events %>%
    filter(type.name == "Pressure") %>%
    count(player.name, name = "pressures")

  # Ball recoveries
  recoveries <- team_events %>%
    filter(type.name == "Ball Recovery") %>%
    count(player.name, name = "ball_recoveries")

  # Pass stats
  pass_stats <- team_events %>%
    filter(type.name == "Pass") %>%
    group_by(player.name) %>%
    summarise(
      passes = n(),
      passes_completed = sum(is.na(pass.outcome.name), na.rm = TRUE),
      pass_completion_pct = passes_completed / passes * 100,
      .groups = "drop"
    )

  # Touches in attacking third
  touches_att_third <- team_events %>%
    filter(!is.na(location.x), location.x >= 80) %>%
    count(player.name, name = "touches_att_third")

  # Touches in box
  touches_in_box <- team_events %>%
    filter(!is.na(location.x), !is.na(location.y),
           location.x >= 102, location.y >= 18, location.y <= 62) %>%
    count(player.name, name = "touches_in_box")

  # Dribbles
  dribbles <- team_events %>%
    filter(type.name == "Dribble") %>%
    group_by(player.name) %>%
    summarise(
      dribbles = n(),
      dribbles_successful = sum(!is.na(dribble.outcome.name) &
                                dribble.outcome.name == "Complete", na.rm = TRUE),
      dribbles_failed = sum(!is.na(dribble.outcome.name) &
                            dribble.outcome.name == "Incomplete", na.rm = TRUE),
      dribble_success_pct = if_else(dribbles > 0,
                                    (dribbles_successful / dribbles) * 100,
                                    NA_real_),
      .groups = "drop"
    )

  cat("      ✓ All metrics calculated\n")

  # Combine metrics
  cat("\n   🔗 Combining metrics...\n")

  player_metrics <- player_minutes %>%
    left_join(progressive_passes, by = "player.name") %>%
    left_join(progressive_carries, by = "player.name") %>%
    left_join(shot_assists, by = "player.name") %>%
    left_join(goal_assists, by = "player.name") %>%
    left_join(xa_stats, by = "player.name") %>%
    left_join(shots_stats, by = "player.name") %>%
    left_join(tackles, by = "player.name") %>%
    left_join(interceptions, by = "player.name") %>%
    left_join(pressures, by = "player.name") %>%
    left_join(recoveries, by = "player.name") %>%
    left_join(pass_stats, by = "player.name") %>%
    left_join(touches_att_third, by = "player.name") %>%
    left_join(touches_in_box, by = "player.name") %>%
    left_join(dribbles, by = "player.name")

  # Replace NAs with 0
  player_metrics <- player_metrics %>%
    mutate(across(c(progressive_passes, progressive_carries, shot_assists,
                    goal_assists, key_passes, shots, goals, tackles,
                    interceptions, pressures, ball_recoveries, passes,
                    touches_att_third, touches_in_box, dribbles,
                    dribbles_successful, dribbles_failed),
                  ~replace_na(., 0))) %>%
    mutate(xA = replace_na(xA, 0), xG = replace_na(xG, 0))

  # Normalize to per 90
  cat("\n   📈 Normalizing to per 90 minutes...\n")

  player_metrics <- player_metrics %>%
    mutate(
      progressive_passes_p90 = progressive_passes / total_minutes * 90,
      progressive_carries_p90 = progressive_carries / total_minutes * 90,
      shot_assists_p90 = shot_assists / total_minutes * 90,
      key_passes_p90 = key_passes / total_minutes * 90,
      xA_p90 = xA / total_minutes * 90,
      shots_p90 = shots / total_minutes * 90,
      xG_p90 = xG / total_minutes * 90,
      tackles_p90 = tackles / total_minutes * 90,
      interceptions_p90 = interceptions / total_minutes * 90,
      pressures_p90 = pressures / total_minutes * 90,
      ball_recoveries_p90 = ball_recoveries / total_minutes * 90,
      touches_att_third_p90 = touches_att_third / total_minutes * 90,
      touches_in_box_p90 = touches_in_box / total_minutes * 90,
      dribbles_p90 = dribbles / total_minutes * 90,
      dribbles_successful_p90 = dribbles_successful / total_minutes * 90
    )

  # Filter minimum minutes
  player_metrics_filtered <- player_metrics %>%
    filter(total_minutes >= min_minutes)

  cat(sprintf("      ✓ %d players with %d+ minutes\n",
              nrow(player_metrics_filtered), min_minutes))

  # Save team-specific metrics
  metrics_file <- file.path(team_dir, "player_metrics.parquet")
  write_parquet(player_metrics_filtered, metrics_file)
  cat(sprintf("\n   💾 Saved: %s\n", metrics_file))

  # Add to aggregated list
  all_team_metrics[[team_name]] <- player_metrics_filtered

  cat(sprintf("\n   ✅ %s metrics complete!\n", team_name))
}

# ==============================================================================
# STEP 2: CREATE AGGREGATED SCOUTING POOL
# ==============================================================================

print_section("STEP 2: CREATE AGGREGATED SCOUTING POOL")

cat("🔗 Combining all teams into single scouting pool...\n")

scouting_pool <- bind_rows(all_team_metrics)

cat(sprintf("\n   ✓ Total players in pool: %d\n", nrow(scouting_pool)))

# Show distribution by team
cat("\n   📊 Distribution by team:\n")
scouting_pool %>%
  count(team.name) %>%
  arrange(desc(n)) %>%
  pwalk(function(team.name, n) {
    cat(sprintf("      • %s: %d players\n", team.name, n))
  })

# Save aggregated pool
output_file <- "data/processed/scouting_pool_all_metrics.parquet"
write_parquet(scouting_pool, output_file)
cat(sprintf("\n   💾 Saved aggregated pool: %s\n", output_file))
cat(sprintf("      File size: %.1f KB\n", file.info(output_file)$size / 1024))

# ==============================================================================
# SUMMARY
# ==============================================================================

print_section("SUMMARY")

cat("✅ Scouting player metrics calculated successfully!\n\n")

cat("📊 Metrics Calculated (per player):\n")
cat("   • Progression: Progressive passes & carries (per 90)\n")
cat("   • Creation: Shot assists, key passes, xA (per 90)\n")
cat("   • Finishing: Shots, goals, xG (per 90)\n")
cat("   • Defense: Tackles, interceptions, pressures (per 90)\n")
cat("   • Possession: Pass completion %, touches in box\n")
cat("   • Dribbling: Dribbles, success rate (per 90)\n")

cat("\n📈 Scouting Pool Summary:\n")
cat(sprintf("   • Total players: %d\n", nrow(scouting_pool)))
cat(sprintf("   • Teams: %d\n", length(scouting_teams)))
cat(sprintf("   • Minimum minutes: %d\n", min_minutes))

cat("\n📁 Files created:\n\n")

for (team in scouting_teams) {
  team_dir <- file.path("data/processed", normalize_team_name(team))
  metrics_file <- file.path(team_dir, "player_metrics.parquet")

  if (file.exists(metrics_file)) {
    size_kb <- file.info(metrics_file)$size / 1024
    cat(sprintf("   ✓ %s/player_metrics.parquet (%.1f KB)\n",
                normalize_team_name(team), size_kb))
  }
}

cat(sprintf("\n   ✓ scouting_pool_all_metrics.parquet (%.1f KB)\n",
            file.info(output_file)$size / 1024))

cat("\n🎯 Next Steps:\n")
cat("   1. Compare with América DNA (from script 03)\n")
cat("   2. Build FitScore model (script 04)\n")
cat("   3. Generate player recommendations\n")

cat("\n💡 Quick load:\n")
cat("   library(arrow); library(tidyverse)\n")
cat("   # Load all players\n")
cat("   scouting_pool <- read_parquet('data/processed/scouting_pool_all_metrics.parquet')\n")
cat("\n   # Load specific team\n")
cat("   toluca <- read_parquet('data/processed/toluca/player_metrics.parquet')\n")
cat("\n   # Top 10 by xG\n")
cat("   scouting_pool %>% arrange(desc(xG_p90)) %>% head(10)\n")

cat("\n")
cat(paste(rep("=", 80), collapse = ""), "\n\n")
