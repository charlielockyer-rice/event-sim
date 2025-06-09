# 🎮 Pokemon Tournament Simulator with Opponent Analysis
# Clean, streamlined version focused on functionality

import pandas as pd
import numpy as np
import random
from typing import List, Dict, Set, Tuple, Union, Optional
from datetime import datetime
from player_database import PlayerDatabase, Player, RatingZone

class TournamentSimulator:
    def __init__(self, db_path: str = 'custom_tournament_players.db'):
        self.db_path = db_path
        self.config = {
            'num_players': 3700,
            'day1_rounds': 9,
            'day2_rounds': 4,
            'points_to_advance': 19,
            'skill_factor': 1.0,
            'global_tie_rate': 0.15,  # Keep at 15% as requested
            'debug_mode': True
        }
        self.tournament_result = None
        
    def calculate_skill_level(self, cp: int) -> float:
        """Calculate skill level with harsh penalties for low CP"""
        if cp <= 331:
            # Very low CP - harsh penalties
            skill = 0.001 + 0.009 * (cp / 331) ** 10
            return skill
        elif cp <= 500:
            # Entry level real players
            progress = (cp - 332) / 168
            skill = 0.30 + 0.20 * progress
            return skill
        elif cp <= 800:
            # Good players - big advantage starts here
            progress = (cp - 501) / 299
            skill = 0.50 + 0.35 * progress
            return skill
        elif cp <= 1200:
            # Very good players
            progress = (cp - 801) / 399
            skill = 0.85 + 0.10 * progress
            return skill
        else:
            # Elite players
            excess = min(cp - 1201, 799)
            skill = 0.95 + 0.05 * (excess / 799)
            return skill

    def simulate_match(self, p1_row: pd.Series, p2_row: pd.Series, debug: bool = False) -> str:
        """Simulate match with BRUTAL penalties for low CP vs high CP"""
        
        p1_cp = p1_row['cp']
        p2_cp = p2_row['cp']
        
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
            # P1 (low) vs P2 (high) - crush P1's skill
            p1_skill *= 0.1  # 90% reduction
            is_brutal_matchup = True
        elif p2_is_low and p1_is_high:
            # P2 (low) vs P1 (high) - crush P2's skill
            p2_skill *= 0.1  # 90% reduction
            is_brutal_matchup = True
        
        # Calculate win probability
        skill_diff = p1_skill - p2_skill
        skill_advantage = skill_diff * self.config['skill_factor']
        p1_win_prob = 0.5 + skill_advantage
        
        # Apply bounds
        if abs(skill_diff) > 0.4:
            p1_win_prob = max(0.001, min(0.999, p1_win_prob))
        elif abs(skill_diff) > 0.2:
            p1_win_prob = max(0.005, min(0.995, p1_win_prob))
        else:
            p1_win_prob = max(0.05, min(0.95, p1_win_prob))
        
        # Debug output
        if debug and is_brutal_matchup:
            print(f"🔥 BRUTAL: {p1_cp} CP vs {p2_cp} CP - P1 win prob: {p1_win_prob:.3%}")
        
        # Simulate outcome
        rand_val = random.random()
        if rand_val < self.config['global_tie_rate']:
            return 'tie', is_brutal_matchup
        elif rand_val < self.config['global_tie_rate'] + p1_win_prob * (1 - self.config['global_tie_rate']):
            return 'player1_wins', is_brutal_matchup
        else:
            return 'player2_wins', is_brutal_matchup

    def load_players(self) -> pd.DataFrame:
        """Load players from database"""
        db = PlayerDatabase(self.db_path)
        all_players = db.load_all_players()
        players = all_players[:self.config['num_players']]
        
        # Convert to tournament format
        players_data = {
            'player_id': [p.player_id for p in players],
            'name': [p.name for p in players],
            'rating_zone': [p.rating_zone.value for p in players],
            'cp': [p.cp for p in players],
            'match_points': [0] * len(players),
            'wins': [0] * len(players),
            'losses': [0] * len(players),
            'ties': [0] * len(players),
            'opponents_played': [set() for _ in players],
            'received_bye': [False] * len(players),
            'is_active': [True] * len(players),
            'match_history': [[] for _ in players]  # Track detailed match history
        }
        
        df = pd.DataFrame(players_data)
        
        # Show field composition
        low_cp_count = len(df[df['cp'] <= 331])
        real_cp_count = len(df[df['cp'] >= 332])
        
        print(f"🔍 FIELD COMPOSITION:")
        print(f"   Total players: {len(df):,}")
        print(f"   Low CP (≤331): {low_cp_count:,} ({low_cp_count/len(df)*100:.1f}%)")
        print(f"   Real players (≥332): {real_cp_count:,} ({real_cp_count/len(df)*100:.1f}%)")
        
        return df

    def generate_pairings(self, players_df: pd.DataFrame) -> List[Tuple]:
        """Generate Swiss pairings"""
        active_players = players_df[players_df['is_active']].copy()
        active_players = active_players.sort_values(['match_points', 'cp'], ascending=[False, False])
        
        pairings = []
        paired_players = set()
        player_list = active_players['player_id'].tolist()
        
        i = 0
        while i < len(player_list):
            if player_list[i] in paired_players:
                i += 1
                continue
                
            player1_id = player_list[i]
            player1_opponents = active_players[active_players['player_id'] == player1_id]['opponents_played'].iloc[0]
            
            # Find valid opponent
            paired = False
            for j in range(i + 1, len(player_list)):
                player2_id = player_list[j]
                if player2_id in paired_players or player2_id in player1_opponents:
                    continue
                    
                pairings.append((player1_id, player2_id))
                paired_players.add(player1_id)
                paired_players.add(player2_id)
                paired = True
                break
            
            # If no valid opponent, pair with anyone
            if not paired:
                for j in range(i + 1, len(player_list)):
                    player2_id = player_list[j]
                    if player2_id not in paired_players:
                        pairings.append((player1_id, player2_id))
                        paired_players.add(player1_id)
                        paired_players.add(player2_id)
                        paired = True
                        break
            
            # Give bye if still unpaired
            if not paired:
                pairings.append((player1_id, 'BYE'))
                paired_players.add(player1_id)
            
            i += 1
        
        return pairings

    def update_player_stats(self, players_df: pd.DataFrame, player_id: int, 
                           match_points: int, wins: int = 0, losses: int = 0, ties: int = 0,
                           opponent_id: int = None, received_bye: bool = False):
        """Update player statistics"""
        idx = players_df[players_df['player_id'] == player_id].index[0]
        
        players_df.at[idx, 'match_points'] += match_points
        players_df.at[idx, 'wins'] += wins
        players_df.at[idx, 'losses'] += losses
        players_df.at[idx, 'ties'] += ties
        
        if opponent_id is not None:
            players_df.at[idx, 'opponents_played'].add(opponent_id)
        
        if received_bye:
            players_df.at[idx, 'received_bye'] = True

    def simulate_round(self, players_df: pd.DataFrame, round_number: int, verbose: bool = True):
        """Simulate a complete round with detailed tracking"""
        
        if verbose:
            print(f"\n--- Round {round_number} ---")
        
        pairings = self.generate_pairings(players_df)
        if verbose:
            print(f"Generated {len(pairings)} pairings")
        
        match_count = 0
        bye_count = 0
        brutal_matchups = 0
        
        for pairing in pairings:
            if pairing[1] == 'BYE':
                # Handle bye
                player_id = pairing[0]
                self.update_player_stats(players_df, player_id, match_points=3, wins=1, received_bye=True)
                
                # Record in match history
                idx = players_df[players_df['player_id'] == player_id].index[0]
                players_df.at[idx, 'match_history'].append({
                    'round': round_number,
                    'opponent_name': 'BYE',
                    'opponent_cp': 0,
                    'result': 'win',
                    'points_gained': 3,
                    'was_brutal_matchup': False
                })
                bye_count += 1
            else:
                # Simulate match
                player1_id, player2_id = pairing
                p1_row = players_df[players_df['player_id'] == player1_id].iloc[0]
                p2_row = players_df[players_df['player_id'] == player2_id].iloc[0]
                
                # Show debug for first few brutal matchups
                debug = self.config['debug_mode'] and round_number <= 2 and brutal_matchups < 3
                
                outcome, is_brutal = self.simulate_match(p1_row, p2_row, debug)
                
                if is_brutal:
                    brutal_matchups += 1
                
                # Update stats and match history
                if outcome == 'player1_wins':
                    self.update_player_stats(players_df, player1_id, match_points=3, wins=1, opponent_id=player2_id)
                    self.update_player_stats(players_df, player2_id, match_points=0, losses=1, opponent_id=player1_id)
                    
                    # Record match history
                    p1_idx = players_df[players_df['player_id'] == player1_id].index[0]
                    p2_idx = players_df[players_df['player_id'] == player2_id].index[0]
                    
                    players_df.at[p1_idx, 'match_history'].append({
                        'round': round_number,
                        'opponent_name': p2_row['name'],
                        'opponent_cp': p2_row['cp'],
                        'result': 'win',
                        'points_gained': 3,
                        'was_brutal_matchup': is_brutal
                    })
                    
                    players_df.at[p2_idx, 'match_history'].append({
                        'round': round_number,
                        'opponent_name': p1_row['name'],
                        'opponent_cp': p1_row['cp'],
                        'result': 'loss',
                        'points_gained': 0,
                        'was_brutal_matchup': is_brutal
                    })
                    
                elif outcome == 'player2_wins':
                    self.update_player_stats(players_df, player1_id, match_points=0, losses=1, opponent_id=player2_id)
                    self.update_player_stats(players_df, player2_id, match_points=3, wins=1, opponent_id=player1_id)
                    
                    # Record match history
                    p1_idx = players_df[players_df['player_id'] == player1_id].index[0]
                    p2_idx = players_df[players_df['player_id'] == player2_id].index[0]
                    
                    players_df.at[p1_idx, 'match_history'].append({
                        'round': round_number,
                        'opponent_name': p2_row['name'],
                        'opponent_cp': p2_row['cp'],
                        'result': 'loss',
                        'points_gained': 0,
                        'was_brutal_matchup': is_brutal
                    })
                    
                    players_df.at[p2_idx, 'match_history'].append({
                        'round': round_number,
                        'opponent_name': p1_row['name'],
                        'opponent_cp': p1_row['cp'],
                        'result': 'win',
                        'points_gained': 3,
                        'was_brutal_matchup': is_brutal
                    })
                    
                else:  # tie
                    self.update_player_stats(players_df, player1_id, match_points=1, ties=1, opponent_id=player2_id)
                    self.update_player_stats(players_df, player2_id, match_points=1, ties=1, opponent_id=player1_id)
                    
                    # Record match history
                    p1_idx = players_df[players_df['player_id'] == player1_id].index[0]
                    p2_idx = players_df[players_df['player_id'] == player2_id].index[0]
                    
                    players_df.at[p1_idx, 'match_history'].append({
                        'round': round_number,
                        'opponent_name': p2_row['name'],
                        'opponent_cp': p2_row['cp'],
                        'result': 'tie',
                        'points_gained': 1,
                        'was_brutal_matchup': is_brutal
                    })
                    
                    players_df.at[p2_idx, 'match_history'].append({
                        'round': round_number,
                        'opponent_name': p1_row['name'],
                        'opponent_cp': p1_row['cp'],
                        'result': 'tie',
                        'points_gained': 1,
                        'was_brutal_matchup': is_brutal
                    })
                
                match_count += 1
        
        if verbose:
            print(f"Completed {match_count} matches, {bye_count} byes, {brutal_matchups} brutal matchups")

    def run_tournament(self) -> Dict:
        """Run complete tournament simulation"""
        
        # Set random seed
        seed = int(datetime.now().timestamp() * 1000000) % 1000000
        random.seed(seed)
        np.random.seed(seed)
        
        tournament_id = f"tournament_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{seed}"
        
        print(f"🎮 TOURNAMENT SIMULATION: {tournament_id}")
        print("=" * 70)
        print(f"Skill Factor: {self.config['skill_factor']}")
        print(f"Tie Rate: {self.config['global_tie_rate']}")
        print(f"🔥 BRUTAL penalties for low CP vs high CP (500+) matchups")
        
        # Load players
        players_df = self.load_players()
        
        # Day 1
        print(f"\n🌅 DAY 1: {self.config['day1_rounds']} Swiss Rounds")
        print("=" * 40)
        
        for round_num in range(1, self.config['day1_rounds'] + 1):
            self.simulate_round(players_df, round_num)
        
        # Check advancement
        advancing_players = players_df[players_df['match_points'] >= self.config['points_to_advance']]
        low_cp_advancing = len(advancing_players[advancing_players['cp'] <= 331])
        real_cp_advancing = len(advancing_players[advancing_players['cp'] >= 332])
        
        print(f"\n📈 DAY 1 RESULTS:")
        print(f"Advancing to Day 2: {len(advancing_players)}")
        print(f"Low CP (≤331) advancing: {low_cp_advancing} ({low_cp_advancing/len(advancing_players)*100:.1f}%)")
        print(f"Real players (≥332) advancing: {real_cp_advancing} ({real_cp_advancing/len(advancing_players)*100:.1f}%)")
        
        # Mark non-advancing players as inactive
        players_df.loc[players_df['match_points'] < self.config['points_to_advance'], 'is_active'] = False
        
        # Day 2
        print(f"\n🌆 DAY 2: {self.config['day2_rounds']} Swiss Rounds")
        print("=" * 40)
        
        for round_num in range(self.config['day1_rounds'] + 1, 
                              self.config['day1_rounds'] + self.config['day2_rounds'] + 1):
            self.simulate_round(players_df, round_num)
        
        # Final standings
        final_standings = players_df[players_df['is_active']].sort_values(
            ['match_points', 'wins'], ascending=[False, False]
        ).reset_index(drop=True)
        
        # Results
        print(f"\n🏆 FINAL RESULTS:")
        if len(final_standings) > 0:
            champion = final_standings.iloc[0]
            print(f"Champion: {champion['name']} ({champion['cp']} CP, {champion['wins']}-{champion['losses']}-{champion['ties']})")
            
            # Top cut analysis
            for cut_size in [8, 16, 32]:
                if cut_size <= len(final_standings):
                    top_cut = final_standings.head(cut_size)
                    low_cp_in_cut = len(top_cut[top_cut['cp'] <= 331])
                    print(f"Top {cut_size}: {low_cp_in_cut} low CP ({low_cp_in_cut/cut_size*100:.1f}%)")
        
        # Store result
        self.tournament_result = {
            'tournament_id': tournament_id,
            'players_df': players_df,
            'final_standings': final_standings,
            'low_cp_advancing': low_cp_advancing,
            'real_cp_advancing': real_cp_advancing
        }
        
        return self.tournament_result

    def analyze_player(self, player_name_or_cp):
        """Analyze specific player's opponents"""
        
        if self.tournament_result is None:
            print("❌ No tournament results. Run tournament first!")
            return
        
        players_df = self.tournament_result['players_df']
        
        # Find player
        if isinstance(player_name_or_cp, str):
            player_matches = players_df[players_df['name'].str.contains(player_name_or_cp, case=False, na=False)]
        else:
            player_matches = players_df[players_df['cp'] == player_name_or_cp]
        
        if len(player_matches) == 0:
            print(f"❌ No player found matching '{player_name_or_cp}'")
            return
        
        if len(player_matches) > 1:
            print(f"🔍 Multiple players found:")
            for _, row in player_matches.iterrows():
                print(f"   • {row['name']} ({row['cp']} CP, {row['wins']}-{row['losses']}-{row['ties']})")
            return
        
        player = player_matches.iloc[0]
        print(f"\n🔍 ANALYZING: {player['name']} ({player['cp']} CP)")
        print(f"Final Record: {player['wins']}-{player['losses']}-{player['ties']} ({player['match_points']} pts)")
        print("=" * 80)
        
        # Analyze matches
        opponent_cps = []
        brutal_matchups = 0
        wins_vs_high_cp = 0
        total_vs_high_cp = 0
        
        print(f"{'Round':<6} {'Opponent':<25} {'Opp CP':<7} {'Result':<6} {'Pts':<4} {'Brutal?'}")
        print("-" * 80)
        
        for match in player['match_history']:
            opponent_cp = match['opponent_cp']
            result = match['result']
            points = match['points_gained']
            was_brutal = match.get('was_brutal_matchup', False)
            
            if opponent_cp > 0:
                opponent_cps.append(opponent_cp)
            
            if was_brutal:
                brutal_matchups += 1
            
            if opponent_cp >= 500:
                total_vs_high_cp += 1
                if result == 'win':
                    wins_vs_high_cp += 1
            
            brutal_indicator = "🔥 YES" if was_brutal else ""
            opponent_name = match['opponent_name'][:24]
            
            print(f"{match['round']:<6} {opponent_name:<25} {opponent_cp:<7} {result:<6} {points:<4} {brutal_indicator}")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"🔥 Brutal matchups faced: {brutal_matchups}")
        print(f"💪 High CP (500+) opponents: {total_vs_high_cp}")
        
        if total_vs_high_cp > 0:
            win_rate = wins_vs_high_cp / total_vs_high_cp * 100
            print(f"   Win rate vs High CP: {wins_vs_high_cp}/{total_vs_high_cp} ({win_rate:.1f}%)")
        else:
            print(f"   🎯 NEVER faced high CP players - explains the success!")
        
        # CP distribution
        if opponent_cps:
            low_opponents = len([cp for cp in opponent_cps if cp <= 331])
            high_opponents = len([cp for cp in opponent_cps if cp >= 500])
            print(f"   Faced {low_opponents} low CP and {high_opponents} high CP opponents")

    def find_successful_low_cp_players(self, min_wins: int = 10):
        """Find successful low CP players"""
        
        if self.tournament_result is None:
            print("❌ No tournament results. Run tournament first!")
            return
        
        players_df = self.tournament_result['players_df']
        successful = players_df[
            (players_df['cp'] <= 331) & 
            (players_df['wins'] >= min_wins)
        ].sort_values('wins', ascending=False)
        
        print(f"\n🚨 SUCCESSFUL LOW CP PLAYERS (≥{min_wins} wins):")
        print("=" * 60)
        
        if len(successful) == 0:
            print("✅ No low CP players with that many wins!")
            return
        
        for _, player in successful.iterrows():
            print(f"• {player['name']} ({player['cp']} CP, {player['wins']}-{player['losses']}-{player['ties']}, {player['match_points']} pts)")
        
        return successful


# Example usage
if __name__ == "__main__":
    # Create simulator
    sim = TournamentSimulator()
    
    print("🎮 Pokemon Tournament Simulator")
    print("==============================")
    print("Commands:")
    print("  sim.run_tournament()                    # Run tournament")
    print("  sim.analyze_player('Jordan Green750')   # Analyze specific player")
    print("  sim.find_successful_low_cp_players()    # Find problematic low CP players")
    print()
    print("Ready to use!") 