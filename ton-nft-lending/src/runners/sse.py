import requests
import time
import json
import pprint
import collections
import sseclient
from threading import Thread
from ..common.config import *
from ..common.utils import to_public_key_address
from ..api.tonapi import get_event, get_nft_info
from ..db.database import Database
from ..transactions.TonClient import TonCenterTonClient


class TAPEventHandler:
    def __init__(self):
        self.database = Database()
        self.client = TonCenterTonClient()

    # handle new event
    def new_event(self, payload):
        # pprint.pprint(payload)
        if "in_progress" not in payload or payload["in_progress"] != False:
            return

        if "actions" in payload:
            for action in payload["actions"]:
                if action["type"] == "NftItemTransfer":
                    self.handle_nft_transfer(action)
                elif action["type"] == "TonTransfer":
                    self.handle_ton_transfer(action)

    # handle nft transfer
    def handle_nft_transfer(self, payload):
        status = payload["status"] if "status" in payload else None
        user_id = (
            payload["NftItemTransfer"]["comment"]
            if "comment" in payload["NftItemTransfer"]
            else None
        )
        nft_address = (
            payload["NftItemTransfer"]["nft"]
            if "nft" in payload["NftItemTransfer"]
            else None
        )
        recipient_address = (
            payload["NftItemTransfer"]["recipient"]["address"]
            if "recipient" in payload["NftItemTransfer"]
            else None
        )
        sender_address = (
            payload["NftItemTransfer"]["sender"]["address"]
            if "sender" in payload["NftItemTransfer"]
            else None
        )

        print(
            f"status: {status}, recipient_address: {recipient_address}, sender_address: {sender_address}, nft_address: {nft_address}, user_id: {user_id}, storage_wallet_address: {storage_wallet_address}"
        )

        if (
            status == "ok"
            and user_id
            and nft_address
            and recipient_address
            and sender_address
        ):
            if (
                recipient_address == storage_wallet_address
                and sender_address != storage_wallet_address
            ):
                # nft was sent to storage wallet, so this is a lend
                # add nft to database
                nft_info = get_nft_info(nft_address)
                # print(nft_info)
                nft_metadata = nft_info["metadata"] if "metadata" in nft_info else {}
                nft_name = (
                    nft_metadata["name"] if "name" in nft_metadata else nft_address
                )
                self.database.add_nft(nft_address, nft_name, user_id, sender_address)
            elif (
                recipient_address != storage_wallet_address
                and sender_address == storage_wallet_address
            ):
                # nft was sent from storage wallet, so this is a return (afterwards)
                pass
                # update nft status in database
                # self.database.update_nft_status_by_address_and_status(nft_address, "available", "returned")

    # handle ton transfer
    def handle_ton_transfer(self, payload):
        status = payload["status"] if "status" in payload else None
        amount = (
            payload["TonTransfer"]["amount"]
            if "amount" in payload["TonTransfer"]
            else None
        )
        message = (
            payload["TonTransfer"]["comment"]
            if "comment" in payload["TonTransfer"]
            else None
        )
        recipient_address = (
            payload["TonTransfer"]["recipient"]["address"]
            if "recipient" in payload["TonTransfer"]
            else None
        )
        sender_address = (
            payload["TonTransfer"]["sender"]["address"]
            if "sender" in payload["TonTransfer"]
            else None
        )

        print(
            f"status: {status}, amount: {amount}, message: {message}, recipient_address: {recipient_address}, sender_address: {sender_address}, storage_wallet_address: {storage_wallet_address}"
        )

        if (
            status == "ok"
            and message
            and amount
            and recipient_address
            and sender_address
        ):
            if (
                recipient_address == storage_wallet_address
                and sender_address != storage_wallet_address
            ):

                messages = message.split(":")
                if len(messages) < 2:
                    return  # invalid message

                command = messages[0]
                if command != "borrow" and command != "takeback":
                    return  # invalid command

                if command == "borrow":  # this is a borrow request
                    user_id = messages[1]
                    if not user_id:
                        return

                    # check if any nft is available
                    nfts = self.database.get_nfts_by_status("available")
                    if not nfts:
                        return  # no nfts available

                    nft = nfts[0]

                    # check amount of toncoins sent
                    values = self.database.get_last_configs()
                    tap_borrow_cost = (
                        values.borrow_cost_per_second * values.borrow_duration_in_second
                    )
                    if amount < tap_borrow_cost:
                        return  # not enough toncoins sent

                    # update nft status for nft in database
                    self.database.update_nft_status_by_address_and_status(
                        nft.address, "available", "borrowed"
                    )

                    # add history to database
                    self.database.add_history(user_id, sender_address, nft.id)

                elif command == "takeback":
                    print(messages)
                    if len(messages) != 3:
                        return

                    user_id, nft_id = messages[1], messages[2]
                    if not user_id or str(nft_id).isdigit() == False:
                        return

                    # check if nft is borrowed
                    nft = self.database.get_nft_by_nft_id(nft_id)
                    print(nft)
                    if (
                        not nft
                        or nft.status != "available"
                        or str(nft.owner_id) != str(user_id)
                    ):
                        return  # nft is borrowed or already returned or not owned by user

                    # check amount of toncoins sent
                    values = self.database.get_last_configs()
                    fee = values.takeback_fee_per_request
                    if amount < fee:
                        return  # not enough toncoins sent

                    # update nft status for nft in database
                    self.database.update_nft_status_by_nft_id(nft_id, "returned")

                    # send nft back to owner
                    self.client.transfer_nft(nft.owner_address, nft.address)

                    # calculate profit
                    histories = self.database.get_histories_by_nft_id(nft_id)

                    # send profit to owner
                    if histories:
                        profit = len(histories) * (
                            values.lend_income_per_second
                            * values.borrow_duration_in_second
                        )
                        print(f"got {len(histories)} histories, profit: {profit}")

                        def _tmp_func(client, addr, amount):
                            print(
                                f"*sleep 60 seconds for transfer {amount} TONs to {addr}*"
                            )
                            time.sleep(60)
                            client.transfer_ton(addr, amount)

                        Thread(
                            target=_tmp_func,
                            args=(
                                self.client,
                                nft.owner_address,
                                profit,
                            ),
                        ).start()


tapEventHandler = TAPEventHandler()

hashes = {"map": set(), "queue": collections.deque()}
hash_max_size = 1000
client = None
while True:
    try:
        print("TonAPI SSE connecting...", end="")
        url = f"{tonapi_api_url}/sse/accounts/transactions?accounts={storage_wallet_address}"
        headers = {
            "Accept": "text/event-stream",
            "Authorization": f"Bearer {tonapi_api_key}",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Content-Type": "text/event-stream",
        }
        stream_response = requests.get(url, headers=headers, stream=True)
        client = sseclient.SSEClient(stream_response)
        print("DONE!")
        for event in client.events():
            event_json = json.loads(event.data)
            # pprint.pprint(event_json)
            if "tx_hash" in event_json:
                tx_hash = event_json["tx_hash"]
                if tx_hash in hashes["map"]:
                    continue
                event_payload = get_event(event_json["tx_hash"])
                hashes["map"].add(tx_hash)
                hashes["queue"].append(tx_hash)

                tapEventHandler.new_event(event_payload)  # process events

            if len(hashes["queue"]) > hash_max_size:
                hashes["map"].remove(hashes["queue"].popleft())
    except Exception as e:
        # close connection
        if client:
            client.close()
        print(e)
        time.sleep(1)
