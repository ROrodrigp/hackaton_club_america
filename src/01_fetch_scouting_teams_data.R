#!/usr/bin/env Rscript
# ==============================================================================
# FETCH SCOUTING TEAMS DATA - TEMPORADA 2024/2025
# ==============================================================================
#
# Propósito: Obtener datos de 18 equipos de Liga MX para scouting (SIN América)
#            Todos los equipos de Liga MX Apertura 2024 excepto Club América
#            Los datos se guardan PARTICIONADOS por equipo
#
# Output structure:
#   data/processed/
#     ├── toluca/
#     │   ├── events.parquet
#     │   ├── matches.csv
#     │   ├── lineups.parquet
#     │   └── minutes_played.parquet
#     ├── guadalajara/
#     ├── monterrey/
#     └── mazatlan/
#
# ==============================================================================

# Load required libraries
suppressPackageStartupMessages({
  library(StatsBombR)
  library(tidyverse)
  library(lubridate)
  library(arrow)
  library(httr)
})

# Helper function to print section headers
print_section <- function(title) {
  cat("\n")
  cat(paste(rep("=", 80), collapse = ""), "\n")
  cat(sprintf("  %s\n", title))
  cat(paste(rep("=", 80), collapse = ""), "\n\n")
}

# Helper function to normalize team names for directories
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

print_section("SCOUTING TEAMS DATA PIPELINE - TEMPORADA 2024/2025")

# Teams to fetch (SIN América - ya procesado anteriormente)
# Los 18 equipos de Liga MX Apertura 2024 excepto Club América
scouting_teams <- c(
  # Equipos ya procesados anteriormente
  "Toluca",
  "Guadalajara",
  "Monterrey",
  "Mazatlán",
  "Cruz Azul",
  "Tigres",
  "León",
  "Atlas",
  "Puebla",
  # 8 equipos nuevos
  "Atlético San Luis",
  "Juárez",
  "Necaxa",
  "Pachuca",
  "Pumas UNAM",
  "Querétaro",
  "Santos Laguna",
  "Tijuana"
)

cat("🎯 Equipos de scouting:\n")
for (i in seq_along(scouting_teams)) {
  cat(sprintf("   %d. %s\n", i, scouting_teams[i]))
}

cat("\n📁 Estructura de directorios (particionado por equipo):\n")
for (team in scouting_teams) {
  team_dir <- normalize_team_name(team)
  cat(sprintf("   • data/processed/%s/\n", team_dir))
}

# Credentials
cat("\n🔐 Setting up authentication...\n")

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

# Create base directory
cat("\n📁 Creating output directories...\n")
dir.create("data/processed", recursive = TRUE, showWarnings = FALSE)

# Create team-specific directories
for (team in scouting_teams) {
  team_dir <- file.path("data/processed", normalize_team_name(team))
  dir.create(team_dir, recursive = TRUE, showWarnings = FALSE)
  cat(sprintf("   ✓ %s\n", team_dir))
}

# ==============================================================================
# STEP 1: GET LATEST SEASON MATCHES
# ==============================================================================

print_section("STEP 1: FETCH MATCHES (2024/2025)")

cat("📊 Fetching competitions...\n")
competitions <- competitions(username, password)

# Filter for Liga MX 2024/2025
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

# Filter matches for scouting teams (EXCLUDING América)
cat("\n🎯 Filtering matches for scouting teams...\n")

# Create regex pattern for scouting teams only
team_pattern <- paste(scouting_teams, collapse = "|")

scouting_matches <- all_matches %>%
  filter(
    str_detect(home_team.home_team_name, regex(team_pattern, ignore_case = TRUE)) |
    str_detect(away_team.away_team_name, regex(team_pattern, ignore_case = TRUE))
  )

cat(sprintf("   ✓ Matches involving scouting teams: %d\n", nrow(scouting_matches)))

# Show matches per team
cat("\n📈 Match distribution by team:\n")
for (team in scouting_teams) {
  team_match_count <- scouting_matches %>%
    filter(
      str_detect(home_team.home_team_name, regex(team, ignore_case = TRUE)) |
      str_detect(away_team.away_team_name, regex(team, ignore_case = TRUE))
    ) %>%
    nrow()

  cat(sprintf("   • %s: %d matches\n", team, team_match_count))
}

# ==============================================================================
# STEP 2: PROCESS EACH TEAM SEPARATELY
# ==============================================================================

print_section("STEP 2: PROCESS EACH TEAM SEPARATELY")

