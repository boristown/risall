import mypsw
import mysql.connector
import math
import datetime
import time

atr_count = 20

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
    SELECT b.symbol_alias, DATE_FORMAT(a.date, "%%Y-%%m-%%d") as date, a.o, a.h, a.l, a.c, a.v as volume, if(a.f>=0.5,"即将上涨↑","即将下跌↓") as side, abs((a.f*2-1)*100) as score , b.symbol, c.basesymbol, a.balance, a.days
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
            list_result[11],
            list_result[12],
            ])
    return index_list

#HSV -> RGB color
def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return rgb2hex(r, g, b)

#RGB -> HEX color
def rgb2hex(r,g,b):
    hexR = str(hex(r))[-2:].replace("x","0")
    hexG = str(hex(g))[-2:].replace("x","0")
    hexB = str(hex(b))[-2:].replace("x","0")
    return '#' + hexR + hexG + hexB

def get_index_list_limit(market_key, maxrows):
    index_list = []
    myconnector, mycursor = init_mycursor()
    list_statement = '''
    SELECT b.symbol_alias, DATE_FORMAT(a.date, "%%Y-%%m-%%d") as date, a.o, a.h, a.l, a.c, a.v as volume, if(a.f>=0.5,"即将上涨↑","即将下跌↓") as side, 
    abs((a.f*2-1)*100) as score , b.symbol, c.basesymbol, if(a.days > 0,power(a.balance, 365.0 / a.days) - 1,0.0) as Annualised
    FROM zeroai.pricehistory as a inner join 
    (select symbol,group_concat(symbol_alias) as symbol_alias, market_type from zeroai.symbol_alias group by symbol, market_type) as b on a.symbol = b.symbol
    inner join zeroai.predictlog as c on a.symbol = c.symbol and a.date = c.MAXDATE
    where b.MARKET_TYPE = '%s'
    and a.date > DATE_ADD(curtime(),INTERVAL -10 DAY)
    and a.f <> 0.5 and a.o > 0
    order by Annualised desc 
    ''' % (market_key)
    if maxrows > 0:
        list_statement += " limit " + str(maxrows)
    mycursor.execute(list_statement)
    list_results = mycursor.fetchall()
    lineno = 0
    hmin = 0.0
    hmax = 240.0
    hcenter = (hmax+hmin)/2.0
    hrange = (hmax-hmin)/2.0
    for list_result in list_results:
        lineno += 1
        #if '涨' in list_result[7]:
        #    hscore = list_result[8] / 100 - 1
        #else:
        #    hscore = list_result[8] / 100

        #hposition = hrange * hscore
        #colorhex = hsv2rgb(hcenter + hposition, 0.9, (hscore + 1.0)/2)
        if '涨' in list_result[7]:
            #colorhex = hsv2rgb(hmin, 0.9, list_result[8] / 100)
            bgcolorhex = '#dddddd'
            colorhex = '#222222'
        else:
            #colorhex = hsv2rgb(hmax, 0.9, list_result[8] / 100)
            bgcolorhex = '#222222'
            colorhex = '#dddddd'
        index_list.append([
            lineno, #line no
            list_result[0], #symboll_alias
            list_result[1], #date
            list_result[2], #o
            list_result[3], #h
            list_result[4], #l
            list_result[5], #c
            list_result[6], #volume
            list_result[7], #side
            list_result[8], #score
            list_result[9], #symbol
            list_result[10], #basesymbol(弃用)
            list_result[11], #Annualised
            bgcolorhex, #Bgcolor
            colorhex, #color
            ])
    return index_list

