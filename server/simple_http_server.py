from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import json
import os

server_host='127.0.0.1'
server_port=8080
last_data={"error": "no_data"}

'''
可用的请求方法
get None 返回网页
get text：last_data 最近一次的数据
get text：time 授时
get text：need_csv 全部数据
post json 用于传递数据
post text：time 授时
'''

def init_record_file():
    record_name=["地点","时间","温度","湿度"]
    if not os.access("./record.csv", os.W_OK):
        with open('./record.csv', 'a+',encoding='utf-8') as record:
            for i in record_name:
                record.write(i+",")
                #初始化记录文件

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
                record.write("\n")
                for i in last_data.keys():
                    record.write(str(last_data[i])+",")
                #写入获得的数据
                
        elif content_type=="text/plain":
            data=post_data.decode('utf-8')
            if str(data)=="time":
                current_date_and_time = str(datetime.now().strftime("%Y/%D-%H:%M:%S"))
                
                #self._set_response(200,"json")
                #self.wfile.write(json.dumps({"datetime": current_date_and_time}).encode('utf-8'))
                
                self._set_response(200,"text")
                self.wfile.write(current_date_and_time.encode('utf-8'))
                
                #同步时间用的，采集器需要发送一个为text类型的内容为time的post请求,响应体用text还是json自己选
                
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