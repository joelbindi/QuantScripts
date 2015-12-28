import requests  
from lxml import html  
import re  
import csv  
import pandas as pd  
from datetime import datetime  
 
#Inputs  
topn = 20            #Top ranking symbols  
null_value = 0         #For missing data  
output_name = "Yahoo Scrapey"  #Name for CSV file  
symbol_file = 'asx50.csv'    #List of symbols  
country_code = '.AX'      #Country code for symbols  
 
symbols = []  
with open (symbol_file, 'rb') as f:  
 r = csv.reader(f, delimiter=' ', quotechar='|')  
 for row in r:  
   symbols.append(', '.join(row))  
print symbols  
 
returns= []  
for s in symbols:  
#EV/EBITDA  
 try:  
   url = 'http://au.finance.yahoo.com/q/ks?s='+s+country_code  
   page = requests.get(url)  
   tree = html.fromstring(page.content)  
   ev_to_ebitda = tree.xpath('//td[contains(text(), "Enterprise Value/EBITDA")]/following-sibling::td[1]/text()')  
   ev_to_ebitda = str(ev_to_ebitda)   
   ev_to_ebitda = re.sub("[^0123456789\.-]","",ev_to_ebitda)  
   if len(ev_to_ebitda) < 1:  
     ev_to_ebitda = null_value  
   else:  
     ev_to_ebitda = float(ev_to_ebitda)  
 except Exception as E:  
   print"Ebitda Error "+str(E)+" "+str(s)    
   
#ROE  
 try:  
   url = 'http://au.finance.yahoo.com/q/ks?s='+s+country_code 
   page = requests.get(url)  
   tree = html.fromstring(page.content)  
   roe = tree.xpath('//td[contains(text(), "Return on Equity")]/following-sibling::td[1]/text()')  
   roe = str(roe)  
   roe = re.sub("[^0123456789\.-]","",roe)  
   if len(roe) < 1:  
     roe = null_value        
   else:  
     roe = float(roe) / 100  
 except Exception as E:  
   print"ROE Error "+str(E)+" "+str(s)   
 
 returns.append([s, ev_to_ebitda, roe])  
   
#Ranking    
d = pd.DataFrame(returns, columns=['symbols', 'ev_to_ebitda', 'roe'])  
d = d[d['ev_to_ebitda'] > 0]  
d = d[d['roe'] > 0]  
print d  
 
d['ebitda_rank']= d['ev_to_ebitda'].rank(ascending=True)  
d['roe_rank']= d['roe'].rank(ascending=False)  
d['score']= d.ebitda_rank + d.roe_rank  
d['rank']= d['score'].rank(ascending=True)  
d = d.sort_values(by='rank', ascending=True)  
ranked = d[:topn]  
print ranked  
 
#CSV Output  
date = datetime.now().strftime("%d_%m_%Y")  
file_name = "%s_%s.%s" % (output_name, date, "csv")  
ranked.to_csv(file_name)    