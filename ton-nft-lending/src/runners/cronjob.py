import time

from ..db.database import Database

INTERVAL = 5  # seconds


def check_and_update_nft_status():
    database = Database()
    values = database.get_last_configs()
    nfts = database.get_nfts_by_status("borrowed")
    for nft in nfts:
        history = database.get_latest_history_by_nft_id(nft.id)
        if not history or (history.occurred_at + values.borrow_duration_in_second < int(time.time())):
            database.update_nft_status_by_nft_id(nft.id, "available")


while True:
    print("Updating nft status\n\n")
    check_and_update_nft_status()
    print(f"\n\nDone, sleep for {INTERVAL} seconds")
    time.sleep(INTERVAL)
