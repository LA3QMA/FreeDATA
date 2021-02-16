#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 21:25:14 2020

@author: DJ2LS
"""

import socketserver
import threading
import logging


import static
import arq

class DATATCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
    
        self.data = bytes()
        while True: 
            chunk = self.request.recv(8192)#.strip() 
            self.data += chunk
            if chunk.endswith(b'\n'):
                break

        # SEND AN ARQ FRAME  -------------------------
        if self.data.startswith(b'ARQ:'):

            data = self.data.split(b'ARQ:')
            data_out = data[1]
                               
            TRANSMIT_ARQ = threading.Thread(target=arq.transmit, args=[data_out], name="TRANSMIT_ARQ")
            TRANSMIT_ARQ.start()
                
                

class CMDTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
    
        self.data = bytes()
        while True: 
            chunk = self.request.recv(8192)#.strip() 
            self.data += chunk
            if chunk.endswith(b'\n'):
                break

        
        
        # self.request is the TCP socket connected to the client
        #self.data = self.request.recv(1024).strip()
###        self.data = self.request.recv(1000000).strip()
     
        # interrupt listening loop "while true" by setting MODEM_RECEIVE to False
        #if len(self.data) > 0:
       #     static.MODEM_RECEIVE = False
        
        
        ####print("{} wrote:".format(self.client_address[0]))
        ####print(self.data)
        
        # just send back the same data, but upper-cased
        #####self.request.sendall(self.data.upper())
        
        #if self.data == b'TEST':
            #logging.info("DER TEST KLAPPT! HIER KOMMT DER COMMAND PARSER HIN!")
        if self.data.startswith(b'SHOWBUFFERSIZE'):
            self.request.sendall(bytes(static.RX_BUFFER[-1]))
            print(static.RX_BUFFER_SIZE)




def start_cmd_socket():

    try:
        logging.info("SRV | STARTING TCP/IP SOCKET FOR CMD ON PORT: " + str(static.PORT))
        socketserver.TCPServer.allow_reuse_address = True #https://stackoverflow.com/a/16641793
        cmdserver = socketserver.TCPServer((static.HOST, static.PORT), CMDTCPRequestHandler)
        cmdserver.serve_forever()
    
    finally:
        cmdserver.server_close()
        
        
def start_data_socket():

    try:
        logging.info("SRV | STARTING TCP/IP SOCKET FOR DATA ON PORT: " + str(static.PORT + 1))
        socketserver.TCPServer.allow_reuse_address = True #https://stackoverflow.com/a/16641793
        dataserver = socketserver.TCPServer((static.HOST, static.PORT + 1), DATATCPRequestHandler)
        dataserver.serve_forever()
    
    finally:
        dataserver.server_close()                              
