from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QSizePolicy,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QHeaderView
import paho.mqtt.client as mqtt
import json

table = None
label = None


class MQTTHandler(QObject):
    new_message = pyqtSignal(str, str, str, str)

    def __init__(self):
        super().__init__()
        self.client = mqtt.Client()
        self.client.username_pw_set("eason", "qazwsx")
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883)
        self.client.subscribe("request/iot/+/+")
        self.client.subscribe("response/iot/+/+")
        self.client.loop_start()

    def on_message(self, client, userdata, message):
        topic = message.topic
        payload = message.payload.decode()

        data = json.loads(payload)

        # 訪問數據
        mac_address = data["mac_address"]
        correlation_id = data["correlation_id"]
        payload_data = payload
        # payload=message
        # action_flg="N"

        # 分割 payload
        # mac_address, correlation_id, payload_data = payload.split("|")

        # 使用信号传递数据到主线程
        self.new_message.emit(topic, mac_address, correlation_id, payload_data)


def on_new_message(topic, mac_address, correlation_id, payload_data):
    # 检查表格行数是否超过 1000，如果是，删除第一行
    if table.rowCount() >= 1000:
        table.removeRow(0)

    # 添加新行
    row_position = table.rowCount()
    table.insertRow(row_position)
    table.setItem(row_position, 0, QTableWidgetItem(topic))
    table.setItem(row_position, 1, QTableWidgetItem(mac_address))
    table.setItem(row_position, 2, QTableWidgetItem(correlation_id))
    table.setItem(row_position, 3, QTableWidgetItem(payload_data))

    # 设置当前焦点到新插入的行
    table.setCurrentCell(row_position, 0)

    # 删除重复的 Correlation ID 行
    remove_duplicate_correlation_ids()


def remove_duplicate_correlation_ids():
    seen = {}  # 用来存储已经看到的 Correlation ID 及其行索引
    rows_to_remove = []  # 存储要删除的行索引

    # 遍历表格的每一行
    for row in range(table.rowCount()):
        correlation_id = table.item(row, 2).text()  # 获取第3列（Correlation ID）的值
        if correlation_id in seen:
            # 如果已经存在，则标记该行需要删除
            rows_to_remove.append(row)
            rows_to_remove.append(seen[correlation_id])  # 也标记之前的行
        else:
            seen[correlation_id] = row  # 记录该行的索引

    # 使用集合去重，避免重复标记同一行
    rows_to_remove = set(rows_to_remove)

    # 倒序删除避免索引问题
    for row in sorted(rows_to_remove, reverse=True):
        table.removeRow(row)


def on_item_double_clicked(row, column):
    """删除双击的行"""
    table.removeRow(row)


def main():
    global table
    app = QApplication([])

    window = QWidget()
    window.setWindowTitle("CIM Mqtt Message Monitor")
    window.resize(1024, 768)
    layout = QVBoxLayout()

    label = QLabel("CIM IOT Mqtt Message Monitor")
    label.setAlignment(Qt.AlignCenter)  # 设置文本居中
    label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # 水平扩展标签

    # 设置字体大小、颜色和粗体
    font = QFont()
    font.setPointSize(25)
    font.setBold(True)  # 设置粗体
    label.setFont(font)
    label.setStyleSheet("color: blue;")  # 设置颜色为蓝色

    layout.addWidget(label)

    # 创建 QTableWidget
    table = QTableWidget()
    table.setRowCount(0)  # 初始化为 0 行
    table.setColumnCount(4)  # 设置列数
    table.setHorizontalHeaderLabels(
        ["Topic", "Mac Address", "Correlation ID", "Payload"]
    )  # 设置列标题
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)
    table.setShowGrid(True)
    layout.addWidget(table)

    # 连接双击事件
    table.itemDoubleClicked.connect(
        lambda item: on_item_double_clicked(item.row(), item.column())
    )

    window.setLayout(layout)
    window.show()

    # 创建 MQTT 处理程序
    mqtt_handler = MQTTHandler()

    # 将信号连接到 on_new_message 函数
    mqtt_handler.new_message.connect(on_new_message)

    app.exec_()


if __name__ == "__main__":
    main()
