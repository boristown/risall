#!/usr/bin/env python
# -*- coding: utf-8 -*-
# by vellhe 2017/7/9
from flask import Flask, send_from_directory, render_template
from flask_restful import reqparse, abort, Api, Resource
import mysql.connector
import mypsw
import mydb
from OpenSSL import SSL
from OpenSSL.crypto import *
import contextlib

app = Flask(__name__,static_url_path='')
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

# # 操作（post / get）资源列表TodoList
# shows a list of all todos, and lets you POST to add new tasks
class Search(Resource):
    def get(self):
        args = parser.parse_args()
        wd = args['wd']
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
        return mydb.get_search_list(markets)

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
    return app.send_static_file("../static/index.html")

#@app.route('/<file>')
#def openfiles():
#    return app.send_static_file("<file>")

@app.route('/market/<id>')
def market(id):
    return app.send_static_file("../static/market/"+id+".html")

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
