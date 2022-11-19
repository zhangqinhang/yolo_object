# coding:utf-8
# import necessary package     #形状 树莓派端
import socket
import time
import sys

import cv2
import numpy as np
import urllib
import threading
import signal
import LeArm
import kinematics as kin
import RPi.GPIO as GPIO

HOST_IP = "0.0.0.0"  # 树莓派的IP地址
HOST_PORT = 8888
print("Starting socket: TCP...")
# 1.create socket object:socket=socket.socket(family,type)
socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("TCP server listen @ %s:%d!" % (HOST_IP, HOST_PORT))
host_addr = (HOST_IP, HOST_PORT)
# 2.bind socket to addr:socket.bind(address)
socket_tcp.bind(host_addr)
# 3.listen connection request:socket.listen(backlog)
socket_tcp.listen(1)
# 4.waite for client:connection,address=socket.accept()
socket_con, (client_ip, client_port) = socket_tcp.accept()
print("Connection accepted from %s." % client_ip)

print("Receiving package...")
data1 = "finish"
triangle = 0
circle = 0
square = 0


while True:
    try:
        data = socket_con.recv(512)
        if len(data) > 0:
            if data == "init":
                print("arm init...")
                LeArm.runActionGroup('init', 1)  #chushi → init
                print("arm init complete...")
                socket_con.send(data1.encode("utf-8"))

            elif data == "triangle":
                print("triangle...")
                if triangle == 0:
                    LeArm.runActionGroup('triangle1', 1)  #youbian → triangle1
                    print("triangle complete")
                    triangle = 1
                elif triangle == 1:
                    LeArm.runActionGroup('triangle2', 1)  #youbian → triangle2
                    print("triangle complete")
                    triangle = 0
                LeArm.runActionGroup('init', 1)
                socket_con.send(data1.encode("utf-8"))

            elif data == "square":
                print("square...")
                if square == 0:
                    LeArm.runActionGroup('square1', 1) #xingzhuang → square1
                    print("square complete")
                    square = 1
                elif square == 1:
                    LeArm.runActionGroup('square2', 1) #xingzhuang → square2
                    print("square complete")
                    square = 0
                LeArm.runActionGroup('init', 1)
                socket_con.send(data1.encode("utf-8"))

            elif data == "circle":
                print("circle...")
                if circle == 0:
                    LeArm.runActionGroup('circle1', 1) #zhongjian → circle1
                    print("circle complete")
                    circle = 1
                elif circle == 1:
                    LeArm.runActionGroup('circle2', 1) #zhongjian → circle2
                    print("circle complete")
                    circle = 0
                LeArm.runActionGroup('init', 1)
                socket_con.send(data1.encode("utf-8"))
            continue
    except Exception:
        socket_tcp.close()
        sys.exit(1)

