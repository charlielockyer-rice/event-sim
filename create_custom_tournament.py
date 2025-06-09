#!/usr/bin/env python3
"""
Create Custom Tournament Dataset

Build a 3700-player tournament with:
- All 600 NA players
- Top 50 EU players  
- Top 50 LA players
- Top 10 OC players
- Top 3 MESA players
- Fill remaining 2987 spots with fake low-CP NA players
"""

import pandas as pd
import random
from player_database import PlayerDatabase, Player, RatingZone
import json
import sqlite3
import os

def load_regional_data():
    """Load all regional CSV files"""
    print("📊 Loading regional player data...")
    
    # Load all regional files
    na_df = pd.read_csv('data/na.csv')
    eu_df = pd.read_csv('data/eu.csv') 
    la_df = pd.read_csv('data/la.csv')
    oc_df = pd.read_csv('data/oc.csv')
    mesa_df = pd.read_csv('data/mesa.csv')
    
    print(f"   NA: {len(na_df)} players")
    print(f"   EU: {len(eu_df)} players") 
    print(f"   LA: {len(la_df)} players")
    print(f"   OC: {len(oc_df)} players")
    print(f"   MESA: {len(mesa_df)} players")
    
    return na_df, eu_df, la_df, oc_df, mesa_df

def create_tournament_composition():
    """Create the exact tournament composition requested"""
    
    na_df, eu_df, la_df, oc_df, mesa_df = load_regional_data()
    
    print(f"\\n🏗️  Building tournament composition...")
    
    # Take the requested players from each region
    tournament_players = []
    
    # All 600 NA players
    print(f"   Adding all {len(na_df)} NA players")
    for _, row in na_df.iterrows():
        tournament_players.append({
            'name': row['Player'],
            'rating_zone': 'NA',
            'cp': row['Championship Points'],
            'source': 'real_na'
        })
    
    # Top 50 EU players
    top_eu = eu_df.head(50)
    print(f"   Adding top {len(top_eu)} EU players")
    for _, row in top_eu.iterrows():
        tournament_players.append({
            'name': row['Player'],
            'rating_zone': 'EU', 
            'cp': row['Championship Points'],
            'source': 'real_eu'
        })
    
    # Top 50 LA players
    top_la = la_df.head(50)
    print(f"   Adding top {len(top_la)} LA players")
    for _, row in top_la.iterrows():
        tournament_players.append({
            'name': row['Player'],
            'rating_zone': 'LATAM',
            'cp': row['Championship Points'], 
            'source': 'real_la'
        })
    
    # Top 10 OC players
    top_oc = oc_df.head(10)
    print(f"   Adding top {len(top_oc)} OC players")
    for _, row in top_oc.iterrows():
        tournament_players.append({
            'name': row['Player'],
            'rating_zone': 'OCE',
            'cp': row['Championship Points'],
            'source': 'real_oc'
        })
    
    # Top 3 MESA players
    top_mesa = mesa_df.head(3)
    print(f"   Adding top {len(top_mesa)} MESA players")
    for _, row in top_mesa.iterrows():
        tournament_players.append({
            'name': row['Player'],
            'rating_zone': 'MESA',
            'cp': row['Championship Points'],
            'source': 'real_mesa'
        })
    
    current_count = len(tournament_players)
    remaining_spots = 3700 - current_count
    
    print(f"\\n📈 Real players: {current_count}")
    print(f"📈 Need to fill: {remaining_spots} more spots with fake NA players")
    
    # Find the minimum CP among real players to set fake player range
    real_cp_values = [p['cp'] for p in tournament_players]
    min_real_cp = min(real_cp_values)
    print(f"📈 Lowest real player CP: {min_real_cp}")
    
    # Generate fake NA players with CP lower than any real player
    fake_cp_min = 50  # Very low
    fake_cp_max = min_real_cp - 1  # Just below lowest real player
    
    print(f"📈 Fake players will have CP range: {fake_cp_min}-{fake_cp_max}")
    
    # Generate names for fake players
    fake_names = generate_fake_names(remaining_spots)
    
    for i in range(remaining_spots):
        fake_cp = random.randint(fake_cp_min, fake_cp_max)
        tournament_players.append({
            'name': fake_names[i],
            'rating_zone': 'NA',
            'cp': fake_cp,
            'source': 'fake_na'
        })
    
    print(f"\\n✅ Tournament composition complete: {len(tournament_players)} total players")
    return tournament_players

