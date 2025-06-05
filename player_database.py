"""
Pokémon Tournament Player Database Management System

This module provides comprehensive player data management for tournament simulation,
including player generation, data storage, and tournament tracking capabilities.
"""

import pandas as pd
import json
import random
import numpy as np
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import sqlite3
from pathlib import Path
import uuid
from datetime import datetime

# Rating Zones as defined in the requirements
class RatingZone(Enum):
    NA = "NA"
    EU = "EU" 
    LATAM = "LATAM"
    OCE = "OCE"
    MESA = "MESA"

@dataclass
class TournamentRecord:
    """Track individual tournament performance"""
    tournament_id: str
    opponents_played: Set[int] = field(default_factory=set)
    match_points: int = 0
    wins: int = 0
    losses: int = 0
    ties: int = 0
    received_bye: bool = False
    is_active: bool = True
    placement: Optional[int] = None
    final_ranking: Optional[int] = None
    
    def to_dict(self):
        """Convert to dictionary, handling sets properly"""
        data = asdict(self)
        data['opponents_played'] = list(self.opponents_played)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary, converting lists back to sets"""
        if isinstance(data, cls):
            return data  # Already a TournamentRecord object
        data = data.copy()
        data['opponents_played'] = set(data.get('opponents_played', []))
        return cls(**data)

@dataclass
class Player:
    """Complete player data structure for tournament simulation"""
    
    # Core Identity
    player_id: int  # Unique identifier (can be same as global_rank for convenience)
    name: str
    global_rank: int  # Official global ranking
    rating_zone: RatingZone
    cp: int  # Championship Points (higher = better ranking)
    
    # Tournament History
    tournaments_played: Dict[str, TournamentRecord] = field(default_factory=dict)
    
    # Career Statistics
    career_tournaments: int = 0
    career_match_points: int = 0
    career_wins: int = 0
    career_losses: int = 0
    career_ties: int = 0
    career_top_cuts: int = 0
    career_wins_tournament: int = 0
    
    # Metadata
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Ensure rating_zone is RatingZone enum"""
        if isinstance(self.rating_zone, str):
            self.rating_zone = RatingZone(self.rating_zone)
    
    def get_current_tournament_record(self, tournament_id: str) -> TournamentRecord:
        """Get or create tournament record for current tournament"""
        if tournament_id not in self.tournaments_played:
            self.tournaments_played[tournament_id] = TournamentRecord(tournament_id=tournament_id)
        return self.tournaments_played[tournament_id]
    
    def update_tournament_stats(self, tournament_id: str, **kwargs):
        """Update statistics for specific tournament"""
        record = self.get_current_tournament_record(tournament_id)
        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)
        self.last_updated = datetime.now().isoformat()
    
    def finish_tournament(self, tournament_id: str, placement: int, final_ranking: int):
        """Mark tournament as finished and update career stats"""
        if tournament_id in self.tournaments_played:
            record = self.tournaments_played[tournament_id]
            record.placement = placement
            record.final_ranking = final_ranking
            
            # Update career stats
            self.career_tournaments += 1
            self.career_match_points += record.match_points
            self.career_wins += record.wins
            self.career_losses += record.losses
            self.career_ties += record.ties
            
            # Check for top cut (placement <= 8 is arbitrary, adjust as needed)
            if placement <= 8:
                self.career_top_cuts += 1
            
            # Check for tournament win
            if placement == 1:
                self.career_wins_tournament += 1
                
            self.last_updated = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary for storage"""
        data = asdict(self)
        data['rating_zone'] = self.rating_zone.value
        # Convert tournament records
        data['tournaments_played'] = {
            tid: record.to_dict() for tid, record in self.tournaments_played.items()
        }
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create player from dictionary"""
        if isinstance(data, cls):
            return data  # Already a Player object
        data = data.copy()
        # Convert tournaments back to TournamentRecord objects
        tournaments = {}
        for tid, record_data in data.get('tournaments_played', {}).items():
            if isinstance(record_data, TournamentRecord):
                tournaments[tid] = record_data
            else:
                tournaments[tid] = TournamentRecord.from_dict(record_data)
        data['tournaments_played'] = tournaments
        return cls(**data)

