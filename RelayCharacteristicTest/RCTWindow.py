import random

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QSizePolicy, QComboBox, QTabWidget, QTextEdit, QWidget, QLabel, QAction, QDialog, QLineEdit, \
    QFormLayout, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen
import serial.tools.list_ports
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import img


class MainWindow(object):
    def setupUi(self):
        self.setWindowTitle('西南交通大学继电器测试实验')
        self.resize(900, 900)
        self.setFixedSize(900, 900)  # 不想固定窗体可以删掉
        self.setWindowIcon(QIcon(':/img/icon.png'))

        self.Status()
        self.Menu()

        # 变量
        self.port = None
        self.baud = None

    # 状态栏
    def Status(self):
        self.status = self.statusBar()  # 开启状态栏（用于显示串口信息）
        self.status.showMessage("串口信息：", 0)
        self.comNum = QLabel('串口号:')
        self.baudNum = QLabel('波特率:')
        self.imgLight = QLabel()
        self.imgLight.setPixmap(QPixmap(':/img/LightOff.png'))

        self.status.addPermanentWidget(self.comNum, stretch=0)
        self.status.addPermanentWidget(self.baudNum, stretch=0)
        self.status.addPermanentWidget(self.imgLight, stretch=0)

    # 菜单栏
    def Menu(self):
        # layout = QHBoxLayout()
        bar = self.menuBar()

        # 开始
        Start = bar.addMenu("开始")

        setUart = QAction("设置串口", self)
        setUart.setShortcut("Ctrl+A")
        Start.addAction(setUart)

        self.startUart = QAction("打开串口", self)
        self.startUart.setShortcut("Ctrl+O")
        Start.addAction(self.startUart)

        self.closeUart = QAction("关闭串口", self)
        self.closeUart.setShortcut("Ctrl+P")
        Start.addAction(self.closeUart)

        quit = QAction("退出", self)
        quit.setShortcut("Ctrl+Q")
        Start.addAction(quit)
        # 开始菜单中的触发器
        quit.triggered.connect(self.close)
        setUart.triggered.connect(self.DlogSetUart)

    # 设置串口的弹窗
    def DlogSetUart(self):
        self.setUartDlog = QDialog()
        self.setUartDlog.setWindowTitle('设置串口')
        self.setUartDlog.resize(180, 100)

        # 设置表单布局的内容（串口号波特率输入）
        label1 = QLabel('串口号:')
        self.enterPort = QComboBox()
        self.enterPort.addItems(self.DetectUart())
        label2 = QLabel('波特率:')
        self.enterBaud = QComboBox()
        self.enterBaud.addItems(
            ['600', '1200', '2400', '4800', '9600', '14400', '19200', '28800', '38400', '57600', '115200', '230400',
             '460800'])
        self.enterBaud.setCurrentIndex(10)
        formLayout = QFormLayout()
        formLayout.addRow(label1, self.enterPort)
        formLayout.addRow(label2, self.enterBaud)

        # 设置水平布局内容（两个按键）
        self.btnOk = QPushButton('确定')
        self.btnCancel = QPushButton('取消')
        hBox = QHBoxLayout()
        hBox.addStretch(1)  # 设置水平伸缩量
        hBox.addWidget(self.btnOk)
        hBox.addStretch(1)
        hBox.addWidget(self.btnCancel)
        hBox.addStretch(1)

        # 设置放布局的控件
        hwg = QWidget()
        fwg = QWidget()
        hwg.setLayout(hBox)
        fwg.setLayout(formLayout)

        # 设置整体的垂直布局
        vLayout = QVBoxLayout()
        vLayout.addWidget(fwg)
        vLayout.addWidget(hwg)

        # 这个弹窗里的信号连接
        self.btnOk.clicked.connect(self.setPortBaud)
        self.btnCancel.clicked.connect(self.setUartDlog.close)

        self.setUartDlog.setLayout(vLayout)
        self.setUartDlog.setWindowModality(Qt.ApplicationModal)  # 独占模式
        self.setUartDlog.exec_()

    # 设置端口和波特率的变量
    def setPortBaud(self):
        self.port = self.enterPort.currentText()
        self.baud = self.enterBaud.currentText()
        self.setPortBaudShow()
        self.setUartDlog.close()

    # 设置状态栏里的端口和波特率
    def setPortBaudShow(self):
        strPort = '串口号:' + self.port
        strBaud = '波特率:' + self.baud
        self.comNum.setText(strPort)
        self.baudNum.setText(strBaud)

    # 检测串口
    def DetectUart(self):
        self.enterPort.clear()
        plist = list(serial.tools.list_ports.comports())
        if len(plist) <= 0:
            return ["无可用串口"]
        else:
            portList = []
            for port in plist:
                portList.append(list(port)[0])
            return portList


