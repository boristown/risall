from jinja2 import Environment, FileSystemLoader 
import mydb
import datetime
import time

def generate_html(title, market_type, localtime, body):
    env = Environment(loader=FileSystemLoader('./'))
    template = env.get_template('template.html')     
    with open("index.html",'w+',encoding='utf-8') as fout:   
        html_content = template.render(
                                        title = title,
                                        market_type=market_type , 
                                        localtime=localtime , 
                                        body=body)
        fout.write(html_content)

if __name__ == "__main__":
    while True:
        body = []
        indexlist = mydb.get_index_list()
        for indexline in indexlist:
            result = {
                'ItemNo':indexline[0], 
                'Market':indexline[1], 
                'Date': indexline[2], 
                'Open':indexline[3],
                "High":indexline[4],
                "Low":indexline[5],
                "Close":indexline[6],
                "Side":indexline[7],
                "Score":indexline[8]
                }
            body.append(result)
        generate_html(u"AI纪元AIEra", u"加密货币CryptoCurrency", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), body)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"index.html已生成。")
        time.sleep(10)