class PlayerDatabase:
    """Manages player database operations"""
    
    def __init__(self, db_path: str = "pokemon_players.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def _convert_db_row_to_dict(self, columns: List[str], row: tuple) -> Dict:
        """Convert database row to properly typed dictionary"""
        data = dict(zip(columns, row))
        
        # Handle potentially binary data
        for key, value in data.items():
            if isinstance(value, bytes):
                # Convert bytes to int if it's a numeric field
                if key in ['player_id', 'global_rank', 'cp', 'career_tournaments', 
                          'career_match_points', 'career_wins', 'career_losses', 
                          'career_ties', 'career_top_cuts', 'career_wins_tournament']:
                    # Convert 8-byte integer from bytes
                    data[key] = int.from_bytes(value, byteorder='little', signed=False)
                else:
                    data[key] = value.decode('utf-8')
            else:
                # Ensure proper types for numeric fields
                if key in ['player_id', 'global_rank', 'cp', 'career_tournaments', 
                          'career_match_points', 'career_wins', 'career_losses', 
                          'career_ties', 'career_top_cuts', 'career_wins_tournament']:
                    data[key] = int(value)
        
        return data
    
    def init_database(self):
        """Initialize SQLite database with proper schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    player_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    global_rank INTEGER UNIQUE NOT NULL,
                    rating_zone TEXT NOT NULL,
                    cp INTEGER NOT NULL,
                    career_tournaments INTEGER DEFAULT 0,
                    career_match_points INTEGER DEFAULT 0,
                    career_wins INTEGER DEFAULT 0,
                    career_losses INTEGER DEFAULT 0,
                    career_ties INTEGER DEFAULT 0,
                    career_top_cuts INTEGER DEFAULT 0,
                    career_wins_tournament INTEGER DEFAULT 0,
                    created_date TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    tournaments_data TEXT  -- JSON string of tournament records
                )
            """)
            
            # Create index for faster lookups
            conn.execute("CREATE INDEX IF NOT EXISTS idx_global_rank ON players(global_rank)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cp ON players(cp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rating_zone ON players(rating_zone)")
            
            conn.commit()
    
    def save_player(self, player: Player):
        """Save or update player in database"""
        with sqlite3.connect(self.db_path) as conn:
            # Convert tournaments to JSON, handling numpy types
            tournaments_data = {}
            for tid, record in player.tournaments_played.items():
                record_dict = record.to_dict()
                # Convert numpy types to native Python types
                for key, value in record_dict.items():
                    if hasattr(value, 'item'):  # numpy scalar
                        record_dict[key] = value.item()
                    elif isinstance(value, (list, set)):
                        record_dict[key] = [int(x) if hasattr(x, 'item') else x for x in value]
                tournaments_data[tid] = record_dict
            
            tournaments_json = json.dumps(tournaments_data)
            
            conn.execute("""
                INSERT OR REPLACE INTO players (
                    player_id, name, global_rank, rating_zone, cp,
                    career_tournaments, career_match_points, career_wins, 
                    career_losses, career_ties, career_top_cuts, career_wins_tournament,
                    created_date, last_updated, tournaments_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                player.player_id, player.name, player.global_rank, 
                player.rating_zone.value, player.cp,
                player.career_tournaments, player.career_match_points,
                player.career_wins, player.career_losses, player.career_ties,
                player.career_top_cuts, player.career_wins_tournament,
                player.created_date, player.last_updated, tournaments_json
            ))
            conn.commit()
    
    def load_player(self, player_id: int) -> Optional[Player]:
        """Load player by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM players WHERE player_id = ?", (player_id,))
            row = cursor.fetchone()
            
            if row:
                # Convert row to dictionary
                columns = [description[0] for description in cursor.description]
                data = self._convert_db_row_to_dict(columns, row)
                
                # Parse tournaments data
                tournaments_data = json.loads(data.pop('tournaments_data', '{}'))
                tournaments = {
                    tid: TournamentRecord.from_dict(record_data)
                    for tid, record_data in tournaments_data.items()
                }
                data['tournaments_played'] = tournaments
                
                return Player.from_dict(data)
        return None
    
    def load_all_players(self) -> List[Player]:
        """Load all players from database"""
        players = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM players ORDER BY global_rank")
            columns = [description[0] for description in cursor.description]
            
            for row in cursor.fetchall():
                data = self._convert_db_row_to_dict(columns, row)
                
                tournaments_data = json.loads(data.pop('tournaments_data', '{}'))
                tournaments = {
                    tid: TournamentRecord.from_dict(record_data)
                    for tid, record_data in tournaments_data.items()
                }
                data['tournaments_played'] = tournaments
                players.append(Player.from_dict(data))
        
        return players
    
    def get_players_by_zone(self, zone: RatingZone) -> List[Player]:
        """Get all players from specific rating zone"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM players WHERE rating_zone = ? ORDER BY cp DESC",
                (zone.value,)
            )
            columns = [description[0] for description in cursor.description]
            
            players = []
            for row in cursor.fetchall():
                data = self._convert_db_row_to_dict(columns, row)
                
                tournaments_data = json.loads(data.pop('tournaments_data', '{}'))
                tournaments = {
                    tid: TournamentRecord.from_dict(record_data)
                    for tid, record_data in tournaments_data.items()
                }
                data['tournaments_played'] = tournaments
                players.append(Player.from_dict(data))
        
        return players
    
    def get_top_players(self, limit: int = 100) -> List[Player]:
        """Get top players by CP"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM players ORDER BY cp DESC LIMIT ?",
                (limit,)
            )
            columns = [description[0] for description in cursor.description]
            
            players = []
            for row in cursor.fetchall():
                data = self._convert_db_row_to_dict(columns, row)
                
                tournaments_data = json.loads(data.pop('tournaments_data', '{}'))
                tournaments = {
                    tid: TournamentRecord.from_dict(record_data)
                    for tid, record_data in tournaments_data.items()
                }
                data['tournaments_played'] = tournaments
                players.append(Player.from_dict(data))
        
        return players

