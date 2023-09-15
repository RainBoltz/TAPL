# NFT Lending Utils

## Overview

This is an abstraction of NFT Lending Utility and Workflow on TON blockchain.

## Prerequisites

### Installation

```bash
$ cd ton-nft-lending
$ pip3 install -r requirements.txt
```

### Setup Database

```bash
$ cd ton-nft-lending/src/db
$ sqlite3
sqlite> .open db.splite3
sqlite> .read schema.sql
sqlite> .exit
```

### Check Configuration

- variables in file `ton-nft-lending/src/common/config.py`
- table `configs` in database `db.splite3`

## Usage

### start tonapi SSE client

```bash
$ cd ton-nft-lending
$ python3 -m src.runners.sse
```

### start web API service

```bash
$ cd ton-nft-lending
$ python3 -m uvicorn src.api.main:app
```

### start db cronjob

```bash
$ cd ton-nft-lending
$ python3 -m src.runners.cronjob
```

## WIP
