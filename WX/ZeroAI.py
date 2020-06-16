# -*- coding: utf-8 -*-
# filename: ZeroAI.py

from wordcloud import WordCloud, STOPWORDS
import mysql.connector
import mypsw
import time
import datetime
import matplotlib.pyplot as plt
from basic import Basic
#from poster.streaminghttp import register_openers
import requests
from requests.packages.urllib3.filepost import encode_multipart_formdata
import json
import glob
import forcastline

class word_in_color(object):
  word_in_rising_major = ''
  word_in_falling_major = ''
  word_in_comments = []
  word_in_rising_minor = []
  word_in_falling_minor = []

def color_word(word, *args, **kwargs):
  if (word == word_in_color.word_in_rising_major):
      color = '#ffffff' # red
  elif (word == word_in_color.word_in_falling_major):
      color = '#f44336' # green
  elif (word in word_in_color.word_in_comments):
      color = '#ffffff' if word_in_color.word_in_rising_major != '' else '#f44336' # grey
  elif (word in word_in_color.word_in_rising_minor):
      color = '#7f7f7f' # deepred
  elif (word in word_in_color.word_in_falling_minor):
      color = '#7a211b' # deepgreen
  else:
      color = '#000000' # black
  return color
    
def utc2local(utc_st):
    #UTC时间转本地时间（+8:00）
    now_stamp = time.time()
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    local_st = utc_st + offset
    return local_st

def chat(origin_input):

  origin_input = origin_input.strip().upper()

  origin_input, aiera_version = forcastline.get_version(origin_input)
  
  input_text, params = forcastline.command(origin_input)

  output_text = ''

  picture_path = 'Img/' + forcastline.pinyin(input_text) + "_" +  aiera_version + "_" + str(params["OFFSET"]) + "_" + str(params["LEN"]) + "_" + str(params["DATE"]) + "_" + datetime.datetime.now().strftime('%Y%m%d%H') + '*.jpg'
  picture_cache = glob.glob(picture_path)
  if picture_cache:
    picture_name = picture_cache[0]
    return picture_url(picture_name)
  
  mydb, mycursor = init_mycursor()

  if input_text == '帮助' or input_text == 'HELP':
    return help_text()

  select_alias_statment = "SELECT symbol_alias.* FROM symbol_alias " \
    " inner join predictlog on symbol_alias.symbol = predictlog.symbol and predictlog.LOADINGDATE > '1950-1-1' " \
    " WHERE symbol_alias.symbol_alias = '" + input_text + "'"

  print(select_alias_statment)

  mycursor.execute(select_alias_statment)
  
  alias_results = mycursor.fetchall()
  
  if len(alias_results) == 0:
    output_text, alias_results = fetch_tag(input_text, mycursor)
    if alias_results == None:
        return output_text
    
  plt.rcParams['font.sans-serif']=['SimHei']
  plt.rcParams['axes.unicode_minus']=False
    
  if len(alias_results) == 0:
    output_text = forcastline.text_no_market(input_text)
    return output_text
    
  if len(alias_results) == 1:
    picture_name, output_text = draw_single(aiera_version, input_text, alias_results, mycursor, params, origin_input)
    if picture_name == None:
        return output_text
  else:
    picture_name = draw_tag(aiera_version, input_text, alias_results)
    
  return picture_url(picture_name)

def draw_single(aiera_version, input_text, alias_results, mycursor, params, origin_input):
    if aiera_version == "V1":
        return draw_single_v1(input_text, alias_results, mycursor)
    if aiera_version == "V2":
        return forcastline.draw_single_v2(input_text, alias_results, mycursor, params, origin_input)

def draw_single_v1(input_text, alias_results, mycursor):
    output_text = ""
    alias_result = alias_results[0]
    select_predictions_statment = "SELECT * FROM predictions WHERE symbol = '" + alias_result[1] + "' ORDER BY time DESC"
    print(select_predictions_statment)
    mycursor.execute(select_predictions_statment)
    predictions_results = mycursor.fetchall()
    if len(predictions_results) == 0:
      output_text = forcastline.text_no_market(input_text)
      return None, output_text
    select_prices_statment = "SELECT * FROM price WHERE symbol = '" + alias_result[1] + "'"
    print(select_prices_statment)
    mycursor.execute(select_prices_statment)
    prices_results = mycursor.fetchall()
    picture_name = draw_market_v1(alias_result, prices_results, predictions_results)
    return picture_name, output_text