def generate_fake_names(count):
    """Generate realistic-looking fake player names"""
    
    # Common first names
    first_names = [
        "Alex", "Sam", "Jordan", "Taylor", "Casey", "Jamie", "Riley", "Avery",
        "Blake", "Cameron", "Drew", "Logan", "Morgan", "Quinn", "Sage", "Skyler",
        "Noah", "Liam", "Emma", "Olivia", "Ethan", "Mason", "Sophia", "Ava",
        "Jacob", "William", "Isabella", "Mia", "Michael", "Alexander", "Emily",
        "Madison", "Aiden", "Jackson", "Harper", "Abigail", "Daniel", "Matthew",
        "Ella", "Charlotte", "Lucas", "Henry", "Grace", "Chloe", "Owen", "Wyatt",
        "Sebastian", "Jack", "Luke", "Jayden", "Zoe", "Lily", "Addison", "Layla",
        "Carter", "Julian", "Grayson", "Leo", "Christopher", "Joshua", "Andrew",
        "Lincoln", "Mateo", "Ryan", "Jaxon", "Nathan", "Aaron", "Isaiah", "Thomas",
        "Charles", "Caleb", "Josiah", "Christian", "Hunter", "Eli", "Jonathan",
        "Connor", "Landon", "Adrian", "Asher", "Jeremiah", "Easton", "Nolan",
        "Colton", "Jordan", "Brody", "Parker", "Joel", "Adam", "Nathaniel", "Kai"
    ]
    
    # Common last names  
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", 
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
        "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
        "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
        "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
        "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz",
        "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris",
        "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan",
        "Cooper", "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos",
        "Kim", "Cox", "Ward", "Richardson", "Watson", "Brooks", "Chavez",
        "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
        "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long"
    ]
    
    fake_names = []
    used_names = set()
    
    while len(fake_names) < count:
        first = random.choice(first_names)
        last = random.choice(last_names)
        full_name = f"{first} {last}"
        
        # Add some variation to avoid duplicates
        if full_name in used_names:
            # Add middle initial or number
            if random.random() < 0.7:
                middle_initial = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                full_name = f"{first} {middle_initial}. {last}"
            else:
                number = random.randint(1, 999)
                full_name = f"{first} {last}{number}"
        
        if full_name not in used_names:
            fake_names.append(full_name)
            used_names.add(full_name)
    
    return fake_names

def create_database_directly(tournament_players, db_path="custom_tournament_players.db"):
    """Create database and populate it directly"""
    
    print(f"\\n💾 Creating database: {db_path}")
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create new database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create players table (same schema as PlayerDatabase)
    cursor.execute('''
        CREATE TABLE players (
            player_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            global_rank INTEGER,
            rating_zone TEXT NOT NULL,
            cp INTEGER NOT NULL
        )
    ''')
    
    # Insert all players
    print(f"💾 Inserting {len(tournament_players)} players...")
    
    for i, player_data in enumerate(tournament_players):
        cursor.execute('''
            INSERT INTO players (player_id, name, global_rank, rating_zone, cp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            i + 1,  # player_id (1-indexed)
            player_data['name'],
            i + 1,  # global_rank (use position as rank)
            player_data['rating_zone'],
            player_data['cp']
        ))
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"✅ Database created with {len(tournament_players)} players")
    
    # Show composition summary
    zone_counts = {}
    source_counts = {}
    for player_data in tournament_players:
        zone = player_data['rating_zone']
        source = player_data['source']
        zone_counts[zone] = zone_counts.get(zone, 0) + 1
        source_counts[source] = source_counts.get(source, 0) + 1
    
    print(f"\\n📊 FINAL COMPOSITION:")
    print(f"By Zone:")
    for zone, count in zone_counts.items():
        percentage = count / len(tournament_players) * 100
        print(f"   {zone}: {count:,} players ({percentage:.1f}%)")
    
    print(f"\\nBy Source:")
    for source, count in source_counts.items():
        percentage = count / len(tournament_players) * 100
        print(f"   {source}: {count:,} players ({percentage:.1f}%)")
    
    return db_path

def save_composition_report(tournament_players, filename="tournament_composition.json"):
    """Save detailed composition report"""
    
    # Create summary statistics
    real_players = [p for p in tournament_players if not p['source'].startswith('fake')]
    fake_players = [p for p in tournament_players if p['source'].startswith('fake')]
    
    report = {
        'total_players': len(tournament_players),
        'real_players': len(real_players),
        'fake_players': len(fake_players),
        'composition': {
            'real_na': len([p for p in tournament_players if p['source'] == 'real_na']),
            'real_eu': len([p for p in tournament_players if p['source'] == 'real_eu']),
            'real_la': len([p for p in tournament_players if p['source'] == 'real_la']), 
            'real_oc': len([p for p in tournament_players if p['source'] == 'real_oc']),
            'real_mesa': len([p for p in tournament_players if p['source'] == 'real_mesa']),
            'fake_na': len([p for p in tournament_players if p['source'] == 'fake_na'])
        },
        'cp_stats': {
            'real_players': {
                'min': min(p['cp'] for p in real_players),
                'max': max(p['cp'] for p in real_players),
                'avg': sum(p['cp'] for p in real_players) / len(real_players)
            },
            'fake_players': {
                'min': min(p['cp'] for p in fake_players),
                'max': max(p['cp'] for p in fake_players),
                'avg': sum(p['cp'] for p in fake_players) / len(fake_players)
            }
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Composition report saved to {filename}")

if __name__ == "__main__":
    print("🎮 Creating Custom Tournament Dataset")
    print("=" * 50)
    
    # Set random seed for reproducible fake names
    random.seed(12345)
    
    # Create tournament composition
    tournament_players = create_tournament_composition()
    
    # Save to database
    db_path = create_database_directly(tournament_players)
    
    # Save composition report
    save_composition_report(tournament_players)
    
    print(f"\\n🎉 Custom tournament dataset created!")
    print(f"Database: {db_path}")
    print(f"Use this database in your simulator for the custom field composition.") 