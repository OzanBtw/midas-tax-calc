from datetime import date, datetime, timedelta
import os
import pandas
import yfinance as yf
import json
import math
import copy
from pdf_paths import get_paths
import time
import shutil


#Example data {'amount': [[Amount_of_stock, dolar_price, stock_price, date]], 'revenue': 0}

pandas.options.mode.chained_assignment = None

def get_first_price_of_month_ticker(df, _datetime):
    while True:
        date = f"{_datetime.year}-{_datetime.month:02}-{_datetime.day:02}"
        try:
            row = df.loc[date]
            break
        except:
            _datetime = _datetime - timedelta(days=1)
    
    return row['Close']

def get_ticker_df(ticker, date):
    path = f"source/cache/ticker_datas/{ticker.upper()}.csv"

    if os.path.isfile(path):
        _df = pandas.read_csv(path,  header=[0, 1], index_col=0, encoding="utf-8")
        _df.columns = _df.columns.droplevel(1)

        return _df

    else:
        _df = yf.download(ticker.upper(), start=date, actions=True, progress=False)
        time.sleep(1)
        _df.to_csv(path)

        _df = pandas.read_csv(path,  header=[0, 1], index_col=0, encoding="utf-8")
        _df.columns = _df.columns.droplevel(1)





        return _df


def get_d_price(text, usd_df):
    b_price = float(usd_df.loc[text == usd_df['Tarih'], 'TP_DK_USD_A_YTL'].iloc[0])

    while b_price == 0 or math.isnan(b_price):
        c_day = text[:2]
        c_month = text[3:5]
        c_year = text[6:]
        p_date = datetime(int(c_year), int(c_month), int(c_day)) - timedelta(days=1)
        text = f"{p_date.day:02d}-{p_date.month:02d}-{p_date.year}"
        b_price = float(usd_df.loc[text == usd_df['Tarih'], 'TP_DK_USD_A_YTL'].iloc[0])

    return b_price

def get_yi_ufe_val(text, yi_ufe_df, isThreeYear=False):
    c_month = int(text[3:5])
    c_year = int(text[6:])
    
    if isThreeYear:
        c_year -= 3

    c_month -= 1
    if c_month == 0:
        c_month = 12
        c_year -= 1
    
    text = f"{c_year}-{c_month}"

    try:
        yi_ufe_val = float(yi_ufe_df.loc[text == yi_ufe_df['Tarih'], 'TP_TUFE1YI_T1'].iloc[0])

    except:
        c_month -= 1
        if c_month == 0:
            c_month = 12
            c_year -= 1 
        text = f"{c_year}-{c_month}"
        yi_ufe_val = float(yi_ufe_df.loc[text == yi_ufe_df['Tarih'], 'TP_TUFE1YI_T1'].iloc[0])


    return yi_ufe_val

def calculate_inflation(b_date, s_date, yi_ufe_df):
    b_val = get_yi_ufe_val(b_date, yi_ufe_df)
    s_val = get_yi_ufe_val(s_date, yi_ufe_df)
    s_val_three = get_yi_ufe_val(s_date, yi_ufe_df, True)
    per_1 = (s_val / s_val_three) - 1
    per_2 = (s_val / b_val) - 1

    if per_1 > 1 and per_2 > 0.1:
        return 1 + per_2
    else:
        return 1
     
    
def calculate_total_spending_value(x, date, yi_ufe_df, usd_df, isSold=True):
    cache_spending_amount = 0.0
    if isSold:
        for i in x['amount']:
            cache_spending_amount += i[0] * i[1] * i[2] * calculate_inflation(i[3], date, yi_ufe_df)
    else:
        b_price = get_d_price(date, usd_df)

        for i in x['amount']:
            cache_spending_amount += i[0] * b_price * i[2]

    return cache_spending_amount

