#!/usr/bin/env python3
"""
Show Current NA Championship Standings
After running 100 events, display and save the current standings
"""

from clean_tournament_sim import TournamentSimulator
import pandas as pd

def main():
    print("🏆 CURRENT NA CHAMPIONSHIP STANDINGS")
    print("=" * 60)
    
    # Initialize simulator with NA tracking
    sim = TournamentSimulator(track_na_standings=True)
    
    if not sim.na_manager:
        print("❌ NA standings manager not available")
        return
    
    # Display current top standings
    print("\n📊 TOP 50 CURRENT STANDINGS:")
    top_standings = sim.na_manager.generate_final_rankings(top_n=50)
    
    # Save current standings
    print(f"\n💾 Saving current standings...")
    output_file = sim.na_manager.save_updated_standings()
    
    print(f"\n✅ Standings saved to: {output_file}")
    
    # Show some quick stats
    total_players = len(sim.na_manager.na_standings)
    players_with_points = len(sim.na_manager.na_standings[sim.na_manager.na_standings['Total_CP'] > 0])
    
    print(f"\n📈 QUICK STATS:")
    print(f"   Total NA players: {total_players:,}")
    print(f"   Players with CP: {players_with_points:,}")
    print(f"   Participation rate: {players_with_points/total_players*100:.1f}%")
    
    # Top 10 summary
    print(f"\n🥇 TOP 10 PLAYERS:")
    top10 = sim.na_manager.na_standings.sort_values('Total_CP', ascending=False).head(10)
    for i, (_, player) in enumerate(top10.iterrows(), 1):
        name = player['Top X Name'][:25]
        total_cp = int(player['Total_CP'])
        print(f"   {i:2d}. {name:<25} {total_cp:,} CP")

if __name__ == "__main__":
    main() 