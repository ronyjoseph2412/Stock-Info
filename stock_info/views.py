from ast import Return
from distutils.log import error
from django.shortcuts import redirect, render,HttpResponseRedirect
import requests
from django.urls import reverse
import json
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date
# Create your views here.
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
def base(request):
    return render(request,'base.html')

def index(request):
    if(request.method=="POST"):
        stock_symbol = request.POST.get('stock_symbol')
        stock_symbol=((stock_symbol.split("(")[1]).split(":"))[1].replace(")","")
        return HttpResponseRedirect(reverse('stock', args=[stock_symbol]))
    nifty_50=nifty_50_details()
    nifty_auto=nifty_auto_function()
    nifty_bank=nifty_bank_function()
    nifty_fmcg=nifty_fmcg_function()
    nifty_it=nifty_it_function()
    stock_name,current,previous_close,per_change=top_gainers()
    worst_stock_name,worst_current,worst_previous_close,worst_per_change=worst_gainers()
    return render(request,'index.html',{"nifty_50":nifty_50,"nifty_auto":nifty_auto,"nifty_bank":nifty_bank,"nifty_fmcg":nifty_fmcg,"nifty_it":nifty_it,'top_stocks':stock_name,'top_previous':current,'top_current':previous_close,'top_change':per_change,'worst_stocks':worst_stock_name,'worst_previous':worst_current,'worst_current':worst_previous_close,'worst_change':worst_per_change})

def nse(request):
    index_name,previous_close,current,change,per_change=nse_indices()
    return render(request,'nse.html',{'index_name':index_name,'previous_close':previous_close,'current':current,'change':change,'per_change':per_change})

def stock(request,id):
    list_details=company_details(id)
    stock_performance=stock_details(list_details['symbol'])
    list_details["name"]=list_details["name"].replace("Limited","Ltd")
    stock_code=list_details['symbol']+"EQN"
    ID = Intra_Day(stock_code)
    timeStamp, dataPoints = ID.intraDay()
    time=[]
    data=[]
    time_small=[]
    data_small=[]
    for i in range(len(timeStamp)):
        if(i%5==0):
            time_stamp=str(timeStamp[i])
            time_stamp=time_stamp.split(" ")[1]
            time.append(time_stamp)
        if(i%10==0):
            time_stamp=str(timeStamp[i])
            time_stamp=time_stamp.split(" ")[1]
            time_small.append(time_stamp)
    for i in range(len(dataPoints)):
        if(i%5==0):
            data.append(dataPoints[i])
        if(i%10==0):
            data_small.append(dataPoints[i])
    chart={}
    color_decidor =str(stock_performance["per_change"])
    if(color_decidor.replace(""," ").split(" ")[1]=="-"):
        chart["background"]='rgba(252, 232, 230, 1)'
        chart["border"]="rgba(165, 14, 14, 1)"
    else:
        chart["background"]='rgba(230, 244, 234, 1)'
        chart["border"]="rgba(19, 115, 51, 1)"
    return render(request,'stock.html',{'data':list_details,'stock':stock_performance,'points':data,'timestamp':time,'points_small':data_small,'timestamp_small':time_small,'chart':chart})

