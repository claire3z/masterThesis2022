# This is a sandbox / sketchbook Python script.
import pandas as pd
import time
from bs4 import BeautifulSoup
import re
import random

pd.set_option('max_colwidth',None)
pd.options.display.width = 0
pd.set_option('display.max_rows', None)

# 2021.11.10
# Download 10Q from EDGAR
# https://github.com/jadchaar/sec-edgar-downloader
# $ pip install -U sec-edgar-downloader

from sec_edgar_downloader import Downloader

# Initialize a downloader instance. If no argument is passed to the constructor, the package will download filings to the current working directory.
dl = Downloader("C:/Users/clair/Desktop/Thesis/masterThesis2022/Data/")
dl.get("10-Q", "goog") # this download ALL 10-Qs
dl.get("10-K", "googl") # only available from 2016 onwards for both tickers goog and googl
dl.get("10-K",'1288776') # this is the old CIK for google before the name change
dl.get("10-Q", "goog", amount = 4) # specify how many to download

dl.get("10-K", "MSFT",amount=20)
dl.get("10-K", "AMZN",amount=21)

equity_ids = ["HOOD", "AMZN"]
for equity_id in equity_ids:
    dl.get('10-Q', equity_id, amount=10)

# S&P500 tickers (source: https://en.wikipedia.org/wiki/List_of_S%26P_500_companies)
# all listed stock tickers (source: https://www.nasdaq.com/market-activity/stocks/screener)
file_name = "C:/Users/clair/Desktop/Thesis/masterThesis2022/Data/Tickers_SP500.csv"
df = pd.read_csv(file_name)
symbols = df['Symbol']

# now = time.time()
for equity_id in symbols[:5]:
    dl.get('10-Q', equity_id, amount=4)
    # print(time.time()-now)
    # now = time.time()
# #16s for 4 reports

### Processing txt file
file_txt = "C:/Users/clair/Desktop/Thesis/masterThesis2022/Data/sec-edgar-filings/MMM/10-Q/0000066740-21-000013/full-submission.txt"
with open(file_txt) as f:
    soup_txt = BeautifulSoup(f.read(),'lxml') # parsing eXtensible Business Reporting Language (XBRL)

# On June 28, 2018, the Commission adopted amendments requiring the use, on a phased in basis, of Inline XBRL for operating company financial statement information and fund risk/return summary information.
soup_txt.title
len(soup_txt.text)
soup_txt.text[:1000]
a_txt = soup_txt.find_all('a')
len(a_txt)

file_html = "C:/Users/clair/Desktop/Thesis/masterThesis2022/Data/sec-edgar-filings/MMM/10-Q/0000066740-21-000013/filing-details.html"
with open(file_html) as f:
    soup_html = BeautifulSoup(f, 'html.parser')

soup_html.head
soup_html.title
a_html = soup_html.find_all('a')
len(a_html)
len(soup_html.text)
soup_html.text[:100]

regex = re.compile(r"Management's Discussion and Analysis of")

pattern_item2 = re.compile(r"Item 2. Management’s Discussion and Analysis of Financial Condition and Results of Operations.",flags=re.IGNORECASE)#Management's Discussion and Analysis of")
pattern_item3 = re.compile(r"Item 3. Quantitative and Qualitative Disclosures About Market Risk.",flags=re.IGNORECASE)

start = re.search(pattern_item2,soup_html.text).start()
end = re.search(pattern_item3,soup_html.text).start()
len(soup_html.text[start:end]) #74927

soup_html.text[start:end][:300]

# split into sentences
import spacy
nlp = spacy.load("en_core_web_sm")

text = soup_html.text[start:end]
sentences = [i for i in nlp(text).sents]
len(sentences) #376
type(str(sentences[10]))

df_mda = pd.DataFrame([str(sentence) for sentence in nlp(text).sents])
df_mda.shape #(376, 289)
df_mda.head(3)
df_mda.columns = ['sent']
for x in df_mda['sent'][:10].list():
    print(len(x))

df_mda[df_mda['sent'].str.contains(re.compile("sales",flags=re.IGNORECASE))]


m = re.finditer(re.compile(r'Months Ended'), text)
for i in m:
    print(i)


# 2021.11.11
# DONE: Test downloading - ticker from csv file and data saved to D:/ drive (c. 80 GB c. 16 hours)
# DONE: Figure out regex patterns for the start and end of MD&A session

from sec_edgar_downloader import Downloader

path = "C:/Users/clair/Desktop/Thesis/masterThesis2022/Data/"
path_save = "D:/masterThesis2022/Data/"

df_sp500 = pd.read_csv(path+"Tickers_SP500.csv")
dl = Downloader(path_save)

# Run this before going to bed...
for ticker in df_sp500["Symbol"][220:]:
    dl.get('10-Q', ticker, amount=100) # only 3x 10Q per year + 10K
    dl.get('10-K', ticker, amount=30) # ideally wanted 30 years (1990-2020)

# most of the company's online files starts in early 2000's. EDGAR only started in 1994/95.

