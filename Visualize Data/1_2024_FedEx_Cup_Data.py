import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load the CSV
csv_path = Path(__file__).resolve().parent / "../Data Processing/fedex_total_achievements.csv"
df = pd.read_csv(csv_path)

# Sort by TotalAchievements
df_sorted = df.sort_values(by="TotalAchievements", ascending=False).head(25)

# Plot Wins and Top10s side by side
plt.figure(figsize=(14, 8))
x = range(len(df_sorted))
plt.bar(x, df_sorted["Wins"], width=0.4, label="Wins", align='center')
plt.bar([i + 0.4 for i in x], df_sorted["Top10s"], width=0.4, label="Top 10s", align='center')
plt.xticks([i + 0.2 for i in x], df_sorted["Name"], rotation=90)
plt.xlabel("Player")
plt.ylabel("Count")
plt.title("Top 25 FedEx Cup Players: Wins vs Top 10 Finishes")
plt.legend()
plt.tight_layout()
plt.show()
