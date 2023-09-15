# TAPL Official Documentation
This is the official documentation for project **TAPL** (**T**elegram **A**nonymous **P**hone-number **L**ending).
> OPENSOURCE CODE: don't Trust, Verify.
>
> PLATFORM/SERVICE: well, you have no choice ¯\\\_(ツ)\_/¯

## Introduction
TAPL is a platform that allows you to lend your [Telegram Anonymous Phone-number](https://telegram.org/blog/ultimate-privacy-topics-2-0) (or some called "Anonymous Telegram Phone-number") to other people easily. The platform is based on the [Telegram](https://telegram.org/) messaging app and is represented by a [Telegram Bot](https://core.telegram.org/bots).

### Why do I need TAPL?
A TAP is a kind of [Non-Fungible Token](https://en.wikipedia.org/wiki/Non-fungible_token) (NFT) with special utilities: it's not only a token, it's a phone-number that you can use to register on Telegram.

#### from lender's perspective...
Imagine that you have one or a bunch of anonymous phone-numbers that you are not using it at all. TAPs are just NFTs, they don't get a job and make money themselves, and we don't get any interest or benefit by locking them in our wallet. So why not lend them to other people and make some money?

1. We own some TAPs, but we are not using every of them.
2. We don't get any interest or benefit by locking them in our wallet.
3. We can lend them to other people and make some money.
4. For safety, we don't have to actually send the TAP to the borrower, we can just lend them the right to use the TAP. (e.i. give the borrower permission to access to the TAP login code)

#### from borrower's perspective...
Imagine you are a Telegram user who temporarily wants to register a new Telegram account and stay anonymous. You can buy a TAP from the market, but it may be too expensive. Why not just borrow one from other people?

1. We need a Telegram Anonymous Phone-number to register on Telegram.
2. Currently TAP is somehow too expensive that we can't afford it.
3. It may be a cheaper choice if We can borrow TAPs from other people and use them to register on Telegram instead of buying them.

## How does it work?

### 1. Lender
1. Get an lending instructions from TAPL Bot.
2. Lend the TAP out by following the instructions.
3. Wait for the TAP to be borrowed. Check the TAP status any time on TAPL Bot.
4. Get an takeback instruction from TAPL Bot.
5. Withdraw the TAP by following the instructions. (only if the TAP is not borrowed)

### 2. Borrower
1. Get a borrowing instructions from TAPL Bot.
2. Borrow the TAP by following the instructions.
3. You temporarily owns the TAP until the lending period expires. Check the TAP status any time on TAPL Bot. You can get the corresponding Login Code though TAPL Bot.

## TAPL System Architecture
![TAPL System Architecture](
https://raw.githubusercontent.com/RainBoltz/TAPL/main/docs/tapl-system-architecture.png)

