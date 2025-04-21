import requests
import sqlite3
import os
from pathlib import Path

# API endpoint and headers
url = "https://api.sportradar.com/golf/trial/v3/en/players/wgr/2025/rankings.json?api_key=7mJFMR3SY3uhkWXNV4F83Zyl9WoaQUMJThtsB6k7"
headers = {"accept": "application/json"}

# Set the unified DB path
base_dir = Path(__file__).resolve().parent.parent
db_dir = base_dir / "dbs"
db_path = db_dir / "All_Golf_Data.db"
os.makedirs(db_dir, exist_ok=True)

table_name = "Current_rankings"

def get_last_player_id():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create table if not exists in shared DB
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        events_played INTEGER,
        points REAL
    )
    ''')

    cursor.execute(f"SELECT MAX(id) FROM {table_name}")
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

        # Step 4: Store each new player
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        for player in next_25_players:
            first_name = player.get("first_name", "N/A")
            last_name = player.get("last_name", "N/A")

            stats = player.get("statistics", {})
            events_played = stats.get("events_played", 0)
            total_points = stats.get("points", 0.0)

            cursor.execute(f'''
            INSERT INTO {table_name} (first_name, last_name, events_played, points)
            VALUES (?, ?, ?, ?)
            ''', (first_name, last_name, events_played, total_points))

        conn.commit()
        conn.close()

        print(f"✅ Added {len(next_25_players)} players to '{table_name}' in {db_path}.")

    except ValueError as e:
        print(f"❌ Error decoding JSON: {e}")
else:
    print(f"❌ Failed to retrieve data. Status code: {response.status_code}")
