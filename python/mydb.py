import mypsw
import mysql.connector
import math
import datetime

def init_mycursor():
    myconnector = mysql.connector.connect(
      host=mypsw.host,
      user=mypsw.user,
      passwd=mypsw.passwd,
      database=mypsw.database,
      auth_plugin='mysql_native_password'
      )
    mycursor = myconnector.cursor()
    return myconnector, mycursor

def get_index_list(market_key):
    index_list = []
    myconnector, mycursor = init_mycursor()
    list_statement = '''
    SELECT b.symbol_alias, DATE_FORMAT(a.date, "%%Y-%%m-%%d") as date, a.o, a.h, a.l, a.c, a.v as volume, if(a.f>=0.5,"即将上涨↑","即将下跌↓") as side, abs((a.f*2-1)*100) as score , b.symbol, c.basesymbol
    FROM zeroai.pricehistory as a inner join 
    (select symbol,group_concat(symbol_alias) as symbol_alias, market_type from zeroai.symbol_alias group by symbol, market_type) as b on a.symbol = b.symbol
    inner join zeroai.predictlog as c on a.symbol = c.symbol and a.date = c.MAXDATE
    where b.MARKET_TYPE = '%s'
    and a.date > DATE_ADD(curtime(),INTERVAL -10 DAY)
    and a.f <> 0.5 and a.o > 0
    order by volume desc;
    ''' % (market_key)
    mycursor.execute(list_statement)
    list_results = mycursor.fetchall()
    lineno = 0
    for list_result in list_results:
        lineno += 1
        index_list.append([
            lineno,
            list_result[0],
            list_result[1],
            list_result[2],
            list_result[3],
            list_result[4],
            list_result[5],
            list_result[6],
            list_result[7],
            list_result[8],
            list_result[9],
            list_result[10],
            ])
    return index_list

def get_search_list(markets):
    index_list = []
    myconnector, mycursor = init_mycursor()
    list_statement = '''
    SELECT b.symbol_alias, DATE_FORMAT(a.date, "%%Y-%%m-%%d") as date, a.o, a.h, a.l, a.c, a.v as volume, if(a.f>=0.5,"即将上涨↑","即将下跌↓") as side, abs((a.f*2-1)*100) as score , b.symbol
    FROM zeroai.pricehistory as a inner join 
    (select symbol,group_concat(symbol_alias) as symbol_alias, market_type from zeroai.symbol_alias group by symbol, market_type) as b on a.symbol = b.symbol
    inner join zeroai.predictlog as c on a.symbol = c.symbol and a.date = c.MAXDATE
    where b.symbol in (%s)
    and a.date > DATE_ADD(curtime(),INTERVAL -10 DAY)
    and a.f <> 0.5 and a.o > 0
    order by volume desc;
    ''' % ','.join(['%s']*len(markets))
    mycursor.execute(list_statement, markets)
    list_results = mycursor.fetchall()
    lineno = 0
    for list_result in list_results:
        lineno += 1
        index_list.append([
            lineno,
            list_result[0],
            list_result[1],
            list_result[2],
            list_result[3],
            list_result[4],
            list_result[5],
            list_result[6],
            list_result[7],
            list_result[8],
            list_result[9],
            #list_result[10],
            ])
    return index_list

def get_market_list(market_key):
    market_list = []
    myconnector, mycursor = init_mycursor()
    list_statement = '''
    SELECT symbol, group_concat(symbol_alias)
    FROM zeroai.symbol_alias 
    where market_type = '%s'
    group by symbol;
    ''' % (market_key)
    mycursor.execute(list_statement)
    list_results = mycursor.fetchall()
    lineno = 0
    for list_result in list_results:
        lineno += 1
        market_list.append([
            list_result[0],
            list_result[1]
            ])
    return market_list

