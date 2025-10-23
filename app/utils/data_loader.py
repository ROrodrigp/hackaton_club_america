"""
Data loading utilities for Club América Streamlit app
"""
import json
import pandas as pd
from pathlib import Path


def get_project_root():
    """Get the project root directory (parent of app/)"""
    return Path(__file__).parent.parent.parent


def load_json(relative_path):
    """
    Load JSON file from project root

    Args:
        relative_path: Path relative to project root (e.g., 'data/processed/file.json')

    Returns:
        dict: Loaded JSON data
    """
    root = get_project_root()
    file_path = root / relative_path

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_csv(relative_path):
    """
    Load CSV file from project root

    Args:
        relative_path: Path relative to project root (e.g., 'data/processed/file.csv')

    Returns:
        pd.DataFrame: Loaded CSV data
    """
    root = get_project_root()
    file_path = root / relative_path

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return pd.read_csv(file_path)


def load_america_dna():
    """Load Club América DNA profile"""
    return load_json('data/processed/america_dna_profile.json')


def load_benchmarks():
    """Load Liga MX P90 benchmarks"""
    return load_json('data/processed/liga_mx_benchmarks_p90.json')


def load_top_recommendations():
    """Load top 20 player recommendations"""
    return load_csv('data/processed/top_recommendations.csv')


def load_worst_recommendations():
    """Load worst 20 player recommendations"""
    return load_csv('data/processed/worst_recommendations.csv')


def load_scouting_pool():
    """Load complete scouting pool with all metrics"""
    return load_csv('data/processed/scouting_pool_all_metrics.csv')


def load_america_players():
    """Load Club América player metrics"""
    try:
        # Try CSV first
        return load_csv('data/processed/player_metrics_2024_2025.csv')
    except FileNotFoundError:
        # Fallback to parquet if available
        import pyarrow.parquet as pq
        root = get_project_root()
        file_path = root / 'data/processed/player_metrics_2024_2025.parquet'
        return pd.read_parquet(file_path)
