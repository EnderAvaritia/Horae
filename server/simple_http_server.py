from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import json
import os

server_port=8080
last_data={"error": "no_data"}

def init_record_file():
    record_name=["时间","温度","湿度"]
    if not os.access("./record.csv", os.W_OK):
        with open('./record.csv', 'a+') as record:
            for i in record_name:
                record.write(i+",")
                #初始化记录文件

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        #通用的响应头

    def do_GET(self):
        global last_data
        self._set_response()
        self.wfile.write(json.dumps(last_data).encode('utf-8'))
        #遗憾的是socketserver不能返回网页，get方法当作api用吧
        
    def do_POST(self):
        global last_data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        #print("post_data")
        #print(str(post_data))
        content_type=str(self.headers['Content-Type'])
        #print(content_type)
        self._set_response()
        #以上是post方法通用的部分
        
        if content_type=="application/json":
            #print("json")
            last_data = json.loads(post_data)
            self.wfile.write(json.dumps({"received": last_data}).encode('utf-8'))
            #这里要不要发个时间回去
            #这里是给采集器发送采集获得的数据用的
            
            with open('./record.csv', 'a+') as record:
                record.write("\n")
                for i in last_data.keys():
                    record.write(str(last_data[i])+",")
                #写入获得的数据
                
        elif content_type=="text/plain":
            #print("text")
            data=post_data.decode('utf-8')
            if str(data)=="time":
                current_date_and_time = str(datetime.now().strftime("%Y/%D-%H:%M:%S"))
                self.wfile.write(json.dumps({"datetime": current_date_and_time}).encode('utf-8'))
                #同步时间用的，采集器需要发送一个为text类型的内容为time的post请求
                
        else:
            self.wfile.write("unexpended_request".encode('utf-8'))
            #万一采集器发了点什么奇奇怪怪的东西过来

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=server_port):
    server_address = ('', port)
    with server_class(server_address, handler_class) as httpd:
        print(f'Starting httpd on port {port}...')
        httpd.serve_forever()
        #启动服务
        
if __name__ == '__main__':
    init_record_file()
    run()
#程序启动