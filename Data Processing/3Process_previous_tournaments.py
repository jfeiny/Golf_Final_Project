import sqlite3
import pandas as pd
from pathlib import Path

# Unified DB
base_dir = Path(__file__).resolve().parent.parent
DB_FILE = base_dir / "dbs" / "All_Golf_Data.db"
TOURNAMENT_IDS = ['628', '656', '657', '655']
OUTPUT_CSV = Path(__file__).resolve().parent / "golfer_performance.csv"

def main():
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()

    # Map GolferID to Name
    cursor.execute("SELECT GolferID, Name FROM golfers")
    golfer_names = {row[0]: row[1] for row in cursor.fetchall()}

    stats = {}  # {GolferID: {"Wins": 0, "Top10s": 0}}

    for tid in TOURNAMENT_IDS:
        cursor.execute("""
            SELECT GolferID, TotalScore
            FROM scores
            WHERE TournamentID = ?
            ORDER BY TotalScore ASC
        """, (tid,))
        rows = cursor.fetchall()

        if not rows:
            continue

        top_10 = rows[:10]
        best_score = rows[0][1]

        for golfer_id, score in top_10:
            if golfer_id not in stats:
                stats[golfer_id] = {"Wins": 0, "Top10s": 0}
            stats[golfer_id]["Top10s"] += 1
            if score == best_score:
                stats[golfer_id]["Wins"] += 1

    # Format output
    data = []
    for golfer_id, s in stats.items():
        data.append({
            "GolferID": golfer_id,
            "Name": golfer_names.get(golfer_id, "Unknown"),
            "Wins": s["Wins"],
            "Top10s": s["Top10s"]
        })

    df = pd.DataFrame(data)
    df.sort_values(by=["Wins", "Top10s"], ascending=False, inplace=True)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"✅ Saved golfer performance to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
