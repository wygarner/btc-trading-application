from django.shortcuts import render
from django.contrib import messages

# from background_task import background

from .models import Bot
from .forms import BotForm

import pandas as pd
import time
import bitmex
import sqlite3
from joblib import load
import bravado

api_key = "replace me"
api_secret = "replace me"

client = bitmex.bitmex(test=True, api_key=api_key, api_secret=api_secret)

conn = sqlite3.connect("btc.db")
c = conn.cursor()

model = load("BTC_100m_forecast.joblib")


def get_midprice(client):
    result = client.Instrument.Instrument_get(symbol="XBTUSD",
                                              reverse=True, count=1).result()
    midprice = result[0][0]["midPrice"]
    return midprice


def place_limit_order(client, quantity, price):
    client.Order.Order_new(symbol="XBTUSD",
                            orderQty=quantity, price=price).result()


def place_stop_loss(client, quantity, price):
    client.Order.Order_new(symbol="XBTUSD",
                            ordType="StopLimit", orderQty=quantity,
                            stopPx=price, price=price).result()


def place_take_profit(client, quantity, price):
    client.Order.Order_new(symbol="XBTUSD",
                            ordType="LimitIfTouched", orderQty=quantity,
                            stopPx=price, price=price).result()


def update_leverage(client, leverage):
    client.Position.Position_updateLeverage(symbol="XBTUSD",
                                            leverage=leverage).result()


def get_position(client):
    return client.Position.Position_get().result()

def get_balance(client):
    
    margin = client.User.User_getMargin(currency="XBt").result()
    balance = round(margin[0]['walletBalance'] * .00000001,6)
    
    return balance

def place_orders(client, direction, risk, reward):
    client.Order.Order_cancelAll().result()
    current_price = get_midprice(client)
    balance = get_balance(client)
    if direction == 1:
        position_size = int((current_price + (current_price*0.0025)) * balance) -2
        place_limit_order(client, position_size, round((current_price + (current_price*0.0025)),0))
        place_stop_loss(client, -position_size, round((current_price - (current_price*risk)),0))
        place_take_profit(client, -position_size, round((current_price + (current_price*0.02)),0))
    else:
        position_size = int((current_price - (current_price*0.0025)) * balance) -2
        place_limit_order(client, -position_size, round((current_price - (current_price*0.0025)),0))
        place_stop_loss(client, position_size, round((current_price + (current_price*reward)),0))
        place_take_profit(client, -position_size, round((current_price - (current_price*0.02)),0))

# @background(schedule=1)
def run_bot(key, secret, confidence, risk, reward):
    # api_key = "-iXO_17idCPYYQgGsRtB7HfI"
    # api_secret = "yod97ok0bHhrdumSb4XnF0KDAg1LH0QciHkVyHb3sF0z0Y8J"
    
    client = bitmex.bitmex(test=True, api_key=api_key, api_secret=api_secret)
    
    conn = sqlite3.connect("btc.db")

    model = load("BTC_100m_forecast.joblib")
    
    while True:
        try:
            position= get_position(client)
        except(bravado.exception.HTTPServiceUnavailable):
            time.sleep(5)
            position= get_position(client)
            
        data = pd.read_sql_query(
            "SELECT * FROM book_imbalances_lag_10 ORDER BY time DESC LIMIT 501 ",
            conn,)[::-1].reset_index(drop=True
                                      ).drop(columns=["index", "lag period"])
    
        # Transform dataframe
        transformed = data.copy()
        history = 500
        
        shifts = [x for x in list(range(1, history + 1))]
        for shift in shifts:
            transformed["t-oir-" + str(shift)] = transformed["oir"].shift(shift)
            transformed["t-voi-" + str(shift)] = transformed["voi"].shift(shift)
            transformed["t-tfi-" + str(shift)] = transformed["tfi"].shift(shift)
            transformed["t-midprice-" + str(shift)] = transformed["midprice"].shift(shift)
        
        transformed = transformed.dropna()
        transformed = transformed.set_index("time").drop(
            ["midprice", "oir", "voi", "tfi"], axis=1
        )
    
        prediction = model.predict(transformed)[0]
        probs = model.predict_proba(transformed)[0][prediction]
    
        try:    
            if position[0][0]['isOpen']==False:
                if probs>= confidence:
                    place_orders(client,prediction, risk, reward)
            
            print("Entry:",position[0][0]['avgEntryPrice'])
            print("Unrealised PnL %:",position[0][0]['unrealisedPnlPcnt'])
            print("`^*^`"*8,"\n")
            time.sleep(5)
        
        except(IndexError):
            print("Position Error","\n")
            time.sleep(5)
        
        

def bot_view(request, *args, **kwargs):
    form = BotForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Success")
    
    my_context = {"form": form
                  }
    
    return render(request, "pages/bot.html", my_context)


def run_bot_view(request, *args, **kwargs):
    obj = Bot.objects.order_by('-id')[0]
    
    run_bot(obj.key, obj.secret, int(obj.confidence), int(obj.risk), int(obj.reward))
    
    form = BotForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Success")
    
    my_context = {"form": form
                  }
    
    return render(request, "pages/run_bot.html", my_context)
