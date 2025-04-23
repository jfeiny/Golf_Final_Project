import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load the CSV with the correct relative path
csv_path = Path(__file__).resolve().parent.parent / "Data Processing" / "golfer_win_predictions.csv"
df = pd.read_csv(csv_path)

# Clean up column names
df.columns = [col.strip() for col in df.columns]

# Sort by LikelihoodScore and take top 5 for clearer pie chart
top_df = df.sort_values(by="LikelihoodScore", ascending=False).head(5)

# Create pie chart
plt.figure(figsize=(8, 8))
plt.pie(
    top_df["LikelihoodScore"],
    labels=top_df["Name"],
    autopct="%1.1f%%",
    startangle=140
)
plt.title("Top 5 Projected Players by Likelihood to Win")
plt.tight_layout()
plt.show()
