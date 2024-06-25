from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import json

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        self.wfile.write(json.dumps({"Todo": "I need a inedx.html"}).encode('utf-8'))
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print("post_data")
        print(str(post_data))
        
        content_type=str(self.headers['Content-Type'])
        print(content_type)
        
        self._set_response()
        if content_type=="application/json":
            print("json")
            data = json.loads(post_data)
            self.wfile.write(json.dumps({"received": data}).encode('utf-8'))
            #这里要不要发个时间回去
        elif content_type=="text/plain":
            print("text")
            data=post_data.decode('utf-8')
            if str(data)=="time":
                current_date_and_time = str(datetime.now().strftime("%Y/%D-%H:%M:%S"))
                self.wfile.write(json.dumps({"datetime": current_date_and_time}).encode('utf-8'))
        else:
            print("error")


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8080):
    server_address = ('', port)
    with server_class(server_address, handler_class) as httpd:
        print(f'Starting httpd on port {port}...')
        httpd.serve_forever()

if __name__ == '__main__':
    run()
