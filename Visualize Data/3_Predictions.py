import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv("golfer_win_predictions.csv")

# Clean up column names
df.columns = [col.strip() for col in df.columns]

# Sort by LikelihoodScore and take top 10
top_df = df.sort_values(by="LikelihoodScore", ascending=False).head(10)
top_df = top_df[::-1]  # Flip for horizontal bar chart

# Plot
plt.figure(figsize=(10, 6))
plt.barh(top_df["Name"], top_df["LikelihoodScore"])
plt.xlabel("Likelihood Score")
plt.title("Top 10 Projected Players by Likelihood to Win")
plt.tight_layout()
plt.show()
