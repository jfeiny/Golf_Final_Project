import sqlite3
import csv
from pathlib import Path

# Set path to the database (../dbs/current_world_rankings.db)
base_dir = Path(__file__).resolve().parent.parent
db_path = base_dir / "dbs" / "current_world_rankings.db"

# Set output CSV path (in the same directory as this script)
output_path = Path(__file__).resolve().parent / "player_averages.csv"

# Connect to the database
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Fetch player data
cursor.execute("SELECT first_name, last_name, events_played, points FROM players")
rows = cursor.fetchall()
conn.close()

# Prepare and write CSV
with open(output_path, mode="w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Player", "Events Played", "Total Points", "Average Points"])

    for row in rows:
        first_name, last_name, events, points = row
        full_name = f"{first_name} {last_name}"
        try:
            avg_points = round(points / events, 2) if events > 0 else 0.0
        except Exception:
            avg_points = 0.0
        writer.writerow([full_name, events, round(points, 2), avg_points])

print(f"✅ CSV file written to: {output_path}")
