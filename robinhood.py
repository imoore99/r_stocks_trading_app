
import robin_stocks.robinhood as r
import pandas as pd
from datetime import datetime
###Variables

now = datetime.now().strftime("%H:%M:%S")

###Robinhood holdings table setup
def robinhood_build(ticker_tbl):
    
    my_stocks = r.build_holdings()
    
    holding_ticker_list = []
    average_buy_list = []
    quantity_list = []
    for i, j in my_stocks.items():
        holding_ticker_list.append(i)
        average_buy_list.append(float(j['average_buy_price']))
        quantity_list.append(float(j['quantity']))

    current_price_list = []
    for i in holding_ticker_list:
        current_price = r.stocks.get_latest_price(i)
        current_price = float(current_price[0])
        current_price_list.append(current_price)

    stock_holdings_df = pd.DataFrame(
                          {'Ticker': holding_ticker_list,
                          'Average_buy_price': average_buy_list,
                          'Quantity_holdings': quantity_list,
                          'Current_price_list': current_price_list}
                          )

    stock_holdings_f = ticker_tbl.set_index('Ticker').join(stock_holdings_df.set_index('Ticker')).reset_index()
    stock_holdings = stock_holdings_f.dropna()
    print(stock_holdings)
    #cash balance/buying power
    cash_bal = r.profiles.load_account_profile('cash_balances')
    buying_power = float(cash_bal['buying_power'])
    portfolio_cash = float(cash_bal['unsettled_funds'])
    pending_deposits = float(cash_bal['uncleared_deposits'])
    unsettled_funds = "{:.2f}".format(float(portfolio_cash+pending_deposits))

    #r.logout()
    #isolate stocks not currently being held
    
    non_holdings = stock_holdings_f[pd.isnull(stock_holdings_f['Quantity_holdings'])]
    
    return stock_holdings, buying_power, unsettled_funds, non_holdings
print("Robinhood stock data loaded at "+ datetime.now().strftime("%H:%M:%S"))

#robinhood crypto table setup
def crypto_robinhood_build(crypto_ticker_data):
    
    crypto_positions = r.crypto.get_crypto_positions()

    crypto_ticker = []
    avg_price = []
    quantity = []
    ask_price = []
    for i in crypto_positions:
        #ticker
        coin = i['currency']['code']
        crypto_ticker.append(coin)

        #Avg_price
        if float(i['cost_bases'][0]['direct_quantity']) <= 0:
            avg_cost = 0
        else: 
            avg_cost = float(i['cost_bases'][0]['direct_cost_basis'])/float(i['cost_bases'][0]['direct_quantity'])
        avg_price.append(avg_cost)

        #quantity_held
        quantity_held = i['cost_bases'][0]['direct_quantity']
        quantity.append(quantity_held)

        #Current Price Data Pull from Robinhood
        quote = r.crypto.get_crypto_quote(coin)
        price = quote['ask_price']
        ask_price.append(price)


    crypto_holdings_df = pd.DataFrame(
                              {'Ticker': crypto_ticker,
                              'Average_buy_price': avg_price,
                              'Quantity': quantity,
                              'Current_price_list': ask_price}
                              )
    ticker_name = []
    amt_to_sell = []
    strategy = []


    for i in crypto_ticker_data:
        n = i['fields']['Name']
        a = i['fields']['Amt_to_sell']
        s = i['fields']['Strategy']

        ticker_name.append(n)
        amt_to_sell.append(a)
        strategy.append(s)
    crypto_ticker_df = pd.DataFrame(
                          {'Ticker': ticker_name,
                          'amt_to_sell':amt_to_sell,
                          'strategy': strategy}
                          )
    crypto_table = crypto_holdings_df.set_index('Ticker').join(crypto_ticker_df.set_index('Ticker'))
    return crypto_table
print("Robinhood crypto data loaded at "+ datetime.now().strftime("%H:%M:%S"))

### Functions that pull out stock historicals
def stock_formula(stock, hist_int, hist_span):
    #---> Create df for historical data
    df = pd.DataFrame()
    #---> load historical data
    h = r.stocks.get_stock_historicals(str(stock), interval=str(hist_int), span=str(hist_span))
    #--->List for loop
    Ticker = []
    Date = []
    Price = []
    #--->Loop through to pull out historical data for analysis
    for i in h:
        t = stock
        d = pd.to_datetime(i['begins_at'], format='%Y-%m-%d').replace(tzinfo=None) 
        n = i['close_price']
        Ticker.append(t)
        Date.append(d)
        Price.append(n)

    df['Ticker'] = Ticker
    df['Date'] = Date
    df['Price'] = Price
    
    df['mean_20'] = df['Price'].rolling(20).mean()
    df['mean_5'] = df['Price'].rolling(5).mean()
    
    df =df[-1:]
    mean_20 = float(df['mean_20'])
    mean_5 = float(df['mean_5'])
    
    return mean_20, mean_5