def help_text():
    output_text = '您好！欢迎来到AI纪元，我是通向未来之路的向导。\n' \
    '请输入：“全球股指”、“商品期货”、“外汇”、“个股”或“加密货币”，获取实时的市场趋势强弱排名。\n' \
    '输入具体的市场代码如“上证指数”、“黄金”或“比特币”，获取市场未来十天的涨跌趋势。\n' \
    '请使用分散化与自动化的方式进行交易，并控制每笔交易的风险值小于1%。\n' \
    'Hello! Welcome to the AI Era, I am the guide to the future.\n' \
    'Please enter: "INDICES", "COMMODITIES", "CURRENCIES", "STOCKS" or "CRYPTOCURRENCY" to get real-time market trend rankings.\n' \
    'Enter specific market codes such as “SSE”, “Gold” or “Bitcoin” to get the market trending in the next 10 days.\n' \
    'Please use a decentralized and automated approach to trading and control the risk value of each transaction to less than 1%.\n'
    return output_text 

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
    select_tags_statment = 'select * from tags where tag in (%s) ' % ','.join(['%s']*len(endtags))
    print(select_tags_statment)
    mycursor.execute(select_tags_statment, endtags)
    tags_results = mycursor.fetchall()
    for tags_result in tags_results:
        markets.append(tags_result[1])
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

def fetch_tag(input_text, mycursor):

    tagname = input_text

    markets = get_markets_from_tag(tagname, mycursor)
  
    utc_today = datetime.datetime.utcnow()+datetime.timedelta(days=-10)
    today_str = utc_today.strftime("%Y-%m-%d")

    if len(markets) > 0:


        select_alias_statment = "SELECT pricehistory.SYMBOL, pricehistory.date, pricehistory.F, symbol_alias.SYMBOL_ALIAS FROM symbol_alias " \
        " inner join predictlog on symbol_alias.symbol = predictlog.symbol and predictlog.LOADINGDATE > '1950-1-1' and predictlog.MAXDATE >= '"+today_str+"' and predictlog.symbol in (%s)  " \
        " inner join pricehistory on pricehistory.symbol = symbol_alias.symbol and pricehistory.date = predictlog.maxdate and pricehistory.l <> pricehistory.h and pricehistory.c > 0 " \
        " ORDER BY pricehistory.SYMBOL" % ','.join(['%s']*len(markets))
      
        print(select_alias_statment)
      
        mycursor.execute(select_alias_statment, markets)
  
        alias_results = mycursor.fetchall()
    
    else:
      
      input_text = input_text.replace("/","%").replace("-","%").replace("*","%").replace(" ","%").replace("?","%").replace("=","%")

      select_alias_statment = "SELECT * FROM symbol_alias WHERE symbol_alias LIKE '%" + input_text + "%' group by symbol"

      print(select_alias_statment)

      mycursor.execute(select_alias_statment)
  
      alias_results = mycursor.fetchall()
    
      if len(alias_results) > 1:
        '''
        select_alias_statment = "SELECT predictions.*, symbol_alias.SYMBOL_ALIAS FROM symbol_alias " \
        " inner join predictions on predictions.symbol = symbol_alias.symbol WHERE symbol_alias LIKE '%" + input_text + "%' ORDER BY symbol ASC"
        '''

        select_alias_statment = "SELECT pricehistory.SYMBOL, pricehistory.date, pricehistory.F, symbol_alias.SYMBOL_ALIAS FROM symbol_alias " \
        " inner join predictlog on symbol_alias.symbol = predictlog.symbol and predictlog.LOADINGDATE > '1950-1-1' " \
        " inner join pricehistory on pricehistory.symbol = symbol_alias.symbol and pricehistory.date = predictlog.maxdate  and pricehistory.l <> pricehistory.h and pricehistory.c > 0 " \
        " WHERE symbol_alias LIKE '%" + input_text + "%' ORDER BY pricehistory.symbol ASC"

        print(select_alias_statment)

        mycursor.execute(select_alias_statment)
  
        alias_results = mycursor.fetchall() 
    
    return "", alias_results

def init_mycursor():
    word_in_color.word_in_rising_major = ''
    word_in_color.word_in_falling_major = ''
    word_in_color.word_in_comments = []
    word_in_color.word_in_rising_minor = []
    word_in_color.word_in_falling_minor = []
    mydb = mysql.connector.connect(
      host=mypsw.wechatguest.host,
      user=mypsw.wechatguest.user,
      passwd=mypsw.wechatguest.passwd,
      database=mypsw.wechatguest.database,
      auth_plugin='mysql_native_password'
      )
    mycursor = mydb.cursor()
    return mydb, mycursor

def picture_url(picture_name):
    myMedia = Media()
    accessToken = Basic().get_access_token()
    filePath = picture_name
    mediaType = "image"
    murlResp = Media.uplaod(accessToken, filePath, mediaType)
    print(murlResp)
    return murlResp

