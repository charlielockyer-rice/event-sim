#!/usr/bin/env python3
"""
Clear all tournament data from database while keeping player base
This reduces file size dramatically for version control
"""

from player_database import PlayerDatabase
import os

def clear_tournament_data(db_path="custom_tournament_players.db"):
    """Clear all tournament history from database"""
    
    print(f"🧹 CLEARING TOURNAMENT DATA FROM DATABASE")
    print("=" * 50)
    
    # Check original file size
    if os.path.exists(db_path):
        original_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
        print(f"📊 Original database size: {original_size:.1f} MB")
    else:
        print(f"❌ Database file {db_path} not found")
        return
    
    # Load database
    db = PlayerDatabase(db_path)
    
    # Get stats before clearing
    stats_before = db.get_database_stats()
    print(f"📋 Before clearing:")
    print(f"   Total players: {stats_before['total_players']:,}")
    print(f"   Players with tournament history: {stats_before['players_with_tournament_history']:,}")
    print(f"   Unique tournaments: {stats_before['unique_tournaments_recorded']}")
    
    # Load all players
    all_players = db.load_all_players()
    print(f"\n🔄 Processing {len(all_players):,} players...")
    
    # Clear tournament history for each player
    cleared_count = 0
    for player in all_players:
        if player.tournament_history:  # Only update if they have history
            player.tournament_history = []  # Clear all tournament data
            db.save_player(player)
            cleared_count += 1
    
    print(f"✅ Cleared tournament history for {cleared_count:,} players")
    
    # Get stats after clearing
    stats_after = db.get_database_stats()
    print(f"\n📋 After clearing:")
    print(f"   Total players: {stats_after['total_players']:,}")
    print(f"   Players with tournament history: {stats_after['players_with_tournament_history']:,}")
    print(f"   Unique tournaments: {stats_after['unique_tournaments_recorded']}")
    
    # Check new file size
    new_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
    reduction = original_size - new_size
    reduction_pct = (reduction / original_size) * 100
    
    print(f"\n💾 FILE SIZE REDUCTION:")
    print(f"   Original: {original_size:.1f} MB")
    print(f"   New:      {new_size:.1f} MB")
    print(f"   Saved:    {reduction:.1f} MB ({reduction_pct:.1f}% reduction)")
    
    if new_size < 100:
        print(f"✅ Database is now under 100MB - ready for git commit!")
    else:
        print(f"⚠️ Database is still {new_size:.1f} MB - may need further optimization")
    
    # Show what's preserved
    print(f"\n🎯 PRESERVED DATA:")
    print(f"   ✅ All {stats_after['total_players']:,} players (names, CP, zones)")
    print(f"   ✅ Database structure and schema")
    print(f"   ✅ Low CP players: {stats_after['low_cp_players']:,}")
    print(f"   ✅ High CP players: {stats_after['high_cp_players']:,}")
    print(f"   ❌ Tournament histories (cleared)")
    print(f"   ❌ Match records (cleared)")
    
    print(f"\n🚀 Ready to commit to git and recreate tournaments on any machine!")
    
    return {
        'original_size_mb': original_size,
        'new_size_mb': new_size,
        'reduction_mb': reduction,
        'reduction_percent': reduction_pct,
        'players_cleared': cleared_count,
        'total_players': stats_after['total_players']
    }

if __name__ == "__main__":
    results = clear_tournament_data() 