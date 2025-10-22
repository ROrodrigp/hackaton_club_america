#!/usr/bin/env Rscript
# ==============================================================================
# CALCULATE PLAYER METRICS - CLUB AMÉRICA 2024/2025
# ==============================================================================
#
# Propósito: Calcular métricas individuales por jugador del Club América
#            para definir el "ADN" del equipo y perfiles de jugadores
#
# Input:
#   - data/processed/america_events_2024_2025.parquet
#   - data/processed/america_matches_2024_2025.csv
#   - data/processed/america_lineups_2024_2025.parquet
#
# Output:
#   - data/processed/player_metrics_2024_2025.parquet
#   - data/processed/team_aggregates_2024_2025.json
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

print_section("CLUB AMÉRICA PLAYER METRICS CALCULATOR")

cat("📂 Loading data...\n")

# Load events
events <- read_parquet("data/processed/america_events_2024_2025.parquet")
cat(sprintf("   ✓ Events loaded: %s\n", format(nrow(events), big.mark = ",")))

# Load lineups
lineups <- read_parquet("data/processed/america_lineups_2024_2025.parquet")
cat(sprintf("   ✓ Lineups loaded: %s\n", format(nrow(lineups), big.mark = ",")))

# Load matches
matches <- read_csv("data/processed/america_matches_2024_2025.csv", show_col_types = FALSE)
cat(sprintf("   ✓ Matches loaded: %d\n", nrow(matches)))

# ==============================================================================
# STEP 1: LOAD PRE-CALCULATED MINUTES PLAYED
# ==============================================================================

print_section("STEP 1: LOAD MINUTES PLAYED")

cat("⏱️  Loading pre-calculated minutes from script 01...\n\n")

# Load player minutes summary (already calculated in script 01)
player_minutes_raw <- read_parquet("data/processed/america_player_minutes_summary.parquet")

cat(sprintf("   ✓ Loaded minutes for %d América players\n", nrow(player_minutes_raw)))

# Get primary position (position with most minutes) from lineups
cat("   📋 Calculating primary position (position with most minutes)...\n")

# Load player-match minutes to calculate position-specific minutes
america_minutes_by_match <- read_parquet("data/processed/america_minutes_played_2024_2025.parquet")

cat(sprintf("   ✓ Loaded %d player-match records\n", nrow(america_minutes_by_match)))

# Join with lineups to get positions for each match
lineup_positions <- lineups %>%
  filter(str_detect(team_name, "América")) %>%
  select(match_id, player_name, positions)

