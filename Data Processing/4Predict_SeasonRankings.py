import sqlite3
import pandas as pd
from pathlib import Path

# Paths
base_dir = Path(__file__).resolve().parent.parent
db_path = base_dir / "dbs" / "All_Golf_Data.db"
output_path = Path(__file__).resolve().parent / "golfer_win_predictions.csv"

# Connect to database
conn = sqlite3.connect(str(db_path))

# Join FedEx_Cup_Standings with Current_rankings in SQL
query = """
SELECT
    f.id AS GolferID,
    f.firstName || ' ' || f.lastName AS Name,
    f.numWins AS Wins,
    f.numTop10s AS Top10s,
    c.events_played AS EventsPlayed,
    c.points AS TotalPoints
FROM
    FedEx_Cup_Standings f
INNER JOIN
    Current_rankings c ON f.id = c.id
"""
df = pd.read_sql_query(query, conn)
conn.close()

# Compute average points and likelihood score
df["AveragePoints"] = df.apply(lambda row: round(row["TotalPoints"] / row["EventsPlayed"], 2) if row["EventsPlayed"] > 0 else 0.0, axis=1)

df["LikelihoodScore"] = (
    df["Wins"] * 10 +
    df["Top10s"] * 5 +
    df["AveragePoints"] * 3
)

# Reorder columns
final_df = df.sort_values(by="LikelihoodScore", ascending=False)[
    ["GolferID", "Name", "Wins", "Top10s", "AveragePoints", "LikelihoodScore"]
]

# Write to CSV
final_df.to_csv(output_path, index=False)
print(f"✅ Golfer predictions written to: {output_path}")
