import requests
import sqlite3
import os
from pathlib import Path

def fetch_and_store_data(season, start_index=0, batch_size=25,
                         api_base_url="https://api.sportsdata.io/golf/v2/json/Rankings/",
                         api_key="ffa103f6bb8e44a0a6c442f4186b5f34",
                         table_name="rankings"):
    """
    Fetches a batch of golf ranking data (25 at a time) from the SportsDataIO API
    and appends it to a structured SQLite database stored in /dbs at the project root.
    """

    # Dynamically build db path relative to this file
    base_dir = Path(__file__).resolve().parent.parent  # Go from /APIs to project root
    db_dir = base_dir / "dbs"
    db_file = db_dir / "golf_rankings.db"

    # Ensure dbs/ directory exists
    os.makedirs(db_dir, exist_ok=True)

    # Connect to DB
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            PlayerSeasonID INTEGER,
            Season INTEGER,
            PlayerID INTEGER,
            Name TEXT,
            WorldGolfRank INTEGER,
            WorldGolfRankLastWeek INTEGER,
            Events INTEGER,
            AveragePoints REAL,
            TotalPoints REAL,
            PointsLost REAL,
            PointsGained REAL,
            UNIQUE(PlayerID, Season)
        )
    ''')

    try:
        response = requests.get(f"{api_base_url}{season}?key={api_key}")
        response.raise_for_status()
        data = response.json()

        batch = data[start_index:start_index + batch_size]

        for item in batch:
            cursor.execute(f'''
                INSERT OR IGNORE INTO {table_name} (
                    PlayerSeasonID, Season, PlayerID, Name, WorldGolfRank,
                    WorldGolfRankLastWeek, Events, AveragePoints, TotalPoints,
                    PointsLost, PointsGained
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.get("PlayerSeasonID"),
                item.get("Season"),
                item.get("PlayerID"),
                item.get("Name"),
                item.get("WorldGolfRank"),
                item.get("WorldGolfRankLastWeek"),
                item.get("Events"),
                item.get("AveragePoints"),
                item.get("TotalPoints"),
                item.get("PointsLost"),
                item.get("PointsGained"),
            ))

        conn.commit()
        print(f"Stored {len(batch)} players from index {start_index} for season {season}.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for season {season}: {e}")
    except ValueError as e:
        print(f"Error processing data for season {season}: {e}")
    finally:
        conn.close()


# Uncomment to test
# fetch_and_store_data(2024, start_index=0)
