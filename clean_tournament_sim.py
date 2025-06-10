#!/usr/bin/env python3
"""
Clean Pokemon Tournament Simulator
Focuses on low CP vs high CP matchup analysis with NA Championship Points tracking
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime
from player_database import PlayerDatabase

class NAStandingsManager:
    """Manages NA player championship points and standings"""
    
    def __init__(self, na_data_path='data/na_full_data.csv'):
        self.na_data_path = na_data_path
        self.na_standings = None
        self.load_na_data()
        
        # Championship points table - REAL VALUES from official table
        # Based on powers of 2 placement brackets
        self.real_points = {
            1: 500,      # 1st place
            2: 480,      # 2nd place
            # 3rd-4th place: 420 points each
            3: 420, 4: 420,
            # 5th-8th place: 380 points each  
            5: 380, 6: 380, 7: 380, 8: 380,
            # 9th-16th place: 300 points each
            9: 300, 10: 300, 11: 300, 12: 300, 13: 300, 14: 300, 15: 300, 16: 300,
            # 17th-32nd place: 200 points each
            17: 200, 18: 200, 19: 200, 20: 200, 21: 200, 22: 200, 23: 200, 24: 200,
            25: 200, 26: 200, 27: 200, 28: 200, 29: 200, 30: 200, 31: 200, 32: 200,
            # 33rd-64th place: 150 points each
            33: 150, 34: 150, 35: 150, 36: 150, 37: 150, 38: 150, 39: 150, 40: 150,
            41: 150, 42: 150, 43: 150, 44: 150, 45: 150, 46: 150, 47: 150, 48: 150,
            49: 150, 50: 150, 51: 150, 52: 150, 53: 150, 54: 150, 55: 150, 56: 150,
            57: 150, 58: 150, 59: 150, 60: 150, 61: 150, 62: 150, 63: 150, 64: 150,
        }
        
        # Generate remaining placements programmatically
        # 65th-128th place: 120 points each
        for i in range(65, 129):
            self.real_points[i] = 120
        # 129th-256th place: 100 points each  
        for i in range(129, 257):
            self.real_points[i] = 100
        # 257th-512th place: 80 points each
        for i in range(257, 513):
            self.real_points[i] = 80
        # 513th-1024th place: 40 points each
        for i in range(513, 1025):
            self.real_points[i] = 40
        
        # Use the real points as our points table
        self.points_table = self.real_points.copy()
    
    def verify_points_table(self):
        """Verify the championship points table matches the official structure"""
        expected_structure = {
            1: 500, 2: 480, 3: 420, 4: 420, 5: 380, 8: 380,
            9: 300, 16: 300, 17: 200, 32: 200, 33: 150, 64: 150,
            65: 120, 128: 120, 129: 100, 256: 100, 257: 80, 512: 80,
            513: 40, 1024: 40
        }
        
        print("🔍 VERIFYING CHAMPIONSHIP POINTS STRUCTURE:")
        all_correct = True
        for placement, expected_points in expected_structure.items():
            actual_points = self.points_table.get(placement, 0)
            status = "✅" if actual_points == expected_points else "❌"
            print(f"   Place {placement:4d}: {actual_points} pts {status}")
            if actual_points != expected_points:
                all_correct = False
        
        if all_correct:
            print("✅ All championship points verified correctly!")
        else:
            print("❌ Championship points verification failed!")
        
        return all_correct
    
    def load_na_data(self):
        """Load NA player data from CSV"""
        self.na_standings = pd.read_csv(self.na_data_path)
        print(f"📊 Loaded {len(self.na_standings)} NA players from standings")
        
        # Create lookup dictionary for faster access
        self.na_lookup = {}
        for _, player in self.na_standings.iterrows():
            # Try multiple name variations for matching
            names_to_try = [
                player['NA Name'].lower().strip(),
                player['Top X Name'].lower().strip()
            ]
            for name in names_to_try:
                if name:
                    self.na_lookup[name] = player.name
    
    def parse_cp_finishes(self, cp_finishes_str):
        """Parse the CP finishes string into a list of integers"""
        if pd.isna(cp_finishes_str) or not cp_finishes_str:
            return []
        
        # Remove quotes and split by comma
        finishes_str = str(cp_finishes_str).strip('"').strip("'")
        if not finishes_str:
            return []
            
        try:
            # Split by comma and convert to integers
            finishes = [int(x.strip()) for x in finishes_str.split(',') if x.strip()]
            return finishes
        except ValueError:
            return []
    
    def update_player_finishes(self, player_name, new_points):
        """Update a player's major event finishes with new points"""
        # Find player in standings
        mask = (self.na_standings['NA Name'].str.lower() == player_name.lower()) | \
               (self.na_standings['Top X Name'].str.lower() == player_name.lower())
        
        if not mask.any():
            print(f"⚠️ Player '{player_name}' not found in NA standings")
            return False
        
        player_idx = mask.idxmax()
        player_row = self.na_standings.loc[player_idx]
        
        # Parse current finishes
        current_finishes = self.parse_cp_finishes(player_row['CP Finishes'])
        
        # Apply 5-finish rule
        if len(current_finishes) < 5:
            # Less than 5 finishes - add new points
            current_finishes.append(new_points)
        else:
            # 5 finishes - check if new points are better than lowest
            min_finish = min(current_finishes)
            if new_points > min_finish:
                # Replace lowest finish
                current_finishes.remove(min_finish)
                current_finishes.append(new_points)
            else:
                return False  # No change made
        
        # Sort finishes in descending order
        current_finishes.sort(reverse=True)
        
        # Update the dataframe
        finishes_str = ', '.join(map(str, current_finishes))
        self.na_standings.loc[player_idx, 'CP Finishes'] = finishes_str
        
        # Recalculate Top X CP
        new_top_x_cp = sum(current_finishes)
        self.na_standings.loc[player_idx, 'Top_X_CP'] = new_top_x_cp
        
        # Recalculate Total CP
        locals_cp = player_row['Locals CP']
        new_total_cp = new_top_x_cp + locals_cp
        self.na_standings.loc[player_idx, 'Total_CP'] = new_total_cp
        
        return True
    
    def process_tournament_results(self, tournament_results):
        """Process tournament results and update NA player standings"""
        if tournament_results is None:
            return
        
        na_updates = 0
        
        # Process each player's result
        # Handle both DataFrame and list inputs
        if hasattr(tournament_results, 'iterrows'):
            # DataFrame input (original format)
            for _, player in tournament_results.iterrows():
                player_name = player['name']
                placement = player.get('final_placement', len(tournament_results) + 1)
                if self._process_individual_player(player_name, placement):
                    na_updates += 1
        else:
            # List input (from multi-event simulation)
            for player in tournament_results:
                player_name = player['player_name']
                placement = player['final_placement']
                
                # Check if this is an NA player
                if self.is_na_player(player_name):
                    # Calculate championship points based on placement
                    points = self.get_championship_points(placement)
                    
                    if points:
                        success = self.update_player_finishes(player_name, points)
                        if success:
                            na_updates += 1
        
    def _process_individual_player(self, player_name, placement):
        """Process an individual player's tournament result"""
        # Check if this is an NA player
        if self.is_na_player(player_name):
            # Calculate championship points based on placement
            points = self.get_championship_points(placement)
            
            if points:
                success = self.update_player_finishes(player_name, points)
                return success
        return False
    
    def is_na_player(self, player_name):
        """Check if a player is in the NA standings"""
        name_lower = player_name.lower().strip()
        return name_lower in self.na_lookup
    
    def get_championship_points(self, placement):
        """Get championship points for a given placement"""
        if placement in self.points_table:
            return self.points_table[placement]
        return None  # No points for placements beyond 1024
    
    def save_updated_standings(self, output_path=None):
        """Save the updated standings to a CSV file"""
        if output_path is None:
            output_path = f"na_standings_updated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        self.na_standings.to_csv(output_path, index=False)
        print(f"💾 Saved updated NA standings to {output_path}")
        return output_path
    
    def get_top_players(self, n=20):
        """Get top N players by total CP"""
        sorted_standings = self.na_standings.sort_values('Total_CP', ascending=False)
        return sorted_standings.head(n)[['Top X Name', 'Total_CP', 'Top_X_CP', 'Locals CP', 'CP Finishes']]
    
    def update_points_table(self, new_points_dict):
        """Update the championship points table with real values
        
        Args:
            new_points_dict: Dictionary mapping placement positions to point values
            e.g., {1: 500, 2: 400, 3: 300, 4: 300, ...}
        """
        self.points_table.update(new_points_dict)
        print(f"✅ Updated points table with {len(new_points_dict)} placement values")
    
    def generate_final_rankings(self, top_n=50):
        """Generate final rankings after tournament and CP updates"""
        print(f"\n🏆 FINAL NA CHAMPIONSHIP STANDINGS (Top {top_n})")
        print("=" * 80)
        
        # Sort by Total_CP descending
        sorted_standings = self.na_standings.sort_values('Total_CP', ascending=False).reset_index(drop=True)
        
        print(f"{'Rank':<4} {'Player Name':<25} {'Total CP':<8} {'Top X CP':<8} {'Locals':<7} {'Current Top 5 Finishes'}")
        print("-" * 80)
        
        for i in range(min(top_n, len(sorted_standings))):
            player = sorted_standings.iloc[i]
            rank = i + 1
            name = player['Top X Name'][:24]  # Truncate long names
            total_cp = int(player['Total_CP'])
            top_x_cp = int(player['Top_X_CP'])
            locals_cp = int(player['Locals CP'])
            finishes = player['CP Finishes'][:30] + "..." if len(str(player['CP Finishes'])) > 30 else player['CP Finishes']
            
            print(f"{rank:<4} {name:<25} {total_cp:<8} {top_x_cp:<8} {locals_cp:<7} {finishes}")
        
        return sorted_standings.head(top_n)
    
    def show_points_structure(self, max_placement=64):
        """Show the current championship points structure"""
        print(f"🏆 OFFICIAL CHAMPIONSHIP POINTS STRUCTURE:")
        print("=" * 50)
        
        # Show the exact brackets from the official table
        brackets = [
            (1, 1, 500),
            (2, 2, 480), 
            (3, 4, 420),
            (5, 8, 380),
            (9, 16, 300),
            (17, 32, 200),
            (33, 64, 150),
            (65, 128, 120),
            (129, 256, 100),
            (257, 512, 80),
            (513, 1024, 40)
        ]
        
        for start, end, points in brackets:
            if start > max_placement:
                break
            if start == end:
                print(f"   Place {start:3d}      : {points} points")
            else:
                display_end = min(end, max_placement)
                print(f"   Places {start:3d}-{display_end:3d} : {points} points")
        
        if max_placement < 1024:
            print(f"   ... (structure continues to 1024th place = 40 points)")
    
    def get_na_player_by_name(self, name):
        """Get NA player data by name"""
        mask = (self.na_standings['NA Name'].str.lower() == name.lower()) | \
               (self.na_standings['Top X Name'].str.lower() == name.lower())
        
        if mask.any():
            return self.na_standings[mask].iloc[0]
        return None

