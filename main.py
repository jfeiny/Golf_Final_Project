from APIs.Sports_io import fetch_and_store_data

def get_top_players(season, total_players=150, batch_size=25):
    for start_index in range(0, total_players, batch_size):
        print(f"\nFetching players {start_index + 1} to {start_index + batch_size}...")
        fetch_and_store_data(season, start_index=start_index, batch_size=batch_size)

if __name__ == "__main__":
    season = 2024  # You can replace this or make it dynamic
    get_top_players(season)