def generate_realistic_name() -> str:
    """Generate realistic player names"""
    first_names = [
        "Alex", "Sam", "Jordan", "Taylor", "Casey", "Morgan", "Avery", "Riley",
        "Cameron", "Dakota", "Parker", "Hayden", "Sage", "River", "Skyler",
        "Phoenix", "Rowan", "Emery", "Quinn", "Blake", "Kai", "Nova", "Remi",
        "Charlie", "Finley", "Reese", "Sawyer", "Lennox", "Ari", "Sage"
    ]
    
    last_names = [
        "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson",
        "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee",
        "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez",
        "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright"
    ]
    
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_sample_players(num_players: int, rating_zone_distribution: Optional[Dict[RatingZone, float]] = None) -> List[Player]:
    """
    Generate sample players with realistic distributions
    
    Args:
        num_players: Number of players to generate
        rating_zone_distribution: Optional custom distribution of rating zones
    
    Returns:
        List of generated Player objects
    """
    
    if rating_zone_distribution is None:
        # Updated distribution reflecting NA-focused tournament with elite international players
        rating_zone_distribution = {
            RatingZone.NA: 0.900,     # North America - domestic tournament
            RatingZone.EU: 0.050,     # Europe - elite travelers only
            RatingZone.LATAM: 0.030,  # Latin America - elite travelers only
            RatingZone.OCE: 0.015,    # Oceania - elite travelers only (adjusted to sum to 1.0)
            RatingZone.MESA: 0.005,   # Middle East/South Africa - elite travelers only
        }
    
    players = []
    zones = list(rating_zone_distribution.keys())
    zone_weights = list(rating_zone_distribution.values())
    
    # Step 1: Assign zones to all players
    player_zones = np.random.choice(zones, size=num_players, p=zone_weights)
    
    # Step 2: Generate CP values - International players are PEERS of top NA players, not better
    na_players = sum(1 for zone in player_zones if zone == RatingZone.NA)
    international_players = num_players - na_players
    
    # Generate ALL CP values together first (unified distribution)
    all_cp_base = np.random.lognormal(mean=6.5, sigma=0.8, size=num_players)
    all_cp_base = np.sort(all_cp_base)[::-1]  # Sort descending (best to worst)
    
    # Scale to full range (50-2500)
    min_cp, max_cp = 50, 2500
    all_cp_values = ((all_cp_base - all_cp_base.min()) / 
                     (all_cp_base.max() - all_cp_base.min()) * 
                     (max_cp - min_cp) + min_cp).astype(int)
    
    # Now assign CP based on elite international concept:
    # International players should be drawn from the TOP TIER of this distribution
    # NA players get the full range, but international players only get top ~25%
    
    # Split CP pool: top 25% for international selection, full range for NA
    top_25_percent_cutoff = int(len(all_cp_values) * 0.25)
    elite_cp_pool = all_cp_values[:top_25_percent_cutoff]  # Top 25% of all CP values
    full_cp_pool = all_cp_values.copy()  # Full range for NA
    
    # Assign CP values
    na_cp_values = []
    international_cp_values = []
    
    # Use shuffled indices for random assignment
    elite_indices = np.random.permutation(len(elite_cp_pool))
    full_indices = np.random.permutation(len(full_cp_pool))
    
    elite_index = 0
    full_index = 0
    
    # Step 3: Create players with appropriate CP based on their zone
    for i in range(num_players):
        # Global rank is 1-indexed position
        global_rank = i + 1
        
        # Get zone for this player
        rating_zone = player_zones[i]
        
        # Generate realistic name
        name = generate_realistic_name()
        
        # Assign CP based on zone and elite status
        if rating_zone == RatingZone.NA:
            # NA players can have any CP value from the full range
            cp = full_cp_pool[full_indices[full_index % len(full_indices)]]
            full_index += 1
        else:
            # International players only get elite CP values (top 25%)
            cp = elite_cp_pool[elite_indices[elite_index % len(elite_indices)]]
            elite_index += 1
        
        player = Player(
            player_id=global_rank,  # Use rank as ID for simplicity
            name=name,
            global_rank=global_rank,
            rating_zone=rating_zone,
            cp=cp
        )
        
        players.append(player)
    
    # Step 4: Re-sort players by CP to ensure global ranking makes sense
    # Higher CP should have lower (better) global rank
    players.sort(key=lambda p: p.cp, reverse=True)
    
    # Reassign global ranks based on CP ranking
    for i, player in enumerate(players):
        player.global_rank = i + 1
        player.player_id = i + 1  # Keep ID same as rank for simplicity
    
    return players