df_sp500["Symbol"][df_sp500["Symbol"]=='GWW']
df_sp500["Symbol"][220]

file_html_Q = "C:/Users/clair/Desktop/Thesis/masterThesis2022/Data/sec-edgar-filings/MMM/10-Q/0000066740-21-000013/filing-details.html"
file_html_K = "C:/Users/clair/Desktop/Thesis/masterThesis2022/Data/sec-edgar-filings/GOOG/10-K/0001652044-21-000010/filing-details.html"

pattern_start = re.compile(r"Item\s?\d?.?\s*Management’s Discussion and Analysis of Financial Condition and Results of Operations",flags=re.IGNORECASE)#Management's Discussion and Analysis of")
pattern_end = re.compile(r"Item\s?\d[A-Z]?.?\s*Quantitative and Qualitative Disclosures About Market Risk",flags=re.IGNORECASE)

file_html = file_html_Q
file_html = file_html_K

with open(file_html) as f:
    soup_html = BeautifulSoup(f, 'html.parser')

starts = re.finditer(pattern_start, soup_html.text)
for i in starts:
    print(i)

ends = re.finditer(pattern_end, soup_html.text)
for i in ends:
    print(i)

mdna = soup_html.text[starts[1]:ends[1]] #first set is table of content; 2nd set

# Need to test how universal is this... TODO



### 2021.11.12

#DONE: understand XBRL
#DONE: extract revenue information

# https://www.xbrl.org/the-standard/how/getting-started-for-developers/
# The foundation of XBRL is the idea of a concept.
# Collections of related concepts are held in an XBRL taxonomy.
# By combining a concept (profit) from a taxonomy (say Canadian GAAP) with a value (1000) and the needed context
# (Acme Corporation, for the period 1 January 2015 to 31 January 2015 in Canadian Dollars) we arrive at a fact.
# Collections of facts in XBRL are contained in documents called instances.
# Instance documents are XBRL based reports about performance, risk, compliance or some other set of logically consistent information that needs to be communicated internally or externally.
# Instances that report dimensionally will have multiple contexts that reference different dimension members, applied to multiple facts.


# us-gaap:Revenues - available for segments
# us-gaap:OperatingIncomeLoss - available for segments corresponding for sales

# Revenue Numbers Extraction

for i in soup_html.find_all('ix:nonfraction',{'name':'us-gaap:Revenues'})[:50]:
    context_id = i['contextref']
    context = soup_html.find_all('xbrli:context', {'id': context_id})[0]
    period = context.find('xbrli:period')
    start_date = period.find('xbrli:startdate').text
    end_date = period.find('xbrli:enddate').text

    if context.find('xbrli:segment'):
        label = ['Segment']
        for l in context.find_all('xbrldi:explicitmember'):
            label.append(l.text)
    else:
        label = 'Total'

    print(i.text, start_date, end_date, label)


# Operating Profit Numbers Extracton

for i in soup_html.find_all('ix:nonfraction',{'name':'us-gaap:OperatingIncomeLoss'}):
    context_id = i['contextref']
    context = soup_html.find_all('xbrli:context', {'id': context_id})[0]
    period = context.find('xbrli:period')
    start_date = period.find('xbrli:startdate').text
    end_date = period.find('xbrli:enddate').text

    if context.find('xbrli:segment'):
        label = ['Segment']
        for l in context.find_all('xbrldi:explicitmember'):
            label.append(l.text)
    else:
        label = 'Total'

    print(i.text, start_date, end_date, label)


# us-gaap:CostOfRevenue - typically only at the company level; not disclosed for segments
# us-gaap:CostsAndExpenses - typically only at the company level
# us-gaap:NetIncomeLoss - typically only at the company level;

# Numbers Extraction only at the group level

for i in soup_html.find_all('ix:nonfraction',{'name':'us-gaap:NetIncomeLoss'}):
    context_id = i['contextref']
    context = soup_html.find_all('xbrli:context', {'id': context_id})[0]
    period = context.find('xbrli:period')
    start_date = period.find('xbrli:startdate').text
    end_date = period.find('xbrli:enddate').text

    if not context.find('xbrli:segment'):
        print(i.text, start_date, end_date)



### 2021.11.13 - 14
# TODO: Check statistics in downloaded files - how many in total etc. [DONE]
# TODO: Spot check if the above patterns work for randomly selected files
# TODO: Think about data structure to save data
# TODO: Parsing MD&A Session - find all sentences containing revenue / profit
# TODO: Perform some EDA - verbs distribution, etc.


random.random()< 0.10

# Total number of files downloaded
import os
path = "D:/masterThesis2022/Data/sec-edgar-filings/"

tickers = []
K_files =[]
Q_files=[]
for ticker in os.listdir(path):
    try:
        K = os.listdir(path+ticker+"/10-K/")
    except FileNotFoundError:
        K = []
    try:
        Q = os.listdir(path+ticker+"/10-Q/")
    except FileNotFoundError:
        Q = []
    tickers.append(ticker)
    K_files.append(K)
    Q_files.append(Q)

