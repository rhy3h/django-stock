from requests_html import HTMLSession
import re

class ClsTradingVolume:
    def __init__(self, code, name, volumeIncreaseRate, volume, avg5dayVolume):
        self.code = code
        self.name = name
        self.volumeIncreaseRate = volumeIncreaseRate
        self.volume = volume
        self.avg5dayVolume = avg5dayVolume

def crawler_trading_volume():
    session = HTMLSession()
    r = session.get("https://concords.moneydj.com/z/zk/zk1/zkparse_590_50.djhtm")

    search_date = re.findall(r'日期:\S+/\S+\n', r.html.text)[0]
    search_date_index = r.html.text.find(search_date) + len(search_date)
    table = re.findall(r'\S+\n\S+\n\S+\n\S+\n\S+\n\S+\n\S+\n', r.html.text[search_date_index:])[1:]

    rank_list = []
    for stock in table:
        item_split = stock[:-1].split('\n')
        code_name = re.findall(r'\d+|\D+', item_split[0])
        tradingVolumeItem = ClsTradingVolume(
            code_name[0],
            code_name[1],
            item_split[4],
            item_split[5],
            item_split[6],
        )
        rank_list.append(tradingVolumeItem)
    
    return rank_list

class ClsDealAmount:
    def __init__(self, code, name, dealAmount):
        self.code = code
        self.name = name
        self.dealAmount = dealAmount

def crawler_listed_trading_amount(type, days):
    session = HTMLSession()
    r = session.get(f"https://concords.moneydj.com/z/zg/zg_CD_{type}_{days}.djhtm")

    stock_list = r.html.find("td.t3t1")
    deal_amount = r.html.find("td.t3n1")
    deal_amount = deal_amount[1::2]

    rank_list = []
    for i in range(50):
        code_name = re.findall(r'\d+|\D+', stock_list[i].text)

        tradingVolumeItem = ClsDealAmount(
            code_name[0],
            code_name[1],
            deal_amount[i].text
        )
        rank_list.append(tradingVolumeItem)
    
    return rank_list

class Stock:
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.days = None
        self.date = []
        self.sumForeign = None
        self.sumING = None
        self.sumDealer = None
        self.capital = None
        self.industry = None
        self.status = None
        self.five = None
        self.ten = None
        self.twenty = None
        self.sixty = None
        self.one_twenty = None
        self.two_forty = None
        self.close = None
        self.changeRate = None
        self.volumeIncreaseRate = None
        self.volume = None
        self.avg5dayVolume = None
        self.dealAmount = None

def crawler_intersection(type, days):
    rank_list = []

    rank_volume_list = crawler_trading_volume()
    rank_amount_list = crawler_listed_trading_amount(type, days)
    
    for i in range(len(rank_amount_list)):
        for j in range(len(rank_volume_list)):
            if rank_amount_list[i].code == rank_volume_list[j].code:
                stock = Stock(
                    rank_volume_list[j].code,
                    rank_volume_list[j].name,
                )
                stock.volumeIncreaseRate = rank_volume_list[j].volumeIncreaseRate
                stock.volume = rank_volume_list[j].volume
                stock.avg5dayVolume = rank_volume_list[j].avg5dayVolume
                stock.dealAmount = rank_amount_list[i].dealAmount
                rank_list.append(stock)
                
                break

    return rank_list


def crawler_union(type, days):
    rank_list = []

    rank_volume_list = crawler_trading_volume()
    rank_amount_list = crawler_listed_trading_amount(type, days)
    
    for i in range(len(rank_amount_list)):
        for j in range(len(rank_volume_list)):
            if rank_amount_list[i].code == rank_volume_list[j].code:
                stock = Stock(
                    rank_volume_list[j].code,
                    rank_volume_list[j].name,
                )
                stock.volumeIncreaseRate = rank_volume_list[j].volumeIncreaseRate
                stock.volume = rank_volume_list[j].volume
                stock.avg5dayVolume = rank_volume_list[j].avg5dayVolume
                stock.dealAmount = rank_amount_list[i].dealAmount
                rank_list.append(stock)
                
                break

    return rank_list