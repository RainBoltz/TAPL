# NFT Lending Utils

## Overview

This is an abstraction of NFT Lending Utility and Workflow on TON blockchain.

## Prerequisites

- Python 3.8+ with pip
- sqlite3

### install dependencies

```bash
$ cd ton-nft-lending
$ pip3 install -r requirements.txt
```

### setup database

```bash
$ cd ton-nft-lending/src/db
$ sqlite3
sqlite> .open db.splite3
sqlite> .read schema.sql
sqlite> .exit
```

### check configurations

- `src/common/config.py`: rename variable **ENVIRONMENT** based on your environment, which will read the corresponding `.[ENVIRONMENT].env` file
- `.[ENVIRONMENT].env` file (ref `.env.sample`)

  - **STORAGE_WALLET_MNEMONICS**: mnemonics of storage wallet, words separated by space
  - **STORAGE_WALLET_ADDRESS**: address of storage wallet, both raw and base64 form are acceptable
  - **NFT_COLLECTION_ADDRESS**: address of NFT collection, both raw and base64 form are acceptable
  - **TONCENTER_API_KEY**: API key of TONCenter, please contact [@tonapibot](https://t.me/tonapibot), tutorial: https://toncenter.com/bot (remember to comfirm that you are on testnet or mainnet)
  - **TONCENTER_API_URL**: _"https://testnet.toncenter.com/api/v2/"_ for testnet and _"https://toncenter.com/api/v2/"_ for mainnet
  - **TONAPI_API_KEY**: API key of TONAPI, please go to [tonconsole](https://tonconsole.com/dashboard) (remember to comfirm that you are on testnet or mainnet)
  - **TONAPI_API_URL**: _"https://testnet.tonapi.io/v2"_ for testnet and _"https://tonapi.io/v2"_ for mainnet

- `src/db/schema.sql`: check if the values in table **_configs_** are desired

## Usage

### start tonapi SSE client

This is the `On-Off-Chain Synchronize Service` in the architecture diagram.

It will listen to the events of the storage wallet and update the database accordingly.

```bash
$ cd ton-nft-lending
$ python3 -m src.runners.sse
```

### start web API service

This is the `API Service` in the architecture diagram.

It will provide the main business logics and the web API for the Telegram Bot to interact with.

```bash
$ cd ton-nft-lending
$ python3 -m uvicorn src.api.main:app
```

### start db cronjob

This is the `cronjob` in the architecture diagram.

It will check the database periodically and do some cleanups and update the status for expired borrowings. 

```bash
$ cd ton-nft-lending
$ python3 -m src.runners.cronjob
```
