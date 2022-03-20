from tkinter import *  
import threading

import pandas as pd

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import robin_stocks.robinhood as r

from datetime import date, datetime, timedelta

import warnings
warnings.filterwarnings("ignore")

#airtable API/Data import
from airtable import api_data_connection, earnings_data
#robinood API/Data/Function import
from robinhood import robinhood_build, crypto_robinhood_build
#trade functions
from trade import swing, no_hold_buy, crypto_swing, swing_long
#login-table setup
from login import (robinhood_table_id, ticker_table_id, cash_bal_table_id, 
                    crypto_table_id, base_id, api_key, email, pw)


###Variables

quantity = 6

loop = 30

#API Connections to Airtable DB
cash_bal_data_api = api_data_connection(api_key, base_id, cash_bal_table_id, 0)
#ticker_data_api = api_data_connection(api_key, base_id, ticker_table_id, 0)
robinhood_data_api = api_data_connection(api_key, base_id, robinhood_table_id, 0)
crypto_ticker_api = api_data_connection(api_key, base_id, crypto_table_id, 0)
#Data Connections to Airtable DB
#cash_bal_data = api_data_connection(api_key, base_id, cash_bal_table_id, 1)
ticker_data = api_data_connection(api_key, base_id, ticker_table_id, 1)
robinhood_data = api_data_connection(api_key, base_id, robinhood_table_id, 1)
#crypto_ticker_data = api_data_connection(api_key, base_id, crypto_table_id, 1)


#tkinter setup
# Create an instance of tkinter frame
win= Tk()
# Set the size of the Tkinter window
#win.geometry("700x350")
run = False

def start_trade_loop():
    global run
    global login
    run = True
    print("Trade Loop Started")
    app_start.config(text="App Started: "+ datetime.now().strftime("%m/%d/%y %H:%M:%S"))
    #Login to Robinhood
    print("robinhood data login "+ datetime.now().strftime("%H:%M:%S"))
    login = r.login(email, pw)

def stop_trade_loop():
    global run
    run = False
    print("Trade Loop Killed")
    app_stop.config(text="App Stopped: "+ datetime.now().strftime("%m/%d/%y %H:%M:%S"))
    r.logout()
    print("robinhood data logout "+ datetime.now().strftime("%H:%M:%S"))

def earnings_fig(data_set):
    trade_date = []
    net_earnings = []

    for i in data_set:
        n = i['fields']['Net Total']
        t = i['fields']['Trade Date'] 
        t= pd.to_datetime(t, format='%Y-%m-%d').replace(tzinfo=None) - timedelta(hours=8)
        trade_date.append(t)
        net_earnings.append(n)

    data = {'Trade Date':trade_date, "Net Earnings": net_earnings}    
    net_earnings = pd.DataFrame(data=data).sort_values('Trade Date').reset_index()
    net_earnings['Trade Date'] = pd.to_datetime(net_earnings['Trade Date'], format='%Y-%m-%d')

    today=date.today()
    today=today.strftime("%m/%d/%Y")
    today = pd.to_datetime(today)

    week=today - timedelta(days=7)
    week_earnings = net_earnings[net_earnings['Trade Date']>week]
    date_list = []
    for i in week_earnings['Trade Date']:
        date_list.append(i.date().strftime("%m/%d"))
    week_earnings['Date'] = date_list
    week_earnings = week_earnings.groupby(['Date']).sum().reset_index()
    week_earnings['Cum Earnings'] = week_earnings['Net Earnings'].cumsum()

    x = week_earnings['Date']
    y = week_earnings['Net Earnings']
    y_2 = week_earnings['Cum Earnings']
    
    fig=Figure(figsize=(6, 3), dpi=100)
    plt = fig.add_subplot(111)
    plt.bar(x, y)
    plt.plot(x, y_2, color='#FACB68')
    fig.autofmt_xdate(rotation=45)
    fig.suptitle('Earnings Breakout', fontsize=14)

    canvas = FigureCanvasTkAgg(fig, master = win)  
    canvas.draw()
    canvas.get_tk_widget().grid(column=5, row=2, columnspan=8, rowspan=5)

earnings_figure = earnings_fig(robinhood_data)

