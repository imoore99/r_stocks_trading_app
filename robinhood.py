
import robin_stocks.robinhood as r
import pandas as pd
from datetime import datetime
###Variables

now = datetime.now().strftime("%H:%M:%S")

###Robinhood holdings table Setup
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
                          'Quantity': quantity_list,
                          'Current_price_list': current_price_list}
                          )

    stock_holdings_f = stock_holdings_df.Ticker.isin(ticker_tbl)
    stock_holdings = stock_holdings_df[stock_holdings_f]
    print(stock_holdings)
    #cash balance/buying power
    cash_bal = r.profiles.load_account_profile('cash_balances')
    buying_power = float(cash_bal['buying_power'])
    portfolio_cash = float(cash_bal['unsettled_funds'])
    pending_deposits = float(cash_bal['uncleared_deposits'])
    unsettled_funds = "{:.2f}".format(float(portfolio_cash+pending_deposits))

    #r.logout()
    #isolate stocks not currently being held
    ticker_tbl = pd.DataFrame(
                {'Ticker':ticker_tbl}
                )
    non_holdings = ticker_tbl[~ticker_tbl.Ticker.isin(stock_holdings['Ticker'])]
    
    return stock_holdings, buying_power, unsettled_funds, non_holdings
print("robinhood loaded at "+ now)



