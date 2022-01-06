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

class ClsStock:
    def __init__(self, code, name, volumeIncreaseRate, volume, avg5dayVolume, dealAmount):
        self.code = code
        self.name = name
        self.volumeIncreaseRate = volumeIncreaseRate
        self.volume = volume
        self.avg5dayVolume = avg5dayVolume
        self.dealAmount = dealAmount

def crawler_intersection(type, days):
    rank_list = []

    rank_volume_list = crawler_trading_volume()
    rank_amount_list = crawler_listed_trading_amount(type, days)
    
    for i in range(len(rank_amount_list)):
        for j in range(len(rank_volume_list)):
            if rank_amount_list[i].code == rank_volume_list[j].code:
                rank_list.append(
                    ClsStock(
                        rank_volume_list[j].code,
                        rank_volume_list[j].name,
                        rank_volume_list[j].volumeIncreaseRate,
                        rank_volume_list[j].volume,
                        rank_volume_list[j].avg5dayVolume,
                        rank_amount_list[i].dealAmount,
                    )
                )
                break

    return rank_list