###THIS SHOULD BE THE START OF THE LOOP
def trade_loop():
    if run:
        print("Loop starts now "+ datetime.now().strftime("%H:%M:%S"))

        print("Airtable ticker load "+ datetime.now().strftime("%H:%M:%S"))
        #Clean airtable data for stored/input ticker list
        airtable_ticker_list = []
        airtable_position_list = []
        for i in ticker_data:
            ticker = i['fields']['Name']
            airtable_ticker_list.append(ticker)
            
            position = i['fields']['Trade_Type']
            airtable_position_list.append(position)
        ticker_tbl = pd.DataFrame(
                        {'Ticker':airtable_ticker_list,
                        'position': airtable_position_list}
                        )
        print("robinhood data load "+ datetime.now().strftime("%H:%M:%S"))

        #clean/extract robinhood data
        robinhood_account_data = robinhood_build(ticker_tbl)
        stock_holdings = robinhood_account_data[0]
        buying_power = robinhood_account_data[1]
        unsettled_funds = robinhood_account_data[2]
        non_holdings = robinhood_account_data[3]

        #clean/extract robinhood crypto data
        #crypto_table = crypto_robinhood_build(crypto_ticker_data).reset_index()
        #crypto_swing_data = crypto_table[crypto_table['strategy']=='Swing']
        #crypto_ST_data = crypto_table[crypto_table['strategy']=='ST']

        print("Airtable cash bal load "+ datetime.now().strftime("%H:%M:%S"))
        #Load current cash bal into airtable
        record = {'Cash Bal': str(buying_power), 'Unsettled Funds':unsettled_funds}
        cash_bal_data_api.create(base_id, cash_bal_table_id, record)
        print("robinhood trade analysis and airtable load "+ datetime.now().strftime("%H:%M:%S"))
        
        #performs swing trade analysis
        swing(stock_holdings, quantity, base_id, robinhood_data_api, robinhood_table_id, buying_power)
        no_hold_buy(non_holdings, quantity)
        swing_long(stock_holdings, quantity, base_id, robinhood_data_api, robinhood_table_id, buying_power)
        #crypto_swing(crypto_swing_data, base_id, robinhood_data_api, robinhood_table_id)

        #tkinter buying power and unsettled funds label configuration
        bp_label.config(text="Buying Power: ${:.2f}".format(float(buying_power)))
        uf_label.config(text="Unsettled Funds: ${:.2f}".format(float(unsettled_funds)))

        #earnings data output
        robinhood_data = api_data_connection(api_key, base_id, robinhood_table_id, 1)
        earnings = earnings_data(robinhood_data)
        lifetime_earnings = earnings[0]
        today_earnings = earnings[1]
        today_trans = earnings[2]
        #tkinter earnings and transactions configuration
        lt_earnings.config(text="Lifetime Earnings: ${:.2f}".format(float(lifetime_earnings)))
        today_net.config(text='Today\'s Net Earnings: ${:.2f}'.format(float(today_earnings)))
        today_trade.config(text='Today\'s Total Trades: {}'.format(int(today_trans)))

        earnings_fig(robinhood_data)

        print("Loop ends now "+ datetime.now().strftime("%H:%M:%S"))
    # After 30 sec call the robinhood_function again
    win.after(30000, trade_loop)
###THIS SHOULD BE THE END OF THE LOOP - breaks for 30 seconds - then restarts

#Tkinter Setup

header = Label(win, text="Robinhood Trade Application", font=("Arial", 15), bg='brown', fg='white', width=100)
header.grid(row=0, column=0, columnspan=12, rowspan=1, ipadx=20, ipady=10)

#Start and Stop Application buttons
header_start_stop = Label(win, text="Start/Stop Trading Process",font=("Arial", 12))
header_start_stop.grid(row=1,column=0, columnspan=4, ipadx=20, ipady=10, padx=20)

start=Button(win, text= "Start Application", relief='raised', command=start_trade_loop)
start.grid(row=2, column=0, columnspan=2, ipadx=2, ipady=2, padx=20, pady=10)
### --> Need to hook up application start times
app_start = Label(win, text="App Started: ")
app_start.grid(row=2,column=2, columnspan=2, ipadx=2, ipady=2, pady=10)

stop=Button(win, text= "Stop Application", relief='raised', command=stop_trade_loop)
stop.grid(row=3, column=0, columnspan=2, ipadx=2, ipady=2, padx=20, pady=10)
### --> Need to hook up application stop times
app_stop = Label(win, text="App Stopped: ")
app_stop.grid(row=3,column=2, columnspan=2, ipadx=2, ipady=2, pady=10)

#trade data
header_start_stop = Label(win, text="Today's Trade Data",font=("Arial", 12))
header_start_stop.grid(row=4,column=0, columnspan=4, ipadx=20, ipady=10, padx=20)

bp_label = Label(win, text='Current Buying Power: ')
bp_label.grid(row=5,column=0, columnspan=4, ipadx=20, ipady=10, padx=20)

uf_label = Label(win, text='Unsettled Funds: ')
uf_label.grid(row=6,column=0, columnspan=4, ipadx=20, ipady=10, padx=20)

today_net = Label(win, text='Today\'s Net Earnings: ')
today_net.grid(row=7,column=0, columnspan=4, ipadx=20, ipady=10, padx=20)

today_trade = Label(win, text='Today\'s Total Trades: ')
today_trade.grid(row=8,column=0, columnspan=4, ipadx=20, ipady=10, padx=20)

#Lifetime earnigns call
lt_earnings = Label(win, text='Lifetime Earnings: ',font=("Arial", 12), borderwidth=1, relief='solid')
lt_earnings.grid(row=1,column=4, columnspan=7, ipadx=20, ipady=10, pady=20)


# Call the trade() function after 30 sec.
win.after(0, trade_loop) 
win.mainloop()