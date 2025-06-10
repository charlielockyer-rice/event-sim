#!/usr/bin/env python3
"""
Analyze 140th place cutoff from existing tournament data
"""

from player_database import PlayerDatabase
from clean_tournament_sim import TournamentSimulator
import pandas as pd
import numpy as np

def analyze_140th_place_from_database():
    """Analyze 140th place cutoff from existing tournament data"""
    
    print("🎯 ANALYZING 140TH PLACE CUTOFF FROM EXISTING TOURNAMENTS")
    print("=" * 60)
    
    # Initialize
    sim = TournamentSimulator(track_na_standings=True)
    db = PlayerDatabase()
    
    if not sim.na_manager:
        print("❌ Could not load NA standings manager")
        return None
    
    # Get initial baseline
    initial_standings = sim.na_manager.na_standings.copy()
    initial_rankings = initial_standings.sort_values('Total_CP', ascending=False).reset_index(drop=True)
    baseline_140th = initial_rankings.iloc[139]['Total_CP']  # 140th place (0-indexed)
    baseline_name = initial_rankings.iloc[139]['Top X Name']
    
    print(f"📊 Baseline 140th place: {baseline_name} with {baseline_140th:,} CP")
    
    # Get all players with tournament history
    all_players = db.load_all_players()
    players_with_history = [p for p in all_players if p.tournament_history]
    
    # Extract all unique tournament IDs
    all_tournament_ids = set()
    for player in players_with_history:
        for tournament in player.tournament_history:
            all_tournament_ids.add(tournament['tournament_id'])
    
    tournament_ids = sorted(list(all_tournament_ids))
    print(f"📋 Found {len(tournament_ids)} tournaments in database")
    
    # Analyze 140th place after each tournament
    place_140_values = []
    tournament_details = []
    
    for i, tournament_id in enumerate(tournament_ids, 1):
        print(f"\n🏆 Analyzing Tournament {i}/{len(tournament_ids)}: {tournament_id}")
        
        # Reset standings to baseline
        sim.na_manager.na_standings = initial_standings.copy()
        
        # Process this specific tournament
        tournament_players = []
        for player in players_with_history:
            for tournament in player.tournament_history:
                if tournament['tournament_id'] == tournament_id:
                    tournament_players.append({
                        'player_name': player.name,
                        'final_placement': tournament['final_placement'],
                        'cp': player.cp,
                        'wins': tournament['wins'],
                        'losses': tournament['losses'],
                        'ties': tournament['ties']
                    })
                    break
        
        # Process results through NA manager
        if tournament_players:
            sim.na_manager.process_tournament_results(tournament_players)
            
            # Get 140th place after this tournament
            updated_rankings = sim.na_manager.na_standings.sort_values('Total_CP', ascending=False).reset_index(drop=True)
            place_140_total = updated_rankings.iloc[139]['Total_CP']
            place_140_name = updated_rankings.iloc[139]['Top X Name']
            
            place_140_values.append(place_140_total)
            
            change_from_baseline = place_140_total - baseline_140th
            print(f"   140th place: {place_140_name} with {place_140_total:,} CP ({change_from_baseline:+,})")
            
            tournament_details.append({
                'tournament_id': tournament_id,
                'tournament_num': i,
                'place_140_name': place_140_name,
                'place_140_total': place_140_total,
                'change_from_baseline': change_from_baseline,
                'participants': len(tournament_players)
            })
        else:
            print(f"   ❌ No participants found for tournament {tournament_id}")
    
    if not place_140_values:
        print("❌ No valid tournament data found")
        return None
    
    # Calculate statistics
    stats = {
        'baseline': baseline_140th,
        'min': np.min(place_140_values),
        'max': np.max(place_140_values),
        'mean': np.mean(place_140_values),
        'median': np.median(place_140_values),
        'std': np.std(place_140_values),
        'values': place_140_values,
        'num_tournaments': len(place_140_values),
        'changes': [v - baseline_140th for v in place_140_values]
    }
    
    # Display results
    print(f"\n📊 140TH PLACE CUTOFF ANALYSIS - FROM {len(place_140_values)} EXISTING TOURNAMENTS")
    print("=" * 70)
    print(f"Baseline 140th place:    {stats['baseline']:,} CP")
    print(f"Minimum cutoff:          {stats['min']:,} CP")
    print(f"Maximum cutoff:          {stats['max']:,} CP")
    print(f"Mean cutoff:             {stats['mean']:,.1f} CP")
    print(f"Median cutoff:           {stats['median']:,.1f} CP")
    print(f"Standard deviation:      {stats['std']:,.1f} CP")
    print(f"Total range:             {stats['max'] - stats['min']:,} CP")
    
    # Impact analysis
    mean_change = np.mean(stats['changes'])
    min_change = np.min(stats['changes'])
    max_change = np.max(stats['changes'])
    
    print(f"\n📈 IMPACT OF TOURNAMENTS:")
    print(f"Average impact per tournament: {mean_change:+,.1f} CP")
    print(f"Best case impact:              {max_change:+,.1f} CP")
    print(f"Worst case impact:             {min_change:+,.1f} CP")
    print(f"Percentage impact range:       {min_change/stats['baseline']*100:+.2f}% to {max_change/stats['baseline']*100:+.2f}%")
    
    # Show all values
    print(f"\n🔢 ALL 140TH PLACE VALUES:")
    for detail in tournament_details:
        print(f"   Tournament {detail['tournament_num']:2d}: {detail['place_140_total']:,} CP ({detail['change_from_baseline']:+,}) - {detail['place_140_name'][:25]}")
    
    # Save results
    import pandas as pd
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save detailed results
    df_results = pd.DataFrame(tournament_details)
    results_file = f"existing_140th_analysis_{timestamp}.csv"
    df_results.to_csv(results_file, index=False)
    
    # Save summary
    summary_file = f"existing_140th_summary_{timestamp}.txt"
    with open(summary_file, 'w') as f:
        f.write(f"140TH PLACE ANALYSIS FROM EXISTING TOURNAMENTS\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"=" * 50 + "\n\n")
        f.write(f"Tournaments analyzed: {stats['num_tournaments']}\n")
        f.write(f"Baseline 140th place: {stats['baseline']:,} CP\n\n")
        f.write(f"STATISTICS:\n")
        f.write(f"Min: {stats['min']:,} CP\n")
        f.write(f"Max: {stats['max']:,} CP\n")
        f.write(f"Mean: {stats['mean']:,.1f} CP\n")
        f.write(f"Median: {stats['median']:,.1f} CP\n")
        f.write(f"Std Dev: {stats['std']:,.1f} CP\n")
        f.write(f"Range: {stats['max'] - stats['min']:,} CP\n\n")
        f.write(f"ALL VALUES:\n")
        for i, value in enumerate(stats['values'], 1):
            f.write(f"Tournament {i}: {value:,} CP\n")
    
    print(f"\n💾 Results saved:")
    print(f"   Detailed data: {results_file}")
    print(f"   Summary:       {summary_file}")
    
    return {
        'statistics': stats,
        'tournament_details': tournament_details,
        'raw_data': place_140_values
    }

if __name__ == "__main__":
    results = analyze_140th_place_from_database() 