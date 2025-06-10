#!/usr/bin/env python3
"""
Simplified Player Database for Tournament Simulation
Focuses on essential functionality with tournament tracking
"""

import sqlite3
import json
import random
from datetime import datetime
from typing import List, Dict, Optional, Any

class Player:
    """Simplified player data structure"""
    
    def __init__(self, player_id: int, name: str, cp: int, global_rank: int = None, rating_zone: str = "NA"):
        self.player_id = player_id
        self.name = name
        self.cp = cp
        self.global_rank = global_rank or player_id
        self.rating_zone = rating_zone
        
        # Tournament tracking
        self.tournament_history = []  # List of tournament results
        
    def add_tournament_result(self, tournament_id: str, final_placement: int, 
                            wins: int, losses: int, ties: int, match_points: int,
                            opponents_faced: List[str], match_details: List[Dict]):
        """Add tournament result to player's history"""
        result = {
            'tournament_id': tournament_id,
            'date': datetime.now().isoformat(),
            'final_placement': final_placement,
            'wins': wins,
            'losses': losses,
            'ties': ties,
            'match_points': match_points,
            'opponents_faced': opponents_faced,
            'match_details': match_details,  # Round-by-round results
            'made_day2': match_points >= 19
        }
        self.tournament_history.append(result)
    
    def get_stats_summary(self) -> Dict:
        """Get overall performance statistics"""
        if not self.tournament_history:
            return {'tournaments': 0, 'avg_placement': 0, 'best_placement': 0, 'day2_rate': 0}
        
        placements = [t['final_placement'] for t in self.tournament_history]
        day2_count = sum(1 for t in self.tournament_history if t['made_day2'])
        
        return {
            'tournaments': len(self.tournament_history),
            'avg_placement': sum(placements) / len(placements),
            'best_placement': min(placements),
            'worst_placement': max(placements),
            'day2_rate': day2_count / len(self.tournament_history),
            'total_wins': sum(t['wins'] for t in self.tournament_history),
            'total_losses': sum(t['losses'] for t in self.tournament_history),
            'total_ties': sum(t['ties'] for t in self.tournament_history)
        }
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage"""
        return {
            'player_id': self.player_id,
            'name': self.name,
            'cp': self.cp,
            'global_rank': self.global_rank,
            'rating_zone': self.rating_zone,
            'tournament_history': json.dumps(self.tournament_history)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Create player from database dictionary"""
        player = cls(
            player_id=data['player_id'],
            name=data['name'],
            cp=data['cp'],
            global_rank=data.get('global_rank', data['player_id']),
            rating_zone=data.get('rating_zone', 'NA')
        )
        
        # Load tournament history if it exists
        history_json = data.get('tournament_history', '[]')
        if isinstance(history_json, str):
            try:
                player.tournament_history = json.loads(history_json)
            except json.JSONDecodeError:
                player.tournament_history = []
        else:
            player.tournament_history = history_json or []
            
        return player

