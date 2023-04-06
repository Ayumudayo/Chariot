# KORD

KORD is a Discord Bot written in python; made with discord.py.

## Prerequisite

---

- Python 3.10 or higher
- .NET 4.* or higher (If you want to use with dll.)

## Install

---

Simply clone this repository, install requirments follow requirements.txt and run `kordBotPy.py` . And that’s it!

## Commands

---

### /kd

Translate Korean to Weird Korean using multiple translations.

### /kdnorn

It just work same with `/kd` but without non-random-blank.

### /line

Create a Line. Line means Draw.

1. When command entered, bot will create a thread on your channel and post a embed with button view.
2. There is 2 Buttons; “Entry” and “Print etnry list”
3. Others can entry to Line with just click Entry button.
4. If deadline reached, bot will remove buttons and edit embed that contain winner.

### **/exchange**

Get exchange rate from https://github.com/fawazahmed0/currency-api

### **/tk**

It use `/exchange` internally to get exchange rate to KRW from TWD

### **/cvtime**

Convert Datetime to UNIX Timestamp.

### /cvstamp

Convert UNIX Timestamp to Datetime

## Links

---

**[discord.py](https://github.com/Rapptz/discord.py)**