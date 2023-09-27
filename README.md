# README

# Chariot

Chariot is a Discord Bot written in python; made with discord.py.

You can check explanation of updates on [My Tistory Blog](https://u-bvm.tistory.com/) maybe? (Korean)

## Prerequisite

- Python 3.10 or higher

## Install

Simply clone this repository, install requirments follow requirements.txt and get API Keys for some features.
Finally you can run `chariot.py`. That’s it!

## Commands

### /kd

Translate Korean to Weird Korean using multiple translations.

### /line

Create a Line. Line means Draw.

1. When command entered, bot will create a thread on your channel and post a embed with button view.
2. There is 2 Buttons; “Entry” and “Print etnry list”
3. Others can entry to Line with just click Entry button.
4. If deadline reached, bot will remove buttons and edit embed that contain winner.

### /exchange

Get exchange rate from https://github.com/fawazahmed0/currency-api.

### /ratetable

Show exchange rate infos in form of embed. 

### /tk

It use `/exchange` internally to get exchange rate to KRW from TWD.

### /cvtime

Convert Datetime to UNIX Timestamp.

### /cvstamp

Convert UNIX Timestamp to Datetime.

### /convertimp

Convert imperial to metric.

### /deepl

Translate words with DeepL translator.

### /maintinfo

Get maintenance info from FFXIV Lodestone.

## Links

**[discord.py](https://github.com/Rapptz/discord.py)**
