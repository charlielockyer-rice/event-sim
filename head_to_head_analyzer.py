#!/usr/bin/env python3
"""
Head-to-Head Player Analysis
Analyze specific player matchups across all tournament runs
"""

import pandas as pd
import glob
import ast
from collections import defaultdict, Counter

def analyze_head_to_head(player_a, player_b, standings_dir):
    """Analyze head-to-head record between two specific players"""
    print(f"⚔️  HEAD-TO-HEAD ANALYSIS: {player_a} vs {player_b}")
    print("=" * 80)
    
    # Load all tournament standings
    standings_files = sorted(glob.glob(f"{standings_dir}/event_*_standings.csv"))
    
    if not standings_files:
        print(f"❌ No tournament standings found in {standings_dir}")
        return None
    
    matchups = []
    
    for file in standings_files:
        df = pd.read_csv(file)
        # Extract event number from filename like "event_001_standings.csv"
        filename = file.split('/')[-1]  # Get just the filename
        if filename.startswith('event_'):
            event_num = int(filename.split('_')[1])
        else:
            continue
        
        # Find both players in this tournament
        player_a_data = df[df['name'] == player_a]
        player_b_data = df[df['name'] == player_b]
        
        if player_a_data.empty or player_b_data.empty:
            continue
            
        # Parse match history for player A (handle numpy types)
        match_history_str = player_a_data.iloc[0]['match_history']
        # Replace numpy types that can't be parsed by ast.literal_eval
        match_history_str = match_history_str.replace('np.int64(', '').replace(')', '')
        player_a_history = ast.literal_eval(match_history_str)
        
        # Check if they played against each other
        for match in player_a_history:
            if match['opponent'] == player_b:
                matchup_data = {
                    'event': event_num,
                    'round': match['round'],
                    'player_a_result': match['result'],
                    'player_b_result': 'loss' if match['result'] == 'win' else ('win' if match['result'] == 'loss' else 'tie'),
                    'player_a_cp': player_a_data.iloc[0]['cp'],
                    'player_b_cp': match['opponent_cp'],
                    'brutal': match['brutal'],
                    'player_a_final_placement': player_a_data.iloc[0]['final_placement'],
                    'player_b_final_placement': player_b_data.iloc[0]['final_placement']
                }
                matchups.append(matchup_data)
    
    if not matchups:
        print(f"🚫 {player_a} and {player_b} never played against each other in {len(standings_files)} tournaments")
        return None
    
    # Analyze the matchups
    total_matches = len(matchups)
    player_a_wins = sum(1 for m in matchups if m['player_a_result'] == 'win')
    player_b_wins = sum(1 for m in matchups if m['player_a_result'] == 'loss')
    ties = sum(1 for m in matchups if m['player_a_result'] == 'tie')
    
    # Calculate win percentages
    player_a_win_pct = (player_a_wins / total_matches) * 100 if total_matches > 0 else 0
    player_b_win_pct = (player_b_wins / total_matches) * 100 if total_matches > 0 else 0
    tie_pct = (ties / total_matches) * 100 if total_matches > 0 else 0
    
    # Summary statistics
    print(f"📊 OVERALL RECORD:")
    print(f"   Total matches: {total_matches}")
    print(f"   {player_a}: {player_a_wins} wins ({player_a_win_pct:.1f}%)")
    print(f"   {player_b}: {player_b_wins} wins ({player_b_win_pct:.1f}%)")
    print(f"   Ties: {ties} ({tie_pct:.1f}%)")
    
    # CP advantage analysis
    avg_cp_diff = sum(m['player_a_cp'] - m['player_b_cp'] for m in matchups) / total_matches
    print(f"\n💪 CP ANALYSIS:")
    print(f"   Average CP difference: {avg_cp_diff:+.0f} (+ means {player_a} higher)")
    
    # Brutal matchup analysis
    brutal_matches = [m for m in matchups if m['brutal']]
    if brutal_matches:
        print(f"   Brutal matchups: {len(brutal_matches)}/{total_matches}")
    
    # Performance comparison
    player_a_avg_placement = sum(m['player_a_final_placement'] for m in matchups) / total_matches
    player_b_avg_placement = sum(m['player_b_final_placement'] for m in matchups) / total_matches
    
    print(f"\n🏆 TOURNAMENT PERFORMANCE (when they played):")
    print(f"   {player_a} average placement: {player_a_avg_placement:.1f}")
    print(f"   {player_b} average placement: {player_b_avg_placement:.1f}")
    
    # Detailed match history
    print(f"\n📋 DETAILED MATCH HISTORY:")
    print(f"{'Event':<8}{'Round':<8}{'Winner':<25}{'CP Diff':<10}{'Brutal':<8}{'Final Placements'}")
    print("-" * 80)
    
    for match in sorted(matchups, key=lambda x: x['event']):
        winner = player_a if match['player_a_result'] == 'win' else (player_b if match['player_a_result'] == 'loss' else 'TIE')
        cp_diff = match['player_a_cp'] - match['player_b_cp']
        brutal = "Yes" if match['brutal'] else "No"
        placements = f"{match['player_a_final_placement']} vs {match['player_b_final_placement']}"
        
        print(f"{match['event']:<8}{match['round']:<8}{winner:<25}{cp_diff:+4.0f}{'':6}{brutal:<8}{placements}")
    
    return {
        'total_matches': total_matches,
        'player_a_wins': player_a_wins,
        'player_b_wins': player_b_wins,
        'ties': ties,
        'player_a_win_pct': player_a_win_pct,
        'player_b_win_pct': player_b_win_pct,
        'avg_cp_difference': avg_cp_diff,
        'detailed_matches': matchups
    }

