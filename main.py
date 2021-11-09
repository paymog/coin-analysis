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
    with open(f"data/{name}.json", "w") as f:
        json.dump(data, f, indent=4)

def last_known_date(data):
    if data:
        return sorted(data.keys())[-1]
    else:
        return "2015-1-1"


for market in cg.get_coins_markets("usd"):
    name = market["id"]
    data = load_data(name)
    for date in datetimerange.DateTimeRange(last_known_date(data), "2021-11-1").range(datetime.timedelta(days=1)):
        while True:
            try:
                date_string = f"{date.day}-{date.month}-{date.year}"
                history = cg.get_coin_history_by_id("bitcoin", date_string)
            except Exception as e:
                print(e)
                save_data(data, name)
                sleep(30)
                continue

            if "market_data" in history:
                current_price = history["market_data"]["current_price"]["usd"]
                market_cap = history["market_data"]["market_cap"]["usd"]

                date_string = date.strftime("%Y-%m-%d")

                data[date_string] = {"market_cap": market_cap, "price": current_price} 
                print(f"Got data for {date_string} for {name}")
            break
    save_data(data, name)