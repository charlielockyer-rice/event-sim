#!/usr/bin/env python3
"""
Debug script to investigate why very low CP players are succeeding
"""
import random

def calculate_skill_level(cp):
    if cp <= 331:
        return 0.01 + 0.14 * (cp / 331) ** 4
    elif cp <= 500:
        progress = (cp - 332) / 168
        return 0.30 + 0.20 * progress
    elif cp <= 700:
        progress = (cp - 501) / 199
        return 0.50 + 0.20 * progress
    elif cp <= 1000:
        progress = (cp - 701) / 299
        return 0.70 + 0.15 * progress
    elif cp <= 1300:
        progress = (cp - 1001) / 299
        return 0.85 + 0.10 * progress
    else:
        excess = min(cp - 1301, 699)
        return 0.95 + 0.05 * (excess / 699)

def calculate_win_probability(p1_cp, p2_cp, skill_factor=0.85, tie_rate=0.15):
    p1_skill = calculate_skill_level(p1_cp)
    p2_skill = calculate_skill_level(p2_cp)
    skill_diff = p1_skill - p2_skill
    skill_advantage = skill_diff * skill_factor
    p1_win_prob = 0.5 + skill_advantage
    
    # Apply bounds
    if abs(skill_diff) > 0.4:
        p1_win_prob = max(0.02, min(0.98, p1_win_prob))
    else:
        p1_win_prob = max(0.05, min(0.95, p1_win_prob))
    
    # Account for ties
    effective_win_prob = p1_win_prob * (1 - tie_rate)
    
    return p1_win_prob, effective_win_prob

def simulate_tournament_probability(cp, opponents_cp_list, tie_rate=0.15):
    """Simulate probability of going 11-2 or better against typical opponents"""
    random.seed(42)
    
    total_wins = 0
    simulations = 10000
    
    for _ in range(simulations):
        wins = 0
        ties = 0
        
        for round_num in range(13):  # 13 rounds total
            # Pick a random opponent CP from typical field
            opp_cp = random.choice(opponents_cp_list)
            win_prob, _ = calculate_win_probability(cp, opp_cp, 0.85, tie_rate)
            
            rand_val = random.random()
            if rand_val < tie_rate:
                ties += 1
            elif rand_val < tie_rate + win_prob * (1 - tie_rate):
                wins += 1
        
        # Check if made top cut (11+ wins or equivalent points)
        points = wins * 3 + ties * 1
        if points >= 33:  # 11-2-0 or better
            total_wins += 1
    
    return total_wins / simulations * 100

# Test the problematic cases from the standings
print("🚨 DEBUGGING SKILL SYSTEM FAILURE")
print("=" * 60)

problematic_players = [
    (55, "Ryan Gomez"),
    (134, "Connor Jackson"), 
    (161, "Lily Walker316"),
    (200, "Daniel X. Sanders"),
    (230, "Parker Lopez"),
    (251, "Nathan Ramos")
]

# Generate typical opponent CPs (mix of fake and real players)
typical_opponents = []
# 80% fake players (50-331 CP)
for _ in range(800):
    typical_opponents.append(random.randint(50, 331))
# 20% real players (332-2000 CP)  
for _ in range(200):
    typical_opponents.append(random.randint(332, 2000))

print("Testing against realistic field composition:")
print(f"{'Player':<20} {'CP':<4} {'Skill':<8} {'vs 500 CP':<10} {'vs 1000 CP':<11} {'11-2+ Prob':<12}")
print("-" * 75)

for cp, name in problematic_players:
    skill = calculate_skill_level(cp)
    win_vs_500, _ = calculate_win_probability(cp, 500)
    win_vs_1000, _ = calculate_win_probability(cp, 1000)
    tournament_prob = simulate_tournament_probability(cp, typical_opponents)
    
    print(f"{name:<20} {cp:<4} {skill:<8.3f} {win_vs_500*100:<10.1f}% {win_vs_1000*100:<11.1f}% {tournament_prob:<12.3f}%")

print(f"\n🔍 ANALYSIS:")
print(f"   • Ryan Gomez (55 CP) making Top 16 should be ~0.001% probability")
print(f"   • If we're seeing 6/8 low CP players in top cut, something is very wrong")
print(f"   • Either the skill function isn't being applied, or there's a bug")

print(f"\n💡 SOLUTION:")
print(f"   • Need to create completely fresh notebook with verified skill system")
print(f"   • Add debug prints to verify skill function is being called correctly")
print(f"   • Test with even more extreme penalties if needed") 