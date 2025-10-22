#!/usr/bin/env Rscript
# ==============================================================================
# FETCH CLUB AMÉRICA DNA DATA - ÚLTIMA TEMPORADA (2024/2025)
# ==============================================================================
#
# Propósito: Obtener TODOS los datos necesarios para calcular el "ADN" del
#            Club América, enfocándonos solo en la temporada 2024/2025
#
# Output:
#   - data/processed/america_events_2024_2025.parquet (eventos limpios)
#   - data/processed/america_matches_2024_2025.csv (partidos)
#   - data/processed/america_lineups_2024_2025.parquet (alineaciones)
#   - data/processed/america_events_360_2024_2025.parquet (datos 360)
#
# ==============================================================================

# Load required libraries
suppressPackageStartupMessages({
  library(StatsBombR)
  library(tidyverse)
  library(lubridate)
  library(arrow)  # For Parquet format (R + Python compatible)
  library(httr)   # For HTTP timeout configuration
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

print_section("CLUB AMÉRICA DNA DATA PIPELINE - TEMPORADA 2024/2025")

# Credentials
cat("🔐 Setting up authentication...\n")

# Load credentials from external file
credentials_file <- ".statsbomb_credentials"

if (!file.exists(credentials_file)) {
  stop(paste0(
    "❌ Credentials file not found: ", credentials_file, "\n",
    "   Please create it using .statsbomb_credentials.example as template\n",
    "   Instructions:\n",
    "   1. Copy .statsbomb_credentials.example to .statsbomb_credentials\n",
    "   2. Add your real credentials\n"
  ))
}

# Read credentials
cred_lines <- readLines(credentials_file)
cred_lines <- cred_lines[!grepl("^#", cred_lines) & nchar(trimws(cred_lines)) > 0]

username <- sub("username=", "", cred_lines[grepl("^username=", cred_lines)])
password <- sub("password=", "", cred_lines[grepl("^password=", cred_lines)])

if (length(username) == 0 || length(password) == 0) {
  stop("❌ Invalid credentials file format. Check .statsbomb_credentials.example")
}

cat("   ✓ Credentials loaded from file\n")

# Create directories
cat("\n📁 Creating output directories...\n")
dir.create("data/processed", recursive = TRUE, showWarnings = FALSE)
cat("   ✓ data/processed/ ready\n")

# ==============================================================================
# STEP 1: GET LATEST SEASON MATCHES
# ==============================================================================

print_section("STEP 1: FETCH MATCHES (2024/2025)")

cat("📊 Fetching competitions...\n")
competitions <- competitions(username, password)

# Filter for Liga MX 2024/2025 (latest season)
liga_mx_latest <- competitions %>%
  filter(
    str_detect(competition_name, regex("Liga MX", ignore_case = TRUE)),
    season_name == "2024/2025"
  )

if (nrow(liga_mx_latest) == 0) {
  stop("❌ No se encontró la temporada 2024/2025 de Liga MX")
}

cat(sprintf("   ✓ Found season: %s\n", liga_mx_latest$season_name))
cat(sprintf("   • Competition ID: %d\n", liga_mx_latest$competition_id))
cat(sprintf("   • Season ID: %d\n", liga_mx_latest$season_id))

# Get all matches
cat("\n⚽ Fetching all matches for 2024/2025...\n")
all_matches <- get.matches(
  username = username,
  password = password,
  season_id = liga_mx_latest$season_id,
  competition_id = liga_mx_latest$competition_id
)

cat(sprintf("   ✓ Total matches in season: %d\n", nrow(all_matches)))

# Filter Club América matches
cat("\n🦅 Filtering Club América matches...\n")
america_matches <- all_matches %>%
  filter(
    str_detect(home_team.home_team_name, regex("América", ignore_case = TRUE)) |
    str_detect(away_team.away_team_name, regex("América", ignore_case = TRUE))
  )

cat(sprintf("   ✓ Club América matches found: %d\n", nrow(america_matches)))

# Show basic stats
cat("\n📈 Match Statistics:\n")
cat(sprintf("   • Home games: %d\n",
            sum(str_detect(america_matches$home_team.home_team_name, "América"))))
cat(sprintf("   • Away games: %d\n",
            sum(str_detect(america_matches$away_team.away_team_name, "América"))))

# Calculate results
america_matches <- america_matches %>%
  mutate(
    is_home = str_detect(home_team.home_team_name, regex("América", ignore_case = TRUE)),
    america_goals = if_else(is_home, home_score, away_score),
    opponent_goals = if_else(is_home, away_score, home_score),
    result = case_when(
      america_goals > opponent_goals ~ "Win",
      america_goals < opponent_goals ~ "Loss",
      TRUE ~ "Draw"
    )
  )

result_summary <- america_matches %>%
  count(result) %>%
  mutate(pct = n / sum(n) * 100)

cat("\n   Results breakdown:\n")
result_summary %>%
  pwalk(function(result, n, pct) {
    cat(sprintf("      - %s: %d (%.1f%%)\n", result, n, pct))
  })

# Save matches
matches_file <- "data/processed/america_matches_2024_2025.csv"
write_csv(america_matches, matches_file)
cat(sprintf("\n   💾 Saved to: %s\n", matches_file))

# ==============================================================================
# STEP 2: GET ALL EVENTS
# ==============================================================================

print_section("STEP 2: FETCH ALL EVENTS")

cat(sprintf("📥 Downloading events for %d matches...\n", nrow(america_matches)))
cat("   ⏳ This may take 5-15 minutes...\n")
cat("   💡 Downloading in batches to avoid timeouts...\n\n")

# Get all events (using allevents for multiple matches)
match_ids <- america_matches$match_id

# Download in batches to avoid timeout
batch_size <- 5  # Download 5 matches at a time
n_batches <- ceiling(length(match_ids) / batch_size)

all_events_list <- list()

cat(sprintf("   Downloading %d batches of %d matches each...\n\n", n_batches, batch_size))

for (i in 1:n_batches) {
  start_idx <- (i - 1) * batch_size + 1
  end_idx <- min(i * batch_size, length(match_ids))
  batch_ids <- match_ids[start_idx:end_idx]

  cat(sprintf("   📦 Batch %d/%d: Matches %d-%d... ",
              i, n_batches, start_idx, end_idx))

  tryCatch({
    # Increase timeout to 10 minutes per batch
    httr::set_config(httr::timeout(600))

    batch_events <- allevents(
      username = username,
      password = password,
      matches = batch_ids,
      parallel = FALSE
    )

    all_events_list[[i]] <- batch_events
    cat(sprintf("✓ (%s events)\n", format(nrow(batch_events), big.mark = ",")))

    # Small pause between batches to be nice to the server
    if (i < n_batches) {
      Sys.sleep(2)
    }

  }, error = function(e) {
    cat(sprintf("❌ Error: %s\n", conditionMessage(e)))
    cat("   Continuing with next batch...\n")
  })
}

# Combine all batches
cat("\n   🔗 Combining all batches...\n")
all_events <- bind_rows(all_events_list)

cat(sprintf("\n   ✓ Downloaded events from %d matches\n", length(unique(all_events$match_id))))
cat(sprintf("   ✓ Total events: %s\n", format(nrow(all_events), big.mark = ",")))

# Show event type distribution
cat("\n   Top 10 event types:\n")
all_events %>%
  count(type.name, sort = TRUE) %>%
  head(10) %>%
  pwalk(function(type.name, n) {
    pct <- n / nrow(all_events) * 100
    cat(sprintf("      - %s: %s (%.1f%%)\n",
                type.name,
                format(n, big.mark = ","),
                pct))
  })

# ==============================================================================
# STEP 3: CLEAN EVENTS DATA
# ==============================================================================

print_section("STEP 3: CLEAN AND ENRICH EVENTS")

cat("🧹 Cleaning events with allclean()...\n")
cat("   This function:\n")
cat("   • Cleans location coordinates (x, y)\n")
cat("   • Extracts goalkeeper info\n")
cat("   • Processes shot data\n")
cat("   • Formats freeze frames (360 data)\n")
cat("   • Adds elapsed time\n")
cat("   • Calculates possession info\n\n")

events_clean <- allclean(all_events)

cat("   ✓ Events cleaned successfully\n")
cat(sprintf("   ✓ New columns added: %d\n",
            ncol(events_clean) - ncol(all_events)))

# Check for key columns
key_columns <- c("location.x", "location.y", "minute", "second",
                 "obv_total_net", "ElapsedTime")
present_cols <- key_columns[key_columns %in% names(events_clean)]
cat(sprintf("   ✓ Key columns present: %d/%d\n",
            length(present_cols), length(key_columns)))

# ==============================================================================
# TEST: Calculate minutes played BEFORE saving to Parquet
# ==============================================================================

print_section("TEST: get.minutesplayed() on fresh data")

cat("🧪 Testing get.minutesplayed() BEFORE Parquet conversion...\n\n")

cat("   Step 1: Format elapsed time...\n")
events_for_minutes <- formatelapsedtime(events_clean)
cat(sprintf("   ✓ ElapsedTime column: %s\n", "ElapsedTime" %in% names(events_for_minutes)))

cat("\n   Step 2: Call get.minutesplayed()...\n")
tryCatch({
  minutes_played_raw <- get.minutesplayed(events_for_minutes)

  cat(sprintf("   ✅ SUCCESS! get.minutesplayed() works on fresh data!\n"))
  cat(sprintf("   ✓ Calculated minutes for %d player-match records\n", nrow(minutes_played_raw)))

  # Note: get.minutesplayed() returns player.id and team.id, not names
  # We'll enrich this with names from lineups later
  cat("   ℹ️  Columns: player.id, team.id, match_id, TimeOn, TimeOff, GameEnd, MinutesPlayed\n")

  # Save raw minutes (we'll enrich with names after loading lineups)
  cat("\n   💾 Saving raw minutes played data...\n")
  write_parquet(minutes_played_raw, "data/processed/minutes_played_raw.parquet")
  cat("   ✓ Saved to: data/processed/minutes_played_raw.parquet\n")

}, error = function(e) {
  cat(sprintf("   ❌ FAILED! Error: %s\n", e$message))
  cat("\n   This means the problem is NOT with Parquet conversion.\n")
  cat("   The issue is with the data structure itself.\n\n")
  traceback()
})

cat("\n")

# Save cleaned events as Parquet (R + Python compatible)
cat("\n💾 Saving events to Parquet format...\n")
events_file <- "data/processed/america_events_2024_2025.parquet"

# Parquet doesn't support list columns, so we need to handle them
# Check for list columns and convert them
list_cols <- names(events_clean)[sapply(events_clean, is.list)]
cat(sprintf("   ℹ️  Found %d list columns to handle\n", length(list_cols)))

# Convert list columns to JSON strings for Parquet compatibility
events_for_parquet <- events_clean
for (col in list_cols) {
  # Skip if it's a simple list that's already been flattened (like location.x, location.y)
  if (!str_detect(col, "\\.(x|y|z)$")) {
    cat(sprintf("   • Converting %s to JSON\n", col))
    events_for_parquet[[col]] <- map_chr(events_for_parquet[[col]],
                                          ~ifelse(is.null(.x) || all(is.na(.x)),
                                                  NA_character_,
                                                  jsonlite::toJSON(.x, auto_unbox = TRUE)))
  }
}

write_parquet(events_for_parquet, events_file)
cat(sprintf("   ✓ Saved to: %s\n", events_file))
cat(sprintf("   ✓ File size: %.1f MB\n", file.info(events_file)$size / 1024^2))

# Also save as CSV (subset for inspection)
events_csv <- "data/processed/america_events_2024_2025_sample.csv"
events_clean %>%
  select(match_id, minute, second, type.name, team.name, player.name,
         location.x, location.y, obv_total_net) %>%
  head(1000) %>%
  write_csv(events_csv)
cat(sprintf("   💾 Sample CSV saved to: %s\n", events_csv))

# ==============================================================================
# STEP 4: GET LINEUPS
# ==============================================================================

print_section("STEP 4: FETCH LINEUPS")

cat(sprintf("👥 Fetching lineups for %d matches...\n", nrow(america_matches)))
cat("   💡 Downloading one match at a time (more reliable)...\n\n")

# Download lineups one match at a time (more reliable than alllineups)
all_lineups_list <- list()
successful_downloads <- 0
failed_downloads <- 0

for (i in 1:length(match_ids)) {
  match_id <- match_ids[i]

  cat(sprintf("   📦 Match %d/%d (ID: %d)... ", i, length(match_ids), match_id))

  tryCatch({
    httr::set_config(httr::timeout(60))  # 60 seconds per match

    lineup <- get.lineups(
      username = username,
      password = password,
      match_id = match_id
    )

    all_lineups_list[[i]] <- lineup
    successful_downloads <- successful_downloads + 1
    cat("✓\n")

    # Small pause to be nice to the server
    if (i %% 10 == 0) {
      cat("   ⏸️  Brief pause...\n")
      Sys.sleep(2)
    } else {
      Sys.sleep(0.5)
    }

  }, error = function(e) {
    failed_downloads <- failed_downloads + 1
    cat(sprintf("❌ Error: %s\n", conditionMessage(e)))
  })
}

# Combine all lineups
cat("\n   🔗 Combining all lineups...\n")
all_lineups <- bind_rows(all_lineups_list)

cat(sprintf("   ✓ Successfully downloaded: %d/%d matches\n",
            successful_downloads, length(match_ids)))
if (failed_downloads > 0) {
  cat(sprintf("   ⚠️  Failed downloads: %d\n", failed_downloads))
}
cat(sprintf("   ✓ Total lineup records: %d\n", nrow(all_lineups)))

# Clean lineups
cat("\n🧹 Cleaning lineups...\n")
lineups_clean <- cleanlineups(all_lineups)

cat(sprintf("   ✓ Total player-match records: %d\n", nrow(lineups_clean)))

# Show América players
america_players <- lineups_clean %>%
  filter(str_detect(team_name, "América")) %>%
  distinct(player_name, player_nickname) %>%
  arrange(player_name)

cat(sprintf("\n   📋 Club América players in this season: %d\n", nrow(america_players)))
cat("   Top 10 players (alphabetically):\n")
america_players %>%
  head(10) %>%
  pwalk(function(player_name, player_nickname) {
    nickname_str <- if_else(is.na(player_nickname), "",
                           sprintf(" (%s)", player_nickname))
    cat(sprintf("      - %s%s\n", player_name, nickname_str))
  })

# Save lineups as Parquet
lineups_file <- "data/processed/america_lineups_2024_2025.parquet"

# Handle list columns in lineups if any
lineups_list_cols <- names(lineups_clean)[sapply(lineups_clean, is.list)]
lineups_for_parquet <- lineups_clean

if (length(lineups_list_cols) > 0) {
  cat("\n   Converting list columns to JSON for Parquet...\n")
  for (col in lineups_list_cols) {
    cat(sprintf("   • %s\n", col))
    lineups_for_parquet[[col]] <- map_chr(lineups_for_parquet[[col]],
                                           ~ifelse(is.null(.x) || all(is.na(.x)),
                                                   NA_character_,
                                                   jsonlite::toJSON(.x, auto_unbox = TRUE)))
  }
}

write_parquet(lineups_for_parquet, lineups_file)
cat(sprintf("\n   💾 Saved to: %s\n", lineups_file))
cat(sprintf("   ✓ File size: %.1f MB\n", file.info(lineups_file)$size / 1024^2))

# ==============================================================================
# STEP 4B: ENRICH MINUTES PLAYED WITH PLAYER NAMES
# ==============================================================================

print_section("STEP 4B: ENRICH MINUTES PLAYED DATA")

cat("🔗 Enriching minutes played with player and team names...\n\n")

# Load raw minutes
minutes_played_raw <- read_parquet("data/processed/minutes_played_raw.parquet")
cat(sprintf("   ✓ Loaded raw minutes: %d player-match records\n", nrow(minutes_played_raw)))

# Get player names from events (player.id -> player.name)
player_id_to_name <- events_clean %>%
  filter(!is.na(player.id) & !is.na(player.name)) %>%
  distinct(player.id, player.name)

cat(sprintf("   ✓ Player ID mapping: %d unique players\n", nrow(player_id_to_name)))

# Get team names from events (team.id -> team.name)
team_id_to_name <- events_clean %>%
  filter(!is.na(team.id) & !is.na(team.name)) %>%
  distinct(team.id, team.name)

cat(sprintf("   ✓ Team ID mapping: %d unique teams\n", nrow(team_id_to_name)))

# Enrich minutes with names
minutes_played_enriched <- minutes_played_raw %>%
  left_join(player_id_to_name, by = "player.id") %>%
  left_join(team_id_to_name, by = "team.id") %>%
  select(match_id, player.id, player.name, team.id, team.name,
         TimeOn, TimeOff, GameEnd, MinutesPlayed)

cat(sprintf("   ✓ Enriched with names: %d records\n", nrow(minutes_played_enriched)))

# Filter only América players
america_minutes_played <- minutes_played_enriched %>%
  filter(str_detect(team.name, "América"))

cat(sprintf("   ✓ Filtered to América: %d player-match records\n", nrow(america_minutes_played)))

# Show top 10 by minutes
cat("\n   🏆 Top 10 América players by minutes (single match):\n")
america_minutes_played %>%
  arrange(desc(MinutesPlayed)) %>%
  head(10) %>%
  pwalk(function(match_id, player.id, player.name, team.id, team.name,
                 TimeOn, TimeOff, GameEnd, MinutesPlayed) {
    cat(sprintf("      - %s: %.1f min (match %d)\n",
                player.name, MinutesPlayed, match_id))
  })

# Save enriched minutes
minutes_file <- "data/processed/america_minutes_played_2024_2025.parquet"
write_parquet(america_minutes_played, minutes_file)
cat(sprintf("\n   💾 Saved to: %s\n", minutes_file))
cat(sprintf("   ✓ File size: %.1f KB\n", file.info(minutes_file)$size / 1024))

# Also create aggregated minutes per player
player_total_minutes <- america_minutes_played %>%
  group_by(player.id, player.name) %>%
  summarise(
    matches_played = n(),
    total_minutes = sum(MinutesPlayed, na.rm = TRUE),
    avg_minutes = mean(MinutesPlayed, na.rm = TRUE),
    times_subbed_on = sum(TimeOn > 0, na.rm = TRUE),
    times_subbed_off = sum(TimeOff < GameEnd, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  arrange(desc(total_minutes))

cat("\n   📊 Summary: Minutes aggregated by player\n")
cat(sprintf("   ✓ Total América players: %d\n", nrow(player_total_minutes)))
cat("\n   🏆 Top 10 by total minutes:\n")
player_total_minutes %>%
  head(10) %>%
  pwalk(function(player.id, player.name, matches_played, total_minutes,
                 avg_minutes, times_subbed_on, times_subbed_off) {
    cat(sprintf("      - %s: %d matches, %.0f min total (%.1f avg)\n",
                player.name, matches_played, total_minutes, avg_minutes))
  })

# Save aggregated minutes
player_minutes_file <- "data/processed/america_player_minutes_summary.parquet"
write_parquet(player_total_minutes, player_minutes_file)
cat(sprintf("\n   💾 Saved summary to: %s\n", player_minutes_file))

# ==============================================================================
# STEP 5: GET 360 DATA (OPTIONAL - IF AVAILABLE)
# ==============================================================================

print_section("STEP 5: FETCH 360 DATA (TACTICAL CONTEXT)")

# Check if 360 data is available
has_360 <- america_matches %>%
  filter(match_status_360 == "available") %>%
  nrow()

cat(sprintf("📍 Matches with 360 data available: %d/%d\n",
            has_360, nrow(america_matches)))

if (has_360 > 0) {
  cat("\n⏳ Downloading 360 data (this may take a while)...\n")

  # Get first match with 360 data as sample
  sample_360_match <- america_matches %>%
    filter(match_status_360 == "available") %>%
    slice(1) %>%
    pull(match_id)

  cat(sprintf("   Fetching 360 data for match ID: %d (sample)\n", sample_360_match))

  tryCatch({
    events_360_sample <- get_events_360(
      username = username,
      password = password,
      match_id = sample_360_match
    )

    cat(sprintf("   ✓ 360 data points retrieved: %s\n",
                format(nrow(events_360_sample), big.mark = ",")))
    cat("\n   360 data columns:\n")
    cat(sprintf("      - teammate (bool): Is teammate?\n"))
    cat(sprintf("      - actor (bool): Is the player performing action?\n"))
    cat(sprintf("      - keeper (bool): Is goalkeeper?\n"))
    cat(sprintf("      - x, y: Player positions (0-120, 0-80)\n"))
    cat(sprintf("      - match_id, id: Event identifiers\n"))

    # Save sample 360 data as Parquet
    events_360_file <- "data/processed/america_events_360_sample.parquet"
    write_parquet(events_360_sample, events_360_file)
    cat(sprintf("\n   💾 Sample saved to: %s\n", events_360_file))
    cat(sprintf("   ✓ File size: %.1f MB\n", file.info(events_360_file)$size / 1024^2))

    cat("\n   ℹ️  To get ALL 360 data, uncomment the loop in this script\n")

    # UNCOMMENT BELOW TO GET ALL 360 DATA (TAKES LONGER)
    # matches_360 <- america_matches %>%
    #   filter(match_status_360 == "available") %>%
    #   pull(match_id)
    #
    # all_360 <- map_dfr(matches_360, function(mid) {
    #   cat(sprintf("   Fetching 360 for match %d...\n", mid))
    #   get_events_360(username, password, mid)
    # })
    #
    # write_parquet(all_360, "data/processed/america_events_360_2024_2025.parquet")

  }, error = function(e) {
    cat(sprintf("   ⚠️  Error fetching 360 data: %s\n", e$message))
    cat("   Continuing without 360 data...\n")
  })
} else {
  cat("   ℹ️  No 360 data available for this season\n")
}

# ==============================================================================
# SUMMARY
# ==============================================================================

print_section("PIPELINE COMPLETE - SUMMARY")

cat("✅ All data successfully downloaded and processed!\n\n")

cat("📊 Data Overview:\n")
cat(sprintf("   • Season: %s\n", liga_mx_latest$season_name))
cat(sprintf("   • Club América matches: %d\n", nrow(america_matches)))
cat(sprintf("   • Total events: %s\n", format(nrow(events_clean), big.mark = ",")))
cat(sprintf("   • Total players: %d\n", nrow(america_players)))
cat(sprintf("   • Matches with 360 data: %d\n", has_360))

cat("\n📁 Files saved:\n")
cat(sprintf("   ✓ %s (matches metadata)\n", matches_file))
cat(sprintf("   ✓ %s (all events)\n", events_file))
cat(sprintf("   ✓ %s (events sample)\n", events_csv))
cat(sprintf("   ✓ %s (lineups)\n", lineups_file))
cat(sprintf("   ✓ %s (player-match minutes) ⭐NEW\n", minutes_file))
cat(sprintf("   ✓ %s (player totals) ⭐NEW\n", player_minutes_file))
if (has_360 > 0 && exists("events_360_sample")) {
  cat(sprintf("   ✓ %s (360 sample)\n", events_360_file))
}

cat("\n🎯 Next Steps:\n")
cat("   1. Run 02_calculate_player_metrics.R to compute per-player stats\n")
cat("   2. Run 03_define_america_dna.R to calculate team DNA profile\n")
cat("   3. Build FitScore model for player recommendations\n")

cat("\n💡 Quick load in R:\n")
cat("   library(arrow); library(tidyverse)\n")
cat("   events <- read_parquet('data/processed/america_events_2024_2025.parquet')\n")
cat("   matches <- read_csv('data/processed/america_matches_2024_2025.csv')\n")
cat("   lineups <- read_parquet('data/processed/america_lineups_2024_2025.parquet')\n")
cat("   minutes <- read_parquet('data/processed/america_player_minutes_summary.parquet')\n")

cat("\n🐍 Quick load in Python:\n")
cat("   import pandas as pd\n")
cat("   events = pd.read_parquet('data/processed/america_events_2024_2025.parquet')\n")
cat("   matches = pd.read_csv('data/processed/america_matches_2024_2025.csv')\n")
cat("   lineups = pd.read_parquet('data/processed/america_lineups_2024_2025.parquet')\n")
cat("   minutes = pd.read_parquet('data/processed/america_player_minutes_summary.parquet')\n")

cat("\n")
cat(paste(rep("=", 80), collapse = ""), "\n\n")
