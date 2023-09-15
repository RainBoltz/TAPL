import json
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

ENVIRONMENT = "test" # or "prod" / "main"
load_dotenv(os.path.dirname(os.path.realpath(__file__)) + f"/.{ENVIRONMENT}.env")


# python telegram bot 13.x
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Updater,
    MessageHandler,
    Filters,
)

from api import APIInstance

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

api_instance = APIInstance()

telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")


def start(update, context):
    buttons = [
        [KeyboardButton("💰Lend and Earn"),
         KeyboardButton("🤝Borrow and Enjoy")],
        [KeyboardButton("📈Market Quotes"), KeyboardButton("😎My Account")],
    ]
    keyboard = ReplyKeyboardMarkup(buttons)

    if update.message:
        replier = update.message.reply_text
        replier(
            "📞Welcome to TAP! Use this bot to borrow TAP (Telegram Anonymous Phone-number)!🤖☎️\n\nTry /lend to earn or /borrow to borrow a number! 💰💰💰💰\n*remember go to /market to checkout the latest borrow fee💵 and valid borrow period⏱️*",
            reply_markup=keyboard,
        )
    elif update.callback_query:
        query = update.callback_query
        query.answer()
        replier = query.edit_message_text
        replier(
            "📞Welcome to TAP! Use this bot to borrow TAP (Telegram Anonymous Phone-number)!🤖☎️\n\nTry /lend to earn or /borrow to borrow a number! 💰💰💰💰\n*remember go to /market to checkout the latest borrow fee💵 and valid borrow period⏱️*",
        )


def freeMessageHandler(update, context):
    if update.message.text == "💰Lend and Earn":
        lend(update, context)
    elif update.message.text == "🤝Borrow and Enjoy":
        borrow(update, context)
    elif update.message.text == "📈Market Quotes":
        market(update, context)
    elif update.message.text == "😎My Account":
        my_account(update, context)
    else:
        pass


def my_account(update, context):
    user_id = update.message.chat_id
    lending_numbers = api_instance.get_all_lend_numbers(user_id)
    borrowing_numbers = api_instance.get_all_borrowed_numbers(user_id)
    vals = api_instance.get_market_quotes()

    total_earnings = 0
    for num in lending_numbers:
        number_id = num["id"]
        orders = api_instance.get_orders_by_number_id(number_id)
        total_earnings += (
            len(orders)
            * vals["lend_income_per_second"]
            * vals["borrow_duration_in_second"]
            / (10 ** 9)
        )

    keyboard = [
        [InlineKeyboardButton("📲 My Lending Numbers",
                              callback_data=f"MYLENDINGS")],
        [InlineKeyboardButton("🔎 Get Login Code", callback_data=f"LOGINCODE")],
        [return_key()],
    ]
    keyboard_menu = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        f"""Your Telegram UID: `{user_id}`\n
📲Total Lendings: {len(lending_numbers)} numbers
💸Total Borrowings: {len(borrowing_numbers)} numbers
🤑Expected Total Earnings: {total_earnings} TONs
""",
        parse_mode="Markdown",
        reply_markup=keyboard_menu,
    )


def market(update, context):
    vals = api_instance.get_market_quotes()

    keyboard_menu = InlineKeyboardMarkup([[return_key()]])

    update.message.reply_text(
        f"""
- Borrow cost per seconds: {vals['borrow_cost_per_second']/(10**9)} TONs
- Total borrow period: {vals['borrow_duration_in_second']} sec.
- Lending income per second: {vals['lend_income_per_second']/(10**9)} TONs
- Takeback fee per request: {vals['takeback_fee_per_request']/(10**9)} TONs
""",
        reply_markup=keyboard_menu,
        parse_mode="Markdown",
    )


def lend(update, context):
    messenger = update.message
    replier = None
    if not messenger:
        query = update.callback_query
        query.answer()
        messenger = query.message
        replier = query.edit_message_text
    else:
        replier = messenger.reply_text

    user_id = messenger.chat_id

    # # get the user's number
    # numbers = api_instance.get_all_own_numbers(user_id)
    # if len(numbers) == 0:
    #     replier("You don't own any number!")
    #     return

    # keyboard = [
    #     [
    #         InlineKeyboardButton(
    #             f"{num}", callback_data=f"LEND::{numbers[num]['address']}"
    #         )
    #     ]
    #     for num in numbers
    # ] + [[return_key()]]
    # keyboard_menu = InlineKeyboardMarkup(keyboard)

    # replier(
    #     "choose a following number to lend",
    #     reply_markup=keyboard_menu,
    #     parse_mode="Markdown",
    # )

    storage_wallet_address = api_instance.get_storage_wallet_address()

    keyboard = [[return_key()]]
    keyboard_menu = InlineKeyboardMarkup(keyboard)

    replier(
        f"""
Start Lending Manually 🛠️ (Use Web Extension version TonKeeper instead of Mobile version)
- Transfer NFT: <Your Number NFT Address>
- Recipient (TAPL Centralized Smart Contract): `{storage_wallet_address}`
- Comment: `{user_id}`
* Please make sure you transfer the NFT with Comment! *
""",
        parse_mode="Markdown",
        reply_markup=keyboard_menu,
    )


