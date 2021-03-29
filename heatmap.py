import options #must have requests-html and html5lib installed
import numpy as np
from pandas import DataFrame
import seaborn as sns
import matplotlib.pyplot as plt
import threading

#####################################
Text = False #Print a summary of the final data
Graph = True #Show a heatmap of the final data with matplotlib
#####################################

# heatmap of options info for a given stock
#
# xaxis - expiration dates
# yaxis - strike prices
# values - Open Interest / Vol

## prompt user input
print("----")
ticker = input("ticker? (e.g. TSLA): ")
print("\n")
data_type = input("graph 'Vol' or 'OI?' ")
if data_type == 'Vol':
    data_type = 'Volume'
else:
    data_type = 'Open Interest'

print("\n")
direction = input("'puts' or 'calls'? ")
if direction == 'calls':
    color = "Greens"
else:
    color = "Reds"

print("\n")
how_far_out = int(input("include how many expiration dates out? "))
print("----")
print("\n")
print("fetching prices...")
print("\n")


expiry_dates = options.get_expiration_dates(ticker)[0:how_far_out]
dict = {}

## for an expiry: fetch strikes, data of type data_type
def chain_for_date(date):
    options_chain = options.get_options_chain(ticker, date)[direction]

    strike_price_df = options_chain["Strike"]
    data_df = options_chain[data_type]

    dict[date] = {  #convert ints to int and floats to float
                    "strikes":[int(i) if (str(i)[-2:]==".0") else float(i) for i in options_chain["Strike"]],

                    #convert "-" values to None and strings to int
                    "data":[None if (str(j).isdigit() == False) else int(j) for j in options_chain[data_type]]
                 }

threads=[]
## use multithreading to call get_options_chain with each date
for date in expiry_dates:
    x = threading.Thread(target=chain_for_date, args=(date,))
    threads.append(x)

[t.start() for t in threads]
[t.join() for t in threads]

## gathers ordered list of all strikes w/o duplicates
strike_prices = []

for date in expiry_dates:
    for i in dict[date]["strikes"]:
        if i not in strike_prices:
            strike_prices.append(i)

strike_prices.sort(reverse=True)


## initalize strike_sums
total_sum = 0
strike_sums = {}
for strike in strike_prices:
    strike_sums[strike] = 0


## populate strike_sums and find the total sum
for date in expiry_dates:
    for index in range(len(dict[date]["strikes"])):
        strike = dict[date]["strikes"][index]
        if dict[date]["data"][index] is not None:
            strike_sums[strike] += dict[date]["data"][index]
            total_sum += dict[date]["data"][index]

data_total = sum(strike_sums.values())


## use sums to find percentages
strike_percentages = []
for strike in strike_prices:
    strike_percentages.append(round(100*strike_sums[strike] / data_total))


## start and end with the first and last time
## that 4 strikes in a row sum to >4% of the data
for index in range(len(strike_percentages)):
    if sum(strike_percentages[index:index+3]) > 4:
        first = index
        break

for index in range(len(strike_percentages),-1,-1):
    if sum(strike_percentages[index-3:index]) > 4:
        last = index
        break

strike_prices = strike_prices[first:last]
strike_percentages = strike_percentages[first:last]


## create trimmed_strike_prices from strike_prices
## which ignores decimal strikes that are insignificant (<2%)
trimmed_strike_prices = []
for index in range(len(strike_prices)):
    if isinstance(strike_prices[index], int) or (strike_percentages[index] > 2):
        trimmed_strike_prices.append(strike_prices[index])


## create C: a dictionary of the final data uniformly formatted by date
C = {}
for date in expiry_dates:
    C[date] = [None for i in range(len(trimmed_strike_prices))]

    for q in range(len(trimmed_strike_prices)):
        if trimmed_strike_prices[q] in dict[date]["strikes"]: #if strike occurs on this date
            index = dict[date]["strikes"].index(trimmed_strike_prices[q])
            C[date][q] = dict[date]["data"][index]


## convert C into a dataframe
df = DataFrame(C, columns=expiry_dates, index=trimmed_strike_prices)


## create heat map graph of results
plt.title(ticker + " " + direction.capitalize()[:-1] + " Options " + data_type + " Heat Map", fontsize=18)
plt.subplots_adjust(bottom=.2)
sns.heatmap(df, linewidths=.1, cmap=color, robust=True) #square=True
plt.tight_layout()


if Text:
    print(df)

if Graph:
    plt.show()
