from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import pandas as pd
import json
import os

server_host='127.0.0.1'
server_port=8080
last_data={"time":0,"pisition":0,"temperature":0,"humidity":0,"pressure":0,"wind_speed":0,"noise":0,"rain":0,"pm2dot5":0,"pm10":0}
#空数据，防止出错

'''
可用的请求方法
get None 返回网页
get text：last_data 最近一次的数据
get text：time 授时
get text：need_csv 全部数据（text格式的）
get text：all 全部数据（json格式的）
get text：在all_record_name中的元素 对应元素索引的数据（json格式的）

post json 用于传递数据
'''
all_record_name=['time','pisition','temperature', 'humidity', 'pressure', 'wind_speed', 'noise', 'rain', 'pm2dot5', 'pm10']
#记录值          时间，   地点，     温度，         湿度，     气压，         风速，     噪声， 降雨量，    pm2.5，  pm10

def init_record_file():
    global all_record_name
    if not os.access("./record.csv", os.W_OK):
        with open('./record.csv', 'a+',encoding='utf-8') as record:
            for i in all_record_name:
                record.write(i+",")
            record.write("\n")
                #初始化记录文件

def pd_get(record_name):
    global all_record_name
    record=pd.read_csv("./record.csv",header=0,index_col=0)
    record=record.sort_index(ascending=True)
    #排序
    if record_name=="all":
        return record.to_json(orient="columns",force_ascii=False)
        #以json格式返回整个列表
    elif record_name in all_record_name:
        record = record.loc[:,record_name]
        return record.to_json(orient="columns",force_ascii=False)
        #获取单列数据，并且json序列化，因为时间已经是行索引了，因此不需要把时间切片
    

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_response(self,status,content_type):
        self.send_response(status)
        if content_type=="json":
            self.send_header('Content-type', 'application/json')
        elif content_type=="html":
            self.send_header('Content-type', 'text/html')
        elif content_type=="text":
            self.send_header('Content-type', 'text/plain')
        else:
            self.send_header('')
        self.end_headers()
        #响应头

    def do_GET(self):
        if self.headers['Content-Length']==None:
            self._set_response(200,"html")
            #遗憾的是socketserver不能返回网页，get方法当作api用吧
            with open("./index.html",'r',encoding='utf-8') as index:
                self.wfile.write(index.read().encode('utf-8'))
            #艹，被群友糊弄了，不能返回网页个头子
            #默认的get请求
        else:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            content_type=str(self.headers['Content-Type'])
            #读点get的数据
            
            if content_type=="text/plain":
                data=post_data.decode('utf-8')
                global all_record_name
                
                if str(data)=="last_data":
                    global last_data
                    self._set_response(200,"json")
                    self.wfile.write(json.dumps(last_data).encode('utf-8'))
                    #之前搓的获取最新数据
                elif str(data)=="time":
                    current_date_and_time = str(datetime.now().strftime("%Y/%D-%H:%M:%S"))
                
                    #self._set_response(200,"json")
                    #self.wfile.write(json.dumps({"datetime": current_date_and_time}).encode('utf-8'))
                    
                    self._set_response(200,"text")
                    self.wfile.write(current_date_and_time.encode('utf-8'))
                    
                    #同步时间用的，采集器需要发送一个为text类型的内容为time的post请求,响应体用text还是json自己选
                elif str(data)=="need_csv":
                    self._set_response(200,"text")
                    with open("./record.csv",'r',encoding='utf-8') as record:
                        self.wfile.write(record.read().encode('utf-8'))
                        #返回绘图所需的数据
                        
                elif str(data)=="all" or str(data) in all_record_name:
                    self._set_response(200,"json")
                    self.wfile.write(pd_get(str(data)).encode('utf-8'))
                    #如果是all的话获取总览数据，如果是记录名的话，获取单列数据
                    
                else:
                    self._set_response(404,"text")
                    self.wfile.write("unexpended_request".encode('utf-8'))
            else:
                self._set_response(404,"text")
                self.wfile.write("unexpended_request".encode('utf-8'))
                #万一客户端发癫
        
    def do_POST(self):
        global last_data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        content_type=str(self.headers['Content-Type'])
        #以上是post方法通用的部分
        
        if content_type=="application/json":
            last_data = json.loads(post_data)
            self._set_response(200,"json")
            self.wfile.write(json.dumps({"received": last_data}).encode('utf-8'))
            #这里要不要发个时间回去
            #这里是给采集器发送采集获得的数据用的
            
            with open('./record.csv', 'a+',encoding='utf-8') as record:
                global all_record_name
                for i in all_record_name:
                    if not i==all_record_name[-1]:
                        try:
                            record.write(str(last_data[i])+",")
                        except:
                            record.write("0,")
                            #格式化输入的数据
                    else:
                        try:
                            record.write(str(last_data[i]))
                        except:
                            record.write("0")
                            #你妈的！pandas读到行尾逗号会报错！
               
                record.write("\n")
                #写入获得的数据
                
        else:
            self._set_response(403,"text")
            self.wfile.write("unexpended_request".encode('utf-8'))
            #万一采集器发了点什么奇奇怪怪的东西过来

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler,host=server_host , port=server_port):
    server_address = (host, port)
    with server_class(server_address, handler_class) as httpd:
        print(f'Starting httpd on port {port}...')
        httpd.serve_forever()
        #启动服务
        
if __name__ == '__main__':
    init_record_file()
    run()
#程序启动