def indices(request,id):
    details={}
    index_name,previous_close,current,change,per_change=nse_indices()
    for i in range(len(index_name)):
        if(index_name[i]==id):
            details['name']=index_name[i]
            break
    details['price']=previous_close[i]
    details['current']=current[i]
    details['change']=change[i]
    details['per_change']=per_change[i]
    color_decidor =str(details["per_change"])
    chart={}
    if(color_decidor.replace(""," ").split(" ")[1]=="-"):
        details["background"]='#fce8e6'
        details["text"]="#a50e0e"
        chart["background"]='rgba(252, 232, 230, 1)'
        chart["border"]="rgba(165, 14, 14, 1)"
    else:
        details["background"]='#e6f4ea'
        details["text"]="#137333"
        chart["background"]='rgba(230, 244, 234, 1)'
        chart["border"]="rgba(19, 115, 51, 1)"
    details["date"],details["time"]=nse_time()
    index_details=nse_all_indices(details['name'])
    ID = Intra_Day(details['name'])
    timeStamp, dataPoints = ID.nifty_intraDay()
    time=[]
    data=[]
    time_small=[]
    data_small=[]
    for i in range(len(timeStamp)):
        if(i%5==0):
            time_stamp=str(timeStamp[i])
            time_stamp=time_stamp.split(" ")[1]
            time.append(time_stamp)
        if(i%10==0):
            time_stamp=str(timeStamp[i])
            time_stamp=time_stamp.split(" ")[1]
            time_small.append(time_stamp)
    for i in range(len(dataPoints)):
        if(i%5==0):
            data.append(dataPoints[i])
        if(i%10==0):
            data_small.append(dataPoints[i])
    
    return render(request,'indices.html',{'details':details,'index_details':index_details,'points':data,'timestamp':time,'points_small':data_small,'timestamp_small':time_small,'chart':chart})

def news(request):
    local_news=news_api()
    world_news=news_world()
    return render(request,'news.html',{"local":local_news,"world":world_news})