def analyze_all_opponents(player_name, standings_dir, top_n=20):
    """Analyze a player's record against all opponents they've faced"""
    print(f"🎯 ALL OPPONENTS ANALYSIS: {player_name}")
    print("=" * 60)
    
    # Load all tournament standings
    standings_files = sorted(glob.glob(f"{standings_dir}/event_*_standings.csv"))
    
    if not standings_files:
        print(f"❌ No tournament standings found in {standings_dir}")
        return None
    
    opponent_records = defaultdict(lambda: {'wins': 0, 'losses': 0, 'ties': 0, 'matches': []})
    
    for file in standings_files:
        df = pd.read_csv(file)
        # Extract event number from filename like "event_001_standings.csv"
        filename = file.split('/')[-1]  # Get just the filename
        if filename.startswith('event_'):
            event_num = int(filename.split('_')[1])
        else:
            continue
        
        # Find player in this tournament
        player_data = df[df['name'] == player_name]
        
        if player_data.empty:
            continue
            
        # Parse match history (handle numpy types)
        match_history_str = player_data.iloc[0]['match_history']
        # Replace numpy types that can't be parsed by ast.literal_eval
        match_history_str = match_history_str.replace('np.int64(', '').replace(')', '')
        match_history = ast.literal_eval(match_history_str)
        
        for match in match_history:
            opponent = match['opponent']
            result = match['result']
            
            # Record the result
            if result == 'win':
                opponent_records[opponent]['wins'] += 1
            elif result == 'loss':
                opponent_records[opponent]['losses'] += 1
            else:  # tie
                opponent_records[opponent]['ties'] += 1
            
            opponent_records[opponent]['matches'].append({
                'event': event_num,
                'round': match['round'],
                'result': result,
                'opponent_cp': match['opponent_cp'],
                'player_cp': player_data.iloc[0]['cp']
            })
    
    # Calculate win percentages and sort
    opponent_stats = []
    for opponent, record in opponent_records.items():
        total = record['wins'] + record['losses'] + record['ties']
        if total > 0:
            win_pct = (record['wins'] / total) * 100
            opponent_stats.append({
                'opponent': opponent,
                'total_matches': total,
                'wins': record['wins'],
                'losses': record['losses'],
                'ties': record['ties'],
                'win_percentage': win_pct,
                'matches': record['matches']
            })
    
    # Sort by most matches played, then by win percentage
    opponent_stats.sort(key=lambda x: (x['total_matches'], x['win_percentage']), reverse=True)
    
    print(f"\n📊 TOP {top_n} MOST FACED OPPONENTS:")
    print(f"{'Opponent':<25}{'Matches':<10}{'W-L-T':<12}{'Win %':<10}")
    print("-" * 60)
    
    for stat in opponent_stats[:top_n]:
        wlt = f"{stat['wins']}-{stat['losses']}-{stat['ties']}"
        print(f"{stat['opponent']:<25}{stat['total_matches']:<10}{wlt:<12}{stat['win_percentage']:.1f}%")
    
    # Best and worst matchups
    frequent_opponents = [s for s in opponent_stats if s['total_matches'] >= 3]
    
    if frequent_opponents:
        print(f"\n🏆 BEST MATCHUPS (3+ matches):")
        best = sorted(frequent_opponents, key=lambda x: x['win_percentage'], reverse=True)[:5]
        for stat in best:
            wlt = f"{stat['wins']}-{stat['losses']}-{stat['ties']}"
            print(f"   {stat['opponent']}: {wlt} ({stat['win_percentage']:.1f}%)")
        
        print(f"\n💀 WORST MATCHUPS (3+ matches):")
        worst = sorted(frequent_opponents, key=lambda x: x['win_percentage'])[:5]
        for stat in worst:
            wlt = f"{stat['wins']}-{stat['losses']}-{stat['ties']}"
            print(f"   {stat['opponent']}: {wlt} ({stat['win_percentage']:.1f}%)")
    
    return opponent_stats

def main():
    # Example usage
    standings_dir = "tournament_standings_20250608_221840"  # Update this path
    
    print("🔍 HEAD-TO-HEAD ANALYSIS EXAMPLES")
    print("=" * 50)
    
    # Example head-to-head
    analyze_head_to_head("Henry Chao", "Samuel Scime", standings_dir)
    
    print("\n" + "="*80 + "\n")
    
    # Example all opponents analysis
    analyze_all_opponents("Henry Chao", standings_dir, top_n=15)

if __name__ == "__main__":
    main() 