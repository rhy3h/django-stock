import csv

def load_dict_stock_list():
    with open('stockapp/files/上市、上櫃(股本、產業、產業地位).csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        stock_list = list(reader)
        
    return stock_list

def load_list_stock_list():
    with open('stockapp/files/上市、上櫃(股本、產業、產業地位).csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        stock_list = list(reader)
    return stock_list