def nifty_50_details():
    stock_url  = "https://www.nseindia.com/"
    response = requests.get(stock_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    nifty_50={}
    nifty_50["price"] = soup.find("span",class_='val').get_text().split("\n")[0]
    nifty_50["open"] = soup.find("span",class_='openVal').get_text()
    nifty_50["high"] = soup.find("span",class_='highVal').get_text()
    nifty_50["low"] = soup.find("span",class_='lowVal').get_text()
    date_time=(soup.find("div",class_='tabTimeVal').get_text().split("Updated:")[1]).split(" ")
    nifty_50["time"]=date_time[2] +" "+date_time[3]
    nifty_50["date"] =date_time[1]
    nifty_50["change"] = soup.find("span",class_='val_per').get_text().split(" ")[0]
    nifty_50["per_change"] = (((soup.find("span",class_='val_per').get_text().split(" ")[1]).split("(")[1]).split(")")[0])
    color_decidor =nifty_50["per_change"]
    if(color_decidor.replace(""," ").split(" ")[1]=="-"):
        nifty_50["background"]='#fce8e6'
        nifty_50["text"]="#a50e0e"
    else:
        nifty_50["background"]='#e6f4ea'
        nifty_50["text"]="#137333"
    return(nifty_50)

def nifty_it_function():
    nse_url = ('https://www.nseindia.com/api/allIndices')
    response = requests.get(nse_url, headers=headers)
    nifty_it={}
    if(response.status_code==200):
        x=response.json()
        for i in range(len(x['data'])):
            if (x['data'][i]['index']=="NIFTY IT"):
                nifty_it['price']=x['data'][i]['last']
                nifty_it['change']=x['data'][i]['variation']
                nifty_it['per_change']=x['data'][i]['percentChange']
                color_decidor =str(nifty_it["per_change"])
                if(color_decidor.replace(""," ").split(" ")[1]=="-"):
                    nifty_it["background"]='#fce8e6'
                    nifty_it["text"]="#a50e0e"
                else:
                    nifty_it["background"]='#e6f4ea'
                    nifty_it["text"]="#137333"
    return(nifty_it)
def nifty_auto_function():
    nse_url = ('https://www.nseindia.com/api/allIndices')
    response = requests.get(nse_url, headers=headers)
    nifty_it={}
    if(response.status_code==200):
        x=response.json()
        for i in range(len(x['data'])):
            if (x['data'][i]['index']=="NIFTY AUTO"):
                nifty_it['price']=x['data'][i]['last']
                nifty_it['change']=x['data'][i]['variation']
                nifty_it['per_change']=x['data'][i]['percentChange']
                color_decidor =str(nifty_it["per_change"])
                if(color_decidor.replace(""," ").split(" ")[1]=="-"):
                    nifty_it["background"]='#fce8e6'
                    nifty_it["text"]="#a50e0e"
                else:
                    nifty_it["background"]='#e6f4ea'
                    nifty_it["text"]="#137333"
    return(nifty_it)
def nifty_bank_function():
    nse_url = ('https://www.nseindia.com/api/allIndices')
    response = requests.get(nse_url, headers=headers)
    
    nifty_it={}
    if(response.status_code==200):
        x=response.json()
        for i in range(len(x['data'])):
            if (x['data'][i]['index']=="NIFTY BANK"):
                nifty_it['price']=x['data'][i]['last']
                nifty_it['change']=x['data'][i]['variation']
                nifty_it['per_change']=x['data'][i]['percentChange']
                color_decidor =str(nifty_it["per_change"])
                if(color_decidor.replace(""," ").split(" ")[1]=="-"):
                    nifty_it["background"]='#fce8e6'
                    nifty_it["text"]="#a50e0e"
                else:
                    nifty_it["background"]='#e6f4ea'
                    nifty_it["text"]="#137333"
    return(nifty_it)
def nifty_fmcg_function():
    nse_url = ('https://www.nseindia.com/api/allIndices')
    response = requests.get(nse_url, headers=headers)
    nifty_it={}
    if(response.status_code==200):
        x=response.json()
        for i in range(len(x['data'])):
            if (x['data'][i]['index']=="NIFTY FMCG"):
                nifty_it['price']=x['data'][i]['last']
                nifty_it['change']=x['data'][i]['variation']
                nifty_it['per_change']=x['data'][i]['percentChange']
                color_decidor =str(nifty_it["per_change"])
                if(color_decidor.replace(""," ").split(" ")[1]=="-"):
                    nifty_it["background"]='#fce8e6'
                    nifty_it["text"]="#a50e0e"
                else:
                    nifty_it["background"]='#e6f4ea'
                    nifty_it["text"]="#137333"
    return(nifty_it)





def company_details(id):
    data = pd.read_csv(r"T:\Django\Stock_Market\Full Project\stock_market\static\NSE_LIST.csv")
    df = data
    symbol = df["SYMBOL"].tolist()
    company=df["NAME OF COMPANY"].tolist()
    date_of_listing=df[" DATE OF LISTING"].tolist()
    isin=df[" ISIN NUMBER"].tolist()
    series= df[" SERIES"].tolist()
    list_of_details={}
    for i in range(len(symbol)):
        list_of_details[symbol[i]]={"symbol":symbol[i],"name":company[i],"date":date_of_listing[i],"isin":isin[i],"series":series[i]}
    return(list_of_details[str(id)])

def stock_details(stock):
    stock_current={}
    stockcode=str(stock)
    stock_url  = 'https://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuote.jsp?symbol='+str(stockcode)
    response = requests.get(stock_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    data_array = soup.find(id='responseDiv').getText().strip().split(":")        
# Last Price        
    for item in data_array:
        if 'lastPrice' in item:
            index = data_array.index(item)+1
            latestPrice=data_array[index].split('"')[1]
            stock_current["price"]=latestPrice
        

# Change
    for item in data_array:
        if 'change' in item:
            index = data_array.index(item)+1
            latestPrice=data_array[index].split('"')[1]
            stock_current["change"]=latestPrice

            
# Change Percentage        
    for item in data_array:
        if 'pChange' in item:
            index = data_array.index(item)+1
            latestPrice=data_array[index].split('"')[1]
            stock_current["per_change"]=latestPrice
        
        
# Previous Close
    for item in data_array:
        if 'previousClose' in item:
            index = data_array.index(item)+1
            latestPrice=data_array[index].split('"')[1]
            if(latestPrice==""):
                stock_current["close"]="-"
            else:
                stock_current["close"]=latestPrice
        
# Day High
    for item in data_array:
        if 'dayHigh' in item:
            index = data_array.index(item)+1
            latestPrice=data_array[index].split('"')[1]
            stock_current["high"]=latestPrice
        
        
# Day Low

    for item in data_array:
        if 'dayLow' in item:
            index = data_array.index(item)+1
            latestPrice=data_array[index].split('"')[1]
            stock_current["low"]=latestPrice
        
        
        
# Average Price {VWAP}
    for item in data_array:
        if 'averagePrice' in item:
            index = data_array.index(item)+1
            latestPrice=data_array[index].split('"')[1]
            stock_current["average"]=latestPrice
        
        
# 52 -High        
        
    for item in data_array:
        if 'high52' in item:
            index = data_array.index(item)+1
            latestPrice=data_array[index].split('"')[1]
            stock_current["52high"]=latestPrice
        
# 52-Low  
    for item in data_array:
        if 'low52' in item:
            index = data_array.index(item)+1
            latestPrice=data_array[index].split('"')[1]
            stock_current["52low"]=latestPrice      
        
        
# Last Updated Time        
        
    for item in data_array:
        if 'lastUpdateTime' in item:
            index = data_array.index(item)+1
            latestPrice=((data_array[index]+":"+data_array[index+1]).split('"')[1]).split(" ")
            stock_current["date"]=latestPrice[0]  
            stock_current["time"]=latestPrice[1].replace(" ","")  
    
    
# Traded Value (Lacs)
    for item in data_array:
        if 'totalTradedValue' in item:
            index = data_array.index(item)+1
            latestPrice=(data_array[index].split('"')[1]).split(",")
            Price=""
            for i in range(len(latestPrice)):
                Price+=latestPrice[i]
            price=float(Price)
            price=(round(price/10000,2))
            price=str(price)+" B"
            stock_current["traded"]=price
        
# Dividend Price            
    for item in data_array:
        if 'DIVIDEND' in item:
            index = data_array.index(item)
            latestPrice=(((((data_array[index].split(",")[0]).strip().split("-")[1]).split('"')[0]).replace("RS","")).replace("PER SHARE","")).replace(" ","")
            stock_current["dividend"]=latestPrice
            break
        else:
            stock_current["dividend"]="-"
    sector_url  = 'https://www1.nseindia.com//live_market/dynaContent/live_watch/get_quote/getPEDetails.jsp?symbol='+str(stockcode)
    response = requests.get(sector_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    data_array=soup.get_text().strip().split(":")
    if(data_array[0]=="null"):
        stock_current["pe"]="-"
    else:
        for item in data_array:
            if 'PE' in item:
                index = data_array.index(item)+1

                latestPrice=data_array[index].split('"')[1]
                stock_current["pe"]=latestPrice
    color_decidor =str(stock_current["per_change"])
    if(color_decidor.replace(""," ").split(" ")[1]=="-"):
        stock_current["background"]='#fce8e6'
        stock_current["text"]="#a50e0e"
    else:
        stock_current["background"]='#e6f4ea'
        stock_current["text"]="#137333"
            
    return(stock_current)


def nse_indices():
    nse_url  = 'https://money.rediff.com/indices/nse'
    response = requests.get(nse_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    data_array = soup.find(id='dataTable').getText().replace("\n",",").split(",")
    index_name=[]
    previous_close=[]
    current=[]
    change=[]
    per_change=[]
    for item in data_array:
        if 'NIFTY' in item:
            index = data_array.index(item)
            index_name.append((data_array[index]))
            previous_close.append(data_array[index+2])
            current.append(data_array[index+3])
            change.append(data_array[index+4])
            per_change.append(data_array[index+5])
    
    return(index_name,previous_close,current,change,per_change)

def nse_all_indices(index_name):
    nse_url = ('https://www.nseindia.com/api/allIndices')
    response = requests.get(nse_url, headers=headers)
    nifty_it={}
    if(response.status_code==200):
        x=response.json()
        for i in range(len(x['data'])):
            if (x['data'][i]['index']==index_name):
                nifty_it['close']=x['data'][i]['previousClose']
                nifty_it['52high']=x['data'][i]['yearHigh']
                nifty_it['52low']=x['data'][i]['yearLow']
                nifty_it['low']=x['data'][i]['low']
                nifty_it['high']=x['data'][i]['high']
    else:
        print("No data")
    return(nifty_it)

def nse_time():
    todays_date = date.today()
    nse_url  = 'https://money.rediff.com/indices/nse'
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
    response = requests.get(nse_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    data_array = soup.find('span',class_='floatR').getText().split("updated:")
    data_array=(data_array[1].split(","))
    data_array[0]=data_array[0]+" "+str(todays_date.year)
    date_now = data_array[0]
    time=data_array[1]
    return(date_now,time)


def top_gainers():
    nse_url  = 'https://money.rediff.com/gainers/nse/daily/nifty'
    response = requests.get(nse_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    data_array= soup.find_all('td')
    gainers_stocks=[]
    stock_name=[]
    current=[]
    previous_close=[]
    per_change=[]
    for i in range(len(data_array)):
        if(data_array[i].getText()=="Stocks"):
            break
        else:
            gainers_stocks.append(data_array[i].getText())
    for i in range(len(gainers_stocks)):
        if(i%4==0):
            gainers_stocks[i]=gainers_stocks[i].replace("\n","")
            gainers_stocks[i]=gainers_stocks[i].replace("\t","")
        else:
            gainers_stocks[i]=gainers_stocks[i].replace(" ","")
    for i in range(len(gainers_stocks)):
        if(i%4==0):
            stock_name.append(gainers_stocks[i])
            current.append(gainers_stocks[i+1])
            previous_close.append(gainers_stocks[i+2])
            per_change.append(gainers_stocks[i+3])
        
    return(stock_name,current,previous_close,per_change)
def worst_gainers():
    nse_url  = 'https://money.rediff.com/losers/nse/daily/nifty'
    response = requests.get(nse_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    data_array= soup.find_all('td')
    gainers_stocks=[]
    stock_name=[]
    current=[]
    previous_close=[]
    per_change=[]
    for i in range(len(data_array)):
        if(data_array[i].getText()=="Stocks"):
            break
        else:
            gainers_stocks.append(data_array[i].getText())
    for i in range(len(gainers_stocks)):
        if(i%4==0):
            gainers_stocks[i]=gainers_stocks[i].replace("\n","")
            gainers_stocks[i]=gainers_stocks[i].replace("\t","")
        else:
            gainers_stocks[i]=gainers_stocks[i].replace(" ","")
    for i in range(len(gainers_stocks)):
        if(i%4==0):
            stock_name.append(gainers_stocks[i])
            current.append(gainers_stocks[i+1])
            previous_close.append(gainers_stocks[i+2])
            per_change.append(gainers_stocks[i+3])
        
    return(stock_name,current,previous_close,per_change)


def news_api():
# Making a get request
    response = requests.get('https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=7765ca30f37345ae9dcae2f9c57b6d18')
    news={"author_name":[],"title":[],"url":[],"img":[],"time":[]}
    if(response.status_code==200):
        x=response.json()
        for i in range(len(x["articles"])):
            news["author_name"].append(x["articles"][i]["source"]["name"])
            news["title"].append(x["articles"][i]["title"])
            news["url"].append(x["articles"][i]["url"])
            news["img"].append(x["articles"][i]["urlToImage"])
            news["time"].append(((x["articles"][i]["publishedAt"].split("T"))[1]).split(":")[0]+":"+((x["articles"][i]["publishedAt"].split("T"))[1]).split(":")[1])
    return(news)

def news_world():
    country_code=["us","au","ca",'nz','gb','sg']
    world_news={"us":{"author":"","title":"","url":"","image":"","time":""},"au":{"author":"","title":"","url":"","image":"","time":""},"ca":{"author":"","title":"","url":"","image":"","time":""},"nz":{"author":"","title":"","url":"","image":"","time":""},"sg":{"author":"","title":"","url":"","image":"","time":""},"gb":{"author":"","title":"","url":"","image":"","time":""}}
    for i in range(len(country_code)):
        news_url="https://newsapi.org/v2/top-headlines?country="+str(country_code[i])+"&category=business&language=en&apiKey=7765ca30f37345ae9dcae2f9c57b6d18"
        response = requests.get(news_url)
        x=response.json()
        if(x["totalResults"]>0):
            world_news[country_code[i]]["author"]=x["articles"][0]["source"]["name"]
            world_news[country_code[i]]["title"]=x["articles"][0]["title"]
            world_news[country_code[i]]["url"]=x["articles"][0]["url"]
            world_news[country_code[i]]["image"]=x["articles"][0]["urlToImage"]
            try:
                world_news[country_code[i]]["time"]=(((x["articles"][0]["publishedAt"].split("T"))[1]).split(":")[0]+":"+((x["articles"][i]["publishedAt"].split("T"))[1]).split(":")[1])
            except:
                print("Error")
                world_news[country_code[i]]["time"]=""
                
    return(world_news)


from datetime import datetime
import requests

head = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/87.0.4280.88 Safari/537.36 "
}


class Intra_Day:
    baseNumber = None
    session = None
    ticker = None

    def __init__(self, ticker):
        self.baseNumber = 0
        self.session = requests.session()
        self.ticker = ticker
        self.session.get("https://www.nseindia.com", headers=head)
        self.session.get("https://www.nseindia.com/get-quotes/equity?symbol=" + ticker, headers=head)

    def secondsTotime(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return hour, minutes, seconds

    def dateCalculator(self, num):
        if self.baseNumber == 0:
            self.baseNumber = (num // 100000) * 100000
        num = abs(num - self.baseNumber)
        num = num / 1000
        num = int(num)
        today = datetime.today()
        (h, m, s) = self.secondsTotime(num)
        return datetime(today.year, today.month, today.day, 9 + h, m, s)

    def intraDay(self,):
        preopen_url = "https://www.nseindia.com/api/chart-databyindex?index=" + self.ticker + "&preopen=true"
        open_url = "https://www.nseindia.com/api/chart-databyindex?index=" + self.ticker
        preopen_webdata = self.session.get(url=preopen_url, headers=head)
        opened_webdata = self.session.get(url=open_url, headers=head)
        timestamp = []
        data = []

        # for (i, j) in preopen_webdata.json()['grapthData']:
        #     timestamp.append(self.dateCalculator(i))
        #     data.append(j)

        for (i, j) in opened_webdata.json()['grapthData']:
            timestamp.append(self.dateCalculator(i))
            data.append(j)
        return timestamp, data

    def nifty_intraDay(self):
        varient = self.ticker
        varient = varient.upper()
        varient = varient.replace(' ', '%20')
        varient = varient.replace('-', '%20')
        preopen_url = "https://www.nseindia.com/api/chart-databyindex?index={}&indices=true&preopen=true".format(
            varient)
        open_url = "https://www.nseindia.com/api/chart-databyindex?index={}&indices=true".format(varient)
        print(preopen_url)
        preopen_webdata = self.session.get(url=preopen_url, headers=head)
        open_webdata = self.session.get(url=open_url, headers=head)
        data = []
        timestamp = []

        # for (i, j) in preopen_webdata.json()['grapthData']:
        #     data.append(j)
        #     timestamp.append(self.dateCalculator(i))

        for (i, j) in open_webdata.json()['grapthData']:
            data.append(j)
            timestamp.append(self.dateCalculator(i))

        return timestamp, data


# ID = Intra_Day('INFYEQN')
# timeStamp, dataPoints = ID.intraDay()
# ID = Intra_Day('NIFTY 50')
# timeStamp, dataPoints = ID.nifty_intraDay()