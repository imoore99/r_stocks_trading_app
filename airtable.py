#Sheet capture airtable data - transforms for plotly charting

from pyairtable import Api
from datetime import date, datetime, timedelta
import pandas as pd
###Variables

now = datetime.now().strftime("%H:%M:%S")
#API Function - extracts api conenction and data

def api_data_connection(api_key, base_id, tbl_name, pos):
    api_key = api_key
    base_id = base_id
    tbl_name = tbl_name
    def airtable_api(api_key, base_id, tbl_name):
        api_var = Api(api_key)
        data = api_var.all(base_id, tbl_name)
        return api_var, data
    data = airtable_api(api_key, base_id, tbl_name)[pos]
    return data

print("airtable loaded at "+ now)

def earnings_data(data_set):
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
    
    lifetime_earnings = sum(net_earnings['Net Earnings'])
    
    today=date.today()
    today=today.strftime("%m/%d/%Y")
    today = pd.to_datetime(today)
    
    today_earnings = sum(net_earnings[net_earnings['Trade Date']>today]['Net Earnings'])
    today_trans = len(net_earnings[net_earnings['Trade Date']>today]['Net Earnings'])
    
    return lifetime_earnings, today_earnings, today_trans

