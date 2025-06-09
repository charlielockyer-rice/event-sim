#!/usr/bin/env python3
"""
Analyze Individual Player Performance Across Tournaments
Load and analyze player performance from tournament standings data
"""

import pandas as pd
import statistics
from collections import defaultdict
import glob
import os

def analyze_player_across_tournaments(player_name, standings_dir):
    """Analyze a specific player's performance across all tournaments"""
    print(f"🔍 ANALYZING PLAYER: {player_name}")
    print("=" * 60)
    
    # Load all tournament standings
    standings_files = sorted(glob.glob(f"{standings_dir}/event_*_standings.csv"))
    
    if not standings_files:
        print(f"❌ No tournament standings found in {standings_dir}")
        return None
    
    player_results = []
    
    for file in standings_files:
        df = pd.read_csv(file)
        # Look for player (case insensitive)
        player_row = df[df['name'].str.lower().str.contains(player_name.lower(), na=False)]
        
        if not player_row.empty:
            player_data = player_row.iloc[0]
            event_num = player_data['event_number']
            placement = player_data['final_placement']
            
            player_results.append({
                'event': event_num,
                'placement': placement,
                'cp': player_data['cp'],
                'wins': player_data['wins'],
                'losses': player_data['losses'],
                'ties': player_data['ties'],
                'match_points': player_data['match_points'],
                'record': f"{player_data['wins']}-{player_data['losses']}-{player_data['ties']}",
                'day2_qualified': player_data['match_points'] >= 19
            })
    
    if not player_results:
        print(f"❌ Player '{player_name}' not found in any tournaments")
        return None
    
    # Analyze performance
    placements = [int(r['placement']) for r in player_results]  # Convert to int to avoid numpy issues
    appearances = len(player_results)
    
    print(f"📊 PERFORMANCE SUMMARY:")
    print(f"   Tournament appearances: {appearances}")
    print(f"   Average placement: {statistics.mean(placements):.1f}")
    print(f"   Best placement: {min(placements)}")
    print(f"   Worst placement: {max(placements)}")
    print(f"   Median placement: {statistics.median(placements):.1f}")
    print(f"   Placement std dev: {statistics.stdev(placements):.1f}" if len(placements) > 1 else "   Placement std dev: N/A (single event)")
    
    # Performance categories
    top8s = sum(1 for p in placements if p <= 8)
    top16s = sum(1 for p in placements if p <= 16)
    top32s = sum(1 for p in placements if p <= 32)
    day2s = sum(1 for r in player_results if r['day2_qualified'])
    
    print(f"\n🏆 ACHIEVEMENT BREAKDOWN:")
    print(f"   Top 8 finishes: {top8s}/{appearances} ({top8s/appearances*100:.1f}%)")
    print(f"   Top 16 finishes: {top16s}/{appearances} ({top16s/appearances*100:.1f}%)")
    print(f"   Top 32 finishes: {top32s}/{appearances} ({top32s/appearances*100:.1f}%)")
    print(f"   Day 2 qualifications: {day2s}/{appearances} ({day2s/appearances*100:.1f}%)")
    
    # Event-by-event breakdown
    print(f"\n📋 EVENT-BY-EVENT RESULTS:")
    print(f"{'Event':<6} {'Place':<6} {'Record':<8} {'Points':<6} {'Day 2'}")
    print("-" * 40)
    for result in player_results:
        day2_status = "✅" if result['day2_qualified'] else "❌"
        print(f"{result['event']:<6} {result['placement']:<6} {result['record']:<8} {result['match_points']:<6} {day2_status}")
    
    return player_results

def load_performance_analysis(standings_dir):
    """Load the pre-computed player performance analysis"""
    performance_file = f"{standings_dir}/player_performance_analysis.csv"
    
    if not os.path.exists(performance_file):
        print(f"❌ Performance analysis file not found: {performance_file}")
        return None
    
    return pd.read_csv(performance_file)

