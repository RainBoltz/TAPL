# TAPL Telegram Bot

## Overview

The Telegram Bot service of TAPL. This is currently the only interface to interact with TAPL.

## Prerequisites

- Python 3.8+ with pip
- Telegram Bot Token (please contact [@BotFather](https://t.me/BotFather), tutorial: https://core.telegram.org/bots#6-botfather)

### install dependencies

```bash
$ cd tapl-bot
$ pip3 install -r requirements.txt
```

### check configurations

- `main.py`: rename variable **ENVIRONMENT** based on your environment, which will read the corresponding `.[ENVIRONMENT].env` file
- `.[ENVIRONMENT].env` file (ref `.env.sample`)
  - **TELEGRAM_BOT_TOKEN**: Telegram Bot Token

## Usage

### start Telegram bot

This is the `Telegram Bot` in the architecture diagram.

It will provide the frontend interface on Telegram for users to interact with.

```bash
$ cd tapl-bot
$ python3 main.py
```
