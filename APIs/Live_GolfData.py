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

    # Build safe path to dbs/FedEx_Cup_Standings.db at project root
    base_dir = Path(__file__).resolve().parent.parent
    db_path = base_dir / "dbs" / "FedEx_Cup_Standings.db"
    os.makedirs(db_path.parent, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playerId TEXT,
            firstName TEXT,
            lastName TEXT,
            rank INTEGER,
            previousRank TEXT,
            numWins INTEGER,
            numTop10s INTEGER
        )
    ''')

    try:
        querystring = {"year": str(year), "statId": str(statId)}
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()

        # ✅ Extract the player list from data["rankings"]
        items = data.get("rankings", [])

        # Slice the batch (simulate pagination)
        batch = items[start_index:start_index + batch_size]

        for item in batch:
            cursor.execute(f'''
                INSERT INTO {table_name} (
                    playerId, firstName, lastName, rank, previousRank, numWins, numTop10s
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.get("playerId"),
                item.get("firstName"),
                item.get("lastName"),
                int(item["rank"].get("$numberInt", 0)),
                item.get("previousRank"),
                int(item.get("numWins", 0)),
                int(item.get("numTop10s", 0))
            ))

        conn.commit()
        print(f"✅ Stored {len(batch)} player records from index {start_index} for statId={statId}, year={year}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decoding error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        conn.close()


# Example usage
fetch_and_store_data(2024, "02671", start_index=0)
