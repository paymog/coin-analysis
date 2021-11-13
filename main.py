from datetime import datetime
from time import sleep
import datetimerange
from pycoingecko import CoinGeckoAPI
import json
import os
import datetime
from typing import Dict, List, Tuple
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

def load_all_data() -> Dict[str, Dict[str, Dict[str, str]]]:
    directory = "data"
    data = {}
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename)) as f:
            
            data[os.path.splitext(filename)[0]] = json.load(f)

    return data

def normalize_data(data: Dict[str, Dict[str, Dict[str, str]]]) -> Dict[str, Dict[str, Dict[str, str]]]:
    normalized_data = {}
    for coin, historical_data in data.items():
        for date, datum in historical_data.items():
            if date not in normalized_data:
                normalized_data[date] = {}
            
            if datum["market_cap"] and datum["price"]:
                normalized_data[date][coin] = datum

    return normalized_data


def sort_coins_by_market_cap(coin_data: Dict[str, Dict[str, str]]) -> List[str]:
    # def sortfunc(key):
    #     # if key not in coin_data or "market_cap" not in coin_data[key] or not coin_data[key]["market_cap"]:
    #     #     return 0
    #     # else:
    #     return coin_data[key]["market_cap"]

    return sorted(coin_data.keys(), key=lambda coin: coin_data[coin]["market_cap"], reverse=True)

def generate_altcoin_portfolio(coin_data: Dict[str, Dict[str, str]], total_investment: int, num_coins_to_invest: int) -> Tuple[Dict[str, float], int]:
    coins_by_market_cap = sort_coins_by_market_cap(coin_data)
    portfolio = {}
    coins_to_invest = coins_by_market_cap[:num_coins_to_invest]
    investment_value = total_investment / len(coins_to_invest)
    for coin in coins_to_invest:
        portfolio[coin] = investment_value / coin_data[coin]["price"]

    return portfolio, investment_value

def generate_bitcoin_portfolio(coin_data: Dict[str, Dict[str, str]], total_investment: int) -> Dict[str, float]: 
    return {"bitcoin": total_investment / coin_data["bitcoin"]["price"] }

def evaluate_portfolio(altcoin_portfolio: Dict[str, float], coin_data: Dict[str, Dict[str, str]], initial_investment_value: int) -> float:
    total_value = 0
    for coin, amount in altcoin_portfolio.items():
        if coin not in coin_data:
            total_value -= initial_investment_value
        else:
            total_value += amount * coin_data[coin]["price"] 

    return total_value


def perform_analysis():
    data = load_all_data()
    normalized_data = normalize_data(data)
    last_date = sorted(normalized_data.keys())[-1]
    btc_performance_sum = 0
    altcoin_performance_sum = 0
    for date, coin_data in normalized_data.items():
        total_investment = 100000
        num_alts_to_invest = 100
        altcoin_portfolio, initial_per_coin_investment = generate_altcoin_portfolio(coin_data, total_investment, num_alts_to_invest)
        altcoin_portfolio_termination_value = evaluate_portfolio(altcoin_portfolio, normalized_data[last_date], initial_per_coin_investment)
        altcoin_performance = (altcoin_portfolio_termination_value - total_investment) / total_investment * 100
        altcoin_performance_sum += altcoin_performance

        bitcoin_portfolio = generate_bitcoin_portfolio(coin_data, total_investment)
        bitcoin_portfolio_termination_value = evaluate_portfolio(bitcoin_portfolio, normalized_data[last_date], total_investment)
        bitcoin_performance = (bitcoin_portfolio_termination_value - total_investment) / total_investment * 100
        btc_performance_sum += bitcoin_performance

        # print(f"{date}\n\tAlt - {altcoin_performance}\n\tBitcoin - {bitcoin_performance}")

    print(f"Avg alt performance {altcoin_performance_sum / len(normalized_data)}")
    print(f"Avg btc performance {btc_performance_sum / len(normalized_data)}")

    # print(normalized_data["2021-05-05"])
    
def clean_bitcoin_data():
    data = load_data("bitcoin")
    first_date = sorted(data.keys())[0]
    print(first_date)
    for d in datetimerange.DateTimeRange(first_date,  "2021-11-12").range(datetime.timedelta(days=1)):
        if d.strftime("%Y-%m-%d") not in data:
            print(d)

# clean_bitcoin_data()
perform_analysis()