def month_data(df, cache_data, usd_df, yi_ufe_df, startdate, debug_ticker):
    for i in range(0, len(df)):
        row = df.iloc[i]
        if row['Currency'] == "USD" and row['Status'] in ["Gerçekleşti", "Kalan İptal Edildi"] :
            date = row['Date'][:8].replace("/", "-")
            date = date[:6]+"20"+date[6:]
            b_price = get_d_price(date, usd_df)
            row['Satisfied_Amount'] = float(row['Satisfied_Amount'].replace(',','.'))
            row['Price'] = float(row['Price'].replace(',','.'))

            if row['Ticker'] not in cache_data.keys():
                cache_data[row['Ticker']] = {"amount": [], "revenue": 0.0, "total_value": 0.0, "current_value": 0.0}

                split_path = "source/cache/splits.json"
                with open(split_path, 'r') as f:
                    split_data = json.load(f)
                
                if row['Ticker'].upper() in split_data.keys():
                    pass
                else:
                    c_day = int(startdate[:2])
                    c_month = int(startdate[3:5])
                    c_year = int(startdate[6:])
                    _date = f"{c_year}-{c_month:02d}-{c_day:02d}"
                    #_df = yf.download(row['Ticker'].upper(), start=_date, actions=True, progress=False)
                    _df = get_ticker_df(row['Ticker'], date=_date)
                    #print(_df)

                    
                    splits = _df[_df["Stock Splits"]>0].drop(columns=['Open', 'High','Low','Close', 'Volume', 'Dividends'])

                    cache_master = []
                    for i in range(len(splits)):
                        _split = float(splits.iloc[i]['Stock Splits'])

                        cache_date = str(splits.index[i])
                        c_year = int(cache_date[:4])
                        c_month = int(cache_date[5:7])
                        c_day = int(cache_date[8:])
                        c_date = f"{c_day:02d}-{c_month:02d}-{c_year}"
                        cache_master.append({"Date": c_date, "Split": _split})

                    split_data[row['Ticker'].upper()] = cache_master
                    with open(split_path, 'w') as f:
                        json.dump(split_data, f, indent=2)


            split_path = "source/cache/splits.json"
            with open(split_path, 'r') as f:
                split_data = json.load(f)[row["Ticker"]]

            n = row['Date'][:8].replace("/", "-")
            n = n[:6]+"20"+n[6:]
            c_date = datetime.strptime(n, '%d-%m-%Y').date()

            for d in split_data:
                _date = datetime.strptime(d['Date'], '%d-%m-%Y').date()
                if _date <= c_date:# split happend!
                    x = cache_data[row['Ticker']] 
                    for m in x['amount']:
                        m[0] = m[0] * d["Split"]
                        m[2] = m[2] / d["Split"]
                    cache_data[row['Ticker']] = x 


            if row['Fee'] == "-":
                fee = 0
            else:
                _text = row['Fee']
                _text = _text.replace(",", ".")
                fee = float(_text)

            if row['Order_Type'] == 'Alış':
                x = cache_data[row['Ticker']] 
                x['amount'].append([row['Satisfied_Amount'], b_price, row['Price'], date])
                x['revenue'] -= fee * b_price
                
                x['total_value'] = calculate_total_spending_value(x, date, yi_ufe_df, usd_df)

                cache_data[row['Ticker']] = x

            elif row['Order_Type'] == 'Satış':
                x = cache_data[row['Ticker']]
                
                a = 0
                count = 0
                last_selling_amount = row['Satisfied_Amount']
                for i in x['amount']:
                    a += i[0]
                    if a <= row['Satisfied_Amount']:
                        count += 1
                        last_selling_amount -= i[0]
                    else:
                        break

            
                total_invest = 0 #tl
                for i in range(count):
                    lis = x['amount'].pop(0)

                    total_invest += lis[0] * lis[1] * lis[2] * calculate_inflation(lis[3], date, yi_ufe_df)
                    #total_invest += lis[1] * fee


                left_over = a - (row['Satisfied_Amount'])

                if left_over > 0: #not closed
                    if left_over > 0.00000000000001:# sometimes, the valeue becomes too small.
                            
                        total_invest += last_selling_amount * x['amount'][0][1] * x['amount'][0][2] * calculate_inflation(x['amount'][0][3], date, yi_ufe_df)
                        #total_invest += x['amount'][0][1] * fee
                    
                        x['amount'][0][0] = left_over
                    else:
                        x['amount'].pop(0)

                total_revenue = row['Satisfied_Amount'] * b_price * row['Price'] - total_invest
                total_revenue -= b_price * fee
                x['revenue'] += total_revenue

                x['total_value'] = calculate_total_spending_value(x, date, yi_ufe_df, usd_df)
                cache_data[row['Ticker']] = x

                if row['Ticker'].lower() in [debug_ticker.lower(), "_none"]:
                    print(f"Profit by selling {row['Ticker']}: {'{:,.2f}'.format(total_revenue)} | {date} | Revenue: {'{:,.2f}'.format(x['revenue'])}")
            
            if row['Ticker'].lower() in [debug_ticker.lower(), "_none"]:
                print(row['Order_Type'], row['Satisfied_Amount'], row['Price'])
                print(row['Ticker'],cache_data[row['Ticker']])
                print('')
    
    return cache_data

