import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Build the correct path to the database
base_dir = Path(__file__).resolve().parent.parent
db_path = base_dir / "dbs" / "FedEx_Cup_Standings_2024.db"

# Connect to the database
conn = sqlite3.connect(str(db_path))

# Query top 25 players by rank
query = """
    SELECT id, firstName, lastName, rank, numWins, numTop10s
    FROM FedEx_Cup_Standings
    ORDER BY rank ASC
    LIMIT 25
"""
data = pd.read_sql(query, conn)
conn.close()

# Add a Player column for labeling
data["Player"] = data["firstName"] + " " + data["lastName"]

# Reorder columns
data = data[["Player", "rank", "numWins", "numTop10s"]]

# Plot wins and top 10s side by side
plt.figure(figsize=(14, 8))
x = range(len(data))
plt.bar(x, data["numWins"], width=0.4, label="Wins", align='center')
plt.bar([i + 0.4 for i in x], data["numTop10s"], width=0.4, label="Top 10s", align='center')
plt.xticks([i + 0.2 for i in x], data["Player"], rotation=90)
plt.xlabel("Player")
plt.ylabel("Count")
plt.title("Top 25 FedEx Ranked Players: Wins vs Top 10 Finishes")
plt.legend()
plt.tight_layout()
plt.show()
