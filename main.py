from tkinter import *
import customtkinter
import os
from evds import evdsAPI
from fifo import renew_all, get_d_price
from pdf import renew_pdf, renew_usd_yi_ufe
import json
import pandas
import datetime
import subprocess
import webbrowser
import threading
from graph import get_revenue_graph, get_ticker_graph
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FuncFormatter


class Loading_AnimationWindow(customtkinter.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.overrideredirect(True)
        self.center_over_parent()
        self.geometry("350x100")
        self.title("Renewing...")
        self.minsize(350, 100)
        self.grab_set()
        

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        progressbar = customtkinter.CTkProgressBar(
            master=self,
            width=250,
            height=40,
            border_width=5,
            corner_radius=10,
            mode="indeterminate")
        
        progressbar.grid(row=0, column=0)
        progressbar.start()
        self.attributes("-topmost", True)


    def center_over_parent(self):
        self.update_idletasks()  # Wait for window to render

        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()

        width = self.winfo_width()
        height = self.winfo_height()

        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)

        x = round(x * 0.8)
        y = round(y * 1.2)


        self.geometry(f"+{x}+{y}")

class HelpWindow(customtkinter.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.geometry("750x550")
        self.title("General Information")
        self.minsize(750, 550)
        
        text = """Welcome! Please review each item in the list below:

    • After adding a new PDF file, click the refresh button located at the bottom left. 
    To add new PDF files, simply drag them into the folder that opens when the 
    PDF Folder button is clicked.

    • For each year, Article 103 must be reviewed, and the tax settings updated accordingly. 
    Transfer the data from the article into the application.
    
    • The annual revenue of a ticker can be displayed as a graph by clicking on the ticker's name. 
    Both the ticker and annual revenue graphs are presented in logarithmic scale.

    • Regarding dividends: This application does not perform any calculations related to 
    dividends. Please use the Declaration System (Hazır Beyan Sistemi) to calculate the 
    tax applicable to your dividends. To calculate the dividend income from NASDAQ for the 
    relevant year, convert the NASDAQ dividends to Turkish Lira using the exchange rate from 
    the day prior to the dividend payment. After calculating the income from both NASDAQ and 
    BIST, refer to Article 86/d to determine the minimum income thresholds for tax applicability 
    on these dividends, respectively. If your income exceeds these thresholds, please submit 
    the relevant statements in the Declaration System."""

        text_font = customtkinter.CTkFont(family="Helvetica", size=18)
        self.text = customtkinter.CTkLabel(self, text=text, font=text_font)
        self.text.place(relx=0.5, rely=0.4, anchor=CENTER)
        
        link_font = customtkinter.CTkFont(family="Helvetica", size=18)
        self.link = customtkinter.CTkLabel(self, text="Declaration System Webstie", font=link_font, fg_color="transparent", text_color="blue", cursor="hand2",)
        self.link.place(relx=0.5, rely=0.8, anchor=CENTER)
        self.link.bind("<Button-1>", self.open_link)


        close_button = customtkinter.CTkButton(self, text="Close", width=70, command=self.close)
        close_button.place(relx=0.5, rely=0.94, anchor=CENTER)
    
    def close(self):
        
        self.destroy()
        self.update()

    def open_link(self, event=None):
        webbrowser.open("https://intvrg.gib.gov.tr/index_gmsi.jsp")

class TaxWindowFrame(customtkinter.CTkScrollableFrame):
    class data_103():
        def __init__(self, frame, r, data):
            validate_command = frame.register(self.validate_input)

            keys = list(data['103'].keys())

            tag_font = customtkinter.CTkFont(family="Helvetica", size=18)
            self.tag = customtkinter.CTkLabel(frame, text=str(r-4)+")", font=tag_font)
            self.tag.grid(row=r, column=1)

            self.entry_price = customtkinter.CTkEntry(frame, placeholder_text="", width=150)
            self.entry_price.grid(row=r, column=2, padx=(0,155), pady=5)
            self.entry_price.configure(validate="key", validatecommand=(validate_command, "%S"))
            x = "{:,}".format(int(keys[r-5]))
            self.entry_price.insert(0, x)


            self.entry_per = customtkinter.CTkEntry(frame, placeholder_text="", width=150)
            self.entry_per.grid(row=r, column=2, padx=(155,0), pady=5)
            self.entry_per.configure(validate="key", validatecommand=(validate_command, "%S"))
            x = "{:,}".format(int(data['103'][keys[r-5]]))
            self.entry_per.insert(0, x)

        def validate_input(self, char):
            if char.isdigit() or char in ["", ",", "."]:
                return True
            elif "." in char or "," in char:
                for i in char:
                    if i not in ["", ",", ".", "0", "1","2","3","4","5","6","7","8","9"]:
                        return False
                return True
            else:
                return False
        
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        tax_path = "source/tax_settings.json"
        with open(tax_path, 'r') as f:
            data = json.load(f)
            if master.master.current_year in data:
                data = data[master.master.current_year]
            else:
                data = data["Example"]
        self.grid_columnconfigure((1,2, 3), weight=1)
        #self.grid_rowconfigure((1,2,3,4,5,6,7,8), weight=1)

        validate_command = self.register(self.validate_input)

        title_font = customtkinter.CTkFont(family="Helvetica", size=15)

        
        self.ratio_price_per_tag = customtkinter.CTkLabel(self, text="Article 103\n\nPrice                                 %", font=title_font)
        self.ratio_price_per_tag.grid(row=3, column=2, pady=(30,5))


        ex_entry_price = customtkinter.CTkEntry(self, placeholder_text=f"EX: Until 100.000 TL", width=150)
        ex_entry_price.grid(row=4, column=2, padx=(0,155), pady=5)
        ex_entry_price.configure(state="disabled")

        ex_entry_per = customtkinter.CTkEntry(self, placeholder_text=f"EX: 10 %", width=150)
        ex_entry_per.grid(row=4, column=2, padx=(155,0), pady=5)
        ex_entry_per.configure(state="disabled")


        self.ratio_entries = []

        for r in range(5):
            self.ratio_entries.append(self.data_103(self, r+5, data))

    def validate_input(self, char):
        if char.isdigit() or char in ["", ",", "."]:
            return True
        elif "." in char or "," in char:
            for i in char:
                if i not in ["", ",", ".", "0", "1","2","3","4","5","6","7","8","9"]:
                    return False
            return True
        else:
            return False

class TaxWindow(customtkinter.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.geometry("550x750")
        self.title("Settings")
        self.minsize(550, 750)
        self.grab_set()
        
        self.title_var = StringVar()
        self.title_var.set(f"GVK for {self.master.current_year}")
        title_font = customtkinter.CTkFont(family="Helvetica", size=20, weight="bold")
        self.title = customtkinter.CTkLabel(self, textvariable=self.title_var, font=title_font)
        self.title.place(relx=0.5, rely=0.05, anchor=CENTER)

        self.tax_frame = TaxWindowFrame(master=self, width=400, height=580)
        self.tax_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        close_button = customtkinter.CTkButton(self, text="Save and Close", width=70, command=self.save_close)
        close_button.place(relx=0.5, rely=0.94, anchor=CENTER)
    
    def save_close(self):
        
        cache_data = {}
        for r in self.tax_frame.ratio_entries:
            a = str(r.entry_price.get())
            b = str(r.entry_per.get())

            a = a.replace(",", "").replace(".","")
            b = b.replace(",", "").replace(".","")

            if a == "" or b == "":
                return
            
            cache_data[int(a)] = int(b)
        
        
        tax_path = "source/tax_settings.json"
        with open(tax_path, 'r') as f:
            data = json.load(f)


        data[str(self.master.current_year)] = {"103": cache_data}
        with open(tax_path, 'w') as f:
            json.dump(data, f)

        self.destroy()
        self.update()

        self.master.tax_calculate()

class LeftAboveFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame, for example:
        self.label = customtkinter.CTkLabel(self, text="Years")
        self.label.grid(row=0, column=0, padx=35, pady=10)

class RevenueGraphWindow(customtkinter.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.geometry("750x550")
        self.title(f"Graph")
        self.minsize(750, 550)

        self.label = None
        
        text_color = 'white'

        time_line, revenues = get_revenue_graph(self.master.current_year)
        
        fig, ax = plt.subplots()
        linthresh = max(1, max(abs(min(revenues)), abs(max(revenues))) * 0.5)
        ax.set_yscale("symlog", linthresh=linthresh)
        ax.plot(time_line, revenues, color="#cccdcf", linewidth=2)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=8))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{x:,.0f}'))
        ax.set_xticks(time_line)

        ax.tick_params(axis='both', which='both', color="#cccdcf")

        
        plt.xlabel("Months", color=text_color)
        plt.ylabel("Revenue as ₺", color=text_color)
        plt.grid(True, color='#535559', linestyle='--')
        plt.title(f"Year {self.master.current_year} Revenue Graph", color=text_color)
        
        fig.patch.set_facecolor('#242424')   # Outside of plot area
        ax.set_facecolor('#2b2b2b')    
        
        for label in ax.get_xticklabels():
            label.set_color(text_color)

        for label in ax.get_yticklabels():
            label.set_color(text_color)

        for spine in ax.spines.values():
            spine.set_edgecolor("#cccdcf")
        


        fig.tight_layout()
        temp_file = "source/cache/temp_plot.png"
        fig.savefig(temp_file)
        plt.close(fig)
        
        # Display the image
        if self.label:
            self.label.destroy()

        img = customtkinter.CTkImage(light_image=Image.open(temp_file),
                                    dark_image=Image.open(temp_file),
                                    size=(750, 550))

        self.label = customtkinter.CTkLabel(self, image=img, text="")
        self.label.pack()


class TickerGraphWindow(customtkinter.CTkToplevel):
    def __init__(self, master, year, ticker, **kwargs):
        super().__init__(master, **kwargs)
        self.geometry("750x550")
        self.title(f"Ticker Graph")
        self.minsize(750, 550)

        self.label = None
        
        text_color = 'white'

        time_line, revenues = get_ticker_graph(year, ticker)
        
        fig, ax = plt.subplots()
        linthresh = max(1, max(abs(min(revenues)), abs(max(revenues))) * 0.5)
        ax.set_yscale("symlog", linthresh=linthresh)
        ax.plot(time_line, revenues, color="#cccdcf", linewidth=2)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=8))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{x:,.0f}'))
        ax.set_xticks(time_line)

        ax.tick_params(axis='both', which='both', color="#cccdcf")

        
        plt.xlabel("Months", color=text_color)
        plt.ylabel("Revenue as ₺", color=text_color)
        plt.grid(True, color='#535559', linestyle='--')
        plt.title(f"Year {self.master.current_year} {ticker} Revenue Graph", color=text_color)
        
        fig.patch.set_facecolor('#242424')   # Outside of plot area
        ax.set_facecolor('#2b2b2b')    
        
        for label in ax.get_xticklabels():
            label.set_color(text_color)

        for label in ax.get_yticklabels():
            label.set_color(text_color)

        for spine in ax.spines.values():
            spine.set_edgecolor("#cccdcf")
        

        fig.tight_layout()
        temp_file = "source/cache/temp_ticker_plot.png"
        fig.savefig(temp_file)
        plt.close(fig)
        
        # Display the image
        if self.label:
            self.label.destroy()

        img = customtkinter.CTkImage(light_image=Image.open(temp_file),
                                    dark_image=Image.open(temp_file),
                                    size=(750, 550))

        self.label = customtkinter.CTkLabel(self, image=img, text="")
        self.label.pack()



class LeftBelowFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame, for example:
        self.renew = customtkinter.CTkButton(self, text="Renew", width=70, command=master.renew_data)
        self.renew.grid(row=0, column=0, padx=15, pady=10)

class LeftFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.buttons = []
    
    def reload_buttons(self, master):
        for b in self.buttons:
            b.grid_forget()

        years = list(master.year_data.keys())
        years.reverse()

        count = 0
        for b in years:

            button = customtkinter.CTkButton(self, text=str(b), width=70, command=lambda b=b: master.show_year(b))
            if count == 0:
                y = 20
            else:
                y = 10
            count += 1
            button.grid(row=count, column=0, padx=15, pady=(y, 5))
            self.buttons.append(button)


        master.show_year(years[0])

class InsideBelowFrame(customtkinter.CTkScrollableFrame):
    class tickers():
        def __init__(self, master, data, name, r, year, status):
            #command=lambda b=b: master.ticker_graph_window_call(b)
            ticker_name_font = customtkinter.CTkFont(family="Helvetica", size=18, underline=True)
            #self.ticker_name = customtkinter.CTkLabel(master, text=f"{name}:", font=ticker_name_font)
            "{:,.2f}".format(float(data['current_value'] - data['total_value']))
            value = "{:,.2f}".format(float(data['revenue']))
            if status: #Active
                self.status_symbol = customtkinter.CTkLabel(master, text=f"🟢")
                unrealised_income = float(data['current_value'] - data['total_value'])
            else:
                self.status_symbol = customtkinter.CTkLabel(master, text=f"🔴")
                unrealised_income = 0

            if int(year) == datetime.date.today().year:
                self.status_symbol.grid(row=r, column=0, padx=(10, 0))
                pad_val = 15
            else:
                pad_val = 100
            

            self.ticker_name = customtkinter.CTkButton(master, text=f"{name}", width=12, font=ticker_name_font, fg_color="transparent", hover_color="#242424", command=lambda name=name: master.ticker_graph_window_call(year ,name))
            self.ticker_name.grid(row=r, column=1, padx=(pad_val, 10))
            
            
            if float(data['revenue']) > 0:
                color = "#44ff00"
            else:
                color = "#ff000d"
            ticker_value_font = customtkinter.CTkFont(family="Helvetica", size=18)

            self.ticker_value = customtkinter.CTkLabel(master, text=f"{value} ₺", font=ticker_value_font, text_color=color)
            self.ticker_value.grid(row=r, column=2, padx=0)

            if float(unrealised_income) > 0:
                color = "#44ff00"
            else:
                color = "#ff000d"
                
            
            self.ticker_unrealised = customtkinter.CTkLabel(master, text=f"  +  {'{:,.2f}'.format(unrealised_income)} ₺", font=ticker_value_font, text_color=color)
            if status and int(year) == datetime.date.today().year:
                self.ticker_unrealised.grid(row=r, column=3, padx=0)

        def remove(self):
            self.status_symbol.grid_forget()
            self.ticker_name.grid_forget()
            self.ticker_value.grid_forget()
            self.ticker_unrealised.grid_forget()

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.ticker_list = []

        self.ticker_graph_window = None

    def update(self, year):

        self.ticker_datas = self.master.year_data[year]['months'][-1]


        for t in self.ticker_list:
            t.remove()

        self.ticker_list = []

        r = 0
        for t in self.ticker_datas:
            if self.ticker_datas[t]['revenue'] != 0:
                if len(self.ticker_datas[t]['amount']) > 0:
                    status = True
                else:
                    status = False
                self.ticker_list.append(self.tickers(self, self.ticker_datas[t], t, r, year, status))
                r += 1

    def ticker_graph_window_call(self, year, ticker):
        if self.ticker_graph_window is None or not self.ticker_graph_window.winfo_exists():
            self.ticker_graph_window = TickerGraphWindow(self.master, year, ticker)  # create window if its None or destroyed
        else:
            self.ticker_graph_window.destroy()
            self.ticker_graph_window = TickerGraphWindow(self.master, year, ticker)

class InsideFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        self.title_var = StringVar()
        self.title_var.set("Revenue of")
        title_font = customtkinter.CTkFont(family="Helvetica", size=20, weight="bold")
        self.title = customtkinter.CTkLabel(self, textvariable=self.title_var, font=title_font)
        self.title.place(relx=0.5, rely=0.1, anchor=CENTER)

        self.price_var = StringVar()
        self.price_var.set("-")
        tl_font = customtkinter.CTkFont(family="Helvetica", size=40)
        self.price = customtkinter.CTkLabel(self, textvariable=self.price_var, font=tl_font)
        self.price.place(relx=0.5, rely=0.5, anchor=CENTER)

        #Total Tax Text
        self.tax_text_var = StringVar()

        tax_font = customtkinter.CTkFont(family="Helvetica", size=18, slant='roman')
        self.tax_text = customtkinter.CTkLabel(self, textvariable=self.tax_text_var, font=tax_font)
        self.tax_text.place(relx=0.5, rely=0.85, anchor=CENTER)


    
    def update(self, year, dolar):
        revenue = self.master.year_data[year]['total_revenue']
        revenue_d = revenue / dolar

        revenue = "{:,.2f}".format(revenue)
        revenue_d = "{:,.2f}".format(revenue_d)
        self.title_var.set(f"Revenue of {year}")
        self.price_var.set(f"{revenue} ₺\n{revenue_d} $")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        no_pdf(self)

        self.title("Midas Tax Calculator")
        self.geometry("1000x700")
        self.minsize(1000, 700)
        
        icon_image = Image.open("source/logo.png")
        icon_photo = ImageTk.PhotoImage(icon_image)
        self.iconphoto(True, icon_photo)


        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure((1,2,3), weight=1)
        self.grid_rowconfigure(0, weight=0)  # configure grid system
        self.grid_rowconfigure((1,2,3), weight=1)  # configure grid system
        self.grid_rowconfigure((4), weight=0)  # configure grid system

        self.inside_frame = InsideFrame(master=self, height=400)
        self.inside_frame.grid(row=1, column=2, sticky="nsew", padx=(0,0))


        self.left_above_frame = LeftAboveFrame(master=self, width=100, corner_radius=0, fg_color="#333333")
        self.left_above_frame.grid(row=0, column=0, sticky="nsew")
        
        self.left_frame = LeftFrame(master=self, width=100, corner_radius=0)
        self.left_frame.grid(row=1, column=0, rowspan=3, sticky="nsew")

        
        self.inside_below_frame = InsideBelowFrame(master=self, width=200, height=450)
        self.inside_below_frame.grid(row=3, column=2, sticky="nsew", pady=50)

        #self.graph_frame = GraphFrame(master=self, width=170, height=200)
        #self.graph_frame.grid(row=3, column=3, sticky="nsew", padx=10, pady=80)


        self.api_key = str(api_request())
        
        renew_usd_yi_ufe(self.api_key)
        
        #renew_pdf(self.api_key)
        #renew_all()
        #self.load_data()

        self.left_below_frame = LeftBelowFrame(master=self, width=100, corner_radius=0, fg_color="#333333")
        self.left_below_frame.grid(row=4, column=0, sticky="nsew")
        
        self.start_load_data()

        pdf_button = customtkinter.CTkButton(self, text="PDF Folder", width=12, command=self.open_pdf_folder)
        pdf_button.grid(row=1, column=4, padx=(0,10), pady=0)

        tax_options_button = customtkinter.CTkButton(self, text="Tax Settings", width=12, command=self.tax_options_call)
        tax_options_button.grid(row=0, column=4, padx=(0, 10), pady=10)

        graph_button = customtkinter.CTkButton(self, text="Revenue Graph", width=12, command=self.revenue_graph_window_call)
        graph_button.grid(row=3, column=4, padx=(0, 10), pady=10)
        
        help_button = customtkinter.CTkButton(self, text="Help", width=12, command=self.help_call)
        help_button.grid(row=4, column=4, padx=(0, 10), pady=10)

        self.help_window = None
        self.revenue_graph_window = None
        self.tax_window = None

        #Request Api key if no api key
        


    def open_pdf_folder(self):
        folder_path = os.path.join(os.getcwd(), "source", "extracts", "pdf")

        try:
            subprocess.Popen(["open", folder_path])
        except:
            subprocess.Popen(f'explorer "{folder_path}"')

    def tax_calculate(self):
        tax_path = "source/tax_settings.json"
        with open(tax_path, 'r') as f:
            data = json.load(f)
        
        if self.current_year not in data.keys():
            self.inside_frame.tax_text_var.set("Please update your Tax Settings!")
            return
        
        data = data[self.current_year]
        revenue = self.year_data[self.current_year]['total_revenue']

        

        total_tax = 0
        l = list(data["103"].keys())
        l.insert(0,0)

        for i in range(1, len(l)):

            if i == 5:
                total_tax += (revenue - float(l[i-1])) * data["103"][l[i]] / 100
                break
            
            if revenue <= float(l[i]):
                total_tax += (revenue - float(l[i-1])) * data["103"][l[i]] / 100
                break
            
            total_tax += (float(l[i]) - float(l[i-1])) * data["103"][l[i]] / 100
        if total_tax > 0:
            total_tax = "{:,.2f}".format(total_tax)
        else:
            total_tax = "{:,.2f}".format(0)
        self.inside_frame.tax_text_var.set(f"Total Tax Due: {total_tax} ₺")


    def load_data(self):
        if not os.path.isfile('source/year_data.json'):
            renew_pdf(self.api_key)
            renew_all()

        with open('source/year_data.json', 'r') as f:
            self.year_data = json.load(f)
        self.usd_df = pandas.read_csv('source/usd_data.csv')
        

        self.left_frame.reload_buttons(self)


    def renew_data_thread(self):
        renew_pdf(self.api_key)
        renew_all()
        self.load_data()
        self.animation_window.destroy()
        self.left_below_frame.renew.configure(state="normal")

    def renew_data(self):
        self.left_below_frame.renew.configure(state="disabled")
        self.animation_window = Loading_AnimationWindow(self)
        threading.Thread(target=self.renew_data_thread, daemon=True).start()

    def start_load_thread(self):
        self.load_data()
        self.animation_window.destroy()
        self.left_below_frame.renew.configure(state="normal")

    def start_load_data(self):
        self.left_below_frame.renew.configure(state="disabled")
        self.animation_window = Loading_AnimationWindow(self)
        threading.Thread(target=self.start_load_thread, daemon=True).start()

    def tax_options_call(self):
        if self.tax_window is None or not self.tax_window.winfo_exists():
            self.tax_window = TaxWindow(self)  # create window if its None or destroyed
        else:
            self.tax_window.focus()

    def revenue_graph_window_call(self):
        if self.revenue_graph_window is None or not self.revenue_graph_window.winfo_exists():
            self.revenue_graph_window = RevenueGraphWindow(self)  # create window if its None or destroyed
        else:
            self.revenue_graph_window.focus()



    def help_call(self):
        if self.help_window is None or not self.help_window.winfo_exists():
            self.help_window = HelpWindow(self)  # create window if its None or destroyed
        else:
            self.help_window.focus()

    def show_year(self, year):
        date = datetime.datetime.today()
        date = f"{date.day:02d}-{date.month:02d}-{date.year}"
        dolar = get_d_price(date, self.usd_df)
        
        self.current_year = year

        self.inside_frame.update(year, dolar)
        self.inside_below_frame.update(year)
        #self.graph_frame.update(year)
        self.tax_calculate()



