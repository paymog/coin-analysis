from datetime import datetime
from time import sleep
import datetimerange
from pycoingecko import CoinGeckoAPI
import json
import os
import datetime
cg = CoinGeckoAPI()

def load_data(name):
    path = f"data/{name}.json"
    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        d = json.load(f)
        return d


def save_data(data, name):
    print(f"saving data for {name}")
    with open(f"data/{name}.json", "w") as f:
        json.dump(data, f, indent=4)



def try_get_historical_data(name):
    try:
        return cg.get_coin_market_chart_by_id(name, "usd", "max")
    except:
        return None


def pull_data_from_coingecko():
    for page in range(10):
        print(f"on page {page}")
        for market in cg.get_coins_markets("usd", per_page=250, page=page):
            name = market["id"]
            print(f"processing market {name}")
            if load_data(name):
                print("data for {name} already exists")
                continue

            historical_data = {}
            while True:
                print(f"trying to get historical data for {name}")
                historical_data = try_get_historical_data(name)
                if not historical_data:
                    print("could not get data, sleeping and trying again")
                    sleep(30)
                else:
                    break

            data = {}
            for datum in zip(historical_data["prices"], historical_data["market_caps"]):
                ddate = datetime.datetime.fromtimestamp(datum[0][0]/1000)
                date_string = ddate.strftime("%Y-%m-%d")
                current_price = datum[0][1]
                market_cap = datum[1][1]
                data[date_string] = {"market_cap": market_cap, "price": current_price} 

            save_data(data, name)

pull_data_from_coingecko()