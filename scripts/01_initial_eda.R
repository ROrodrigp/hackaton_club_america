#!/usr/bin/env Rscript
# Initial Exploratory Data Analysis for Club América Player Recommendation System
# Explores StatsBomb data for Liga MX (Apertura 2021 - Clausura 2025)

# Load required libraries
suppressPackageStartupMessages({
  library(StatsBombR)
  library(tidyverse)
  library(lubridate)
})

# Helper function to print section headers
print_section <- function(title) {
  cat("\n")
  cat(paste(rep("=", 80), collapse = ""), "\n")
  cat(sprintf("  %s\n", title))
  cat(paste(rep("=", 80), collapse = ""), "\n\n")
}

# ============================================================================
# START ANALYSIS
# ============================================================================

print_section("CLUB AMÉRICA - INITIAL DATA EXPLORATION (AUTHENTICATED)")

# Set credentials
cat("🔐 Setting up authentication...\n")
username <- "itam_hackathon@hudl.com"
password <- "pGwIprel"
cat("   ✓ Credentials loaded\n")

# 1. Get competitions with authentication
cat("\n📊 Fetching available competitions with credentials...\n")

competitions <- competitions(username, password)
cat(sprintf("   Total competitions available: %d\n", nrow(competitions)))

# 2. Filter for Liga MX
cat("\n🇲🇽 Filtering for Liga MX...\n")
liga_mx <- competitions %>%
  filter(str_detect(competition_name, regex("Liga MX", ignore_case = TRUE)))

cat(sprintf("   Liga MX seasons found: %d\n", nrow(liga_mx)))

if (nrow(liga_mx) == 0) {
  cat("\n❌ No Liga MX data found. Checking all competitions...\n")
  cat("\nAll competitions:\n")
  print(head(competitions %>% select(competition_name, season_name), 20))
  stop("No Liga MX data found")
}

cat("\n   Available seasons:\n")
liga_mx %>%
  arrange(season_name) %>%
  select(season_name) %>%
  pull() %>%
  walk(~cat(sprintf("      - %s\n", .x)))

# 3. Get all matches
cat("\n⚽ Fetching matches for each season...\n")

all_matches <- liga_mx %>%
  pmap_dfr(function(competition_id, season_id, season_name, ...) {
    tryCatch({
      matches <- get.matches(username, password, season_id, competition_id)
      matches$season_name <- season_name
      cat(sprintf("   ✓ %s: %d matches\n", season_name, nrow(matches)))
      return(matches)
    }, error = function(e) {
      cat(sprintf("   ✗ %s: Error - %s\n", season_name, conditionMessage(e)))
      return(NULL)
    })
  })

if (is.null(all_matches) || nrow(all_matches) == 0) {
  cat("\n❌ No matches found\n")
  stop("No matches found")
}

cat(sprintf("\n   Total matches collected: %d\n", nrow(all_matches)))

# Save matches data
data_dir <- file.path(dirname(dirname(getwd())), "data")
if (!dir.exists(data_dir)) {
  dir.create(data_dir, recursive = TRUE)
}

matches_file <- file.path(data_dir, "liga_mx_matches.csv")
write_csv(all_matches, matches_file)
cat(sprintf("   💾 Saved to: %s\n", matches_file))

# 4. Find Club América
print_section("CLUB AMÉRICA ANALYSIS")

# Try different variations of the team name
america_matches <- all_matches %>%
  filter(
    str_detect(home_team.home_team_name, regex("América", ignore_case = TRUE)) |
    str_detect(away_team.away_team_name, regex("América", ignore_case = TRUE))
  )

if (nrow(america_matches) == 0) {
  cat("❌ Club América not found. Available teams:\n")
  all_teams <- unique(c(all_matches$home_team.home_team_name, all_matches$away_team.away_team_name))
  head(sort(all_teams), 20) %>%
    walk(~cat(sprintf("   - %s\n", .x)))
  stop("Club América not found")
}

cat("✓ Found Club América matches\n")
cat(sprintf("\n📈 Club América Statistics:\n"))
cat(sprintf("   Total matches: %d\n", nrow(america_matches)))

cat("\n   Matches by season:\n")
america_matches %>%
  count(season_name) %>%
  arrange(season_name) %>%
  pwalk(function(season_name, n) {
    cat(sprintf("      - %s: %d matches\n", season_name, n))
  })

# Calculate results
america_results <- america_matches %>%
  mutate(
    is_home = str_detect(home_team.home_team_name, regex("América", ignore_case = TRUE)),
    result = case_when(
      is_home & home_score > away_score ~ "Win",
      is_home & home_score < away_score ~ "Loss",
      !is_home & away_score > home_score ~ "Win",
      !is_home & away_score < home_score ~ "Loss",
      TRUE ~ "Draw"
    )
  )