class PlayerDatabase:
    """Simplified database for tournament players"""
    
    def __init__(self, db_path: str = "custom_tournament_players.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with simple schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    player_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    cp INTEGER NOT NULL,
                    global_rank INTEGER,
                    rating_zone TEXT DEFAULT 'NA',
                    tournament_history TEXT DEFAULT '[]'
                )
            """)
            conn.commit()
    
    def load_all_players(self) -> List[Player]:
        """Load all players from database"""
        with sqlite3.connect(self.db_path) as conn:
            # Check if tournament_history column exists
            cursor = conn.execute("PRAGMA table_info(players)")
            columns = [column[1] for column in cursor.fetchall()]
            has_tournament_history = 'tournament_history' in columns
            
            if has_tournament_history:
                # Check if rating_zone exists too
                has_rating_zone = 'rating_zone' in columns
                
                if has_rating_zone:
                    cursor = conn.execute("""
                        SELECT player_id, name, cp, global_rank, rating_zone, tournament_history 
                        FROM players 
                        ORDER BY cp DESC, global_rank ASC
                    """)
                    
                    players = []
                    for row in cursor.fetchall():
                        player_data = {
                            'player_id': row[0],
                            'name': row[1],
                            'cp': row[2],
                            'global_rank': row[3] or row[0],
                            'rating_zone': row[4] or 'NA',
                            'tournament_history': row[5] or '[]'
                        }
                        players.append(Player.from_dict(player_data))
                else:
                    cursor = conn.execute("""
                        SELECT player_id, name, cp, global_rank, tournament_history 
                        FROM players 
                        ORDER BY cp DESC, global_rank ASC
                    """)
                    
                    players = []
                    for row in cursor.fetchall():
                        player_data = {
                            'player_id': row[0],
                            'name': row[1],
                            'cp': row[2],
                            'global_rank': row[3] or row[0],
                            'rating_zone': 'NA',
                            'tournament_history': row[4] or '[]'
                        }
                        players.append(Player.from_dict(player_data))
            else:
                # Handle old database schema - load with old schema and migrate
                print("📦 Loading from old database schema...")
                
                # Load with whatever columns exist
                if 'global_rank' in columns:
                    cursor = conn.execute("""
                        SELECT player_id, name, cp, global_rank 
                        FROM players 
                        ORDER BY cp DESC, global_rank ASC
                    """)
                else:
                    cursor = conn.execute("""
                        SELECT player_id, name, cp 
                        FROM players 
                        ORDER BY cp DESC, player_id ASC
                    """)
                
                players = []
                for row in cursor.fetchall():
                    if len(row) >= 4:  # Has global_rank
                        player_data = {
                            'player_id': row[0],
                            'name': row[1],
                            'cp': row[2],
                            'global_rank': row[3] or row[0],
                            'tournament_history': '[]'
                        }
                    else:  # No global_rank
                        player_data = {
                            'player_id': row[0],
                            'name': row[1],
                            'cp': row[2],
                            'global_rank': row[0],
                            'tournament_history': '[]'
                        }
                    players.append(Player.from_dict(player_data))
                
                # Now migrate the schema for future use
                self._migrate_old_schema()
            
            return players
    
    def _migrate_old_schema(self):
        """Migrate old database schema to new simplified schema"""
        with sqlite3.connect(self.db_path) as conn:
            # Check current schema
            cursor = conn.execute("PRAGMA table_info(players)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'tournament_history' not in columns:
                # Add tournament_history column
                conn.execute("ALTER TABLE players ADD COLUMN tournament_history TEXT DEFAULT '[]'")
                
                # If the old schema had global_rank, we're good
                # If not, add it (use player_id as default)
                if 'global_rank' not in columns:
                    conn.execute("ALTER TABLE players ADD COLUMN global_rank INTEGER")
                    conn.execute("UPDATE players SET global_rank = player_id WHERE global_rank IS NULL")
                
                conn.commit()
                print("✅ Database schema migrated successfully")
            
            # Check for rating_zone column and add if missing
            if 'rating_zone' not in columns:
                conn.execute("ALTER TABLE players ADD COLUMN rating_zone TEXT DEFAULT 'NA'")
                conn.commit()
                print("✅ Added rating_zone column to existing database")
    
    def load_players_subset(self, num_players: int) -> List[Player]:
        """Load top N players (by CP ranking)"""
        all_players = self.load_all_players()
        return all_players[:num_players]
    
    def save_player(self, player: Player):
        """Save a single player to the database"""
        data = player.to_dict()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO players
                (player_id, name, cp, global_rank, rating_zone, tournament_history)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data['player_id'], data['name'], data['cp'],
                data['global_rank'], data['rating_zone'], data['tournament_history']
            ))
            conn.commit()
    
    def save_tournament_results(self, tournament_id: str, players_df, final_standings):
        """Save tournament results for all players"""
        # Load all players once at the beginning (major performance improvement)
        all_players = self.load_all_players()
        player_lookup = {p.player_id: p for p in all_players}
        
        # Create lookup for final placements
        placement_lookup = {}
        for i, (_, player) in enumerate(final_standings.iterrows(), 1):
            placement_lookup[player['player_id']] = i
        
        saved_count = 0
        for _, player_row in players_df.iterrows():
            player_id = player_row['player_id']
            
            # Get existing player from lookup (much faster)
            player = player_lookup.get(player_id)
            if not player:
                continue
            
            # Extract match details from match_history (ensure JSON serializable)
            match_details = []
            for match in player_row.get('match_history', []):
                match_details.append({
                    'round': int(match.get('round', 0)),
                    'opponent': str(match.get('opponent', 'Unknown')),
                    'opponent_cp': int(match.get('opponent_cp', 0)),
                    'result': str(match.get('result', 'unknown')),
                    'brutal': bool(match.get('brutal', False))
                })
            
            # Get opponents faced
            opponents_faced = list(player_row.get('opponents_played', set()))
            if opponents_faced and isinstance(opponents_faced[0], int):  # Convert IDs to names
                opponent_names = []
                for opp_id in opponents_faced:
                    opp_rows = players_df[players_df['player_id'] == opp_id]
                    if not opp_rows.empty:
                        opponent_names.append(opp_rows.iloc[0]['name'])
                opponents_faced = opponent_names
            
            # Get final placement
            final_placement = placement_lookup.get(player_id, len(players_df) + 1)
            
            # Add tournament result (convert numpy types to native Python types)
            player.add_tournament_result(
                tournament_id=tournament_id,
                final_placement=int(final_placement),
                wins=int(player_row['wins']),
                losses=int(player_row['losses']),
                ties=int(player_row['ties']),
                match_points=int(player_row['match_points']),
                opponents_faced=opponents_faced,
                match_details=match_details
            )
            
            # Save updated player
            self.save_player(player)
            saved_count += 1
    
    def get_player_analysis(self, player_name: str) -> Optional[Dict]:
        """Get detailed analysis for a specific player"""
        players = self.load_all_players()
        
        # Find player (case insensitive)
        target_player = None
        for player in players:
            if player.name.lower() == player_name.lower():
                target_player = player
                break
        
        if not target_player:
            return None
        
        stats = target_player.get_stats_summary()
        
        return {
            'player': target_player,
            'stats': stats,
            'recent_tournaments': target_player.tournament_history[-5:],  # Last 5 tournaments
            'all_tournaments': target_player.tournament_history
        }
    
    def get_top_performers(self, min_tournaments: int = 5, metric: str = 'avg_placement') -> List[Dict]:
        """Get top performing players across tournaments"""
        players = self.load_all_players()
        performers = []
        
        for player in players:
            if len(player.tournament_history) >= min_tournaments:
                stats = player.get_stats_summary()
                performers.append({
                    'name': player.name,
                    'cp': player.cp,
                    'stats': stats
                })
        
        # Sort by the specified metric
        if metric == 'avg_placement':
            performers.sort(key=lambda x: x['stats']['avg_placement'])
        elif metric == 'day2_rate':
            performers.sort(key=lambda x: x['stats']['day2_rate'], reverse=True)
        elif metric == 'best_placement':
            performers.sort(key=lambda x: x['stats']['best_placement'])
        
        return performers
    
    def get_database_stats(self) -> Dict:
        """Get overview statistics of the database"""
        players = self.load_all_players()
        
        players_with_history = [p for p in players if p.tournament_history]
        
        if players_with_history:
            all_tournaments = []
            for player in players_with_history:
                all_tournaments.extend(player.tournament_history)
            
            unique_tournaments = len(set(t['tournament_id'] for t in all_tournaments))
        else:
            unique_tournaments = 0
        
        return {
            'total_players': len(players),
            'players_with_tournament_history': len(players_with_history),
            'unique_tournaments_recorded': unique_tournaments,
            'low_cp_players': len([p for p in players if p.cp <= 331]),
            'high_cp_players': len([p for p in players if p.cp >= 332])
        }

# Utility functions for generating fake players (if needed)
def generate_fake_name(rating_zone: str = "NA") -> str:
    """Generate a realistic-looking fake name based on rating zone"""
    if rating_zone == "JP":
        return generate_japanese_name()
    else:
        # Default NA/Western names
        first_names = [
            "Alex", "Blake", "Casey", "Drew", "Emery", "Finley", "Gray", "Harper", 
            "Indigo", "Jordan", "Kai", "Logan", "Morgan", "Neo", "Ocean", "Parker",
            "Quinn", "River", "Sage", "Taylor", "Uri", "Vale", "Winter", "Xander", "Yuki", "Zion"
        ]
        
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
            "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris"
        ]
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_japanese_name() -> str:
    """Generate realistic Japanese names"""
    # Common Japanese given names
    male_names = [
        "Hiroshi", "Takeshi", "Yuki", "Satoshi", "Kenji", "Makoto", "Ryota", "Daiki",
        "Shota", "Kenta", "Ryo", "Yuto", "Haruto", "Sota", "Ren", "Kaito", 
        "Yamato", "Hayato", "Tatsuki", "Akira", "Koichi", "Shinji", "Masato",
        "Naoki", "Tomoki", "Kazuki", "Takumi", "Tsubasa", "Kosuke", "Taiga"
    ]
    
    female_names = [
        "Yuki", "Akiko", "Emi", "Rei", "Miki", "Saki", "Yui", "Mika", "Rina", "Kana",
        "Ami", "Mao", "Hana", "Aoi", "Kokoro", "Nana", "Rika", "Sayaka", "Yuka", "Misaki",
        "Asuka", "Midori", "Haruka", "Sakura", "Shiori", "Ayaka", "Nanami", "Rena", "Karin", "Honoka"
    ]
    
    # Common Japanese surnames
    surnames = [
        "Tanaka", "Sato", "Suzuki", "Takahashi", "Watanabe", "Ito", "Yamamoto", "Nakamura",
        "Kobayashi", "Kato", "Yoshida", "Yamada", "Sasaki", "Yamazaki", "Mori", "Abe",
        "Ikeda", "Hashimoto", "Yamashita", "Ishikawa", "Nakajima", "Maeda", "Ogawa", "Goto",
        "Okada", "Hasegawa", "Murakami", "Kondo", "Ishida", "Saito", "Sakamoto", "Endo",
        "Aoki", "Fujii", "Nishimura", "Fukuda", "Ota", "Miura", "Takeuchi", "Nakano",
        "Matsuda", "Harada", "Inoue", "Kimura", "Hayashi", "Shimizu", "Yamaguchi", "Matsumoto"
    ]
    
    # Mix of male and female names for variety
    all_given_names = male_names + female_names
    given_name = random.choice(all_given_names)
    surname = random.choice(surnames)
    
    return f"{given_name} {surname}"

def generate_fake_players(num_players: int, start_id: int = 1) -> List[Player]:
    """Generate fake players with specific distribution for testing"""
    players = []
    
    # Create 250 NA players (low CP: 50-300)
    na_players = min(250, num_players)
    for i in range(na_players):
        player_id = start_id + i
        name = generate_fake_name("NA")
        cp = random.randint(50, 300)
        players.append(Player(player_id, name, cp, player_id, "NA"))
    
    # Create 250 JP players (650 CP each) if we still need more
    jp_players = min(250, num_players - na_players)
    for i in range(jp_players):
        player_id = start_id + na_players + i
        name = generate_fake_name("JP")
        cp = 650
        players.append(Player(player_id, name, cp, player_id, "JP"))
    
    # If we still need more players, create additional NA players with low CP
    remaining_needed = num_players - na_players - jp_players
    for i in range(remaining_needed):
        player_id = start_id + na_players + jp_players + i
        name = generate_fake_name("NA")
        cp = random.randint(50, 300)
        players.append(Player(player_id, name, cp, player_id, "NA"))
    
    return players

def create_sample_database(db_path: str = "custom_tournament_players.db", 
                          num_players: int = 5000, force_recreate: bool = False):
    """Create a sample database with fake players"""
    import os
    
    if force_recreate and os.path.exists(db_path):
        os.remove(db_path)
    
    db = PlayerDatabase(db_path)
    
    # Check if database already has players
    existing_players = db.load_all_players()
    if existing_players and not force_recreate:
        print(f"Database already has {len(existing_players)} players")
        return db
    
    print(f"Creating sample database with {num_players} players...")
    
    # Generate fake players
    fake_players = generate_fake_players(num_players)
    
    # Save to database
    for player in fake_players:
        db.save_player(player)
    
    print(f"✅ Created database with {num_players} players")
    return db

if __name__ == "__main__":
    # Create sample database for testing
    db = create_sample_database("test_players.db", 1000, force_recreate=True)
    
    # Show database stats
    stats = db.get_database_stats()
    print(f"\n📊 Database Stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}") 