def check_api():
    api_path = "source/api.txt"
    if os.path.isfile(api_path):
        with open(api_path, 'r') as f:
            api_key = f.read()
        try:
            evds = evdsAPI(api_key)
            return True
        except:
            return False
    else:
        return False


def no_pdf(master):
    path = 'source/extracts/pdf'
    if not os.path.isdir('source/extracts'):
        os.mkdir('source/extracts')

    if not os.path.isdir(path):
        os.mkdir('source/extracts/pdf')
        master.open_pdf_folder()

        text = "It seems that pdf folder is empty. Please make sure to put all required pdf files!"
        dialog = customtkinter.CTkInputDialog(text=text, title="PDF Files")
        dialog.grab_set()
        dialog.get_input()

        no_pdf(master)

    elif len(os.listdir(path)) == 0:
        master.open_pdf_folder()

        text = "It seems that pdf folder is empty. Please make sure to put all required pdf files!"
        dialog = customtkinter.CTkInputDialog(text=text, title="PDF Files")
        dialog.grab_set()
        dialog.get_input()

        no_pdf(master)


def api_request():
    if not check_api():
        text = "Please enter your API key from evds2:"
        dialog = customtkinter.CTkInputDialog(text=text, title="API Key")
        dialog.grab_set()
        api_key = dialog.get_input()

        try:
            evds = evdsAPI(api_key)
            api_path = "source/api.txt"
            with open(api_path, 'w') as f:
                f.write(api_key)
            return api_key
        
        except:
            api_request()

    else:
        api_path = "source/api.txt"
        if os.path.isfile(api_path):
            with open(api_path, 'r') as f:
                api_key = f.read()
                return api_key


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")





#button = customtkinter.CTkButton(master=root, text="Hello World!")
#button.place(relx=0.5, rely=0.5, anchor=CENTER)



tax_path = "source/tax_settings.json"

if os.path.isfile(tax_path):
    with open(tax_path, 'r') as f:
        tax_cache_data = json.load(f)

    if "Example" not in tax_cache_data.keys():

        tax_cache_data = {"Example": {"103": {"110000": 15, "230000": 20, "580000": 27, "3000000": 35, "0": 40}}}
        with open(tax_path, 'w') as f:
            json.dump(tax_cache_data, f)
else:
    with open(tax_path, 'w') as f:
        tax_cache_data = {"Example": {"103": {"110000": 15, "230000": 20, "580000": 27, "3000000": 35, "0": 40}}}
        json.dump(tax_cache_data, f)

app = App()
app.mainloop()



