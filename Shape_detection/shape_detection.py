# 形状 电脑端   canny版本
import cv2 as cv
import numpy as np
import socket
import serial
import time
import os
import math
import threading
#---------------------------------------------------------------------------------------------------
SERVER_IP = "192.168.3.213"  # 树莓派的IP地址
SERVER_PORT = 8888           # port号
server_addr = (SERVER_IP, SERVER_PORT)  #地址+port
socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#---------------------------------------------------------------------------------------------------
while True:
    try:
        print("Connecting to server @ %s:%d..." % (SERVER_IP, SERVER_PORT))
        socket_tcp.connect(server_addr)
        break
    except Exception:
        print("Can't connect to server,try it latter!")
        time.sleep(1)
        continue
#---------------------------------------------------------------------------------------------------
print("Arm init...")
init="init"
socket_tcp.send(init.encode("utf-8"))

while True:
    data = socket_tcp.recv(512)
    if data == b"finish":
        break
    elif len(data) > 3:
        print(data)
        while True:
            time.sleep(3)
            print("raspberry serial error")
#---------------------------------------------------------------------------------------------------
arduino = serial.Serial("/dev/ttyACM2",115200,timeout = 0.0001)
time.sleep(1.5)
print("arduino connecting")

def arduinoSerial():
    arduino.write("45".encode('utf-8'))
    time.sleep(0.5)
#---------------------------------------------------------------------------------------------------
def socketrecv():
    while True:
        data = socket_tcp.recv(512)
        if data == b"finish":
            break
        elif len(data) > 3:
            print(data)
            while True:
                time.sleep(5)
                print("raspberry serial error")
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def angle(point_1, point_2, point_0):
    x1 = point_1[0][0] - point_0[0][0]
    y1 = point_1[0][1] - point_0[0][1]
    x2 = point_2[0][0] - point_0[0][0]
    y2 = point_2[0][1] - point_0[0][1]

    compress = 10

    cosine_ag = ((x1 * x2 + y1 * y2) / compress) / math.sqrt(((x1 * x1 + y1 * y1) / compress) * ((x2 * x2 + y2 * y2)
                                                                                                 / compress) + 1e-10)
    scale_ag = (x1 * x1 + y1 * y1) / (x2 * x2 + y2 * y2)
    return cosine_ag, scale_ag
#---------------------------------------------------------------------------------------------------

