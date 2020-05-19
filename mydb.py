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

def get_index_list():
    index_list = []
    myconnector, mycursor = init_mycursor()
    list_statement = '''
    SELECT b.symbol_alias, DATE_FORMAT(a.date,"%Y-%m-%d"), a.o, a.h, a.l, a.c, if(a.f>=0.5,"涨↑","跌↓") as side, abs((a.f*2-1)*100) as score 
    FROM zeroai.pricehistory as a inner join zeroai.symbol_alias as  b on a.symbol = b.symbol
    inner join zeroai.predictlog as c on a.symbol = c.symbol and a.date = c.MAXDATE
    where b.MARKET_TYPE = "加密货币"
    and a.date > DATE_ADD(curtime(),INTERVAL -10 DAY)
    and a.f <> 0.5
    order by score desc;
    '''
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
            list_result[7]
            ])
    return index_list
