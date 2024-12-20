from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QHeaderView
import paho.mqtt.client as mqtt

table = None
label = None

class MQTTHandler(QObject):
    # 定义一个信号，用于在主线程中更新表格
    new_message = pyqtSignal(str, str, str, str)

    def __init__(self):
        super().__init__()

        # 初始化 MQTT 客户端
        self.client = mqtt.Client()
        self.client.username_pw_set("eason", "qazwsx")
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883)
        self.client.subscribe("request/+/+")
        self.client.subscribe("response/+/+")
        self.client.loop_start()

    def on_message(self, client, userdata, message):
        # 解析消息
        topic = message.topic
        payload = message.payload.decode()

        # 分割 payload
        mac_address, correlation_id, payload_data = payload.split('|')

        # 使用信号传递数据到主线程
        self.new_message.emit(topic, mac_address, correlation_id, payload_data)

def on_new_message(topic, mac_address, correlation_id, payload_data):
    # 检查表格行数是否超过 1000，如果是，删除第一行
    if table.rowCount() >= 1000:
        table.removeRow(0)

    # 更新表格
    row_position = table.rowCount()
    table.insertRow(row_position)
    table.setItem(row_position, 0, QTableWidgetItem(topic))
    table.setItem(row_position, 1, QTableWidgetItem(mac_address))
    table.setItem(row_position, 2, QTableWidgetItem(correlation_id))
    table.setItem(row_position, 3, QTableWidgetItem(payload_data))

    # 设置当前焦点到新插入的行
    table.setCurrentCell(row_position, 0)

def main():
    global table
    app = QApplication([])

    window = QWidget()
    window.setWindowTitle("CIM Mqtt Message Monitor")
    window.resize(1024, 768)
    layout = QVBoxLayout()

    label = QLabel('CIM IOT Mqtt Message Monitor')
    label.setAlignment(Qt.AlignCenter)
    label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    font = QFont()
    font.setPointSize(15)
    font.setBold(True)  # 设置粗体
    label.setFont(font)
    # 设置字体颜色为蓝色
    label.setStyleSheet("color: blue;")
    layout.addWidget(label)

    table = QTableWidget()
    table.setRowCount(0)
    table.setColumnCount(4)
    table.setHorizontalHeaderLabels(["Topic", "Mac Address", "Correlation ID", "Payload"])
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)
    table.setShowGrid(True)
    layout.addWidget(table)

    window.setLayout(layout)
    window.show()

    # 创建 MQTT 处理程序
    mqtt_handler = MQTTHandler()

    # 将信号连接到 on_new_message 函数
    mqtt_handler.new_message.connect(on_new_message)

    app.exec_()

if __name__ == "__main__":
    main()
