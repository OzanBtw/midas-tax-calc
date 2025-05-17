import matplotlib.pyplot as plt
import json
from datetime import date, datetime, timedelta



def get_revenue_graph(year):
    path = "source/year_data.json"
    with open(path, 'r') as f:
        data = json.load(f)

    months = data[year]['months']

    revenues = []
    for m in months:
        revenue = 0.0
        for t in m.keys():
            revenue += m[t]['revenue']
        revenues.append(revenue)

    
    time_line = [1,2,3,4,5,6,7,8,9,10,11,12]
    
    if date.today().year == int(year):
        k = date.today().month -1
        time_line = time_line[:k]
        revenues = revenues[:k]

    return time_line, revenues



def get_ticker_graph(year, ticker):
    path = "source/year_data.json"
    with open(path, 'r') as f:
        data = json.load(f)

    months = data[year]['months']

    revenues = []
    for m in months:
        if ticker in m.keys():
            revenues.append(m[ticker]['revenue'])
        else:
            revenues.append(0)

    
    time_line = [1,2,3,4,5,6,7,8,9,10,11,12]
    
    if date.today().year == int(year):
        k = date.today().month -1
        time_line = time_line[:k]
        revenues = revenues[:k]

    return time_line, revenues


if __name__ == "__main__":
    print(get_ticker_graph("2024", "TSLA"))