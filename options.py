import requests
import threading
import pandas as pd
import numpy as np

# Sandbox (free) access to Tradier's API
KEY = '3AljpLEMJRAGWauIXPgqz5U1HmcA'

def get_expiration_dates(ticker):

    """Returns a list of current expiration dates for a given ticker"""

    response = requests.get('https://sandbox.tradier.com/v1/markets/options/expirations',
        params={'symbol': ticker},
        headers={'Authorization': 'Bearer '+KEY, 'Accept': 'application/json'})

    response = response.json()
    return response['expirations']['date']

def get_option_chain(ticker, date):

    """Returns a dictionary of lists sorted by calls & puts of option data
       at every strike price on a given expiration date for a given ticker.

       Each option's data has the following keys:
      ['symbol', 'description', 'exch', 'type', 'last', 'change',
       'volume', 'open', 'high', 'low', 'close', 'bid', 'ask',
       'underlying', 'strike', 'greeks', 'change_percentage',
       'average_volume', 'last_volume', 'trade_date', 'prevclose',
       'week_52_high', 'week_52_low', 'bidsize', 'bidexch', 'bid_date',
       'asksize', 'askexch', 'ask_date', 'open_interest', 'contract_size',
       'expiration_date', 'expiration_type', 'option_type', 'root_symbol']"""

    response = requests.get('https://sandbox.tradier.com/v1/markets/options/chains',
               params={'symbol': ticker, 'expiration': date, 'greeks': 'true'},
               headers={'Authorization': 'Bearer '+KEY, 'Accept': 'application/json'})

    response = response.json()['options']['option']
    result = {'calls' : [], 'puts' : []}

    for option in response:
        if option['option_type'] == 'call':
            result['calls'].append(option)
        else:
            result['puts'].append(option)

    return result

def get_option_chains(ticker, date_range):

    """Returns a dictionary (sorted by date) of option chains using
       multithreading given a ticker and date range"""

    chains = {}
    def add_chain(date):
      chains[date] = get_option_chain(ticker, date)

    threads=[]
    dates = get_expiration_dates(ticker)[0:date_range]
    for date in dates:
        x = threading.Thread(target=add_chain, args=(date,))
        threads.append(x)
    [t.start() for t in threads]
    [t.join() for t in threads]

    sorted = {}
    for date in dates:
        sorted[date] = chains[date]

    return sorted


def get_all_strikes(chains):

    """Returns a list of all strikes in a dictionary
       of options chains"""

    dates = list(chains.keys())
    strikes = []
    for date in dates:
        for option in chains[date]['calls']:
            if option['strike'] not in strikes:
                strikes.append(option['strike'])

    strikes.sort(reverse=True)
    return strikes


def get_dataframe(chains, direction, key):

    """Returns a pandas dataframe given a option metric
       key and dictionary of option chains"""

    z = {}
    dates = list(chains.keys())
    for date in dates:
        local_strikes = [option['strike'] for option in chains[date][direction]]
        data = []
        for strike in get_all_strikes(chains):
            if strike in local_strikes:
                index = local_strikes.index(strike)
                data.append(chains[date][direction][index][key])
            else:
                data.append(np.nan)

        z[date] = data

    return pd.DataFrame(z, index=get_all_strikes(chains))