class ShapeAnalysis:
    def __init__(self):
        self.shapes = {'triangle': 0, 'rectangle': 0, 'polygons': 0, 'circles': 0}

    def analysis(self, frame):
        global run_Flag
        h, w, ch = frame.shape
        result = np.zeros((h, w, ch), dtype=np.uint8)                       #长 、 宽 、 通道数

        print("start to detect lines...\n")
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)                        #原始图像灰度化  # cv.imshow("gray",gray)

        ret, binary = cv.threshold(gray, 100, 255, cv.THRESH_BINARY)        #对灰度化图像二值化  # cv.imshow("binary",binary)

        yu = binary & gray                                                  #二值化和灰度化 与操作  # cv.imshow("yu",yu)

        #cv.imshow("input image", frame)                                     #显示原图像

        canny = cv.Canny(yu, 255, 255, 3)                                   #对yu图像canny边缘检测  # 80 240 3  #参数自己测试

        #cv.imshow("canny",canny)                                            #显示canny边缘检测图像

        contours,hierachy = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)  #轮廓检测
        # ---------------------------------------------------------------------------------------------------
        if len(contours)>0:
            for cnt in range(len(contours)):
                print("cot",len(contours))
                area = cv.contourArea(contours[cnt])                            #计算轮廓面积
                if area > 222:                                                  #用面积过滤噪声

                    cv.drawContours(result, contours, cnt, (0, 255, 0), 2)      #绘制轮廓

                    epsilon = 0.02 * cv.arcLength(contours[cnt], True)          #
                    approx = cv.approxPolyDP(contours[cnt], epsilon, True)      #轮廓逼近

                    corners = len(approx)                                       #角点数判断
                    shape_type = ""                                             #
                    # ---------------------------------------------------------------------------------------------------
                    if corners == 3:
                        count = self.shapes['triangle']
                        count = count+1
                        self.shapes['triangle'] = count
                        shape_type = "triangle"   #三角形
                        arduinoSerial()
                        time.sleep(0.2)
                        socket_tcp.send("triangle".encode("utf-8"))
                        socketrecv()
                    # ---------------------------------------------------------------------------------------------------
                    elif corners == 4:
                        maxCosine = 0
                        for j in range(2, 5):
                            cosine, scale = angle(approx[j % 4], approx[j - 2], approx[j - 1])
                            cosine = math.fabs(cosine)
                            maxCosine = max(maxCosine, cosine)
                            print(maxCosine)

                        if maxCosine > 0.6:
                            count = self.shapes['triangle']
                            count = count + 1
                            self.shapes['triangle'] = count
                            shape_type = "triangle"  # 三角形
                            arduinoSerial()
                            time.sleep(0.2)
                            socket_tcp.send("triangle".encode("utf-8"))
                            socketrecv()

                        elif maxCosine < 0.3:
                            count = self.shapes['rectangle']
                            count = count + 1
                            self.shapes['rectangle'] = count
                            shape_type = "rectangle"  # 四边形
                            arduinoSerial()
                            time.sleep(0.2)
                            socket_tcp.send("square".encode("utf-8"))
                            socketrecv()
                    # ---------------------------------------------------------------------------------------------------
                    elif corners > 4 and corners <= 6:
                        if area < 1800:
                            count = self.shapes['triangle']
                            count = count + 1
                            self.shapes['triangle'] = count
                            shape_type = "triangle"  # 三角形
                            arduinoSerial()
                            time.sleep(0.2)
                            socket_tcp.send("triangle".encode("utf-8"))
                            socketrecv()

                        else:
                            count = self.shapes['rectangle']
                            count = count + 1
                            self.shapes['rectangle'] = count
                            shape_type = "rectangle"  # 四边形
                            arduinoSerial()
                            time.sleep(0.2)
                            socket_tcp.send("square".encode("utf-8"))
                            socketrecv()
                    # ---------------------------------------------------------------------------------------------------
                    elif corners >= 8:
                        count = self.shapes['circles']
                        count = count + 1
                        self.shapes['circles'] = count
                        shape_type = "circles"  #圆
                        arduinoSerial()
                        time.sleep(0.2)
                        socket_tcp.send("circle".encode("utf-8"))
                        socketrecv()

                    # ---------------------------------------------------------------------------------------------------
                    elif 6 < corners < 8:
                        count = self.shapes['polygons']
                        count = count + 1
                        self.shapes['polygons'] = count
                        shape_type = "polygons"  #多边形
                        arduinoSerial()
                        time.sleep(0.2)
                    # ---------------------------------------------------------------------------------------------------
                    # 求解中心位置
                    run_Flag = True
                    print("run_flag = true")
                    mm = cv.moments(contours[cnt])
                    if mm['m00'] != 0:
                        cx = int(mm['m10'] / mm['m00'])
                        cy = int(mm['m01'] / mm['m00'])
                        cv.circle(result, (cx, cy), 3, (0, 0, 255), -1)
                        # if shape_type != "polygons":
                        cv.putText(result, shape_type, (cx, cy), cv.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 0), 1)
                        cv.putText(result, str(corners), (cx, cy+20), cv.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 0), 1)

                    # 颜色分析
                        color = frame[cy][cx]
                        color_str = "(" + str(color[0]) + ", " + str(color[1]) + ", " + str(color[2]) + ")"

                        # 计算面积与周长
                        p = cv.arcLength(contours[cnt], True)
                        area = cv.contourArea(contours[cnt])
                        print("周长: %.3f, 面积: %.3f 颜色: %s 形状: %s "% (p, area, color_str, shape_type))
                else:
                    arduinoSerial()
                    time.sleep(0.5)
                    run_Flag = True
        else :
            arduinoSerial()
            time.sleep(0.5)
            run_Flag = True

        #cv.imshow("Analysis Result", self.draw_text_info(result))
        #cv.imwrite("./test-result.png", self.draw_text_info(result))
        return self.shapes

    def draw_text_info(self, image):
        c1 = self.shapes['triangle']
        c2 = self.shapes['rectangle']
        c3 = self.shapes['polygons']
        c4 = self.shapes['circles']
        cv.putText(image, "triangle: "+str(c1), (10, 20), cv.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 0), 1)
        cv.putText(image, "rectangle: " + str(c2), (10, 40), cv.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 0), 1)
        cv.putText(image, "polygons: " + str(c3), (10, 60), cv.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 0), 1)
        cv.putText(image, "circles: " + str(c4), (10, 80), cv.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 0), 1)
        return image
#---------------------------------------------------------------------------------------------------
ld = ShapeAnalysis()
camera = cv.VideoCapture(6)
run_Flag = True
while camera.isOpened:
    ret, src = camera.read()
    if not ret:
        break
    cv.imshow("src",src)
    src = src[260: 360, 270: 370]
    if run_Flag:
        run_Flag = False
        t = threading.Thread(target=ld.analysis,args = (src,))
        t.setDaemon(True)
        t.start()
        #time.sleep(0.1)
    
    for i in range(5):
        ret, src = camera.read()
        pass
    if cv.waitKey(1) == 27:
        break    
cv.destroyAllWindows()    


