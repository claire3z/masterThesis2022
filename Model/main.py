# This is a sandbox / sketchbook Python script.
import pandas as pd
import time
from bs4 import BeautifulSoup
import re
import os
import random
from ast import literal_eval # pandas store list as string; need to convert back


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
            for i in range(len(ends)): ### CORRECTION HERE!
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





### 2021.11.22 Processing the rest of the tech samples

data_root = "C:/Users/clair/Desktop/Thesis/masterThesis2022/Data/"
path = data_root+'Samples/Information Technology/'
sample = pd.read_csv(data_root+'statistics_samples1.csv')

# Add additional tickers
add_tickers = ['AVGO_Avago Technologies_0001441634','AVGO_Broadcom Corp_0001054374','AVGO_Broadcom Merged_0001649338','NXPI_0001193125']
# Need to change the folder name in NXP from 20-F to 10-K and add an empty folder '10-Q'
for ticker in add_tickers:
    K = os.listdir(path+ticker+"/10-K/")
    Q = os.listdir(path+ticker+"/10-Q/")
    add_sample = pd.DataFrame({'ticker':[ticker], '10K_files':str(K), '10Q_files':str(Q), 'k_count':[len(K)], 'q_count':[len(Q)]})
    sample = sample.append(add_sample)

sample.set_index('ticker', inplace=True)
print(sample.index)

type(sample['10K_files'][0])
type(sample['10K_files'][-1])


# Start Preprocessing
temp = []
for ticker in sample.index:
    for doc in literal_eval(sample.loc[ticker, '10K_files']): # pandas store list as string; need to convert back
        if len(doc) != 0:
            d = {}
            d['ticker'] = ticker
            d['type'] = '10K'
            d['file'] = doc
            folder = path + ticker + "/10-K/" + doc + "/"
            file = os.listdir(folder)[0]
            file_name = folder + "/" + file
            d['ix'], d['start'], d['end'] = identify_MDA_save(file_name)
            temp.append(d)
    print(d)
    for doc in literal_eval(sample.loc[ticker, '10Q_files']):
        if len(doc) != 0:
            d = {}
            d['ticker'] = ticker
            d['type'] = '10Q'
            d['file'] = doc
            # file_name = path+ticker+"/10-Q/"+doc+'/filing-details.html' # sometimes only available in .txt
            folder = path + ticker + "/10-Q/" + doc + "/"
            file = os.listdir(folder)[0]
            file_name = folder + "/" + file
            d['ix'], d['start'], d['end'] = identify_MDA_save(file_name)
            temp.append(d)
    print(d)

df = pd.DataFrame(temp)
df.to_pickle(data_root + '/sample1_scan.pkl')
df.to_csv(data_root+'/sample1_scan.csv')

# Statistics Overview
df1 = pd.read_pickle(data_root +'/sample1_scan.pkl')
df1.head()

### NLP POS and Chunking Revisit

# SpaCy
import spacy
from spacy.matcher import Matcher
from spacy.tokens import Span
from spacy import displacy

nlp = spacy.load("en_core_web_sm")
nlp.pipe_names #['tok2vec', 'tagger', 'parser', 'ner', 'attribute_ruler', 'lemmatizer']

text = "Revenue grew by 5% in the quarter as compared to last quarter. The growth was mainly driven by increase in customer demand."
doc = nlp(text)

for sentence in doc.sents:
    print(sentence)

for nounphrase in doc.noun_chunks:
    print(nounphrase)

for chunk in doc.noun_chunks:
    print(chunk.text, '->',chunk.root.text, '->',chunk.root.dep_,'->',
            chunk.root.head.text)

for token in doc:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop)

# Part-of-Speech Tags and Dependency Labels
[token.pos_ for token in doc] #['NOUN', 'NOUN', 'AUX', 'ADV', 'VERB', 'ADP', 'NOUN', 'ADP', 'NOUN', 'NOUN', 'PUNCT']
[token.tag_ for token in doc] #['NN', 'NN', 'VBD', 'RB', 'VBN', 'IN', 'NN', 'IN', 'NN', 'NN', '.']
[token.dep_ for token in doc] #['compound', 'nsubjpass', 'auxpass', 'advmod', 'ROOT', 'agent', 'pobj', 'prep', 'compound', 'pobj', 'punct']

# Chunks
[chunk.text for chunk in doc.noun_chunks] #['Revenue', '5%', 'the quarter', 'last quarter', 'The growth', 'increase', 'customer demand']

[verb.lemma_ for verb in doc if verb.dep_ == 'ROOT'] #['grow', 'drive']


s = {}
for word in doc:
    if word.dep_ == "ROOT":
        root = word
        s['verb'] = root
        break
for child in root.children:
    print(child, child.dep_)
    if child.dep_ == "nsubj":
        nsubj = child.text
        nsubj_subtree = ''.join(w.text_with_ws for w in child.subtree).strip()
        s['subj'] = nsubj_subtree
    if child.dep_ == "pobj":
        pobj = child.text
        pobj_subtree = ''.join(w.text_with_ws for w in child.subtree).strip()
        s['subj'] = pobj_subtree


### 2021.11.25
# Collect all the verbs in MD&A
# Sentence length histogram
# Top 20 most frequent words - colored bars
# Top 20 n-gram
# Word clouds

path = "C:/Users/clair/Desktop/Thesis/masterThesis2022/Data/"

df = pd.read_pickle(path+'/scan_samples1.pkl')
df.drop('Unnamed: 0', axis=1, inplace=True)
df['type'].replace("10Q","10-Q", inplace=True)
df['type'].replace("10K","10-K", inplace=True)
df['type'].unique()
df.head()

row = df.iloc[0,:]
def get_MDA(row):
    ticker = row.name
    type_= row['type']
    file = row['file']
    folder = path + 'Samples/Information Technology/' + ticker + "/" + type_ + "/" + file + "/"
    file_name = folder + "/" + os.listdir(folder)[0]

    with open(file_name) as f:
        soup_html = BeautifulSoup(f, 'html.parser')

    soup_text = soup_html.get_text(strip=True)
    soup_text = soup_text.replace('\xa0', '').replace('\n', '')

    return soup_text[row.start:row.end]

df2 = df.iloc[2:4,:].copy()
df2['MDA'] = df2.apply(lambda row: get_MDA(row),axis=1)

