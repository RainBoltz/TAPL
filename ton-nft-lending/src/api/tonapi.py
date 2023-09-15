import requests
from ..common.config import *
from ..common.utils import to_public_key_address


def get_user_onchain_nfts(user_address):
    req_url = f"{tonapi_api_url}/accounts/{user_address}/nfts?collection={nft_collection_address}&limit=1000&offset=0&indirect_ownership=false"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {tonapi_api_key}",
    }
    response = requests.get(req_url, headers=headers)

    if response.status_code == 200:
        return {
            f'{item["metadata"]["name"]}': {
                "address": to_public_key_address(item["address"]),
                "owner_address": to_public_key_address(item["owner"]["address"]),
            }
            for item in response.json()["nft_items"]
        }
    else:
        return {}


def get_event(tx_hash):
    req_url = f"{tonapi_api_url}/events/{tx_hash}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {tonapi_api_key}",
    }
    response = requests.get(req_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {}


def get_nft_info(nft_address):
    req_url = f"{tonapi_api_url}/nfts/{nft_address}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {tonapi_api_key}",
    }
    response = requests.get(req_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {}
