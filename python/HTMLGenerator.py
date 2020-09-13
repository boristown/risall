from jinja2 import Environment, FileSystemLoader 
import mydb
import datetime
import time
import math
from tqdm import tqdm
import donate

def getdonatetext(donates):
    donatetext = ""
    for donateperson in donates:
        if len(donatetext) > 0:
            donatetext = donatetext + "                          "
        donatetext = donatetext + donateperson
    return donatetext

def generate_html(title, html_name, market_type, 
                  market_ref2, market_type2,
                  market_ref3, market_type3,
                  market_ref4, market_type4,
                  market_ref5, market_type5,
                  market_ref6, market_type6,
                  market_ref7, market_type7,
                  donate,
                  localtime, body):
    #env = Environment(loader=FileSystemLoader('./'))
    env = Environment(loader=FileSystemLoader('../static/template/'))
    template = env.get_template('template.html')
    with open('../static/' + html_name,'w+',encoding='utf-8') as fout:   
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
        
def generate_market_html(title, html_name, market_name, market_id,
                  market_type, market_type_ref,  market_prediction,
                  #price_list, donate, data_dict,
                  localtime
                  #, body
                  ):
    #env = Environment(loader=FileSystemLoader('./'))
    env = Environment(loader=FileSystemLoader('../static/template/'))
    template = env.get_template('market.html')
    with open('../static/' + html_name,'w+',encoding='utf-8') as fout:   
        html_content = template.render(
                                        title = title, market_name=market_name ,  market_id = market_id,
                                        market_type = market_type, market_type_ref = market_type_ref, market_prediction =market_prediction,
                                        #price_list = price_list, donate = donate, data_dict=data_dict,
                                        localtime=localtime , 
                                        #body=body
                                        )
        fout.write(html_content)

if __name__ == "__main__":
    html_name = {
        "外汇":"currencies.html",
        "加密货币":"crypto.html",
        "全球股指":"indices.html",
        "商品期货":"commodities.html",
        "股票":"stocks.html",
        "美国股票":"stocksUS.html",
        "香港股票":"stocksHK.html",
        }
    market_type = {
        "外汇":"外汇Currencies",
        "加密货币":"加密货币Crypto",
        "全球股指":"全球股指Indices",
        "商品期货":"商品期货Commodities",
        "股票":"中国股票CN Stocks",
        "美国股票":"美国股票US Stocks",
        "香港股票":"香港股票HK Stocks",
        }

    currenciesDict = {}
    while True:
        for market_key in market_type:
            body = []
            keys = []
            for market_key2 in market_type:
                if market_key2 != market_key:
                    keys.append(market_key2)
            indexlist = mydb.get_index_list(market_key)
            if market_key == '外汇':
                currenciesDict = {}
                for indexline in indexlist:
                    currenciesDict[indexline[10]] = indexline[6]
            market_list = mydb.get_market_list(market_key)

            annualised = {}
            processbar = tqdm(market_list, ncols=80)
            for market_id in processbar:
                processbar.set_description(market_key)
                marketprices, annualised[market_id[0]] = mydb.get_market_prices(market_id[0])
                if len(marketprices) == 0:
                    continue
                market_html_name = '../static/market/' + market_id[0] + ".html"
                price_list = [{"date":marketprice["Date"],"close":marketprice["Close"], "balance":marketprice["Balance"]} for marketprice in marketprices][-1::-1]
                price_lists = []
                price_lists.append(price_list[-30:])
                price_lists.append(price_list[-60:])
                price_lists.append(price_list[-120:])
                price_lists.append(price_list[-240:])
                price_lists.append(price_list)
                datelist = [marketprice["Date"] for marketprice in marketprices][-1::-1]
                valuelist = price_list
                data_dict = dict(zip(datelist, valuelist))
                #日期插值
                mindate = datetime.datetime.strptime(datelist[0], "%Y-%m-%d")
                maxdate = datetime.datetime.strptime(datelist[-1], "%Y-%m-%d")
                currentdate = mindate
                lastitem = price_list[0]
                while currentdate <= maxdate:
                    currentdatestr = currentdate.strftime("%Y-%m-%d")
                    if currentdatestr not in data_dict:
                        data_dict[currentdatestr] = lastitem
                    else:
                        lastitem = data_dict[currentdatestr]
                    currentdate += datetime.timedelta(days=1)
                market_prediction = "今日操作：" + marketprices[0]["Prediction"] +  " 年化：" + str(round(annualised[market_id[0]] * 100, 2)) + "%"
                generate_market_html(u"AI预测：" +market_id[1] +"--预测线forcastline.com", market_html_name, market_id[1], market_id[0], 
                      market_type[market_key], '../' + html_name[market_key], market_prediction,
                      #price_lists, getdonatetext(donate.donate), data_dict,
                      time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                      #, marketprices
                      )
            
            for indexline in indexlist:
                if True or indexline[1][0:3] == 'USD' or ',USD' in indexline[1]:
                    volume = indexline[7]
                elif indexline[11] is not None:
                    volume = indexline[7] * indexline[6] * currenciesDict[indexline[11]]
                else:
                    volume = indexline[7] * indexline[6]
                result = {
                    'ItemNo':indexline[0], 
                    'Market':'<span><p>'+indexline[1].replace(',','</p><p>')+'</p></span>',
                    'Date': indexline[2], 
                    'Open':indexline[3],
                    "High":indexline[4],
                    "Low":indexline[5],
                    "Close":indexline[6],
                    "Volume":volume,
                    "Rise":str(round((indexline[6] / indexline[3] - 1) * 100, 2)) + "%",
                    "Side":indexline[8],
                    "Score":round(indexline[9],2),
                    "Class":'rise' if '涨' in indexline[8] else 'fall',
                    #"Symbol":"market.html?id="+indexline[10],
                    "Symbol":"market/"+indexline[10] + ".html",
                    "Annualised": annualised[indexline[10]]
                    }
                if annualised[indexline[10]] <= 0:
                    result["Class"] += ' loss'
                else:
                    result["Class"] += ' win'
                body.append(result)
            body.sort(reverse = True, key = lambda line:(line["Annualised"], line["Score"]))
            for bodyitem in body:
                bodyitem["Annualised"] = str(round(bodyitem["Annualised"] * 100, 2)) + "%"
            itemNo = 0
            for indexline in body:
                itemNo += 1
                indexline["ItemNo"] = itemNo
            generate_html(u"AI预测：" + market_type[market_key] +"--预测线forcastline.com", 
                          html_name[market_key], market_type[market_key], 
                          html_name[keys[0]], market_type[keys[0]],
                          html_name[keys[1]], market_type[keys[1]],
                          html_name[keys[2]], market_type[keys[2]],
                          html_name[keys[3]], market_type[keys[3]],
                          html_name[keys[4]], market_type[keys[4]],
                          html_name[keys[5]], market_type[keys[5]],
                          getdonatetext(donate.donate),
                          time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                          body)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),html_name[market_key],"已生成。")
            
        #time.sleep(10)