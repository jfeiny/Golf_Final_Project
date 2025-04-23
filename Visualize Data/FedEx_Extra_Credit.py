import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load the CSV
csv_path = Path(__file__).resolve().parent.parent / "Data Processing" / "fedex_total_achievements.csv"
df = pd.read_csv(csv_path)

# Sort by TotalAchievements and take top 10 for better pie visibility
top_10 = df.sort_values(by="TotalAchievements", ascending=False).head(10)

# Pie chart of Wins
plt.figure(figsize=(8, 8))
plt.pie(
    top_10["Wins"],
    labels=top_10["Name"],
    autopct="%1.1f%%",
    startangle=140
)
plt.title("Share of Wins Among Top 10 FedEx Cup Players")
plt.tight_layout()
plt.show()