def get_market_prices(market_id):
    market_list = []
    myconnector, mycursor = init_mycursor()
    list_statement = '''
    SELECT DATE_FORMAT(date, "%%Y-%%m-%%d") as date, O, H, L, C, V, if(F>=0.5,"做多Buy","做空Sell") as side, abs((F*2-1)*100) as score, ATR
    FROM zeroai.pricehistory where symbol = '%s'  and o > 0 and l > 0 and c > 0 and h < l * 10 and c >= l and c <= h 
    order by date asc;
    ''' % (market_id)
    mycursor.execute(list_statement)
    list_results = mycursor.fetchall()

    last_c = 0
    tr0list = [] #TR0清单
    orderlist = [] #持有清单
    lineno = 0
    atr = 0.0
    balance = 1.0
    for list_result in list_results:
        Date = list_result[0]
        Open = list_result[1]
        High = list_result[2]
        Low = list_result[3]
        Close = list_result[4]
        if last_c == 0:
            last_c = Open #Open Price
        tr = max(High, last_c) / min(Low, last_c) - 1.0
        if tr > 9.0 or tr == 0:
            continue
        lineno += 1
        tr0 = tr / 120.0
        #添加最新TR0值
        tr0list.append(tr0)
        atr += tr0
        if lineno > 120:
            #删除120天前的TR0值
            atr -= tr0list.pop(0)
        last_c = Close
        if list_result[7] > 0 and atr > 0:
            #模拟交易
            for oldorder in orderlist:
                if 'Buy' in oldorder["Prediction"]:#buy 
                    if Low < oldorder["StopPrice"]:#Stop
                        oldorder["StopDate"] = Date
                        quantity = oldorder["Balance"] * 0.01 / oldorder["Close"] / oldorder["ATR"]
                        buyamount = quantity * oldorder["Close"]
                        sellamount = quantity * oldorder["StopPrice"]
                        Profit = sellamount - buyamount
                        balance += Profit
                        if balance < 0:
                            balance = 0
                        else:
                            oldorder["Profit"] = str(round(Profit / oldorder["Balance"] * 100, 3)) + '%' if oldorder["Balance"] > 0 else '0%'
                        orderlist.remove(oldorder)
                        continue
                    else:
                        oldorder["TrailingPrice"] = max(oldorder["TrailingPrice"], High)
                        oldorder["StopPrice"] = oldorder["TrailingPrice"] / (atr + 1)
                else:#sell
                    if High > oldorder["StopPrice"]:#Stop
                        oldorder["StopDate"] = Date
                        quantity = oldorder["Balance"] * 0.01 / oldorder["Close"] / oldorder["ATR"]
                        sellamount = quantity * oldorder["Close"]
                        buyamount = quantity * oldorder["StopPrice"]
                        Profit = sellamount - buyamount
                        balance += Profit
                        if balance < 0:
                            balance = 0
                        else:
                            oldorder["Profit"] = str(round(Profit / oldorder["Balance"] * 100, 3)) + '%' if oldorder["Balance"] > 0 else '0%'
                        orderlist.remove(oldorder)
                        continue
                    else:
                        oldorder["TrailingPrice"] = min(oldorder["TrailingPrice"], Low)
                        oldorder["StopPrice"] = oldorder["TrailingPrice"] * (atr + 1)
            neworder = {
                "Date":list_result[0],
                "Open":list_result[1],
                "High":list_result[2],
                "Low":list_result[3],
                "Close":list_result[4],
                "Volume":list_result[5],
                "Today":str(round((list_result[4] / list_result[1] - 1)*100,2)) + '%',
                "Prediction":list_result[6],
                "Score":round(list_result[7],2),
                "Class":'rise' if 'Buy' in list_result[6] else 'fall',
                #"ATR": list_result[8],
                "ATR": atr,
                "TrailingPrice": list_result[4],
                "StopPrice": list_result[4] / (atr + 1) if 'Buy' in list_result[6]  else (atr + 1) * list_result[4],
                "StopDate": '-',
                "Profit": '0.0%',
                "Balance": balance
                }
            market_list.append(neworder)
            orderlist.append(neworder)
    if len(market_list) == 0:
        return market_list, 0.0
    market_list.sort(reverse = True, key = lambda item:item["Date"])
    for market_item in market_list:
        market_item["ATR"] = str(round(market_item["ATR"] * 100.0, 2)) + '%'
    lastdate = datetime.datetime.strptime(market_list[0]["Date"], '%Y-%m-%d')
    firstdate = datetime.datetime.strptime(market_list[-1]["Date"], '%Y-%m-%d')
    daycount = (lastdate - firstdate ).days
    return market_list , math.pow(balance, 365.0 / daycount) - 1 if daycount > 0 else 0.0
