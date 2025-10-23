#!/usr/bin/env python3
"""
==============================================================================
CALCULATE PLAYER FIT SCORE - CLUB AMÉRICA
==============================================================================

Propósito: Calcular qué tan bien encaja cada jugador del scouting pool
           con el perfil táctico (DNA) de Club América

Input:
  - data/processed/america_dna.json
  - data/processed/scouting_pool_all_metrics.parquet
  - data/processed/liga_mx_benchmarks_p90.json

Output:
  - data/processed/player_fit_scores.json
  - data/processed/top_recommendations.csv

Methodology:
  FitScore = (DNA Match × 0.60) + (Gap Filling × 0.30) + (Role Fit × 0.10)

==============================================================================
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Weights for FitScore components
WEIGHTS = {
    'dna_match': 0.60,
    'gap_filling': 0.30,
    'role_fit': 0.10
}

# DNA dimensions (in order)
DNA_DIMENSIONS = [
    'progression',
    'creation',
    'finishing',
    'pressing',
    'possession',
    'dribbling'
]

# Minimum score threshold to consider a dimension as a "weakness"
# 95.0 = Identifies Pressing + Progression as areas to improve
# 90.0 = Only identifies Pressing
WEAKNESS_THRESHOLD = 95.0

# Number of top recommendations to generate
TOP_N = 20

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def load_america_dna(filepath):
    """Load Club América DNA profile"""
    with open(filepath, 'r') as f:
        dna = json.load(f)
    return dna


def load_benchmarks(filepath):
    """Load Liga MX benchmarks (P90)"""
    with open(filepath, 'r') as f:
        benchmarks = json.load(f)
    return benchmarks


def calculate_player_dna_score(player, benchmarks, dimension):
    """
    Calculate DNA score for a single dimension for a player

    Mirrors the logic from 03_define_america_dna.R
    """

    if dimension == 'progression':
        # Progression: 40% progressive passes, 30% carries, 30% touches
        prog_passes = min(player['progressive_passes_p90'] / benchmarks['progressive_passes_p90'], 1.0) * 40
        prog_carries = min(player['progressive_carries_p90'] / benchmarks['progressive_carries_p90'], 1.0) * 30
        touches = min(player['touches_att_third_p90'] / benchmarks['touches_att_third_p90'], 1.0) * 30
        return prog_passes + prog_carries + touches

    elif dimension == 'creation':
        # Creation: 50% xA, 30% shot_assists, 20% key_passes
        xa = min(player['xA_p90'] / benchmarks['xA_p90'], 1.0) * 50
        shot_assists = min(player['shot_assists_p90'] / benchmarks['shot_assists_p90'], 1.0) * 30
        key_passes = min(player['key_passes_p90'] / benchmarks['key_passes_p90'], 1.0) * 20
        return xa + shot_assists + key_passes

    elif dimension == 'finishing':
        # Finishing: 60% xG, 40% shot quality
        xg = min(player['xG_p90'] / benchmarks['xG_p90'], 1.0) * 60

        # Shot quality = xG per shot (if player has shots)
        shot_quality = 0
        if player['shots_p90'] > 0:
            player_shot_quality = player['xG_p90'] / player['shots_p90']
            benchmark_shot_quality = benchmarks['xG_p90'] / benchmarks['shots_p90']
            shot_quality = min(player_shot_quality / benchmark_shot_quality, 1.0) * 40

        return xg + shot_quality

    elif dimension == 'pressing':
        # Pressing: 60% pressures, 20% tackles, 20% interceptions
        pressures = min(player['pressures_p90'] / benchmarks['pressures_p90'], 1.0) * 60
        tackles = min(player['tackles_p90'] / benchmarks['tackles_p90'], 1.0) * 20
        interceptions = min(player['interceptions_p90'] / benchmarks['interceptions_p90'], 1.0) * 20
        return pressures + tackles + interceptions

    elif dimension == 'possession':
        # Possession: 60% pass completion, 40% touches attacking third
        pass_comp = min(player['pass_completion_pct'] / benchmarks['pass_completion_pct'], 1.0) * 60
        touches = min(player['touches_att_third_p90'] / benchmarks['touches_att_third_p90'], 1.0) * 40
        return pass_comp + touches

    elif dimension == 'dribbling':
        # Dribbling: 40% attempts, 35% successful, 25% success rate
        attempts = min(player['dribbles_p90'] / benchmarks['dribbles_p90'], 1.0) * 40
        successful = min(player['dribbles_successful_p90'] / benchmarks['dribbles_successful_p90'], 1.0) * 35
        success_rate = min(player['dribble_success_pct'] / benchmarks['dribble_success_pct'], 1.0) * 25
        return attempts + successful + success_rate

    else:
        raise ValueError(f"Unknown dimension: {dimension}")


def calculate_player_dna_vector(player, benchmarks):
    """
    Calculate complete DNA vector for a player (6 dimensions)

    Returns: dict with scores for each dimension
    """
    dna_vector = {}

    for dimension in DNA_DIMENSIONS:
        score = calculate_player_dna_score(player, benchmarks, dimension)
        dna_vector[dimension] = score

    return dna_vector


def extract_america_dna_vector(america_dna):
    """
    Extract América's DNA scores as a vector

    Returns: numpy array of shape (6,)
    """
    vector = []
    for dimension in DNA_DIMENSIONS:
        score = america_dna['dimensions'][dimension]['score']
        vector.append(score)

    return np.array(vector)


def calculate_dna_match_score(player_vector, america_vector):
    """
    Calculate DNA Match score using cosine similarity

    Args:
        player_vector: numpy array (6,)
        america_vector: numpy array (6,)

    Returns: score 0-100
    """
    # Reshape for sklearn
    player_v = np.array(list(player_vector.values())).reshape(1, -1)
    america_v = america_vector.reshape(1, -1)

    # Cosine similarity returns value in [-1, 1], we want [0, 100]
    similarity = cosine_similarity(player_v, america_v)[0][0]

    # Convert to 0-100 scale
    # similarity of 1.0 = 100, similarity of 0 = 50, similarity of -1 = 0
    score = (similarity + 1) / 2 * 100

    return score


def identify_team_weaknesses(america_dna, threshold=WEAKNESS_THRESHOLD):
    """
    Identify América's weaknesses (dimensions below threshold)

    Returns: dict {dimension: gap_from_threshold}
    """
    weaknesses = {}

    for dimension in DNA_DIMENSIONS:
        score = america_dna['dimensions'][dimension]['score']
        if score < threshold:
            gap = threshold - score
            weaknesses[dimension] = gap

    return weaknesses


def calculate_gap_filling_score(player_vector, america_dna, weaknesses):
    """
    Calculate how much the player fills América's gaps

    Args:
        player_vector: dict with DNA scores
        america_dna: América DNA object
        weaknesses: dict of weaknesses

    Returns: score 0-100
    """
    if not weaknesses:
        # No weaknesses = player gets average score
        return 50.0

    total_gap_filled = 0
    total_possible_gap = 0

    for dimension, gap in weaknesses.items():
        america_score = america_dna['dimensions'][dimension]['score']
        player_score = player_vector[dimension]

        # How much does player exceed América's score?
        improvement = max(0, player_score - america_score)

        # Weight by the size of the gap
        weighted_improvement = improvement * gap

        total_gap_filled += weighted_improvement
        total_possible_gap += gap * (100 - america_score)  # Max possible improvement

    # Normalize to 0-100
    if total_possible_gap > 0:
        score = (total_gap_filled / total_possible_gap) * 100
    else:
        score = 50.0

    return min(score, 100.0)


def calculate_role_fit_score(player, position_needs=None):
    """
    Calculate role fit score based on position

    For Phase 1: Simple implementation - all positions equally valuable

    Args:
        player: player row from dataframe
        position_needs: dict (not used in Phase 1)

    Returns: score 0-100
    """
    # Phase 1: Equal opportunity for all positions
    # All players get a baseline score of 70
    # This component will be expanded in Phase 2

    return 70.0


def calculate_fit_score(player, benchmarks, america_dna, america_vector, weaknesses):
    """
    Calculate complete FitScore for a player

    Returns: dict with all score components
    """
    # Calculate player's DNA vector
    player_dna_vector = calculate_player_dna_vector(player, benchmarks)

    # Component 1: DNA Match (60%)
    dna_match = calculate_dna_match_score(player_dna_vector, america_vector)

    # Component 2: Gap Filling (30%)
    gap_filling = calculate_gap_filling_score(player_dna_vector, america_dna, weaknesses)

    # Component 3: Role Fit (10%)
    role_fit = calculate_role_fit_score(player)

    # Combined FitScore
    fit_score = (
        dna_match * WEIGHTS['dna_match'] +
        gap_filling * WEIGHTS['gap_filling'] +
        role_fit * WEIGHTS['role_fit']
    )

    return {
        'fit_score': fit_score,
        'dna_match_score': dna_match,
        'gap_filling_score': gap_filling,
        'role_fit_score': role_fit,
        'player_dna': player_dna_vector
    }


def generate_recommendation_text(player, scores, america_dna, weaknesses):
    """
    Generate human-readable explanation of why player is a good fit

    Returns: string
    """
    reasons = []

    # Check DNA match
    if scores['dna_match_score'] >= 90:
        reasons.append("Excellent tactical match with América's style")
    elif scores['dna_match_score'] >= 80:
        reasons.append("Strong tactical compatibility")

    # Check which dimensions player excels at
    player_dna = scores['player_dna']
    elite_dimensions = []

    for dimension in DNA_DIMENSIONS:
        if player_dna[dimension] >= 90:
            elite_dimensions.append(dimension.capitalize())

    if elite_dimensions:
        dims_str = ", ".join(elite_dimensions[:2])  # Max 2 to keep concise
        reasons.append(f"Elite in: {dims_str}")

    # Check if fills gaps
    if scores['gap_filling_score'] >= 70 and weaknesses:
        weak_dims = list(weaknesses.keys())
        if weak_dims:
            reasons.append(f"Strengthens team's {weak_dims[0]}")

    if not reasons:
        reasons.append("Solid all-around player")

    return "; ".join(reasons)


def generate_why_avoid(player):
    """
    Generate explanation of why a player is a poor fit

    Returns: string
    """
    reasons = []

    # Check DNA mismatch
    if player['dna_match_score'] < 70:
        reasons.append("Poor tactical compatibility")

    # Check which dimensions are weak
    weak_dims = []
    for dimension in DNA_DIMENSIONS:
        if player['player_dna'][dimension] < 50:
            weak_dims.append(dimension.capitalize())

    if weak_dims:
        dims_str = ", ".join(weak_dims[:3])
        reasons.append(f"Weak in: {dims_str}")

    # Check if doesn't fill gaps
    if player['gap_filling_score'] < 30:
        reasons.append("Doesn't address team weaknesses")

    if not reasons:
        reasons.append("Below-average across multiple dimensions")

    return "; ".join(reasons)


# ==============================================================================
# MAIN PIPELINE
# ==============================================================================

def main():
    print_section("CLUB AMÉRICA - PLAYER FIT SCORE CALCULATOR")

    # -------------------------------------------------------------------------
    # STEP 1: LOAD DATA
    # -------------------------------------------------------------------------

    print_section("STEP 1: LOAD DATA")

    print("📂 Loading Club América DNA profile...")
    america_dna = load_america_dna("data/processed/america_dna_profile.json")
    print(f"   ✓ DNA loaded: Overall score = {america_dna['overall_score']:.2f}")
    print(f"   ✓ Tactical identity: {america_dna['tactical_identity']}")

    print("\n📂 Loading scouting pool players...")
    # Try parquet first, fallback to CSV if pyarrow has compatibility issues
    try:
        players_df = pd.read_parquet("data/processed/scouting_pool_all_metrics.parquet")
    except Exception as e:
        print(f"   ⚠️  Parquet read failed ({type(e).__name__}), using CSV fallback...")
        players_df = pd.read_csv("data/processed/scouting_pool_all_metrics.csv")

    print(f"   ✓ Loaded {len(players_df)} players from scouting pool")
    print(f"   ✓ Teams: {players_df['team.name'].nunique()}")

    # Fill NA values with 0 (defensive handling)
    players_df = players_df.fillna(0)
    print(f"   ✓ Cleaned NA values")

    print("\n📂 Loading Liga MX benchmarks (P90)...")
    benchmarks = load_benchmarks("data/processed/liga_mx_benchmarks_p90.json")
    print(f"   ✓ Benchmarks loaded")

    # -------------------------------------------------------------------------
    # STEP 2: EXTRACT AMÉRICA DNA VECTOR
    # -------------------------------------------------------------------------

    print_section("STEP 2: EXTRACT AMÉRICA DNA VECTOR")

    america_vector = extract_america_dna_vector(america_dna)

    print("América DNA Scores:")
    for i, dimension in enumerate(DNA_DIMENSIONS):
        score = america_vector[i]
        print(f"   • {dimension.capitalize():12s}: {score:.2f}")

    # -------------------------------------------------------------------------
    # STEP 3: IDENTIFY TEAM WEAKNESSES
    # -------------------------------------------------------------------------

    print_section("STEP 3: IDENTIFY TEAM WEAKNESSES")

    weaknesses = identify_team_weaknesses(america_dna, threshold=WEAKNESS_THRESHOLD)

    if weaknesses:
        print(f"Weaknesses identified (< {WEAKNESS_THRESHOLD}):")
        for dimension, gap in weaknesses.items():
            current_score = america_dna['dimensions'][dimension]['score']
            print(f"   • {dimension.capitalize():12s}: {current_score:.2f} (gap: {gap:.2f})")
    else:
        print(f"✅ No weaknesses found - all dimensions >= {WEAKNESS_THRESHOLD}")

    # -------------------------------------------------------------------------
    # STEP 4: CALCULATE FIT SCORES FOR ALL PLAYERS
    # -------------------------------------------------------------------------

    print_section("STEP 4: CALCULATE FIT SCORES")

    print(f"🔬 Calculating FitScore for {len(players_df)} players...\n")

    results = []

    for idx, player in players_df.iterrows():
        # Calculate all score components
        scores = calculate_fit_score(
            player,
            benchmarks,
            america_dna,
            america_vector,
            weaknesses
        )

        # Generate recommendation text
        recommendation = generate_recommendation_text(player, scores, america_dna, weaknesses)

        # Compile result
        result = {
            'player_name': player['player.name'],
            'team': player['team.name'],
            'position': player.get('primary_position', 'N/A'),
            'total_minutes': player['total_minutes'],
            'matches_played': player['matches_played'],
            'fit_score': round(scores['fit_score'], 2),
            'dna_match_score': round(scores['dna_match_score'], 2),
            'gap_filling_score': round(scores['gap_filling_score'], 2),
            'role_fit_score': round(scores['role_fit_score'], 2),
            'player_dna': {k: round(v, 2) for k, v in scores['player_dna'].items()},
            'why_good_fit': recommendation
        }

        results.append(result)

    print(f"   ✓ Calculated FitScore for all {len(results)} players")

    # -------------------------------------------------------------------------
    # STEP 5: RANK AND SELECT TOP RECOMMENDATIONS
    # -------------------------------------------------------------------------

    print_section("STEP 5: TOP RECOMMENDATIONS")

    # Sort by fit_score descending
    results_sorted = sorted(results, key=lambda x: x['fit_score'], reverse=True)

    # Get top N
    top_recommendations = results_sorted[:TOP_N]

    print(f"🏆 Top {TOP_N} Player Recommendations:\n")

    for i, player in enumerate(top_recommendations, 1):
        print(f"{i:2d}. {player['player_name']:25s} ({player['team']:15s}) - "
              f"FitScore: {player['fit_score']:5.2f}")
        print(f"     Position: {player['position']:10s} | "
              f"DNA Match: {player['dna_match_score']:5.2f} | "
              f"Gap Fill: {player['gap_filling_score']:5.2f}")
        print(f"     → {player['why_good_fit']}")
        print()

    # -------------------------------------------------------------------------
    # STEP 5B: WORST FIT PLAYERS (AVOID THESE)
    # -------------------------------------------------------------------------

    print_section("STEP 5B: WORST FIT PLAYERS (AVOID)")

    # Get bottom N (worst fits)
    worst_recommendations = results_sorted[-TOP_N:]
    worst_recommendations.reverse()  # Show worst first

    print(f"⚠️  Bottom {TOP_N} Players (Poorest Tactical Fit):\n")
    print("These players should be AVOIDED - they don't match América's style\n")

    for i, player in enumerate(worst_recommendations, 1):
        print(f"{i:2d}. {player['player_name']:25s} ({player['team']:15s}) - "
              f"FitScore: {player['fit_score']:5.2f}")
        print(f"     Position: {player['position']:10s} | "
              f"DNA Match: {player['dna_match_score']:5.2f} | "
              f"Gap Fill: {player['gap_filling_score']:5.2f}")

        # Generate "why bad fit" explanation
        reasons = []

        # Check DNA mismatch
        if player['dna_match_score'] < 70:
            reasons.append("Poor tactical compatibility")

        # Check which dimensions are weak
        weak_dims = []
        for dimension in DNA_DIMENSIONS:
            if player['player_dna'][dimension] < 50:
                weak_dims.append(dimension.capitalize())

        if weak_dims:
            dims_str = ", ".join(weak_dims[:3])
            reasons.append(f"Weak in: {dims_str}")

        # Check if doesn't fill gaps
        if player['gap_filling_score'] < 30:
            reasons.append("Doesn't address team weaknesses")

        if not reasons:
            reasons.append("Below-average across multiple dimensions")

        why_bad = "; ".join(reasons)
        print(f"     ⚠️  Why avoid: {why_bad}")
        print()

    # -------------------------------------------------------------------------
    # STEP 6: SAVE RESULTS
    # -------------------------------------------------------------------------

    print_section("STEP 6: SAVE RESULTS")

    # Save complete results as JSON
    output_json = {
        'players': results_sorted,
        'metadata': {
            'total_players_analyzed': len(results),
            'america_dna_version': america_dna['season'],
            'america_overall_score': america_dna['overall_score'],
            'benchmarks_percentile': 90,
            'weights': WEIGHTS,
            'weakness_threshold': WEAKNESS_THRESHOLD,
            'top_n': TOP_N,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }

    output_json_path = "data/processed/player_fit_scores.json"
    with open(output_json_path, 'w') as f:
        json.dump(output_json, f, indent=2)

    print(f"💾 Saved complete results to: {output_json_path}")
    print(f"   File size: {Path(output_json_path).stat().st_size / 1024:.1f} KB")

    # Save top recommendations as CSV
    top_df = pd.DataFrame([
        {
            'rank': i + 1,
            'player_name': p['player_name'],
            'team': p['team'],
            'position': p['position'],
            'fit_score': p['fit_score'],
            'dna_match': p['dna_match_score'],
            'gap_filling': p['gap_filling_score'],
            'minutes': p['total_minutes'],
            'matches': p['matches_played'],
            'why_recommend': p['why_good_fit']
        }
        for i, p in enumerate(top_recommendations)
    ])

    output_csv_path = "data/processed/top_recommendations.csv"
    top_df.to_csv(output_csv_path, index=False)

    print(f"💾 Saved top {TOP_N} recommendations to: {output_csv_path}")

    # Save worst recommendations as CSV
    worst_df = pd.DataFrame([
        {
            'rank': i + 1,
            'player_name': p['player_name'],
            'team': p['team'],
            'position': p['position'],
            'fit_score': p['fit_score'],
            'dna_match': p['dna_match_score'],
            'gap_filling': p['gap_filling_score'],
            'minutes': p['total_minutes'],
            'matches': p['matches_played'],
            'why_avoid': generate_why_avoid(p)
        }
        for i, p in enumerate(worst_recommendations)
    ])

    output_worst_csv_path = "data/processed/worst_recommendations.csv"
    worst_df.to_csv(output_worst_csv_path, index=False)

    print(f"💾 Saved worst {TOP_N} fits to: {output_worst_csv_path}")

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------

    print_section("SUMMARY")

    print("✅ FitScore calculation complete!\n")

    print(f"📊 Statistics:")
    print(f"   • Total players analyzed: {len(results)}")
    print(f"   • Best fit: {top_recommendations[0]['player_name']} "
          f"({top_recommendations[0]['fit_score']:.2f})")
    print(f"   • Worst fit: {worst_recommendations[0]['player_name']} "
          f"({worst_recommendations[0]['fit_score']:.2f})")
    print(f"   • Average FitScore: {np.mean([r['fit_score'] for r in results]):.2f}")
    print(f"   • Score range: {min(r['fit_score'] for r in results):.2f} - "
          f"{max(r['fit_score'] for r in results):.2f}")

    print(f"\n📁 Files created:")
    print(f"   ✓ {output_json_path} (complete results)")
    print(f"   ✓ {output_csv_path} (top {TOP_N} recommendations)")
    print(f"   ✓ {output_worst_csv_path} (worst {TOP_N} fits - AVOID)")

    print(f"\n🎯 Next Steps:")
    print(f"   1. Review top recommendations in CSV")
    print(f"   2. Analyze player DNA profiles in JSON")
    print(f"   3. Consider Phase 2 enhancements (visualization, role fit)")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
