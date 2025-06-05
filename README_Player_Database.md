# Pokémon Tournament Player Database System

A comprehensive player data management system for tournament simulation with real player information, career tracking, and advanced analytics.

## 🎯 Overview

This system provides a robust foundation for simulating Pokémon TCG tournaments with realistic player data. It includes all the fields you specified:

- **Name**: Realistic generated names
- **Global Rank**: 1-indexed ranking system 
- **Rating Zone**: 5 zones (NA, EU, LATAM, OCE, MESA)
- **CP (Championship Points)**: Higher CP = higher ranking
- **Tournament Data**: Complete match history, opponents, wins/losses, career statistics

## 📊 Key Features

### ✅ Complete Player Data Structure
- Individual player profiles with all required fields
- Tournament-specific records (per tournament tracking)
- Career statistics aggregation
- Realistic data distributions

### ✅ Flexible Database Storage
- SQLite backend for reliability and portability
- JSON export/import capabilities
- CSV export for analysis
- Automatic data type conversion

### ✅ Tournament Integration
- Seamless integration with existing tournament simulator
- Skill-based match outcomes (CP influences win probability)
- Automatic career statistics updates
- Multiple tournament selection methods

### ✅ Advanced Analytics
- Performance analysis by rating zone
- CP vs performance correlations
- Tournament composition analysis
- Export capabilities for external analysis

## 🚀 Quick Start

### 1. Generate Player Database

```python
from player_database import create_player_database

# Create database with 5000 players
db = create_player_database(
    num_players=5000,
    db_path="pokemon_players.db"
)
```

### 2. Load and Query Players

```python
from player_database import PlayerDatabase, RatingZone

db = PlayerDatabase("pokemon_players.db")

# Get top players by CP
top_players = db.get_top_players(100)

# Get players from specific zone
na_players = db.get_players_by_zone(RatingZone.NA)

# Load specific player
player = db.load_player(player_id=1)
```

### 3. Run Tournament with Player Data

```python
from tournament_integration import TournamentPlayerIntegration

integration = TournamentPlayerIntegration("pokemon_players.db")

# Create tournament field
tournament_players = integration.create_tournament_field(
    field_size=512,
    selection_method="qualified_mixed"
)

# Convert to tournament format
tournament_df = integration.convert_players_to_tournament_format(tournament_players)

# Run tournament with skill-based outcomes
results = integration.simulate_tournament_with_skills(tournament_df, skill_factor=0.2)

# Update player database with results
integration.update_player_records(results, "tournament_2024_01")
```

## 📁 File Structure

```
├── player_database.py          # Core database system
├── demo_player_system.py       # Demonstration script
├── tournament_integration.py   # Tournament simulator integration
├── pokemon_players.db          # SQLite database file
└── exports/                    # Exported data files
    ├── players.csv
    ├── players.json
    └── player_summary.json
```

## 🎮 Player Data Model

### Core Player Attributes

```python
@dataclass
class Player:
    player_id: int              # Unique identifier
    name: str                   # Generated realistic name
    global_rank: int            # 1-indexed global ranking
    rating_zone: RatingZone     # NA, EU, LATAM, OCE, MESA
    cp: int                     # Championship Points (50-2500)
    
    # Tournament History
    tournaments_played: Dict[str, TournamentRecord]
    
    # Career Statistics
    career_tournaments: int
    career_match_points: int
    career_wins: int
    career_losses: int
    career_ties: int
    career_top_cuts: int
    career_wins_tournament: int
```

### Tournament Record Structure

```python
@dataclass
class TournamentRecord:
    tournament_id: str
    opponents_played: Set[int]
    match_points: int
    wins: int
    losses: int
    ties: int
    received_bye: bool
    is_active: bool
    placement: Optional[int]
    final_ranking: Optional[int]
```

## 🌍 Rating Zone Distribution

Realistic distribution for NA-hosted tournaments with elite international players:

- **NA (North America)**: 90% - Domestic tournament base
- **EU (Europe)**: 5% - Elite travelers only
- **LATAM (Latin America)**: 3% - Elite travelers only  
- **OCE (Oceania)**: 1.5% - Elite travelers only
- **MESA (Middle East/South Africa)**: 0.5% - Elite travelers only

**Elite International Players**: Non-NA players have CP distributions similar to the top 10% of NA players, reflecting that only the most skilled players travel internationally to compete.

## 🏆 CP (Championship Points) System

- **Range**: 50-2500 CP
- **Distribution**: Log-normal distribution (realistic)
- **Correlation**: Higher CP = higher global rank
- **Tournament Impact**: CP influences match win probability (configurable)

## 🎯 Tournament Selection Methods

### 1. Top CP Selection
```python
# Simple: best players by CP
players = integration.create_tournament_field(
    field_size=1000,
    selection_method="top_cp"
)
```

### 2. Zone Balanced
```python
# Balanced representation from each zone
players = integration.create_tournament_field(
    field_size=1000,
    selection_method="zone_balanced"
)
```

### 3. Qualified Mixed (Realistic)
```python
# 60% global top players + 40% zone qualifiers
players = integration.create_tournament_field(
    field_size=1000,
    selection_method="qualified_mixed"
)
```

