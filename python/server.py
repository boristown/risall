from tornado.httpserver import HTTPServer
from tornado.wsgi import WSGIContainer
from api import app
from tornado.ioloop import IOLoop

s = HTTPServer(WSGIContainer(app),ssl_context=('../static/ssl/cert.pem','../static/ssl/pkey.pem'))
s.bind(443, "0.0.0.0")
s.listen(9900) # 监听 9900 端口
IOLoop.current().start()