class TournamentSimulator:
    def __init__(self, db_path='custom_tournament_players.db', track_na_standings=True):
        self.db_path = db_path
        self.tournament_result = None
        self.track_na_standings = track_na_standings
        
        # Initialize NA standings manager if requested
        if self.track_na_standings:
            try:
                self.na_manager = NAStandingsManager()
            except Exception as e:
                print(f"⚠️ Could not load NA standings: {e}")
                self.track_na_standings = False
                self.na_manager = None
        else:
            self.na_manager = None
        
    def calculate_skill_level(self, cp):
        """Calculate skill level with harsh penalties for low CP"""
        if cp <= 331:
            # Very low CP - harsh penalties (lowered skill range)
            skill = 0.2 + 0.10 * (cp / 331) ** 10
            return skill
        elif cp <= 500:
            # Entry level real players (lowered skill range)
            progress = (cp - 332) / 168
            skill = 0.30 + 0.20 * progress
            return skill
        elif cp <= 800:
            # Good players (lowered skill range)
            progress = (cp - 501) / 299
            skill = 0.50 + 0.30 * progress
            return skill
        else:
            # Elite players (lowered skill range)
            return 0.70 + 0.20 * min((cp - 801) / 1000, 1.0)

    def simulate_match(self, p1_cp, p2_cp, p1_name="P1", p2_name="P2", debug=False):
        """Simulate match with BRUTAL penalties for low CP vs high CP"""
        
        # Calculate base skills
        p1_skill = self.calculate_skill_level(p1_cp)
        p2_skill = self.calculate_skill_level(p2_cp)
        
        # BRUTAL MATCHUP PENALTIES: Low CP vs High CP (500+)
        p1_is_low = p1_cp <= 331
        p2_is_low = p2_cp <= 331
        p1_is_high = p1_cp >= 500
        p2_is_high = p2_cp >= 500
        
        is_brutal_matchup = False
        
        if p1_is_low and p2_is_high:
            # P1 (low) vs P2 (high) - significant skill reduction
            p1_skill *= 0.25  # 75% reduction (less nuclear)
            is_brutal_matchup = True
        elif p2_is_low and p1_is_high:
            # P2 (low) vs P1 (high) - significant skill reduction
            p2_skill *= 0.25  # 75% reduction (less nuclear)
            is_brutal_matchup = True
        
        # Calculate win probability
        skill_diff = p1_skill - p2_skill
        p1_win_prob = 0.5 + skill_diff
        
        # Apply bounds
        p1_win_prob = max(0.001, min(0.999, p1_win_prob))
        
        # Removed debug printing for speed
        
        # Simulate outcome (15% tie rate as requested)
        rand_val = random.random()
        if rand_val < 0.15:  # 15% tie rate
            return 'tie', is_brutal_matchup
        elif rand_val < 0.15 + p1_win_prob * 0.85:
            return 'player1_wins', is_brutal_matchup
        else:
            return 'player2_wins', is_brutal_matchup

    def load_players(self, num_players=None):
        """Load players from database with variable tournament size"""
        if num_players is None:
            # Random tournament size between 3700-4000 as requested
            num_players = random.randint(3700, 4000)
        
        db = PlayerDatabase(self.db_path)
        all_players = db.load_all_players()
        
        # Ensure we have enough players
        if len(all_players) < num_players:
            print(f"⚠️ Database only has {len(all_players)} players, requesting {num_players}")
            num_players = len(all_players)
        
        players = all_players[:num_players]
        
        # Create DataFrame
        df = pd.DataFrame({
            'player_id': [p.player_id for p in players],
            'name': [p.name for p in players],
            'cp': [p.cp for p in players],
            'match_points': [0] * len(players),
            'wins': [0] * len(players),
            'losses': [0] * len(players),
            'ties': [0] * len(players),
            'opponents_played': [set() for _ in players],
            'is_active': [True] * len(players),
            'match_history': [[] for _ in players]
        })
        
        # Show composition
        low_cp = len(df[df['cp'] <= 331])
        real_cp = len(df[df['cp'] >= 332])
        
        print(f"📊 FIELD COMPOSITION:")
        print(f"   Total: {len(df):,} players")
        print(f"   Low CP (≤331): {low_cp:,} ({low_cp/len(df)*100:.1f}%)")
        print(f"   Real players (≥332): {real_cp:,} ({real_cp/len(df)*100:.1f}%)")
        
        return df

    def generate_swiss_pairings(self, df):
        """Generate Swiss pairings - truly random within point brackets"""
        active = df[df['is_active']].copy()
        
        # Group by points, then randomize within each group
        pairings = []
        paired = set()
        
        # Get unique point totals and process from highest to lowest
        point_totals = sorted(active['match_points'].unique(), reverse=True)
        
        for points in point_totals:
            # Get all players with this point total
            bracket_players = active[active['match_points'] == points].copy()
            
            # Remove already paired players
            bracket_players = bracket_players[~bracket_players['player_id'].isin(paired)]
            
            if len(bracket_players) == 0:
                continue
            
            # Randomize the order within this point bracket
            bracket_players = bracket_players.sample(frac=1.0).reset_index(drop=True)
            bracket_list = bracket_players.to_dict('records')
            
            # Pair players within this bracket
            i = 0
            while i < len(bracket_list):
                player = bracket_list[i]
                player_id = player['player_id']
                
                if player_id in paired:
                    i += 1
                    continue
                
                # Find opponent in same bracket
                opponent_found = False
                
                # Try to find valid opponent (not played before)
                for j in range(i + 1, len(bracket_list)):
                    opp = bracket_list[j]
                    opp_id = opp['player_id']
                    
                    if opp_id not in paired and opp_id not in player['opponents_played']:
                        pairings.append((player_id, opp_id))
                        paired.add(player_id)
                        paired.add(opp_id)
                        opponent_found = True
                        break
                
                # If no valid opponent in bracket, pair with anyone in bracket
                if not opponent_found:
                    for j in range(i + 1, len(bracket_list)):
                        opp = bracket_list[j]
                        opp_id = opp['player_id']
                        
                        if opp_id not in paired:
                            pairings.append((player_id, opp_id))
                            paired.add(player_id)
                            paired.add(opp_id)
                            opponent_found = True
                            break
                
                # If still no opponent in bracket (odd number), leave unpaired for now
                if not opponent_found:
                    break
                
                i += 1
        
        # Handle remaining unpaired players (cross-bracket pairings or byes)
        unpaired = active[~active['player_id'].isin(paired)]['player_id'].tolist()
        
        for i in range(0, len(unpaired), 2):
            if i + 1 < len(unpaired):
                # Pair two unpaired players
                pairings.append((unpaired[i], unpaired[i + 1]))
                paired.add(unpaired[i])
                paired.add(unpaired[i + 1])
            else:
                # Give bye to last unpaired player
                pairings.append((unpaired[i], 'BYE'))
                paired.add(unpaired[i])
        
        return pairings

    def simulate_round(self, df, round_num, verbose=True):
        """Simulate one round"""
        if verbose:
            print(f"\n--- Round {round_num} ---")
        
        active_count = len(df[df['is_active']])
        if verbose:
            print(f"Active players: {active_count}")
        
        pairings = self.generate_swiss_pairings(df)
        if verbose:
            print(f"Generated {len(pairings)} pairings")
        
        brutal_count = 0
        match_count = 0
        
        for pairing in pairings:
            if pairing[1] == 'BYE':
                # Handle bye
                player_id = pairing[0]
                idx = df[df['player_id'] == player_id].index[0]
                
                df.at[idx, 'match_points'] += 3
                df.at[idx, 'wins'] += 1
                df.at[idx, 'match_history'].append({
                    'round': round_num,
                    'opponent': 'BYE',
                    'opponent_cp': 0,
                    'result': 'win',
                    'brutal': False
                })
            else:
                # Simulate match
                p1_id, p2_id = pairing
                p1_idx = df[df['player_id'] == p1_id].index[0]
                p2_idx = df[df['player_id'] == p2_id].index[0]
                
                p1_cp = df.at[p1_idx, 'cp']
                p2_cp = df.at[p2_idx, 'cp']
                p1_name = df.at[p1_idx, 'name']
                p2_name = df.at[p2_idx, 'name']
                
                # No debug output for speed
                outcome, is_brutal = self.simulate_match(p1_cp, p2_cp, p1_name, p2_name, debug=False)
                
                if is_brutal:
                    brutal_count += 1
                
                # Update opponents played
                df.at[p1_idx, 'opponents_played'].add(p2_id)
                df.at[p2_idx, 'opponents_played'].add(p1_id)
                
                # Update results
                if outcome == 'player1_wins':
                    df.at[p1_idx, 'match_points'] += 3
                    df.at[p1_idx, 'wins'] += 1
                    df.at[p2_idx, 'losses'] += 1
                    
                    df.at[p1_idx, 'match_history'].append({
                        'round': round_num, 'opponent': p2_name, 'opponent_cp': p2_cp,
                        'result': 'win', 'brutal': is_brutal
                    })
                    df.at[p2_idx, 'match_history'].append({
                        'round': round_num, 'opponent': p1_name, 'opponent_cp': p1_cp,
                        'result': 'loss', 'brutal': is_brutal
                    })
                    
                elif outcome == 'player2_wins':
                    df.at[p2_idx, 'match_points'] += 3
                    df.at[p2_idx, 'wins'] += 1
                    df.at[p1_idx, 'losses'] += 1
                    
                    df.at[p1_idx, 'match_history'].append({
                        'round': round_num, 'opponent': p2_name, 'opponent_cp': p2_cp,
                        'result': 'loss', 'brutal': is_brutal
                    })
                    df.at[p2_idx, 'match_history'].append({
                        'round': round_num, 'opponent': p1_name, 'opponent_cp': p1_cp,
                        'result': 'win', 'brutal': is_brutal
                    })
                    
                else:  # tie
                    df.at[p1_idx, 'match_points'] += 1
                    df.at[p2_idx, 'match_points'] += 1
                    df.at[p1_idx, 'ties'] += 1
                    df.at[p2_idx, 'ties'] += 1
                    
                    df.at[p1_idx, 'match_history'].append({
                        'round': round_num, 'opponent': p2_name, 'opponent_cp': p2_cp,
                        'result': 'tie', 'brutal': is_brutal
                    })
                    df.at[p2_idx, 'match_history'].append({
                        'round': round_num, 'opponent': p1_name, 'opponent_cp': p1_cp,
                        'result': 'tie', 'brutal': is_brutal
                    })
                
                match_count += 1
                
                # Progress indicator for large tournaments (less frequent)
                if verbose and match_count % 1000 == 0:
                    print(f"  Processed {match_count} matches...")
        
        if verbose:
            print(f"Completed {match_count} matches, {len(pairings) - match_count} byes, {brutal_count} brutal matchups")

    def run_tournament(self, num_players=None, verbose=True, save_results=False):
        """Run complete tournament"""
        # Set seed
        seed = int(datetime.now().timestamp()) % 1000000
        random.seed(seed)
        
        if verbose:
            print(f"🎮 TOURNAMENT SIMULATION (seed: {seed})")
        
        # Load players
        df = self.load_players(num_players)
        
        # Day 1: 9 rounds
        for round_num in range(1, 10):
            self.simulate_round(df, round_num, verbose=False)
        
        # Check advancement (19+ points)
        advancing = df[df['match_points'] >= 19]
        low_cp_advancing = len(advancing[advancing['cp'] <= 331])
        
        # Day 2: 4 more rounds
        df.loc[df['match_points'] < 19, 'is_active'] = False
        
        for round_num in range(10, 14):
            self.simulate_round(df, round_num, verbose=False)
        
        # Final standings
        final = df[df['is_active']].sort_values(['match_points', 'wins'], ascending=[False, False])
        
        if verbose:
            if len(final) > 0:
                champ = final.iloc[0]
                low_in_top8 = len(final.head(8)[final.head(8)['cp'] <= 331]) if len(final) >= 8 else 0
                print(f"🏆 Champion: {champ['name']} ({champ['cp']} CP) | Day 2: {len(final)} | Low CP in Top 8: {low_in_top8}")
        
        # Add final placement to all players
        final_with_placement = final.copy()
        final_with_placement['final_placement'] = range(1, len(final_with_placement) + 1)
        
        # Update the main dataframe with placements
        for idx, row in final_with_placement.iterrows():
            df.loc[idx, 'final_placement'] = row['final_placement']
        
        # Set placement for players who didn't make Day 2
        non_advancing = df[df['match_points'] < 19]
        # Sort non-advancing players by points, then by wins
        non_advancing_sorted = non_advancing.sort_values(['match_points', 'wins'], ascending=[False, False])
        start_placement = len(final_with_placement) + 1
        
        for i, (idx, row) in enumerate(non_advancing_sorted.iterrows()):
            df.loc[idx, 'final_placement'] = start_placement + i
        
        # Process NA standings if enabled
        if self.track_na_standings and self.na_manager:
            try:
                self.na_manager.process_tournament_results(df)
            except Exception as e:
                if verbose:
                    print(f"❌ Error processing NA standings: {e}")
        
        # Generate tournament ID
        tournament_id = f"tournament_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save tournament results to database (optional for speed)
        if save_results:
            try:
                from player_database import PlayerDatabase
                db = PlayerDatabase(self.db_path)
                db.save_tournament_results(tournament_id, df, final_with_placement)
            except Exception as e:
                if verbose:
                    print(f"⚠️ Could not save tournament results: {e}")
        
        # Store results
        self.tournament_result = {
            'players_df': df,
            'final_standings': final_with_placement,
            'seed': seed,
            'tournament_id': tournament_id
        }
        
        return self.tournament_result

    def quick_analysis(self, player_name):
        """Quick analysis of a player's performance across all tournaments"""
        try:
            from player_database import PlayerDatabase
            db = PlayerDatabase(self.db_path)
            analysis = db.get_player_analysis(player_name)
            
            if not analysis:
                print(f"❌ Player '{player_name}' not found in database")
                return None
            
            player = analysis['player']
            stats = analysis['stats']
            
            print(f"\n🔍 PLAYER ANALYSIS: {player.name}")
            print("=" * 60)
            print(f"💎 CP: {player.cp}")
            print(f"📊 Tournament History: {stats['tournaments']} tournaments")
            
            if stats['tournaments'] > 0:
                print(f"📈 Average Placement: {stats['avg_placement']:.1f}")
                print(f"🏆 Best Placement: {stats['best_placement']}")
                print(f"📉 Worst Placement: {stats['worst_placement']}")
                print(f"🎯 Day 2 Rate: {stats['day2_rate']*100:.1f}%")
                print(f"⚔️ Overall Record: {stats['total_wins']}-{stats['total_losses']}-{stats['total_ties']}")
                
                # Show recent tournaments
                print(f"\n📋 RECENT TOURNAMENTS:")
                recent = analysis['recent_tournaments'][-3:]  # Last 3
                for tournament in recent:
                    date = tournament['date'][:10]  # Just the date part
                    placement = tournament['final_placement']
                    record = f"{tournament['wins']}-{tournament['losses']}-{tournament['ties']}"
                    day2 = "✅" if tournament['made_day2'] else "❌"
                    print(f"   {date}: #{placement} ({record}) Day2: {day2}")
            else:
                print("   No tournament history found")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing player: {e}")
            return None

    def get_top_performers(self, min_tournaments=3):
        """Get top performing players from database"""
        try:
            from player_database import PlayerDatabase
            db = PlayerDatabase(self.db_path)
            performers = db.get_top_performers(min_tournaments=min_tournaments, metric='avg_placement')
            
            print(f"\n🏆 TOP PERFORMERS (min {min_tournaments} tournaments)")
            print("=" * 80)
            print(f"{'Rank':<4} {'Player':<25} {'CP':<5} {'Tournaments':<11} {'Avg Place':<9} {'Day 2%'}")
            print("-" * 80)
            
            for i, performer in enumerate(performers[:20], 1):  # Top 20
                name = performer['name'][:24]
                cp = performer['cp']
                stats = performer['stats']
                
                print(f"{i:<4} {name:<25} {cp:<5} {stats['tournaments']:<11} "
                      f"{stats['avg_placement']:<9.1f} {stats['day2_rate']*100:<5.1f}%")
            
            return performers
            
        except Exception as e:
            print(f"❌ Error getting top performers: {e}")
            return []

    def database_stats(self):
        """Show database statistics"""
        try:
            from player_database import PlayerDatabase
            db = PlayerDatabase(self.db_path)
            stats = db.get_database_stats()
            
            print(f"\n📊 DATABASE STATISTICS")
            print("=" * 40)
            print(f"Total players: {stats['total_players']:,}")
            print(f"Players with tournament history: {stats['players_with_tournament_history']:,}")
            print(f"Unique tournaments recorded: {stats['unique_tournaments_recorded']}")
            print(f"Low CP players (≤331): {stats['low_cp_players']:,}")
            print(f"High CP players (≥332): {stats['high_cp_players']:,}")
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting database stats: {e}")
            return {}

    def run_multiple_quick(self, num_tournaments=10, verbose=True, save_results=False):
        """Run multiple tournaments quickly for batch analysis"""
        print(f"🚀 RUNNING {num_tournaments} TOURNAMENTS")
        
        results = []
        for i in range(num_tournaments):
            if verbose:
                print(f"🎮 Tournament {i+1}/{num_tournaments}...", end=" ")
            
            # Run tournament with random player count
            result = self.run_tournament(verbose=False, save_results=save_results)
            
            if result:
                champion_name = result['final_standings'].iloc[0]['name'] if len(result['final_standings']) > 0 else 'Unknown'
                champion_cp = result['final_standings'].iloc[0]['cp'] if len(result['final_standings']) > 0 else 0
                
                if verbose:
                    cp_indicator = "🔥" if champion_cp <= 331 else "💎"
                    print(f"Champion: {champion_name} ({champion_cp} CP) {cp_indicator}")
                
                results.append({
                    'tournament_id': result['tournament_id'],
                    'total_players': len(result['players_df']),
                    'day2_players': len(result['final_standings']),
                    'champion': champion_name,
                    'champion_cp': champion_cp,
                    'seed': result['seed']
                })
        
        if results:
            avg_players = sum(r['total_players'] for r in results) / len(results)
            low_cp_champions = sum(1 for r in results if r['champion_cp'] <= 331)
            
            print(f"\n📈 SUMMARY: {len(results)} tournaments | Avg size: {avg_players:.0f} players | Low CP champions: {low_cp_champions}/{len(results)} ({low_cp_champions/len(results)*100:.1f}%)")
        
        return results

    def analyze_player(self, search_term):
        """Analyze a specific player's matches"""
        if self.tournament_result is None:
            print("❌ No tournament results. Run tournament first!")
            return
        
        df = self.tournament_result['players_df']
        
        # Find player
        if isinstance(search_term, str):
            matches = df[df['name'].str.contains(search_term, case=False, na=False)]
        else:
            matches = df[df['cp'] == search_term]
        
        if len(matches) == 0:
            print(f"❌ No player found for '{search_term}'")
            return
        
        if len(matches) > 1:
            print(f"🔍 Multiple matches found:")
            for i, (_, row) in enumerate(matches.iterrows(), 1):
                print(f"   {i}. {row['name']} ({row['cp']} CP, {row['wins']}-{row['losses']}-{row['ties']})")
            print(f"\n💡 To analyze a specific player, use the exact name:")
            for _, row in matches.iterrows():
                print(f"   sim.analyze_player('{row['name']}')")
            return
        
        player = matches.iloc[0]
        
        print(f"\n🔍 PLAYER ANALYSIS: {player['name']}")
        print(f"CP: {player['cp']}")
        print(f"Record: {player['wins']}-{player['losses']}-{player['ties']} ({player['match_points']} pts)")
        print("=" * 70)
        
        # Match analysis
        brutal_faced = 0
        high_cp_opponents = 0
        wins_vs_high = 0
        
        print(f"{'Rd':<3} {'Opponent':<20} {'Opp CP':<7} {'Result':<6} {'Brutal?'}")
        print("-" * 50)
        
        for match in player['match_history']:
            opp_cp = match['opponent_cp']
            result = match['result']
            brutal = match['brutal']
            
            if brutal:
                brutal_faced += 1
            
            if opp_cp >= 500:
                high_cp_opponents += 1
                if result == 'win':
                    wins_vs_high += 1
            
            brutal_mark = "🔥" if brutal else ""
            opp_name = match['opponent'][:19]
            
            print(f"{match['round']:<3} {opp_name:<20} {opp_cp:<7} {result:<6} {brutal_mark}")
        
        print(f"\n📊 SUMMARY:")
        print(f"🔥 Brutal matchups: {brutal_faced}")
        print(f"💪 High CP (500+) opponents: {high_cp_opponents}")
        
        if high_cp_opponents > 0:
            rate = wins_vs_high / high_cp_opponents * 100
            print(f"   Win rate vs high CP: {wins_vs_high}/{high_cp_opponents} ({rate:.1f}%)")
        else:
            print(f"   🎯 Never faced high CP - explains success!")

    def find_successful_low_cp(self, min_wins=10):
        """Find successful low CP players"""
        if self.tournament_result is None:
            print("❌ No tournament results. Run tournament first!")
            return
        
        df = self.tournament_result['players_df']
        successful = df[(df['cp'] <= 331) & (df['wins'] >= min_wins)]
        successful = successful.sort_values('wins', ascending=False)
        
        print(f"\n🚨 SUCCESSFUL LOW CP PLAYERS (≥{min_wins} wins):")
        print("=" * 50)
        
        if len(successful) == 0:
            print("✅ No low CP players found with that many wins!")
            return
        
        for _, player in successful.iterrows():
            print(f"• {player['name']} ({player['cp']} CP)")
            print(f"  Record: {player['wins']}-{player['losses']}-{player['ties']}")
        
        return successful

    def analyze_all_matches(self, search_term):
        """Analyze ALL players matching the search term"""
        if self.tournament_result is None:
            print("❌ No tournament results. Run tournament first!")
            return
        
        df = self.tournament_result['players_df']
        
        # Find all matching players
        if isinstance(search_term, str):
            matches = df[df['name'].str.contains(search_term, case=False, na=False)]
        else:
            matches = df[df['cp'] == search_term]
        
        if len(matches) == 0:
            print(f"❌ No players found for '{search_term}'")
            return
        
        print(f"🔍 ANALYZING ALL {len(matches)} PLAYERS MATCHING '{search_term}'")
        print("=" * 80)
        
        for i, (_, player) in enumerate(matches.iterrows(), 1):
            print(f"\n[{i}/{len(matches)}] {player['name']} ({player['cp']} CP)")
            print(f"Record: {player['wins']}-{player['losses']}-{player['ties']} ({player['match_points']} pts)")
            print("-" * 50)
            
            # Quick analysis
            brutal_faced = sum(1 for match in player['match_history'] if match.get('brutal', False))
            high_cp_opponents = sum(1 for match in player['match_history'] if match.get('opponent_cp', 0) >= 500)
            
            print(f"🔥 Brutal matchups: {brutal_faced}")
            print(f"💪 High CP (500+) opponents: {high_cp_opponents}")
            
            if high_cp_opponents == 0:
                print(f"   🎯 Never faced high CP - explains any success!")
            
            print()

    def tournament_summary(self):
        """Generate comprehensive tournament summary"""
        if self.tournament_result is None:
            print("❌ No tournament results. Run tournament first!")
            return
        
        result = self.tournament_result
        df = result['players_df']
        final = result['final_standings']
        
        print(f"\n" + "="*60)
        print(f"🏆 TOURNAMENT SUMMARY")
        print("="*60)
        
        # Field composition
        total = len(df)
        low_cp = len(df[df['cp'] <= 331])
        real_cp = len(df[df['cp'] >= 332])
        
        print(f"\n📊 FIELD COMPOSITION:")
        print(f"   Total players: {total:,}")
        print(f"   Low CP (≤331): {low_cp:,} ({low_cp/total*100:.1f}%)")
        print(f"   Real players (≥332): {real_cp:,} ({real_cp/total*100:.1f}%)")
        
        # Day 1 advancement
        day1_advancing = len(df[df['match_points'] >= 19])
        low_cp_advancing = len(df[(df['match_points'] >= 19) & (df['cp'] <= 331)])
        
        print(f"\n📈 DAY 1 ADVANCEMENT:")
        print(f"   Advanced to Day 2: {day1_advancing}")
        print(f"   Low CP advancing: {low_cp_advancing} ({low_cp_advancing/day1_advancing*100:.1f}%)")
        print(f"   Real CP advancing: {day1_advancing - low_cp_advancing} ({(day1_advancing - low_cp_advancing)/day1_advancing*100:.1f}%)")
        
        # Final results
        if len(final) > 0:
            champion = final.iloc[0]
            print(f"\n🏆 CHAMPION:")
            print(f"   {champion['name']} ({champion['cp']} CP)")
            print(f"   Record: {champion['wins']}-{champion['losses']}-{champion['ties']} ({champion['match_points']} pts)")
            
            # Top cuts analysis
            print(f"\n🥇 TOP CUTS BREAKDOWN:")
            for cut_size in [8, 16, 32, 64]:
                if cut_size <= len(final):
                    top_cut = final.head(cut_size)
                    low_in_cut = len(top_cut[top_cut['cp'] <= 331])
                    real_in_cut = cut_size - low_in_cut
                    
                    print(f"   Top {cut_size:2d}: {low_in_cut:2d} low CP ({low_in_cut/cut_size*100:4.1f}%), {real_in_cut:2d} real CP ({real_in_cut/cut_size*100:4.1f}%)")
        
        # CP distribution in final standings
        if len(final) > 0:
            print(f"\n📋 FINAL STANDINGS BY CP RANGE:")
            cp_ranges = [
                ("Very Low (≤100)", 0, 100),
                ("Low (101-331)", 101, 331), 
                ("Entry (332-500)", 332, 500),
                ("Good (501-800)", 501, 800),
                ("Elite (801+)", 801, 9999)
            ]
            
            for range_name, min_cp, max_cp in cp_ranges:
                count = len(final[(final['cp'] >= min_cp) & (final['cp'] <= max_cp)])
                if count > 0:
                    pct = count / len(final) * 100
                    print(f"   {range_name:18s}: {count:3d} players ({pct:4.1f}%)")
        
        # Successful low CP players
        successful_low = df[(df['cp'] <= 331) & (df['wins'] >= 8)].sort_values('wins', ascending=False)
        
        print(f"\n🚨 SUCCESSFUL LOW CP PLAYERS (≥8 wins):")
        if len(successful_low) == 0:
            print("   ✅ None! Skill system working properly.")
        else:
            for _, player in successful_low.iterrows():
                print(f"   • {player['name']} ({player['cp']} CP, {player['wins']}-{player['losses']}-{player['ties']})")
        
        print(f"\n" + "="*60)

    def track_140th_place_experiment(self, num_simulations=10, tournament_size=None, save_results=True):
        """Track 140th place championship points across multiple INDEPENDENT tournaments
        
        Each tournament starts from the same baseline to see range of possible outcomes.
        
        Args:
            num_simulations: Number of independent tournaments to simulate
            tournament_size: Number of players per tournament
            save_results: Whether to save detailed results to file
            
        Returns:
            Dictionary with statistics and raw data
        """
        print(f"🎯 140TH PLACE CHAMPIONSHIP POINTS EXPERIMENT - INDEPENDENT SCENARIOS")
        print("=" * 70)
        print(f"Running {num_simulations} INDEPENDENT tournaments with {tournament_size:,} players each")
        print(f"Each tournament starts from the same baseline (no cumulative effects)")
        print(f"Goal: Predict range of possible 140th place cutoffs")
        
        if not self.track_na_standings or not self.na_manager:
            print("❌ Cannot run experiment - NA standings not loaded")
            return None
        
        # Save the initial state
        initial_standings = self.na_manager.na_standings.copy()
        initial_rankings = initial_standings.sort_values('Total_CP', ascending=False).reset_index(drop=True)
        
        if len(initial_rankings) < 140:
            print("❌ Not enough players in standings for 140th place analysis")
            return None
            
        initial_140th = initial_rankings.iloc[139]['Total_CP']  # 139 = 140th place (0-indexed)
        initial_140th_name = initial_rankings.iloc[139]['Top X Name']
        print(f"📊 Baseline 140th place: {initial_140th_name} with {initial_140th:,} CP")
        
        # Store results
        place_140_totals = []
        tournament_results = []
        
        # Run independent simulations
        for sim_num in range(1, num_simulations + 1):
            print(f"\n🏆 INDEPENDENT SCENARIO {sim_num}/{num_simulations}")
            print("-" * 50)
            
            # RESET to initial state before each tournament
            self.na_manager.na_standings = initial_standings.copy()
            
            # Run tournament (quietly for speed)
            result = self.run_tournament(num_players=tournament_size, verbose=False, save_results=save_results)
            
            if result:
                # Get 140th place after THIS tournament only
                updated_rankings = self.na_manager.na_standings.sort_values('Total_CP', ascending=False).reset_index(drop=True)
                place_140_total = updated_rankings.iloc[139]['Total_CP']
                place_140_name = updated_rankings.iloc[139]['Top X Name']
                
                place_140_totals.append(place_140_total)
                
                tournament_results.append({
                    'simulation': sim_num,
                    'place_140_name': place_140_name,
                    'place_140_total': place_140_total,
                    'tournament_winner': result['final_standings'].iloc[0]['name'],
                    'tournament_size': tournament_size,
                    'change_from_baseline': place_140_total - initial_140th
                })
                
                change = place_140_total - initial_140th
                print(f"   140th place: {place_140_name} with {place_140_total:,} CP ({change:+,} from baseline)")
            else:
                print(f"   ❌ Tournament {sim_num} failed")
        
        # Restore initial state
        self.na_manager.na_standings = initial_standings.copy()
        
        if not place_140_totals:
            print("❌ No successful tournaments completed")
            return None
        
        # Calculate statistics
        import numpy as np
        stats = {
            'mean': np.mean(place_140_totals),
            'min': np.min(place_140_totals),
            'max': np.max(place_140_totals),
            'std': np.std(place_140_totals),
            'median': np.median(place_140_totals),
            'initial_value': initial_140th,
            'final_values': place_140_totals,
            'num_simulations': len(place_140_totals),
            'tournament_size': tournament_size,
            'changes_from_baseline': [x - initial_140th for x in place_140_totals]
        }
        
        # Display results
        self._display_140th_place_stats(stats, tournament_results)
        
        # Save results if requested
        if save_results:
            self._save_140th_place_results(stats, tournament_results)
        
        return {
            'statistics': stats,
            'tournament_details': tournament_results,
            'raw_data': place_140_totals
        }
    
    def _display_140th_place_stats(self, stats, tournament_results):
        """Display statistics for 140th place experiment"""
        print(f"\n📊 140TH PLACE CUTOFF PREDICTION - INDEPENDENT SCENARIOS")
        print("=" * 70)
        print(f"Scenarios analyzed: {stats['num_simulations']} independent tournaments")
        print(f"Tournament size: {stats['tournament_size']:,} players each")
        print(f"Baseline 140th place: {stats['initial_value']:,} CP")
        print()
        print(f"🎯 PREDICTED 140TH PLACE CUTOFF RANGE:")
        print(f"   Lowest possible:     {stats['min']:,} CP")
        print(f"   Highest possible:    {stats['max']:,} CP")
        print(f"   Most likely (mean):  {stats['mean']:,.1f} CP")
        print(f"   Median:              {stats['median']:,.1f} CP")
        print(f"   Standard deviation:  {stats['std']:,.1f} CP")
        print(f"   Total range:         {stats['max'] - stats['min']:,} CP")
        
        # Show changes from baseline
        import numpy as np
        changes = stats['changes_from_baseline']
        mean_change = np.mean(changes)
        min_change = np.min(changes)
        max_change = np.max(changes)
        
        print(f"\n📊 IMPACT OF ONE TOURNAMENT:")
        print(f"   Average impact:  {mean_change:+,.1f} CP")
        print(f"   Best case:       {max_change:+,.1f} CP")
        print(f"   Worst case:      {min_change:+,.1f} CP")
        print(f"   % impact range:  {(min_change/stats['initial_value']*100):+.2f}% to {(max_change/stats['initial_value']*100):+.2f}%")
        
        # Show all scenarios
        print(f"\n🔢 ALL INDEPENDENT SCENARIOS:")
        for i, result in enumerate(tournament_results, 1):
            value = result['place_140_total']
            change = result['change_from_baseline']
            name = result['place_140_name'][:20]
            print(f"   Scenario {i:2d}: {value:,} CP ({change:+,}) - {name}")
    
    def _save_140th_place_results(self, stats, tournament_results):
        """Save 140th place experiment results to files"""
        import pandas as pd
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed tournament results
        df_results = pd.DataFrame(tournament_results)
        results_file = f"140th_place_experiment_{timestamp}.csv"
        df_results.to_csv(results_file, index=False)
        
        # Save summary statistics
        stats_file = f"140th_place_stats_{timestamp}.txt"
        with open(stats_file, 'w') as f:
            f.write(f"140TH PLACE CHAMPIONSHIP POINTS EXPERIMENT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"Simulations: {stats['num_simulations']}\n")
            f.write(f"Tournament size: {stats['tournament_size']:,}\n")
            f.write(f"Initial 140th place: {stats['initial_value']:,} CP\n\n")
            f.write(f"STATISTICS:\n")
            f.write(f"Mean: {stats['mean']:,.1f} CP\n")
            f.write(f"Median: {stats['median']:,.1f} CP\n")
            f.write(f"Min: {stats['min']:,} CP\n")
            f.write(f"Max: {stats['max']:,} CP\n")
            f.write(f"Std Dev: {stats['std']:,.1f} CP\n")
            f.write(f"Range: {stats['max'] - stats['min']:,} CP\n\n")
            f.write(f"RAW VALUES:\n")
            for i, value in enumerate(stats['final_values'], 1):
                f.write(f"Simulation {i}: {value:,} CP\n")
        
        print(f"\n💾 Results saved:")
        print(f"   Detailed data: {results_file}")
        print(f"   Statistics:    {stats_file}")
        
        return results_file, stats_file

    def run_multi_event_simulation(self, num_events=5, players_per_event=None, save_individual_standings=True):
        """Run multiple tournaments and aggregate results"""
        from datetime import datetime
        import os
        
        print(f"🎮 MULTI-EVENT SIMULATION: {num_events} tournaments")
        print("=" * 60)
        
        all_results = []
        all_tournament_standings = []  # Store individual tournament standings
        
        # Create directory for individual tournament standings
        if save_individual_standings:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            standings_dir = f"tournament_standings_{timestamp}"
            os.makedirs(standings_dir, exist_ok=True)
            print(f"📁 Saving individual standings to: {standings_dir}/")
        
        for event_num in range(1, num_events + 1):
            print(f"\n🏆 EVENT {event_num}/{num_events}")
            print("-" * 40)
            
            # Use random tournament size if not specified
            tournament_size = players_per_event if players_per_event is not None else random.randint(3700, 4000)
            
            # Run tournament
            result = self.run_tournament(tournament_size, save_results=True)
            
            # Extract key metrics
            df = result['players_df']
            final = result['final_standings']
            
            # Save individual tournament standings
            if save_individual_standings:
                # Add event number and final placement to the standings
                standings_with_event = final.copy()
                standings_with_event['event_number'] = event_num
                standings_with_event['final_placement'] = range(1, len(final) + 1)
                
                # Save to CSV
                standings_file = f"{standings_dir}/event_{event_num:03d}_standings.csv"
                standings_with_event.to_csv(standings_file, index=False)
                
                # Store for aggregated analysis
                all_tournament_standings.append(standings_with_event)
            
            # Process NA standings if tracking is enabled
            if self.track_na_standings and self.na_manager:
                # Create tournament results for NA manager
                tournament_results = []
                for i, (_, player) in enumerate(final.iterrows(), 1):
                    tournament_results.append({
                        'player_name': player['name'],
                        'final_placement': i,
                        'cp': player['cp'],
                        'record': f"{player['wins']}-{player['losses']}-{player['ties']}"
                    })
                
                # Update NA standings
                self.na_manager.process_tournament_results(tournament_results)
            
            # Calculate metrics
            total_players = len(df)
            low_cp_count = len(df[df['cp'] <= 331])
            advanced = len(df[df['match_points'] >= 19])
            low_cp_advanced = len(df[(df['match_points'] >= 19) & (df['cp'] <= 331)])
            
            champion = final.iloc[0]
            
            # Top cut stats
            top8_low = len(final.head(8)[final.head(8)['cp'] <= 331])
            top16_low = len(final.head(16)[final.head(16)['cp'] <= 331])
            top32_low = len(final.head(32)[final.head(32)['cp'] <= 331])
            
            # Successful low CP count
            successful_low = len(df[(df['cp'] <= 331) & (df['wins'] >= 8)])
            
            event_data = {
                'event': event_num,
                'total_players': total_players,
                'low_cp_count': low_cp_count,
                'low_cp_pct': low_cp_count / total_players * 100,
                'advanced': advanced,
                'low_cp_advanced': low_cp_advanced,
                'low_cp_advanced_pct': low_cp_advanced / advanced * 100 if advanced > 0 else 0,
                'champion_name': champion['name'],
                'champion_cp': champion['cp'],
                'champion_record': f"{champion['wins']}-{champion['losses']}-{champion['ties']}",
                'top8_low': top8_low,
                'top16_low': top16_low,
                'top32_low': top32_low,
                'successful_low_cp': successful_low
            }
            
            all_results.append(event_data)
            
            # Quick event summary
            print(f"   Champion: {champion['name']} ({champion['cp']} CP)")
            print(f"   Low CP advanced: {low_cp_advanced}/{advanced} ({low_cp_advanced/advanced*100:.1f}%)")
            print(f"   Low CP in Top 8: {top8_low}/8")
        
        # Save aggregated player performance analysis
        if save_individual_standings and all_tournament_standings:
            self._save_player_performance_analysis(all_tournament_standings, standings_dir)
        
        # Aggregate analysis
        self._analyze_multi_event_results(all_results)
        
        # Final summary with file locations
        if save_individual_standings:
            print(f"\n📁 FILES SAVED:")
            print(f"   Individual standings: {standings_dir}/event_XXX_standings.csv")
            print(f"   Player performance:   {standings_dir}/player_performance_analysis.csv")
            print(f"   Tournament summary:   {standings_dir}/tournament_summary.csv")
        
        return {
            'aggregate_results': all_results,
            'individual_standings': all_tournament_standings if save_individual_standings else None,
            'standings_directory': standings_dir if save_individual_standings else None
        }
    
    def _analyze_multi_event_results(self, results):
        """Analyze results across multiple events"""
        import statistics
        
        print(f"\n" + "="*60)
        print(f"📊 MULTI-EVENT ANALYSIS ({len(results)} tournaments)")
        print("="*60)
        
        # Calculate averages and stats
        low_cp_advanced_pcts = [r['low_cp_advanced_pct'] for r in results]
        champion_cps = [r['champion_cp'] for r in results]
        top8_lows = [r['top8_low'] for r in results]
        top16_lows = [r['top16_low'] for r in results]
        top32_lows = [r['top32_low'] for r in results]
        successful_lows = [r['successful_low_cp'] for r in results]
        
        print(f"\n📈 LOW CP ADVANCEMENT TO DAY 2:")
        print(f"   Average: {statistics.mean(low_cp_advanced_pcts):.1f}%")
        print(f"   Range: {min(low_cp_advanced_pcts):.1f}% - {max(low_cp_advanced_pcts):.1f}%")
        print(f"   Std Dev: {statistics.stdev(low_cp_advanced_pcts):.1f}%")
        
        print(f"\n🏆 CHAMPIONS:")
        print(f"   Average CP: {statistics.mean(champion_cps):.0f}")
        print(f"   Range: {min(champion_cps)} - {max(champion_cps)} CP")
        print(f"   Low CP champions: {sum(1 for cp in champion_cps if cp <= 331)}/{len(results)}")
        
        print(f"\n🥇 TOP CUTS (Low CP players):")
        print(f"   Top 8 average: {statistics.mean(top8_lows):.1f} players")
        print(f"   Top 16 average: {statistics.mean(top16_lows):.1f} players")
        print(f"   Top 32 average: {statistics.mean(top32_lows):.1f} players")
        
        print(f"\n🚨 SUCCESSFUL LOW CP PLAYERS (8+ wins):")
        print(f"   Average per event: {statistics.mean(successful_lows):.1f}")
        print(f"   Range: {min(successful_lows)} - {max(successful_lows)}")
        print(f"   Total across all events: {sum(successful_lows)}")
        
        # Event-by-event breakdown
        print(f"\n📋 EVENT-BY-EVENT BREAKDOWN:")
        print(f"{'Event':<6} {'Champion CP':<12} {'Low Adv %':<10} {'Top8 Low':<9} {'Success Low'}")
        print("-" * 55)
        for r in results:
            print(f"{r['event']:<6} {r['champion_cp']:<12} {r['low_cp_advanced_pct']:<10.1f} {r['top8_low']:<9} {r['successful_low_cp']}")
        
        # Consistency analysis
        print(f"\n🎯 CONSISTENCY ANALYSIS:")
        if statistics.stdev(low_cp_advanced_pcts) < 2.0:
            print(f"   ✅ Very consistent low CP advancement rates (σ={statistics.stdev(low_cp_advanced_pcts):.1f}%)")
        elif statistics.stdev(low_cp_advanced_pcts) < 5.0:
            print(f"   ⚠️ Moderately consistent low CP advancement (σ={statistics.stdev(low_cp_advanced_pcts):.1f}%)")
        else:
            print(f"   ❌ High variance in low CP advancement (σ={statistics.stdev(low_cp_advanced_pcts):.1f}%)")
        
        zero_low_events = sum(1 for r in results if r['top8_low'] == 0)
        print(f"   Events with 0 low CP in Top 8: {zero_low_events}/{len(results)} ({zero_low_events/len(results)*100:.1f}%)")
    
    def _save_player_performance_analysis(self, all_tournament_standings, standings_dir):
        """Analyze and save individual player performance across all tournaments"""
        import pandas as pd
        import statistics
        from collections import defaultdict
        
        print(f"\n📊 Analyzing player performance across {len(all_tournament_standings)} tournaments...")
        
        # Combine all tournament data
        all_data = pd.concat(all_tournament_standings, ignore_index=True)
        
        # Group by player and calculate performance metrics
        player_performance = defaultdict(list)
        
        for player_name in all_data['name'].unique():
            player_data = all_data[all_data['name'] == player_name]
            
            # Basic info
            cp = player_data['cp'].iloc[0]  # CP should be consistent
            appearances = len(player_data)
            
            # Placement statistics
            placements = player_data['final_placement'].tolist()
            avg_placement = statistics.mean(placements)
            best_placement = min(placements)
            worst_placement = max(placements)
            median_placement = statistics.median(placements)
            placement_std = statistics.stdev(placements) if len(placements) > 1 else 0
            
            # Win rate and record analysis
            total_wins = player_data['wins'].sum()
            total_losses = player_data['losses'].sum()
            total_ties = player_data['ties'].sum()
            total_matches = total_wins + total_losses + total_ties
            win_rate = total_wins / total_matches if total_matches > 0 else 0
            
            # Tournament performance categories
            top8_finishes = len(player_data[player_data['final_placement'] <= 8])
            top16_finishes = len(player_data[player_data['final_placement'] <= 16])
            top32_finishes = len(player_data[player_data['final_placement'] <= 32])
            top64_finishes = len(player_data[player_data['final_placement'] <= 64])
            
            # Day 2 advancement (assuming 19+ match points)
            day2_appearances = len(player_data[player_data['match_points'] >= 19])
            day2_rate = day2_appearances / appearances if appearances > 0 else 0
            
            player_performance[player_name] = {
                'name': player_name,
                'cp': cp,
                'appearances': appearances,
                'avg_placement': avg_placement,
                'best_placement': best_placement,
                'worst_placement': worst_placement,
                'median_placement': median_placement,
                'placement_std': placement_std,
                'total_wins': total_wins,
                'total_losses': total_losses,
                'total_ties': total_ties,
                'win_rate': win_rate,
                'top8_finishes': top8_finishes,
                'top16_finishes': top16_finishes,
                'top32_finishes': top32_finishes,
                'top64_finishes': top64_finishes,
                'day2_appearances': day2_appearances,
                'day2_rate': day2_rate,
                'top8_rate': top8_finishes / appearances if appearances > 0 else 0,
                'top16_rate': top16_finishes / appearances if appearances > 0 else 0,
                'placement_consistency': 1 / (1 + placement_std) if placement_std > 0 else 1  # Higher = more consistent
            }
        
        # Convert to DataFrame and sort by average placement
        performance_df = pd.DataFrame.from_dict(player_performance, orient='index')
        performance_df = performance_df.sort_values('avg_placement')
        
        # Save detailed player performance
        performance_file = f"{standings_dir}/player_performance_analysis.csv"
        performance_df.to_csv(performance_file, index=False)
        
        # Save tournament summary
        summary_data = []
        for i, standings in enumerate(all_tournament_standings, 1):
            champion = standings.iloc[0]
            summary_data.append({
                'event_number': i,
                'champion_name': champion['name'],
                'champion_cp': champion['cp'],
                'champion_wins': champion['wins'],
                'champion_losses': champion['losses'],
                'champion_ties': champion['ties'],
                'total_players': len(standings)
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_file = f"{standings_dir}/tournament_summary.csv"
        summary_df.to_csv(summary_file, index=False)
        
        print(f"   ✅ Player performance analysis saved to {performance_file}")
        print(f"   ✅ Tournament summary saved to {summary_file}")
        
        # Display top performers
        print(f"\n🏆 TOP 10 PERFORMERS (by average placement):")
        top_performers = performance_df.head(10)
        print(f"{'Rank':<4} {'Player Name':<25} {'CP':<5} {'Avg Place':<9} {'Best':<5} {'Top8s':<6} {'Day2 Rate'}")
        print("-" * 75)
        for i, (_, player) in enumerate(top_performers.iterrows(), 1):
            name = player['name'][:24]
            cp = int(player['cp'])
            avg_place = player['avg_placement']
            best = int(player['best_placement'])
            top8s = int(player['top8_finishes'])
            day2_rate = player['day2_rate']
            print(f"{i:<4} {name:<25} {cp:<5} {avg_place:<9.1f} {best:<5} {top8s:<6} {day2_rate:.2f}")
        
        return performance_df


def main():
    """Interactive mode"""
    print("🎮 Pokemon Tournament Simulator")
    print("=" * 40)
    
    sim = TournamentSimulator()
    
    print("\nAvailable commands:")
    print("1. sim.run_tournament()                    # Run single tournament")
    print("2. sim.run_multi_event_simulation(5)      # Run multiple tournaments")
    print("3. sim.tournament_summary()                # Comprehensive results summary")
    print("4. sim.analyze_player('player_name')       # Analyze specific player")
    print("5. sim.analyze_all_matches('partial_name') # Analyze all players matching name")
    print("6. sim.find_successful_low_cp()           # Find problematic low CP players")
    print("\nExample workflow:")
    print(">>> sim.run_tournament()")
    print(">>> sim.tournament_summary()")
    print(">>> sim.analyze_player('Jordan Green')")
    
    return sim


if __name__ == "__main__":
    sim = main() 