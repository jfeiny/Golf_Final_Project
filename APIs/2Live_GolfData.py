import requests
import sqlite3
import os
from pathlib import Path

def fetch_and_store_data(year, statId,
                         batch_size=25,
                         api_key="59395f455dmsh84b486008bbbfdbp147b10jsnb41e22684ecc",
                         table_name="FedEx_Cup_Standings"):

    url = "https://live-golf-data.p.rapidapi.com/stats"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "live-golf-data.p.rapidapi.com"
    }

    # Unified DB path
    base_dir = Path(__file__).resolve().parent.parent
    db_path = base_dir / "dbs" / "All_Golf_Data.db"
    os.makedirs(db_path.parent, exist_ok=True)

    # Connect to unified DB
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create main table
    cursor.execute(f'''
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

    # Create tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS FetchTracker (
            statId TEXT PRIMARY KEY,
            lastIndex INTEGER
        )
    ''')

    # Get last start_index
    cursor.execute("SELECT lastIndex FROM FetchTracker WHERE statId = ?", (statId,))
    result = cursor.fetchone()
    start_index = result[0] if result else 0

    try:
        # Get name → ID map
        cursor.execute("SELECT id, first_name, last_name FROM Current_rankings")
        rows = cursor.fetchall()
        name_to_id = {(first.lower(), last.lower()): pid for pid, first, last in rows}

        # Fetch next batch
        response = requests.get(url, headers=headers, params={"year": str(year), "statId": str(statId)})
        response.raise_for_status()
        data = response.json()

        rankings = data.get("rankings", [])
        batch = rankings[start_index:start_index + batch_size]

        if not batch:
            print("✅ All data already fetched.")
            return

        inserted = 0
        for item in batch:
            first = item.get("firstName", "").strip()
            last = item.get("lastName", "").strip()
            key = (first.lower(), last.lower())

            player_id = name_to_id.get(key)

            if player_id:
                cursor.execute(f'''
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
                print(f"⚠️ Skipped: {first} {last} not found in Current_rankings")

        # Update tracker
        new_index = start_index + batch_size
        cursor.execute('''
            INSERT INTO FetchTracker (statId, lastIndex)
            VALUES (?, ?)
            ON CONFLICT(statId) DO UPDATE SET lastIndex=excluded.lastIndex
        ''', (statId, new_index))

        conn.commit()
        print(f"✅ Inserted {inserted} new records (index {start_index}–{new_index - 1})")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        conn.close()

# Example run
if __name__ == "__main__":
    fetch_and_store_data(2024, "02671")