df = pd.DataFrame.from_dict({'ticker':tickers, '10K_files':K_files,'10Q_files':Q_files})
df['k_count'] = df['10K_files'].apply(len)
df['q_count'] = df['10Q_files'].apply(len)
df['total'] = df['k_count']+df['q_count']
df[['k_count','q_count']].describe()
df['total'].describe()

df.set_index('ticker', inplace=True)


df_sp = pd.read_csv(path_save+'Tickers_SP500.csv')
df_sp.set_index('Symbol',inplace=True)

# df_edgar = pd.io.json.read_json(path_save+'company_tickers_exchange.json') #ValueError: arrays must all be same length
import json
with open(path_save+'company_tickers_exchange.json') as file_json:
    json_data = json.load(file_json)
df_edgar = pd.DataFrame(json_data['data'],columns=json_data['fields'])
df_edgar.set_index('ticker', inplace=True)
df_edgar.head()

# create a master database
df = pd.concat([df_edgar[['cik','name','exchange']],df], axis=1, join="inner") #add columns from edgar file
df = pd.concat([df, df_sp[['GICS Sector', 'GICS Sub-Industry','Date first added','Founded']]], axis=1, join="inner") # add columns from sp500 file
# Founded dates are not accurate from wikipedia (https://en.wikipedia.org/wiki/List_of_S%26P_500_companies)
df.columns #Index(['cik', 'name', 'exchange', '10K_files', '10Q_files', 'k_count', 'q_count', 'total', 'GICS Sector', 'GICS Sub-Industry', 'Date first added', 'Founded'], dtype='object')
len(df.index)

path_save = "C:/Users/clair/Desktop/Thesis/masterThesis2022/Data/"
df.to_csv(path_save+"statistics.csv",index=True, index_label='ticker')
df = pd.read_csv(path_save+'statistics.csv')

missing = df.index[df['total']<80].values
# A total of 145 companies (c. 30% of 500) have less than 80 reports; there are two categories:
# 1) IPO dates after 2000 (NOT so easy to find historical IPO dates); ASSUMING most companies with more than 40 reports belong to this category
# 2) company changed name/ticker, EDGAR only captures the latest (e.g. Google -> Alphabet 2015)

df_missing = df.loc[missing,['name','total','exchange']]
group1 = df_missing.index[df_missing['total']>40].values
### 88 companies, spot checks: Under-Armour, Discovery, Tesla ... makes sense.

df_missing[(df_missing['total']>30)&(df_missing['total']<=40)].size
### 17 companies, spot checks: paycom Software 31 2014; Twitter 32 2013; Hilton 32 2013; Norwegian Cruise 36, 2013; News Corp 32, 2013; Allegion 32, 2013

df_missing[(df_missing['total']>20)&(df_missing['total']<=30)].size
### 16 companies

### IPOs:
# PayPal 2015; IHS 2014; ETSY 2015; Fortive Corp 2016; Catalent, Inc. 2014;

### M&As:
# Kraft Heinz 2015 merger
# Walgreens Boots Alliance 2015 merger
# Keysight Technology 2014 spin-off from Agilent Technologies
# CITIZENS FINANCIAL GROUP INC/RI 2014 carve-out of Royal Bank of Scotland
# Hewlett Packard Enterprise Co 2015 spin-off from HP


df_missing[(df_missing['total']<20)].size
### 24 companies

### IPOs:
# Ceridian HCM Holding Inc. 2018; Viatris Inc 2020; # Moderna, Inc 2018 IPO; # Baker Hughes Co 2017 IPO;

### M&As:
# CARRIER GLOBAL Corp 2020 separation from United Technologies
# Otis Worldwide Corp 2020 separation from United Technologies
# (United Technology renamed RAYTHEON TECHNOLOGIES and already included in database under RTX, CIK #101829)

# DuPont de Nemours, Inc 2019 separation of its Agriculture Division through the spin-off of Corteva, Inc. (“Corteva”). The company was formerly known as DowDuPont Inc
# Corteva, Inc. 2019 - 11 spin-off from DowDuPont;

# ViacomCBS Inc 2019 CBS acquisition of Viacom
# Amcor plc 2019 acquisition of Bemis Company Inc. and began trading on the NYSE under the ticker symbol “AMCR” and on the Australian Securities Exchange under the ticker “AMC.
# WRK WestRock Co 12 - 2015 merger of MeadWestvaco and RockTenn
# DXC Technology Co  19 - 2017 spin-off of Enterprise Service segment from Hewlett Packard Enterprise
# OGN Organon & Co. 2020 spin-off of Women’s Health, Legacy Brands and Biosimilars businesses from Merck & Co.


