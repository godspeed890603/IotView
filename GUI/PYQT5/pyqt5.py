from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

def on_click():
    label.setText("Button clicked!")

app = QApplication([])

window = QWidget()
window.setWindowTitle("Simple PyQt5 App")

layout = QVBoxLayout()

label = QLabel('Hello, PyQt5!')
layout.addWidget(label)

button = QPushButton('Click me')
button.clicked.connect(on_click)
layout.addWidget(button)

window.setLayout(layout)
window.show()

app.exec_()
