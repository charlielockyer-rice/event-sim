#!/usr/bin/env python3
"""
Show Tournament Standings

This script demonstrates how to access and display the full tournament standings
after running a tournament simulation.
"""

from notebook_integration import run_skill_based_tournament
import pandas as pd

def show_tournament_standings(db_path: str, num_players: int = 1000):
    """Run tournament and show detailed standings"""
    
    print("Running tournament to demonstrate standings display...")
    
    # Run the tournament and capture results
    results = run_skill_based_tournament(
        db_path=db_path, 
        num_players=num_players, 
        skill_factor=0.50
    )
    
    # Access the final standings
    final_standings = results['final_standings']
    
    print(f"\n🏆 FULL FINAL STANDINGS:")
    print("=" * 90)
    print(f"Tournament ID: {results['tournament_id']}")
    print(f"Total Players: {len(final_standings):,}")
    print(f"Day 1 Advancement: {results['day1_advancement']} players")
    
    # Display standings with nice formatting
    print(f"\n{'Rank':<4} {'Name':<15} {'Zone':<6} {'CP':<6} {'Record':<12} {'Points':<6} {'Status'}")
    print("-" * 90)
    
    for i in range(min(50, len(final_standings))):
        row = final_standings.iloc[i]
        rank = i + 1
        record = f"{row['wins']}-{row['losses']}-{row['ties']}"
        
        # Add status indicators
        if rank <= 8:
            status = "🏆 Top Cut"
        elif rank <= 32:
            status = "⭐ Top 32"
        elif row['match_points'] >= 19:
            status = "✅ Made Day 2"
        else:
            status = "❌ Day 1 Exit"
        
        print(f"{rank:<4} {row['name']:<15} {row['rating_zone']:<6} {row['cp']:<6} {record:<12} {row['match_points']:<6} {status}")
    
    if len(final_standings) > 50:
        print(f"\n... and {len(final_standings) - 50} more players")
    
    # Show some statistics
    print(f"\n📊 SUMMARY STATISTICS:")
    print("-" * 40)
    
    # Champion info
    champion = final_standings.iloc[0]
    print(f"Champion: {champion['name']} ({champion['rating_zone']})")
    print(f"Champion CP: {champion['cp']}")
    print(f"Champion Record: {champion['wins']}-{champion['losses']}-{champion['ties']} ({champion['match_points']} pts)")
    
    # Zone breakdown in top cuts
    print(f"\nZone Performance:")
    for cut_size in [8, 16, 32]:
        if cut_size <= len(final_standings):
            top_cut = final_standings.head(cut_size)
            zone_counts = top_cut['rating_zone'].value_counts()
            intl_count = sum(zone_counts.get(zone, 0) for zone in ['EU', 'LATAM', 'OCE', 'MESA'])
            na_count = zone_counts.get('NA', 0)
            intl_pct = intl_count / cut_size * 100
            print(f"  Top {cut_size:2d}: {na_count:2d} NA, {intl_count:2d} International ({intl_pct:.1f}%)")
    
    return results

def show_standings_from_existing_results(results_dict):
    """
    Show standings if you already have results from a tournament
    
    Usage in Jupyter:
        results = run_skill_based_tournament('corrected_players.db', num_players=1000)
        show_standings_from_existing_results(results)
    """
    
    final_standings = results_dict['final_standings']
    
    print(f"🏆 TOURNAMENT STANDINGS")
    print("=" * 70)
    print(f"Tournament ID: {results_dict['tournament_id']}")
    
    # Quick display function
    print(f"\n{'Rank':<4} {'Name':<15} {'Zone':<6} {'CP':<6} {'Record':<12} {'Points'}")
    print("-" * 70)
    
    # Show top 30 by default
    for i in range(min(30, len(final_standings))):
        row = final_standings.iloc[i]
        rank = i + 1
        record = f"{row['wins']}-{row['losses']}-{row['ties']}"
        print(f"{rank:<4} {row['name']:<15} {row['rating_zone']:<6} {row['cp']:<6} {record:<12} {row['match_points']}")
    
    print(f"\n(Showing top 30 of {len(final_standings)} players)")

if __name__ == "__main__":
    # Example usage
    results = show_tournament_standings('corrected_players.db', num_players=1000)
    
    print(f"\n" + "="*70)
    print("💡 IN JUPYTER NOTEBOOK, YOU CAN:")
    print("="*70)
    print("# Option 1: Run tournament and see standings automatically")
    print("from show_standings import show_tournament_standings")
    print("results = show_tournament_standings('corrected_players.db', 1000)")
    print()
    print("# Option 2: Show standings from existing results")
    print("from show_standings import show_standings_from_existing_results")
    print("results = run_skill_based_tournament('corrected_players.db', 1000)")
    print("show_standings_from_existing_results(results)")
    print()
    print("# Option 3: Access data directly for custom analysis")
    print("standings = results['final_standings']")
    print("print(standings.head(20))  # Top 20")
    print("print(standings[standings['rating_zone'] != 'NA'])  # International only") 