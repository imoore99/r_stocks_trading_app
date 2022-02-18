

from datetime import datetime
import time
import robin_stocks.robinhood as r


###Variables

now = datetime.now().strftime("%H:%M:%S")
def swing(stock_holdings, non_holdings, quantity, base_id, robinhood_data_api, robinhood_table_id):
    for i in range(len(stock_holdings)):
        ticker = stock_holdings.iloc[i,0]
        avg_price = stock_holdings.iloc[i, 1]
        sell_price = avg_price*1.005
        current_price = stock_holdings.iloc[i, 3]
        quantity_holdings = stock_holdings.iloc[i, 2]
        record = {'Name':str(ticker), 'Cost Per Share':avg_price, 'Sold Price Per Share':current_price, 'Quantity Sold':quantity}
        if current_price >= avg_price and quantity_holdings > quantity:
            ###sell command in robinhood
            r.orders.order_sell_market(ticker, quantity)
            print('Sell', ticker, avg_price, current_price, current_price, quantity)
            #airtable API current
            robinhood_data_api.create(base_id, robinhood_table_id, record)
        elif quantity_holdings < quantity:
            ###buy command in robinhood
            r.orders.order_buy_market(ticker, quantity)
            print('Buy', ticker, avg_price, sell_price, current_price, quantity)
        #Made need to establish a 1s break in code for each loop
        time.sleep(.25)
    for i in non_holdings['Ticker']:
        r.orders.order_buy_market(ticker, quantity+.10)
        print('Buy', i, quantity+.10)
print("trade loaded at "+ now)