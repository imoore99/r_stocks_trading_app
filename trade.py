

from datetime import datetime
import time
import robin_stocks.robinhood as r

from robinhood import stock_formula


###Variables
#Stock swing formula
now = datetime.now().strftime("%H:%M:%S")
def swing(stock_holdings, quantity, base_id, robinhood_data_api, robinhood_table_id, buying_power):
    #Filter stock_holdings for swing stocks
    swing_holdings = stock_holdings[stock_holdings['position']=='Swing']
    print('Swing Holdings: ')
    print(swing_holdings)
    for i in range(len(swing_holdings)):
        ticker = swing_holdings.iloc[i,0]
        avg_price = swing_holdings.iloc[i, 2]
        sell_price = float(avg_price)*1.0035
        current_price = swing_holdings.iloc[i, 4]
        quantity_holdings = swing_holdings.iloc[i, 3]
        record = {'Name':str(ticker), 'Cost Per Share':avg_price, 'Sold Price Per Share':current_price, 'Quantity Sold':quantity}
        if current_price > sell_price and quantity_holdings >= quantity:
            ###sell command in robinhood
            r.orders.order_sell_market(ticker, quantity)
            print('Sell', ticker, avg_price, sell_price, current_price, quantity)
            #airtable API current
            robinhood_data_api.create(base_id, robinhood_table_id, record)
        elif quantity_holdings < quantity and buying_power >= (quantity*5):
            ###buy command in robinhood
            buy_quantity = quantity - quantity_holdings
            r.orders.order_buy_market(ticker, buy_quantity)
            print('Buy', ticker, avg_price, sell_price, current_price, buy_quantity)
        #Made need to establish a 1s break in code for each loop
        time.sleep(.25)


#non-holdings formula
def no_hold_buy(non_holdings, quantity):
    print('Non-Holdings: ')
    print(non_holdings)
    for t in non_holdings['Ticker']:
        r.orders.order_buy_fractional_by_quantity(t, int(quantity)+.10)
        print('Buy', t, int(quantity)+.10)
        time.sleep(.25)

#Swing-Long formula
def swing_long(stock_holdings, quantity, base_id, robinhood_data_api, robinhood_table_id, buying_power):
    #Filter stock_holdings for swing-long stocks
    swing_long_holdings = stock_holdings[stock_holdings['position']=='Swing-Long']
    print('Swing-Long:')
    print(swing_long_holdings)
    for i in range(len(swing_long_holdings)):
        ticker = swing_long_holdings.iloc[i,0]
        avg_price = swing_long_holdings.iloc[i, 2]
        current_price = swing_long_holdings.iloc[i, 4]
        quantity_holdings = swing_long_holdings.iloc[i, 3]

        data = stock_formula(ticker, 'hour', 'month')
        mean_20 = data[0]
        mean_5 = data[1]
        
        record = {'Name':str(ticker), 'Cost Per Share':avg_price, 'Sold Price Per Share': current_price, 'Quantity Sold':quantity}

        if mean_5 <= mean_20 and mean_5 > avg_price and quantity_holdings >= quantity:
            ###sell command in robinhood
            r.orders.order_sell_market(ticker, quantity)
            print('Sell', ticker, quantity_holdings, mean_20, mean_5) 
            #airtable API current
            robinhood_data_api.create(base_id, robinhood_table_id, record)
        
        elif mean_5 >= mean_20 and quantity_holdings < quantity and buying_power >= (quantity*10):
            buy_quantity = quantity-quantity_holdings
            print('Buy', ticker, buy_quantity, mean_20, mean_5) 
        #Made need to establish a 1s break in code for each loop
        time.sleep(.25)

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
        if current_price >= sell_price and quantity_holdings >= quantity_to_sell:
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