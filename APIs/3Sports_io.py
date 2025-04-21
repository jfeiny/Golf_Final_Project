import requests
import sqlite3
import os
from pathlib import Path

API_KEY = 'ffa103f6bb8e44a0a6c442f4186b5f34'
TOURNAMENT_IDS = ['628', '656', '657', '655']
API_BASE = 'https://api.sportsdata.io/golf/v2/json/PlayerTournamentRoundScoresFinal/'
BATCH_SIZE = 25
MAX_PER_TOURNAMENT = 100

# Unified database path
base_dir = Path(__file__).resolve().parent.parent
db_path = base_dir / "dbs" / "All_Golf_Data.db"
os.makedirs(db_path.parent, exist_ok=True)

def fetch_scores(tournament_id):
    url = f"{API_BASE}{tournament_id}?key={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def setup_db():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS golfers (
            GolferID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            PlayerID INTEGER,
            GolferID INTEGER,
            TournamentID TEXT,
            TotalScore INTEGER,
            PRIMARY KEY (PlayerID, TournamentID),
            FOREIGN KEY (GolferID) REFERENCES golfers(GolferID)
        )
    ''')

    conn.commit()
    return conn

def get_existing_player_ids(conn, tournament_id):
    cursor = conn.cursor()
    cursor.execute("SELECT PlayerID FROM scores WHERE TournamentID = ?", (tournament_id,))
    return set(row[0] for row in cursor.fetchall())

def get_or_create_golfer_id(conn, name):
    cursor = conn.cursor()
    cursor.execute("SELECT GolferID FROM golfers WHERE Name = ?", (name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO golfers (Name) VALUES (?)", (name,))
    conn.commit()
    return cursor.lastrowid

def insert_batch(conn, players, tournament_id):
    cursor = conn.cursor()
    inserted = 0
    for player in players:
        player_id = player.get("PlayerID")
        total_score = player.get("TotalScore")

        if total_score is None or player_id is None:
            continue

        name = player.get("Name") or f"{player.get('FirstName', '')} {player.get('LastName', '')}".strip()
        name = name.strip()
        golfer_id = get_or_create_golfer_id(conn, name)

        try:
            cursor.execute('''
                INSERT INTO scores (PlayerID, GolferID, TournamentID, TotalScore)
                VALUES (?, ?, ?, ?)
            ''', (player_id, golfer_id, tournament_id, total_score))
            inserted += 1
        except sqlite3.IntegrityError:
            continue  # Skip duplicates

    conn.commit()
    return inserted

def main():
    conn = setup_db()
    total_inserted = 0

    for tournament_id in TOURNAMENT_IDS:
        existing_ids = get_existing_player_ids(conn, tournament_id)
        existing_count = len(existing_ids)

        if existing_count >= MAX_PER_TOURNAMENT:
            print(f"✅ Tournament {tournament_id} is already full.")
            continue

        try:
            data = fetch_scores(tournament_id)
        except Exception as e:
            print(f"❌ Failed to fetch scores for Tournament {tournament_id}: {e}")
            continue

        new_players = [p for p in data if p.get("TotalScore") is not None and p.get("PlayerID") not in existing_ids]
        slots_remaining = MAX_PER_TOURNAMENT - existing_count
        num_to_add = min(len(new_players), slots_remaining, BATCH_SIZE - total_inserted)

        if num_to_add <= 0:
            continue

        inserted = insert_batch(conn, new_players[:num_to_add], tournament_id)
        total_inserted += inserted
        print(f"✅ Added {inserted} players to Tournament {tournament_id}")

        if total_inserted >= BATCH_SIZE:
            break

    conn.close()

    if total_inserted == 0:
        print("🎉 All tournaments are full or no new players to add.")
    else:
        print(f"🔁 Added {total_inserted} total players this run.")

if __name__ == "__main__":
    main()