def show_top_performers(standings_dir, n=20):
    """Show top N performers from the analysis"""
    df = load_performance_analysis(standings_dir)
    
    if df is None:
        return
    
    print(f"🏆 TOP {n} PERFORMERS (by average placement)")
    print("=" * 100)
    print(f"{'Rank':<4} {'Player Name':<25} {'CP':<5} {'Apps':<4} {'Avg':<6} {'Best':<5} {'T8s':<4} {'T16s':<5} {'Day2%':<6} {'Consistency'}")
    print("-" * 100)
    
    top_n = df.head(n)
    for i, (_, player) in enumerate(top_n.iterrows(), 1):
        name = player['name'][:24]
        cp = int(player['cp'])
        apps = int(player['appearances'])
        avg = player['avg_placement']
        best = int(player['best_placement'])
        t8s = int(player['top8_finishes'])
        t16s = int(player['top16_finishes'])
        day2_pct = player['day2_rate'] * 100
        consistency = player['placement_consistency']
        
        print(f"{i:<4} {name:<25} {cp:<5} {apps:<4} {avg:<6.1f} {best:<5} {t8s:<4} {t16s:<5} {day2_pct:<6.1f} {consistency:.3f}")

def find_most_consistent_players(standings_dir, min_appearances=10):
    """Find players with the most consistent performance"""
    df = load_performance_analysis(standings_dir)
    
    if df is None:
        return
    
    # Filter players with minimum appearances and sort by consistency
    consistent_players = df[df['appearances'] >= min_appearances].sort_values('placement_consistency', ascending=False)
    
    print(f"\n🎯 MOST CONSISTENT PLAYERS (min {min_appearances} appearances)")
    print("=" * 80)
    print(f"{'Rank':<4} {'Player Name':<25} {'CP':<5} {'Apps':<4} {'Avg±Std':<12} {'Consistency'}")
    print("-" * 80)
    
    for i, (_, player) in enumerate(consistent_players.head(10).iterrows(), 1):
        name = player['name'][:24]
        cp = int(player['cp'])
        apps = int(player['appearances'])
        avg = player['avg_placement']
        std = player['placement_std']
        consistency = player['placement_consistency']
        
        print(f"{i:<4} {name:<25} {cp:<5} {apps:<4} {avg:.1f}±{std:.1f}   {consistency:.3f}")

def main():
    """Interactive analysis"""
    print("🔍 TOURNAMENT PLAYER PERFORMANCE ANALYZER")
    print("=" * 50)
    
    # Look for tournament standings directories - check for 'complete' first, then timestamped ones
    if os.path.isdir("tournament_standings_complete"):
        latest_dir = "tournament_standings_complete"
        print(f"📁 Using complete standings: {latest_dir}")
    else:
        standings_dirs = sorted([d for d in glob.glob("tournament_standings_*") if os.path.isdir(d)])
        
        if not standings_dirs:
            print("❌ No tournament standings directories found.")
            print("   Run a multi-event simulation first with save_individual_standings=True")
            return
        
        latest_dir = standings_dirs[-1]
        print(f"📁 Using latest standings: {latest_dir}")
    
    # Check what files are available
    files = os.listdir(latest_dir)
    event_files = [f for f in files if f.startswith('event_') and f.endswith('.csv')]
    
    print(f"📊 Found {len(event_files)} tournament events")
    
    # Show overview
    if 'player_performance_analysis.csv' in files:
        print(f"\n🏆 PERFORMANCE OVERVIEW:")
        show_top_performers(latest_dir, 15)
        
        print(f"\n🎯 CONSISTENCY LEADERS:")
        find_most_consistent_players(latest_dir, min_appearances=5)
    
    print(f"\n💡 USAGE EXAMPLES:")
    print(f"   # Analyze specific player:")
    print(f"   analyze_player_across_tournaments('Jordan Green', '{latest_dir}')")
    print(f"   ")
    print(f"   # Show top performers:")
    print(f"   show_top_performers('{latest_dir}', 25)")
    print(f"   ")
    print(f"   # Find consistent players:")
    print(f"   find_most_consistent_players('{latest_dir}', min_appearances=20)")
    
    return latest_dir

if __name__ == "__main__":
    latest_dir = main() 