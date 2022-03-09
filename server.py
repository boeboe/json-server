#!/usr/bin/env python3

import os, socket, ssl, sys

from datetime import datetime
# from dotenv import load_dotenv
from functools import partial
from http.server import HTTPServer, BaseHTTPRequestHandler

class CustomHandler(BaseHTTPRequestHandler):

  def __init__(self, host, ip, msg, region, zone, *args, **kwargs):
    self.host = host
    self.ip = ip
    self.msg = msg
    self.region = region
    self.zone = zone
    super().__init__(*args, **kwargs)

  def do_GET(self):
    self.send_response(200)
    self.send_header('content-type','application/json')
    self.end_headers()

    json_response = """{
  "destination_ip": "%s",
  "headers": "%s",
  "host": "%s",
  "message": "%s",
  "region": "%s",
  "source_ip": "%s",
  "timestamp": "%s",
  "zone": "%s"
}""" % (self.ip, list(filter(None, str(self.headers).splitlines())), self.host, self.msg,
        self.region, self.client_address[0], str(datetime.now()), self.zone)

    self.wfile.write(json_response.encode())

def main():
  # load_dotenv()
  
  HTTP_PORT = int(os.getenv('HTTP_PORT', 8080))
  HOST = socket.gethostname()
  IP = socket.gethostbyname(HOST)
  MSG = os.getenv('MSG', "Hello grasshopper!")
  REGION = os.getenv('REGION', "Unkown")
  ZONE = os.getenv('ZONE', "Unkown")
  TLS_MODE = os.getenv('TLS_MODE', "none").lower()
  SERVER_CERT = os.getenv('SERVER_CERT', "")
  SERVER_KEY = os.getenv('SERVER_KEY', "")
  CLIENT_CA_CERT = os.getenv('CLIENT_CA_CERT', "")

  handler = partial(CustomHandler, HOST, IP, MSG, REGION, ZONE)
  httpd = HTTPServer(('',HTTP_PORT), handler)

  if TLS_MODE == "none":
    pass
  elif TLS_MODE == "tls":
    if not os.path.isfile(SERVER_CERT):
      sys.exit(f"SERVER_CERT file '{SERVER_CERT}' does not exist")
    if not os.path.isfile(SERVER_KEY):
      sys.exit(f"SERVER_KEY file '{SERVER_KEY}' does not exist")

    httpd.socket = ssl.wrap_socket(httpd.socket, 
                                   certfile=SERVER_CERT,
                                   keyfile=SERVER_KEY, 
                                   server_side=True)

  elif TLS_MODE == "mtls":
    if not os.path.isfile(SERVER_CERT):
      sys.exit(f"SERVER_CERT file '{SERVER_CERT}' does not exist")
    if not os.path.isfile(SERVER_KEY):
      sys.exit(f"SERVER_KEY file '{SERVER_KEY}' does not exist")
    if not os.path.isfile(CLIENT_CA_CERT):
      sys.exit(f"CLIENT_CA_CERT file '{CLIENT_CA_CERT}' does not exist")

    httpd.socket = ssl.wrap_socket(httpd.socket, 
                                   certfile=SERVER_CERT,
                                   keyfile=SERVER_KEY, 
                                   ca_certs=CLIENT_CA_CERT,
                                   server_side=True,
                                   cert_reqs=ssl.CERT_REQUIRED,
                                   do_handshake_on_connect=True)
  else:
    print(f"Invalid TLS_MODE environment variable value {TLS_MODE}")
    print("Try any of the following: none, tls or mtls")
    exit(1)

  print(f'Server started in tls mode "{TLS_MODE}" on port {HTTP_PORT}')
  print('  Host %s' %HOST)
  print('  Ip %s' %IP)
  print('  Msg %s' %MSG)
  print('  Region %s' %REGION)
  print('  Zone %s' %ZONE)
  httpd.serve_forever()

if __name__ == '__main__':
  main()