# Process each team
for (team_name in scouting_teams) {

  cat("\n")
  cat(paste(rep("-", 80), collapse = ""), "\n")
  cat(sprintf("  Processing: %s\n", team_name))
  cat(paste(rep("-", 80), collapse = ""), "\n\n")

  team_dir <- file.path("data/processed", normalize_team_name(team_name))

  # Filter matches for this team
  team_matches <- scouting_matches %>%
    filter(
      str_detect(home_team.home_team_name, regex(team_name, ignore_case = TRUE)) |
      str_detect(away_team.away_team_name, regex(team_name, ignore_case = TRUE))
    ) %>%
    mutate(
      is_home = str_detect(home_team.home_team_name, regex(team_name, ignore_case = TRUE)),
      team_goals = if_else(is_home, home_score, away_score),
      opponent_goals = if_else(is_home, away_score, home_score),
      result = case_when(
        team_goals > opponent_goals ~ "Win",
        team_goals < opponent_goals ~ "Loss",
        TRUE ~ "Draw"
      )
    )

  cat(sprintf("   📋 Matches: %d\n", nrow(team_matches)))

  # Save matches
  matches_file <- file.path(team_dir, "matches.csv")
  write_csv(team_matches, matches_file)
  cat(sprintf("   💾 Saved: %s\n", matches_file))

  # Get match IDs
  match_ids <- team_matches$match_id

  # Download events in batches
  cat(sprintf("\n   📥 Downloading events for %d matches...\n", length(match_ids)))

  batch_size <- 5
  n_batches <- ceiling(length(match_ids) / batch_size)

  all_events_list <- list()

  for (i in 1:n_batches) {
    start_idx <- (i - 1) * batch_size + 1
    end_idx <- min(i * batch_size, length(match_ids))
    batch_ids <- match_ids[start_idx:end_idx]

    cat(sprintf("      Batch %d/%d... ", i, n_batches))

    tryCatch({
      httr::set_config(httr::timeout(600))

      batch_events <- allevents(
        username = username,
        password = password,
        matches = batch_ids,
        parallel = FALSE
      )

      all_events_list[[i]] <- batch_events
      cat(sprintf("✓ (%s events)\n", format(nrow(batch_events), big.mark = ",")))

      if (i < n_batches) {
        Sys.sleep(2)
      }

    }, error = function(e) {
      cat(sprintf("❌ Error: %s\n", conditionMessage(e)))
    })
  }

  # Combine all batches
  cat("\n   🔗 Combining batches...\n")
  all_events <- bind_rows(all_events_list)

  cat(sprintf("   ✓ Total events: %s\n", format(nrow(all_events), big.mark = ",")))

  # Clean events
  cat("\n   🧹 Cleaning events...\n")
  events_clean <- allclean(all_events)

  cat(sprintf("   ✓ Cleaned: %d columns\n", ncol(events_clean)))

  # Calculate minutes played
  cat("\n   ⏱️  Calculating minutes played...\n")

  events_for_minutes <- formatelapsedtime(events_clean)

  tryCatch({
    minutes_played_raw <- get.minutesplayed(events_for_minutes)

    cat(sprintf("   ✓ Minutes calculated: %d player-match records\n",
                nrow(minutes_played_raw)))

    # Enrich with names
    player_id_to_name <- events_clean %>%
      filter(!is.na(player.id) & !is.na(player.name)) %>%
      distinct(player.id, player.name)

    team_id_to_name <- events_clean %>%
      filter(!is.na(team.id) & !is.na(team.name)) %>%
      distinct(team.id, team.name)

    minutes_played_enriched <- minutes_played_raw %>%
      left_join(player_id_to_name, by = "player.id") %>%
      left_join(team_id_to_name, by = "team.id") %>%
      select(match_id, player.id, player.name, team.id, team.name,
             TimeOn, TimeOff, GameEnd, MinutesPlayed)

    # Filter to this team only
    team_minutes <- minutes_played_enriched %>%
      filter(str_detect(team.name, regex(team_name, ignore_case = TRUE)))

    cat(sprintf("   ✓ Filtered to %s: %d player-match records\n",
                team_name, nrow(team_minutes)))

  }, error = function(e) {
    cat(sprintf("   ❌ Error calculating minutes: %s\n", e$message))
    team_minutes <- NULL
  })

  # Save events as Parquet
  cat("\n   💾 Saving events to Parquet...\n")
  events_file <- file.path(team_dir, "events.parquet")

  # Convert list columns to JSON
  list_cols <- names(events_clean)[sapply(events_clean, is.list)]
  events_for_parquet <- events_clean

  for (col in list_cols) {
    if (!str_detect(col, "\\.(x|y|z)$")) {
      events_for_parquet[[col]] <- map_chr(events_for_parquet[[col]],
                                            ~ifelse(is.null(.x) || all(is.na(.x)),
                                                    NA_character_,
                                                    jsonlite::toJSON(.x, auto_unbox = TRUE)))
    }
  }

  write_parquet(events_for_parquet, events_file)
  cat(sprintf("   ✓ Saved: %s (%.1f MB)\n",
              events_file, file.info(events_file)$size / 1024^2))

  # Download lineups
  cat("\n   👥 Fetching lineups...\n")

  all_lineups_list <- list()

  for (i in 1:length(match_ids)) {
    match_id <- match_ids[i]

    cat(sprintf("      Match %d/%d... ", i, length(match_ids)))

    tryCatch({
      httr::set_config(httr::timeout(60))

      lineup <- get.lineups(
        username = username,
        password = password,
        match_id = match_id
      )

      all_lineups_list[[i]] <- lineup
      cat("✓\n")

      if (i %% 10 == 0) {
        Sys.sleep(2)
      } else {
        Sys.sleep(0.5)
      }

    }, error = function(e) {
      cat(sprintf("❌\n"))
    })
  }

  # Combine and clean lineups
  all_lineups <- bind_rows(all_lineups_list)

  cat(sprintf("\n   ✓ Total lineup records: %d\n", nrow(all_lineups)))

  lineups_clean <- cleanlineups(all_lineups)

  # Filter to this team only
  team_lineups <- lineups_clean %>%
    filter(str_detect(team_name, regex(team_name, ignore_case = TRUE)))

  cat(sprintf("   ✓ Filtered to %s: %d records\n", team_name, nrow(team_lineups)))

  # Save lineups as Parquet
  lineups_file <- file.path(team_dir, "lineups.parquet")

  lineups_list_cols <- names(team_lineups)[sapply(team_lineups, is.list)]
  lineups_for_parquet <- team_lineups

  if (length(lineups_list_cols) > 0) {
    for (col in lineups_list_cols) {
      lineups_for_parquet[[col]] <- map_chr(lineups_for_parquet[[col]],
                                             ~ifelse(is.null(.x) || all(is.na(.x)),
                                                     NA_character_,
                                                     jsonlite::toJSON(.x, auto_unbox = TRUE)))
    }
  }

  write_parquet(lineups_for_parquet, lineups_file)
  cat(sprintf("   💾 Saved: %s\n", lineups_file))

  # Save minutes played
  if (!is.null(team_minutes)) {
    minutes_file <- file.path(team_dir, "minutes_played.parquet")
    write_parquet(team_minutes, minutes_file)
    cat(sprintf("   💾 Saved: %s\n", minutes_file))
  }

  cat(sprintf("\n   ✅ %s processing complete!\n", team_name))
}

