import requests
from bs4 import BeautifulSoup

class EsunBroker():
    def __init__(self, name, buyin, sellout, diff, percent):
        self.name = name
        self.buyin = buyin
        self.sellout = sellout
        self.diff = diff
        self.percent = percent

def crawler(code, begin_date, end_date):
    broker_table = {'positive':[], 'negative':[]}

    url = f"https://sjmain.esunsec.com.tw/z/zc/zco/zco.djhtm?a={code}&e={begin_date}&f={end_date}"
    resource_page = requests.get(url)

    soup = BeautifulSoup(resource_page.text, "html.parser")

    broker_name = soup.find_all('td', class_="t4t1")
    broker_price = soup.find_all('td', class_="t3n1")

    i = 0
    while i < len(broker_name[:-4]):
        name = broker_name[i].text
        buyin = int(broker_price[i * 4].text.replace(',', ''))
        sellout = int(broker_price[i  * 4 + 1].text.replace(',', ''))
        diff = buyin - sellout
        percent = broker_price[i * 4 + 3].text
        esun_broker = EsunBroker(name, buyin, sellout, diff, percent)
        if esun_broker.diff > 0:
            broker_table['positive'].append(esun_broker)
        else:
            broker_table['negative'].append(esun_broker)

        i += 1
    
    return broker_table