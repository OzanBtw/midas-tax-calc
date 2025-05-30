import pandas as pd
from tabula import read_pdf
from pdf_paths import get_paths
import os
from evds import evdsAPI
from datetime import date


def get_orders(path):
    i = 0
    orders = []
    while True:
        i += 1
        try:
            df = read_pdf(path,pages=i)
        except:
            break

        for t in df:
            if "YATIRIM İŞLEMLERİ" in t.columns[0]:
                orders.append(t)

    if len(orders) == 0:
        return pd.DataFrame()
    else:
        df_master = orders.pop(0)
        for o in orders:
            df_master = pd.concat([df_master, o], ignore_index=True)

    return df_master

def create_master_table():
    prefix_path = 'source/extracts/tables/'
    paths, startdate = get_paths()

    df_master = pd.read_csv(prefix_path+paths[0]+".csv", encoding="utf-8")
    paths.pop(0)
    
    for p in paths:
        df = pd.read_csv(prefix_path+p+".csv", encoding="utf-8")
        df_master = pd.concat([df_master, df], ignore_index=True)

    df_master = df_master.drop(columns=['Unnamed: 0'], errors='ignore')
    df_master = df_master.drop(columns=['Empty'], errors='ignore')
    df_master.to_csv(prefix_path+"Master_Ekstre.csv")


def renew_usd_yi_ufe(api_key):
    paths, startdate = get_paths()
    evds = evdsAPI(api_key)

    startdate = "01-01-"+str(int(startdate[3:])-3)
    today = f"{date.today().day}-{date.today().month}-{date.today().year}"

    usd_data = evds.get_data(['TP.DK.USD.A.YTL'], startdate=startdate, enddate=today)

    yi_ufe_data = evds.get_data(['TP.TUFE1YI.T1'], startdate=startdate, enddate=today)


    usd_data.to_csv('source/usd_data.csv')

    yi_ufe_data.to_csv('source/yi_ufe.csv')

    
def renew_pdf(api_key):
    #Getting Datas
    paths, startdate = get_paths()

    evds = evdsAPI(api_key)


    startdate = "01-01-"+str(int(startdate[3:])-3)
    today = f"{date.today().day}-{date.today().month}-{date.today().year}"

    usd_data = evds.get_data(['TP.DK.USD.A.YTL'], startdate=startdate, enddate=today)

    yi_ufe_data = evds.get_data(['TP.TUFE1YI.T1'], startdate=startdate, enddate=today)


    usd_data.to_csv('source/usd_data.csv')

    yi_ufe_data.to_csv('source/yi_ufe.csv')
    
    prefix1 = "source/extracts/pdf/"
    prefix2 = "source/extracts/tables/"

    if not os.path.isdir(prefix1):
        os.mkdir(prefix1)
        
    if not os.path.isdir(prefix2):
        os.mkdir(prefix2)
    else:
        for i in os.listdir(prefix2):
            file_path = os.path.join(prefix2, i)
            os.remove(file_path)

    #Getting tables
    for p in paths:
        path = f"{prefix1}{p}.pdf"
        path_save = f"{prefix2}{p}.csv"

        if os.path.isfile(path_save):
            continue
        else:

            df = get_orders(path)
            if df.empty:
                data = {"Date": [], 
                        "Order": [],
                        "Ticker": [],
                        "Order_Type": [],
                        "Status": [],
                        "Currency": [],
                        "Amount": [],
                        "Order_Price": [],
                        "Satisfied_Amount": [],
                        "Price": [],
                        "Fee": [],
                        "Return": [],
                        "Empty": []}
                df = pd.DataFrame(data)
                df = df.drop(columns=['Order', 'Amount','Order_Price','Fee'])
            else:
                df = df.dropna(axis=1, how='all')

                try:
                    names = ["Date", "Order","Ticker","Order_Type","Status","Currency","Amount","Order_Price","Satisfied_Amount","Price", "Fee", "Return", "Empty"]
                    df.columns = names[:len(df.columns)]
                    df = df.drop([0])
                    df = df.drop(columns=['Order', 'Amount','Order_Price'])

                except:
                    print(f"An error might be occured on {path}. Please check it!")
                    data = {"Date": [], 
                                        "Order": [],
                                        "Ticker": [],
                                        "Order_Type": [],
                                        "Status": [],
                                        "Currency": [],
                                        "Amount": [],
                                        "Order_Price": [],
                                        "Satisfied_Amount": [],
                                        "Price": [],
                                        "Fee": [],
                                        "Return": [],
                                        "Empty": []}
                    df = pd.DataFrame(data)
                    df = df.drop(columns=['Order', 'Amount','Order_Price'])
                    


            df.to_csv(path_save)
    
    create_master_table()