class ChildWindow(QWidget):
    def __init__(self):
        super(ChildWindow, self).__init__()

        # 全局网格布局
        self.allLayout = QGridLayout()
        # head（图片显示、函数图形等）

        self.widget = Head()

        # 接收框
        self.recvEdit = QTextEdit(self)
        self.recvEdit.setReadOnly(True)  # 接收框设为只读
        # 发送框
        self.sendEdit = QLineEdit(self)  # 发送框
        # 发送按钮
        self.sendBtn = QPushButton(self)
        self.sendBtn.setText('发送')

        # 设置整体的网格布局
        self.allLayout.addWidget(self.widget, 1, 0, 3, 3)
        self.allLayout.addWidget(self.recvEdit, 4, 0, 2, 3)
        self.allLayout.addWidget(self.sendEdit, 6, 0)
        self.allLayout.addWidget(self.sendBtn, 6, 1)


# ChildWindow中的head（标签变化框）
class Head(QTabWidget):
    def __init__(self):
        super(Head, self).__init__()
        # 四个标签
        # 开机检测

        self.tab1 = MyLabel()
        self.tab1.setPixmap(QPixmap(':/img/StartDetect.jpg'))
        self.tab1.setScaledContents(True)

        self.tab2 = QLabel('压流测试数据显示请查看实验板')
        self.tab2.setAlignment(Qt.AlignCenter)
        self.tab2.setFont(QFont("Roman times", 30, QFont.Bold))

        self.tab3 = MyDynamicMplCanvas()  # 触点测试

        self.tab4 = MyDynamicMplCanvas1()  # 过渡过程

        self.addTab(self.tab1, '开机检测')
        self.addTab(self.tab2, '继电器电流电压测试')
        self.addTab(self.tab3, '继电器触点检测')
        self.addTab(self.tab4, '继电器吸起落下过渡过程')


