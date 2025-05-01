# Codeforces / AtCoder Contest bot on Telegram
#### Made By Skyzhou
#### Better view on my blog [CF/At Notification bot on Telegram](https://skyzhou.top/2025/05/01/CFAt_Tg_Bot/)
---

## Introduction

A simple CF/At contest notification on every 8:00a.m. (UTC+8) if the day has a CF/At contest based on Telegram Bot.

## How to use?

First, you need to have a **server(not in China Mainland)** to deploy the Telegram Bot backend.

Then, search **@BotFather** on Telegram and create a bot by following his instructions.

After successfully created a Telegram Bot, you have to create a ```config.json``` like below, to put your **```TOKEN```** in it. Or you can just copy the ```config_empty.json``` file and rename it to ```config.json```.

```json
{
    "TOKEN": "YOUR TOKEN HERE",
    "CHAT_ID": 1145141919810
}
```

To test whether the Bot has been created correctly and get the CHAT_ID of the messsage room where you want to use later. You can run the code ```getChatId.py``` first, and ```/start``` in Telegram. You will now get your **```CHAT_ID```**, it should be put correctly in the ```config.json```, too.

The last step is to run ```main.py``` and wait for the alarm on every 8:00a.m. (UTC+8) if the day has a CF/At contest. 😋

P.S. Remember to use the **venv** by ```requirements.txt```

--- 

Warning: If you're in China Mainland

It's amazing that Apple and most of the Android system has put the notificaiton API on Chinese Server, that means you don't have to use VPN tools to receive such a notification by Telegram when using iPhone in China Mainland!

But unfortunately, if you're a Huawei user, I'm sorry to tell that the notification is **not** available in China Mainland without using VPN tools.

## Test Images

![TestingImage](https://img.skyzhou.top/i/2025/05/01/6812f452578ff.jpg)