### Former entity
# DowDuPont Inc - 2019 spin-off; DowDuPont Inc. (NYSE: DWDP)-old; Dow Inc. (“Dow” included in database 118)-Materials Science Division.
# Kraft Inc. IPO 2011 - 2015 merger
# Heinz IPO 1946 - 2013 take private 3G/BH
# Walgreens before 2015 merger
# Amcor plc 2019 acquisition - Amcor Limited (ASX: AMC) listed in Australia before acquisition of Bemis Company, Inc. (NYSE: BMS) and dual listing current ticker NYSE:AMCR
# Walt Disney current https://www.sec.gov/Archives/edgar/data/0001744489 ; before https://www.sec.gov/Archives/edgar/data/1001039/
# News Corp 2013 acquisition
# Twenty-First Century Fox, Inc. (Nasdaq: FOXA, FOX) 2013-2019
# 21st Century Fox was the legal successor to News Corporation dealing primarily in the film and television industries. 21st Century Fox was formed by the splitting of entertainment and media properties from News Corporation.. acquisition by The Walt Disney Company in 2019.
# Viacom before 2019
# CBS before 2019


### Name Changes
# Google changed its name in 2015? and SEC CIK has changed - current 0001652044; before 0001288776 // https://www.sec.gov/edgar/browse/?CIK=0001288776
# GOOG / GOOGL repeat; 2015 name change; missing prior IPO 2004
# BBWI Bath & Body Works, Inc. 2021 name change from 'Victoria's Secretes' / 'L Brands’; symbol will also change from “LB” to “BBWI.”


### Missing
# STERIS plc 1992 - 11; - incorporation changes from UK to Ireland
# Broadcom Inc. 1998 - 14 -  acquired by Avago Technologies in 2016; previously Broadcom Corp
# Cigna Corp 1998 - 12 - acquired Express Scripts in 2018
# NXP Semiconductors N.V 2011 - 9: switched to 10-Q and 10-F in 2019; before foreign issuer 20-F instead of 10-K; quarterly reports not required to file
# Medtronic 27; - 2015 registration from US to Ireland, acquisition of Irish–tax registered Covidien (a U.S. tax inversion to Ireland from 2007)
# Lumen Technologies, Inc. 1972 - 5: name change in 2020 from CenturyLink (NYSE:CTL) to Lumen Technologies (LUMN); same CIK could get all.
# EVRG Evergy, Inc. - 14: merger of Great Plains Energy and Westar Energy, Inc. 2017
# CTRA Coterra Energy Inc. IPO 1990 - 11: Cimarex, Cabot Complete Merger, Rebrand as Coterra Energy 2021


df['name'].size #502
df['name'].unique().size #497
df_sp.index.difference(df.index) #['BF.B':Brown-Forman Corporation Class B, 'BRK.B', 'FRC']

df_sp[df_sp.index =="BF.B"]
df_sp[df_sp.index =="BRK.B"]
df_sp[df_sp.index =="FRC"]


dl = Downloader("C:/Users/clair/Desktop/Thesis/masterThesis2022/Data/")
cik = '0001067983'
dl.get("10-K", cik, amount = 20) # 20 download works
dl.get("10-K", 'BRK.B', amount = 2) #0 not working
dl.get("10-K", 'BRK', amount = 20) # works, same as using cik
dl.get("10-K", 'BF', amount = 2) # works - remove .B

dl.get("10-K", 'FRC', amount = 2) # does not work # Listed: 2010-12-09
dl.get('10-K','0001132979',amount=2) # does not work
dl.get('10-K','XNYS:FRC',amount=2) #Not available...

dl.get('10-K','LB',amount=2) #L Brands
dl.get('10-K','LUMN',amount=10) #Lumen Technologies only 1
dl.get('10-K','18926',amount=10) #Lumen Technologies only 1


feigein20F = ['NXPI']
dl = Downloader("C:/Users/clair/Desktop/Thesis/masterThesis2022/Data/")
dl.get('20-F', 'NXPI') #8

addn1 = {'BF':'BROWN FORMAN CORP',
        'BRK':'BERKSHIRE HATHAWAY INC',

        'LB':'BBWI - Bath & Body Works name change from L Brands in 2021 ',
        '1288776': 'GOOG - Alphabet name change from Google Inc. in 2015',
        '18926':'LUMN - Lumen Technologies name change from CenturyLink in 2020',

        '1624899':'STE - STERIS plc 2015-19 before HQ change from UK to Ireland', '815065':'STE - STERIS Corp 1999-2015',
        '64670':'MDT - Medtronic plc HQ change from US to Ireland in 2014; Medtronic Inc 1999-2015 before tax inversion',
        }

for ticker in addn1.keys():
    dl.get('10-Q', ticker, amount=100) # only 3x 10Q per year + 10K
    dl.get('10-K', ticker, amount=30) # ideally wanted 30 years (1990-2020)


