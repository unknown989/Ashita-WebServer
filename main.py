# -*- coding: utf-8 -*-

import socket
import sys
from configparser import ConfigParser as cp
from _thread import start_new_thread as snt

class Server():
    def __init__(self):
        co = cp()

        co.read("config.ini")

        sc = co["SERVERINFO"]

        host = sc["HOST"]
        port = sc["PORT"]
        self.mainFile = sc["INDEXFILE"]
        self.defDir = sc["DEFAULTDIR"]
        self.redirect = sc["REDIRECT"]
        self.shownotfounderrorinpage = sc["404_ERROR_PAGE_TOGGLE"]
        self.shownotfounderrorinpage = True if self.shownotfounderrorinpage == "true" else False
        self.redirect = True if self.redirect == "true" else False
        self.redirectloc = sc["REDIRECT_LOCATION"]
        self.error404 = sc["404PAGE"]
        self.error404 = self.defDir+self.error404 if self.defDir.endswith("/") else self.defDir+"/"+self.error404
        self.ip,self.cl = [],[]
        
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print("Binding...")
        self.s.bind((host,int(port)))
        print("Listening...")
        self.s.listen()
        print("Starting The Thread For Accepting Connections...")
        snt(self.acceptClients())
        print("Done")
        self.s.close()
    def acceptClients(self):
        while True:
            i,c = self.s.accept()
            self.ip.append(i)
            self.cl.append(c)
            filename = i.recv(1024)
            print(filename.decode())
            filename = filename.split()[1]
            filename = filename.decode()
            #print("FILENAME REQUESTES : "+str(filename))
            
            if filename == "/":
                filename = self.defDir+"/"+self.mainFile if not self.defDir.endswith("/") else self.defDir+"/"+self.mainFile
            else:
                if str(filename).startswith("/"):
                    filename = self.defDir+"/"+"".join(list(filename)[1:]) if not self.defDir.endswith("/") else self.defDir+"/"+"".join(list(filename)[1:])
                else:
                    filename = self.defDir+"/"+filename if not self.defDir.endswith("/") else self.defDir+"/"+self.mainFile
            print("FILENAME REQUESTES : "+str(filename))
            try:
                with open(filename,"r") as f:
                    content = f.read()
                self.sendMsg("HTTP/1.0 200 OK\r\n\r\n".encode(encoding="utf8"),i)
                for cc in content:
                    self.sendMsg(str(cc).encode(encoding="utf8"),i)
            except Exception as e:
                print(str(e))
                if self.redirect:
                    self.sendMsg("HTTP/1.1 303 See Other\r\nLocation: {}\r\n".format(self.redirectloc).encode(encoding="utf8"),i)
                else:
                    self.sendMsg("HTTP/1.1 404 Not Found\r\n\r\n".encode(encoding="utf8"))
                    if self.shownotfounderrorinpage:
                        with open(self.error404,"r") as f:
                            for ce in f.read():
                                self.sendMsg(ce.encode(encoding="utf8"),i)
            i.close()
    
    def sendMsg(self,msg,ip):
        ip.send(msg)
        print("Sent : "+str(msg))


# Running The Server
try:
    Server()
except KeyboardInterrupt:
    sys.exit()