def create_player_database(num_players: int = 5000, 
                          db_path: str = "pokemon_players.db",
                          force_recreate: bool = False) -> PlayerDatabase:
    """
    Create and populate a player database
    
    Args:
        num_players: Number of players to generate
        db_path: Path to database file
        force_recreate: Whether to recreate database if it exists
    
    Returns:
        PlayerDatabase instance
    """
    
    db_path_obj = Path(db_path)
    
    # Remove existing database if force_recreate
    if force_recreate and db_path_obj.exists():
        db_path_obj.unlink()
        print(f"🗑️  Removed existing database: {db_path}")
    
    # Create database
    db = PlayerDatabase(db_path)
    
    # Check if database already has data
    existing_players = db.load_all_players()
    if existing_players and not force_recreate:
        print(f"📊 Database already contains {len(existing_players)} players")
        return db
    
    print(f"🎯 Generating {num_players} sample players...")
    
    # Generate players
    players = generate_sample_players(num_players)
    
    # Save to database
    print("💾 Saving players to database...")
    for i, player in enumerate(players):
        db.save_player(player)
        if (i + 1) % 1000 == 0:
            print(f"   Saved {i + 1}/{num_players} players...")
    
    print(f"✅ Database created with {num_players} players!")
    
    # Show some statistics
    zone_counts = {}
    cp_stats = []
    for player in players:
        zone_counts[player.rating_zone.value] = zone_counts.get(player.rating_zone.value, 0) + 1
        cp_stats.append(player.cp)
    
    print(f"\n📈 Player Distribution:")
    for zone, count in sorted(zone_counts.items()):
        percentage = count / num_players * 100
        print(f"   {zone}: {count:,} players ({percentage:.1f}%)")
    
    print(f"\n🏆 CP Statistics:")
    print(f"   Range: {min(cp_stats):,} - {max(cp_stats):,}")
    print(f"   Average: {np.mean(cp_stats):,.0f}")
    print(f"   Median: {np.median(cp_stats):,.0f}")
    
    return db

def export_players_to_formats(db: PlayerDatabase, export_dir: str = "exports"):
    """Export players to various formats for analysis"""
    
    export_path = Path(export_dir)
    export_path.mkdir(exist_ok=True)
    
    print(f"📤 Exporting player data to {export_dir}/...")
    
    players = db.load_all_players()
    
    # Convert to pandas DataFrame for easy export
    player_data = []
    for player in players:
        player_data.append({
            'player_id': player.player_id,
            'name': player.name,
            'global_rank': player.global_rank,
            'rating_zone': player.rating_zone.value,
            'cp': player.cp,
            'career_tournaments': player.career_tournaments,
            'career_match_points': player.career_match_points,
            'career_wins': player.career_wins,
            'career_losses': player.career_losses,
            'career_ties': player.career_ties,
            'career_top_cuts': player.career_top_cuts,
            'career_wins_tournament': player.career_wins_tournament,
            'created_date': player.created_date,
            'last_updated': player.last_updated
        })
    
    df = pd.DataFrame(player_data)
    
    # Export to CSV
    csv_path = export_path / "players.csv"
    df.to_csv(csv_path, index=False)
    print(f"   ✅ CSV: {csv_path}")
    
    # Export to JSON
    json_path = export_path / "players.json"
    df.to_json(json_path, orient='records', indent=2)
    print(f"   ✅ JSON: {json_path}")
    
    # Export summary statistics
    summary_path = export_path / "player_summary.json"
    summary = {
        'total_players': len(players),
        'rating_zone_distribution': df['rating_zone'].value_counts().to_dict(),
        'cp_statistics': {
            'min': int(df['cp'].min()),
            'max': int(df['cp'].max()),
            'mean': float(df['cp'].mean()),
            'median': float(df['cp'].median()),
            'std': float(df['cp'].std())
        },
        'top_10_players': df.head(10)[['name', 'global_rank', 'rating_zone', 'cp']].to_dict('records')
    }
    
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"   ✅ Summary: {summary_path}")
    
    print(f"�� Export complete!") 