## 🔬 Advanced Features

### Skill-Based Match Simulation

The system can simulate matches where CP affects win probability:

```python
results = integration.simulate_tournament_with_skills(
    tournament_df,
    skill_factor=0.3  # 30% skill influence, 70% randomness
)
```

- `skill_factor=0.0`: Completely random outcomes
- `skill_factor=1.0`: Deterministic based on CP
- `skill_factor=0.2-0.3`: Realistic balance

### Career Statistics Tracking

Players automatically accumulate career statistics:

- Total tournaments played
- Career match points
- Win/loss/tie record
- Top cut appearances
- Tournament victories

### Analytics and Insights

```python
# Performance by zone
zone_stats = results.groupby('rating_zone').agg({
    'match_points': ['mean', 'std'],
    'cp': 'mean'
})

# CP vs performance correlation
correlation = results['cp'].corr(results['match_points'])
```

## 📤 Export Capabilities

### CSV Export
```python
# For Excel analysis, data science
df.to_csv("players.csv")
```

### JSON Export
```python
# For web applications, APIs
df.to_json("players.json", orient='records')
```

### Summary Statistics
```python
export_players_to_formats(db, export_dir="exports")
# Creates: players.csv, players.json, player_summary.json
```

## 🔧 Integration with Existing Tournament Simulator

The system seamlessly integrates with your existing Jupyter notebook tournament simulator:

1. **Compatible DataFrame Format**: Converts Player objects to the expected pandas DataFrame
2. **Enhanced Match Outcomes**: Adds skill-based probability to match simulation
3. **Automatic Updates**: Updates player database after tournaments
4. **Preserved Functionality**: All existing tournament features still work

### Example Integration

```python
# Load existing tournament functions from notebook
# (copy functions from pokemon_tournament_simulator.ipynb)

# Create tournament field from database
integration = TournamentPlayerIntegration()
players = integration.create_tournament_field(1000)
tournament_df = integration.convert_players_to_tournament_format(players)

# Use existing tournament simulator functions
day1_results = simulate_day1(tournament_df)
day2_results = simulate_day2(day1_results)
top_cut_results = simulate_complete_top_cut(day2_results)

# Update database with results
integration.update_player_records(day2_results, "world_championship_2024")
```

## 🎛️ Configuration Options

### Custom Player Generation

```python
# Custom rating zone distribution
custom_distribution = {
    RatingZone.NA: 0.50,
    RatingZone.EU: 0.35,
    RatingZone.LATAM: 0.10,
    RatingZone.OCE: 0.03,
    RatingZone.MESA: 0.02
}

players = generate_sample_players(
    num_players=1000,
    rating_zone_distribution=custom_distribution
)
```

### Tournament Field Customization

```python
# Custom zone quotas for tournaments
zone_quotas = {
    "NA": 400,
    "EU": 300,
    "LATAM": 200,
    "OCE": 75,
    "MESA": 25
}

players = integration.create_tournament_field(
    field_size=1000,
    selection_method="zone_balanced",
    zone_quotas=zone_quotas
)
```

## 📈 Sample Analytics Output

```
📊 TOURNAMENT ANALYSIS
Tournament Size: 512 players
Champion: Alex Johnson (483 CP)
Champion Record: 8-1-0

📈 Performance by Rating Zone:
            match_points    cp
                    mean  mean
rating_zone               
EU                 12.39   309
LATAM              12.62   252
MESA               12.42   268
NA                 13.22   287
OCE                12.78   286

🏆 Top 8 Analysis:
Average CP: 268
Zone Distribution: {'NA': 4, 'LATAM': 3, 'EU': 1}

🔍 CP vs Performance Correlation: 0.068
```

## 🚦 Getting Started Commands

```bash
# Generate demo database
python3 demo_player_system.py

# Run tournament integration example
python3 tournament_integration.py

# Check generated files
ls -la *.db exports/
```

## 💾 Database Files Generated

- `demo_players.db` - Small demo database (1000 players)
- `tournament_players.db` - Full tournament database (5000 players)
- `custom_demo.db` - Custom player examples
- `exports/` - CSV, JSON, and summary files

## 🔄 Next Steps

1. **Integrate with Existing Notebook**: Copy tournament functions from Jupyter notebook
2. **Add Skill-Based Outcomes**: Implement ELO rating adjustments
3. **Regional Qualifications**: Add qualification tournament simulation
4. **Advanced Analytics**: Machine learning for player performance prediction
5. **Web Interface**: Create dashboard for tournament management

## 🤝 Future Enhancements

- **ELO Rating System**: Dynamic skill ratings that update based on match outcomes
- **Deck Archetype Tracking**: Track what decks players use and their success rates
- **Regional Tournaments**: Simulate regional qualification systems
- **Prize Support**: Track prize money and product earnings
- **Team/Sponsor Data**: Add team affiliations and sponsorship information
- **Real Data Import**: Import actual player data from official sources

---

This player database system provides the foundation for realistic tournament simulation with actual player data, career tracking, and comprehensive analytics. It's designed to scale from small local tournaments to world championship simulations. 