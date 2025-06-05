#!/usr/bin/env python3
"""
Jupyter Notebook Integration for Player Database System

This module provides integration between the player database system and the 
existing Jupyter notebook tournament structure (Day 1 + Day 2 + Top Cut).
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Set, Tuple, Union, Optional
from player_database import PlayerDatabase, Player, RatingZone
import random
from datetime import datetime

class NotebookTournamentIntegration:
    """Integrates player database with Jupyter notebook tournament system"""
    
    def __init__(self, db_path: str):
        self.db = PlayerDatabase(db_path)
        self.tournament_id = f"notebook_tournament_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def load_players_for_tournament(self, num_players: Optional[int] = None) -> pd.DataFrame:
        """
        Load players from database and convert to notebook format
        
        Args:
            num_players: Number of players to load (None for all)
            
        Returns:
            DataFrame in the format expected by the Jupyter notebook
        """
        
        # Load players from database
        all_players = self.db.load_all_players()
        
        if num_players is not None:
            players = all_players[:num_players]
        else:
            players = all_players
        
        print(f"Loading {len(players):,} players for tournament...")
        
        # Convert to notebook format
        players_data = {
            'player_id': [],
            'name': [],
            'rating_zone': [],
            'cp': [],
            'match_points': [],
            'wins': [],
            'losses': [],
            'ties': [],
            'opponents_played': [],
            'received_bye': [],
            'is_active': []
        }
        
        for player in players:
            players_data['player_id'].append(player.player_id)
            players_data['name'].append(player.name)
            players_data['rating_zone'].append(player.rating_zone.value)
            players_data['cp'].append(player.cp)
            players_data['match_points'].append(0)
            players_data['wins'].append(0)
            players_data['losses'].append(0)
            players_data['ties'].append(0)
            players_data['opponents_played'].append(set())
            players_data['received_bye'].append(False)
            players_data['is_active'].append(True)
        
        df = pd.DataFrame(players_data)
        
        # Show field composition
        zone_counts = df['rating_zone'].value_counts()
        print(f"\nTournament Field Composition:")
        for zone in ['NA', 'EU', 'LATAM', 'OCE', 'MESA']:
            if zone in zone_counts.index:
                count = zone_counts[zone]
                percentage = count / len(df) * 100
                print(f"   {zone}: {count:,} players ({percentage:.1f}%)")
        
        # Show CP statistics
        cp_values = df['cp'].values
        print(f"\nCP Statistics:")
        print(f"   Range: {cp_values.min():,} - {cp_values.max():,}")
        print(f"   Average: {cp_values.mean():.0f}")
        print(f"   Median: {np.median(cp_values):.0f}")
        
        return df
    
    def skill_based_match_simulation(self, player1_row: pd.Series, player2_row: pd.Series, 
                                   global_tie_rate: float = 0.15, 
                                   skill_factor: float = 0.50) -> str:
        """
        Simulate match with skill consideration based on CP
        
        Args:
            player1_row: Pandas Series for player 1
            player2_row: Pandas Series for player 2
            global_tie_rate: Base tie rate
            skill_factor: How much CP affects win probability
            
        Returns:
            Match outcome: 'player1_wins', 'player2_wins', or 'tie'
        """
        
        p1_cp = player1_row['cp']
        p2_cp = player2_row['cp']
        
        # Calculate relative skill advantage
        cp_diff = p1_cp - p2_cp
        max_cp = max(p1_cp, p2_cp, 1000)
        
        # Convert CP difference to win probability adjustment
        skill_advantage = (cp_diff / max_cp) * skill_factor
        
        # Base probabilities (50/50 before skill adjustment)
        base_p1_win = 0.5
        
        # Adjust probability based on skill
        p1_win_prob = base_p1_win + skill_advantage
        p1_win_prob = max(0.15, min(0.85, p1_win_prob))  # Clamp between 15-85%
        
        # Simulate outcome
        rand_val = random.random()
        
        if rand_val < global_tie_rate:
            return 'tie'
        elif rand_val < global_tie_rate + p1_win_prob * (1 - global_tie_rate):
            return 'player1_wins'
        else:
            return 'player2_wins'
    
    def simulate_match_with_skill(self, player1_id: int, player2_id: int, 
                                players_df: pd.DataFrame,
                                global_tie_rate: float = 0.15,
                                skill_factor: float = 0.50) -> str:
        """
        Enhanced match simulation that considers player skill (CP)
        
        This replaces the notebook's simple random simulate_match function
        """
        
        p1_row = players_df[players_df['player_id'] == player1_id].iloc[0]
        p2_row = players_df[players_df['player_id'] == player2_id].iloc[0]
        
        return self.skill_based_match_simulation(p1_row, p2_row, global_tie_rate, skill_factor)
    
    def update_player_stats_enhanced(self, players_df: pd.DataFrame, player_id: int, 
                                   match_points: int, wins: int = 0, losses: int = 0, ties: int = 0,
                                   opponent_id: int = None, received_bye: bool = False):
        """Enhanced version of notebook's update_player_stats function"""
        idx = players_df[players_df['player_id'] == player_id].index[0]
        
        players_df.at[idx, 'match_points'] += match_points
        players_df.at[idx, 'wins'] += wins
        players_df.at[idx, 'losses'] += losses
        players_df.at[idx, 'ties'] += ties
        
        if opponent_id is not None:
            players_df.at[idx, 'opponents_played'].add(opponent_id)
        
        if received_bye:
            players_df.at[idx, 'received_bye'] = True
    
    def simulate_round_enhanced(self, players_df: pd.DataFrame, round_number: int, 
                              global_tie_rate: float = 0.15, skill_factor: float = 0.50):
        """
        Enhanced round simulation with skill-based outcomes
        
        This can replace the notebook's simulate_round function
        """
        print(f"\n--- Round {round_number} ---")
        
        # Use notebook's existing pairing logic
        pairings = self.pair_round_notebook_style(players_df)
        print(f"Generated {len(pairings)} pairings")
        
        match_count = 0
        bye_count = 0
        
        for pairing in pairings:
            if pairing[1] == 'BYE':
                # Handle bye
                player_id = pairing[0]
                self.update_player_stats_enhanced(
                    players_df, player_id, 
                    match_points=3, wins=1, received_bye=True
                )
                bye_count += 1
                print(f"  Player {player_id} receives a BYE")
            else:
                # Simulate match with skill consideration
                player1_id, player2_id = pairing
                outcome = self.simulate_match_with_skill(
                    player1_id, player2_id, players_df, 
                    global_tie_rate, skill_factor
                )
                
                if outcome == 'player1_wins':
                    self.update_player_stats_enhanced(
                        players_df, player1_id, 
                        match_points=3, wins=1, opponent_id=player2_id
                    )
                    self.update_player_stats_enhanced(
                        players_df, player2_id, 
                        match_points=0, losses=1, opponent_id=player1_id
                    )
                elif outcome == 'player2_wins':
                    self.update_player_stats_enhanced(
                        players_df, player1_id, 
                        match_points=0, losses=1, opponent_id=player2_id
                    )
                    self.update_player_stats_enhanced(
                        players_df, player2_id, 
                        match_points=3, wins=1, opponent_id=player1_id
                    )
                else:  # tie
                    self.update_player_stats_enhanced(
                        players_df, player1_id, 
                        match_points=1, ties=1, opponent_id=player2_id
                    )
                    self.update_player_stats_enhanced(
                        players_df, player2_id, 
                        match_points=1, ties=1, opponent_id=player1_id
                    )
                
                match_count += 1
        
        print(f"Completed {match_count} matches and {bye_count} byes")
        
        # Show current standings summary with zone breakdown
        active_players = players_df[players_df['is_active']]
        points_distribution = active_players['match_points'].value_counts().sort_index(ascending=False)
        print("Current points distribution:")
        for points, count in points_distribution.items():
            print(f"  {points} points: {count} players")
    
    def pair_round_notebook_style(self, players_df: pd.DataFrame) -> List[Tuple[Union[int, str], Union[int, str]]]:
        """
        Pairing logic compatible with the Jupyter notebook style
        
        This replicates the notebook's pair_round function
        """
        # Filter active players and sort by match points (descending), then by player_id
        active_players = players_df[players_df['is_active']].copy()
        active_players = active_players.sort_values(['match_points', 'player_id'], 
                                                   ascending=[False, True])
        
        pairings = []
        paired_players = set()
        
        player_list = active_players['player_id'].tolist()
        
        # Pair players
        i = 0
        while i < len(player_list):
            if player_list[i] in paired_players:
                i += 1
                continue
                
            player1_id = player_list[i]
            player1_opponents = active_players[active_players['player_id'] == player1_id]['opponents_played'].iloc[0]
            
            # Find a valid opponent
            paired = False
            for j in range(i + 1, len(player_list)):
                player2_id = player_list[j]
                if player2_id in paired_players:
                    continue
                    
                # Check if they've played before
                if player2_id not in player1_opponents:
                    pairings.append((player1_id, player2_id))
                    paired_players.add(player1_id)
                    paired_players.add(player2_id)
                    paired = True
                    break
            
            # If no valid opponent found, pair with next available (allowing rematch if necessary)
            if not paired:
                for j in range(i + 1, len(player_list)):
                    player2_id = player_list[j]
                    if player2_id not in paired_players:
                        pairings.append((player1_id, player2_id))
                        paired_players.add(player1_id)
                        paired_players.add(player2_id)
                        paired = True
                        break
            
            # If still not paired and no more players, give bye
            if not paired:
                pairings.append((player1_id, 'BYE'))
                paired_players.add(player1_id)
                paired = True
            
            i += 1
        
        return pairings
    
    def simulate_full_tournament(self, players_df: pd.DataFrame,
                               day1_rounds: int = 9,
                               day2_rounds: int = 4,
                               points_to_advance: int = 19,
                               global_tie_rate: float = 0.15,
                               skill_factor: float = 0.50,
                               top_cut_size: int = 8) -> Dict:
        """
        Simulate a complete tournament with notebook structure
        
        Args:
            players_df: Tournament players DataFrame
            day1_rounds: Number of Day 1 rounds
            day2_rounds: Number of Day 2 rounds
            points_to_advance: Points needed to advance to Day 2
            global_tie_rate: Base tie rate
            skill_factor: How much CP affects outcomes
            top_cut_size: Intended Top Cut size
            
        Returns:
            Dictionary with complete tournament results
        """
        
        print("🎮 FULL TOURNAMENT SIMULATION WITH SKILL-BASED OUTCOMES")
        print("=" * 70)
        print(f"Tournament ID: {self.tournament_id}")
        print(f"Players: {len(players_df):,}")
        print(f"Structure: Day 1 ({day1_rounds} rounds) + Day 2 ({day2_rounds} rounds) + Top Cut")
        print(f"Skill Factor: {skill_factor} (higher = more skill influence)")
        
        # Day 1 Simulation
        print(f"\n🌅 DAY 1: {day1_rounds} Swiss Rounds")
        print("=" * 40)
        
        for round_num in range(1, day1_rounds + 1):
            self.simulate_round_enhanced(players_df, round_num, global_tie_rate, skill_factor)
        
        # Day 1 Cut
        day1_standings = players_df.sort_values(['match_points', 'wins'], ascending=[False, False])
        advancing_players = day1_standings[day1_standings['match_points'] >= points_to_advance].copy()
        
        print(f"\n📊 DAY 1 RESULTS:")
        print(f"Players with {points_to_advance}+ points advance to Day 2: {len(advancing_players)}")
        
        # Mark non-advancing players as inactive
        players_df.loc[players_df['match_points'] < points_to_advance, 'is_active'] = False
        
        # Show Day 1 zone performance
        self.analyze_day_performance(advancing_players, "Day 1 Advancement")
        
        if len(advancing_players) == 0:
            print("❌ No players advanced to Day 2!")
            return {'error': 'No advancement to Day 2'}
        
        # Day 2 Simulation
        print(f"\n🌆 DAY 2: {day2_rounds} Swiss Rounds")
        print("=" * 40)
        print(f"Starting with {len(advancing_players)} players")
        
        for round_num in range(day1_rounds + 1, day1_rounds + day2_rounds + 1):
            self.simulate_round_enhanced(players_df, round_num, global_tie_rate, skill_factor)
        
        # Final standings
        final_standings = players_df[players_df['is_active']].sort_values(
            ['match_points', 'wins'], ascending=[False, False]
        ).reset_index(drop=True)
        
        print(f"\n🏆 FINAL STANDINGS:")
        champion = final_standings.iloc[0]
        print(f"Champion: {champion['name']} ({champion['rating_zone']}, {champion['cp']} CP)")
        print(f"Record: {champion['wins']}-{champion['losses']}-{champion['ties']} ({champion['match_points']} pts)")
        
        # Top Cut Analysis
        self.analyze_top_cuts(final_standings)
        
        # Update database with results
        self.update_database_with_results(players_df)
        
        return {
            'tournament_id': self.tournament_id,
            'final_standings': final_standings,
            'day1_advancement': len(advancing_players),
            'champion': champion.to_dict(),
            'total_players': len(players_df)
        }
    
    def analyze_day_performance(self, standings_df: pd.DataFrame, phase_name: str):
        """Analyze performance by rating zone"""
        
        print(f"\n📈 {phase_name.upper()} BY ZONE:")
        zone_stats = standings_df.groupby('rating_zone').agg({
            'match_points': ['count', 'mean'],
            'cp': 'mean',
            'wins': 'mean'
        }).round(1)
        
        total_players = len(standings_df)
        
        for zone in ['NA', 'EU', 'LATAM', 'OCE', 'MESA']:
            if zone in zone_stats.index:
                stats = zone_stats.loc[zone]
                count = int(stats['match_points']['count'])
                avg_pts = stats['match_points']['mean']
                avg_cp = stats['cp']['mean']
                avg_wins = stats['wins']['mean']
                percentage = count / total_players * 100
                print(f"  {zone}: {count:,} players ({percentage:.1f}%) | "
                      f"Avg: {avg_pts:.1f} pts, {avg_cp:.0f} CP, {avg_wins:.1f} wins")
    
    def analyze_top_cuts(self, final_standings: pd.DataFrame):
        """Analyze international representation in various top cuts"""
        
        print(f"\n🏅 TOP CUT ANALYSIS:")
        
        for cut_size in [8, 16, 32, 64]:
            if cut_size <= len(final_standings):
                top_cut = final_standings.head(cut_size)
                intl_count = len(top_cut[top_cut['rating_zone'] != 'NA'])
                na_count = cut_size - intl_count
                intl_pct = intl_count / cut_size * 100
                
                print(f"  Top {cut_size:2d}: {na_count:2d} NA ({100-intl_pct:4.1f}%) | "
                      f"{intl_count:2d} International ({intl_pct:4.1f}%)")
    
    def update_database_with_results(self, players_df: pd.DataFrame):
        """Update the player database with tournament results"""
        
        print(f"\n💾 UPDATING DATABASE...")
        print(f"Tournament ID: {self.tournament_id}")
        
        updated_count = 0
        
        for _, row in players_df.iterrows():
            player_id = row['player_id']
            player = self.db.load_player(player_id)
            
            if player:
                # Update tournament record
                player.update_tournament_stats(
                    self.tournament_id,
                    match_points=row['match_points'],
                    wins=row['wins'],
                    losses=row['losses'],
                    ties=row['ties'],
                    opponents_played=row['opponents_played'],
                    received_bye=row['received_bye'],
                    is_active=row['is_active']
                )
                
                # Save updated player
                self.db.save_player(player)
                updated_count += 1
        
        print(f"Updated {updated_count} player records")

