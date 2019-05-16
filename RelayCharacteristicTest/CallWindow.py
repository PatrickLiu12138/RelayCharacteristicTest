import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow,QApplication,QTabWidget
from RCTWindow import *
from SerialManager import serManager
import img

class windows(QMainWindow, MainWindow):
    def __init__(self, parent = None):
        super(windows, self).__init__(parent)
        self.uartIsOpen = 0
        self.portData = 0
        self.level = []
        self.portChoice = ''
        self.initUi()

    def initUi(self):
        self.setupUi()

        #设置中心的子窗口
        self.child = ChildWindow()
        mainFarm = QWidget(self)
        mainFarm.setLayout(self.child.allLayout)
        self.child.sendBtn.clicked.connect(self.SendUARTAline)#子窗口的触发信号
        self.setCentralWidget(mainFarm)

        #主窗口的各种触发信号
        self.startUart.triggered.connect(self.OpenUart)
        self.closeUart.triggered.connect(self.CloseUart)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.RecvUartALine)
        self.timer.start(0)

    def ChangePicData(self):
        self.child.widget.tab3.update_figure()
        self.child.widget.tab4.update_figure()

    def RecvUartALine(self):
        if(self.uartIsOpen == 1):
            recvData = self.ser.RecvALine()
            if(recvData != None and recvData != '\n'):
                self.child.recvEdit.append('>' + recvData)  #接收框显示
                self.VerifyData(recvData)

    def VerifyData(self, data):
        if(data[0:2] == 'V='):
            self.child.widget.tab1.uText = 'V=' + str(int(data[2:8], 16)/100) + 'V' #修改head>tab1图上的文字
            self.child.widget.update()
            if(data[10:12] == 'I='):
                self.child.widget.tab1.iText = 'I=' + str(int(data[12:18], 16)/100) + 'mA'    #修改head>tab1图上的文字
                self.child.widget.update()
        # 不能写'FFFF'进行判断  具体原因不清楚  求助！！！
                temp = int(data[24:28], 16)
                if (data[20:22] == 'P=') and (temp != self.portData):   #修改head>tab1图上端口连线
                    self.portData = list('{:016b}'.format(temp))
                    self.portData.reverse()
                    self.child.widget.tab1.port = self.portData
                    self.child.widget.tab1.update()
        if(data[1:6] == ':20DC' or data[1:6] == ':20DD' or data[1:6] == ':20DE' or data[1:6] == ':20DF'):
            if(data[1:8] == ':20DC00'):
                #初始化tab4数据
                self.child.widget.tab4.val = [1 for i in range(512)]
                self.child.widget.tab4.val1 = [2 for i in range(512)]
                #初始化tab3数值
                self.child.widget.tab3.val = [1 for i in range(512)]
                self.child.widget.tab3.val1 = [2 for i in range(512)]
                self.child.widget.tab3.val2 = [3 for i in range(512)]
                self.child.widget.tab3.val3 = [4 for i in range(512)]
                self.child.widget.tab3.val4 = [5 for i in range(512)]
                self.child.widget.tab3.val5 = [6 for i in range(512)]
                self.child.widget.tab3.val6 = [7 for i in range(512)]
                self.child.widget.tab3.val7 = [8 for i in range(512)]
                self.portChoice = data[10:14]   #选择的端口
            pdata = data[10: 74]
            for i in range(0, len(pdata), 4):
                if(pdata[i:i + 4] == self.portChoice):
                    self.level.append(0.5)
                else:
                    self.level.append(0)

        if(data[1:5] == ':208' or data[1:5] == ':209' or data[0:7] == ':208000'):
            #电流
            pdata = data[10: 74]
            if (data[0:7] == ':208000'):
                #初始化tab4电流数据
                self.child.widget.tab4.i = []
                pdata = data[9: 73]
            for i in range(0, len(pdata), 4):
                self.child.widget.tab4.i.append(int(pdata[i:i + 4], 16) / 100)

        if(data[1:5] == ':204' or data[1:5] == ':205' or data[0:7] == ':204000'):
            #电压
            pdata = data[10: 74]
            if (data[0:7] == ':204000'):
                #初始化tab4电压数据
                self.child.widget.tab4.v = []
                pdata = data[9: 73]
            for i in range(0, len(pdata), 4):
                self.child.widget.tab4.v.append(int(pdata[i:i + 4], 16) / 100)
            print(self.child.widget.tab4.v)
        if(data[1:12] == ':00000001FF'):
            if self.portChoice != '':
                if self.portChoice == 'FFFE':
                    self.child.widget.tab3.val = list(
                        map(lambda x: x[0] - x[1], zip(self.child.widget.tab3.val, self.level)))
                    self.child.widget.tab4.val = self.child.widget.tab3.val
                elif self.portChoice == 'FFFD':
                    self.child.widget.tab3.val1 = list(
                        map(lambda x: x[0] - x[1], zip(self.child.widget.tab3.val1, self.level)))
                    self.child.widget.tab4.val1 = self.child.widget.tab3.val1
                elif self.portChoice == 'FFFB':
                    self.child.widget.tab3.val2 = list(
                        map(lambda x: x[0] - x[1], zip(self.child.widget.tab3.val2, self.level)))
                elif self.portChoice == 'FFF7':
                    self.child.widget.tab3.val3 = list(
                        map(lambda x: x[0] - x[1], zip(self.child.widget.tab3.val3, self.level)))
                elif self.portChoice == 'FFEF':
                    self.child.widget.tab3.val4 = list(
                        map(lambda x: x[0] - x[1], zip(self.child.widget.tab3.val4, self.level)))
                elif self.portChoice == 'FFDF':
                    self.child.widget.tab3.val5 = list(
                        map(lambda x: x[0] - x[1], zip(self.child.widget.tab3.val5, self.level)))
                elif self.portChoice == 'FFBF':
                    self.child.widget.tab3.val6 = list(
                        map(lambda x: x[0] - x[1], zip(self.child.widget.tab3.val6, self.level)))
                elif self.portChoice == 'FF7F':
                    self.child.widget.tab3.val7 = list(
                        map(lambda x: x[0] - x[1], zip(self.child.widget.tab3.val7, self.level)))
                self.portChoice = ''
            self.ChangePicData()
            self.level = []

    def SendUARTAline(self):
        if(self.uartIsOpen == 1):
            sendData = self.child.sendEdit.text()
            if(sendData != ''):
                try:
                    self.ser.SendAline(sendData.encode('utf-8'))
                    self.child.recvEdit.append('<' + sendData)
                    self.VerifyData(sendData)
                except:
                    self.status.showMessage('发送失败', 0)
                else:
                    self.status.showMessage('发送成功', 0)

    def OpenUart(self):
        try:
            self.ser = serManager(self.port, int(self.baud))
            print(self.ser)
            self.ser.Open()
        except Exception as e:
            self.status.showMessage('串口打开失败',0)
            print(e)
        else:
            self.status.showMessage('串口打开成功', 0)
            self.uartIsOpen = 1
            self.imgLight.setPixmap(QPixmap(':/img/LightOn.png'))

    def CloseUart(self):
        try:
            self.ser.Close()
            self.imgLight.setPixmap(QPixmap('LightOff.png'))
        except:
            self.status.showMessage('串口关闭失败', 0)
        else:
            self.status.showMessage('串口关闭成功', 0)
            self.uartIsOpen = 0

    def closeEvent(self, QCloseEvent):
        try:
            self.CloseUart()
            print('串口已关闭')
        except:
            pass
        finally:
            QCloseEvent.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    Win = windows()
    Win.show()
    sys.exit(app.exec_())