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
        self.ip,self.cl = [],[]

        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print("Binding...")
        self.s.bind((host,int(port)))
        print("Listening...")
        self.s.listen()
        print("Starting The Thread For Accepting Connections...")
        snt(self.accept())
        print("Done")
    def accept(self):
        while True:
            i,c = self.s.accept()
            self.ip.append(i)
            self.cl.append(c)
            filename = i.recv(1024)
            filename = filename.split()[1]
            filename = filename.decode()
            #print("FILENAME REQUESTES : "+str(filename))
            self.sendMsg("HTTP/1.0 200 OK\r\n\r\n",i)
            if filename == "/":
                filename = self.defDir+"/"+self.mainFile if not self.defDir.endswith("/") else self.defDir+"/"+self.mainFile
            else:
                if str(filename).startswith("/"):
                    filename = self.defDir+"/"+"".join(list(filename)[1:]) if not self.defDir.endswith("/") else self.defDir+"/"+"".join(list(filename)[1:])
                else:
                    filename = self.defDir+"/"+filename if not self.defDir.endswith("/") else self.defDir+"/"+self.mainFile
            print("FILENAME REQUESTES : "+str(filename))
            try:
                if not filename.endswith("ico"):
                    with open(filename,"r") as f:
                        content = f.read()
                    for cc in content:
                        self.sendMsg(str(cc),i)
                else:
                    with open(filename,"rb") as f:
                        content = f.read()
                    for cc in content:
                        self.sendMsg(cc.encode(),i,enc=False)
            except:
                self.sendMsg(str("404 Not Found"),i)
            i.close()
    
    def sendMsg(self,msg,ip,enc=True):
        if enc:
            ip.send(msg.encode())
            print("Sent...")
        else:
            ip.send(msg)
            print("Sent No Encoded...")


# Running The Server
try:
    Server()
except KeyboardInterrupt:
    sys.exit()