def get_search_list(markets):
    index_list = []
    myconnector, mycursor = init_mycursor()
    list_statement = '''
    SELECT b.symbol_alias, DATE_FORMAT(a.date, "%%Y-%%m-%%d") as date, a.o, a.h, a.l, a.c, a.v as volume, if(a.f>=0.5,"即将上涨↑","即将下跌↓") as side, abs((a.f*2-1)*100) as score , b.symbol, balance, days, a.date as datetime
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
        balance = list_result[10]
        daycount = list_result[11]
        startdate = list_result[12] + datetime.timedelta(days=-daycount)
        #print("balance = " + str(balance) + ";daycount = " + str(daycount))
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
            math.pow(balance, 365.0 / daycount) - 1 if daycount > 0 else 0.0
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

#Get Market Type
def getmarkettype(market_id):
    myconnector, mycursor = init_mycursor()
    select_statement = '''
    SELECT MARKET_TYPE, group_concat(symbol_alias) 
    FROM SYMBOL_ALIAS
    WHERE SYMBOL = '%s'
    group by symbol;
    ''' % (market_id)
    mycursor.execute(select_statement)
    select_results = mycursor.fetchall()
    for result in select_results:
        markettype = result[0]
        marketname = result[1]
    return markettype, marketname

def get_market_prices_limit(market_id, pageindex, pagesize):
    market_list = []
    myconnector, mycursor = init_mycursor()
    pagesize = int(pagesize)
    pageindex = int(pageindex)
    offset = int(pagesize) * ( int(pageindex) - 1 )
    if offset < 0 :
        offset = 0
    
    count_statement = '''
    SELECT count(*) 
    FROM zeroai.pricehistory where symbol = '%s'  and o > 0 and l > 0 and c > 0 and h < l * 10 and c >= l and c <= h 
    ;
    ''' % (market_id)
    mycursor.execute(count_statement)
    count_results = mycursor.fetchall()

    for count_result in count_results:
        pagetotal = count_result[0]

    pagetotal = math.ceil(pagetotal * 1.0 / pagesize)

    list_statement = '''
    select * from (SELECT DATE_FORMAT(date, "%%Y-%%m-%%d") as date, O, H, L, C, V, if(F>=0.5,"做多Buy","做空Sell") as side, abs((F*2-1)*100) as score, ATR, balance, days , date as datetime
    FROM zeroai.pricehistory where symbol = '%s'  and o > 0 and l > 0 and c > 0 and h < l * 10 and c >= l and c <= h 
    order by date desc limit %s, %s) a
    order by date asc;
    ''' % (market_id, str(offset), str(pagesize))
    mycursor.execute(list_statement)
    list_results = mycursor.fetchall()

    last_c = 0
    tr0list = [] #TR0清单
    orderlist = [] #持有清单
    lineno = 0
    atr = 0.0
    balance = 1.0
    trsum = 0
    dayindex = 0
    for list_result in list_results:
        dayindex += 1
        Open = list_result[1]
        High = list_result[2]
        Low = list_result[3]
        Close = list_result[4]
        if last_c == 0:
            last_c = Open #Open Price
        tr = max(High, last_c) / min(Low, last_c) - 1.0
        last_c = Close
        if tr > 9.0 or tr == 0:
            continue
        if dayindex > atr_count:
            break
        lineno += 1
        trsum += tr
        tr0 = tr / atr_count
        tr0list.append(tr0)
    atr = trsum / lineno

    last_c = 0
    #lineno = 0

    for list_result in list_results:
        Date = list_result[0]
        Open = list_result[1]
        High = list_result[2]
        Low = list_result[3]
        Close = list_result[4]
        if list_result[9] > 0:
            balance = list_result[9]
        if last_c == 0:
            last_c = Open #Open Price
        else:
            if last_c < Low:
                Low = last_c
            elif last_c > High:
                High = last_c
        tr = max(High, last_c) / min(Low, last_c) - 1.0
        #last_c = Close
        if tr > 9.0 or tr == 0:
            continue
        lineno += 1
        tr0 = tr / atr_count
        #添加最新TR0值
        tr0list.append(tr0)
        atr += tr0
        if lineno > atr_count:
            #删除120天前的TR0值
            atr -= tr0list.pop(0)
        if list_result[7] > 0 and atr > 0:
            #模拟交易
            for oldorder in orderlist:
                if 'Buy' in oldorder["Prediction"]: #buy 
                    if Low < oldorder["StopPrice"]: #Stop
                        oldorder["StopDate"] = Date
                        quantity = oldorder["Balance"] * 0.006 / oldorder["Close"] / oldorder["ATR"]
                        buyamount = quantity * oldorder["Close"]
                        sellamount = quantity * oldorder["StopPrice"]
                        Profit = sellamount - buyamount
                        if Profit <= 0:
                            oldorder["Class"] += " loss"
                        else:
                            oldorder["Class"] += " win"
                        #balance += Profit
                        if balance < 0:
                            balance = 0
                        else:
                            oldorder["Profit"] = str(round(Profit / oldorder["Balance"] * 100, 2)) + '%' if oldorder["Balance"] > 0 else '0%'
                        orderlist.remove(oldorder)
                        #continue
                    else:
                        oldorder["TrailingPrice"] = max(oldorder["TrailingPrice"], High)
                        oldorder["StopPrice"] = oldorder["TrailingPrice"] / (atr*2 + 1)
                else: #sell
                    if High > oldorder["StopPrice"]: #Stop
                        oldorder["StopDate"] = Date
                        quantity = oldorder["Balance"] * 0.006 / oldorder["Close"] / oldorder["ATR"]
                        sellamount = quantity * oldorder["Close"]
                        buyamount = quantity * oldorder["StopPrice"]
                        Profit = sellamount - buyamount
                        if Profit <= 0:
                            oldorder["Class"] += " loss"
                        else:
                            oldorder["Class"] += " win"
                        #balance += Profit
                        if balance < 0:
                            balance = 0
                        else:
                            oldorder["Profit"] = str(round(Profit / oldorder["Balance"] * 100, 2)) + '%' if oldorder["Balance"] > 0 else '0%'
                        orderlist.remove(oldorder)
                        #continue
                    else:
                        oldorder["TrailingPrice"] = min(oldorder["TrailingPrice"], Low)
                        oldorder["StopPrice"] = oldorder["TrailingPrice"] * (atr*2 + 1)
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
                "Balance": balance,
                "Days": list_result[10],
                "Datetime": list_result[11],
                }
            market_list.append(neworder)
            orderlist.append(neworder)

    if len(market_list) == 0:
        return market_list, 0.0
    market_list.sort(reverse = True, key = lambda item:item["Date"])
    
    for market_item in market_list:
        market_item["ATR"] = str(round(market_item["ATR"] * 100.0, 2)) + '%'
        market_item["StopPrice"] = float(format(market_item["StopPrice"], '.5g'))


    daycount = market_list[0]["Days"]
    startdate = market_list[0]["Datetime"] + datetime.timedelta(days=-daycount)
    #print("balance = " + str(balance) + ";daycount = " + str(daycount))
    return market_list , math.pow(balance, 365.0 / daycount) - 1 if daycount > 0 else 0.0, pagetotal, startdate.strftime('%Y-%m-%d')


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
    trsum = 0
    dayindex = 0
    for list_result in list_results:
        dayindex += 1
        Date = list_result[0]
        Open = list_result[1]
        High = list_result[2]
        Low = list_result[3]
        Close = list_result[4]
        if last_c == 0:
            last_c = Open #Open Price
        tr = max(High, last_c) / min(Low, last_c) - 1.0
        #last_c = Close
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
        if list_result[7] > 0 and atr > 0:
            #模拟交易
            for oldorder in orderlist:
                if 'Buy' in oldorder["Prediction"]:#buy 
                    if Low < oldorder["StopPrice"]:#Stop
                        oldorder["StopDate"] = Date
                        quantity = oldorder["Balance"] * 0.006 / oldorder["Close"] / oldorder["ATR"]
                        buyamount = quantity * oldorder["Close"]
                        sellamount = quantity * oldorder["StopPrice"]
                        Profit = sellamount - buyamount
                        balance += Profit
                        if balance < 0:
                            balance = 0
                        else:
                            oldorder["Profit"] = str(round(Profit / oldorder["Balance"] * 100, 3)) + '%' if oldorder["Balance"] > 0 else '0%'
                        orderlist.remove(oldorder)
                        #continue
                    else:
                        oldorder["TrailingPrice"] = max(oldorder["TrailingPrice"], High)
                        oldorder["StopPrice"] = oldorder["TrailingPrice"] / (atr*2 + 1)
                else:#sell
                    if High > oldorder["StopPrice"]:#Stop
                        oldorder["StopDate"] = Date
                        quantity = oldorder["Balance"] * 0.006 / oldorder["Close"] / oldorder["ATR"]
                        sellamount = quantity * oldorder["Close"]
                        buyamount = quantity * oldorder["StopPrice"]
                        Profit = sellamount - buyamount
                        balance += Profit
                        if balance < 0:
                            balance = 0
                        else:
                            oldorder["Profit"] = str(round(Profit / oldorder["Balance"] * 100, 3)) + '%' if oldorder["Balance"] > 0 else '0%'
                        orderlist.remove(oldorder)
                        #continue
                    else:
                        oldorder["TrailingPrice"] = min(oldorder["TrailingPrice"], Low)
                        oldorder["StopPrice"] = oldorder["TrailingPrice"] * (atr*2 + 1)
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
                "StopPrice": list_result[4] / (atr*2 + 1) if 'Buy' in list_result[6]  else (atr*2 + 1) * list_result[4],
                "StopDate": '-',
                "Profit": '0.0%',
                "Balance": balance
                }
            market_list.append(neworder)
            orderlist.append(neworder)

    if len(market_list) == 0:
        return market_list, 0.0
    market_list.sort(reverse = True, key = lambda item:item["Date"])
    lastdate = datetime.datetime.strptime(market_list[0]["Date"], '%Y-%m-%d')
    firstdate = datetime.datetime.strptime(market_list[-1]["Date"], '%Y-%m-%d')
    
    update_val = []
    for market_item in market_list:
        market_item["ATR"] = str(round(market_item["ATR"] * 100.0, 2)) + '%'
        market_item["StopPrice"] = float(format(market_item["StopPrice"], '.5g'))

    for market_item in market_list[0:2]:
        currentdays = datetime.datetime.strptime(market_item["Date"], '%Y-%m-%d')
        #当前天数
        days = (currentdays - firstdate ).days
        update_val.append((market_item["Balance"], days, market_id, market_item["Date"]))
    #更新余额
    update_sql = "UPDATE pricehistory SET balance = %s, days = %s where SYMBOL = %s and DATE = %s "
    
    while True:
        try:
            mycursor.executemany(update_sql, update_val)
            myconnector.commit()    # 数据表内容有更新，必须使用到该语句
            break
        except Exception as e:
            print(str(e))
            myconnector.rollback( )
            time.sleep(1)

    daycount = (lastdate - firstdate ).days
    
    return market_list , math.pow(balance, 365.0 / daycount) - 1 if daycount > 0 else 0.0

#Get Input Price List
#Input: {"Prices":[{"Close":[11,22,33],"High":[12,23,34],"Low":[10,21,32]},{"Close":[21,32,43],"High":[22,33,44],"Low":[20,31,42]}]}
def getInputPriceList(body_j_data):
    pricelistsymbols = body_j_data["Prices"]
    inputPriceListSymbols = []
    inputPriceListSymbols2 = []
    symbolCount = len(pricelistsymbols)
    dayscount = len(pricelistsymbols[0]["Close"])
    for pricelistsymbol in pricelistsymbols:
        closelist = [math.log(closePrice) for closePrice in pricelistsymbol["Close"]]
        highlist = [math.log(highPrice) for highPrice in pricelistsymbol["High"]]
        lowlist = [math.log(lowPrice) for lowPrice in pricelistsymbol["Low"]]
        maxprice = max(highlist)
        minprice = min(lowlist)
        rangePrice = maxprice - minprice
        closelistscaled = [(closePrice - minprice) / rangePrice for closePrice in closelist]
        highlistscaled = [(highPrice - minprice) / rangePrice for highPrice in highlist]
        lowlistscaled = [(lowPrice - minprice) / rangePrice for lowPrice in lowlist]
        inputPriceList = []
        for dayindex in range(dayscount):
            inputPriceList.extend([highlistscaled[dayindex],closelistscaled[dayindex],lowlistscaled[dayindex]])
        inputPriceListSymbols.append(inputPriceList)
    for dayindex in range(dayscount*3):
        for symbolindex in range(symbolCount):
            inputPriceListSymbols2.append(inputPriceListSymbols[symbolindex][dayindex])
    return inputPriceListSymbols2

#parse To Rise Prob
#Output: {"RiseProbabilities":[0.6, 0.55]}
def parseToRiseProb(rsp):
    print(rsp)
    if 'error' in rsp:
        return rsp
    problist = [probitem["probabilities"][1] for probitem in rsp["predictions"]]
    outputRiseProb = {"RiseProbabilities": problist}
    return outputRiseProb