addn2 = {'54507':'EVRG - Westar Energy (WR) before merger 2017 (containing latest)', '1143068':'EVRG - Great Plains Energy Inc before merger 2017',
         '701221': 'CI - CIGNA Holding Co 2004-2018 before acquiring the pharmacy services company Express Scripts in 2018', '1532063':'Express Scripts before acquisition by Cigna 2011-2018; IPO 2011',
         '1649338':'AVGO - Broadcom Pte. Ltd. merged entity 2016-18','1054374':'Broadcom Corp before acquisition by Avago Technologies 1999-2015', '1441634':'Avago Technologies LTD before the acquisition of Broadcom 2009-2015',
         '858470':'CTRA - Cabot Oil & Gas Corp before merger in 2021 (containing latest)', '1168054':'CTRA - Cimarex Energy before merger 2021',
         '1545158':'KHC - Kraft Foods Group IPO 2011-2015 merger with Heinz', '46640':'KHC - H.J. Heinz 1994 - 2013 Take private',
         '104207':'WBA - Walgreens Co 1994-2015 delisting merger with Boots',
         '11199':'AMCR - Bemis Company, Inc. (NYSE: BMS) 1994 - 2019 acquisition by Amcor',
        '813828':'VIAC - CBS Corp 2007-2021 merger 2019 (containing latest)',
         '1339947':'VIAC - Viacom Inc 2005-2019 before merger with CBS in 2019',
         '1001039':'DIS - Walt Disney Co 2001-2020 before acquisition of 21st Century Fox',
        '1308161':'NewsCorp/Fox - 21st Century Fox / News Corp 2006 - 2019 before acquisition by Walt Disney',
}


for ticker in addn2.keys():
    dl.get('10-Q', ticker, amount=100) # only 3x 10Q per year + 10K
    dl.get('10-K', ticker, amount=30) # ideally wanted 30 years (1990-2020)


### Still missing:
# 'FRC' - First republic bank (https://sec.report/Ticker/FRC)

df[['cik','name','total']][df.name=='Walt Disney Co']


### Notes:
# News Corp A / News Corp repeats? - News Corp Class A and Class B Common Stock under the ticker symbols “NWSA” and “NWS,” respectively
# The current News Corp began trading on the NASDAQ stock exchange under the symbol "NWS" on July 1, 2013; at the same time, the former News Corporation (which encompassed purely of media properties, such as Fox Entertainment Group and 20th Century Fox) was renamed 21st Century Fox.
# 21 Centry Fox 2013 - 2019 sell to disney; remaining Fox Corp
# News Corp pior to 2013?
# Walt Disney Co 1957 - 10 2019 acquisition of Twenty-First Century Fox, Inc.
# Fox Corp 2019 - Fox Corp represents the assets not sold to Disney by the predecessor firm, Twenty First Century Fox. The remaining assets include Fox News, the FOX broadcast network, FS1 and FS2, Fox Business, Big Ten Network, 28 owned and operated local television stations of which 17 are affiliated with the Fox Network, and the Fox Studios lot. The Murdoch family continues to control the successor firm,

# Nov. 22, 2019 /PRNewswire/ -- CBS Corporation (NYSE: CBS.A and CBS) ("CBS") today announced that following the effective time of the merger of Viacom Inc. ("Viacom") with and into CBS (the "merger"), with CBS continuing as the surviving company,
# CBS will delist its Class A and Class B common stock from the NYSE and will list the Class A and Class B common stock of the combined company, renamed "ViacomCBS Inc." ("ViacomCBS"), including the outstanding shares of CBS Class A and Class B common stock (which will remain outstanding shares of ViacomCBS), on the Nasdaq Global Select Market ("Nasdaq"). Trading of the Class A and Class B common stock of ViacomCBS on Nasdaq under the new ticker symbols "VIACA" and "VIAC," respectively,


# ISSUES: some companies are not pulling full 20 years of record... might be due to 1) IPO date 2) Name change or ticker change
# import yfinance as yf
# disney = yf.Ticker("DIS")
# disney.info.keys()
#
# disney.history(period='max')
# disney.financials
# disney.major_holders
#
# alph = yf.Ticker('GOOGL')
# for key in alph.get_info().keys():
#     print(key)
#
# alph.get_info()['startDate'] #None
# alph.get_info()['sector']
#
# disney.info['sector']
# disney.info['startDate']

### yfinance does not have IPO dates for most companies...


df = pd.read_csv(path_save+"statistics_v1.csv",index_col='ticker')

df.drop(['GOOGL','DISCA','FOXA','NWSA','UAA'], axis='index', inplace=True)

df.to_csv(path_save+"statistics_v1.csv",index=True, index_label='ticker')

# Process additional downloads
path = path_save+"sec-edgar-filings/"
tickers = []
ciks = []
names =[]
K_files =[]
Q_files=[]
for ticker in os.listdir(path):
    try:
        K = os.listdir(path+ticker+"/10-K/")
    except FileNotFoundError:
        K = []
    try:
        Q = os.listdir(path+ticker+"/10-Q/")
    except FileNotFoundError:
        Q = []

    i = ticker.find('_')
    tickers.append(ticker[:i])

    j = ticker.rfind('_')
    ciks.append(ticker[j+1:])

    if i !=j:
        names.append(ticker[i+1:j])
    else:
        names.append('.')

    K_files.append(K)
    Q_files.append(Q)


