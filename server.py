#!/usr/bin/env python3

import json, os, socket, ssl, sys

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

    json_response = {
      "destination_ip": self.ip,
      "headers": list(filter(None, str(self.headers).splitlines())),
      "host": self.host,
      "message": self.msg,
      "region": self.region,
      "source_ip": self.client_address[0],
      "timestamp": str(datetime.now()),
      "zone": self.zone
    }

    self.wfile.write(json.dumps(json_response, indent=2, sort_keys=True).encode())

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
    sys.exit(f"Invalid TLS_MODE value '{TLS_MODE}'\nValid opions are: 'none', 'tls' or 'mtls'")

  print(f'Server started in tls mode "{TLS_MODE}" on port {HTTP_PORT}')
  print(f"  Host {HOST}")
  print(f"  Ip {IP}")
  print(f"  Msg {MSG}")
  print(f"  Region {REGION}")
  print(f"  Zone {ZONE}")
  httpd.serve_forever()

if __name__ == '__main__':
  main()
