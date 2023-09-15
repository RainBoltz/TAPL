import time
import json
import base64
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from .tonapi import get_user_onchain_nfts, get_event
from ..common.config import nft_collection_address, storage_wallet_address
from ..db.database import Database
from random import randint

# fastapi setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://127.0.0.1",
        "http://localhost",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["get", "post"],
    allow_headers=["*"],
)

# variables
database = Database()


# get nfts (wallet_address) -> [ nft ]
@app.get("/get_nfts")
def get_nfts(wallet_address: str):
    mapping = get_user_onchain_nfts(wallet_address)
    return mapping


# lend nft (user_id, nft_address) -> transaction_deep_link
@app.post("/lend_nft")
def lend_nft(req: dict = Body()):
    user_id, nft_address = req["user_id"], req["nft_address"]

    # TODO: tonkeeper bug, deeplink not working
    current_timestamp = int(time.time())
    transfer_body = {
        "version": "0",
        "body": {
            "type": "nft-transfer",
            "expires_sec": current_timestamp + 60,  # expires after 60 seconds
            "params": {
                "newOwnerAddress": storage_wallet_address,
                "nftItemAddress": nft_address,
                "text": str(user_id),
                "amount": 1_000_000_000,
                "forwardAmount": 1_000_000_000,
            },
        },
    }

    transfer_body_str = json.dumps(transfer_body)
    b64_transfer_body_str = base64.encodebytes(transfer_body_str.encode())

    return (
        "https://app.tonkeeper.com/v1/txrequest-inline/"
        + b64_transfer_body_str.decode()
    )


# get user lending nfts (user_id) -> [ nft ]
@app.get("/get_user_lending_nfts")
def get_user_lending_nfts(user_id: int):
    mapping = database.get_not_returned_nfts_by_user_id(user_id)
    return mapping


# check nft status (nft_id) -> {...details}
@app.get("/check_nft_status")
def check_nft_status(nft_id: int):
    details = database.get_nft_by_nft_id(nft_id)
    return details


# borrow nft (user_id, nft_id) -> transaction_deep_link or None
@app.post("/borrow_nft")
def borrow_nft(req: dict = Body()):
    user_id = req["user_id"]

    # check if any nft is available
    nft = database.get_nfts_by_status("available")
    if len(nft) == 0:
        return {"url": ""}

    # get send transaction link
    values = database.get_last_configs()
    amount = values.borrow_cost_per_second * values.borrow_duration_in_second
    return {
        "url": f"ton://transfer/{storage_wallet_address}?amount={amount}&text=borrow:{user_id}"
    }


# get user borrowing nfts (user_id) -> [ nft ]
@app.get("/get_user_borrowing_nfts")
def get_user_borrowing_nfts(user_id: int):
    values = database.get_last_configs()
    duration = values.borrow_duration_in_second

    mapping = database.get_history_by_user_id_and_time_range(
        user_id, int(time.time() - duration), int(time.time())
    )
    return mapping


# take back nft (user_id, nft_id) -> None
@app.post("/take_back_nft")
def take_back_nft(req: dict = Body()):
    user_id, nft_id = req["user_id"], req["nft_id"]

    # check if nft is borrowed
    nft = database.get_nft_by_nft_id(nft_id)
    if not nft or nft.status == "borrowed" or str(nft.owner_id) != str(user_id):
        return {"url": ""}

    # get send transaction link
    values = database.get_last_configs()
    amount = values.takeback_fee_per_request
    return {
        "url": f"ton://transfer/{storage_wallet_address}?amount={amount}&text=takeback:{user_id}:{nft_id}"
    }


# For TG Bot
@app.get("/lent_nfts")
def lent_nfts(user_id: int):
    nfts = database.get_not_returned_nfts_by_user_id(user_id)
    return nfts


@app.get("/borrowed_nfts")
def borrowed_nfts(user_id: int):
    values = database.get_last_configs()
    histories = database.get_history_by_user_id_and_time_range(
        user_id, int(time.time()) - values.borrow_duration_in_second, int(time.time())
    )
    nfts = []
    for history in histories:
        nfts.append(database.get_nft_by_nft_id(history.nft_id))
    return nfts


@app.get("/configs")
def get_configs():
    values = database.get_last_configs()
    return values


@app.get("/own_nfts")
def own_nfts(user_address: str):
    nfts = get_user_onchain_nfts(user_address)
    return nfts


@app.get("/storage_wallet_address")
def get_storage_wallet_address():
    return {"address": storage_wallet_address}


@app.get("/nft")
def get_nft(nft_id: int):
    nft = database.get_nft_by_nft_id(nft_id)
    return nft


@app.get("/orders")
def get_orders(nft_id: int):
    orders = database.get_histories_by_nft_id(nft_id)
    return orders


# TAP specified
@app.get("/number_login_code")
def number_login_code(user_id: str, number_id: str):
    number_id = int(number_id)
    user_id = int(user_id)

    vals = database.get_last_configs()
    nft = database.get_nft_by_nft_id(number_id)

    if not nft:
        print("nft not found")
        return {"code": "-3"}
    elif nft.status != "borrowed":
        print("nft not borrowed")
        return {"code": "-3"}

    history = database.get_latest_history_by_nft_id(number_id)
    if not history:
        print("history not found")
        return {"code": "-3"}
    elif history.borrower_id != int(user_id):
        print("user not match")
        return {"code": "-3"}
    elif history.occurred_at + vals.borrow_duration_in_second < int(time.time()):
        print("nft expired")
        return {"code": "-3"}

    # TODO: implement with Fragment on Production
    return {"code": "".join([f"{randint(0, 9)}" for _ in range(6)])}
