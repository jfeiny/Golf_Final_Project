from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Resolve the CSV path relative to this script's location
csv_path = Path(__file__).resolve().parent / "../Data Processing/player_averages.csv"

# Load the CSV
df = pd.read_csv(csv_path)

# Ensure Average Points column is numeric
df["Average Points"] = pd.to_numeric(df["Average Points"], errors="coerce")

# Sort by Average Points and select the top 25
top_25 = df.sort_values("Average Points", ascending=False).head(25)

# Plot horizontal bar chart
plt.figure(figsize=(12, 8))
plt.barh(top_25["Player"], top_25["Average Points"])
plt.xlabel("Average Points")
plt.title("Top 25 Players by Average Points")
plt.gca().invert_yaxis()  # Puts highest scorer at the top
plt.tight_layout()
plt.show()
