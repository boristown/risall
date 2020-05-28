from jinja2 import Environment, FileSystemLoader 
import mydb
import datetime
import time
import math

def generate_html(title, html_name, market_type, 
                  market_ref2, market_type2,
                  market_ref3, market_type3,
                  market_ref4, market_type4,
                  market_ref5, market_type5,
                  market_ref6, market_type6,
                  market_ref7, market_type7,
                  donate,
                  localtime, body):
    env = Environment(loader=FileSystemLoader('./'))
    template = env.get_template('template.html')
    with open(html_name,'w+',encoding='utf-8') as fout:   
        html_content = template.render(
                                        title = title, market_type=market_type , 
                                        market_ref2 = market_ref2, market_type2 = market_type2,
                                        market_ref3 = market_ref3, market_type3 = market_type3,
                                        market_ref4 = market_ref4, market_type4 = market_type4,
                                        market_ref5 = market_ref5, market_type5 = market_type5,
                                        market_ref6 = market_ref6, market_type6 = market_type6,
                                        market_ref7 = market_ref7, market_type7 = market_type7,
                                        donate = donate,
                                        localtime=localtime , 
                                        body=body)
        fout.write(html_content)
        
def generate_market_html(title, html_name, market_name,
                  market_type, market_type_ref, 
                  price_list, donate,
                  localtime, body):
    env = Environment(loader=FileSystemLoader('./'))
    template = env.get_template('market.html')
    with open(html_name,'w+',encoding='utf-8') as fout:   
        html_content = template.render(
                                        title = title, market_name=market_name , 
                                        market_type = market_type, market_type_ref = market_type_ref, 
                                        price_list = price_list, donate = donate,
                                        localtime=localtime , 
                                        body=body)
        fout.write(html_content)

if __name__ == "__main__":
    html_name = {
        "加密货币":"index.html",
        "全球股指":"indices.html",
        "商品期货":"commodities.html",
        "外汇":"currencies.html",
        "股票":"stocks.html",
        "美国股票":"stocksUS.html",
        "香港股票":"stocksHK.html",
        }
    market_type = {
        "加密货币":"加密货币Crypto",
        "全球股指":"全球股指Indices",
        "商品期货":"商品期货Commodities",
        "外汇":"外汇Currencies",
        "股票":"中国股票CN Stocks",
        "美国股票":"美国股票US Stocks",
        "香港股票":"香港股票HK Stocks",
        }

    donate = '冯*俊 赞助10元 2020年5月23日&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;刘*超 赞助200元 2020年5月23日&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;张*勇 赞助50元 2020年5月25日&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;熊*添 赞助1000元 2020年5月23日&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;秦汉 赞助100元 2020年5月25日&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;赵磊 赞助12.34元 2020年5月25日&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;于*万 赞助1元 2020年5月25日'

    while True:
        for market_key in market_type:
            body = []
            keys = []
            for market_key2 in market_type:
                if market_key2 != market_key:
                    keys.append(market_key2)
            indexlist = mydb.get_index_list(market_key)
            for indexline in indexlist:
                result = {
                    'ItemNo':indexline[0], 
                    'Market':'<span><p>'+indexline[1].replace(',','</p><p>')+'</p></span>',
                    'Date': indexline[2], 
                    'Open':indexline[3],
                    "High":indexline[4],
                    "Low":indexline[5],
                    "Close":indexline[6],
                    "Rise":str(round((indexline[6] / indexline[3] - 1) * 100, 2)) + "%",
                    "Side":indexline[7],
                    "Score":round(indexline[8],2),
                    "Class":'rise' if '涨' in indexline[7] else 'fall',
                    "Symbol":"market/"+indexline[9] + ".html",
                    }
                body.append(result)
            generate_html(u"预测线forcastline.com", 
                          html_name[market_key], market_type[market_key], 
                          html_name[keys[0]], market_type[keys[0]], 
                          html_name[keys[1]], market_type[keys[1]], 
                          html_name[keys[2]], market_type[keys[2]], 
                          html_name[keys[3]], market_type[keys[3]], 
                          html_name[keys[4]], market_type[keys[4]], 
                          html_name[keys[5]], market_type[keys[5]], 
                          donate,
                          time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 
                          body)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),html_name[market_key],"已生成。")
            market_list = mydb.get_market_list(market_key)
            for market_id in market_list:
                marketprices = mydb.get_market_prices(market_id[0])
                market_html_name = 'market/' + market_id[0] + ".html"
                price_array = [marketprice["Close"] for marketprice in marketprices][-1::-1]
                generate_market_html(u"预测线forcastline.com", market_html_name, market_id[1],
                      market_type[market_key], '../' + html_name[market_key],
                      price_array, donate,
                      time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), marketprices)
        #time.sleep(10)