from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView
import paho.mqtt.client as mqtt

def on_click():
    label.setText("Button clicked!")

def on_message(client, userdata, message):
    # 解析消息
    topic = message.topic
    payload = message.payload.decode()

    # 分割 payload
    mac_address, correlation_id, payload_data = payload.split('|')

    # 更新表格
    row_position = table.rowCount()
    table.insertRow(row_position)
    table.setItem(row_position, 0, QTableWidgetItem(topic))
    table.setItem(row_position, 1, QTableWidgetItem(mac_address))
    table.setItem(row_position, 2, QTableWidgetItem(correlation_id))
    table.setItem(row_position, 3, QTableWidgetItem(payload_data))

    # 设置当前焦点到新插入的行
    table.setCurrentCell(row_position, 0)

# 创建主窗口
app = QApplication([])

window = QWidget()
window.setWindowTitle("CIM Mqtt Message Monitor")

# 设置窗口大小为 1024 x 768
window.resize(1024, 768)

# 创建垂直布局
layout = QVBoxLayout()

# 添加标签
label = QLabel('CIM IOT Mqtt Message Monitor')
label.setAlignment(Qt.AlignCenter)  # 设置文本居中
label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # 水平扩展标签

# 设置字体大小
font = QFont()
font.setPointSize(15)
label.setFont(font)

layout.addWidget(label)

# # 添加按钮
# button = QPushButton('Click me')
# button.clicked.connect(on_click)
# layout.addWidget(button)

# 创建一个 QTableWidget（类似 DataGrid）
table = QTableWidget()
table.setRowCount(0)  # 初始化为 0 行
table.setColumnCount(4)  # 设置列数
table.setHorizontalHeaderLabels(["Topic", "Mac Address", "Correlation ID", "Payload"])  # 设置列标题

# 设置列宽自动均分整个窗口宽度
header = table.horizontalHeader()
header.setSectionResizeMode(QHeaderView.Stretch)

# 启用表格网格线
table.setShowGrid(True)

# 将 QTableWidget 添加到布局中
layout.addWidget(table)

# 设置布局并显示窗口
window.setLayout(layout)
window.show()

# 设置 MQTT 客户端
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set("eason", "qazwsx")
mqtt_client.on_message = on_message

mqtt_client.connect("localhost", 1883)
mqtt_client.subscribe("request/+/+")
mqtt_client.loop_start()

app.exec_()