result_summary <- america_results %>%
  count(result) %>%
  mutate(pct = n / sum(n) * 100)

cat("\n   Results:\n")
result_summary %>%
  pwalk(function(result, n, pct) {
    cat(sprintf("      - %s: %d (%.1f%%)\n", result, n, pct))
  })

win_rate <- result_summary %>%
  filter(result == "Win") %>%
  pull(pct) %>%
  first()

if (!is.na(win_rate)) {
  cat(sprintf("      - Win rate: %.1f%%\n", win_rate))
}

# Save América matches
america_file <- file.path(data_dir, "club_america_matches.csv")
write_csv(america_results, america_file)
cat(sprintf("\n   💾 Saved Club América matches to: %s\n", america_file))

# 5. Sample event data
print_section("EVENT DATA EXPLORATION")

sample_match <- america_results %>% slice(1)
sample_match_id <- sample_match$match_id

cat("Loading sample match:\n")
cat(sprintf("   Match: %s vs %s\n",
            sample_match$home_team.home_team_name,
            sample_match$away_team.away_team_name))
cat(sprintf("   Date: %s\n", sample_match$match_date))
cat(sprintf("   Score: %d - %d\n",
            sample_match$home_score,
            sample_match$away_score))

tryCatch({
  cat("\n⏳ Fetching event data (this may take a moment)...\n")

  events <- get.events(username, password, sample_match_id)

  cat(sprintf("\n📊 Event Data Summary:\n"))
  cat(sprintf("   Total events: %d\n", nrow(events)))

  event_types <- events %>%
    count(type.name, sort = TRUE)

  cat(sprintf("   Event types: %d\n", nrow(event_types)))
  cat("\n   Top 10 event types:\n")
  event_types %>%
    head(10) %>%
    pwalk(function(type.name, n) {
      cat(sprintf("      - %s: %d\n", type.name, n))
    })

  # Check for 360 data
  cols_360 <- names(events)[str_detect(names(events),
                                       regex("360|freeze|visible", ignore_case = TRUE))]

  if (length(cols_360) > 0) {
    cat(sprintf("\n   360-related columns found: %s\n",
               paste(cols_360, collapse = ", ")))

    for (col in cols_360) {
      non_null <- sum(!is.na(events[[col]]))
      pct <- non_null / nrow(events) * 100
      cat(sprintf("      - %s: %d events (%.1f%%)\n", col, non_null, pct))
    }
  } else {
    cat("\n   No 360-related columns found in sample\n")
  }

  # Player stats
  players <- events %>%
    filter(!is.na(player.name)) %>%
    distinct(player.name, team.name, position.name)

  cat(sprintf("\n   Players in match: %d\n", nrow(players)))
  cat(sprintf("   Positions represented: %d\n",
             length(unique(players$position.name))))

  # Save sample events
  sample_events_file <- file.path(data_dir, "sample_events.csv")
  write_csv(events, sample_events_file)
  cat(sprintf("\n   💾 Saved sample events to: %s\n", sample_events_file))

}, error = function(e) {
  cat(sprintf("\n❌ Error loading events: %s\n", conditionMessage(e)))
})

# 6. Summary
print_section("SUMMARY")

cat("✅ Data successfully loaded and explored!\n")
cat("\nKey Findings:\n")
cat(sprintf("   • Liga MX seasons available: %d\n", nrow(liga_mx)))
cat(sprintf("   • Total matches: %d\n", nrow(all_matches)))
cat(sprintf("   • Club América matches: %d\n", nrow(america_results)))
if (!is.na(win_rate)) {
  cat(sprintf("   • Club América win rate: %.1f%%\n", win_rate))
}

if (exists("events") && !is.null(events)) {
  cat("   • Event data accessible: Yes\n")
  cat(sprintf("   • Sample match events: %d\n", nrow(events)))
}

cat("\n📁 Files saved to data/ directory:\n")
cat("   • liga_mx_matches.csv\n")
cat("   • club_america_matches.csv\n")
if (exists("events") && !is.null(events)) {
  cat("   • sample_events.csv\n")
}

cat("\n🎯 Next Steps:\n")
cat("   1. Analyze Club América's tactical profile\n")
cat("   2. Deep dive into player statistics\n")
cat("   3. Explore passing networks and defensive actions\n")
cat("   4. Build player evaluation framework\n")

cat("\n")
cat(paste(rep("=", 80), collapse = ""), "\n\n")
