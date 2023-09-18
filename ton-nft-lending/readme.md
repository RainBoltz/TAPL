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

- remember to provide the **TAPL_ENV** variable when running the scripts (if not given, the default will be `TAPL_ENV=test`)
- `.[TAPL_ENV].env` file (ref `.env.sample`)

  - **STORAGE_WALLET_MNEMONICS**: mnemonics of storage wallet, words separated by space
  - **STORAGE_WALLET_ADDRESS**: address of storage wallet, both raw and base64 form are acceptable
  - **NFT_COLLECTION_ADDRESS**: address of NFT collection, both raw and base64 form are acceptable
  - **TONCENTER_API_KEY**: API key of TONCenter, please contact [@tonapibot](https://t.me/tonapibot), tutorial: https://toncenter.com/bot (remember to comfirm that you are on testnet or mainnet)
  - **TONCENTER_API_URL**: _https://testnet.toncenter.com/api/v2/_ for testnet and _https://toncenter.com/api/v2/_ for mainnet
  - **TONAPI_API_KEY**: API key of TONAPI, please go to [tonconsole](https://tonconsole.com/dashboard) (remember to comfirm that you are on testnet or mainnet)
  - **TONAPI_API_URL**: _https://testnet.tonapi.io/v2_ for testnet and _https://tonapi.io/v2_ for mainnet

- `src/db/schema.sql`: check if the values in table **_configs_** are desired

- `src/api/main.py`: function `number_login_code` is the utility function to interact with [fragment.com](https://fragment.com) and get the login code for a given phone-number, note that ***currently it is mocked with a random 6-digit number***. (the production version **WILL NOT REVEAL IN PUBLIC** recently due to the further business concerns, contact [@rainboltz](https://t.me/rainboltz) for more collaboration details)

## Usage

### start tonapi SSE client

This is the `On-Off-Chain Synchronize Service` in the architecture diagram.

> It will listen to the events of the storage wallet and update the database accordingly.

```bash
$ cd ton-nft-lending
$ python3 -m src.runners.sse
```

### start web API service

This is the `API Service` in the architecture diagram.

> It will provide the main business logics and the web API for the Telegram Bot to interact with.

```bash
$ cd ton-nft-lending
$ python3 -m uvicorn src.api.main:app
```

### start db cronjob

This is the `cronjob` in the architecture diagram.

> It will check the database periodically and do some cleanups and update the status for expired borrowings.

```bash
$ cd ton-nft-lending
$ python3 -m src.runners.cronjob
```
