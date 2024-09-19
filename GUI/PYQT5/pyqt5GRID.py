from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem

def on_click():
    label.setText("Button clicked!")

app = QApplication([])

# 创建主窗口
window = QWidget()
window.setWindowTitle("CIM IOT Mqtt monitor")

# 设置窗口大小为 1024 x 768
window.resize(1024, 768)

# 创建垂直布局
layout = QVBoxLayout()

# 添加标签
label = QLabel('Hello, PyQt5!')
layout.addWidget(label)

# 添加按钮
button = QPushButton('Click me')
button.clicked.connect(on_click)
layout.addWidget(button)

# 创建一个 QTableWidget（类似 DataGrid）
table = QTableWidget()
table.setRowCount(3)  # 设置行数
table.setColumnCount(3)  # 设置列数
table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])  # 设置列标题

# 填充表格数据
table.setItem(0, 0, QTableWidgetItem("Row 1, Col 1"))
table.setItem(0, 1, QTableWidgetItem("Row 1, Col 2"))
table.setItem(0, 2, QTableWidgetItem("Row 1, Col 3"))

table.setItem(1, 0, QTableWidgetItem("Row 2, Col 1"))
table.setItem(1, 1, QTableWidgetItem("Row 2, Col 2"))
table.setItem(1, 2, QTableWidgetItem("Row 2, Col 3"))

table.setItem(2, 0, QTableWidgetItem("Row 3, Col 1"))
table.setItem(2, 1, QTableWidgetItem("Row 3, Col 2"))
table.setItem(2, 2, QTableWidgetItem("Row 3, Col 3"))

# 将 QTableWidget 添加到布局中
layout.addWidget(table)

# 设置布局并显示窗口
window.setLayout(layout)
window.show()

app.exec_()
