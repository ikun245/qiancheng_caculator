"""
Created on: 2025-01-23 11:45:35 UTC
Author: ikun245
Description: 赔率计算器 - 支持快捷键和手动计算
Version: 2.0.3
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QLabel, QFrame, QSlider, QGridLayout)
from PyQt5.QtCore import Qt, QPoint, QLocale,QTimer,QPropertyAnimation, QRect
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator, QIcon  # 添加 QIcon
import pyperclip


def resource_path(relative_path):
    """ 获取资源的绝对路径 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
class FloatingCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        # 基础窗口设置
        self.setWindowTitle("千城赔率计算器")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setFixedSize(350, 450)

        # 设置应用程序的默认字体
        self.default_font = QFont("Microsoft YaHei", 10, QFont.Bold)
        QApplication.setFont(self.default_font)

        # 创建主窗口部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(10)

        # 初始化变量
        self.current_entry = None
        self.drag_pos = None
        self.numpad_visible = False
        self.numpad_widget = None
        self.toggle_button = None

        # 初始化输入框变量
        self.prob1_entry = None
        self.prob2_entry = None
        self.people1_entry = None
        self.people2_entry = None
        self.transparency_label = None
        self.transparency_slider = None

        # 初始化UI
        self.setup_ui()
        self.current_entry = None  # 确保正确初始化
    def calculate(self):
        """执行计算功能"""
        try:
            def get_valid_number(text, is_float=True):
                text = text.strip()
                if not text or text == '.' or text == '0.':
                    return None
                try:
                    return float(text) if is_float else int(text)
                except ValueError:
                    return None

            prob1 = get_valid_number(self.prob1_entry.text(), True)
            prob2 = get_valid_number(self.prob2_entry.text(), True)
            people1 = get_valid_number(self.people1_entry.text(), False)
            people2 = get_valid_number(self.people2_entry.text(), False)

            # 只要有三个值，就计算第四个值
            if prob1 and people1 and prob2 and not people2:
                # 计算金额2
                result = int((prob1 * people1) / prob2)
                self.people2_entry.setText(str(result))
            elif prob1 and people1 and people2 and not prob2:
                # 计算赔率2
                result = (prob1 * people1) / people2
                self.prob2_entry.setText(f"{result:.2f}")
            elif prob1 and prob2 and people2 and not people1:
                # 计算金额1
                result = int((prob2 * people2) / prob1)
                self.people1_entry.setText(str(result))
            elif prob2 and people1 and people2 and not prob1:
                # 计算赔率1
                result = (prob2 * people2) / people1
                self.prob1_entry.setText(f"{result:.2f}")

        except Exception as e:
            print(f"计算错误: {str(e)}")

    def setup_ui(self):
        """设置UI组件"""




        self.create_title_bar()
        self.create_ad_space()
        self.create_input_area()
        self.create_action_buttons()

        self.create_numpad()
        self.create_transparency_slider()
        spacer = QWidget()
        spacer.setFixedHeight(5)
        self.main_layout.addWidget(spacer)


    def do_clear_all(self):
        """清空所有输入框并重置焦点"""
        try:
            self.prob1_entry.setText("")
            self.prob2_entry.setText("")
            self.people1_entry.setText("")
            self.people2_entry.setText("")
            self.current_entry = self.prob1_entry
            self.prob1_entry.setFocus()
        except Exception as e:
            print(f"清除错误: {str(e)}")

    def create_title_bar(self):
        title_container = QWidget()
        title_container.setFixedHeight(30)
        title_layout = QHBoxLayout(title_container)
        title_layout.setSpacing(0)
        title_layout.setContentsMargins(5, 0, 0, 0)

        title_label = QLabel("千城赔率计算器V2.1.3")
        title_label.setStyleSheet("""
            font-family: "Microsoft YaHei";
            font-size: 16px;
            font-weight: bold;
        """)

        min_btn = QPushButton("─")
        close_btn = QPushButton("×")

        min_btn.setFixedSize(45, 30)
        close_btn.setFixedSize(45, 30)

        button_style = """
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                color: #333333;
                font-family: "Microsoft YaHei";
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """
        close_style = """
            QPushButton:hover {
                background-color: #e81123;
                color: white;
            }
        """

        min_btn.setStyleSheet(button_style)
        close_btn.setStyleSheet(button_style + close_style)

        min_btn.setFocusPolicy(Qt.NoFocus)
        close_btn.setFocusPolicy(Qt.NoFocus)

        min_btn.clicked.connect(self.showMinimized)
        close_btn.clicked.connect(self.close)

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(min_btn)
        title_layout.addWidget(close_btn)

        title_container.mousePressEvent = self.titlebar_mouse_press
        title_container.mouseMoveEvent = self.titlebar_mouse_move
        title_container.mouseReleaseEvent = self.titlebar_mouse_release

        self.main_layout.addWidget(title_container)

    def titlebar_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def titlebar_mouse_move(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def titlebar_mouse_release(self, event):
        self.drag_pos = None

    def create_ad_space(self):
        """创建带滚动效果的广告区域"""
        ad_container = QWidget()
        ad_layout = QVBoxLayout(ad_container)
        ad_layout.setContentsMargins(0, 0, 0, 0)

        # 创建广告标签
        self.ad_label = QLabel()
        self.ad_label.setStyleSheet("""
            QLabel {
                font-family: "Microsoft YaHei";
                font-size: 14px;
                font-weight: bold;
                background-color: #f8f8f8;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        # 设置初始文本
        self.ad_label.setText('足球胜率80%TG:qiancheng8778   三同ipTG:hxm13113039   ')

        # 创建动画
        self.scroll_animation = QTimer()
        self.scroll_animation.timeout.connect(self.scroll_text)
        self.scroll_animation.start(300)  # 每50毫秒更新一次

        ad_layout.addWidget(self.ad_label)
        self.main_layout.addWidget(ad_container)

    def scroll_text(self):
        """文本滚动效果"""
        text = self.ad_label.text()
        text = text[1:] + text[0]  # 将第一个字符移到末尾
        self.ad_label.setText(text)

    def create_input_area(self):
        """创建输入区域"""
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)  # 使用水平布局
        input_layout.setContentsMargins(0, 0, 0, 15)
        input_layout.setSpacing(15)

        # 创建左侧赔率区域
        prob_widget = QWidget()
        prob_layout = QVBoxLayout(prob_widget)  # 垂直布局
        prob_layout.setContentsMargins(0, 0, 0, 0)
        prob_layout.setSpacing(10)

        # 赔率标签和输入框
        prob_label = QLabel("赔率")
        prob_label.setAlignment(Qt.AlignCenter)  # 设置标签文字居中
        prob_label.setMinimumWidth(160)  # 确保标签宽度与输入框一致

        self.prob1_entry = QLineEdit()
        self.prob1_entry.setPlaceholderText("A台")
        self._setup_entry(self.prob1_entry)

        self.prob2_entry = QLineEdit()
        self.prob2_entry.setPlaceholderText("B台")
        self._setup_entry(self.prob2_entry)

        prob_layout.addWidget(prob_label)
        prob_layout.addWidget(self.prob1_entry)
        prob_layout.addWidget(self.prob2_entry)

        # 创建右侧下注金额区域
        people_widget = QWidget()
        people_layout = QVBoxLayout(people_widget)  # 垂直布局
        people_layout.setContentsMargins(0, 0, 0, 0)
        people_layout.setSpacing(10)

        # 下注金额标签和输入框
        people_label = QLabel("下注金额")
        people_label.setAlignment(Qt.AlignCenter)  # 设置标签文字居中
        people_label.setMinimumWidth(160)  # 确保标签宽度与输入框一致

        self.people1_entry = QLineEdit()
        self.people1_entry.setPlaceholderText("A台")
        self._setup_entry(self.people1_entry)

        self.people2_entry = QLineEdit()
        self.people2_entry.setPlaceholderText("B台")
        self._setup_entry(self.people2_entry)

        people_layout.addWidget(people_label)
        people_layout.addWidget(self.people1_entry)
        people_layout.addWidget(self.people2_entry)

        # 添加到主布局
        input_layout.addWidget(prob_widget)
        input_layout.addWidget(people_widget)

        # 简单设置 Tab 顺序
        QWidget.setTabOrder(self.prob1_entry, self.people1_entry)
        QWidget.setTabOrder(self.people1_entry, self.prob2_entry)
        QWidget.setTabOrder(self.prob2_entry, self.people2_entry)

        self.main_layout.addWidget(input_widget)

    def _setup_entry(self, entry):
        """设置输入框的样式和属性"""
        # 设置样式
        entry.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #dcdcdc;
                border-radius: 8px;
                background-color: white;
                selection-background-color: #0078d4;
                selection-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)

        # 设置大小和边距
        entry.setFixedHeight(40)
        entry.setMinimumWidth(160)  # 调整宽度以适应两列布局
        entry.setTextMargins(8, 0, 8, 0)

        # 设置交互属性
        entry.setCursor(Qt.IBeamCursor)
        entry.setMouseTracking(True)
        entry.setFocusPolicy(Qt.StrongFocus)

        # 添加右键菜单
        entry.setContextMenuPolicy(Qt.CustomContextMenu)
        entry.customContextMenuRequested.connect(
            lambda pos, e=entry: self.show_context_menu(pos, e)
        )

        # 添加焦点事件处理
        entry.focusInEvent = lambda event, e=entry: self.handle_focus_in(event, e)
        # 添加点击事件处理
        entry.mousePressEvent = lambda event, e=entry: self.handle_entry_click(event, e)

    def handle_entry_click(self, event, entry):
        """处理输入框点击事件"""
        self.current_entry = entry
        entry.setFocus()
        content = entry.text().strip()
        if content:
            pyperclip.copy(content)
            tip = QLabel("已复制到剪贴板", self)
            tip.setStyleSheet("""
                        QLabel {
                            background-color: rgba(0, 0, 0, 0.7);
                            color: white;
                            padding: 8px 12px;
                            border-radius: 4px;
                            font-size: 12px;
                        }
                    """)
            tip.adjustSize()

            # 计算提示框位置（居中显示）
            pos = self.mapToGlobal(self.rect().center())
            tip.move(pos.x() - tip.width() // 2, pos.y() - tip.height() // 2)

            tip.show()

            # 创建定时器，1秒后隐藏提示
            QTimer.singleShot(1000, tip.deleteLater)
        QLineEdit.mousePressEvent(entry, event)  # 调用原始的鼠标点击事件处理

    def handle_focus_in(self, event, entry):
        """处理输入框获得焦点的事件"""
        self.current_entry = entry  # 更新当前输入框
        QLineEdit.focusInEvent(entry, event)  # 调用原始的焦点事件处理
    def show_context_menu(self, pos, entry):
        """显示右键菜单"""
        menu = entry.createStandardContextMenu()
        menu.exec_(entry.mapToGlobal(pos))

    def create_action_buttons(self):
        """创建控制按钮（切换、计算和清除）"""
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        control_layout.setContentsMargins(0, 10, 0, 10)
        control_layout.setSpacing(10)

        # 创建左侧的切换按钮
        self.toggle_button = QPushButton("▲")
        self.toggle_button.setFixedSize(45, 45)
        self.toggle_button.setFocusPolicy(Qt.NoFocus)
        self.toggle_button.clicked.connect(self.toggle_numpad)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                font-family: "Microsoft YaHei";
                background-color: #f0f0f0;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)

        control_layout.addWidget(self.toggle_button)
        control_layout.addStretch()

        # 创建计算按钮（使用 = 符号）
        calc_btn = QPushButton("=")
        calc_btn.setFixedSize(80, 45)
        calc_btn.setFocusPolicy(Qt.NoFocus)
        calc_btn.clicked.connect(self.calculate)
        calc_btn.setStyleSheet("""
            QPushButton {
                font-family: "Microsoft YaHei";
                background-color: #0078d4;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)

        # 创建清除按钮（使用 × 符号）
        clear_btn = QPushButton("×")
        clear_btn.setFixedSize(80, 45)
        clear_btn.setFocusPolicy(Qt.NoFocus)
        clear_btn.clicked.connect(self.do_clear_all)
        clear_btn.setStyleSheet("""
            QPushButton {
                font-family: "Microsoft YaHei";
                background-color: #e81123;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: #c41019;
            }
        """)

        control_layout.addWidget(calc_btn)
        control_layout.addWidget(clear_btn)
        self.main_layout.addWidget(control_widget)

    def create_numpad_toggle(self):
        """创建数字键盘切换按钮"""
        toggle_widget = QWidget()
        toggle_layout = QHBoxLayout(toggle_widget)
        toggle_layout.setContentsMargins(0, 5, 0, 5)

        toggle_layout.addStretch()  # 左侧添加弹性空间

        self.toggle_button = QPushButton("▼")
        self.toggle_button.setFixedSize(45, 45)
        self.toggle_button.setFocusPolicy(Qt.NoFocus)
        self.toggle_button.clicked.connect(self.toggle_numpad)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                font-family: "Microsoft YaHei";
                background-color: #f0f0f0;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)

        toggle_layout.addWidget(self.toggle_button)

        self.main_layout.addWidget(toggle_widget)

    def create_numpad(self):
        """创建数字键盘"""
        self.numpad_widget = QWidget()
        numpad_layout = QGridLayout(self.numpad_widget)
        numpad_layout.setSpacing(0)
        numpad_layout.setContentsMargins(0, 0, 0, 0)

        buttons = [
            '7', '8', '9',
            '4', '5', '6',
            '1', '2', '3',
            '.', '0', '←'
        ]

        positions = [(i, j) for i in range(4) for j in range(3)]
        button_size = 95

        for position, button in zip(positions, buttons):
            btn = QPushButton(button)
            btn.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
            btn.setFixedSize(button_size, button_size)
            btn.setFocusPolicy(Qt.NoFocus)

            if button == '←':
                btn.setStyleSheet("""
                            QPushButton {
                                font-family: "Microsoft YaHei";
                                background-color: #0078d4;
                                color: white;
                                border: 1px solid #0078d4;
                                border-radius: 5px;
                                font-size: 18px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background-color: #106ebe;
                            }
                        """)
            else:
                btn.setStyleSheet("""
                            QPushButton {
                                font-family: "Microsoft YaHei";
                                background-color: white;
                                border: 1px solid #dcdcdc;
                                border-radius: 5px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background-color: #f0f0f0;
                            }
                        """)

            btn.clicked.connect(lambda x, b=button: self.numpad_click(b))
            numpad_layout.addWidget(btn, *position)

        self.main_layout.addWidget(self.numpad_widget)
        self.numpad_widget.setVisible(False)

    def create_transparency_slider(self):
        """创建透明度滑块"""
        slider_widget = QWidget()
        slider_layout = QVBoxLayout(slider_widget)
        slider_layout.setContentsMargins(0, 10, 0, 5)
        slider_layout.setSpacing(5)

        self.transparency_label = QLabel("透明度")
        self.transparency_label.setAlignment(Qt.AlignCenter)
        self.transparency_label.setStyleSheet("""
                    font-family: "Microsoft YaHei";
                    font-size: 14px;
                    font-weight: bold;
                """)

        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(15, 100)
        self.transparency_slider.setValue(100)
        self.transparency_slider.valueChanged.connect(self.update_transparency)
        self.transparency_slider.setFocusPolicy(Qt.NoFocus)

        # 设置滑块的样式
        self.transparency_slider.setStyleSheet("""
               QSlider::groove:horizontal {
                   border: 1px solid #999999;
                   height: 4px;
                   background: #cccccc;
                   margin: 2px 0;
                   border-radius: 2px;
               }

               QSlider::handle:horizontal {
                   background: #0078d4;
                   border: 2px solid #0078d4;
                   width: 16px;
                   height: 16px;
                   margin: -8px 0;
                   border-radius: 10px;
               }

               QSlider::handle:horizontal:hover {
                   background: #106ebe;
                   border: 2px solid #106ebe;
               }

               QSlider::sub-page:horizontal {
                   background: #cccccc;
                   border-radius: 2px;
               }
           """)

        slider_layout.addWidget(self.transparency_label)
        slider_layout.addWidget(self.transparency_slider)

        self.main_layout.addWidget(slider_widget)

    def update_transparency(self, value):
        """更新窗口透明度"""
        opacity = value / 100.0
        self.setWindowOpacity(opacity)
        self.transparency_label.setText(f"透明度")

    def toggle_numpad(self):
        self.numpad_visible = not self.numpad_visible
        self.toggle_button.setText("▼" if self.numpad_visible else "▲")
        self.numpad_widget.setVisible(self.numpad_visible)

        # 调整窗口大小
        if self.numpad_visible:
            self.setFixedHeight(750)
        else:
            self.setFixedHeight(450)

    def numpad_click(self, value):
        """处理数字键盘点击事件"""
        if not self.current_entry:
            self.current_entry = self.prob1_entry
            self.current_entry.setFocus()

        if value == '←':
            if self.current_entry and self.current_entry.text():
                current_text = self.current_entry.text()
                self.current_entry.setText(current_text[:-1])
        elif value == '.':
            if self.current_entry in [self.prob1_entry, self.prob2_entry]:
                current_text = self.current_entry.text()
                if '.' not in current_text:
                    if not current_text:
                        self.current_entry.setText('0')
                    self.current_entry.setText(current_text + '.')
        else:
            current_text = self.current_entry.text()
            self.current_entry.setText(current_text + value)

    def keyPressEvent(self, event):
        """处理键盘事件"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.calculate()
        elif event.key() == Qt.Key_Space:
            self.do_clear_all()
        elif event.key() == Qt.Key_Backspace:
            if self.current_entry and self.current_entry.text():
                current_text = self.current_entry.text()
                self.current_entry.setText(current_text[:-1])
        else:
            super().keyPressEvent(event)

    def on_entry_click(self, entry):
        """处理输入框点击事件"""
        self.current_entry = entry
        entry.setFocus()
        content = entry.text().strip()
        if content:
            pyperclip.copy(content)

def main():
        app = QApplication(sys.argv)
        calculator = FloatingCalculator()
        calculator.prob1_entry.setFocus()
        calculator.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()