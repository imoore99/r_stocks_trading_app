

from datetime import datetime
import time
import robin_stocks.robinhood as r


###Variables
#Stock swing formula
now = datetime.now().strftime("%H:%M:%S")
def swing(stock_holdings, non_holdings, quantity, base_id, robinhood_data_api, robinhood_table_id):
    for i in range(len(stock_holdings)):
        ticker = stock_holdings.iloc[i,0]
        avg_price = stock_holdings.iloc[i, 1]
        sell_price = avg_price*1.0035
        current_price = stock_holdings.iloc[i, 3]
        quantity_holdings = stock_holdings.iloc[i, 2]
        record = {'Name':str(ticker), 'Cost Per Share':avg_price, 'Sold Price Per Share':current_price, 'Quantity Sold':quantity}
        if current_price > avg_price and quantity_holdings > quantity:
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
        r.orders.order_buy_fractional_by_quantity(ticker, .10)
        print('Buy', i, .10)
print("Stock trades loaded at "+ datetime.now().strftime("%H:%M:%S"))

#Crypto swing formula
def crypto_swing(swing_table, base_id, robinhood_data_api, robinhood_table_id):
    for i in range(len(swing_table)):
        #variable set-up
        ticker = swing_table.iloc[i,0]
        avg_price = float(swing_table.iloc[i, 1])
        sell_price = float(avg_price)*1.0035
        quantity_holdings = float(swing_table.iloc[i, 2])
        current_price = float(swing_table.iloc[i, 3])
        quantity_to_sell = float(swing_table.iloc[i, 4])
        
        #airtable record posting data
        record = {'Name':str(ticker), 'Cost Per Share':avg_price, 'Sold Price Per Share':current_price, 'Quantity Sold':quantity_to_sell}
        
        #Buy and sell conditions for swing trade
        if sell_price > avg_price and quantity_holdings > quantity_to_sell:
            ###sell command in robinhood
            r.orders.order_crypto(ticker, 'sell', quantity_to_sell)
            print('Sell', ticker, avg_price, sell_price, current_price, quantity_to_sell)
            #airtable API current
            robinhood_data_api.create(base_id, robinhood_table_id, record)
        elif quantity_holdings < quantity_to_sell:
            ###buy command in robinhood
            r.orders.order_crypto(ticker, 'buy', quantity_to_sell)
            print('Buy', ticker, avg_price, sell_price, current_price, quantity_to_sell)
        #Made need to establish a 1s break in code for each loop
        time.sleep(.25)
print("Crypto trades loaded at "+ datetime.now().strftime("%H:%M:%S"))