def do_lend(update, context):
    print(update.callback_query.data)
    query = update.callback_query
    query.answer()
    number_address = query.data.split("::")[1]
    keyboard_menu = InlineKeyboardMarkup([[return_key()]])

    user_id = query.message.chat_id

    # success = api_instance.do_lend_number(user_id, number_address)
    # if success:
    #     query.edit_message_text(
    #         f"Successfully lend the number {number}🎉!",
    #         parse_mode="Markdown",
    #         reply_markup=keyboard_menu,
    #     )
    # else:
    #     query.edit_message_text(
    #         f"Failed to lend the number {number}!",
    #         parse_mode="Markdown",
    #         reply_markup=keyboard_menu,
    #     )

    storage_wallet_address = api_instance.get_storage_wallet_address()

    query.edit_message_text(
        f"""
Start Lending Manually 🛠️ (Use Web Extension version TonKeeper instead of Mobile version)
- Transfer NFT: `{number_address}`"
- Recipient (TAPL Centralized Smart Contract): `{storage_wallet_address}`
- Comment: `{user_id}`
* Please make sure you transfer the NFT with Comment! *
""",
        parse_mode="Markdown",
        reply_markup=keyboard_menu,
    )


def my_lendings(update, context):
    messenger = update.message
    replier = None
    if not messenger:
        query = update.callback_query
        query.answer()
        messenger = query.message
        replier = query.edit_message_text
    else:
        replier = messenger.reply_text

    user_id = messenger.chat_id

    numbers = api_instance.get_all_lend_numbers(user_id)
    if len(numbers) == 0:
        replier("You haven't lent any number yet!")
        return

    keyboard = [
        [
            InlineKeyboardButton(
                f"{num['name']}", callback_data=f"CHECKORDER::{num['id']}"
            )
        ]
        for num in numbers
    ] + [[return_key()]]
    keyboard_menu = InlineKeyboardMarkup(keyboard)

    replier(
        "choose a following number to check lending status",
        reply_markup=keyboard_menu,
        parse_mode="Markdown",
    )


def check_order(update, context):
    query = update.callback_query
    query.answer()
    number_id = query.data.split("::")[1]

    vals = api_instance.get_market_quotes()

    number_data = api_instance.get_number(number_id)
    if not number_data or number_data["status"] == "returned":
        print(f"error, TAPL smart contract does not own {number_data}")
        return

    orders = api_instance.get_orders_by_number_id(number_id)
    latest_order = orders[0] if len(orders) > 0 else None
    total_earnings = (
        len(orders)
        * vals["lend_income_per_second"]
        * vals["borrow_duration_in_second"]
        / (10 ** 9)
    )

    if number_data["status"] == "borrowed":
        start_at = datetime.fromtimestamp(latest_order["occurred_at"])
        end_at = datetime.fromtimestamp(
            latest_order["occurred_at"] + vals["borrow_duration_in_second"]
        )
        query.edit_message_text(
            f"""
Number: `{number_data['name']}`\n
- Status: `borrowed`
- Borrowed at: `{start_at}`
- Borrowed until: `{end_at}`
- Expected total earnings: {total_earnings} TONs
""",
            parse_mode="Markdown",
        )
    elif number_data["status"] == "available":
        keyboard = [
            [
                InlineKeyboardButton(
                    f"♻️ Withdraw Number", callback_data=f"TAKEBACK::{number_id}"
                )
            ],
            [return_key()],
        ]
        keyboard_menu = InlineKeyboardMarkup(keyboard)
        created_at = datetime.fromtimestamp(number_data["received_at"])
        query.edit_message_text(
            f"""
Number: `{number_data['name']}`\n
- Status: `available`
- Start Lending at: `{created_at}`
- Expected total earnings: {total_earnings} TONs
""",
            parse_mode="Markdown",
            reply_markup=keyboard_menu,
        )

    else:
        print(f"unknown error: {number_data} and latest order {latest_order}")
        return


def get_code(update, context):
    messenger = update.message
    replier = None
    if not messenger:
        query = update.callback_query
        query.answer()
        messenger = query.message
        replier = query.edit_message_text
    else:
        replier = messenger.reply_text

    user_id = messenger.chat_id

    numbers = api_instance.get_all_borrowed_numbers(user_id)

    if len(numbers) == 0:
        replier("You haven't borrow any number yet!")
        return

    keyboard = [
        [InlineKeyboardButton(
            f"{num['name']}", callback_data=f"GETCODE::{num['id']}")]
        for num in numbers
    ] + [[return_key()]]
    keyboard_menu = InlineKeyboardMarkup(keyboard)

    replier(
        "choose a following number to get the login code",
        reply_markup=keyboard_menu,
        parse_mode="Markdown",
    )


