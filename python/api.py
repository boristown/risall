#!/usr/bin/env python
# -*- coding: utf-8 -*-
# by vellhe 2017/7/9
from flask import Flask, send_from_directory, render_template, request
from jinja2 import Environment, FileSystemLoader 
from flask_restful import reqparse, abort, Api, Resource
import mysql.connector
import mypsw
import mydb
from OpenSSL import SSL
from OpenSSL.crypto import *
import contextlib
import json
import donate
import datetime
import time
import math

app = Flask(__name__,static_url_path='',root_path='C:\Forcastlinecom')
api = Api(app)

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '哈哈哈'},
    'todo3': {'task': 'profit!'},
}
#context = SSL.Context(SSL.PROTOCOL_TLSv1_2)
#context.use_privatekey_file('www-forcastline-com-iis-0614213034.pfx')
#context.use_certificate_file('www-forcastline-com-iis-0614213034.pfx')


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


parser = reqparse.RequestParser()
parser.add_argument('task')
parser.add_argument('wd')


# # 操作（put / get / delete）单一资源Todo
# shows a single todo item and lets you delete a todo item
class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201

# # 操作（post / get）资源列表TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201

def init_mycursor():
    myconnection = mysql.connector.connect(
      host=mypsw.host,
      user=mypsw.user,
      passwd=mypsw.passwd,
      database=mypsw.database,
      auth_plugin='mysql_native_password'
      )
    mycursor = myconnection.cursor()
    return myconnection, mycursor

def get_subtags(tagname, mycursor):
    subtags = []
    select_subtags_statment = "select * from subtags where tag = '" + tagname + "' and tag <> subtag"
    print(select_subtags_statment)
    mycursor.execute(select_subtags_statment)
    subtags_results = mycursor.fetchall()
    for subtags_result in subtags_results:
        subtags.append(subtags_result[1])
    return subtags

def get_markets_from_endtags(endtags, mycursor):
    markets = []
    select_tags_statment = 'select symbol_alias.symbol, group_concat(symbol_alias.symbol_alias) ' \
    'from tags inner join symbol_alias on tags.symbol = symbol_alias.symbol where tags.tag in (%s) group by symbol_alias.symbol ' % ','.join(['%s']*len(endtags))
    print(select_tags_statment)
    mycursor.execute(select_tags_statment, endtags)
    tags_results = mycursor.fetchall()
    for tags_result in tags_results:
        markets.append({"id":tags_result[0],"name":tags_result[1]})
    return markets

def get_markets_from_tag(tagname, mycursor):
      nextsubtags = []
      endtags = []
      subtags = get_subtags(tagname, mycursor)
      if len(subtags) == 0:
          endtags.append(tagname)
      while len(subtags) > 0:
          for subtag in subtags:
              nextsubtag = get_subtags(subtag, mycursor)
              if len(nextsubtag) == 0:
                  endtags.append(subtag)
              else:
                  nextsubtags.extend(nextsubtag)
          subtags = nextsubtags
      markets = get_markets_from_endtags(endtags, mycursor)
      return markets

def getMarket(wd):
    if not wd:
        return {"type":"E", "message":"请在form-data中传入wd参数"}
    input_text = wd.strip().upper()
    output_list = []
    myconnection, mycursor = init_mycursor()
    #fetch var name
    select_alias_statment = "SELECT symbol_alias.symbol, group_concat(symbol_alias.symbol_alias) FROM symbol_alias " \
        " inner join predictlog on symbol_alias.symbol = predictlog.symbol and predictlog.LOADINGDATE > '1950-1-1' " \
        " WHERE symbol_alias.symbol_alias = '" + input_text + "' group by symbol"
        
    print(select_alias_statment)
    mycursor.execute(select_alias_statment)
    alias_results = mycursor.fetchall()
    for alias_result in alias_results:
        output_list.append({"id":alias_result[0], "name":alias_result[1]})
    if len(output_list) == 0:
        #fetch var tag
        output_list = get_markets_from_tag(input_text, mycursor)
        if len(output_list) == 0:
            input_text = input_text.replace("/","%").replace("-","%").replace("*","%").replace(" ","%").replace("?","%").replace("=","%")
            select_alias_statment = "SELECT symbol_alias.symbol, group_concat(symbol_alias) FROM symbol_alias WHERE symbol_alias LIKE '%" + input_text + "%' group by symbol"
            print(select_alias_statment)
            mycursor.execute(select_alias_statment)
            alias_results = mycursor.fetchall()
            for alias_result in alias_results:
                output_list.append({"id":alias_result[0], "name":alias_result[1]})
    markets = [market["id"] for market in output_list]
    if len(markets) == 0:
        return [],[]
    return mydb.get_search_list(markets), markets

# # 操作（post / get）资源列表TodoList
# shows a list of all todos, and lets you POST to add new tasks
class Search(Resource):
    def get(self):
        args = parser.parse_args()
        wd = args['wd']
        marketsList, markets = getMarket(wd)
        return marketsList

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201

