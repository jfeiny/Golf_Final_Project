import requests
import sqlite3
import json
import os
from pathlib import Path

def fetch_and_store_data(year, statId, start_index=0, batch_size=25,
                         api_key="59395f455dmsh84b486008bbbfdbp147b10jsnb41e22684ecc",
                         table_name="FedEx_Cup_Standings"):

    url = "https://live-golf-data.p.rapidapi.com/stats"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "live-golf-data.p.rapidapi.com"
    }

    # Paths
    base_dir = Path(__file__).resolve().parent.parent
    fedex_db_path = base_dir / "dbs" / "FedEx_Cup_Standings_2024.db"
    rankings_db_path = base_dir / "dbs" / "current_world_rankings.db"
    os.makedirs(fedex_db_path.parent, exist_ok=True)

    # Connect to both databases
    conn_fedex = sqlite3.connect(str(fedex_db_path))
    conn_rankings = sqlite3.connect(str(rankings_db_path))
    cursor_fedex = conn_fedex.cursor()
    cursor_rankings = conn_rankings.cursor()

    # Create FedEx table with id = existing player id
    cursor_fedex.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            firstName TEXT,
            lastName TEXT,
            rank INTEGER,
            previousRank TEXT,
            numWins INTEGER,
            numTop10s INTEGER
        )
    ''')

    try:
        # Load ID lookup from current_world_rankings.db
        cursor_rankings.execute("SELECT id, first_name, last_name FROM players")
        rows = cursor_rankings.fetchall()
        name_to_id = {(first.lower(), last.lower()): pid for pid, first, last in rows}

        # Request data
        querystring = {"year": str(year), "statId": str(statId)}
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()

        items = data.get("rankings", [])
        batch = items[start_index:start_index + batch_size]

        inserted = 0
        for item in batch:
            first = item.get("firstName", "").strip()
            last = item.get("lastName", "").strip()
            key = (first.lower(), last.lower())

            player_id = name_to_id.get(key)

            if player_id:
                cursor_fedex.execute(f'''
                    INSERT OR REPLACE INTO {table_name} (
                        id, firstName, lastName, rank, previousRank, numWins, numTop10s
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    player_id,
                    first,
                    last,
                    int(item.get("rank", {}).get("$numberInt", 0)),
                    item.get("previousRank"),
                    int(item.get("numWins", 0)),
                    int(item.get("numTop10s", 0))
                ))
                inserted += 1
            else:
                print(f"⚠️ Skipped: {first} {last} not found in current_world_rankings.db")

        conn_fedex.commit()
        print(f"✅ Inserted {inserted} players into {table_name} using external IDs")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        conn_fedex.close()
        conn_rankings.close()

# Example usage:
# fetch_and_store_data(2024, "02671", start_index=0)
