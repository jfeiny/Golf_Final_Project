from APIs.Sports_io import fetch_and_store_data as fetch_sportsdataio
from APIs.Live_GolfData import fetch_and_store_data as fetch_livegolfdata

def get_top_players_sportsdataio(season, total_players=150, batch_size=25):
    for start_index in range(0, total_players, batch_size):
        print(f"\n[SportsDataIO] Fetching players {start_index + 1} to {start_index + batch_size}...")
        fetch_sportsdataio(season, start_index=start_index, batch_size=batch_size)

def get_top_players_livegolf(year, stat_id="02671", total_players=150, batch_size=25):
    for start_index in range(0, total_players, batch_size):
        print(f"\n[LiveGolfData] Fetching FedExCup players {start_index + 1} to {start_index + batch_size}...")
        fetch_livegolfdata(year, stat_id, start_index=start_index, batch_size=batch_size)

if __name__ == "__main__":
    season = 2024
    stat_id = "02671"  # FedEx Cup Standings

    print("\n=== Pulling from SportsDataIO ===")
    get_top_players_sportsdataio(season)

    print("\n=== Pulling from Live Golf Data (FedEx Cup) ===")
    get_top_players_livegolf(season, stat_id=stat_id)