df_addn = pd.DataFrame.from_dict({'ticker':tickers,'cik':ciks, 'name':names, '10K_files':K_files,'10Q_files':Q_files})
df_addn['k_count'] = df_addn['10K_files'].apply(len)
df_addn['q_count'] = df_addn['10Q_files'].apply(len)
df_addn['total'] = df_addn['k_count']+df_addn['q_count']

df_addn[['k_count','q_count']].describe()
df_addn['total'].describe()

df_addn.set_index('ticker', inplace=True)
df_addn.to_csv(path_save+"statistics_v2.csv",index=True, index_label='ticker')

# Combining initial data with additional downloads
df_combined = pd.concat([df,df_addn], axis=0, join="outer")
len(df),len(df_addn),len(df_combined) #(497, 26, 523)
len(df_combined.index.unique()) #500

df_summary = df_combined.groupby(level=0)['total'].sum()
df_summary.describe()
df_summary.plot.hist(bins=4)

df_combined.groupby('GICS Sector').count()['name']

samples1 = df_combined[df_combined['GICS Sub-Industry'].isin(['Application Software','Semiconductors','Data Processing & Outsourced Services'])]

samples2 = df_combined[df_combined['GICS Sub-Industry']!='Information Technology'].sample(10)


### 2021.11.17
#TODO: Transfer sample files from D:/ to C:/ [Done]
#TODO: Create proprocessing.ipynb [Done]
#TODO: Further test and modify patterns [Done]
#TODO: Data structure for folder-file-positions-interactive?

file_name = "YUM/10-K/0001041061-01-500003/filing-details.html" ### <-- this is just a PDF
# file_name = "GOOG/10-Q/0001652044-21-000057/filing-details.html" ### <-- this is
# file_name = "GOOG/10-K/0001652044-16-000012/filing-details.html"

file_html = path + file_name
pattern_start = re.compile(
    r"Item\s?\d?.?\s*Management[’|']s Discussion and Analysis of Financial Condition and Results of Operations",
    flags=re.IGNORECASE)  # Management's Discussion and Analysis of")
pattern_end = re.compile(r"Item\s?\d[A-Z]?.?\s*?Quantitative and Qualitative Disclosures about Market",
                         flags=re.IGNORECASE)

with open(file_html) as f:
    soup_html = BeautifulSoup(f, 'html.parser')

soup_text = soup_html.get_text(strip=True)
soup_text = soup_text.replace('\n', ' ').replace('\xa0', ' ')

print(soup_html.title)
print('Raw len = {}, vs clean len = {} / {}'.format(len(soup_html.text), len(soup_html.get_text(strip=True)),
                                                    len(soup_text)))

print("Starting matches:")
starts = re.finditer(pattern_start, soup_text)
for i in starts:
    print(i)

print("\nEnding matches:")
ends = re.finditer(pattern_end, soup_text)
for i in ends:
    print(i)

starts = [*re.finditer(pattern_start, soup_text)]
if len(starts) > 1:
    start = starts[1].start()
elif len(starts) == 1:
    start = starts[0].start()
else:
    pattern_start = re.compile(
        r"Management[’|']s Discussion and Analysis of Financial Condition and Results of Operations",
        flags=re.IGNORECASE)  # Management's Discussion and Analysis of")

    print("Starting matches:")
    starts = re.finditer(pattern_start, soup_text)
    for i in starts:
        print(i)

    starts = [*re.finditer(pattern_start, soup_text)]
    if len(starts) == 1:
        start = starts[0].start()

ends = [*re.finditer(pattern_end, soup_text)]
if len(ends) > 1:
    end = ends[1].start()
elif len(ends) == 1:
    end = ends[0].start()
else:
    pattern_end = re.compile(r"Quantitative and Qualitative Disclosures about Market", flags=re.IGNORECASE)

    print("\nEnding matches:")
    ends = re.finditer(pattern_end, soup_text)
    for i in ends:
        print(i)

    ends = [*re.finditer(pattern_end, soup_text)]
    if len(ends) == 1:
        end = ends[0].start()

print(
    '\n\nStarting position = {}\n {} \n...\n {}\nEnding posisition ={}\n\n{}'.format(start, soup_text[start:end][:500],
                                                                                     soup_text[start:end][-500:], end,
                                                                                     soup_text[end:end + 100]))

# Testing for financial extraction
## NOTES:
# Inline XBRL
# On June 28, 2018, the Commission adopted amendments requiring the use, on a phased in basis, of Inline XBRL for operating company financial statement information and fund risk/return summary information.

# When must filers begin filing using Inline XBRL?
# There is a three-year phase-in for U.S. GAAP filers to comply the Inline XBRL requirements, beginning with fiscal periods ending on or after:
# June 15, 2019 for large accelerated filers
# June 15, 2020 for accelerated filers
# June 15, 2021 for all other filers
# For IFRS filers, compliance is required beginning with fiscal periods ending on or after June 15, 2021.