text = 'Item2. Management’s Discussion and Analysis of Financial Condition and Results of OperationsCAUTIONARY STATEMENT REGARDING FORWARD-LOOKING INFORMATIONWe make statements in this report, and we may from time to time make other written reports and oral statements, regarding our outlook or expectations for financial, business or strategic matters regarding or affecting us that are “forward-looking statements” within the meaning of the Private Securities Litigation Reform Act of 1995, as amended, all of which are based on management’s current expectations and are subject to risks and uncertainties which change over time and may cause results to differ materially from those set forth in the statements. One can identify these forward-looking statements by their use of words such as “anticipates,” “expects,” “plans,” “will,” “estimates,” “forecasts,” “projects” and other words of similar meaning, or negative variations of any of the foregoing. One can also identify them by the fact that they do not relate strictly to historical or current facts. Such forward-looking statements include, but are not limited to, statements relating to the Company’s growth strategy, financial results, product development, product approvals, product potential and development programs. One must carefully consider any such statement and should understand that many factors could cause actual results to differ materially from the Company’s forward-looking statements. These factors include inaccurate assumptions and a broad variety of other risks and uncertainties, including the impact of the global outbreak of COVID-19 and other risks and uncertainties some that are known and some that are not. No forward-looking statement can be guaranteed and actual future results may vary materially. The factors described in Part II. Item 1A. Risk Factors of this report or otherwise described in our filings with the SEC, provide examples of risks, uncertainties and events that may cause our actual results to differ materially from the expectations expressed in our forward-looking statements, including, but not limited to:•difficulties in operating as an independent company;•costs and temporary business interruptions related to the Separation;•competition from generic and /or biosimilar products as our products lose patent protection;•expanded competition in the women\'s health market;•difficulties with performance of third parties we will rely on for our business growth;•the failure of any supplier to provide substances, materials, or services as agreed;•difficulties developing and sustaining relationships with commercial counterparties;•increased “brand” competition in therapeutic areas important to our long-term business performance;•expiration of current patents or loss of patent protection for our products;•difficulties and uncertainties inherent in the implementation of our acquisition strategy;•pricing pressures, both in the United States and abroad, including rules and practices of managed care groups, judicialdecisions and governmental laws and regulations related to Medicare, Medicaid and health care reform,pharmaceutical reimbursement and pricing in general;•the impact of the global COVID-19 pandemic and any future pandemic, epidemic, or similar public health threat, onour business, operations and financial performance;•changes in government laws and regulations, including laws governing intellectual property, and the enforcementthereof affecting our business;•efficacy or safety concerns with respect to marketed products, whether or not scientifically justified, leading to productrecalls, withdrawals or declining sales;•future actions of third-parties including significant changes in customer relationships or changes in the behavior andspending patterns of purchasers of health care products and services, including delaying medical procedures, rationingprescription medications, reducing the frequency of physician visits and forgoing health care insurance coverage;•loss of key employees or inability to identify and recruit new employees;•legal factors, including product liability claims, antitrust litigation and governmental investigations, including taxdisputes, environmental concerns and patent disputes with branded and generic competitors, any of which couldpreclude commercialization of products or negatively affect the profitability of existing products;-31-•cyber-attacks on, or other failures, accidents, or security breaches of, our or third-party providers’ informationtechnology systems, which could disrupt our operations;•lost market opportunity resulting from delays and uncertainties in the approval process of the FDA and foreignregulatory authorities;•increased focus on privacy issues in countries around the world, including the United States and the European Union, and a more difficult legislative and regulatory landscape for privacy and data protection that continues to evolve with the potential to directly affect our business, including recently enacted laws in a majority of states in the United States requiring security breach notification;•changes in tax laws including changes related to the taxation of foreign earnings;•changes in accounting pronouncements promulgated by standard-setting or regulatory bodies, including the Financial Accounting Standards Board and the SEC, that are adverse to us; and•economic factors over which we have no control, including changes in inflation, interest rates and foreign currency exchange rates.It is not possible to predict or identify all such factors. Consequently, the reader should not consider the above list or any other such list to be a complete statement of all potential risks or uncertainties. Further, any forward-looking statement speaks only as of the date on which it is made, and we undertake no obligation to update or revise any forward-looking statement to reflect events or circumstances after the date on which the statement is made or to reflect the occurrence of unanticipated events, except as otherwise may be required by law.GeneralThe following Management’s Discussion and Analysis of Financial Condition and Results of Operations is intended to assist the reader in understanding the Company’s financial condition and results of operations. The following discussion and analysis should be read in conjunction with the Company’s Condensed Consolidated Financial Statements included in Part I, Item 1 of this report and with our audited combined financial statements, including the accompanying notes, and Management’s Discussion and Analysis of Financial Condition and Results of Operations included in the Form 10.  Operating results discussed herein are not necessarily indicative of the results of any future period.The Company is a global healthcare company that develops and delivers innovative health solutions through a portfolio of prescription therapies within women\'s health, biosimilars and established brands. The Company sells these products through various channels including drug wholesalers and retailers, hospitals, government agencies and managed health care providers such as health maintenance organizations, pharmacy benefit managers and other institutions. The Company operates six manufacturing facilities, which are located in Belgium, Brazil, Indonesia, Mexico, the Netherlands and the UK.Separation from MerckPursuant to the Separation and Distribution Agreement, the Separation from Merck was completed on June 2, 2021, in which Organon\'s Common Stock was distributed to all holders of outstanding shares of Merck Common Stock as of the close of business on the Record Date. For each share of Merck Common Stock held, such holder received one tenth of one share of Common Stock, and holders received cash in lieu of any fractional share of Common Stock they otherwise would have been entitled to receive in connection with the Distribution. Organon is now a standalone publicly traded company, and on June 3, 2021, regular-way trading of the Common Stock commenced on the New York Stock Exchange ("NYSE") under the symbol "OGN." Until the Separation on June 2, 2021, Organon’s historical combined financial statements were prepared on a standalone basis and were derived from Merck’s consolidated financial statements and accounting records.For the period subsequent to June 2, 2021, as a standalone publicly traded company, Organon presents its financial statements on a consolidated basis. The Condensed Consolidated Financial Statements have been prepared in accordance with accounting principles generally accepted in the United States of America.Recent DevelopmentsBusiness DevelopmentIn June 2021, Organon completed its acquisition of Alydia Health, a commercial-stage medical device company. Alydia’s device, the Jada System, is intended to provide control and treatment of abnormal postpartum uterine bleeding or hemorrhage when conservative management is warranted. The transaction consideration included a $219 million upfront-32-payment, of which $50 million was paid in April 2021 and the remaining $169 million was paid by Organon upon the close of the acquisition on June 16, 2021. Additionally, there is a $25 million sales based contingent milestone payment that will be paid by Organon upon achievement. The contingent milestone payment was not probable as of June 30, 2021 and therefore has not been accrued. The transaction was accounted for as an asset acquisition as substantially all of the value was concentrated in a single identifiable asset. This resulted in an intangible of $247million attributed to the Jada System device. This asset is subject to amortization on a straight-line basis over its expected useful life of 11 years. In addition to the intangible asset, we also recorded other net liabilities of $7 million, a deferred tax liability of $44 million related to the intangible asset, and compensation expense of $23 million, which was recorded inSelling General and Administrative Expenses. Of the $23 million of compensation expense, $19.4 million were related to accelerated vesting of Alydia stock-based compensation awards.In July 2021, Organon and ObsEva entered into a license agreement whereby Organon will license the global development, manufacturing and commercial rights to ebopiprant (OBE022). Ebopiprant is an investigational, orally active, selective prostaglandin F2α (PGF2α) receptor antagonist being evaluated as a potential treatment for preterm labor by reducing inflammation and uterine contractions. Under the terms of the license agreement, Organon will gain exclusive worldwide rights to develop and commercialize ebopiprant. ObsEva is entitled to receive tiered double-digit royalties on commercial sales, up to $90 million in development and regulatory milestone payments, and up to $385 million sales-based milestone payments that will be paid by Organon upon achievement. Upon execution of the agreement, Organon paid a $25 million upfront payment.DebtIn April 2021, in connection with the Separation, Organon Finance 1 LLC (“Organon Finance 1”), a subsidiary of Merck, issued €1.25 billion aggregate principal amount of 2.875% senior secured notes due 2028, $2.1 billion aggregate principal amount of 4.125% senior secured notes due 2028 and $2.0 billion aggregate principal amount of 5.125% senior unsecured notes due 2031 (collectively, "the notes"). Interest payments are due semiannually on October 30 and April 30. As part of the Separation, on June 2, 2021, Organon and a wholly-owned Dutch subsidiary of Organon (the “Dutch Co-Issuer”) assumed the obligations under the notes as co-issuers, Organon Finance 1 was released as an obligor under the notes, and certain subsidiaries of Organon agreed to guarantee the notes. Each series of notes was issued pursuant to an indenture dated April 22, 2021, between Organon and U.S. Bank National Association. Organon and the Dutch Co-Issuer assumed the obligations under the notes pursuant to a first supplemental indenture to the relevant indenture, and the guarantors agreed to guarantee the notes pursuant to a second supplemental indenture to the relevant indenture.Also upon Separation on June 2, 2021, Organon entered into a credit agreement providing for a Term Loan B Facility, consisting of (i) a U.S. dollar denominated senior secured “tranche B” term loan in the amount of $3.0 billion due 2028 (ii) a euro denominated senior secured “tranche B” term loan in the amount of €750 million due 2028: and a Revolving Credit Facility (“Revolving Credit Facility”), in an aggregate principal amount of up to $1 billion, with a five-year term that matures in 2026.Borrowings made under the Revolving Credit Facility, initially bear interest at (i) in U.S. Dollars at 2.00% in excess of an Adjusted London Interbank Offered Rate (“Adjusted LIBOR”) (subject to a floor of 0.00%) or 1.00% in excess of an alternate base rate ("ABR"), at our option and (ii) in euros, at 2.00% in excess of an adjusted Euro Interbank Offer Rate (“Adjusted EURIBOR”). The Term Loan B Facility bears interest at (i) denominated in U.S. Dollars, at 3.00% in excess of Adjusted LIBOR (subject to a floor of 0.50%) or 2.00% in excess of ABR, at our option and (ii) denominated in euros, at 3.00% in excess of Adjusted EURIBOR (subject to a floor of 0.00%). The interest rate on revolving loans under the Revolving Credit Facility is subject to a step-down based on meeting a leverage ratio target and is subject to a commitment fee which applies to the unused portion of the revolving facility, initially equal to 0.50% and subject to a step-down to 0.375% based on meeting a leverage ratio target. The Revolving Credit Facility is also subject to customary financial covenants.Organon used the net proceeds from the notes offering, together with available cash on its balance sheet and borrowings under senior secured credit facilities, to distribute $9.0 billion to Merck and to pay fees and expenses related to the Separation.Net Investment HedgeIn June 2021, €1.75 billion in the aggregate of both the euro-denominated term loan (€750 million) and the 2.875% euro-denominated secured notes (€1.25 billion) have been designated, and effective as, economic hedges of the net investment in a foreign operation. As a result, $56 million of foreign currency gains due to spot rate fluctuations on the euro-denominated debt instruments are included in foreign currency translation adjustment inOther Comprehensive Incomefor the three and six months ended June30, 2021.COVID-19 Update-33-Organon remains focused on protecting the safety of its employees and supporting Organon’s communities in response to the COVID-19 pandemic. COVID-19-related disruptions, including patients’ inability to access health care providers, prioritization of COVID-19 patients, as well as social distancing measures have negatively affected our results.In the second quarter of 2021, the negative impact of the COVID-19 pandemic to Organon sales was estimated to be approximately $120 million. Our product portfolio is comprised of physician prescribed products, mainly in established brands, which have been affected by social distancing measures and fewer medical visits. Additionally, our portfolio in Women\'s Health includes products which are physician administered, which have been affected by limited access to physicians and healthcare centers. These impacts, as well as the prioritization of COVID-19 patients at health care providers, resulted in reduced administration of many products within established brands particularly for respiratory and cardiovascular products and to a lesser extent,Nexplanon/Implanon NXT, throughout the first half of 2021.We believe that global health systems and patients continue to adapt to the evolving impacts of the COVID-19 pandemic, and although we experienced recoveries during the second quarter of 2021 as compared to the comparable period in 2020, we expect that ongoing negative impacts will persist through 2021 and will continue to principally affect products within established brands and women’s health, primarilyNexplanon/Implanon NXT.Operating expenses in the second quarter and first six months of 2021 were higher primarily due to the effect of lower promotional and selling costs incurred in the second quarter and first six months of 2020 attributable to the COVID-19 pandemic as well as incremental costs associated with establishing Organon as a standalone company.Operating ResultsSales OverviewThree Months Ended June 30,% Change% Change Excluding Foreign ExchangeSix Months Ended June 30,% Change% Change Excluding Foreign Exchange($ in millions)2021202020212020United States$339$30312%12%$690$697(1)%(1)%International1,2571,2243%(4)%2,4122,608(8)%(13)%Total$1,595$1,5265%(1)%$3,101$3,306(6)%(11)%U.S. plus international may not equal total due to rounding.Worldwide sales were $1.6 billion for the second quarter of 2021, an increase of 5% compared with the second quarter of 2020. The increase is primarily due to higher sales of women’s health products, including Nexplanon/Implanon NXT, Follistim AQ (follitropin beta injection) and Ganirelix Acetate Injection, as well as higher sales of biosimilar products resulting from the continued uptake of Renflexis (infliximab-abda) in the United States and the uptake of Aybintio (bevacizumab) in the European Union ("EU"). The sales increase was partially offset by ongoing generic competition for cardiovascular products Zetia and Vytorin (ezetimibe and simvastatin) mainly in Japan, decline in sales due to the volume-based procurement program (the "VBP") in China, an expiration of distribution agreement in Korea for Rosuzet in December 2020, and decreased demand for Cozaar/Hyzaar.Worldwide sales were $3.1 billion for the first six months of 2021, a decline of 6% compared with the first six months of 2020. The decline during the first six months of 2021 primarily reflects decreases across markets due to ongoing generic competition for products within the established brands business, particularly for cardiovascular products Zetia and Vytorin (ezetimibe and simvastatin), lower sales of respiratory products Singulair (montelukast), Dulera and Nasonex, and generic competition for women’s health product NuvaRing (etonogestrel/ethinyl estradiol vaginal ring), as well as the negative impact of VBP in China. The sales decline was offset by higher sales of women\'s health products Nexplanon/Implanon NXT, Follistim AQ (follitropin beta injection) and Ganirelix Acetate Injection due to higher demand, and higher sales of biosimilars resulting from the continued uptake of Renflexis mainly in the United States and Aybintio in the EU.The total impact of loss of exclusivity ("LOE") is approximately $130 million during the second quarter of 2021 compared to the second quarter of 2020 and approximately $210 million for the first six months of 2021 compared to the same period in 2020. Additionally, the VBP in China continues to unfavorably affect a number of our products with an impact to sales of approximately $40 million for the second quarter of 2021 compared to the second quarter of 2020 and approximately $90 million for the first six months of 2021 compared to the same period in 2020. The COVID-19 pandemic continued to negatively affect sales in the second quarter of 2021 across several markets. For the first six months of 2021, the sales decline was partially offset by the COVID-19 recoveries as well as by higher sales in women\'s products and biosimilar products.-34-Organon’s operations include a portfolio of products. Highlights of the sales of Organon’s products for the three months and six months ended June 30, 2021 and 2020 are provided below. See Note 16 “Product and Geographic Information” to the Condensed Consolidated Financial Statements for further details on sales of our products.Women’s HealthThree Months Ended June 30,% Change% Change Excluding Foreign ExchangeSix Months Ended June 30,% Change% Change Excluding Foreign Exchange($ in millions)2021202020212020Nexplanon/Implanon NXT$184$13240%39%$368$32613%12%NuvaRing5363(16)%(19)%98126(22)%(24)%Follistim AQ654448%40%1178537%31%Ganirelix Acetate Injection3114117%102%6030101%89%ContraceptionWorldwide sales ofNexplanon/Implanon NXT, a single-rod subdermal contraceptive implant, increased 40% and 13% in the second quarter and first six months of 2021, respectively, primarily reflecting recovery from the COVID-19 pandemic in the United States, Europe and Canada, favorable impact from pricing, and phasing of tenders in Latin America during the second quarter of 2021.Worldwide sales ofNuvaRing, a vaginal contraceptive product, declined 16% and 22% in the second quarter and first six months of 2021 primarily due to ongoing generic competition in the United States and the EU. We expect a continued decline in NuvaRing sales as a result of generic competition. In addition to sales of brandedNuvaRing, we have an agreement with a generic manufacturer that authorizes the sale of generic etonogestrel/ethinyl estradiol vaginal ring in the United States. Under the terms of the agreement, we are reimbursed on a cost-plus basis by the generic manufacturer for supplying finished goods and receive a share of the net profits recorded by the generic manufacturer. Under the terms of the agreement, our share in the profits declines over time as new participants enter the market. Revenues from this arrangement were $19 million and $49 million for the second quarter of 2021 and 2020, respectively, and $51million and $67million for the first six months of 2021 and 2020, respectively. Revenues for the second quarter of 2021 and the first six months of 2021 primarily reflect our share of the profits. Revenues for the second quarter and the first six months of 2020 reflect supply sales of the generic product to the manufacturer. The decline in revenue for the second quarter and first six months of 2021 is due to the entry of a new market participant. Given the nature of this arrangement, we expect revenue under this arrangement to continue to decline significantly for the second half of 2021.FertilityWorldwide sales of Follistim AQ (marketed in most countries outside the United States as Puregon), a fertility treatment, increased 48% and 37% in the second quarter and the first six months of 2021, respectively, primarily due to volume growth in the United States as well as recovery from the COVID-19 pandemic in the United States Europe, Canada and China, partially offset by overall unfavorable discount rates in the U.S. for the six months ended June 30, 2021.Worldwide sales of Ganirelix Acetate Injection (marketed in certain countries outside the United States as Orgalutran), a fertility treatment, increased 117% in the second quarter of 2021, primarily due to the recovery from the COVID-19 pandemic in Europe, Canada and China. For the first six months of 2021, sales increased 101% primarily due to increased demand in the United States as well as recovery from the COVID-19 pandemic in the United States, Europe, Canada and China.-35-BiosimilarsThree Months Ended June 30,% Change% Change Excluding Foreign ExchangeSix Months Ended June 30,% Change% Change Excluding Foreign Exchange($ in millions)2021202020212020Renflexis$43$3041%38%$81$5938%36%Ontruzant221920%13%454011%3%Brenzys1111(2)%(16)%2129(27)%(35)%The following biosimilar products are part of a development and commercialization agreement between Organon and Samsung Bioepis entered into in 2013. See Note 3 to the Condensed Consolidated Financial Statements. Our commercialization territories under the agreement vary by product as noted below.Renflexisis a biosimilar to Remicade (infliximab) for the treatment of certain inflammatory diseases. Sales growth in the second quarter and first six months of 2021 was driven primarily by continued demand growth in the United States since launch in 2017, partially offset by higher discount rates. We have commercialization rights toRenflexisin countries outside the EU, Korea, China, Turkey and Russia.Ontruzant(trastuzumab-dttb) is a biosimilar to Herceptin (trastuzumab) for the treatment of HER2-overexpressing breast cancer and HER2-overexpressing metastatic gastric or gastroesophageal junction adenocarcinoma. For the second quarter and first six months of 2021, sales reflect uptake since the July 2020 launch in the United States, partially offset by a decrease in the EU reflecting increasing competitive pressures and price erosion. We have commercialization rights toOntruzantin countries outside of Korea and China.Brenzys(etanercept) is a biosimilar to Enbrel (etanercept) for the treatment of certain inflammatory diseases. Sales in the second quarter and first six months of 2021 decreased 2% and 27%, respectively, primarily due to timing of shipments to Brazil related to government orders. We have commercialization rights toBrenzysin countries outside of the United States, the E.U., Korea, China and Japan.Recent LaunchesAybintiois a biosimilar to Avastin (bevacizumab) for the treatment of metastatic carcinoma of the colon or rectum, metastatic non-squamous, non-small cell lung cancer, metastatic renal cell carcinoma, metastatic cervical cancer, epithelial ovarian, fallopian tube, or primary peritoneal cancer and metastatic breast cancer. We recorded sales of $8 million and $16 million during the second quarter and first six months of 2021, respectively, with no comparable sales during the second quarter and first six months of 2020 due to the approval ofAybintioin the EU in August 2020 and its launch in September 2020. We currently have no plan for the timing of any launch ofAybintioin the United States nor do we know when such timing would be determined. We have commercialization rights toAybintioin the United States, Canada, Germany, Italy, France, the UK and Spain.Hadlima (adalimumab-bwwd) is a biosimilar to Humira (adalimumab) for the treatment of certain inflammatory diseases. We have worldwide commercialization rights to Hadlima in countries outside of the EU, Korea, China, Turkey and Russia. Samsung Bioepis reached a global settlement with AbbVie permitting us to launch Hadlima in the United States in June 2023 and outside of the United States starting in 2021. Hadlima is currently approved in the United States, Australia, Canada, and Israel. Hadlima was launched in Australia and Canada in February 2021. Following these launches, we recorded modest sales during the second quarter and first six months of 2021.Established BrandsEstablished brands represents a broad portfolio of well-known brands, which generally are beyond market exclusivity, including leading brands in cardiovascular, respiratory, dermatology and non-opioid pain management, for which generic competition varies by market.-36-CardiovascularThree Months Ended June 30,% Change% Change Excluding Foreign ExchangeSix Months Ended June 30,% Change% Change Excluding Foreign Exchange($ in millions)2021202020212020Zetia/Vytorin$144$176(18)%(24)%$276$374(26)%(31)%Atozet1211155%(3)%233238(2)%(9)%Rosuzet1831(42)%(43)%3363(47)%(49)%Cozaar/Hyzaar8698(12)%(17)%177200(12)%(17)%Zocor16164%(2)%3139(21)%(26)%Combined global sales ofZetia(marketed in most countries outside of the United States asEzetrol) andVytorin(marketed outside of the United States asInegy), medicines for lowering LDL cholesterol, declined 18% during the second quarter of 2021 primarily driven by lower sales ofEzetrolin Japan. Sales decreased 26% in the first six months of 2021 primarily driven by lower sales ofEzetrolin Japan, lower demand in the United States due to generic competition, as well as lower sales ofEzetrolandInegyin the EU. The patent that provided market exclusivity forEzetrolin Japan expired in September 2019 and generic competition began in June 2020. The EU patents forEzetrolandInegyexpired in April 2018 and April 2019, respectively. Accordingly, we are experiencing sales declines in these markets as a result of generic competition and expects the declines to continue. Higher demand forEzetrolin China during the second quarter of 2021 partially offset the sales decline.Sales ofAtozet(ezetimibe and atorvastatin calcium) (marketed outside of the United States), a medicine for lowering LDL cholesterol, increased 5% in the second quarter of 2021 primarily due to volume growth in France and a slight increase in sales in various markets, partially offset by lower demand in Germany due to competition. Sales ofAtozetdeclined 2% in the first six months of 2021 due to lower demand in the EU, primarily in Germany and Spain due to competition, coupled with unfavorable pricing, partially offset by a volume increase in France and higher demand in the Asia Pacific region.Sales ofRosuzet(ezetimibe and rosuvastatin calcium) (marketed outside of the United States), a medicine for lowering LDL cholesterol, declined 42% and 47% in the second quarter and first six months of 2021, respectively, due to the expiration of a distribution agreement in Korea in December 2020. We expect sales to continue to decline for the second half of 2021.Combined global sales ofCozaar(losartan potassium), andHyzaar(losartan potassium and hydrochlorothiazide) (a combination of Cozaar and hydrochlorothiazide that is marketed in Japan asPreminent), a medicine for the treatment of hypertension, declined 12% in both the second quarter and first six months of 2021. The decrease in the second quarter is primarily due to a shift in product and channel mix and lower demand in China as well as lower demand as a result of growing generic competition in Japan. The sales decrease in the first six months of 2021 reflects lower demand in the United States, lower demand due to generic competition in Japan and the Asia Pacific region, the effect of the shift in product mix and lower demand in China, and lower sales in Canada as sales in the second quarter of 2020 was higher due to competitor supply shortages.Worldwide sales ofZocor(simvastatin), a statin for modifying cholesterol, remained relatively flat in the second quarter of 2021. Sales ofZocordecreased 21% in the first six months of 2021, primarily due to lower volumes in China due to the VBP impact.RespiratoryThree Months Ended June 30,% Change% Change Excluding Foreign ExchangeSix Months Ended June 30,% Change% Change Excluding Foreign Exchange($ in millions)2021202020212020Singulair$92$100(8)%(12)%$199$255(22)%(26)%Nasonex52496%(1)%95120(21)%(24)%Dulera523934%31%91122(26)%(27)%Worldwide sales ofSingulair, a once-a-day oral medicine for the chronic treatment of asthma and for the relief of symptoms of allergic rhinitis, declined 8% in the second quarter of 2021 primarily due to the lower performance in Japan attributable to generic competition as well as timing of shipments in Japan in the second quarter of 2020, VBP impact in China partially offset by the recovery from the COVID-19 pandemic.Singulairsales in the first six months of 2021 decreased 22% primarily attributable to the impact of VBP in China, lower volume in Japan due to generic competition as well as the timing of shipments, and ongoing impact of the COVID-19 pandemic in the Asia Pacific region. Sales for the first six months of 2021-37-also reflect lower demand in Europe and Canada in the beginning of 2021 due to the COVID-19 pandemic. The sales decline was partially offset by the recovery from the COVID-19 pandemic in China.Global sales ofNasonex, an inhaled nasal corticosteroid for the treatment of nasal allergy symptoms, increased 6% in the second quarter of 2021 primarily due to higher demand in China and favorable performance in Russia, partially offset by lower sales in the United States due to the impact of COVID-19 pandemic and generic competition in Japan. Global sales ofNasonexdecreased 21% in the first six months of 2021 primarily driven by lower demand impacted by the COVID-19 pandemic across several markets in the United States, Europe, and Latin America, and generic competition in Japan, partially offset by higher demand in China.Global sales ofDulera, a combination medicine for the treatment of asthma, increased 34% in the second quarter of 2021 primarily due to favorable discount rates in the United States. For the first six months of 2021, global sales ofDuleradecreased 26% largely due to significant buy-in in the six months of 2020 related to the COVID-19 pandemic, partially offset by the favorable discount rates in the United States in the second quarter of 2021.Non-Opioid Pain, Bone and DermatologyThree Months Ended June 30,% Change% Change Excluding Foreign ExchangeSix Months Ended June 30,% Change% Change Excluding Foreign Exchange($ in millions)2021202020212020Arcoxia$62$65(4)%(9)%$119$135(12)%(16)%Sales ofArcoxia(etoricoxib), for the treatment of arthritis and pain, were slightly lower in the second quarter of 2021 primarily due to the impact of VBP in China. Sales ofArcoxiafor the first six months of 2021 decreased 12% primarily due to the impact of VBP in China and lower demand in the Asia Pacific region attributable to the COVID-19 pandemic. The sales decline was also attributable to lower demand in certain markets in the Middle East and Russia that occurred during the first quarter of 2021.OtherThree Months Ended June 30,% Change% Change Excluding Foreign ExchangeSix Months Ended June 30,% Change% Change Excluding Foreign Exchange($ in millions)2021202020212020Proscar$32$51(38)%(43)%$64$94(32)%(37)%Worldwide sales ofProscar, for the treatment of symptomatic benign prostate enlargement, declined 38% and 32% in the second quarter and first six months of 2021 primarily due to lower performance reflecting the impact of VBP in China.-38-Costs, Expenses and OtherThree Months Ended June 30,% ChangeSix Months Ended June 30,% Change($ in millions)2021202020212020Cost of sales$583$46027%$1,174$99818%Selling, general and administrative41628446%79860133%Research and development765149%1439649%Restructuring costs119*231*Other (income) expense, net8210*8034*$1,158$82441%$2,197$1,76025%* Calculation not meaningful.Cost of SalesCost of sales increased 27% in the second quarter of 2021 compared to the second quarter of 2020. The increase in cost of sales for the second quarter is primarily due to increases in manufacturing costs and certain costs related to tolling arrangements with Merck which were not in place in the second quarter of 2020. For the first six months of 2021, cost of sales increased 18% compared to the first six months of 2020. The increase during the period reflects increases in manufacturing costs absorbed by Organon, increase in stand up costs, and cost related to tolling arrangements with Merck, which were not in place during the comparable prior year period. The increase also reflects increases in direct corporate Organon costs.Gross margin was 63% in the second quarter of 2021 compared with 70% in the second quarter of 2020. Gross margin was 62% in the first six months of 2021 compared with 70% in the first six months of 2020. The gross margin declines reflect an increase in stand up costs, as well as certain costs related to tolling arrangements with Merck, which have lower gross margin percentages compared to product sales.Selling, General and AdministrativeSelling, general and administrative expenses increased 46% and 33% in the second quarter of 2021 and the first six months of 2021, respectively, due to costs incurred to establish Organon as a standalone entity, higher employee related costs, and higher selling and promotional costs.Research and DevelopmentResearch and development expenses increased 49% in the second quarter of 2021 and 49% for the first six months of 2021 primarily reflecting higher employee related costs incurred to establish Organon as a standalone entity.Restructuring CostsCertain of our operations have been affected by restructuring plans initiated by Merck. The decline in restructuring costs is due to lower allocated costs from Merck during the second quarter and the first six months of 2021 compared to the comparable periods of 2020. See Note 5 to our Condensed Consolidated Financial Statements.Other (Income) Expense, NetThe increase in other (income) expense, net during the second quarter of 2021 and the first six months of 2021 is primarily attributable to $62 million of interest expense related to the issuance of debt instruments during the second quarter of 2021.Taxes on IncomeThe effective income tax rates were 1.4% and 16.5% for the second quarter of 2021 and 2020, respectively, and reflect the beneficial impact of foreign earnings and the $70 million tax benefit relating to a portion of the non-U.S. step-up of tax basis associated with Organon\'s Separation from Merck. The effective income tax rates for the first six months of 2021 and 2020, were 8.6% and 14.6%, respectively. The decrease in effective interest rates for the six months ended June 30, 2021 reflect the beneficial impact of foreign earnings, the $70 million tax benefit relating to a portion of the non-U.S. step-up of tax basis as well as the income tax benefit recognized in connection with the conclusion of the Internal Revenue Service (IRS) examination of Merck’s 2015-2016 U.S. federal income tax returns. As a result of the examination conclusion, we reflected an allocation from Merck of $18 million in the Condensed Consolidated Financial Statements representing our portion of the payment made to the IRS. Our portion of reserves for unrecognized tax benefits for the years under examination exceeded the allocated adjustments relating to this examination period and therefore for the six months ended June 30, 2021, we included a $29 million net tax benefit. This net benefit reflects reductions in reserves for unrecognized tax benefits and other related liabilities for tax positions relating to the years that were under examination.-39-Income/Loss from Discontinued OperationsThe historical results of certain Merck non-U.S. legal entities that were contributed to Organon in connection with the Separation included operations related to other Merck products that were retained by Merck. Substantially all of the Merck Retained Products business of the Transferred Entities were contributed by Organon to Merck and its affiliates. Accordingly, the historical results of operations of the Merck Retained Products have been reflected as discontinued operations in the Condensed Consolidated Financial Statements for all periods presented.Loss from discontinued operations, net of taxes, was $4 million for the three months ended June30, 2021 and $44 million for the three months ended June30, 2020. There was no income or loss from discontinued operations, net of taxes for the first six months of 2021compared to a loss from discontinued operations of $75 million in the first six months of 2020.Net IncomeNet income was $427 million and $542 million in the second quarter of 2021 and 2020, respectively. Net income was $826 million and $1.2 billion for the first six months of 2021 and 2020. The decrease in net income for both periods reflects an increase in costs and expenses incurred to establish Organon as a standalone entity, partially offset by higher sales due to higher demand for certain of our products across several markets in the second quarter of 2021. Partial recovery for certain products from the COVID-19 pandemic also offset the increase in costs during the second quarter of 2021.Analysis of Liquidity and Capital ResourcesLiquidity and Capital ResourcesUp to the date of Separation on June 2, 2021, Organon participated in Merck’s centralized treasury model, which included its cash pooling and other intercompany financing arrangements. We have historically generated, and expect to continue to generate, positive cash flow from operations.In April 2021, in connection with the Separation, Organon Finance 1, previously a subsidiary of Merck, issued €1.25 billion aggregate principal amount of 2.875% senior secured notes due 2028, $2.1 billion aggregate principal amount of 4.125% senior secured notes due 2028 and $2.0 billion aggregate principal amount of 5.125% senior unsecured notes due 2031. The notes were assumed by Organon and the Dutch Co-Issuer. In addition, on June 2, 2021, we entered into a credit agreement providing for a $3.0 billion U.S. dollar-denominated senior secured term loan due 2028 and a euro denominated senior secured term loan in the amount of €750 million due 2028. We also entered into a secured, unsubordinated five-year revolving credit facility that provides for the availability of $1.0 billion of borrowings. As of June 30, 2021 there are no borrowings outstanding under our Revolving Credit Facility. We distributed $9.0 billion of the $9.5 billion proceeds to Merck in accordance with the terms of the Separation.After the distribution to Merck of $9.0 billion net debt proceeds and settlement of certain balances with Merck and its affiliates, we began operations as an independent company with approximately $900 million of cash and cash equivalents, which reflects approximately $400 million from Merck which will be used for the purchase of inventory from Merck upon exit of certain IOMs. At June 30, 2021, we had cash and cash equivalents of $730 million. Following the Separation, we expect to fund our ongoing operating, investing and financing requirements mainly through cash flows from operations, available liquidity through cash on hand, available capacity under our Revolving Credit Facility and access to capital markets.Working capital of continuing operations was $936million at June30, 2021 and $348million in December31, 2020. The overall increase in working capital of continuing operations was primarily driven by cash funding by Merck in connection with the Separation, offset by an increase in current liabilities with Merck primarily for inventory purchases, as well as increases in employee benefits and payroll.Cash provided by operating activities was $1.7 billion in the first six months of 2021 compared to $1.5 billion in the first six months of 2020. Cash provided by operating activities was favorably impacted by an increase in accounts payable, including amounts due to Merck, partially offset by a decline in net income.Cash used in investing activities was $287 million in the first six months of 2021 and $86 million in the first six months of 2020, primarily reflecting the asset acquisition of Alydia Health.Cash used in financing activities was $772 million in the first six months of 2021 and $1.4 billion in the first six months of 2020. The change in cash used in financing activities reflects the proceeds from the issuance of long term debt, the payment of related debt issuance costs and the settlement of  the transactions with Merck in connection with the Separation (see Note 17 to our Condensed Consolidated Financial Statements).Our ability to fund our operations and anticipated capital needs is reliant upon the generation of cash from operations, supplemented as necessary by periodic utilization of our Revolving Credit Facility. Our principal uses of cash in the-40-future will be primarily to fund our operations, working capital needs, capital expenditures, repayment of borrowings, payment of dividends and strategic business development transactions.In August 2021, the Board of Directors declared a quarterly dividend of $0.28 per share on Organon’s stock that is payable on September 13, 2021 to stockholders of record at the close of business on August 23, 2021.We believe that our financing arrangements, future cash from operations, and access to capital markets will provide adequate resources to fund our future cash flow needs.Critical Accounting EstimatesOur significant accounting policies, which include management’s best estimates and judgments, are included in Note 2 to the Condensed Consolidated Financial Statements for the year ended December31, 2020 included in our Form 10, as amended, filed on April 29, 2021. See Note 2 to the Condensed Consolidated Financial Statements for information on the adoption of new accounting standards during 2021. Other than as discussed below related to our accounting policy on stock-based compensation, there have been no changes to our accounting policies as of June 30, 2021. A discussion of accounting estimates considered critical because of the potential for a significant impact on the financial statements due to the inherent uncertainty in such estimates are disclosed in the Critical Accounting Estimates section of Management’s Discussion and Analysis of Financial Condition and Results of Operations included in Organon\'s Form 10.In connection with the Separation, and in accordance with the Employee Matters Agreement, ("EMA"), Organon\'s employees with outstanding former Merck stock-based awards received replacement stock-based awards under the 2021 Incentive Stock Plan. The plan provides for the grant of various types of awards including restricted stock unit awards, stock appreciation rights, stock options, performance-based awards and cash awards.We expense all stock-based payment awards to employees, including grants of stock options, over the requisite service period based on the grant date fair value of the awards. We determine the fair value of certain stock-based awards using the Black-Scholes option-pricing model which uses both historical and current market data to estimate the fair value. This method incorporates various assumptions such as the risk-free interest rate, expected volatility, expected dividend yield and expected life of the options. Refer to Note 11 for further details.Recently Issued Accounting StandardsFor a discussion of recently issued accounting standards, see Note 2 to the Condensed Consolidated Financial Statements.'
doc = nlp(text)
len([*doc.sents]) #181
len([*doc.noun_chunks]) #1747
# Verbs
verbs = [verb.lemma_ for verb in doc if verb.dep_ == 'ROOT']
len(verbs) #181
pd.DataFrame(verbs).value_counts()[:20].to_dict()

