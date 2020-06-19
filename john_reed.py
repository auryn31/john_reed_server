import requests
import json
import http.server
import socketserver
from http import HTTPStatus
import redis
from datetime import datetime
from urllib.parse import urlparse
import urllib.parse as urlparse
from urllib.parse import parse_qs
from datetime import date, timedelta


def load_json(r, studio, yesterday):
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y-%H")
    if yesterday == True:
        yesterday = date.today() - timedelta(days=1)
        timestampStr = yesterday.strftime("%d-%b-%Y-23")
    redis_key = studio + '-' + timestampStr
    print("["+timestampStr+"] Call for key: " + redis_key + " yesterday: " + str(yesterday))
    a = r.get(redis_key)
    if a:
        return a
    if yesterday:
        return 'null'
    x = requests.get('https://typo3.johnreed.fitness/studiocapacity.json?studioId='+studio)
    r.set(redis_key, x.content)
    return x.content



PORT = 8080
password = ''
r = redis.from_url('redis://:{}@redis:6379/0'.format(password), decode_components=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse.urlparse(self.path)

        url_parameter = parse_qs(parsed.query)
        studio = url_parameter["studio"][0]
        yesterday = False
        if "yesterday" in url_parameter:
            yesterday = url_parameter["yesterday"][0] == 'True' or url_parameter["yesterday"][0] == 'true'
        content = load_json(r, studio, yesterday)
        print(content)
        if content != 'null':
            self.send_response(HTTPStatus.OK)
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.end_headers()

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print("serving at port", PORT)
    print("Example call: curl localhost:8080/\?studio=1414810010")
    httpd.serve_forever()