#!/usr/bin/env python3
"""
Demonstration of the full championship points system
"""

from clean_tournament_sim import TournamentSimulator, NAStandingsManager

def demo_full_championship_system():
    """Demonstrate the complete championship points system"""
    print("🏆 FULL CHAMPIONSHIP POINTS SYSTEM DEMONSTRATION")
    print("=" * 70)
    
    # Create simulator with NA tracking
    sim = TournamentSimulator(track_na_standings=True)
    
    if not sim.na_manager:
        print("❌ NA standings not available")
        return
    
    # Show initial championship points structure
    print("\n📋 CHAMPIONSHIP POINTS STRUCTURE:")
    sim.na_manager.show_points_structure(64)
    
    # Show initial top players
    print(f"\n📊 INITIAL TOP 10 NA PLAYERS:")
    initial_top = sim.na_manager.get_top_players(10)
    for i, (_, player) in enumerate(initial_top.iterrows(), 1):
        print(f"{i:2d}. {player['Top X Name']:25s} {player['Total_CP']:4d} CP "
              f"(TopX: {player['Top_X_CP']:4d}, Locals: {player['Locals CP']:3d})")
        if i <= 3:  # Show finishes for top 3
            print(f"     Finishes: {player['CP Finishes']}")
    
    # Demonstrate what happens when we update points for existing top players
    print(f"\n🎯 ANALYZING SOME TOP PLAYERS' CURRENT FINISHES:")
    sample_names = ['Henry Chao', 'Caleb Rogerson', 'Rahul Reddy']
    
    for name in sample_names:
        player = sim.na_manager.get_na_player_by_name(name)
        if player is not None:
            finishes = sim.na_manager.parse_cp_finishes(player['CP Finishes'])
            print(f"   {name:15s}: {finishes} (min: {min(finishes) if finishes else 0})")
            print(f"                  Would a 1st place (500 pts) help? {'YES' if not finishes or 500 > min(finishes) else 'NO'}")
    
    # Run a full tournament
    print(f"\n🎮 RUNNING FULL TOURNAMENT (3700 players)...")
    result = sim.run_tournament(num_players=3700)
    
    if result:
        print(f"\n✅ Tournament completed!")
        
        # Save updated standings
        output_file = sim.na_manager.save_updated_standings()
        print(f"💾 Updated standings saved to: {output_file}")
        
        # Show changes in top 10
        print(f"\n📈 FINAL TOP 10 NA PLAYERS AFTER TOURNAMENT:")
        final_top = sim.na_manager.get_top_players(10)
        
        for i, (_, player) in enumerate(final_top.iterrows(), 1):
            # Check if this player was in initial top 10
            was_in_initial = any(player['Top X Name'] == initial_player['Top X Name'] 
                               for _, initial_player in initial_top.iterrows())
            
            change_indicator = ""
            if was_in_initial:
                # Find their initial position
                for j, (_, initial_player) in enumerate(initial_top.iterrows(), 1):
                    if player['Top X Name'] == initial_player['Top X Name']:
                        if j > i:
                            change_indicator = f" ⬆️ (was #{j})"
                        elif j < i:
                            change_indicator = f" ⬇️ (was #{j})"
                        else:
                            change_indicator = f" ➡️ (same)"
                        break
            else:
                change_indicator = " 🆕 (new to top 10)"
            
            print(f"{i:2d}. {player['Top X Name']:25s} {player['Total_CP']:4d} CP{change_indicator}")
        
        # Show some statistics about the tournament
        final_standings = result['final_standings']
        print(f"\n📊 TOURNAMENT STATISTICS:")
        print(f"   Total players: {len(final_standings):,}")
        
        # Count NA players in top cuts
        na_names = set(sim.na_manager.na_standings['NA Name'].str.lower()) | \
                  set(sim.na_manager.na_standings['Top X Name'].str.lower())
        
        for cut_size in [8, 16, 32, 64]:
            if cut_size <= len(final_standings):
                top_cut = final_standings.head(cut_size)
                na_in_cut = sum(1 for name in top_cut['name'] 
                              if name.lower() in na_names)
                print(f"   Top {cut_size:2d}: {na_in_cut:2d} NA players ({na_in_cut/cut_size*100:4.1f}%)")
        
        # Show point distribution for top finishers
        print(f"\n🏅 CHAMPIONSHIP POINTS AWARDED (Top 20):")
        top_20 = final_standings.head(20)
        for i, (_, player) in enumerate(top_20.iterrows(), 1):
            placement = int(player['final_placement'])
            points = sim.na_manager.get_championship_points(placement)
            is_na = player['name'].lower() in na_names
            na_indicator = " 🇺🇸" if is_na else ""
            print(f"   {placement:2d}. {player['name'][:20]:20s} {points:3d} pts{na_indicator}")
        
        return output_file
    
    else:
        print("❌ Tournament failed")
        return None

def analyze_points_impact():
    """Analyze the impact of different point structures"""
    print(f"\n🔬 ANALYZING DIFFERENT POINT STRUCTURES")
    print("=" * 50)
    
    na_manager = NAStandingsManager()
    
    # Show current structure
    print(f"\n📋 CURRENT STRUCTURE (sample placements):")
    key_placements = [1, 2, 3, 4, 5, 8, 9, 16, 17, 32, 33, 64, 65, 128, 129, 256]
    for placement in key_placements:
        points = na_manager.get_championship_points(placement)
        print(f"   Place {placement:3d}: {points} points")
    
    # Show what different structures might look like
    print(f"\n💡 ALTERNATIVE POINT STRUCTURES:")
    
    # Example 1: More top-heavy
    print(f"\n   Example 1 - More top-heavy:")
    alt_points_1 = {'a': 1000, 'b': 750, 'c': 500, 'd': 350, 'e': 250}
    temp_manager = NAStandingsManager()
    temp_manager.update_placeholder_points(alt_points_1)
    for placement in [1, 2, 3, 5, 9, 17]:
        points = temp_manager.get_championship_points(placement)
        print(f"     Place {placement:2d}: {points} points")
    
    # Example 2: More flat
    print(f"\n   Example 2 - More flat distribution:")
    alt_points_2 = {'a': 400, 'b': 350, 'c': 300, 'd': 275, 'e': 250}
    temp_manager2 = NAStandingsManager()
    temp_manager2.update_placeholder_points(alt_points_2)
    for placement in [1, 2, 3, 5, 9, 17]:
        points = temp_manager2.get_championship_points(placement)
        print(f"     Place {placement:2d}: {points} points")

if __name__ == "__main__":
    # Run the demonstration
    output_file = demo_full_championship_system()
    
    if output_file:
        analyze_points_impact()
        
        print(f"\n🎉 DEMONSTRATION COMPLETE!")
        print(f"\n📋 Summary:")
        print(f"   ✅ Championship points system fully integrated")
        print(f"   ✅ NA player standings automatically updated")
        print(f"   ✅ 5-finish rule properly implemented")
        print(f"   ✅ Updated standings saved to: {output_file}")
        print(f"\n💡 You can now:")
        print(f"   1. Provide real point values using sim.na_manager.update_placeholder_points()")
        print(f"   2. Run multiple tournaments and see cumulative effects")
        print(f"   3. Export updated standings anytime with save_updated_standings()")
        print(f"   4. Analyze individual player progression")
    else:
        print(f"\n❌ Demonstration failed") 