### 2021.11.18
# mainly working on .ipynb to finalize the patterns

# Verbose version
def identify_MDA(file_name):
    file_html = path + file_name
    with open(file_html) as f:
        soup_html = BeautifulSoup(f, 'html.parser')

    soup_text = soup_html.get_text(strip=True)
    soup_text = soup_text.replace('\xa0', '').replace('\n', '')

    pattern_toc = re.compile(r"(table of contents)|(index)", flags=re.IGNORECASE)
    toc = re.search(pattern_toc, soup_text)
    ix = len(soup_html.find_all('ix:header'))

    pattern_start = re.compile(
        r"(?<![\"|“|'])Item\s?\d?.?\s*Management[’|']s[\s]*Discussion[\s]*and[\s]*Analysis[\s]*of[\s]*Financial[\s]*Condition[\s]*and[\s]*Results[\s]*of[\s]*Operations",
        flags=re.IGNORECASE)  # Management's Discussion and Analysis of")
    starts = [*re.finditer(pattern_start, soup_text)]
    if len(starts) == 0:
        pattern_start = re.compile(
            r"(?<![\"|“|'])Management[’|']s[\s]*Discussion[\s]*and[\s]*Analysis[\s]*of[\s]*Financial[\s]*Condition[\s]*and Results[\s]*of[\s]*Operations",
            flags=re.IGNORECASE)  # Management's Discussion and Analysis of")
        starts = [*re.finditer(pattern_start, soup_text)]

    if len(starts) == 1:
        start = starts[0].start()

    elif len(starts) > 1:
        if toc:
            start = starts[1].start()
        else:
            start = 0
            print('\n>>>>>>NO TOC and MORE THAN 1 START POSITIONS!!!<<<<<<\n')
            pass  # TODO
    else:
        start = 0
        print('\n>>>>>>COULD NOT FIND ANY START POSITION!!!<<<<<<\n')
        pass  # TODO

    pattern_end = re.compile(
        r"(?<![\"|“|'])Item\s?\d[A-Z]?.?\s*Quantitative[\s]*and[\s]*Qualitative[\s]*Disclosure[s]?[\s]*about[\s]*Market",
        flags=re.IGNORECASE)
    ends = [*re.finditer(pattern_end, soup_text)]
    if len(ends) == 0:
        pattern_end = re.compile(
            r"(?<![\"|“|'])Quantitative[\s]*and[\s]*Qualitative[\s]*Disclosure[s]?[\s]*about[\s]*Market",
            flags=re.IGNORECASE)
        ends = [*re.finditer(pattern_end, soup_text)]

    if len(ends) == 1:
        end = ends[0].start()

    elif len(ends) > 1:
        if toc:
            end = ends[1].start()
        else:
            for i in len(ends):
                if ends[i].start() > start + 10000:
                    end = ends[i].start()
                    break
            print('\n>>>>>>NO TOC and MORE THAN 1 END POSITIONS!!!<<<<<<\n')
            pass  # TODO

    else:
        end = min(start + 50000, len(soup_text))
        print('\n>>>>>>COULD NOT FIND ANY END POSITION!!!<<<<<<\n')
        pass  # TODO

        # if end position is not found (some companies did not have Quantitiative and Qualitative section in earlier reports)
        # then end = start + 10000

    print(soup_html.title.text, 'IX=', ix, 'size=', len(soup_text), 'toc=', toc, '\n')

    print("Starting matches:")
    for i in starts:
        print(i, '\n...', soup_text[i.start() - 100:i.start() + 100])

    print("\nEnding matches:")
    for i in ends:
        print(i, '\n...', soup_text[i.start() - 100:i.start() + 100])

    print(
        '\n\n{}\n----------------------->>> Starting position = {} <<<---------------------\n {} \n...\n {}\n----------------------->>> Ending posisition = {} <<<---------------------\n{}'.format(
            soup_text[start - 100:start], start, soup_text[start:start + 500], soup_text[end - 500:end], end,
            soup_text[end:end + 100]))
    if end < start:
        print("END > START !!!")
    print('\n============================================================================\n\n\n')

    return start, end


file_names = ["YUM/10-K/0001041061-01-500003/filing-details.html",
              "YUM/10-Q/0001564590-16-029416/filing-details.html",
              "YUM/10-K/0001564590-21-009460/filing-details.html",

              "GOOG/10-Q/0001652044-21-000057/filing-details.html",
              "GOOG/10-K/0001652044-19-000004/filing-details.html",
              "GOOG/10-K/0001652044-21-000010/filing-details.html",

              "MRK/10-Q/0000310158-00-500003/filing-details.html",
              "MRK/10-K/0000310158-18-000005/filing-details.html",
              "MRK/10-K/0000310158-21-000004/filing-details.html",

              'D/10-Q/0000215466-12-000006/filing-details.html',
              'D/10-Q/0001564590-21-054856/filing-details.html',
              'D/10-K/0000882184-17-000103/filing-details.html'
              ]
record = {}
for file_name in file_names:
    record[file_name] = identify_MDA(file_name)


