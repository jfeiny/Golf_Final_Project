import requests
import sqlite3
import os
from pathlib import Path

# API endpoint and headers
url = "https://api.sportradar.com/golf/trial/v3/en/players/wgr/2025/rankings.json?api_key=7mJFMR3SY3uhkWXNV4F83Zyl9WoaQUMJThtsB6k7"
headers = {"accept": "application/json"}

# Build safe path to ../dbs/current_world_rankings.db
base_dir = Path(__file__).resolve().parent.parent  # Go one level up
db_dir = base_dir / "dbs"
db_path = db_dir / "current_world_rankings.db"
os.makedirs(db_dir, exist_ok=True)

# Ensure the table exists and return last assigned autoincrement ID
def get_last_player_id():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Updated schema: replace avg_points with events_played
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        events_played INTEGER,
        points REAL
    )
    ''')

    cursor.execute("SELECT MAX(id) FROM players")
    last_player_id = cursor.fetchone()[0]
    conn.close()
    return last_player_id if last_player_id else 0

# Step 1: Get last local ID
last_player_id = get_last_player_id()

# Step 2: Make API call
response = requests.get(url, headers=headers)

if response.status_code == 200:
    try:
        data = response.json()
        players = data.get('players', [])

        # Step 3: Select next 25 players after last stored
        next_25_players = players[last_player_id:last_player_id + 25]

        # Step 4: Store each new player with events_played + points
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        for player in next_25_players:
            first_name = player.get("first_name", "N/A")
            last_name = player.get("last_name", "N/A")

            stats = player.get("statistics", {})
            events_played = stats.get("events_played", 0)
            total_points = stats.get("points", 0.0)

            cursor.execute('''
            INSERT INTO players (first_name, last_name, events_played, points)
            VALUES (?, ?, ?, ?)
            ''', (first_name, last_name, events_played, total_points))

        conn.commit()
        conn.close()

        print(f"✅ Successfully added {len(next_25_players)} new players to the database at {db_path}.")

    except ValueError as e:
        print(f"❌ Error decoding JSON: {e}")
else:
    print(f"❌ Failed to retrieve data. Status code: {response.status_code}")
