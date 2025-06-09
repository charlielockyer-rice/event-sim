#!/usr/bin/env python3
"""
Modify Tournament Size

Utility to adjust tournament size by:
1. Using fewer players from existing database (subset)
2. Adding more fake players to existing database (expand)
"""

import sqlite3
import random
from create_custom_tournament import generate_fake_names

def check_current_database_size(db_path: str = "custom_tournament_players.db"):
    """Check how many players are currently in the database"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM players")
        total_players = cursor.fetchone()[0]
        
        # Check real vs fake breakdown
        cursor.execute("SELECT COUNT(*) FROM players WHERE cp >= 332")
        real_players = cursor.fetchone()[0]
        fake_players = total_players - real_players
        
        # Check zone distribution
        cursor.execute("SELECT rating_zone, COUNT(*) FROM players GROUP BY rating_zone")
        zone_counts = dict(cursor.fetchall())
        
        conn.close()
        
        print(f"📊 Current Database: {db_path}")
        print(f"   Total players: {total_players:,}")
        print(f"   Real players: {real_players:,} (CP ≥ 332)")
        print(f"   Fake players: {fake_players:,} (CP < 332)")
        print(f"   Zone breakdown:")
        for zone, count in zone_counts.items():
            print(f"     {zone}: {count:,}")
        
        return total_players, real_players, fake_players
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        return None, None, None

def expand_database(target_size: int, db_path: str = "custom_tournament_players.db"):
    """Add more fake players to reach target size"""
    
    current_total, real_players, fake_players = check_current_database_size(db_path)
    
    if current_total is None:
        print("❌ Cannot read current database")
        return False
    
    if target_size <= current_total:
        print(f"⚠️  Target size {target_size:,} is not larger than current size {current_total:,}")
        print(f"💡 Use subset_database() to use fewer players, or increase target_size")
        return False
    
    players_to_add = target_size - current_total
    print(f"➕ Adding {players_to_add:,} fake players to reach {target_size:,} total")
    
    # Generate new fake players
    print("🎭 Generating fake player names...")
    fake_names = generate_fake_names(players_to_add)
    
    # Find the current highest player_id
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(player_id) FROM players")
    max_id = cursor.fetchone()[0]
    
    # Add new players
    fake_cp_min = 50
    fake_cp_max = 331  # Just below real player threshold
    
    print(f"💾 Inserting {players_to_add:,} new players...")
    
    for i in range(players_to_add):
        new_id = max_id + i + 1
        fake_cp = random.randint(fake_cp_min, fake_cp_max)
        
        cursor.execute('''
            INSERT INTO players (player_id, name, global_rank, rating_zone, cp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            new_id,
            fake_names[i],
            new_id,  # Use position as rank
            'NA',    # All fake players are NA
            fake_cp
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database expanded to {target_size:,} players")
    
    # Verify
    check_current_database_size(db_path)
    return True

def explain_tournament_sizing():
    """Explain how tournament sizing works"""
    
    print("🎯 TOURNAMENT SIZING GUIDE")
    print("=" * 50)
    print()
    print("📊 Current Custom Database:")
    check_current_database_size()
    
    print(f"\n🔧 How to Change Tournament Size:")
    print()
    
    print("1️⃣  USE FEWER PLAYERS (no database change needed):")
    print("   - Change TOURNAMENT_CONFIG['num_players'] in notebook")
    print("   - Example: Set to 1000 for smaller tournament")
    print("   - Uses first N players from database (includes all real players)")
    
    print("\n2️⃣  USE MORE PLAYERS (expand database):")
    print("   - Current database has exactly 3,700 players")
    print("   - To use more, run: expand_database(5000)")
    print("   - Adds more fake NA players with low CP")
    
    print("\n3️⃣  REGENERATE COMPLETELY (for different composition):")
    print("   - Modify create_custom_tournament.py")
    print("   - Change player counts from each region")
    print("   - Run script to create new database")
    
    print(f"\n💡 RECOMMENDED APPROACH:")
    print("   - For smaller tournaments: just change num_players in notebook")
    print("   - For larger tournaments: use expand_database()")
    print("   - For different regions: regenerate database")

if __name__ == "__main__":
    explain_tournament_sizing()
    
    print(f"\n🚀 EXAMPLE USAGE:")
    print("=" * 30)
    print("# Check current size")
    print("python modify_tournament_size.py")
    print()
    print("# Expand to 5000 players")
    print("from modify_tournament_size import expand_database")
    print("expand_database(5000)")
    print()
    print("# Use fewer players (no database change)")
    print("# Just change TOURNAMENT_CONFIG['num_players'] = 1000 in notebook") 