# Clean version

def identify_MDA_save(file_name):
    with open(file_name) as f:
        soup_html = BeautifulSoup(f, 'html.parser')

    soup_text = soup_html.get_text(strip=True)
    soup_text = soup_text.replace('\xa0', '').replace('\n', '')

    pattern_toc = re.compile(r"(table of contents)|(index)", flags=re.IGNORECASE)
    toc = re.search(pattern_toc, soup_text)
    ix = len(soup_html.find_all('ix:header'))

    pattern_start = re.compile(
        r"(?<![\"|“|'])Item\s?\d?.?\s*Management[’|']s[\s]*Discussion[\s]*and[\s]*Analysis[\s]*of[\s]*Financial[\s]*Condition[\s]*and[\s]*Results[\s]*of[\s]*Operations",
        flags=re.IGNORECASE)  # Management's Discussion and Analysis of")
    starts = [*re.finditer(pattern_start, soup_text)]
    if len(starts) == 0:
        pattern_start = re.compile(
            r"(?<![\"|“|'])Management[’|']s[\s]*Discussion[\s]*and[\s]*Analysis[\s]*of[\s]*Financial[\s]*Condition[\s]*and Results[\s]*of[\s]*Operations",
            flags=re.IGNORECASE)  # Management's Discussion and Analysis of")
        starts = [*re.finditer(pattern_start, soup_text)]

    if len(starts) == 1:
        start = starts[0].start()

    elif len(starts) > 1:
        if toc:
            start = starts[1].start()
        else:
            start = 0
    #            print('\n>>>>>>NO TOC and MORE THAN 1 START POSITIONS!!!<<<<<<\n')
    #            pass #TODO
    else:
        start = 0
    #        print('\n>>>>>>COULD NOT FIND ANY START POSITION!!!<<<<<<\n')
    #        pass #TODO

    pattern_end = re.compile(
        r"(?<![\"|“|'])Item\s?\d[A-Z]?.?\s*Quantitative[\s]*and[\s]*Qualitative[\s]*Disclosure[s]?[\s]*about[\s]*Market",
        flags=re.IGNORECASE)
    ends = [*re.finditer(pattern_end, soup_text)]
    if len(ends) == 0:
        pattern_end = re.compile(
            r"(?<![\"|“|'])Quantitative[\s]*and[\s]*Qualitative[\s]*Disclosure[s]?[\s]*about[\s]*Market",
            flags=re.IGNORECASE)
        ends = [*re.finditer(pattern_end, soup_text)]

    if len(ends) == 1:
        end = ends[0].start()

    elif len(ends) > 1:
        if toc:
            end = ends[1].start()
        else:
            for i in len(ends):
                if ends[i].start() > start + 10000:
                    end = ends[i].start()
                    break
    #            print('\n>>>>>>NO TOC and MORE THAN 1 END POSITIONS!!!<<<<<<\n')
    #            pass #TODO

    else:
        end = min(start + 50000, len(soup_text))

    return ix, start, end


# Add Google old files (before name change) to the sample 2

sample2 = pd.read_csv(path[:-8]+'statistics_samples2.csv')

ticker = 'GOOG_1288776'
K = os.listdir(path+ticker+"/10-K/")
Q = os.listdir(path+ticker+"/10-Q/")
add_google = pd.DataFrame({'ticker':[ticker], '10K_files':[K], '10Q_files':[Q], 'k_count':[len(K)], 'q_count':[len(Q)]})

sample2 = sample2.append(add_google)
sample2.set_index('ticker', inplace=True)

# Delete AVGO since it has been added to the IT sample
sample2.drop('AVGO',axis='index',inplace=True)

sample2.index

# Start Preprocessing

from ast import literal_eval

# pandas store list as string; need to convert back

temp = []
for ticker in sample2.index:
    d = {}
    d['ticker'] = ticker
    for doc in literal_eval(sample2.loc[ticker, '10K_files']):
        if len(doc) != 0:
            d['type'] = '10K'
            d['file'] = doc
            folder = path + ticker + "/10-K/" + doc + "/"
            file = os.listdir(folder)[0]
            file_name = folder + "/" + file
            d['ix'], d['start'], d['end'] = identify_MDA_save(file_name)
            temp.append(d)
    print(d)
    for doc in literal_eval(sample2.loc[ticker, '10Q_files']):
        d['type'] = '10Q'
        d['file'] = doc
        #        file_name = path+ticker+"/10-Q/"+doc+'/filing-details.html'
        folder = path + ticker + "/10-Q/" + doc + "/"
        file = os.listdir(folder)[0]
        file_name = folder + "/" + file
        d['ix'], d['start'], d['end'] = identify_MDA_save(file_name)
        temp.append(d)
    print(d)

df = pd.DataFrame(temp)

df.to_pickle(path[:-8] + '/sample2_scan.pkl')


# Statistics Overview
df2 = pd.read_pickle(path[:-8]+'/sample2_scan.pkl')
df2.head()