# Calculate minutes per position for each player
player_position_minutes <- america_minutes_by_match %>%
  left_join(lineup_positions, by = c("match_id", "player.name" = "player_name")) %>%
  mutate(
    # Parse positions JSON and extract primary position
    primary_position = map_chr(positions, function(pos_json) {
      if (is.na(pos_json) || pos_json == "null" || pos_json == "") {
        return(NA_character_)
      }

      tryCatch({
        pos_df <- jsonlite::fromJSON(pos_json)

        # Get first position (starting position)
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
  filter(!is.na(primary_position)) %>%
  select(match_id, player.name, player.id, primary_position, MinutesPlayed)

cat(sprintf("   ✓ Extracted position data from %d player-match records\n",
            length(unique(paste(player_position_minutes$player.name, player_position_minutes$match_id)))))

# Aggregate minutes by player and position
position_summary <- player_position_minutes %>%
  group_by(player.name, primary_position) %>%
  summarise(
    minutes_in_position = sum(MinutesPlayed, na.rm = TRUE),
    matches_in_position = n(),
    .groups = "drop"
  )

# Get primary position (most minutes) for each player
primary_positions <- position_summary %>%
  group_by(player.name) %>%
  arrange(desc(minutes_in_position)) %>%
  slice(1) %>%
  ungroup() %>%
  select(player.name, primary_position, minutes_in_primary = minutes_in_position)

cat(sprintf("   ✓ Calculated primary position for %d players\n", nrow(primary_positions)))

# Join minutes with primary positions
player_minutes <- player_minutes_raw %>%
  left_join(primary_positions, by = "player.name") %>%
  rename(player_name = player.name) %>%
  select(player_name, player.id, matches_played, total_minutes, avg_minutes,
         primary_position, minutes_in_primary, times_subbed_on, times_subbed_off) %>%
  arrange(desc(total_minutes))

cat(sprintf("   ✓ Enriched with positions\n"))

cat("\n   🏆 Top 10 players by total minutes:\n")
player_minutes %>%
  head(10) %>%
  mutate(across(where(is.numeric), ~round(., 1))) %>%
  pwalk(function(player_name, player.id, matches_played, total_minutes, avg_minutes,
                 primary_position, minutes_in_primary, times_subbed_on, times_subbed_off) {
    pos_str <- ifelse(is.na(primary_position), "", sprintf(" [%s]", primary_position))
    pos_pct <- if (!is.na(minutes_in_primary) && total_minutes > 0) {
      sprintf(" (%.0f%% in position)", (minutes_in_primary / total_minutes) * 100)
    } else ""
    sub_str <- if (times_subbed_on > 0 || times_subbed_off > 0) {
      sprintf(" (Sub On:%d Off:%d)", times_subbed_on, times_subbed_off)
    } else ""
    cat(sprintf("      - %s%s%s: %d matches, %.0f total min (%.1f avg)%s\n",
                player_name, pos_str, pos_pct, matches_played, total_minutes, avg_minutes, sub_str))
  })

# ==============================================================================
# STEP 2: FILTER AMÉRICA EVENTS
# ==============================================================================

print_section("STEP 2: FILTER AMÉRICA EVENTS")

america_events <- events %>%
  filter(str_detect(team.name, "América"))

cat(sprintf("📊 América events: %s (%.1f%% of total)\n",
            format(nrow(america_events), big.mark = ","),
            nrow(america_events) / nrow(events) * 100))

# ==============================================================================
# STEP 3: CALCULATE PROGRESSION METRICS
# ==============================================================================

print_section("STEP 3: PROGRESSION METRICS")

cat("🏃 Calculating progressive passes and carries...\n\n")

# Progressive passes: passes that move the ball significantly closer to goal
# Definition: pass that moves the ball at least 10 yards towards goal
progressive_passes <- america_events %>%
  filter(type.name == "Pass") %>%
  mutate(
    # Calculate if pass is progressive
    # Progressive if: moves ball 10+ yards towards goal (higher x value)
    is_progressive = !is.na(location.x) & !is.na(pass.end_location.x) &
      (pass.end_location.x - location.x) >= 10
  ) %>%
  filter(is_progressive) %>%
  count(player.name, name = "progressive_passes")

cat(sprintf("   ✓ Progressive passes calculated for %d players\n",
            nrow(progressive_passes)))

# Progressive carries: dribbles that move ball closer to goal
progressive_carries <- america_events %>%
  filter(type.name == "Carry") %>%
  mutate(
    # Progressive if carries ball 10+ yards towards goal
    is_progressive = !is.na(location.x) & !is.na(carry.end_location.x) &
      (carry.end_location.x - location.x) >= 10
  ) %>%
  filter(is_progressive) %>%
  count(player.name, name = "progressive_carries")

cat(sprintf("   ✓ Progressive carries calculated for %d players\n",
            nrow(progressive_carries)))

# ==============================================================================
# STEP 4: CALCULATE CREATION METRICS
# ==============================================================================

print_section("STEP 4: CREATION METRICS")

cat("🎨 Calculating shot-creating actions and xA...\n\n")

# Shot assists (key passes)
shot_assists <- america_events %>%
  filter(type.name == "Pass", !is.na(pass.shot_assist)) %>%
  count(player.name, name = "shot_assists")

cat(sprintf("   ✓ Shot assists calculated for %d players\n",
            nrow(shot_assists)))

# Goal assists
goal_assists <- america_events %>%
  filter(type.name == "Pass", !is.na(pass.goal_assist)) %>%
  count(player.name, name = "goal_assists")

cat(sprintf("   ✓ Goal assists calculated for %d players\n",
            nrow(goal_assists)))

# Expected Assists (xA) - sum of xG from shots created by passes
cat("   Calculating xA (sum of xG from passes that led to shots)...\n")

# Step 1: Get passes that led to shots (shot assists)
shot_assist_passes <- america_events %>%
  filter(type.name == "Pass", !is.na(pass.shot_assist)) %>%
  arrange(match_id, index) %>%
  select(match_id, index, player.name, pass.recipient.name, id) %>%
  rename(passer = player.name, pass_index = index, pass_id = id)

cat(sprintf("      - Found %d shot-creating passes\n", nrow(shot_assist_passes)))

# Step 2: Get shots with xG
shots_with_xg <- america_events %>%
  filter(type.name == "Shot") %>%
  arrange(match_id, index) %>%
  select(match_id, index, player.name, shot.statsbomb_xg, id) %>%
  rename(shooter = player.name, shot_index = index, shot_id = id)

cat(sprintf("      - Found %d shots with xG data\n", nrow(shots_with_xg)))

# Step 3: Link passes to resulting shots
# The shot should be the next event by the recipient
# Use a more efficient join that avoids many-to-many warnings
xa_data <- shot_assist_passes %>%
  left_join(
    shots_with_xg,
    by = c("match_id" = "match_id", "pass.recipient.name" = "shooter"),
    relationship = "many-to-many"  # Expected: one passer can pass to shooter multiple times
  ) %>%
  # Filter to ensure shot comes after pass and is within next 5 events
  filter(
    !is.na(shot_index),  # Ensure shot exists
    shot_index > pass_index,
    shot_index - pass_index <= 5  # Allow up to 4 events between (e.g., control, carry, dribble, etc.)
  ) %>%
  # If multiple shots after a pass, take the closest one
  group_by(match_id, pass_id) %>%
  arrange(shot_index) %>%
  slice(1) %>%
  ungroup()

cat(sprintf("      - Successfully linked %d passes to shots\n", nrow(xa_data)))

# Step 4: Sum xA per player
xa_stats <- xa_data %>%
  group_by(passer) %>%
  summarise(
    xA = sum(shot.statsbomb_xg, na.rm = TRUE),
    key_passes = n(),  # Count of passes that led to shots
    .groups = "drop"
  ) %>%
  rename(player.name = passer)

cat(sprintf("   ✓ xA calculated for %d players\n", nrow(xa_stats)))
cat(sprintf("      - Total xA across all players: %.2f\n",
            sum(xa_stats$xA, na.rm = TRUE)))

# ==============================================================================
# STEP 5: CALCULATE FINISHING METRICS
# ==============================================================================

print_section("STEP 5: FINISHING METRICS")

cat("⚽ Calculating xG and shots...\n\n")

# Shots and xG
shots_stats <- america_events %>%
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

cat(sprintf("   ✓ Shot statistics calculated for %d players\n",
            nrow(shots_stats)))

# ==============================================================================
# STEP 6: CALCULATE DEFENSIVE METRICS
# ==============================================================================

print_section("STEP 6: DEFENSIVE METRICS")

cat("🛡️  Calculating tackles, interceptions, and pressures...\n\n")

# Tackles
tackles <- america_events %>%
  filter(type.name == "Duel", !is.na(duel.type.name),
         str_detect(duel.type.name, "Tackle")) %>%
  group_by(player.name) %>%
  summarise(
    tackles = n(),
    tackles_won = sum(!is.na(duel.outcome.name) &
                      duel.outcome.name == "Won", na.rm = TRUE),
    .groups = "drop"
  )

cat(sprintf("   ✓ Tackles calculated for %d players\n", nrow(tackles)))

# Interceptions
interceptions <- america_events %>%
  filter(type.name == "Interception") %>%
  count(player.name, name = "interceptions")

cat(sprintf("   ✓ Interceptions calculated for %d players\n",
            nrow(interceptions)))

# Pressures
pressures <- america_events %>%
  filter(type.name == "Pressure") %>%
  count(player.name, name = "pressures")

cat(sprintf("   ✓ Pressures calculated for %d players\n",
            nrow(pressures)))

# Ball recoveries
recoveries <- america_events %>%
  filter(type.name == "Ball Recovery") %>%
  count(player.name, name = "ball_recoveries")

cat(sprintf("   ✓ Ball recoveries calculated for %d players\n",
            nrow(recoveries)))

# ==============================================================================
# STEP 7: CALCULATE POSSESSION METRICS
# ==============================================================================

print_section("STEP 7: POSSESSION METRICS")

cat("🎯 Calculating pass completion and touches...\n\n")

# Pass completion
pass_stats <- america_events %>%
  filter(type.name == "Pass") %>%
  group_by(player.name) %>%
  summarise(
    passes = n(),
    passes_completed = sum(is.na(pass.outcome.name), na.rm = TRUE),
    pass_completion_pct = passes_completed / passes * 100,
    .groups = "drop"
  )

cat(sprintf("   ✓ Pass statistics calculated for %d players\n",
            nrow(pass_stats)))

# Touches in attacking third (x > 80)
touches_att_third <- america_events %>%
  filter(!is.na(location.x), location.x >= 80) %>%
  count(player.name, name = "touches_att_third")

cat(sprintf("   ✓ Touches in attacking third calculated for %d players\n",
            nrow(touches_att_third)))

# Touches in box (x >= 102, y between 18 and 62)
touches_in_box <- america_events %>%
  filter(!is.na(location.x), !is.na(location.y),
         location.x >= 102, location.y >= 18, location.y <= 62) %>%
  count(player.name, name = "touches_in_box")

cat(sprintf("   ✓ Touches in box calculated for %d players\n",
            nrow(touches_in_box)))

# ==============================================================================
# STEP 8: CALCULATE DRIBBLING METRICS
# ==============================================================================

print_section("STEP 8: DRIBBLING METRICS")

cat("🎨 Calculating dribbles and take-ons...\n\n")

# Dribbles (take-ons / 1v1 situations)
dribbles <- america_events %>%
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

cat(sprintf("   ✓ Dribble statistics calculated for %d players\n",
            nrow(dribbles)))
cat(sprintf("      - Total dribble attempts: %d\n", sum(dribbles$dribbles)))
cat(sprintf("      - Successful dribbles: %d (%.1f%%)\n",
            sum(dribbles$dribbles_successful),
            sum(dribbles$dribbles_successful) / sum(dribbles$dribbles) * 100))

cat("\n   ℹ️  Note: Progressive carries are calculated in STEP 3\n")

# ==============================================================================
# STEP 9: COMBINE ALL METRICS
# ==============================================================================

print_section("STEP 9: COMBINE AND NORMALIZE METRICS")

cat("🔗 Combining all metrics into single dataframe...\n")

# Start with player minutes as base
player_metrics <- player_minutes

# Join all metrics
player_metrics <- player_metrics %>%
  left_join(progressive_passes, by = c("player_name" = "player.name")) %>%
  left_join(progressive_carries, by = c("player_name" = "player.name")) %>%
  left_join(shot_assists, by = c("player_name" = "player.name")) %>%
  left_join(goal_assists, by = c("player_name" = "player.name")) %>%
  left_join(xa_stats, by = c("player_name" = "player.name")) %>%
  left_join(shots_stats, by = c("player_name" = "player.name")) %>%
  left_join(tackles, by = c("player_name" = "player.name")) %>%
  left_join(interceptions, by = c("player_name" = "player.name")) %>%
  left_join(pressures, by = c("player_name" = "player.name")) %>%
  left_join(recoveries, by = c("player_name" = "player.name")) %>%
  left_join(pass_stats, by = c("player_name" = "player.name")) %>%
  left_join(touches_att_third, by = c("player_name" = "player.name")) %>%
  left_join(touches_in_box, by = c("player_name" = "player.name")) %>%
  left_join(dribbles, by = c("player_name" = "player.name"))

# Replace NAs with 0 for count metrics (but NOT percentages or xA/xG)
player_metrics <- player_metrics %>%
  mutate(across(c(progressive_passes, progressive_carries, shot_assists,
                  goal_assists, key_passes, shots, goals, tackles,
                  interceptions, pressures, ball_recoveries, passes,
                  touches_att_third, touches_in_box, dribbles, dribbles_successful,
                  dribbles_failed),
                ~replace_na(., 0))) %>%
  # For xA and xG, keep NA as 0 but preserve the decimal values
  mutate(
    xA = replace_na(xA, 0),
    xG = replace_na(xG, 0)
  )

cat(sprintf("   ✓ Combined metrics for %d players\n", nrow(player_metrics)))

# Normalize to per 90 minutes
cat("\n📊 Normalizing metrics per 90 minutes...\n")

player_metrics <- player_metrics %>%
  mutate(
    # Per 90 metrics
    progressive_passes_p90 = progressive_passes / total_minutes * 90,
    progressive_carries_p90 = progressive_carries / total_minutes * 90,
    shot_assists_p90 = shot_assists / total_minutes * 90,
    key_passes_p90 = key_passes / total_minutes * 90,
    xA_p90 = xA / total_minutes * 90,  # Expected assists per 90
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

cat("   ✓ Normalized all count metrics to per-90 rates\n")

# Filter players with minimum minutes (e.g., 270 minutes = 3 full games)
min_minutes <- 900

player_metrics_filtered <- player_metrics %>%
  filter(total_minutes >= min_minutes) %>%
  arrange(desc(total_minutes))

cat(sprintf("\n   ✓ Filtered to players with %d+ minutes: %d players\n",
            min_minutes, nrow(player_metrics_filtered)))

# ==============================================================================
# STEP 10: SAVE RESULTS
# ==============================================================================

print_section("STEP 10: SAVE PLAYER METRICS")

# Save as Parquet
output_file <- "data/processed/player_metrics_2024_2025.parquet"
write_parquet(player_metrics_filtered, output_file)
cat(sprintf("💾 Saved to: %s\n", output_file))
cat(sprintf("   File size: %.1f KB\n", file.info(output_file)$size / 1024))

# Also save full metrics (unfiltered) for reference
output_file_full <- "data/processed/player_metrics_2024_2025_full.parquet"
write_parquet(player_metrics, output_file_full)
cat(sprintf("💾 Saved full dataset to: %s\n", output_file_full))

# ==============================================================================
# STEP 11: CALCULATE TEAM AGGREGATES
# ==============================================================================

print_section("STEP 11: TEAM AGGREGATES")

cat("🦅 Calculating Club América team-level statistics...\n\n")

team_aggregates <- list(
  # Progression
  avg_progressive_passes_p90 = mean(player_metrics_filtered$progressive_passes_p90, na.rm = TRUE),
  avg_progressive_carries_p90 = mean(player_metrics_filtered$progressive_carries_p90, na.rm = TRUE),

  # Creation
  avg_shot_assists_p90 = mean(player_metrics_filtered$shot_assists_p90, na.rm = TRUE),
  avg_key_passes_p90 = mean(player_metrics_filtered$key_passes_p90, na.rm = TRUE),
  avg_xA_p90 = mean(player_metrics_filtered$xA_p90, na.rm = TRUE),  # Expected assists

  # Finishing
  avg_shots_p90 = mean(player_metrics_filtered$shots_p90, na.rm = TRUE),
  avg_xG_p90 = mean(player_metrics_filtered$xG_p90, na.rm = TRUE),

  # Defense
  avg_tackles_p90 = mean(player_metrics_filtered$tackles_p90, na.rm = TRUE),
  avg_interceptions_p90 = mean(player_metrics_filtered$interceptions_p90, na.rm = TRUE),
  avg_pressures_p90 = mean(player_metrics_filtered$pressures_p90, na.rm = TRUE),

  # Possession
  avg_pass_completion_pct = mean(player_metrics_filtered$pass_completion_pct, na.rm = TRUE),
  avg_touches_att_third_p90 = mean(player_metrics_filtered$touches_att_third_p90, na.rm = TRUE),

  # Dribbling
  avg_dribbles_p90 = mean(player_metrics_filtered$dribbles_p90, na.rm = TRUE),
  avg_dribbles_successful_p90 = mean(player_metrics_filtered$dribbles_successful_p90, na.rm = TRUE),
  avg_dribble_success_pct = mean(player_metrics_filtered$dribble_success_pct, na.rm = TRUE),

  # Meta
  total_players = nrow(player_metrics_filtered),
  total_matches = nrow(matches),
  season = "2024/2025"
)

# Save as JSON
team_file <- "data/processed/team_aggregates_2024_2025.json"
write_json(team_aggregates, team_file, pretty = TRUE, auto_unbox = TRUE)
cat(sprintf("💾 Team aggregates saved to: %s\n", team_file))

# ==============================================================================
# SUMMARY
# ==============================================================================

print_section("SUMMARY")

cat("✅ Player metrics calculated successfully!\n\n")

cat("📊 Metrics Calculated (per player):\n")
cat("   • Progression: Progressive passes & carries (per 90)\n")
cat("   • Creation: Shot assists, key passes, xA (per 90) ⭐\n")
cat("   • Finishing: Shots, goals, xG (per 90)\n")
cat("   • Defense: Tackles, interceptions, pressures (per 90)\n")
cat("   • Possession: Pass completion %, touches in box\n")
cat("   • Dribbling: Dribbles, successful dribbles, success rate (per 90) ⭐\n")
cat("\n   ⭐ xA = Expected Assists (sum of xG from shots created)\n")
cat("   ⭐ Dribbles = Take-ons / 1v1 situations (desequilibrio individual)\n")

cat(sprintf("\n📈 Players analyzed: %d (with %d+ minutes)\n",
            nrow(player_metrics_filtered), min_minutes))

cat("\n🏆 Top 5 Players by Total Minutes:\n")
player_metrics_filtered %>%
  select(player_name, matches_played, total_minutes) %>%
  head(5) %>%
  mutate(rank = row_number()) %>%
  pwalk(function(player_name, matches_played, total_minutes, rank) {
    cat(sprintf("   %d. %s: %d matches, %.0f minutes\n",
                rank, player_name, matches_played, total_minutes))
  })

cat("\n📁 Files created:\n")
cat(sprintf("   ✓ %s\n", output_file))
cat(sprintf("   ✓ %s\n", output_file_full))
cat(sprintf("   ✓ %s\n", team_file))

cat("\n🎯 Next Steps:\n")
cat("   1. Run 03_define_america_dna.R to calculate tactical DNA\n")
cat("   2. Explore player metrics with visualization\n")
cat("   3. Build player comparison and recommendation system\n")

cat("\n💡 Quick load:\n")
cat("   library(arrow)\n")
cat("   metrics <- read_parquet('data/processed/player_metrics_2024_2025.parquet')\n")
cat("   glimpse(metrics)\n")

cat("\n")
cat(paste(rep("=", 80), collapse = ""), "\n\n")