# ==============================================================================
# SUMMARY
# ==============================================================================

print_section("PIPELINE COMPLETE - SUMMARY")

cat("✅ Scouting teams data successfully downloaded!\n\n")

cat("📊 Data Overview:\n")
cat(sprintf("   • Season: %s\n", liga_mx_latest$season_name))
cat(sprintf("   • Scouting teams: %d\n", length(scouting_teams)))
cat(sprintf("   • Total matches: %d\n", nrow(scouting_matches)))

cat("\n📁 Data structure (partitioned by team):\n\n")

for (team in scouting_teams) {
  team_dir <- file.path("data/processed", normalize_team_name(team))

  cat(sprintf("   %s/\n", normalize_team_name(team)))

  # Check files
  files <- c("matches.csv", "events.parquet", "lineups.parquet", "minutes_played.parquet")

  for (file in files) {
    file_path <- file.path(team_dir, file)
    if (file.exists(file_path)) {
      size_mb <- file.info(file_path)$size / 1024^2
      if (size_mb < 1) {
        size_str <- sprintf("%.0f KB", file.info(file_path)$size / 1024)
      } else {
        size_str <- sprintf("%.1f MB", size_mb)
      }
      cat(sprintf("      ✓ %s (%s)\n", file, size_str))
    } else {
      cat(sprintf("      ✗ %s (not found)\n", file))
    }
  }
  cat("\n")
}

cat("🎯 Next Steps:\n")
cat("   1. Run 02_calculate_scouting_metrics.R to compute per-player stats\n")
cat("   2. Compare with América DNA (from script 03)\n")
cat("   3. Build FitScore model for player recommendations\n")

cat("\n💡 Quick load example:\n")
cat("   library(arrow); library(tidyverse)\n")
cat("   toluca_events <- read_parquet('data/processed/toluca/events.parquet')\n")
cat("   toluca_lineups <- read_parquet('data/processed/toluca/lineups.parquet')\n")

cat("\n")
cat(paste(rep("=", 80), collapse = ""), "\n\n")
