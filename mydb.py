import mypsw
import mysql.connector

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
    SELECT b.symbol_alias, DATE_FORMAT(a.date, "%%Y-%%m-%%d") as date, a.o, a.h, a.l, a.c, if(a.f>=0.5,"即将上涨↑","即将下跌↓") as side, abs((a.f*2-1)*100) as score , b.symbol
    FROM zeroai.pricehistory as a inner join 
    (select symbol,group_concat(symbol_alias) as symbol_alias, market_type from zeroai.symbol_alias group by symbol, market_type) as b on a.symbol = b.symbol
    inner join zeroai.predictlog as c on a.symbol = c.symbol and a.date = c.MAXDATE
    where b.MARKET_TYPE = '%s'
    and a.date > DATE_ADD(curtime(),INTERVAL -10 DAY)
    and a.f <> 0.5 and a.l <> a.h and a.o > 0
    order by score desc;
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
            list_result[8]
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
    SELECT DATE_FORMAT(date, "%%Y-%%m-%%d") as date, O, H, L, C, V, if(F>=0.5,"即将上涨↑","即将下跌↓") as side, abs((F*2-1)*100) as score
    FROM zeroai.pricehistory where symbol = '%s'  and f <> 0.5 and l <> h and o > 0
    order by date desc;
    ''' % (market_id)
    mycursor.execute(list_statement)
    list_results = mycursor.fetchall()
    lineno = 0
    for list_result in list_results:
        lineno += 1
        market_list.append({
            "Date":list_result[0],
            "Open":list_result[1],
            "High":list_result[2],
            "Low":list_result[3],
            "Close":list_result[4],
            "Volume":list_result[5],
            "Today":round((list_result[4] / list_result[1] - 1)*100,2),
            "Prediction":list_result[6],
            "Score":round(list_result[7],2),
            "Class":'rise' if '涨' in list_result[6] else 'fall',
            })
    return market_list