class MyMplCanvas(FigureCanvas):
    """这是一个窗口部件，即QWidget（当然也是FigureCanvasAgg）"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.grid('off')
        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class MyDynamicMplCanvas(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.axes.set_xticklabels(['', '', '', '', ''])
        self.axes.set_yticks(np.linspace(0, 8, 9))
        self.axes.set_yticklabels(['', 'PC0', 'PC1', 'PC2', 'PC3', 'PC4', 'PC5', 'PC6', 'PC7'])
        self.l = [i for i in range(512)]
        self.val = [1 for i in range(512)]
        self.val1 = [2 for i in range(512)]
        self.val2 = [3 for i in range(512)]
        self.val3 = [4 for i in range(512)]
        self.val4 = [5 for i in range(512)]
        self.val5 = [6 for i in range(512)]
        self.val6 = [7 for i in range(512)]
        self.val7 = [8 for i in range(512)]

    def compute_initial_figure(self):
        pass

    def update_figure(self):
        # 构建4个随机整数，位于闭区间[0, 10]
        self.axes.clear()
        self.axes.set_xticklabels(['', '', '', '', ''])
        self.axes.set_yticks(np.linspace(0, 8, 9))
        self.axes.set_yticklabels(['', 'PC0', 'PC1', 'PC2', 'PC3', 'PC4', 'PC5', 'PC6', 'PC7'])

        self.l = [i for i in range(512)]

        self.axes.plot(self.l, self.val, 'r')
        self.axes.plot(self.l, self.val1, 'blue')
        self.axes.plot(self.l, self.val2, 'green')
        self.axes.plot(self.l, self.val3, 'black')
        self.axes.plot(self.l, self.val4, 'r')
        self.axes.plot(self.l, self.val5, 'blue')
        self.axes.plot(self.l, self.val6, 'green')
        self.axes.plot(self.l, self.val7, 'black')
        self.draw()

class MyMplCanvas1(FigureCanvas):
    """这是一个窗口部件，即QWidget（当然也是FigureCanvasAgg）"""

    def __init__(self, parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(211)
        self.axes.grid('off')
        self.axes1 = fig.add_subplot(212)
        self.axes1.grid('off')
        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class MyDynamicMplCanvas1(MyMplCanvas1):
    def __init__(self, *args, **kwargs):
        MyMplCanvas1.__init__(self, *args, **kwargs)
        self.axes.set_xticklabels(['', '', '', '', ''])
        self.axes1.set_xticklabels(['', '', '', '', ''])
        self.axes1.set_yticks([0, 1, 2])
        self.axes1.set_yticklabels(['', 'PC0', 'PC1'])
        self.l = [i for i in range(512)]
        self.val = [1 for i in range(512)]
        self.val1 = [2 for i in range(512)]
        self.vil = [i for i in range(4096)]
        self.i = [0 for i in range(4096)]
        self.v = [0 for i in range(4096)]

    def update_figure(self):
        self.axes1.clear()
        self.axes.clear()
        self.axes1.set_xticklabels(['', '', '', '', ''])
        self.axes.set_xticklabels(['', '', '', '', ''])
        self.axes1.set_yticks([0, 1, 2])
        self.axes1.set_yticklabels(['', 'PC0', 'PC1'])

        self.l = [i for i in range(512)]

        self.axes1.plot(self.l, self.val, 'r')
        self.axes1.plot(self.l, self.val1, 'blue')
        self.axes.plot(self.vil, self.i, color = 'r', label = 'Current')
        self.axes.plot(self.vil, self.v, color = 'blue', label = 'Voltage')
        self.axes.legend(loc='upper right', shadow=False, fontsize='x-large', bbox_to_anchor=(1.1, 1.3))
        self.draw()

# 开机测试界面
class MyLabel(QLabel):
    iPosX = 325
    iPosY = 395
    uPosX = 370
    uPosY = 490
    iText = 'I=A'
    uText = 'U=V'
    port = ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1']
    positionList = [(67, 71), (108, 112), (189, 193), (230, 234), (311, 315), (351, 355), (440, 444), (481, 485)]

    def paintEvent(self, Event):
        super().paintEvent(Event)
        painter = QPainter(self)
        self.drawText(Event, painter)
        self.drawLine(Event, painter)

    # 图片上的字
    def drawText(self, event, qp):
        qp.setPen(QColor(168, 34, 3))
        qp.setFont(QFont('Roman times', 20))
        qp.drawText(self.iPosX, self.iPosY, self.iText)
        qp.setPen(QColor(168, 34, 3))
        qp.setFont(QFont('Roman times', 20))
        qp.drawText(self.uPosX, self.uPosY, self.uText)

    # 图片上的线
    def drawLine(self, event, qp):
        linePen = QPen()
        linePen.setWidth(4)
        linePen.setColor(Qt.red)
        qp.setPen(linePen)
        count = 0
        for each in self.port:
            if count <= 7:
                if each == '0':
                    qp.drawLine(50, self.positionList[count][0], 50, self.positionList[count][1])
            else:
                if each == '0':
                    qp.drawLine(100, self.positionList[count - 8][0], 100, self.positionList[count - 8][1])
            count += 1