# Helper functions for easy notebook integration
def create_tournament_from_database(db_path: str, num_players: Optional[int] = None) -> Tuple[pd.DataFrame, NotebookTournamentIntegration]:
    """
    Quick setup function for notebook use
    
    Returns:
        Tuple of (players_df, tournament_integration)
    """
    integration = NotebookTournamentIntegration(db_path)
    players_df = integration.load_players_for_tournament(num_players)
    return players_df, integration

def run_skill_based_tournament(db_path: str, 
                             num_players: Optional[int] = None,
                             skill_factor: float = 0.50,
                             day1_rounds: int = 9,
                             day2_rounds: int = 4) -> Dict:
    """
    Run a complete skill-based tournament
    
    This function can be called directly from a Jupyter notebook cell
    """
    players_df, integration = create_tournament_from_database(db_path, num_players)
    
    results = integration.simulate_full_tournament(
        players_df,
        day1_rounds=day1_rounds,
        day2_rounds=day2_rounds,
        skill_factor=skill_factor
    )
    
    return results

if __name__ == "__main__":
    # Test the integration
    print("Testing Jupyter notebook integration...")
    
    # Run a test tournament
    results = run_skill_based_tournament(
        db_path="large_tournament_players.db",
        num_players=1000,
        skill_factor=0.50
    )
    
    print(f"\n✅ Test complete! Tournament ID: {results['tournament_id']}") 