def renew_all(ticker="_none"):
    if not os.path.isdir("source/cache"):
        os.mkdir("source/cache")
    if os.path.isdir("source/cache/ticker_datas"):
        shutil.rmtree("source/cache/ticker_datas")
    
    os.mkdir("source/cache/ticker_datas")

    split_path = "source/cache/splits.json"

    if not os.path.isdir("source/cache"):
        os.mkdir("source/cache")

    split_data = {}
    with open(split_path, "w") as f:
        json.dump(split_data, f, indent=2)

    usd_df = pandas.read_csv('source/usd_data.csv', encoding="utf-8")
    usd_df['TP_DK_USD_A_YTL'] = usd_df['TP_DK_USD_A_YTL'].fillna(0.0)


    yi_ufe_df = pandas.read_csv('source/yi_ufe.csv', encoding="utf-8")

    paths, startdate, enddate = get_paths()
    startdate = f"01-{startdate.replace('_', '-')}"
    #startdate = '01-08-2023'
    start_year = int(startdate[-4:])
    end_year = int(enddate[-4:])


    months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    flag = True
    main_data = {}
    for y in range(start_year, end_year+1):
        month_master = []
        count = -1
        for m in months:
            count += 1
            path = f"source/extracts/tables/Midas_Ekstre_{m}_{y}.csv"
            if flag: #checks if this is the first data or not
                cache_data = {}  
                flag = False
            if os.path.isfile(path):

                df = pandas.read_csv(path, encoding="utf-8")
                cache_data = month_data(df, cache_data, usd_df, yi_ufe_df ,startdate, ticker)
                month_master.append(copy.deepcopy(cache_data))
            else:

                month_master.append(copy.deepcopy(cache_data))
                continue

        #clear revenue for the next year
        revenue = 0.0
        last_month = month_master[-1]
        for t in last_month.keys():
            revenue += last_month[t]['revenue']

        data = {"months": month_master, "total_revenue": revenue}
        cache = []
        for t in cache_data:
            if len(cache_data[t]['amount']) == 0:
                cache.append(t)
            else:
                if cache_data[t]['revenue'] != 0:
                    cache_data[t]['revenue'] = 0

        for t in cache:
            del cache_data[t]

        main_data[y] = data.copy()


    #gettin current values:
    last_data = main_data[end_year]['months'][-1]

    #print("Active orders:")
    _year = int(enddate[3:])
    _month = int(enddate[:2])
    for t in last_data.keys():
        day_1 = f"{1:02}-{_month:02}-{_year}"
        b_price = get_d_price(day_1, usd_df)
        c_val = 0.0

        if len(last_data[t]['amount']) > 0:  #actually active?
            _df = get_ticker_df(t, day_1)
            _datetime = datetime(_year, _month, 1)

            current_price = get_first_price_of_month_ticker(_df, _datetime)
    
        else: 
            current_price = 0

        for o in last_data[t]['amount']:
            c_val += o[0] * b_price * current_price
        last_data[t]['current_value'] = c_val

        last_data[t]['total_value'] = calculate_total_spending_value(last_data[t], day_1, yi_ufe_df, usd_df, isSold=False)

        #print(f"\t{t}: {c_val}, {last_data[t]['total_value']}")



    cache_path = f"source/year_data.json"
    with open(cache_path, 'w') as f:
        json.dump(main_data, f, indent=3)


if __name__ == "__main__":
    renew_all("MRT")