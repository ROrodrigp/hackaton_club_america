#!/usr/bin/env Rscript
# Debug script to understand get.minutesplayed() error

library(arrow)
library(tidyverse)
library(StatsBombR)

cat("🔍 DEBUGGING get.minutesplayed() ERROR\n")
cat("=====================================\n\n")

# Load events from Parquet
cat("1. Loading events from Parquet...\n")
events <- read_parquet("data/processed/america_events_2024_2025.parquet")
cat(sprintf("   ✓ Loaded %s events\n", format(nrow(events), big.mark = ",")))
cat(sprintf("   ✓ Number of columns: %d\n\n", ncol(events)))

# Check structure before formatelapsedtime
cat("2. Structure BEFORE formatelapsedtime():\n")
cat(sprintf("   - Class: %s\n", paste(class(events), collapse = ", ")))
cat(sprintf("   - Has 'period' column: %s\n", "period" %in% colnames(events)))
cat(sprintf("   - Has 'match_id' column: %s\n", "match_id" %in% colnames(events)))
cat(sprintf("   - Has 'ElapsedTime' column: %s\n\n", "ElapsedTime" %in% colnames(events)))

# Sample first row to see structure
cat("3. First row sample:\n")
first_row <- events[1, ]
cat(sprintf("   - Type of first row: %s\n", class(first_row)))
cat(sprintf("   - ncol of first row: %s\n\n", ncol(first_row)))

# Apply formatelapsedtime
cat("4. Applying formatelapsedtime()...\n")
events <- formatelapsedtime(events)
cat(sprintf("   ✓ Done\n"))
cat(sprintf("   - Has 'ElapsedTime' column now: %s\n\n", "ElapsedTime" %in% colnames(events)))

# Check columns that might be lists
cat("5. Checking for list-type columns:\n")
list_cols <- sapply(events, is.list)
if (any(list_cols)) {
  cat(sprintf("   Found %d list columns:\n", sum(list_cols)))
  list_col_names <- names(events)[list_cols]
  for (col in list_col_names[1:min(10, length(list_col_names))]) {
    cat(sprintf("      - %s\n", col))
  }
  if (length(list_col_names) > 10) {
    cat(sprintf("      ... and %d more\n", length(list_col_names) - 10))
  }
} else {
  cat("   No list columns found\n")
}
cat("\n")

# Check column types
cat("6. Column type summary:\n")
col_types <- sapply(events, class)
col_type_summary <- table(sapply(col_types, function(x) paste(x, collapse = "|")))
for (type in names(col_type_summary)) {
  cat(sprintf("   - %s: %d columns\n", type, col_type_summary[type]))
}
cat("\n")

# Try to peek into get.minutesplayed source
cat("7. Checking what get.minutesplayed expects...\n")
cat("   Let's see if the function expects specific column structures\n\n")

# Sample a single match to test
cat("8. Testing with a SINGLE match:\n")
sample_match_id <- unique(events$match_id)[1]
cat(sprintf("   - Testing with match_id: %s\n", sample_match_id))
sample_events <- events %>% filter(match_id == sample_match_id)
cat(sprintf("   - Events in this match: %d\n", nrow(sample_events)))

cat("\n   Attempting get.minutesplayed() on single match...\n")
tryCatch({
  result <- get.minutesplayed(sample_events)
  cat("   ✓ SUCCESS on single match!\n")
  cat(sprintf("   - Result rows: %d\n", nrow(result)))
  cat(sprintf("   - Result columns: %s\n", paste(colnames(result), collapse = ", ")))
}, error = function(e) {
  cat(sprintf("   ✗ FAILED on single match\n"))
  cat(sprintf("   Error: %s\n", e$message))
})

cat("\n9. DIAGNOSIS COMPLETE\n")