nouns = [noun.lemma_ for noun in doc if noun.tag_ == 'NN']
len(nouns) #1110
pd.DataFrame(nouns).value_counts()[:20].to_dict()

# directly add them will create a combined dictionary with addition of same keys
pd.DataFrame(verbs).value_counts()[:20]+pd.DataFrame(verbs).value_counts()[:20]


### 2021.11.26
# maybe we should have kept space and newline for identification of paragraphs?

def identify_MDA(file_name):
    with open(file_name) as f:
        soup_html = BeautifulSoup(f, 'html.parser')

    # CAN'T remove all tables first since ITEM 7. Management... is sometimes wrapped in a table...
    for table in soup_html.find_all('table'):
        if len(table.find_all('tr'))>3:
            table.decompose()

    soup_text = soup_html.get_text(strip=False,separator=' ') #keep sentences from different spans separated with a space
    # soup_text = soup_html.get_text(strip=True)
    # soup_text = soup_text.replace('\xa0', '').replace('\n', '')


    pattern_toc = re.compile(r"(table of contents)|(index)", flags=re.IGNORECASE)
    toc = re.search(pattern_toc, soup_text)
#    ix = len(soup_html.find_all('ix:header'))

    pattern_start = re.compile(
        r"(?<![\"|“|'])Item\s?\d?.?\s*Management[’|\']s[\s]*Discussion[\s]*and[\s]*Analysis[\s]*of[\s]*Financial[\s]*Condition[\s]*and[\s]*Results[\s]*of[\s]*Operations",
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
            pass #TODO
    else:
        start = 0
        print('\n>>>>>>COULD NOT FIND ANY START POSITION!!!<<<<<<\n')
        pass #TODO

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
            for i in range(len(ends)): ### CORRECTION HERE!
                if ends[i].start() > start + 10000:
                    end = ends[i].start()
                    break
                print('\n>>>>>>NO TOC and MORE THAN 1 END POSITIONS!!!<<<<<<\n')
                pass #TODO

    else:
        end = min(start + 50000, len(soup_text))

    return soup_text[start:end]



text = identify_MDA(path+'Samples/GOOG/10-K/0001652044-16-000012/filing-details.html') ## soup_text = soup_html.get_text(strip=True)

text2 = identify_MDA(path+'Samples/GOOG/10-K/0001652044-16-000012/filing-details.html') ## soup_text = soup_text.replace('\xa0', '').replace('\n', '')

text3 = identify_MDA(path+'Samples/GOOG/10-K/0001652044-16-000012/filing-details.html') ## soup_text = soup_html.get_text(strip=False)

text4 = identify_MDA(path+'Samples/GOOG/10-K/0001652044-16-000012/filing-details.html') ## soup_text = soup_html.get_text(strip=False,separator='\n')

text5 = identify_MDA(path+'Samples/GOOG/10-K/0001652044-16-000012/filing-details.html') ## soup_text = soup_html.get_text(strip=False,separator=' ')

text6 = identify_MDA(path+'Samples/GOOG/10-K/0001652044-16-000012/filing-details.html') ## removed all tables but can't find MDA - modified to remove table with more than 3 rows

len(text),len(text2), len(text3) , len(text4), len(text5) # (73274, 73227, 74415, 77194, 77194)
len(text6) #65769

for t in [text5, text6]:
    doc = nlp(t)
    print(len([*doc.sents]))   #324, 319, 423, 713, 474, 383
    for i in range(400):
        print(len([*doc.sents][i]),'\t',[*doc.sents][i])

### CONCLUSION: need to modify identify_MDA() as per text5 to get proper sentence segmentation

lens = []
sentences = []
for i in range(383): # text6
    if len([*doc.sents][i])>8:
        sentences.append(str([*doc.sents][i]))
        lens.append(len([*doc.sents][i]))

print(len(sentences)) #326
df_ = pd.DataFrame({'sent': sentences, 'len': lens})
df_.head()
df_.iloc[72]

import matplotlib.pyplot as plt
df_['len'].hist()
plt.show()

df_[(df_.len>60)&(df_.len<90)]

x = nlp('This is primarily due to the increase in market demand.')# It is driven by growth in demand. The decline has been primarily due to increase in cost.')
len([*x.sents])
for v in x:
    print(v,v.dep_,v.tag_,v.pos_)
[v.lemma_ for v in x if v.dep_ == 'ROOT']
[v.lemma_ for v in x if v.tag_ == 'VBN']
[v.lemma_ for v in x if v.pos_ == 'VERB']

df_['verbs'] = df_['sent'].apply(lambda v: v.lemma_ for v in x if v.dep_ == 'ROOT')
type(df_['sent'][0])

from collections import Counter

a = pd.DataFrame({'1':[['a','a','a'],[1,2,2],[1,3]],'2':[10,20,30],'3':['I drive a car.','This is fun.','I am very sleepy.']})
a['1'].apply(lambda x: pd.DataFrame(x).value_counts())
Counter(a['1'].tolist())

doc = nlp(text6)
#verbs = [verb.lemma_ for verb in doc if verb.dep_ == 'ROOT' and verb.pos_=='VERB']
verbs = [v.lemma_ for v in doc if v.dep_ == 'ROOT' and (v.pos_ == 'VERB' or v.pos_ == 'AUX')]
len(verbs) #314
c1 = Counter(verbs)
c2 = Counter(verbs[-10:])
c1+c2
sum([c1,c2,c1],Counter())
c1+c2

def get_verbs(text):
    doc = nlp(text)
    verbs = [v.lemma_ for v in doc if v.dep_ == 'ROOT' and (v.pos_=='VERB' or v.pos_=='AUX')]
    print(verbs)
    return Counter(verbs)

a['verbs'] = a['3'].apply(lambda x: get_verbs(x))

for sent in [*doc.sents]:
    for word in sent:
        if word.dep_ == 'ROOT' and word.lemma_ == 'drive':
            print(sent,'\n')

type(list(doc.noun_chunks)[101].text) #<class 'spacy.tokens.span.Span'>
type(doc.noun_chunks)# generator
len(list(doc.noun_chunks)) #2617
len(Counter(i.text.lower() for i in doc.noun_chunks)) #1223 #.most_common(20)


len([*re.finditer(re.compile('due to'),text6)]) #35
doc.count_by()


#https://towardsdatascience.com/lovecraft-with-natural-language-processing-part-2-tokenisation-and-word-counts-f970f6ff5690

def create_word_counts_by_pos(raw_text, list_of_pos, word_count_dict_input=None):
    """
    takes a raw text file
    tokenizes and lemmatizes it
    limits inspection to list_of_pos types of words
    counts the individual lemmas
    returns a dictionary, keys are pos's in list_of_pos
    values are dictinaries with word counts
    """

    doc = nlp(raw_text)

    if word_count_dict_input is None:
        word_count_dict = {}
        for part_of_speech in list_of_pos:
            word_count_dict[part_of_speech] = {}
    else:
        word_count_dict = word_count_dict_input

    for token in doc:
        part_of_speech = token.pos_

        if part_of_speech in list_of_pos and token.is_stop == False:
            word_lemma = token.lemma_
            current_count = word_count_dict[part_of_speech].get(word_lemma, 0)
            current_count += 1
            word_count_dict[part_of_speech][word_lemma] = current_count

    return word_count_dict


def filter_word_count_dict_to_frequent(word_count_dict, threshold):
    """
    Loops through word_count_dict, only keeps items where
    value is higher than a certain threshold
    """
    frequent_word_count_dict = {}

    list_of_pos = word_count_dict.keys()

    for part_of_speech in list_of_pos:
        frequent_word_count_dict[part_of_speech] = {}
        for key in word_count_dict[part_of_speech]:
            if word_count_dict[part_of_speech][key] > threshold:
                frequent_word_count_dict[part_of_speech][key] =  word_count_dict[part_of_speech][key]

    return frequent_word_count_dict


def collect_most_frequent_words(word_count_dict, number_to_collect):
    """
    word_count_dict is assumed to be in a format where keys are part-of-speech,
    values are counts
    number_of_collect: we will collect this amount from each group
    if there is a tie: the one that appeared first
    """

    list_of_pos = word_count_dict.keys()
    most_frequent_words = {}

    for part_of_speech in list_of_pos:
        most_frequent_words[part_of_speech] = sorted(word_count_dict[part_of_speech].items(), key=lambda x: x[1], reverse=True)[:number_to_collect]

    return most_frequent_words

list_of_pos = ['NOUN', 'PROPN', 'ADJ', 'VERB']
word_count_dict = create_word_counts_by_pos(text, list_of_pos)
frequent_word_count_dict = filter_word_count_dict_to_frequent(word_count_dict, 10)


# https://stackoverflow.com/questions/62776477/how-to-extract-sentences-with-key-phrases-in-spacy

from spacy.matcher import PhraseMatcher

text = "I am happy. Net cash provided by operating activities increased  from  2014  to  2015  primarily due to increased net income adjusted for depreciation and stock-based compensation expense, and loss  on sales of marketable and non-marketable securities. I am sleepy. Our provision for income taxes and our effective tax rate increased from  2013  to  2014 , largely due to proportionately more earnings realized in countries that have higher statutory tax rates and more benefit recognized in 2013 relative to 2014 due to the retroactive extension of the 2012 federal research and development credit, offset by a benefit taken on a valuation allowance release related to a capital loss carryforward in 2014. "

phrase_matcher = PhraseMatcher(nlp.vocab)
phrases = ['due to', 'am sleepy']
patterns = [nlp(text) for text in phrases]
phrase_matcher.add('dueto', None, *patterns)

doc = nlp(text)

for sent in doc.sents:
    for match_id, start, end in phrase_matcher(nlp(sent.text)):
        if nlp.vocab.strings[match_id] in ["dueto"]:
            print(sent.text)

### 2021.11.27
# TODO: customize a function that count number of words under each POS category

# SPACY POS_ (universal, coarse-grain) https://github.com/explosion/spaCy/blob/master/spacy/glossary.py
SpaCy_POS_glossary ={ "ADJ": "adjective",
    "ADP": "adposition",
    "ADV": "adverb",
    "AUX": "auxiliary",
    "CONJ": "conjunction",
    "CCONJ": "coordinating conjunction",
    "DET": "determiner",
    "INTJ": "interjection",
    "NOUN": "noun",
    "NUM": "numeral",
    "PART": "particle",
    "PRON": "pronoun",
    "PROPN": "proper noun",
    "PUNCT": "punctuation",
    "SCONJ": "subordinating conjunction",
    "SYM": "symbol",
    "VERB": "verb",
    "X": "other",
    "EOL": "end of line",
    "SPACE": "space"}


def count_words_by_pos(text, part_of_speech,frequency=None, limit=None):
    '''
    :param text: str
    :param part_of_speech: list e.g. ['VERB','NOUN',...]
    :param frequency: minimum number of word appearance in the input text
    :param limit: number of words to be included
    :return: dict{'VERB':{'be':10, 'have':8,...}, 'NOUN':{'apple':3,'banana':2}
    '''
    doc = nlp(text)
    d = {}
    for pos in part_of_speech:
        d[pos] = {}

    for token in doc:
        if token.pos_ in part_of_speech:
            c = d[token.pos_].get(token.lemma_, 0)
            c += 1
            d[token.pos_][token.lemma_] = c

    sorted_d = {}
    for pos_ in part_of_speech:
        sorted_d[pos_] = dict(sorted(d[pos_].items(), key = lambda x: x[1], reverse = True))

    if frequency and limit:
        limit_sorted_d = {}
        for pos_ in part_of_speech:
            limit_sorted_d[pos_] = {}
            i = 0
            for word in sorted_d[pos_].keys():
                if sorted_d[pos_][word] >= frequency and i < limit:
                    limit_sorted_d[pos_][word] = sorted_d[pos_][word]
                    i += 1
                else:
                    break
    else:
        limit_sorted_d = sorted_d

    return limit_sorted_d

d = {'a':{1: 2, 3: 4, 4: 3, 2: 1, 0: 0},'b':{10: 20, 30: 40, 40: 30, 20: 10, 0: 100}}
sorted_d = {}
for k in d.keys():
    sorted_d[k] = dict(sorted(d[k].items(), key = lambda x: x[1], reverse = True))
print('Dictionary in descending order by value : ',sorted_d)
limit = 2
limit_sorted_d = {}
for k in sorted_d.keys():
    limit_sorted_d[k] = dict()
    for k1 in list(sorted_d[k])[:limit]:
        limit_sorted_d[k][k1] = sorted_d[k][k1]
print('Dictionary limit sorted : ',limit_sorted_d)

part_of_speech=['VERB','PNOUN','NOUN','ADJ','ADV','ADP','CONJ','CCONJ','SCONJ']
count_words_by_pos(text6, part_of_speech,limit=50,frequency=1)


# Use counter instead of dictionary
def count_words_by_pos(text, part_of_speech,frequency=None, limit=None):
    '''
    :param text: str
    :param part_of_speech: list e.g. ['VERB','NOUN',...]
    :param frequency: minimum number of word appearance in the input text
    :param limit: number of words to be included
    :return: dict{'VERB':Counter('be':10, 'have':8,...), 'NOUN':Counter('apple':3,'banana':2)}
    '''
    doc = nlp(text)
    d = {}
    for pos in part_of_speech:
        d[pos] = [] #Counter()

    for token in doc:
        if token.pos_ in part_of_speech:
            d[token.pos_].append(token.lemma_)

    for pos in part_of_speech:
        counter = Counter(d[pos])
        if frequency:
            counter = Counter({k: c for k, c in counter.items() if c >= frequency})
        d[pos] = counter.most_common(limit)

    return d

count_words_by_pos(text6, part_of_speech,limit=None,frequency=3)


file_name = 'C:/Users/clair/Desktop/Thesis/masterThesis2022/Data/Samples\GOOG/10-K/0001652044-16-000012/filing-details.html'
file_name[:file_name.rfind('/')+1]

# turn a list of tuples into a counter
l = [('include', 36), ('reflect', 24), ('relate', 22), ('offset', 18), ('increase', 16), ('continue', 15), ('base', 14), ('compare', 14), ('expect', 12), ('provide', 12), ('affect', 11), ('decline', 11), ('establish', 11), ('look', 9), ('denominate', 9), ('market', 8), ('condense', 8), ('end', 8), ('decrease', 8), ('•', 7), ('use', 7), ('make', 6), ('result', 6), ('receive', 6), ('pay', 6), ('enter', 6), ('secure', 6), ('see', 6), ('operate', 5), ('record', 5), ('issue', 5), ('drive', 5), ('identify', 4), ('follow', 4), ('incur', 4), ('fund', 4), ('regard', 3), ('cause', 3), ('differ', 3), ('consider', 3), ('know', 3), ('guarantee', 3), ('vary', 3), ('agree', 3), ('develop', 3), ('combine', 3), ('distribute', 3), ('remain', 3), ('assume', 3), ('lower', 3), ('toll', 3), ('restructure', 3), ('work', 3)]
Counter(dict(l))

from wordcloud import WordCloud
wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                min_font_size = 10).generate(text)

