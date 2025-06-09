#!/usr/bin/env python3
"""
Test Individual Tournament Standings Tracking
Demonstrates the new functionality to save and analyze individual tournament results
"""

from clean_tournament_sim import TournamentSimulator
from analyze_player_performance import analyze_player_across_tournaments, show_top_performers

def main():
    print("🎮 TESTING INDIVIDUAL TOURNAMENT STANDINGS TRACKING")
    print("=" * 60)
    
    # Initialize simulator
    sim = TournamentSimulator(track_na_standings=True)
    
    print(f"📊 Running 5 tournaments with individual standings tracking...")
    
    # Run multi-event simulation with individual standings saving
    results = sim.run_multi_event_simulation(
        num_events=5, 
        players_per_event=1000,  # Smaller for testing
        save_individual_standings=True
    )
    
    standings_dir = results['standings_directory']
    print(f"\n✅ Individual standings saved to: {standings_dir}")
    
    # Demonstrate player analysis
    print(f"\n🔍 DEMONSTRATING PLAYER ANALYSIS:")
    
    # Find a champion from one of the events
    if results['individual_standings']:
        # Get the champion from the first event
        first_event = results['individual_standings'][0]
        champion = first_event.iloc[0]
        champion_name = champion['name']
        
        print(f"\n📊 Analyzing champion: {champion_name}")
        analyze_player_across_tournaments(champion_name, standings_dir)
    
    print(f"\n📁 FILES CREATED:")
    print(f"   Directory: {standings_dir}/")
    print(f"   - event_001_standings.csv through event_005_standings.csv")
    print(f"   - player_performance_analysis.csv")
    print(f"   - tournament_summary.csv")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"   1. Run analyze_player_performance.py to explore all the data")
    print(f"   2. Use analyze_player_across_tournaments('PlayerName', '{standings_dir}') for specific analysis")
    print(f"   3. Open the CSV files in Excel/etc for custom analysis")
    
    return standings_dir

if __name__ == "__main__":
    test_dir = main() 