from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView

def on_click():
    label.setText("Button clicked!")

app = QApplication([])

# 创建主窗口
window = QWidget()
window.setWindowTitle("CIM Mqtt Message Monitor")

# 设置窗口大小为 1024 x 768
window.resize(1024, 768)

# 创建垂直布局
layout = QVBoxLayout()

# 添加标签
label = QLabel('Hello, PyQt5!')
label.setAlignment(Qt.AlignCenter)  # 设置文本居中
label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # 水平扩展标签

# 设置字体大小
font = QFont()
font.setPointSize(15)
label.setFont(font)

layout.addWidget(label)

# 添加按钮
button = QPushButton('Click me')
button.clicked.connect(on_click)
layout.addWidget(button)

# 创建一个 QTableWidget（类似 DataGrid）
table = QTableWidget()
table.setRowCount(3)  # 设置行数
table.setColumnCount(4)  # 设置列数，增加一列
table.setHorizontalHeaderLabels(["Topic", "Mac Address", "Correlation ID", "Payload"])  # 设置列标题

# 填充表格数据
table.setItem(0, 0, QTableWidgetItem("Topic1"))
table.setItem(0, 1, QTableWidgetItem("AA:BB:CC:DD:EE:01"))
table.setItem(0, 2, QTableWidgetItem("12345"))
table.setItem(0, 3, QTableWidgetItem("Payload 1"))

table.setItem(1, 0, QTableWidgetItem("Topic2"))
table.setItem(1, 1, QTableWidgetItem("AA:BB:CC:DD:EE:02"))
table.setItem(1, 2, QTableWidgetItem("67890"))
table.setItem(1, 3, QTableWidgetItem("Payload 2"))

table.setItem(2, 0, QTableWidgetItem("Topic3"))
table.setItem(2, 1, QTableWidgetItem("AA:BB:CC:DD:EE:03"))
table.setItem(2, 2, QTableWidgetItem("13579"))
table.setItem(2, 3, QTableWidgetItem("Payload 3"))

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

app.exec_()
