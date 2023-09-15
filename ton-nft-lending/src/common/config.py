from .utils import to_public_key_address

import os
from dotenv import load_dotenv

load_dotenv(os.path.dirname(os.path.realpath(__file__)) + "/.test.env") # or .main.env

tonapi_api_key = os.getenv("TONAPI_API_KEY")
tonapi_api_url = os.getenv("TONAPI_API_URL")

nft_collection_address = to_public_key_address(os.getenv("NFT_COLLECTION_ADDRESS"))

storage_wallet_address = to_public_key_address(os.getenv("STORAGE_WALLET_ADDRESS"))

toncenter_api_key = os.getenv("TONCENTER_API_KEY")
toncenter_api_url = os.getenv("TONCENTER_API_URL")

storage_wallet_mnemonics = os.getenv("STORAGE_WALLET_MNEMONICS")
