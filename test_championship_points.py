#!/usr/bin/env python3
"""
Test script for Championship Points system
"""

from clean_tournament_sim import TournamentSimulator, NAStandingsManager

def test_na_standings_system():
    """Test the NA standings management system"""
    print("🧪 TESTING NA CHAMPIONSHIP POINTS SYSTEM")
    print("=" * 60)
    
    # Test NAStandingsManager independently
    print("\n1️⃣ Testing NAStandingsManager...")
    try:
        na_manager = NAStandingsManager()
        
        # Show current points structure
        na_manager.show_points_structure(32)
        
        # Show some sample players
        print(f"\n📋 SAMPLE NA PLAYERS (top 5):")
        top_players = na_manager.get_top_players(5)
        for i, (_, player) in enumerate(top_players.iterrows(), 1):
            print(f"{i}. {player['Top X Name']:20s} - {player['Total_CP']:4d} CP")
            print(f"   Current finishes: {player['CP Finishes']}")
        
        print("\n✅ NAStandingsManager loaded successfully!")
        
    except Exception as e:
        print(f"❌ Error testing NAStandingsManager: {e}")
        return False
    
    # Test integration with tournament simulator
    print("\n2️⃣ Testing Tournament Integration...")
    try:
        # Create simulator with NA tracking enabled
        sim = TournamentSimulator(track_na_standings=True)
        
        print(f"✅ TournamentSimulator created with NA tracking enabled")
        
        # Check if NA manager is properly initialized
        if sim.na_manager:
            print(f"✅ NA manager integrated successfully")
            print(f"   Tracking {len(sim.na_manager.na_standings)} NA players")
        else:
            print(f"❌ NA manager not properly initialized")
            return False
            
    except Exception as e:
        print(f"❌ Error testing tournament integration: {e}")
        return False
    
    return True

def test_small_tournament():
    """Run a small tournament to test the championship points flow"""
    print("\n3️⃣ Running Small Tournament Test...")
    
    try:
        # Create simulator 
        sim = TournamentSimulator(track_na_standings=True)
        
        if not sim.na_manager:
            print("❌ Cannot test without NA manager")
            return
        
        # Show some sample NA player data before tournament
        print(f"\n📊 BEFORE TOURNAMENT - Sample NA Players:")
        sample_players = ['Henry Chao', 'Charlie Lockyer', 'Caleb Rogerson']
        
        for name in sample_players:
            player = sim.na_manager.get_na_player_by_name(name)
            if player is not None:
                print(f"   {name:15s}: {player['Total_CP']:4d} CP (Finishes: {player['CP Finishes']})")
        
        # Run a smaller tournament for testing
        print(f"\n🎮 Running tournament with 100 players...")
        result = sim.run_tournament(num_players=100)
        
        if result:
            print(f"\n✅ Tournament completed successfully!")
            
            # Check if any sample players were in the tournament and got updated
            final_standings = result['final_standings']
            
            print(f"\n🏆 Tournament Results:")
            print(f"   Total players: {len(final_standings)}")
            if len(final_standings) > 0:
                winner = final_standings.iloc[0]
                print(f"   Winner: {winner['name']} ({winner['cp']} CP) - Placement: {winner['final_placement']}")
                
                # Show championship points structure
                print(f"\n🎯 Championship Points Sample:")
                for i in range(1, min(9, len(final_standings) + 1)):
                    points = sim.na_manager.get_championship_points(i)
                    print(f"   Place {i}: {points} points")
            
        else:
            print(f"❌ Tournament failed")
            
    except Exception as e:
        print(f"❌ Error running small tournament: {e}")

def demonstrate_points_updates():
    """Demonstrate how to update championship points"""
    print("\n4️⃣ Demonstrating Points Updates...")
    
    try:
        na_manager = NAStandingsManager()
        
        print(f"\n📋 Current placeholder points:")
        for key, value in na_manager.placeholder_points.items():
            print(f"   {key}: {value} points")
        
        # Example: Update with custom point values
        print(f"\n🔄 Updating with custom point values...")
        new_placeholder_points = {
            'a': 600,  # 1st place gets more points
            'b': 500,  # 2nd place
            'c': 400,  # 3rd-4th place
        }
        
        na_manager.update_placeholder_points(new_placeholder_points)
        
        print(f"\n📋 Updated points structure (first 16 places):")
        na_manager.show_points_structure(16)
        
    except Exception as e:
        print(f"❌ Error demonstrating points updates: {e}")

if __name__ == "__main__":
    print("🎮 POKEMON TOURNAMENT CHAMPIONSHIP POINTS SYSTEM TEST")
    print("=" * 70)
    
    # Run tests
    if test_na_standings_system():
        test_small_tournament()
        demonstrate_points_updates()
        
        print(f"\n🎉 All tests completed!")
        print(f"\n💡 Next steps:")
        print(f"   1. Provide real championship point values to replace placeholders")
        print(f"   2. Run full tournaments with sim.run_tournament()")
        print(f"   3. NA player standings will be automatically updated")
        print(f"   4. Use sim.na_manager.save_updated_standings() to export results")
    else:
        print(f"\n❌ Tests failed - check your data files and setup") 