#!/usr/bin/env Rscript
# Setup script to install required R packages for the analysis

cat("================================================================================\n")
cat("  Installing R Packages for Club América Player Recommendation System\n")
cat("================================================================================\n\n")

# List of required packages
packages <- c(
  "devtools",      # For installing StatsBombR from GitHub
  "tidyverse",     # Data manipulation and visualization
  "ggplot2",       # Advanced plotting
  "dplyr",         # Data manipulation
  "tidyr",         # Data tidying
  "readr",         # Fast reading of data
  "lubridate",     # Date manipulation
  "purrr",         # Functional programming
  "ggrepel",       # Better text labels in plots
  "scales",        # Scale functions for visualization
  "RColorBrewer",  # Color palettes
  "plotly"         # Interactive plots
)

# Function to install packages if not already installed
install_if_missing <- function(pkg) {
  if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
    cat(sprintf("Installing %s...\n", pkg))
    install.packages(pkg, repos = "https://cran.rstudio.com/", quiet = TRUE)
    cat(sprintf("✓ %s installed\n", pkg))
  } else {
    cat(sprintf("✓ %s already installed\n", pkg))
  }
}

# Install CRAN packages
cat("\n📦 Installing CRAN packages...\n\n")
for (pkg in packages) {
  install_if_missing(pkg)
}

# Install StatsBombR from GitHub
cat("\n📦 Installing StatsBombR from GitHub...\n\n")
if (!require("StatsBombR", quietly = TRUE)) {
  library(devtools)
  cat("Installing StatsBombR...\n")
  tryCatch({
    devtools::install_github("statsbomb/StatsBombR", quiet = TRUE)
    cat("✓ StatsBombR installed successfully\n")
  }, error = function(e) {
    cat("✗ Error installing StatsBombR:", conditionMessage(e), "\n")
  })
} else {
  cat("✓ StatsBombR already installed\n")
}

cat("\n================================================================================\n")
cat("  Setup Complete!\n")
cat("================================================================================\n\n")

# Print installed versions
cat("Installed package versions:\n")
for (pkg in c(packages, "StatsBombR")) {
  if (require(pkg, character.only = TRUE, quietly = TRUE)) {
    version <- packageVersion(pkg)
    cat(sprintf("  %s: %s\n", pkg, version))
  }
}

cat("\n✅ All packages installed successfully!\n\n")