@contextlib.contextmanager
def pfx_to_pem(pfx_path, pfx_password):
    ''' Decrypts the .pfx file to be used with requests. '''
    with tempfile.NamedTemporaryFile(suffix='.pem', delete=False) as t_pem:
        f_pem = open(t_pem.name, 'wb')
        pfx = open(pfx_path, 'rb').read()
        p12 = OpenSSL.crypto.load_pkcs12(pfx, pfx_password)
        f_pem.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, p12.get_privatekey()))
        f_pem.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, p12.get_certificate()))
        ca = p12.get_ca_certificates()
        if ca is not None:
            for cert in ca:
                f_pem.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert))
        f_pem.close()
        yield t_pem.name

# 设置路由
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')
api.add_resource(Search, '/api/search')

@app.route('/')
def home():
    return app.send_static_file("index.html")

@app.route('/vue')
def vuehome():
    return app.send_static_file("vue/index.html")

def generate_search_html(title, 
                  wd,
                  donate,
                  localtime, body):
    #env = Environment(loader=FileSystemLoader('./'))
    env = Environment(loader=FileSystemLoader('../static/template/'))
    template = env.get_template('searchTemplate.html')
    #with open('../static/' + html_name,'w+',encoding='utf-8') as fout:   
    html_content = template.render(
                                    title = title, 
                                    market_wd = wd,
                                    donate = donate,
                                    localtime=localtime , 
                                    body=body)
    return html_content
    #fout.write(html_content)

list_name={
    "currencies":"外汇",
    "crypto":"加密货币",
    "indices":"全球股指",
    "commodities":"商品期货",
    "stocks":"股票",
    "stocksUS":"美国股票",
    "stocksHK":"香港股票",
    }

html_name = {
    "外汇":"currencies.html",
    "加密货币":"index.html",
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

@app.route('/api/l', methods=['post','get'])
def getlist():
    listname = request.args.get("name")
    if listname not in list_name:
        return {}
    maxrows = int(request.args.get("maxrows"))

    body = []
    keys = []
    market_key = list_name[listname]
    for market_key2 in market_type:
        if market_key2 != market_key:
            keys.append(market_key2)
    if maxrows:
        indexlist = mydb.get_index_list_limit(market_key, maxrows)
    else:
        indexlist = mydb.get_index_list_limit(market_key, 0)
    for indexline in indexlist:
        volume = indexline[7]
        #balance = indexline[12]
        #daycount = indexline[13]
        #annualised = math.pow(balance, 365.0 / daycount) - 1 if daycount > 0 else 0.0
        annualised = indexline[12]
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
            "Symbol":"market.html?symbol="+indexline[10],
            "Annualised": annualised,
            "Color": indexline[13]
            }
        body.append(result)
    #body.sort(reverse = True, key = lambda line:(line["Annualised"], line["Score"]))
    for bodyitem in body:
        bodyitem["Annualised"] = str(round(bodyitem["Annualised"] * 100, 2)) + "%"
    itemNo = 0
    for indexline in body:
        itemNo += 1
        indexline["ItemNo"] = itemNo
    return {
        "title": u"AI预测：" + market_type[market_key] +"--预测线forcastline.com",
        "market_type": market_type[market_key],
        "market_ref2": html_name[keys[0]],
        "market_type2": market_type[keys[0]],
        "market_ref3": html_name[keys[1]],
        "market_type3": market_type[keys[1]],
        "market_ref4": html_name[keys[2]],
        "market_type4": market_type[keys[2]],
        "market_ref5": html_name[keys[3]],
        "market_type5": market_type[keys[3]],
        "market_ref6": html_name[keys[4]],
        "market_type6": market_type[keys[4]],
        "market_ref7": html_name[keys[5]],
        "market_type7": market_type[keys[5]],
        "donate": donate.donate,
        "localtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "markets": body,
        }

@app.route('/s', methods=['post','get'])
def searchpage():
    wd = request.args.get('wd')
    marketlist, markets = getMarket(wd)
    if len(marketlist) == 1:
        return app.send_static_file("market/" + markets[0] +".html")
    #marketlist = json.loads(marketJson)
    body = []
    for marketitem in marketlist:
        indexline = marketitem
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
            "Symbol":"market/"+indexline[10] + ".html"
            }
        body.append(result)
    body.sort(reverse = True, key = lambda line:(line["Score"]))
    itemNo = 0
    for indexline in body:
        itemNo += 1
        indexline["ItemNo"] = itemNo
    renderedhtml = generate_search_html(u"AI预测：" + wd +"--预测线forcastline.com", 
                    wd,
                    donate.donate,
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 
                    body)
    return renderedhtml

#@app.route('/<file>')
#def openfiles():
#    return app.send_static_file("<file>")

#@app.route('/market/<id>')
#def market(id):
#    return app.send_static_file("market/"+id+".html")

if __name__ == '__main__':
    #app.run(host="0.0.0.0", ssl_context='adhoc')
    #passwd = ''
    #p12 = load_pkcs12(open('ssl/www-forcastline-com-iis-0614213034.pfx', 'rb').read(), passwd)
    #pkey = p12.get_privatekey()
    #open('ssl/pkey.pem', 'wb').write(dump_privatekey(FILETYPE_PEM, pkey))
    #cert = p12.get_certificate()
    #open('ssl/cert.pem', 'wb').write(dump_certificate(FILETYPE_PEM, cert))
    #ca_certs = p12.get_ca_certificates()
    #ca_file = open('ssl/ca.pem', 'wb')
    app.run(host="0.0.0.0", port="443", ssl_context=('../static/ssl/cert.pem','../static/ssl/pkey.pem'))