def draw_market_v1(alias_result, prices_results, predictions_results):
    plt.figure(figsize=(6.4,6.4), dpi=100, facecolor='black')

    predictions_result = predictions_results[0]
    
    #plt.subplot(211)

    plt.style.use('dark_background')

    x=[i for i in range(1,122)]
    y=[prices_results[0][121-price_index] for price_index in range(120)]
    
    plt.title( alias_result[2] + ":" + alias_result[0] + " " 
              + predictions_result[1].strftime('%Y-%m-%d %H:%M') 
              + " UTC\n微信公众号：AI纪元 WeChat Public Account: AI Era V1") #图标题 
    
    #plt.xlabel(u'过去120天收盘价') #X轴标签
    prediction_text, nextprice = forcastline.day_prediction_text(predictions_result[2],float(prices_results[0][2]),float(prices_results[0][122]))
    plt.xlabel( prediction_text ) #X轴标签
    
    #plt.plot(x,y,"green",linewidth=1, label=u"价格")
    y.append(nextprice)
    currentprice = prices_results[0][2]
    if nextprice >= currentprice:
      plt.plot(x,y,"white",label="ATR:"+ str(float(prices_results[0][122])*100) + "%" )
      plt.fill_between(x,min(y),y,facecolor="white",alpha=0.3)
      plt.plot(x,[currentprice] * 121, "w--", label="Price:"+str(currentprice))
    else:
      plt.plot(x,y,"red", label="ATR:"+ str(float(prices_results[0][122])*100) + "%" )
      plt.fill_between(x,min(y),y,facecolor="red",alpha=0.3)
      plt.plot(x,[currentprice] * 121, "r--", label="Price:"+str(currentprice))
  
    plt.annotate(xy=[122,currentprice], s=currentprice, bbox=None)

    if nextprice >= currentprice:
      bbox_props = dict(boxstyle='round',fc='white', ec='k',lw=1)
      plt.annotate(xy=[122,nextprice], s=nextprice, color='white', bbox=None)
    else:
      bbox_props = dict(boxstyle='round',fc='red', ec='k',lw=1)
      plt.annotate(xy=[122,nextprice], s=nextprice, color='red', bbox=None)
    
    plt.legend(loc = 2)
    
    picture_name = 'Img/' + forcastline.pinyin(alias_result[0]) + "_V1" + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.jpg'
    plt.savefig(picture_name, facecolor='black')
    return picture_name

def draw_tag(aiera_version, input_text, alias_results):
    stopwords = set(STOPWORDS) 
    word_frequencies = {}
    market_list = []
    for alias_result in alias_results:
      predictions_result = alias_result
      x=[0,1]
      y=[0.0, score(predictions_result[2])]

      maxvalue = max(y)
      minvalue = min(y)
      if abs(maxvalue) >= abs(minvalue):
        bestvalue = maxvalue
        bestindex = y.index(maxvalue)
      else:
        bestvalue = minvalue
        bestindex = y.index(minvalue)
      
      word_single = predictions_result[3]
      word_single = "/" + word_single + "/"
      market_list.append((word_single, bestvalue))
      wordcount = abs(bestvalue)
      if bestvalue >= 0:
        word_in_color.word_in_rising_minor.append(word_single)
      else:
        word_in_color.word_in_falling_minor.append(word_single)
      
        
      word_frequencies[word_single] = wordcount
    market_list.sort(key=lambda x:x[1], reverse=False)
    time_str = "Time:"+max( [alias_result[1] for alias_result in alias_results] ).strftime('%Y-%m-%d') + "_UTC"
    if abs(market_list[0][1]) > abs(market_list[-1][1]):
      word_in_color.word_in_falling_major = market_list[0][0]
      comment_frequency = int(abs(market_list[0][1]))
    else:
      word_in_color.word_in_rising_major = market_list[-1][0]
      comment_frequency = int(abs(market_list[-1][1]))
    word_in_color.word_in_comments = ['输入：'+input_text,time_str,'微信公众号：AI纪元']
    word_frequencies[word_in_color.word_in_comments[0]] = comment_frequency
    word_frequencies[word_in_color.word_in_comments[1]] = comment_frequency
    word_frequencies[word_in_color.word_in_comments[2]] = comment_frequency
    
    market_index = 0
    y_market = [market[0] for market in market_list]
    x_score = [market[1] for market in market_list]
    y_pos = [i for i, _ in enumerate(y_market)]
    
    wordcloud = WordCloud(width = 700, height = 700, 
                background_color ='black', 
                color_func=color_word,
                stopwords = stopwords,
                font_path='simhei.ttf',
                collocations=False
                ).generate_from_frequencies(word_frequencies)
    
    plt.figure(figsize = (7.0, 7.0), facecolor = None) 
    plt.imshow(wordcloud, interpolation="bilinear") 
    plt.axis("off") 
    plt.margins(x=0, y=0) 
    plt.tight_layout(pad = 0) 
    
    picture_name = 'Img/' + forcastline.pinyin(input_text) + "_" +  aiera_version + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.jpg'
    plt.savefig(picture_name)
    return picture_name

def score(prediction_result):
  return (prediction_result * 2 - 1) * 100

class Media(object):
  #def __init__(self):
    #register_openers()
  #上传图片
  def uplaod(accessToken, filePath, mediaType):
    openFile = open(filePath, "rb")
    param = {'media': openFile.read()}
    postData, content_type = encode_multipart_formdata(param)

    postUrl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s" % (accessToken, mediaType)
    headers = {'Content-Type': content_type}
    files = {'media': open(filePath, "rb")}
    urlResp = requests.post(postUrl, files=files)
    print(urlResp.text)
    return json.loads(urlResp.text)['media_id']
