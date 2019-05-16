import serial
import binascii

class serManager():
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud

    def Open(self):
        self.ser = serial.Serial(timeout=0.5)
        self.ser.baudrate = self.baud
        self.ser.port = self.port
        self.ser.open()
        print(self.ser.is_open)

    def Close(self):
        self.ser.close()

    def RecvALine(self):
        if(self.ser.in_waiting != 0):
            print(self.ser.in_waiting)
            data = self.ser.readline()
            print(data)
            data = data.decode('gb2312')   #iso-8859-1
            print(data)
            return str(data)
        else:
            return None

    def SendAline(self, data):
        self.ser.write(data)

