#!/usr/bin/env python3
"""
Initial Exploratory Data Analysis for Club América Player Recommendation System
Using authenticated StatsBomb API access for Liga MX data
"""

import pandas as pd
import numpy as np
from statsbombpy import sb
import warnings
import os

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

# Credentials
CREDS = {"user": "itam_hackathon@hudl.com", "passwd": "pGwIprel"}

def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def main():
    print_section("CLUB AMÉRICA - INITIAL DATA EXPLORATION (AUTHENTICATED)")

    # 1. Get competitions with authentication
    print("📊 Fetching available competitions with credentials...")
    competitions = sb.competitions(creds=CREDS)
    print(f"   Total competitions available: {len(competitions)}")

    # 2. Filter for Liga MX
    print("\n🇲🇽 Filtering for Liga MX...")
    liga_mx = competitions[competitions['competition_name'].str.contains('Liga MX', case=False, na=False)]

    if len(liga_mx) == 0:
        print("\n⚠️  No 'Liga MX' found. Searching for 'Mexico' or 'Mexican'...")
        liga_mx = competitions[
            competitions['competition_name'].str.contains('Mexico', case=False, na=False) |
            competitions['country_name'].str.contains('Mexico', case=False, na=False)
        ]

    if len(liga_mx) == 0:
        print("\n❌ No Liga MX data found. Available competitions:")
        print("\nAll competitions:")
        print(competitions[['competition_id', 'competition_name', 'country_name', 'season_name']].to_string())
        return

    print(f"   Liga MX seasons found: {len(liga_mx)}")
    print("\n   Available seasons:")
    for idx, row in liga_mx.sort_values('season_name').iterrows():
        print(f"      - {row['season_name']} (comp_id: {row['competition_id']}, season_id: {row['season_id']})")

    # 3. Get all matches
    print("\n⚽ Fetching matches for each season...")
    all_matches = []

    for idx, row in liga_mx.iterrows():
        comp_id = row['competition_id']
        season_id = row['season_id']
        season_name = row['season_name']

        try:
            matches = sb.matches(competition_id=comp_id, season_id=season_id, creds=CREDS)
            matches['season_name'] = season_name
            all_matches.append(matches)
            print(f"   ✓ {season_name}: {len(matches)} matches")
        except Exception as e:
            print(f"   ✗ {season_name}: Error - {e}")

    if not all_matches:
        print("\n❌ No matches found")
        return

    df_matches = pd.concat(all_matches, ignore_index=True)
    print(f"\n   Total matches collected: {len(df_matches)}")

    # Save matches data
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    matches_file = os.path.join(data_dir, 'liga_mx_matches.csv')
    df_matches.to_csv(matches_file, index=False)
    print(f"   💾 Saved to: {matches_file}")

    # Show available teams
    print("\n📋 Teams in dataset:")
    all_teams = pd.concat([df_matches['home_team'], df_matches['away_team']]).unique()
    for i, team in enumerate(sorted(all_teams), 1):
        print(f"   {i:2d}. {team}")

    # 4. Find Club América
    print_section("CLUB AMÉRICA ANALYSIS")

    america_matches = df_matches[
        (df_matches['home_team'].str.contains('América', case=False, na=False)) |
        (df_matches['away_team'].str.contains('América', case=False, na=False))
    ]

    if len(america_matches) == 0:
        print("❌ Club América not found with 'América'. Trying 'America'...")
        america_matches = df_matches[
            (df_matches['home_team'].str.contains('America', case=False, na=False)) |
            (df_matches['away_team'].str.contains('America', case=False, na=False))
        ]

    if len(america_matches) == 0:
        print("❌ Club América not found.")
        return

    print(f"✓ Found Club América matches")
    print(f"\n📈 Club América Statistics:")
    print(f"   Total matches: {len(america_matches)}")
    print(f"\n   Matches by season:")
    for season, count in america_matches['season_name'].value_counts().sort_index().items():
        print(f"      - {season}: {count} matches")

    # Calculate results
    def get_team_result(row, team_name='América'):
        is_home = team_name.lower() in row['home_team'].lower()
        if is_home:
            if row['home_score'] > row['away_score']:
                return 'Win'
            elif row['home_score'] < row['away_score']:
                return 'Loss'
            else:
                return 'Draw'
        else:
            if row['away_score'] > row['home_score']:
                return 'Win'
            elif row['away_score'] < row['home_score']:
                return 'Loss'
            else:
                return 'Draw'

    america_matches['result'] = america_matches.apply(get_team_result, axis=1)

    wins = (america_matches['result'] == 'Win').sum()
    draws = (america_matches['result'] == 'Draw').sum()
    losses = (america_matches['result'] == 'Loss').sum()
    win_rate = wins / len(america_matches) * 100

    print(f"\n   Results:")
    print(f"      - Wins: {wins} ({wins/len(america_matches)*100:.1f}%)")
    print(f"      - Draws: {draws} ({draws/len(america_matches)*100:.1f}%)")
    print(f"      - Losses: {losses} ({losses/len(america_matches)*100:.1f}%)")
    print(f"      - Win rate: {win_rate:.1f}%")

    # Save América matches
    america_file = os.path.join(data_dir, 'club_america_matches.csv')
    america_matches.to_csv(america_file, index=False)
    print(f"\n   💾 Saved Club América matches to: {america_file}")

    # 5. Sample event data
    print_section("EVENT DATA EXPLORATION")

    sample_match = america_matches.iloc[0]
    sample_match_id = sample_match['match_id']

    print(f"Loading sample match:")
    print(f"   Match: {sample_match['home_team']} vs {sample_match['away_team']}")
    print(f"   Date: {sample_match['match_date']}")
    print(f"   Score: {sample_match['home_score']} - {sample_match['away_score']}")

    try:
        print(f"\n⏳ Fetching event data (this may take a moment)...")
        events = sb.events(match_id=sample_match_id, creds=CREDS)

        print(f"\n📊 Event Data Summary:")
        print(f"   Total events: {len(events)}")
        print(f"   Event types: {events['type'].nunique()}")
        print(f"   Columns: {len(events.columns)}")

        print(f"\n   Top 10 event types:")
        for event_type, count in events['type'].value_counts().head(10).items():
            print(f"      - {event_type}: {count}")

        # Check for 360 data
        cols_360 = [col for col in events.columns if '360' in col.lower() or 'freeze' in col.lower() or 'visible' in col.lower()]
        if cols_360:
            print(f"\n   360-related columns found: {cols_360}")
            for col in cols_360:
                non_null = events[col].notna().sum()
                print(f"      - {col}: {non_null} events ({non_null/len(events)*100:.1f}%)")
        else:
            print(f"\n   No 360-related columns found in sample")

        # Player stats
        players = events[events['player'].notna()][['player', 'team', 'position']].drop_duplicates()
        print(f"\n   Players in match: {len(players)}")
        print(f"   Positions represented: {players['position'].nunique()}")

        # Save sample events
        sample_events_file = os.path.join(data_dir, 'sample_events.csv')
        events.to_csv(sample_events_file, index=False)
        print(f"\n   💾 Saved sample events to: {sample_events_file}")

    except Exception as e:
        print(f"\n❌ Error loading events: {e}")
        import traceback
        traceback.print_exc()

    # 6. Summary
    print_section("SUMMARY")

    print("✅ Data successfully loaded and explored!")
    print(f"\nKey Findings:")
    print(f"   • Liga MX seasons available: {len(liga_mx)}")
    print(f"   • Total matches: {len(df_matches)}")
    print(f"   • Teams in dataset: {len(all_teams)}")
    print(f"   • Club América matches: {len(america_matches)}")
    print(f"   • Club América win rate: {win_rate:.1f}%")

    if 'events' in locals():
        print(f"   • Event data accessible: Yes")
        print(f"   • Sample match events: {len(events)}")

    print("\n📁 Files saved to data/ directory:")
    print("   • liga_mx_matches.csv")
    print("   • club_america_matches.csv")
    if 'events' in locals():
        print("   • sample_events.csv")

    print("\n🎯 Next Steps:")
    print("   1. Analyze Club América's tactical profile")
    print("   2. Deep dive into player statistics")
    print("   3. Explore passing networks and defensive actions")
    print("   4. Build player evaluation framework")

    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