def get_code_from_fragment(update, context):
    query = update.callback_query
    query.answer()
    number_id = query.data.split("::")[1]
    user_id = query.message.chat_id

    code = api_instance.get_number_login_code(user_id, number_id)

    keyboard_menu = InlineKeyboardMarkup([[return_key()]])

    if code == "-1":
        print(f"didn't buy the number@id={number_id}")
        query.edit_message_text(
            "Well, You actually don't own this number :(",
            reply_markup=keyboard_menu,
            parse_mode="Markdown",
        )
    elif code == "-2":
        print(f"haven't login with the number@id={number_id}")
        query.edit_message_text(
            "Please login with the number first to generate the login code!",
            reply_markup=keyboard_menu,
            parse_mode="Markdown",
        )
    elif code == "-3":
        print(f"invalid number@id={number_id}")
        query.edit_message_text(
            "Well, You actually don't own this number :(",
            reply_markup=keyboard_menu,
            parse_mode="Markdown",
        )
    elif code == "0":
        print(f"internal error (maybe api service is down)")
        query.edit_message_text(
            "Internal error, Please try again later!",
            reply_markup=keyboard_menu,
            parse_mode="Markdown",
        )
    else:
        query.edit_message_text(
            f"Here is your code: `{code}`",
            parse_mode="Markdown",
            reply_markup=keyboard_menu,
        )


def borrow(update, context):
    user_id = update.message.chat_id
    vals = api_instance.get_market_quotes()
    storage_wallet_address = api_instance.get_storage_wallet_address()
    cost = vals["borrow_cost_per_second"] * vals["borrow_duration_in_second"]

    payment_url = api_instance.get_borrow_payment_url(user_id)
    if not payment_url:
        update.message.reply_text(
            "💔 Sorry, Numbers are out of stock! 😭😭😭\n Please check again later 😢"
        )
        return

    tonkeeper_deeplink_button = InlineKeyboardButton(
        "💎 Payment Link",
        url=payment_url,
    )
    keyboard_menu = InlineKeyboardMarkup(
        [[tonkeeper_deeplink_button], [return_key()]])

    update.message.reply_text(
        f"""
Borrow a Number Manually 🛠️
- Transfer TON amount: `{cost/(10**9)}`
- Recipient (TAPL Centralized Smart Contract): `{storage_wallet_address}`
- Comment: `borrow:{user_id}`
* Please make sure you transfer the TONs with Comment! *
""",
        reply_markup=keyboard_menu,
        parse_mode="Markdown",
    )


def do_take_back(update, context):
    # print("do take back")
    query = update.callback_query
    query.answer()
    number_id = query.data.split("::")[1]

    user_id = query.message.chat_id

    vals = api_instance.get_market_quotes()
    storage_wallet_address = api_instance.get_storage_wallet_address()
    cost = vals["takeback_fee_per_request"]

    payment_url = api_instance.get_takeback_payment_url(user_id, number_id)
    if not payment_url:
        query.edit_message_text("Internal error, Please try again later!")
        return

    tonkeeper_deeplink_button = InlineKeyboardButton(
        "💎 Payment Link",
        url=payment_url,
    )
    keyboard_menu = InlineKeyboardMarkup(
        [[tonkeeper_deeplink_button], [return_key()]])

    query.edit_message_text(
        f"""
Take back a Number Manually 🛠️
- Transfer TON amount: `{cost/(10**9)}`
- Recipient (TAPL Centralized Smart Contract): `{storage_wallet_address}`
- Comment: `takeback:{user_id}:{number_id}`
* Please make sure you transfer the TONs with Comment! *
""",
        reply_markup=keyboard_menu,
        parse_mode="Markdown",
    )


def return_key():
    keyboard = InlineKeyboardButton("🔙 Back to Menu", callback_data=f"START")
    return keyboard


updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(start, pattern="START"))
dispatcher.add_handler(CommandHandler("myaccount", my_account))
dispatcher.add_handler(CommandHandler("help", start))
dispatcher.add_handler(CommandHandler("market", market))
dispatcher.add_handler(CommandHandler("lend", lend))
dispatcher.add_handler(CallbackQueryHandler(lend, pattern="LENDS"))
dispatcher.add_handler(CallbackQueryHandler(do_lend, pattern="^LEND::[.]+$"))
dispatcher.add_handler(CommandHandler("mylendings", my_lendings))
dispatcher.add_handler(CallbackQueryHandler(my_lendings, pattern="MYLENDINGS"))
dispatcher.add_handler(
    CallbackQueryHandler(check_order, pattern="^CHECKORDER::[0-9]+$")
)
dispatcher.add_handler(CallbackQueryHandler(
    do_take_back, pattern="^TAKEBACK::[0-9]+$"))
dispatcher.add_handler(CommandHandler("getcode", get_code))
dispatcher.add_handler(
    CallbackQueryHandler(get_code, pattern="LOGINCODE")
)
dispatcher.add_handler(
    CallbackQueryHandler(get_code_from_fragment, pattern="^GETCODE::[0-9]+$")
)
dispatcher.add_handler(CommandHandler("borrow", borrow))

dispatcher.add_handler(MessageHandler(Filters.text, freeMessageHandler))

updater.start_polling()
updater.idle()
