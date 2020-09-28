from django.shortcuts import render
from django.contrib import messages

from .models import Strategy
from .forms import StrategyForm

import pandas as pd
import numpy as np

import plotly.express as px

import sqlite3

from joblib import load


model = load("BTC_100m_forecast.joblib")

def get_data():
    # Connect to DB
    conn = sqlite3.connect("btc.db")
    # c = conn.cursor()
    
    data = pd.read_sql_query("SELECT * FROM book_imbalances_lag_10", conn)
    data = data.drop(columns=["index"])
    data["time"] = pd.to_datetime(data["time"])
    data = data.set_index("time", drop=False)
    data = data.tz_localize(tz="US/Eastern")
    
    return data
    

def get_test_data():

    test_data = pd.read_csv("test_data_predictions.csv")
    
    # print(test_data)
    
    return test_data


class MarketSim:
    def __init__(self, data, test_data, confidence, risk, reward, position_size, balance):
        self.data = data
        self.test_data = test_data
        self.confidence = float(confidence)
        self.risk = float(risk)
        self.reward = float(reward)
        self.position_size = int(position_size)
        self.balance = int(balance)
        self.starting_balance = int(balance)
        self.get_predictions()

    def get_predictions(self):
        confidence_df = self.test_data[
            (self.test_data["probs 0"] > self.confidence)
            | (self.test_data["probs 1"] > self.confidence)
        ]
        confidence_df["success"] = "no"
        confidence_df.loc[
            confidence_df["prediction"] == confidence_df["target"], "success"
        ] = "yes"

        live_test = confidence_df[
            ["trade time", "t-midprice-501", "midprice", "prediction", "success"]
        ]
        live_test = live_test.rename(
            columns={"trade time": "time", "midprice": "future midprice"}
        )
        
        live_test = live_test.dropna()
        live_test["time"] = pd.to_datetime(live_test["time"])
        
        live_test = live_test.reset_index(drop=True)

        live_test = live_test.merge(
           self.data[["time", "midprice"]].reset_index(drop=True), on="time"
        )
        live_test = live_test.append(self.data[["time", "midprice"]].reset_index(drop=True))
        live_test = live_test.set_index("time")
        live_test = live_test.sort_index()

        self.test_data = live_test

    def test(self):
        position = ""
        trade_price = 0
        self.profit_list = []
        self.open_times = []
        self.close_times = []
        self.open_prices = []
        self.close_prices = []
        self.direction_list = []

        for index, row in self.test_data.iterrows():
            if row["prediction"] == 0 and position == "":
                position = "short"
                trade_price = row["t-midprice-501"]
                #                 + (row["t-midprice-501"] * 0.0001)
                self.open_times.append(index)
                self.open_prices.append(trade_price)
                self.direction_list.append(position)
            elif row["prediction"] == 1 and position == "":
                position = "long"
                trade_price = row["t-midprice-501"]
                #                 - (row["t-midprice-501"] * 0.0001)
                self.open_times.append(index)
                self.open_prices.append(trade_price)
                self.direction_list.append(position)
            if position == "short":
                if row["midprice"] <= trade_price - (trade_price * self.reward):
                    close_price = row["midprice"]
                    profit = (trade_price - close_price) * (
                        self.position_size / trade_price
                    )
                    profit += self.position_size * 0.00025
                    profit += self.position_size * 0.00025
                    profit = round(profit, 2)
                    self.profit_list.append(profit)
                    position = ""
                    self.close_times.append(index)
                    self.close_prices.append(row["midprice"])
                    self.balance += profit
                elif row["midprice"] >= trade_price + (trade_price * self.risk):
                    close_price = row["midprice"]
                    profit = (trade_price - close_price) * (
                        self.position_size / trade_price
                    )
                    profit += self.position_size * 0.00025
                    profit += self.position_size * -0.00075
                    profit = round(profit, 2)
                    self.profit_list.append(profit)
                    position = ""
                    self.close_times.append(index)
                    self.close_prices.append(row["midprice"])
                    self.balance += profit
            if position == "long":
                if row["midprice"] >= trade_price + (trade_price * self.reward):
                    close_price = row["midprice"]
                    profit = (
                        (trade_price - close_price)
                        * (self.position_size / trade_price)
                        * -1
                    )
                    profit += self.position_size * 0.00025
                    profit += self.position_size * -0.00075
                    profit = round(profit, 2)
                    self.profit_list.append(profit)
                    position = ""
                    self.close_times.append(index)
                    self.close_prices.append(row["midprice"])
                    self.balance += profit
                elif row["midprice"] <= trade_price - (trade_price * self.risk):
                    close_price = row["midprice"]
                    profit = (
                        (trade_price - close_price)
                        * (self.position_size / trade_price)
                        * -1
                    )
                    profit += self.position_size * 0.00025
                    profit += self.position_size * 0.00025
                    profit = round(profit, 2)
                    self.profit_list.append(profit)
                    position = ""
                    self.close_times.append(index)
                    self.close_prices.append(row["midprice"])
                    self.balance += profit

            self.position_size = self.balance

        self.equity_list = []
        for i in self.profit_list:
            self.equity_list.append(i + self.starting_balance)
            self.starting_balance = i + self.starting_balance

    def get_trades(self):
        trades_df = pd.DataFrame(self.open_times, columns=["open time"])
        trades_df["key"] = trades_df.index
        trades_df["open price"] = self.open_prices

        try:
            trades_df["close time"] = self.close_times
            trades_df["close price"] = self.close_prices
            trades_df["equity"] = self.equity_list
            trades_df["PnL"] = self.profit_list
        except (ValueError):
            self.close_times.append(np.nan)
            self.close_prices.append(np.nan)
            self.profit_list.append(np.nan)
            self.equity_list.append(np.nan)
            trades_df["close time"] = self.close_times
            trades_df["close price"] = self.close_prices
            trades_df["equity"] = self.equity_list
            trades_df["PnL"] = self.profit_list

        trades_df["position"] = self.direction_list

        trades_close = trades_df.drop(columns=["open time", "open price"])
        trades_open = trades_df.drop(columns=["close time", "close price"])
        trades_close["OC"] = "close"
        trades_open["OC"] = "open"

        trades_open = trades_open.rename(
            columns={"open time": "time", "open price": "price"}
        )
        trades_close = trades_close.rename(
            columns={"close time": "time", "close price": "price"}
        )

        trades_df = trades_open.append(trades_close)
        trades_df["key"] = trades_df["key"].astype(str)

        self.trades_df = trades_df
        
        opens = trades_df.loc[trades_df["OC"] == "open"]
        closes = trades_df.loc[trades_df["OC"] == "close"]
        
        trades_df = opens.merge(closes, on="key").rename(
            columns={'time_x': 'open time','time_y': 'close time', 
                     'price_x': 'open', 'equity_x': 'equity', 'PnL_x': 'PnL', 
                     'position_x': 'position', 'price_y': 'close'}).drop(
                         columns=['key','OC_x','equity_y','PnL_y',
                                  'position_y','OC_y'])
        trades_df = trades_df[['open time', 'close time', 'position', 'open', 
                               'close', 'PnL', 'equity']]

        return trades_df

    def display_trades(self):
        fig = px.scatter(
            self.trades_df,
            x="time",
            y="price",
            color="key",
            hover_data=["OC", "position", "PnL"],
        )
        
        return fig

    def display_equity(self):
        equity_df = self.trades_df.copy().drop_duplicates(subset=["key"])
        fig = px.line(equity_df, x="time", y="equity")
        
        return fig
    




def strat_create_view(request):
    form = StrategyForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Loading test data...")

    context = {
        "form": form,
        }
    return render(request, "strat/strat_create.html", context)


def strat_test_view(request):
    obj = Strategy.objects.order_by('-id')[0]
    
    form = StrategyForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Loading test data...")
    
    data = get_data()
    predictions = get_test_data()
    test = MarketSim(data, predictions, obj.confidence, obj.risk, obj.reward, 10000, 10000)
    test.test()
    trades = test.get_trades()
    trades = trades.to_html()
    final_balance = round(test.balance,2)
    starting_balance = 10000
    final_pnl = round((test.balance - starting_balance) / starting_balance,3)
    display_trades = test.display_trades()
    display_equity = test.display_equity()
    
    display_trades = display_trades.to_html(auto_play=False, full_html=False, default_height=600, default_width=1000)
    display_equity = display_equity.to_html(auto_play=False, full_html=False, default_height=600, default_width=1000)
    
    context = {
        "object": obj,
        "form": form,
        "trades": trades,
        "final_balance": final_balance,
        "final_pnl": final_pnl,
        "display_trades": display_trades,
        "display_equity": display_equity,
        }
    return render(request, "strat/strat_detail.html", context)