#wordcloud = WordCloud().generate_from_frequencies(dict(l))
wordcloud = WordCloud().generate_from_frequencies(c1)
plt.imshow(wordcloud)
plt.show()

import seaborn as sns

x, y = [], []
for word,count in c1.most_common(20):
    x.append(word)
    y.append(count)

sns.barplot(x=y, y=x)
plt.show()

fig, (ax1, ax2) = plt.subplots(1, 2, sharey=False,figsize = (11,7))
ax1.imshow(wordcloud)
ax1.set_title('Word Cloud')
ax2 = sns.barplot(y,x)
ax2.set_title('Top')
plt.show()

fig, bar = plt.subplots(figsize = (11,7))
bar = sns.barplot(data = deliveries, x = 'day', y = 'del_tip_amount', hue='time', order = labels)
bar.set_title('Average tip per shift')

text = 'The total revenue grew by 10% from last quarter, primarily driven by growth in market demand. ' \
       'The incease in cost is driven by growth in headcount. ' \
       'The net income decreased by 5%, due to increase in operating costs. '
doc = nlp(text)
sentences = [s for s in doc.sents]
for s in sentences:
    print(len(s)-1, s.root, [(chunk.text, chunk.root.dep_, chunk.root.head.text) for chunk in s.noun_chunks])

for chunk in doc.noun_chunks:
    print(chunk.text, '->',chunk.root.text, '->',chunk.root.dep_,'->',
            chunk.root.head.text)

roots = ['drive']
for i in range(len(sentences)):
    s = sentences[i]
    if s.root.lemma_ in roots:
        print(s)

phrases = ['driven by','due to']
for i in range(len(sentences)):
    s = sentences[i].text
    for p in phrases:
        if p in s:
            print(p,": ",s)

'due to' in sentences[2].text

def x(y):
    if y:
        return y
x(1)
print(x(None))

l=[]
l.append(x(1))
l.append(x(None))
l