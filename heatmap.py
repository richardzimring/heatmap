from options import *
import json
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

## USER INPUTS ##
TICKER = input('Stock ticker? (Ex. TSLA): ')
DATE_RANGE = int(input('How many expiration dates out?: '))
DIRECTION = input('"calls" or "puts"?: ')
METRIC = input('"open_interest" or "volume"?: ')
if DIRECTION == 'calls':
    color = "Greens"
else:
    color = "Reds"

# Fetch options data using "options.py" helper functions
chains = get_option_chains(TICKER, DATE_RANGE)
df = get_dataframe(chains, DIRECTION, METRIC)

# Trim strike price range
strike_sums = df.sum(axis=1)
sig_strikes = list(strike_sums[lambda i: i > 0.03*sum(strike_sums)].index.values)
df = df[sig_strikes[0] : sig_strikes[-1]]
print(df)

# Plot a heatmap
sns.heatmap(df,
            linewidths=2,
            cmap=color)
plt.title(TICKER + " " + DIRECTION.capitalize()[:-1] + " Options " + METRIC.replace('_',' ').title() + " Heat Map", fontsize=18)
plt.xlabel("Expiration Date")
plt.ylabel("Strike Price")
plt.tight_layout()
plt.show()
