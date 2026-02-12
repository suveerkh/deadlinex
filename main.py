import sys
import sqlite3
import math
import json
import os
import subprocess
from dotenv import load_dotenv
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget,
    QScrollArea, QGraphicsDropShadowEffect, QLineEdit, QDateEdit, QTimeEdit,
    QTextEdit, QFileDialog, QAbstractSpinBox, QComboBox, QMenu, QMessageBox, QDialog, QCheckBox, QCalendarWidget,
    QToolTip, QSystemTrayIcon, QFrame, QToolButton, QSizePolicy, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QSize, QDateTime, QTimer, Signal, QRectF, QTime, QPoint, QThread, QDate, QObject, QEvent, QSettings, QUrl, QStandardPaths
from PySide6.QtGui import QColor, QPainter, QIcon, QAction, QPixmap, QTextCharFormat, QFont
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget
from google import genai

load_dotenv()

# Inline SVG icons
SVG_HOME = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M240 6.1c9.1-8.2 22.9-8.2 32 0l232 208c9.9 8.8 10.7 24 1.8 33.9s-24 10.7-33.9 1.8l-8-7.2 0 205.3c0 35.3-28.7 64-64 64l-288 0c-35.3 0-64-28.7-64-64l0-205.3-8 7.2c-9.9 8.8-25 8-33.9-1.8s-8-25 1.8-33.9L240 6.1zm16 50.1L96 199.7 96 448c0 8.8 7.2 16 16 16l48 0 0-104c0-39.8 32.2-72 72-72l48 0c39.8 0 72 32.2 72 72l0 104 48 0c8.8 0 16-7.2 16-16l0-248.3-160-143.4zM208 464l96 0 0-104c0-13.3-10.7-24-24-24l-48 0c-13.3 0-24 10.7-24 24l0 104z"/></svg>"""
SVG_TASK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M133.8 36.3c10.9 7.6 13.5 22.6 5.9 33.4l-56 80c-4.1 5.8-10.5 9.5-17.6 10.1S52 158 47 153L7 113C-2.3 103.6-2.3 88.4 7 79S31.6 69.7 41 79l19.8 19.8 39.6-56.6c7.6-10.9 22.6-13.5 33.4-5.9zm0 160c10.9 7.6 13.5 22.6 5.9 33.4l-56 80c-4.1 5.8-10.5 9.5-17.6 10.1S52 318 47 313L7 273c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l19.8 19.8 39.6-56.6c7.6-10.9 22.6-13.5 33.4-5.9zM224 96c0-17.7 14.3-32 32-32l224 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-224 0c-17.7 0-32-14.3-32-32zm0 160c0-17.7 14.3-32 32-32l224 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-224 0c-17.7 0-32-14.3-32-32zM160 416c0-17.7 14.3-32 32-32l288 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-288 0c-17.7 0-32-14.3-32-32zM64 376a40 40 0 1 1 0 80 40 40 0 1 1 0-80z"/></svg>"""
SVG_SUN = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><path d="M178.2-10.1c7.4-3.1 15.8-2.2 22.5 2.2l87.8 58.2 87.8-58.2c6.7-4.4 15.1-5.2 22.5-2.2S411.4-.5 413 7.3l20.9 103.2 103.2 20.9c7.8 1.6 14.4 7 17.4 14.3s2.2 15.8-2.2 22.5l-58.2 87.8 58.2 87.8c4.4 6.7 5.2 15.1 2.2 22.5s-9.6 12.8-17.4 14.3L433.8 401.4 413 504.7c-1.6 7.8-7 14.4-14.3 17.4s-15.8 2.2-22.5-2.2l-87.8-58.2-87.8 58.2c-6.7 4.4-15.1 5.2-22.5 2.2s-12.8-9.6-14.3-17.4L143 401.4 39.7 380.5c-7.8-1.6-14.4-7-17.4-14.3s-2.2-15.8 2.2-22.5L82.7 256 24.5 168.2c-4.4-6.7-5.2-15.1-2.2-22.5s9.6-12.8 17.4-14.3L143 110.6 163.9 7.3c1.6-7.8 7-14.4 14.3-17.4zM207.6 256a80.4 80.4 0 1 1 160.8 0 80.4 80.4 0 1 1 -160.8 0zm208.8 0a128.4 128.4 0 1 0 -256.8 0 128.4 128.4 0 1 0 256.8 0z"/></svg>"""
SVG_MOON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M256 0C114.6 0 0 114.6 0 256S114.6 512 256 512c68.8 0 131.3-27.2 177.3-71.4 7.3-7 9.4-17.9 5.3-27.1s-13.7-14.9-23.8-14.1c-4.9 .4-9.8 .6-14.8 .6-101.6 0-184-82.4-184-184 0-72.1 41.5-134.6 102.1-164.8 9.1-4.5 14.3-14.3 13.1-24.4S322.6 8.5 312.7 6.3C294.4 2.2 275.4 0 256 0z"/></svg>"""
SVG_DELETE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M136.7 5.9L128 32 32 32C14.3 32 0 46.3 0 64S14.3 96 32 96l384 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-96 0-8.7-26.1C306.9-7.2 294.7-16 280.9-16L167.1-16c-13.8 0-26 8.8-30.4 21.9zM416 144L32 144 53.1 467.1C54.7 492.4 75.7 512 101 512L347 512c25.3 0 46.3-19.6 47.9-44.9L416 144z"/></svg>"""
SVG_FILTER = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M32 64C19.1 64 7.4 71.8 2.4 83.8S.2 109.5 9.4 118.6L192 301.3 192 416c0 8.5 3.4 16.6 9.4 22.6l64 64c9.2 9.2 22.9 11.9 34.9 6.9S320 492.9 320 480l0-178.7 182.6-182.6c9.2-9.2 11.9-22.9 6.9-34.9S492.9 64 480 64L32 64z"/></svg>"""
SVG_CHAT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M512 240c0 114.9-114.6 208-256 208c-37.1 0-72.3-6.4-104.1-17.9c-11.9 8.7-31.3 20.6-54.3 30.6C73.6 471.1 44.7 480 16 480c-6.5 0-12.3-3.9-14.8-9.9c-2.5-6-1.1-12.8 3.4-17.4l0 0 0 0 0 0 0 0 .3-.3c.3-.3 .7-.7 1.3-1.4c1.1-1.2 2.8-3.1 4.9-5.7c4.1-5 9.6-12.4 15.2-21.6c10-16.6 19.5-38.4 21.4-62.9C17.7 326.8 0 285.1 0 240C0 125.1 114.6 32 256 32s256 93.1 256 208z"/></svg>"""
SVG_CALENDAR = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M152 24c0-13.3-10.7-24-24-24s-24 10.7-24 24l0 40L64 64c-35.3 0-64 28.7-64 64l0 320c0 35.3 28.7 64 64 64l320 0c35.3 0 64-28.7 64-64l0-320c0-35.3-28.7-64-64-64l-40 0 0-40c0-13.3-10.7-24-24-24s-24 10.7-24 24l0 40L152 64l0-40zM48 192l352 0 0 256c0 8.8-7.2 16-16 16L64 464c-8.8 0-16-7.2-16-16l0-256z"/></svg>"""
SVG_CHEVRON_LEFT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M9.4 233.4c-12.5 12.5-12.5 32.8 0 45.3l192 192c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L77.3 256 246.6 86.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-192 192z"/></svg>"""
SVG_CHEVRON_RIGHT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 233.4c12.5 12.5 12.5 32.8 0 45.3l-192 192c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L242.7 256 73.4 86.6c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l192 192z"/></svg>"""
SVG_TIMER = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M256 0a256 256 0 1 1 0 512A256 256 0 1 1 256 0zM232 120l0 136c0 8 4 15.5 10.7 20l96 64c11 7.4 25.9 4.4 33.3-6.7s4.4-25.9-6.7-33.3L280 243.2 280 120c0-13.3-10.7-24-24-24s-24 10.7-24 24z"/></svg>"""
SVG_SETTINGS = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M495.9 166.6c3.2 8.7 .5 18.4-6.4 24.6l-43.3 39.4c1.1 8.3 1.7 16.8 1.7 25.4s-.6 17.1-1.7 25.4l43.3 39.4c6.9 6.2 9.6 15.9 6.4 24.6c-4.4 11.9-9.7 23.3-15.8 34.3l-4.7 8.1c-6.6 11-14 21.4-22.1 31.2c-5.9 7.2-15.7 9.6-24.5 6.8l-55.7-17.7c-13.4 10.3-28.2 18.9-44 25.4l-12.5 57.1c-2 9.1-9 16.3-18.2 17.8c-13.8 2.3-28 3.5-42.5 3.5s-28.7-1.2-42.5-3.5c-9.2-1.5-16.2-8.7-18.2-17.8l-12.5-57.1c-15.8-6.5-30.6-15.1-44-25.4L83.1 425.9c-8.8 2.8-18.6 .3-24.5-6.8c-8.1-9.8-15.5-20.2-22.1-31.2l-4.7-8.1c-6.1-11-11.4-22.4-15.8-34.3c-3.2-8.7-.5-18.4 6.4-24.6l43.3-39.4C64.6 273.1 64 264.6 64 256s.6-17.1 1.7-25.4L22.4 191.2c-6.9-6.2-9.6-15.9-6.4-24.6c4.4-11.9 9.7-23.3 15.8-34.3l4.7-8.1c6.6-11 14-21.4 22.1-31.2c5.9-7.2 15.7-9.6 24.5-6.8l55.7 17.7c13.4-10.3 28.2-18.9 44-25.4l12.5-57.1c2-9.1 9-16.3 18.2-17.8C227.3 1.2 241.5 0 256 0s28.7 1.2 42.5 3.5c9.2 1.5 16.2 8.7 18.2 17.8l12.5 57.1c15.8 6.5 30.6 15.1 44 25.4l55.7-17.7c8.8-2.8 18.6-.3 24.5 6.8c8.1 9.8 15.5 20.2 22.1 31.2l4.7 8.1c6.1 11 11.4 22.4 15.8 34.3zM256 336a80 80 0 1 0 0-160 80 80 0 1 0 0 160z"/></svg>"""
SVG_CLOSE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><path d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z"/></svg>"""
SVG_ALERT="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M256 0c14.7 0 28.2 8.1 35.2 21l216 400c6.7 12.4 6.4 27.4-.8 39.5S486.1 480 472 480L40 480c-14.1 0-27.2-7.4-34.4-19.5s-7.5-27.1-.8-39.5l216-400c7-12.9 20.5-21 35.2-21zm0 352a32 32 0 1 0 0 64 32 32 0 1 0 0-64zm0-192c-18.2 0-32.7 15.5-31.4 33.7l7.4 104c.9 12.5 11.4 22.3 23.9 22.3 12.6 0 23-9.7 23.9-22.3l7.4-104c1.3-18.2-13.1-33.7-31.4-33.7z"/></svg>"""

# Scrollbar Stylesheet
SCROLLBAR_STYLESHEET = """
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #b0b0b0;
    min-height: 20px;
    border-radius: 5px;
    margin: 2px;
}
QScrollBar::handle:vertical:hover {
    background: #909090;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 10px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: #b0b0b0;
    min-width: 20px;
    border-radius: 5px;
    margin: 2px;
}
QScrollBar::handle:horizontal:hover {
    background: #909090;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}
"""

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Clickable SVG Widget
class ClickableSvgWidget(QSvgWidget):
    clicked = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
    def mousePressEvent(self, event):
        self.clicked.emit()
        event.accept()

# Sidebar Button using SVG Widget
class SvgButton(QWidget):
    def __init__(self, text, svg_code):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("SvgButton")
        self.svg_code = svg_code
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.svg = QSvgWidget()
        self.update_icon_color("#333333")
        self.svg.setFixedSize(24,24)
        self.btn = QPushButton(text)
        self.btn.setStyleSheet("color:#333333;font-size:16px;background:transparent;border:none;text-align:left;padding:5px;")
        layout.addWidget(self.svg)
        layout.addWidget(self.btn)
        layout.addStretch()
        layout.setContentsMargins(5,5,5,5)

    def update_icon_color(self, color):
        new_svg = self.svg_code.replace('<svg ', f'<svg fill="{color}" ')
        self.svg.load(bytearray(new_svg, 'utf-8'))

    def set_theme(self, is_light):
        text_color = "#333333" if is_light else "#ffffff"
        hover_bg = "#e0e0e0" if is_light else "#3c3c3c"
        self.btn.setStyleSheet(f"color:{text_color};font-size:16px;background:transparent;border:none;text-align:left;padding:5px;")
        self.setStyleSheet(f"""
            #SvgButton {{ background-color: transparent; border-radius: 5px; }}
            #SvgButton:hover {{ background-color: {hover_bg}; }}
        """)
        self.update_icon_color(text_color)

# Hover SVG Widget
class HoverSvgWidget(ClickableSvgWidget):
    def __init__(self, svg_code, normal_color, hover_color="#ff4444", parent=None):
        super().__init__(parent)
        self.svg_code = svg_code
        self.normal_color = normal_color
        self.hover_color = hover_color
        self._update_bytes()
        self.load(self.normal_svg_bytes)

    def _update_bytes(self):
        self.normal_svg_bytes = bytearray(self.svg_code.replace('<svg ', f'<svg fill="{self.normal_color}" '), 'utf-8')
        self.hover_svg_bytes = bytearray(self.svg_code.replace('<svg ', f'<svg fill="{self.hover_color}" '), 'utf-8')

    def enterEvent(self, event):
        self.load(self.hover_svg_bytes)
        super().enterEvent(event)
    def leaveEvent(self, event):
        self.load(self.normal_svg_bytes)
        super().leaveEvent(event)
    
    def set_theme_colors(self, normal, hover):
        self.normal_color = normal
        self.hover_color = hover
        self._update_bytes()
        self.load(self.normal_svg_bytes)

# Icon Hover Filter for QToolButton
class IconHoverFilter(QObject):
    def __init__(self, button, svg_code, normal_color, hover_color):
        super().__init__(button)
        self.button = button
        self.normal_pixmap = self._create_pixmap(svg_code, normal_color)
        self.hover_pixmap = self._create_pixmap(svg_code, hover_color)
        self.button.setIcon(QIcon(self.normal_pixmap))

    def _create_pixmap(self, svg_code, color):
        new_svg = svg_code.replace('<svg ', f'<svg fill="{color}" ')
        renderer = QSvgRenderer(bytearray(new_svg, 'utf-8'))
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap

    def eventFilter(self, obj, event):
        if obj == self.button:
            if event.type() == QEvent.Enter:
                self.button.setIcon(QIcon(self.hover_pixmap))
            elif event.type() == QEvent.Leave:
                self.button.setIcon(QIcon(self.normal_pixmap))
        return super().eventFilter(obj, event)

# Attachment Item Widget
class AttachmentItemWidget(QWidget):
    deleted = Signal(QListWidgetItem)

    def __init__(self, text, item, is_light, parent=None):
        super().__init__(parent)
        self.item = item
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        filename = os.path.basename(text)
        self.label = QLabel(filename)
        self.label.setToolTip(text)
        self.label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.label)
        layout.addStretch()

        self.delete_btn = QToolButton()
        self.delete_btn.setFixedSize(16, 16)
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setStyleSheet("background: transparent; border: none;")
        self.delete_btn.clicked.connect(lambda: self.deleted.emit(self.item))
        layout.addWidget(self.delete_btn)
        
        self.update_theme(is_light)

    def update_theme(self, is_light):
        text_color = "#333" if is_light else "#fff"
        self.label.setStyleSheet(f"background: transparent; border: none; color: {text_color};")
        
        if hasattr(self, "delete_filter"):
            self.delete_btn.removeEventFilter(self.delete_filter)
            
        icon_color = "#666" if is_light else "#aaa"
        self.delete_filter = IconHoverFilter(self.delete_btn, SVG_CLOSE, icon_color, "#ff4444")
        self.delete_btn.installEventFilter(self.delete_filter)

# Assignment 
class Assignment:
    def __init__(self, title, deadline, completed=False, description="", attachment=None, difficulty="Easy", id=None):
        self.id = id
        self.title = title
        self.deadline = deadline
        self.completed = completed
        self.description = description
        if attachment is None:
            self.attachment = []
        elif isinstance(attachment, str):
            self.attachment = [attachment] if attachment else []
        else:
            self.attachment = attachment
        self.difficulty = difficulty

class AssignmentWidget(QWidget):
    deleted = Signal(object)
    completed = Signal(object, bool)
    clicked = Signal(object)

    def __init__(self, assignment, parent=None):
        super().__init__(parent)
        self.assignment = assignment
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCursor(Qt.PointingHandCursor)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        info_layout = QVBoxLayout()
        self.title_lbl = QLabel(assignment.title)
        
        date_str = assignment.deadline.toString("MMM d, yyyy h:mm ap")
        self.date_lbl = QLabel(f"Due: {date_str}")
        
        info_layout.addWidget(self.title_lbl)
        info_layout.addWidget(self.date_lbl)
        
        diff_colors = {"Easy": "#81c784", "Low": "#81c784", "Medium": "#ffb74d", "Hard": "#e57373", "High": "#e57373"}
        c = diff_colors.get(assignment.difficulty, "#888")
        self.diff_lbl = QLabel(assignment.difficulty)
        self.diff_lbl.setStyleSheet(f"color: {c}; border: 1px solid {c}; border-radius: 4px; padding: 2px 4px; font-size: 10px; font-weight: bold;")
        info_layout.addWidget(self.diff_lbl)
        
        if not assignment.completed:
            now = QDateTime.currentDateTime()
            days = now.date().daysTo(assignment.deadline.date())
            
            urgency_text = ""
            urgency_color = ""
            
            if now > assignment.deadline:
                urgency_text = "Past Due"
                urgency_color = "#e57373"
            elif days <= 2:
                urgency_text = "Urgent"
                urgency_color = "#e57373"
            elif days <= 7:
                urgency_text = "Upcoming"
                urgency_color = "#ffb74d"
            else:
                urgency_text = "Safe"
                urgency_color = "#81c784"
            
            self.urgency_lbl = QLabel(urgency_text)
            self.urgency_lbl.setStyleSheet(f"color: {urgency_color}; font-weight: bold; font-size: 12px; border: none; background: transparent;")
            info_layout.addWidget(self.urgency_lbl)
            
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        self.delete_btn = QToolButton()
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setStyleSheet("background: transparent; border: none;")
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.clicked.connect(lambda: self.deleted.emit(self.assignment))
        layout.addWidget(self.delete_btn)
        
        self.update_theme(True)

    def update_theme(self, is_light):
        bg = "#f9f9f9" if is_light else "#2c2c2c"
        border = "#ddd" if is_light else "#444"
        text_color = "#333" if is_light else "#fff"
        date_color = "#666" if is_light else "#aaa"
        icon_color = "#333333" if is_light else "#ffffff"
        
        self.setStyleSheet(f"background-color: {bg}; border-radius: 10px; border: 1px solid {border}; color: {text_color};")
        self.title_lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {text_color}; border: none; background: transparent;")
        self.date_lbl.setStyleSheet(f"color: {date_color}; font-size: 14px; border: none; background: transparent;")
        
        if hasattr(self, "delete_filter"):
            self.delete_btn.removeEventFilter(self.delete_filter)
        
        self.delete_filter = IconHoverFilter(self.delete_btn, SVG_DELETE, icon_color, "#ff4444")
        self.delete_btn.installEventFilter(self.delete_filter)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.assignment)
        super().mouseReleaseEvent(event)

# Database Manager
class DatabaseManager:
    def __init__(self, db_name="assignments.db"):
        data_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        db_path = os.path.join(data_dir, db_name)
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                deadline TEXT,
                completed INTEGER,
                description TEXT,
                attachment TEXT,
                difficulty TEXT
            )
        """)
        self.conn.commit()

    def add_assignment(self, assignment):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO assignments (title, deadline, completed, description, attachment, difficulty)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (assignment.title, assignment.deadline.toString(Qt.ISODate),
              1 if assignment.completed else 0, assignment.description,
              json.dumps(assignment.attachment), assignment.difficulty))
        assignment.id = cursor.lastrowid
        self.conn.commit()

    def update_assignment(self, assignment):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE assignments
            SET title=?, deadline=?, completed=?, description=?, attachment=?, difficulty=?
            WHERE id=?
        """, (assignment.title, assignment.deadline.toString(Qt.ISODate),
              1 if assignment.completed else 0, assignment.description,
              json.dumps(assignment.attachment), assignment.difficulty, assignment.id))
        self.conn.commit()

    def delete_assignment(self, assignment_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM assignments WHERE id=?", (assignment_id,))
        self.conn.commit()

    def _parse_attachments(self, attachment_data):
        if not attachment_data:
            return []
        try:
            attachments = json.loads(attachment_data)
            return attachments if isinstance(attachments, list) else [str(attachments)]
        except json.JSONDecodeError:
            return [attachment_data]  

    def load_assignments(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM assignments")
        rows = cursor.fetchall()
        return [
            Assignment(
                id=row[0],
                title=row[1],
                deadline=QDateTime.fromString(row[2], Qt.ISODate),
                completed=bool(row[3]),
                description=row[4],
                attachment=self._parse_attachments(row[5]),
                difficulty=row[6]
            ) for row in rows
        ]

# Pie Chart Widget - shows distribution of assignments by urgency
class PieChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.past_due = 0
        self.red = 0
        self.yellow = 0
        self.green = 0
        self.setMinimumSize(250, 250)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setMouseTracking(True)

    def set_data(self, past_due, red, yellow, green):
        self.past_due = past_due
        self.red = red
        self.yellow = yellow
        self.green = green
        self.update()

    def paintEvent(self, event):
        self.bars = []
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        total = self.past_due + self.red + self.yellow + self.green
        rect = self.rect()
        size = min(rect.width(), rect.height()) - 20
        rect = QRectF((rect.width() - size) / 2, (rect.height() - size) / 2, size, size)

        if total == 0:
            painter.setBrush(QColor("#cccccc"))
            painter.drawEllipse(rect)
            return

        start_angle = 90 * 16
        
        # Past Due
        if self.past_due > 0:
            span = int((self.past_due / total) * 360 * 16)
            painter.setBrush(QColor("#d32f2f"))
            painter.drawPie(rect, start_angle, span)
            start_angle += span

        # Red (<= 2 days)
        if self.red > 0:
            span = int((self.red / total) * 360 * 16)
            painter.setBrush(QColor("#e57373"))
            painter.drawPie(rect, start_angle, span)
            start_angle += span
            
        # Yellow (3-7 days)
        if self.yellow > 0:
            span = int((self.yellow / total) * 360 * 16)
            painter.setBrush(QColor("#ffb74d"))
            painter.drawPie(rect, start_angle, span)
            start_angle += span
            
        # Green (> 7 days)
        if self.green > 0:
            remaining = (90 * 16 + 360 * 16) - start_angle
            painter.setBrush(QColor("#81c784"))
            painter.drawPie(rect, start_angle, remaining)

    def mouseMoveEvent(self, event):
        total = self.past_due + self.red + self.yellow + self.green
        if total == 0:
            return

        rect = self.rect()
        size = min(rect.width(), rect.height()) - 20
        pie_rect = QRectF((rect.width() - size) / 2, (rect.height() - size) / 2, size, size)
        
        center = pie_rect.center()
        pos = event.position()
        dx = pos.x() - center.x()
        dy = pos.y() - center.y()
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > size/2:
            QToolTip.hideText()
            return

        angle_rad = math.atan2(-dy, dx)
        angle_deg = math.degrees(angle_rad)
        if angle_deg < 0:
            angle_deg += 360
            
        rel_angle = angle_deg - 90
        if rel_angle < 0:
            rel_angle += 360
            
        past_due_span = (self.past_due / total) * 360
        red_span = (self.red / total) * 360
        yellow_span = (self.yellow / total) * 360
        
        if rel_angle < past_due_span:
            text = f"Past Due: {self.past_due}"
        elif rel_angle < past_due_span + red_span:
            text = f"Urgent (<= 2 days): {self.red}"
        elif rel_angle < past_due_span + red_span + yellow_span:
            text = f"Upcoming (3-7 days): {self.yellow}"
        else:
            text = f"Safe (> 7 days): {self.green}"
            
        QToolTip.showText(event.globalPosition().toPoint(), text)

# AI Worker 
class AIWorker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, client, prompt):
        super().__init__()
        self.client = client
        self.prompt = prompt
        self.models = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]

    def run(self):
        for model in self.models:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=self.prompt
                )
                self.finished.emit(response.text)
                return
            except Exception as e:
                err_str = str(e).lower()
                if "429" in err_str or "resource" in err_str or "quota" in err_str:
                    continue
                self.error.emit(str(e))
                return
        self.error.emit("Global Rate Limit Reached. Please Try Again Later!")

class ThinkingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.dots = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(300)
        self.is_light = True

    def animate(self):
        self.dots = (self.dots + 1) % 4
        self.update()

    def set_theme(self, is_light):
        self.is_light = is_light
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor("#666") if self.is_light else QColor("#ccc")
        painter.setPen(color)
        text = "DeadlineX AI is thinking" + "." * self.dots
        painter.drawText(self.rect(), Qt.AlignLeft | Qt.AlignVCenter, text)

class FlashCard(QFrame):
    def __init__(self, title, text, color_start, color_end, icon_svg, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedHeight(140)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.setStyleSheet(f"""
            FlashCard {{
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 {color_start}, stop:1 {color_end});
                border-radius: 20px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        
        header = QHBoxLayout()
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 15px; font-weight: 600; background: transparent; border: none;")
        
        self.icon_widget = QSvgWidget()
        self.icon_widget.setFixedSize(28, 28)
        new_svg = icon_svg.replace('<svg ', '<svg fill="rgba(255,255,255,0.9)" ')
        self.icon_widget.load(bytearray(new_svg, 'utf-8'))
        self.icon_widget.setStyleSheet("background: transparent; border: none;")
        
        header.addWidget(self.title_lbl)
        header.addStretch()
        header.addWidget(self.icon_widget)
        layout.addLayout(header)
        
        self.text_lbl = QLabel(text)
        self.text_lbl.setStyleSheet("color: white; font-size: 20px; font-weight: bold; background: transparent; border: none;")
        self.text_lbl.setWordWrap(True)
        layout.addWidget(self.text_lbl)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)

    def update_text(self, text):
        self.text_lbl.setText(text)

    def update_theme(self, is_light):
        pass

# Bar Chart Widget - shows number of assignments each week
class BarChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.data = [] 
        self.bars = [] 
        self.setMinimumHeight(200)
        self.is_light = True
        self.setMouseTracking(True)

    def set_data(self, data):
        self.data = data
        self.update()

    def update_theme(self, is_light):
        self.is_light = is_light
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        left, right, top, bottom = 40, 20, 20, 40
        
        axis_color = QColor("#333") if self.is_light else QColor("#fff")
        painter.setPen(axis_color)
        painter.drawLine(left, rect.height() - bottom, rect.width() - right, rect.height() - bottom)
        painter.drawLine(left, rect.height() - bottom, left, top)
        
        if not self.data: return

        max_val = max([d[1] for d in self.data]) if self.data else 1
        if max_val == 0: max_val = 1
        
        count = len(self.data)
        bar_width = (rect.width() - left - right) / count * 0.6
        spacing = (rect.width() - left - right) / count * 0.4
        
        x = left + spacing / 2
        
        for label, value in self.data:
            h = (value / max_val) * (rect.height() - top - bottom)
            y = rect.height() - bottom - h
            
            painter.setBrush(QColor("#2196F3"))
            painter.setPen(Qt.NoPen)
            bar_rect = QRectF(x, y, bar_width, h)
            painter.drawRoundedRect(bar_rect, 4, 4)
            
            self.bars.append((bar_rect, value, label))
            
            painter.setPen(axis_color)
            painter.drawText(QRectF(x - 10, rect.height() - bottom + 5, bar_width + 20, 20), Qt.AlignCenter, label)
            
            x += bar_width + spacing

    def mouseMoveEvent(self, event):
        pos = event.position()
        for rect, value, label in self.bars:
            if rect.contains(pos):
                QToolTip.showText(event.globalPosition().toPoint(), f"{label}: {value} assignments")
                return
        QToolTip.hideText()

# Dashboard Widget
class Dashboard(QWidget):
    assignment_clicked = Signal(object)
    assignment_deleted = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chart_week_offset = 0
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Dashboard")
        lbl_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Stats Cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.card_monthly = FlashCard("Monthly Progress", "0 cleared this month", "#4facfe", "#00f2fe", SVG_CALENDAR)
        self.card_due = FlashCard("Alert!", "0 assignments are past due!", "#43e97b", "#38f9d7", SVG_ALERT)
        self.card_pending = FlashCard("Focus", "0 more to go", "#fa709a", "#fee140", SVG_TIMER)
        
        stats_layout.addWidget(self.card_monthly)
        stats_layout.addWidget(self.card_due)
        stats_layout.addWidget(self.card_pending)
        layout.addLayout(stats_layout)
        
        # Charts Area
        charts_container = QWidget()
        charts_layout = QHBoxLayout(charts_container)
        charts_layout.setContentsMargins(0,0,0,0)
        
        # Pie Chart
        pie_container = QWidget()
        pie_layout = QVBoxLayout(pie_container)
        pie_layout.setContentsMargins(0,0,0,0)
        pie_lbl = QLabel("Assignments Distribution")
        pie_lbl.setAlignment(Qt.AlignCenter)
        pie_lbl.setStyleSheet("font-weight: bold; margin-bottom: 5px; border: none;")
        pie_layout.addWidget(pie_lbl)
        self.chart = PieChartWidget()
        pie_layout.addWidget(self.chart)
        charts_layout.addWidget(pie_container)
        
        # Bar Chart
        bar_container = QWidget()
        bar_layout = QVBoxLayout(bar_container)
        
        bar_header = QHBoxLayout()
        bar_header.addWidget(QLabel("Weekly Workload"))
        bar_header.addStretch()
        
        self.prev_week_btn = HoverSvgWidget(SVG_CHEVRON_LEFT, "#333", "#ff9800")
        self.prev_week_btn.setFixedSize(24, 24)
        self.prev_week_btn.clicked.connect(self.prev_week)
        
        self.next_week_btn = HoverSvgWidget(SVG_CHEVRON_RIGHT, "#333", "#ff9800")
        self.next_week_btn.setFixedSize(24, 24)
        self.next_week_btn.clicked.connect(self.next_week)
        
        bar_header.addWidget(self.prev_week_btn)
        bar_header.addWidget(self.next_week_btn)
        bar_layout.addLayout(bar_header)
        
        self.bar_chart = BarChartWidget()
        bar_layout.addWidget(self.bar_chart)
        
        charts_layout.addWidget(bar_container)
        layout.addWidget(charts_container)
        
        # Due Today
        lbl_due = QLabel("Assignments Due Today")
        lbl_due.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(lbl_due)
        
        self.due_scroll = QScrollArea()
        self.due_scroll.setWidgetResizable(True)
        self.due_scroll.setStyleSheet("border: none;")
        
        self.due_container = QWidget()
        self.due_layout = QVBoxLayout(self.due_container)
        self.due_layout.setAlignment(Qt.AlignTop)
        self.due_layout.setContentsMargins(0, 0, 0, 0)
        
        self.due_scroll.setWidget(self.due_container)
        layout.addWidget(self.due_scroll)
        
        self.update_theme(True)

    def update_theme(self, is_light):
        text = "#333333" if is_light else "#ffffff"
        border = "#888" if is_light else "#555"
        
        self.card_monthly.update_theme(is_light)
        self.card_due.update_theme(is_light)
        self.card_pending.update_theme(is_light)
        self.bar_chart.update_theme(is_light)
        
        icon_color = "#333333" if is_light else "#ffffff"
        hover_bg = "#e0e0e0" if is_light else "#555555"
        
        self.prev_week_btn.set_theme_colors(icon_color, "#ff9800")
        self.next_week_btn.set_theme_colors(icon_color, "#ff9800")
        
        # Update items in due layout
        for i in range(self.due_layout.count()):
            w = self.due_layout.itemAt(i).widget()
            if isinstance(w, AssignmentWidget):
                w.update_theme(is_light)

    def prev_week(self):
        self.chart_week_offset -= 1
        if hasattr(self, 'last_assignments'):
            self.update_dashboard(self.last_assignments)

    def next_week(self):
        self.chart_week_offset += 1
        if hasattr(self, 'last_assignments'):
            self.update_dashboard(self.last_assignments)

    def _categorize_assignments(self, assignments):
        now = QDateTime.currentDateTime()
        today = now.date()
        past_due, red, yellow, green = 0, 0, 0, 0
        
        for a in assignments:
            if not a.completed:
                if now > a.deadline:
                    past_due += 1
                else:
                    days = today.daysTo(a.deadline.date())
                    if days <= 2:
                        red += 1
                    elif days <= 7:
                        yellow += 1
                    else:
                        green += 1
        return past_due, red, yellow, green

    def update_dashboard(self, assignments):
        self.last_assignments = assignments
        total = len(assignments)
        completed = sum(1 for a in assignments if a.completed)
        pending = total - completed
        
        now = QDateTime.currentDateTime()
        today = now.date()
        past_due, red, yellow, green = self._categorize_assignments(assignments)
        
        current_month = today.month()
        current_year = today.year()
        monthly_completed = sum(1 for a in assignments if a.completed and a.deadline.date().month() == current_month and a.deadline.date().year() == current_year)
        
        if monthly_completed == 0:
             self.card_monthly.update_text("No assignments cleared this month yet. Let's get started!")
        else:
            self.card_monthly.update_text(f"You have cleared {monthly_completed} assignments this month!")

        if past_due == 0:
             self.card_due.update_text("No assignments are past due! Great job!")
        else:
            self.card_due.update_text(f"You have {past_due} assignments past due!")
        
        if pending == 0:
             self.card_pending.update_text("All caught up! Great job!")
        else:
             self.card_pending.update_text(f"Only {pending} more to go!")
        
        self.chart.set_data(past_due, red, yellow, green)
        
        # Weekly Workload (4 Weeks View)
        start_date = today.addDays(self.chart_week_offset * 7)
        
        bar_data = []
        for i in range(4): # Show 4 weeks
            week_start = start_date.addDays(i * 7)
            week_end = week_start.addDays(6)
            count = sum(1 for a in assignments if not a.completed and week_start <= a.deadline.date() <= week_end)
            label = week_start.toString("d/M")
            bar_data.append((label, count))
            
        self.bar_chart.set_data(bar_data)

        # Update Due Today List
        while self.due_layout.count():
            item = self.due_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for a in assignments:
            if not a.completed and a.deadline.date() == today:
                w = AssignmentWidget(a)
                w.clicked.connect(self.assignment_clicked.emit)
                w.deleted.connect(self.assignment_deleted.emit)
                is_light = self.bar_chart.is_light 
                w.update_theme(is_light)
                self.due_layout.addWidget(w)

# Delete Popup
class DeletePopup(QDialog):
    def __init__(self, title, is_light, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        self.widget = QWidget()
        
        bg = "#ffffff" if is_light else "#333333"
        text = "#333333" if is_light else "#ffffff"
        border = "#ccc" if is_light else "#555"
        
        self.widget.setStyleSheet(f"QWidget {{ background-color: {bg}; border: 1px solid {border}; border-radius: 15px; }} QLabel {{ color: {text}; font-size: 16px; border: none; }}")
        
        inner = QVBoxLayout(self.widget)
        inner.setContentsMargins(20, 20, 20, 20)
        
        lbl = QLabel(f"Delete '{title}'?")
        lbl.setAlignment(Qt.AlignCenter)
        inner.addWidget(lbl)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"background-color: transparent; color: {text}; border: 1px solid {border}; padding: 8px 16px; border-radius: 8px;")
        cancel_btn.clicked.connect(self.reject)
        
        del_btn = QPushButton("Delete")
        del_btn.setStyleSheet("background-color: #e57373; color: white; padding: 8px 16px; border-radius: 8px; border: none;")
        del_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(del_btn)
        inner.addLayout(btn_layout)
        
        layout.addWidget(self.widget)

# Add Assignment Widget
class AddAssignmentWidget(QWidget):
    assignment_added = Signal(dict)
    cancelled = Signal()
    settings_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_light = True
        layout = QVBoxLayout(self)
        
        lbl = QLabel("Create Assignment")
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(lbl)
        
        self.error_lbl = QLabel()
        self.error_lbl.setStyleSheet("color: red; font-weight: bold; margin-bottom: 10px;")
        self.error_lbl.hide()
        layout.addWidget(self.error_lbl)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Assignment Title")
        layout.addWidget(QLabel("Title <span style='color:red'>*</span>"))
        self.title_input.setStyleSheet("padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 8px;")
        layout.addWidget(self.title_input)
        
        layout.addWidget(QLabel("Description"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Description")
        self.description_input.setMaximumHeight(100)
        self.description_input.setStyleSheet("padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 8px;")
        layout.addWidget(self.description_input)
        
        # Date and Time Selection
        dt_layout = QHBoxLayout()
        
        d_layout = QVBoxLayout()
        d_layout.addWidget(QLabel("Date <span style='color:red'>*</span>"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDateTime.currentDateTime().date())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.date_edit.setStyleSheet("padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 8px;")
        d_layout.addWidget(self.date_edit)
        
        t_layout = QVBoxLayout()
        t_layout.addWidget(QLabel("Time <span style='color:red'>*</span>"))
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.time_edit.setStyleSheet("padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 8px;")
        t_layout.addWidget(self.time_edit)
        
        diff_layout = QVBoxLayout()
        diff_layout.addWidget(QLabel("Difficulty <span style='color:red'>*</span>"))
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Low", "Medium", "High"])
        diff_layout.addWidget(self.diff_combo)
        
        dt_layout.addLayout(d_layout)
        dt_layout.addLayout(t_layout)
        dt_layout.addLayout(diff_layout)
        layout.addLayout(dt_layout)
        
        # Attachments
        layout.addWidget(QLabel("Attachments"))
        self.attachments_list = QListWidget(self)
        self.attachments_list.setStyleSheet("border: 1px solid #ccc; border-radius: 8px;")
        self.attachments_list.setMaximumHeight(80)
        layout.addWidget(self.attachments_list)

        att_btn_layout = QHBoxLayout()
        self.browse_btn = QPushButton("Add Files")
        self.browse_btn.clicked.connect(self.add_attachments)
        att_btn_layout.addStretch()
        att_btn_layout.addWidget(self.browse_btn)
        layout.addLayout(att_btn_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Assignment")
        self.add_btn.setStyleSheet("""
            QPushButton { background-color: #ff9800; color: white; padding: 12px; border-radius: 8px; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background-color: #ffa726; }
        """)
        self.add_btn.clicked.connect(self.submit)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton { background-color: #f5f5f5; color: #333; padding: 12px; border-radius: 8px; font-size: 16px; }
            QPushButton:hover { background-color: #e0e0e0; }
        """)
        self.cancel_btn.clicked.connect(self.cancelled.emit)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.add_btn)
        layout.addLayout(btn_layout)

        self.load_settings()

    def load_settings(self):
        settings = QSettings("DeadlineX", "App")
        default_diff = settings.value("default_difficulty", "Low")
        self.diff_combo.setCurrentText(default_diff)

    def reset_form(self):
        self.title_input.clear()
        self.description_input.clear()
        self.date_edit.setDate(QDateTime.currentDateTime().date())
        self.time_edit.setTime(QTime.currentTime())
        self.attachments_list.clear()
        self.error_lbl.hide()
        self.load_settings()

    def add_attachments(self):
        fnames, _ = QFileDialog.getOpenFileNames(self, "Select Attachments")
        if fnames:
            self.add_attachment_paths(fnames)

    def add_attachment_paths(self, paths):
        for path in paths:
            if self.find_item_by_path(path):
                continue

            item = QListWidgetItem(self.attachments_list)
            item.setData(Qt.UserRole, path)
            item.setSizeHint(QSize(0, 30))

            widget = AttachmentItemWidget(path, item, self.is_light)
            widget.deleted.connect(self.remove_attachment_item)

            self.attachments_list.setItemWidget(item, widget)



    def find_item_by_path(self, path):
        for i in range(self.attachments_list.count()):
            item = self.attachments_list.item(i)
            if item.data(Qt.UserRole) == path:
                return item
        return None

    def remove_attachment_item(self, item):
        self.attachments_list.takeItem(self.attachments_list.row(item))

    def submit(self):
        title = self.title_input.text().strip()
        if not title:
            self.error_lbl.setText("Fields not entered")
            self.error_lbl.show()
            return
        self.error_lbl.hide()
        
        date = self.date_edit.date()
        time = self.time_edit.time()
        deadline = QDateTime(date, time)
        
        description = self.description_input.toPlainText()
        attachments = [self.attachments_list.item(i).data(Qt.UserRole) for i in range(self.attachments_list.count())]
        difficulty = self.diff_combo.currentText()
        
        self.assignment_added.emit({
            "title": title,
            "deadline": deadline,
            "completed": False,
            "description": description,
            "attachment": attachments or [],
            "difficulty": difficulty
        })
        self.title_input.clear()
        self.description_input.clear()
        self.attachments_list.clear()
        self.load_settings()

    def update_theme(self, is_light):
        self.is_light = is_light
        bg = "#ffffff" if is_light else "#333333"
        text = "#333333" if is_light else "#ffffff"
        border = "#ccc" if is_light else "#555"
        hover = "#e0e0e0" if is_light else "#444444"
        
        input_style = f"padding: 12px; font-size: 16px; border: 1px solid {border}; border-radius: 8px; background-color: {bg}; color: {text};"
        
        self.title_input.setStyleSheet(input_style)
        self.description_input.setStyleSheet(input_style)
        self.date_edit.setStyleSheet(input_style)
        self.time_edit.setStyleSheet(input_style)
        self.attachments_list.setStyleSheet(f"QListWidget {{ border: 1px solid {border}; border-radius: 8px; background-color: {bg}; color: {text}; }}")
        
        for i in range(self.attachments_list.count()):
            item = self.attachments_list.item(i)
            widget = self.attachments_list.itemWidget(item)
            if isinstance(widget, AttachmentItemWidget):
                widget.update_theme(is_light)
        
        combo_style = f"""
            QComboBox {{ 
                padding: 12px 15px; 
                font-size: 16px; 
                border: 2px solid {border}; 
                border-radius: 12px; 
                background-color: {bg}; 
                color: {text};
            }} 
            QComboBox:hover {{ 
                border: 2px solid #ff9800;
                background-color: {hover}; 
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 0px;
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {bg};
                color: {text};
                selection-background-color: #ff9800;
                selection-color: white;
                border: 1px solid {border};
                border-radius: 8px;
                outline: none;
                padding: 5px;
            }}
        """
        self.diff_combo.setStyleSheet(combo_style)
        
        btn_bg = "#e0e0e0" if is_light else "#444444"
        btn_fg = "#333" if is_light else "#ffffff"
        btn_hover = "#d0d0d0" if is_light else "#555555"
        btn_style = f"""
            QPushButton {{ background-color: {btn_bg}; color: {btn_fg}; padding: 12px; border-radius: 8px; font-size: 14px; }}
            QPushButton:hover {{ background-color: {btn_hover}; }}
        """
        self.browse_btn.setStyleSheet(btn_style)
        
        cancel_bg = "#f5f5f5" if is_light else "#444444"
        cancel_hover = "#e0e0e0" if is_light else "#555555"
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {cancel_bg}; color: {btn_fg}; padding: 12px; border-radius: 8px; font-size: 16px; }}
            QPushButton:hover {{ background-color: {cancel_hover}; }}
        """)

# Edit Assignment Widget
class EditAssignmentWidget(QWidget):
    saved = Signal()
    cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_light = True
        self.current_assignment = None
        layout = QVBoxLayout(self)
        
        lbl = QLabel("Edit Assignment")
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(lbl)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Assignment Title")
        layout.addWidget(QLabel("Title"))
        self.title_input.setStyleSheet("padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 8px;")
        layout.addWidget(self.title_input)
        
        layout.addWidget(QLabel("Description"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setStyleSheet("padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 8px;")
        layout.addWidget(self.description_input)
        
        dt_layout = QHBoxLayout()
        
        d_layout = QVBoxLayout()
        d_layout.addWidget(QLabel("Date"))
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.date_edit.setStyleSheet("padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 8px;")
        d_layout.addWidget(self.date_edit)
        
        t_layout = QVBoxLayout()
        t_layout.addWidget(QLabel("Time"))
        self.time_edit = QTimeEdit()
        self.time_edit.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.time_edit.setStyleSheet("padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 8px;")
        t_layout.addWidget(self.time_edit)
        
        diff_layout = QVBoxLayout()
        diff_layout.addWidget(QLabel("Difficulty"))
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Low", "Medium", "High"])
        self.diff_combo.setStyleSheet("QComboBox { padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 8px; background-color: white; selection-background-color: #ff9800; } QComboBox:hover { background-color: #e0e0e0; }")
        diff_layout.addWidget(self.diff_combo)
        
        dt_layout.addLayout(d_layout)
        dt_layout.addLayout(t_layout)
        dt_layout.addLayout(diff_layout)
        layout.addLayout(dt_layout)
        
        self.completed_cb = QCheckBox("Mark as Done")
        self.completed_cb.setStyleSheet("font-size: 16px; margin-top: 10px;")
        layout.addWidget(self.completed_cb)

        # Attachments
        layout.addWidget(QLabel("Attachments"))
        self.attachments_list = QListWidget(self)
        self.attachments_list.setStyleSheet("border: 1px solid #ccc; border-radius: 8px;")
        self.attachments_list.setMaximumHeight(80)
        self.attachments_list.itemDoubleClicked.connect(self.open_attachment)
        layout.addWidget(self.attachments_list)

        att_btn_layout = QHBoxLayout()
        self.browse_btn = QPushButton("Add Files")
        self.browse_btn.clicked.connect(self.add_attachments)
        att_btn_layout.addStretch()
        att_btn_layout.addWidget(self.browse_btn)
        layout.addLayout(att_btn_layout)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setStyleSheet("""
            QPushButton { background-color: #ff9800; color: white; padding: 12px; border-radius: 8px; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background-color: #ffa726; }
        """)
        self.save_btn.clicked.connect(self.save)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton { background-color: #f5f5f5; color: #333; padding: 12px; border-radius: 8px; font-size: 16px; }
            QPushButton:hover { background-color: #e0e0e0; }
        """)
        self.cancel_btn.clicked.connect(self.cancelled.emit)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def load_data(self, assignment):
        self.current_assignment = assignment
        self.title_input.setText(assignment.title)
        self.description_input.setText(assignment.description)
        self.date_edit.setDate(assignment.deadline.date())
        self.time_edit.setTime(assignment.deadline.time())
        self.diff_combo.setCurrentText(assignment.difficulty)
        self.completed_cb.setChecked(assignment.completed)
        self.attachments_list.clear()
        if assignment.attachment and isinstance(assignment.attachment, list):
            self.add_attachment_paths(assignment.attachment)

    def save(self):
        if self.current_assignment:
            self.current_assignment.title = self.title_input.text()
            self.current_assignment.description = self.description_input.toPlainText()
            self.current_assignment.deadline = QDateTime(self.date_edit.date(), self.time_edit.time())
            self.current_assignment.difficulty = self.diff_combo.currentText()
            self.current_assignment.completed = self.completed_cb.isChecked()
            attachments = [self.attachments_list.item(i).data(Qt.UserRole) for i in range(self.attachments_list.count())]
            self.current_assignment.attachment = attachments
            self.saved.emit()

    def open_attachment(self, item):
        filepath = item.data(Qt.UserRole)
        try:
            if sys.platform == "win32":
                os.startfile(filepath)
            elif sys.platform == "darwin":
                subprocess.run(["open", filepath], check=True)
            else: 
                subprocess.run(["xdg-open", filepath], check=True)
        except Exception as e:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText(f"Could not open file: {filepath}")
            msg_box.setInformativeText(str(e))
            msg_box.setWindowTitle("File Open Error")
            msg_box.exec()

    def add_attachments(self):
        fnames, _ = QFileDialog.getOpenFileNames(self, "Select Attachments")
        if fnames:
            self.add_attachment_paths(fnames)

    def add_attachment_paths(self, paths):
        for path in paths:
            if self.find_item_by_path(path): continue
            item = QListWidgetItem(self.attachments_list)
            item.setData(Qt.UserRole, path)
            item.setSizeHint(QSize(0, 30))
            widget = AttachmentItemWidget(path, item, self.is_light)
            widget.deleted.connect(self.remove_attachment_item)
            self.attachments_list.setItemWidget(item, widget)

    def find_item_by_path(self, path):
        for i in range(self.attachments_list.count()):
            if self.attachments_list.item(i).data(Qt.UserRole) == path:
                return self.attachments_list.item(i)
        return None
    def remove_attachment_item(self, item):
        self.attachments_list.takeItem(self.attachments_list.row(item))
    def update_theme(self, is_light):
        self.is_light = is_light
        bg = "#ffffff" if is_light else "#333333"
        text = "#333333" if is_light else "#ffffff"
        border = "#ccc" if is_light else "#555"
        hover = "#e0e0e0" if is_light else "#444444"
        
        input_style = f"padding: 12px; font-size: 16px; border: 1px solid {border}; border-radius: 8px; background-color: {bg}; color: {text};"
        
        self.title_input.setStyleSheet(input_style)
        self.description_input.setStyleSheet(input_style)
        self.date_edit.setStyleSheet(input_style)
        self.time_edit.setStyleSheet(input_style)
        self.attachments_list.setStyleSheet(f"QListWidget {{ border: 1px solid {border}; border-radius: 8px; background-color: {bg}; color: {text}; }}")
        
        for i in range(self.attachments_list.count()):
            item = self.attachments_list.item(i)
            widget = self.attachments_list.itemWidget(item)
            if isinstance(widget, AttachmentItemWidget):
                widget.update_theme(is_light)
        
        combo_style = f"""
            QComboBox {{ 
                padding: 12px; 
                font-size: 16px; 
                border: 1px solid {border}; 
                border-radius: 8px; 
                background-color: {bg}; 
                color: {text};
                selection-background-color: #ff9800; 
            }} 
            QComboBox:hover {{ 
                background-color: {hover}; 
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {bg};
                color: {text};
                selection-background-color: #ff9800;
                selection-color: white;
            }}
        """
        self.diff_combo.setStyleSheet(combo_style)
        
        cancel_bg = "#f5f5f5" if is_light else "#444444"
        btn_fg = "#333" if is_light else "#ffffff"
        cancel_hover = "#e0e0e0" if is_light else "#555555"
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {cancel_bg}; color: {btn_fg}; padding: 12px; border-radius: 8px; font-size: 16px; }}
            QPushButton:hover {{ background-color: {cancel_hover}; }}
        """)

        att_btn_style = f"""
            QPushButton {{ background-color: {cancel_bg}; color: {btn_fg}; padding: 8px 12px; border-radius: 8px; font-size: 14px; }}
            QPushButton:hover {{ background-color: {cancel_hover}; }}
        """
        self.browse_btn.setStyleSheet(att_btn_style)


# Chat Widget
class ChatWidget(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.worker = None
        self.setup_ui()
        self.configure_ai()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl = QLabel("DeadlineX AI Assistant")
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(lbl)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("border: none;")
        layout.addWidget(self.chat_display)

        self.thinking_widget = ThinkingWidget()
        self.thinking_widget.hide()
        layout.addWidget(self.thinking_widget)

        # Input Area
        self.input_container = QFrame()
        self.input_container.setObjectName("InputContainer")
        input_layout = QHBoxLayout(self.input_container)
        input_layout.setContentsMargins(10, 5, 10, 5)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask about your assignments...")
        self.input_field.setFrame(False)
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setStyleSheet("""
            QPushButton { background-color: #ff9800; color: white; padding: 8px 15px; border-radius: 15px; font-weight: bold; }
            QPushButton:hover { background-color: #ffa726; }
        """)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        layout.addWidget(self.input_container)
        self.update_theme(True)

    def configure_ai(self):
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            self.chat_display.append(f"<b>System:</b> Failed to initialize AI: {e}")

    def send_message(self):
        text = self.input_field.text().strip()
        if not text: return
        
        self.chat_display.append(f"<p style='color:#ff9800'><b>You:</b> {text}</p>")
        self.input_field.clear()
        
        self.thinking_widget.show()
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())
        
        # Prepare Data
        assignments = self.db.load_assignments()
        data_str = "\n".join([f"- {a.title} (Due: {a.deadline.toString('MMM d, yyyy h:mm ap')}, Difficulty: {a.difficulty}, Completed: {a.completed}, Desc: {a.description})" for a in assignments])
        current_time = QDateTime.currentDateTime().toString("MMM d, yyyy h:mm ap")
        prompt = f"System: You are DeadlineX AI. Answer all questions strictly related to the assignment. Dont use markdown. The current date and time is {current_time}. When asked who you are or which AI, answer 'DeadlineX AI'. Use the following assignment data to answer the user's question.\nData:\n{data_str}\n\nUser: {text}"

        # Start Worker
        self.worker = AIWorker(self.client, prompt)
        self.worker.finished.connect(self.on_ai_response)
        self.worker.error.connect(self.on_ai_error)
        self.worker.start()

    def on_ai_response(self, text):
        self.thinking_widget.hide()
        self.chat_display.append(f"<p style='color:#4caf50'><b>DeadlineX AI:</b> {text}</p>")
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def on_ai_error(self, error_msg):
        self.thinking_widget.hide()
        self.chat_display.append(f"<p style='color:red'><b>Error:</b> {error_msg}</p>")

    def update_theme(self, is_light):
        bg = "#ffffff" if is_light else "#333333"
        text = "#333333" if is_light else "#ffffff"
        border = "#ccc" if is_light else "#555"
        
        self.chat_display.setStyleSheet(f"background-color: {bg}; color: {text}; border: 1px solid {border}; border-radius: 5px; padding: 10px;")
        self.input_field.setStyleSheet(f"color: {text};")
        self.thinking_widget.set_theme(is_light)
        
        if is_light:
            self.input_container.setStyleSheet("QFrame#InputContainer { background: #fff; border: 1px solid #ccc; border-radius: 25px; }")
            self.input_field.setStyleSheet("color: #333; background: transparent; border: none;")
        else:
            self.input_container.setStyleSheet("QFrame#InputContainer { background: #424242; border: 1px solid #555; border-radius: 25px; }")
            self.input_field.setStyleSheet("color: #fff; background: transparent; border: none;")

# Calendar Page
class CalendarPage(QWidget):
    assignment_clicked = Signal(object)
    assignment_deleted = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nav_filters = {}
        self.assignments = []
        self.current_date = QDateTime.currentDateTime().date()
        self.is_light = True
        
        layout = QVBoxLayout(self)
        
        # Custom Calendar Header (Prev | Month Year | Next)
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(10, 0, 10, 10)
        
        self.prev_btn = QToolButton()
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.clicked.connect(lambda: self.calendar.showPreviousMonth())
        
        self.month_lbl = QLabel()
        self.month_lbl.setAlignment(Qt.AlignCenter)
        self.month_lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.next_btn = QToolButton()
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.clicked.connect(lambda: self.calendar.showNextMonth())
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.month_lbl, 1)
        nav_layout.addWidget(self.next_btn)
        layout.addLayout(nav_layout)
        
        # Calendar
        self.calendar = QCalendarWidget()
        self.calendar.setNavigationBarVisible(False) 
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_selected)
        self.calendar.currentPageChanged.connect(self.update_header)
        layout.addWidget(self.calendar)
        
        # Selected Date Label
        self.date_label = QLabel(self.current_date.toString("MMMM d, yyyy"))
        self.date_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.date_label)
        
        # Assignments List Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)
        
        # Initialize Header
        self.update_header(self.calendar.yearShown(), self.calendar.monthShown())
        
        self.update_theme(True)

    def update_header(self, year, month):
        d = QDate(year, month, 1)
        self.month_lbl.setText(d.toString("MMMM yyyy"))

    def set_assignments(self, assignments):
        self.assignments = assignments
        self.highlight_dates()
        self.on_date_selected(self.calendar.selectedDate())

    def highlight_dates(self):
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        dates = set()
        for a in self.assignments:
            if not a.completed:
                dates.add(a.deadline.date())
        
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold)
        fmt.setForeground(QColor("#ff9800"))
        fmt.setFontUnderline(True)
        
        for date in dates:
            self.calendar.setDateTextFormat(date, fmt)

    def on_date_selected(self, date):
        self.current_date = date
        self.date_label.setText(date.toString("MMMM d, yyyy"))
        
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        daily_assignments = [a for a in self.assignments if a.deadline.date() == date and not a.completed]
        
        if not daily_assignments:
            lbl = QLabel("No assignments due on this day.")
            lbl.setStyleSheet("color: #888; font-style: italic; margin: 10px;")
            self.container_layout.addWidget(lbl)
        else:
            for a in daily_assignments:
                w = AssignmentWidget(a)
                w.clicked.connect(self.assignment_clicked.emit)
                w.deleted.connect(self.assignment_deleted.emit)
                w.update_theme(self.is_light)
                self.container_layout.addWidget(w)

    def update_theme(self, is_light):
        self.is_light = is_light
        bg = "#ffffff" if is_light else "#333333"
        text = "#333333" if is_light else "#ffffff"
        
        cal_bg = "#ffffff" if is_light else "#424242"
        cal_text = "#000000" if is_light else "#ffffff"
        nav_color = "#333" if is_light else "#fff"
        
        self.month_lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {text};")
        
        self.calendar.setStyleSheet(f"""
            QCalendarWidget {{ border-radius: 15px; background-color: {cal_bg}; }}
            QCalendarWidget QWidget {{ alternate-background-color: {cal_bg}; background-color: {cal_bg}; color: {cal_text}; border-radius: 15px; }}
            QCalendarWidget QMenu {{ background-color: {cal_bg}; color: {cal_text}; }}
            QCalendarWidget QSpinBox {{ color: {cal_text}; background-color: {cal_bg}; selection-background-color: #ff9800; }}
            QCalendarWidget QAbstractItemView:enabled {{ color: {cal_text}; background-color: {cal_bg}; selection-background-color: #ff9800; selection-color: white; }}
        """)
        
        icon_color = "#333" if is_light else "#fff"
        
        # Custom Nav Buttons
        for btn, svg in [(self.prev_btn, SVG_CHEVRON_LEFT), (self.next_btn, SVG_CHEVRON_RIGHT)]:
            if btn in self.nav_filters:
                btn.removeEventFilter(self.nav_filters[btn])
            self.nav_filters[btn] = IconHoverFilter(btn, svg, icon_color, "#ff9800")
            btn.installEventFilter(self.nav_filters[btn])
            btn.setStyleSheet("background: transparent; border: none;")
        
        self.date_label.setStyleSheet(f"font-size: 18px; font-weight: bold; margin-top: 10px; color: {text};")
        
        for i in range(self.container_layout.count()):
            w = self.container_layout.itemAt(i).widget()
            if isinstance(w, AssignmentWidget):
                w.update_theme(is_light)
            elif isinstance(w, QLabel):
                w.setStyleSheet("color: #888; font-style: italic; margin: 10px;")

# Focus Widget
class FocusWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("DeadlineX", "App")
        self.focus_dur = int(self.settings.value("focus_min", 25)) * 60
        self.short_dur = int(self.settings.value("short_break_min", 5)) * 60
        self.long_dur = int(self.settings.value("long_break_min", 15)) * 60
        
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        sound_path = resource_path("alert.mp3")
        if os.path.exists(sound_path):
            self.player.setSource(QUrl.fromLocalFile(sound_path))
            self.audio_output.setVolume(1.0)
        
        self.seconds_left = self.focus_dur
        self.is_running = False
        self.mode = "Focus"  
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        
        self.setup_ui()
        self.update_theme(True)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)

        self.lbl_mode = QLabel("Focus Time")
        self.lbl_mode.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_mode)

        m, s = divmod(self.seconds_left, 60)
        self.lbl_timer = QLabel(f"{m:02d}:{s:02d}")
        self.lbl_timer.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_timer)

        # Controls
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        self.btn_start = QPushButton("Start")
        self.btn_start.setFixedSize(120, 50)
        self.btn_start.clicked.connect(self.toggle_timer)
        
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setFixedSize(120, 50)
        self.btn_reset.clicked.connect(self.reset_timer)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Modes
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(10)
        
        self.btn_focus = QPushButton(f"Focus ({self.focus_dur//60}m)")
        self.btn_short = QPushButton(f"Short Break ({self.short_dur//60}m)")
        self.btn_long = QPushButton(f"Long Break ({self.long_dur//60}m)")
        
        self.btn_focus.clicked.connect(lambda: self.set_mode(self.focus_dur, "Focus"))
        self.btn_short.clicked.connect(lambda: self.set_mode(self.short_dur, "Short Break"))
        self.btn_long.clicked.connect(lambda: self.set_mode(self.long_dur, "Long Break"))

        for btn in [self.btn_focus, self.btn_short, self.btn_long]:
            btn.setCursor(Qt.PointingHandCursor)
            mode_layout.addWidget(btn)
            
        layout.addLayout(mode_layout)

    def refresh_settings(self):
        self.focus_dur = int(self.settings.value("focus_min", 25)) * 60
        self.short_dur = int(self.settings.value("short_break_min", 5)) * 60
        self.long_dur = int(self.settings.value("long_break_min", 15)) * 60
        
        self.btn_focus.setText(f"Focus ({self.focus_dur//60}m)")
        self.btn_short.setText(f"Short Break ({self.short_dur//60}m)")
        self.btn_long.setText(f"Long Break ({self.long_dur//60}m)")
        
        if self.mode == "Focus":
            self.seconds_left = self.focus_dur
        elif self.mode == "Short Break":
            self.seconds_left = self.short_dur
        elif self.mode == "Long Break":
            self.seconds_left = self.long_dur
        self.update_display()

    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.btn_start.setText("Resume")
        else:
            self.timer.start(1000)
            self.btn_start.setText("Pause")
        self.is_running = not self.is_running

    def tick(self):
        if self.seconds_left > 0:
            self.seconds_left -= 1
            self.update_display()
        else:
            self.timer.stop()
            self.is_running = False
            self.btn_start.setText("Start")
            QApplication.beep()
            self.player.play()

    def update_display(self):
        m, s = divmod(self.seconds_left, 60)
        self.lbl_timer.setText(f"{m:02d}:{s:02d}")

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.btn_start.setText("Start")
        if self.mode == "Focus": self.seconds_left = self.focus_dur
        elif self.mode == "Short Break": self.seconds_left = self.short_dur
        elif self.mode == "Long Break": self.seconds_left = self.long_dur
        self.update_display()

    def set_mode(self, seconds, mode):
        self.mode = mode
        self.lbl_mode.setText(f"{mode} Time")
        self.seconds_left = seconds
        self.reset_timer()

    def update_theme(self, is_light):
        text = "#333333" if is_light else "#ffffff"
        timer_color = "#ff9800"
        
        self.lbl_mode.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {text};")
        self.lbl_timer.setStyleSheet(f"font-size: 96px; font-weight: bold; color: {timer_color};")
        
        btn_style = f"""
            QPushButton {{ background-color: #ff9800; color: white; border-radius: 25px; font-size: 18px; font-weight: bold; }}
            QPushButton:hover {{ background-color: #ffa726; }}
        """
        self.btn_start.setStyleSheet(btn_style)
        
        reset_bg = "#e0e0e0" if is_light else "#555555"
        reset_fg = "#333" if is_light else "#fff"
        self.btn_reset.setStyleSheet(f"""
            QPushButton {{ background-color: {reset_bg}; color: {reset_fg}; border-radius: 25px; font-size: 18px; }}
            QPushButton:hover {{ background-color: #d0d0d0; }}
        """)
        
        mode_bg = "transparent"
        mode_fg = "#2196F3"
        mode_border = "#2196F3"
        
        mode_style = f"""
            QPushButton {{ background-color: {mode_bg}; color: {mode_fg}; border: 1px solid {mode_border}; border-radius: 15px; padding: 8px 16px; font-size: 14px; }}
            QPushButton:hover {{ background-color: rgba(33, 150, 243, 0.1); }}
        """
        self.btn_focus.setStyleSheet(mode_style)
        self.btn_short.setStyleSheet(mode_style)
        self.btn_long.setStyleSheet(mode_style)

# Settings Widget
class SettingsWidget(QWidget):
    settings_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("DeadlineX", "App")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        
        self.lbl_title = QLabel("Settings")
        layout.addWidget(self.lbl_title)
        
        # Default Difficulty
        self.lbl_diff = QLabel("Default Difficulty")
        layout.addWidget(self.lbl_diff)
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Low", "Medium", "High"])
        self.diff_combo.setCurrentText(self.settings.value("default_difficulty", "Low"))
        layout.addWidget(self.diff_combo)
        
        # Timer Durations
        self.lbl_focus = QLabel("Focus Duration (minutes)")
        layout.addWidget(self.lbl_focus)
        self.focus_spin = QLineEdit(str(self.settings.value("focus_min", 25)))
        layout.addWidget(self.focus_spin)
        
        self.lbl_short = QLabel("Short Break Duration (minutes)")
        layout.addWidget(self.lbl_short)
        self.short_spin = QLineEdit(str(self.settings.value("short_break_min", 5)))
        layout.addWidget(self.short_spin)
        
        self.lbl_long = QLabel("Long Break Duration (minutes)")
        layout.addWidget(self.lbl_long)
        self.long_spin = QLineEdit(str(self.settings.value("long_break_min", 15)))
        layout.addWidget(self.long_spin)
        
        layout.addStretch()
        
        self.msg_lbl = QLabel("Settings saved successfully!")
        self.msg_lbl.setAlignment(Qt.AlignCenter)
        self.msg_lbl.hide()
        layout.addWidget(self.msg_lbl)

        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)
        
        self.update_theme(True)

    def save_settings(self):
        self.settings.setValue("default_difficulty", self.diff_combo.currentText())
        
        try:
            f = int(self.focus_spin.text())
            s = int(self.short_spin.text())
            l = int(self.long_spin.text())
            self.settings.setValue("focus_min", f)
            self.settings.setValue("short_break_min", s)
            self.settings.setValue("long_break_min", l)
        except ValueError:
            pass 
            
        self.settings_changed.emit()
        self.msg_lbl.show()
        QTimer.singleShot(3000, self.msg_lbl.hide)

    def update_theme(self, is_light):
        bg = "#ffffff" if is_light else "#333333"
        text = "#333333" if is_light else "#ffffff"
        input_bg = "#ffffff" if is_light else "#424242"
        input_border = "#ccc" if is_light else "#555"
        
        self.lbl_title.setStyleSheet(f"font-size: 24px; font-weight: bold; margin-bottom: 20px; color: {text};")
        
        label_style = f"color: {text}; font-size: 14px; margin-top: 10px;"
        self.lbl_diff.setStyleSheet(label_style)
        self.lbl_focus.setStyleSheet(label_style)
        self.lbl_short.setStyleSheet(label_style)
        self.lbl_long.setStyleSheet(label_style)
        
        input_style = f"padding: 10px; border: 1px solid {input_border}; border-radius: 5px; background-color: {input_bg}; color: {text}; font-size: 14px;"
        self.focus_spin.setStyleSheet(input_style)
        self.short_spin.setStyleSheet(input_style)
        self.long_spin.setStyleSheet(input_style)
        
        combo_style = f"""
            QComboBox {{ padding: 10px; border: 1px solid {input_border}; border-radius: 5px; background-color: {input_bg}; color: {text}; font-size: 14px; }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{ background-color: {input_bg}; color: {text}; selection-background-color: #ff9800; }}
        """
        self.diff_combo.setStyleSheet(combo_style)
        
        self.save_btn.setStyleSheet("background-color: #ff9800; color: white; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 16px;")
        self.msg_lbl.setStyleSheet("color: #4CAF50; font-weight: bold; margin-top: 10px; font-size: 14px;")

# MainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # ---------------- Notifications ----------------
        self.notified_ids = set()
        self.setup_tray_icon()
        self.notification_timer = QTimer(self)
        self.notification_timer.timeout.connect(self.check_deadlines)
        self.notification_timer.start(60000) # Check every minute
        
        self.settings = QSettings("DeadlineX", "App")
        self.is_light = self.settings.value("theme", "light") == "light"
        self.view_mode = "Upcoming" # Upcoming or Completed
        self.setWindowTitle("DeadlineX")
        self.setGeometry(100,100,1200,700)
        self.setStyleSheet("background-color:#ffffff;color:#333333;\n" + SCROLLBAR_STYLESHEET)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout()
        central.setLayout(layout)

        # ---------------- Sidebar ----------------
        sidebar_layout = QVBoxLayout()
        self.home_btn = SvgButton("Home", SVG_HOME)
        self.task_btn = SvgButton("Assignments", SVG_TASK)
        self.chat_btn = SvgButton("DeadlineX AI", SVG_CHAT)
        self.cal_btn = SvgButton("Calendar", SVG_CALENDAR)
        self.timer_btn = SvgButton("Focus Timer", SVG_TIMER)
        
        self.home_btn.btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.task_btn.btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.chat_btn.btn.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        self.cal_btn.btn.clicked.connect(lambda: self.stack.setCurrentIndex(5))
        self.timer_btn.btn.clicked.connect(lambda: self.stack.setCurrentIndex(6))
        
        self.home_btn.set_theme(self.is_light)
        self.task_btn.set_theme(self.is_light)
        self.chat_btn.set_theme(self.is_light)
        self.cal_btn.set_theme(self.is_light)
        self.timer_btn.set_theme(self.is_light)
        
        sidebar_layout.addWidget(self.home_btn)
        sidebar_layout.addWidget(self.task_btn)
        sidebar_layout.addWidget(self.chat_btn)
        sidebar_layout.addWidget(self.cal_btn)
        sidebar_layout.addWidget(self.timer_btn)
        sidebar_layout.addStretch()

        # Theme Toggle
        self.theme_svg = ClickableSvgWidget()
        self.theme_svg.load(bytearray(SVG_MOON,'utf-8'))
        self.theme_svg.setFixedSize(32,32)
        self.theme_svg.setStyleSheet("""
            QSvgWidget { border-radius: 16px; background-color: transparent; }
            QSvgWidget:hover { background-color: #e0e0e0; }
        """)
        self.theme_svg.clicked.connect(self.toggle_theme)

        # Settings Icon
        self.settings_icon = ClickableSvgWidget()
        self.settings_icon.setFixedSize(32,32)
        self.settings_icon.setToolTip("Settings")
        self.settings_icon.clicked.connect(lambda: self.stack.setCurrentIndex(7))

        bottom_bar = QWidget()
        bottom_layout = QVBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(0, 10, 0, 10)
        bottom_layout.setSpacing(15)
        bottom_layout.addWidget(self.theme_svg)
        bottom_layout.addWidget(self.settings_icon)
        sidebar_layout.addWidget(bottom_bar)

        self.sidebar_widget = QWidget()
        self.sidebar_widget.setLayout(sidebar_layout)
        self.sidebar_widget.setFixedWidth(200)
        self.sidebar_widget.setStyleSheet("background-color:#f0f0f0;")
        layout.addWidget(self.sidebar_widget)

        # ---------------- Main Area ----------------
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        self.dashboard = Dashboard()
        self.stack.addWidget(self.dashboard)
        self.dashboard.assignment_clicked.connect(self.open_editor)
        self.dashboard.assignment_deleted.connect(self.delete_assignment)

        # ---------------- Assignments Page ----------------
        self.assignments_page = QWidget()
        self.assignments_layout = QVBoxLayout(self.assignments_page)
        
        # Header with Filter
        header_layout = QHBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search assignments...")
        self.search_bar.setStyleSheet("QLineEdit { padding: 8px; border: 1px solid #ccc; border-radius: 15px; font-size: 14px; }")
        self.search_bar.textChanged.connect(self.filter_assignments_by_search)
        header_layout.addWidget(self.search_bar)
        
        header_layout.addStretch()
        
        self.filter_btn = ClickableSvgWidget()
        self.filter_btn.load(bytearray(SVG_FILTER.replace('<svg ', '<svg fill="#333333" '), 'utf-8'))
        self.filter_btn.setFixedSize(24, 24)
        self.filter_btn.setStyleSheet("""
            QSvgWidget { border-radius: 4px; background-color: transparent; }
            QSvgWidget:hover { background-color: #e0e0e0; }
        """)
        self.filter_btn.clicked.connect(self.show_filter_menu)
        header_layout.addWidget(self.filter_btn)
        self.assignments_layout.addLayout(header_layout)
        
        # View Toggles
        toggle_layout = QHBoxLayout()
        self.btn_upcoming = QPushButton("Upcoming")
        self.btn_completed = QPushButton("Completed")
        self.btn_upcoming.clicked.connect(lambda: self.set_view_mode("Upcoming"))
        self.btn_completed.clicked.connect(lambda: self.set_view_mode("Completed"))
        toggle_layout.addWidget(self.btn_upcoming)
        toggle_layout.addWidget(self.btn_completed)
        
        self.btn_clear_completed = QPushButton("Clear All Completed")
        self.btn_clear_completed.setStyleSheet("background-color: #e57373; color: white; border-radius: 15px; padding: 8px; font-weight: bold;")
        self.btn_clear_completed.clicked.connect(self.clear_all_completed)
        self.btn_clear_completed.hide()
        toggle_layout.addWidget(self.btn_clear_completed)
        self.assignments_layout.addLayout(toggle_layout)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;\n" + SCROLLBAR_STYLESHEET)
        self.assignments_container = QWidget()
        self.assignments_list_layout = QVBoxLayout(self.assignments_container)
        self.assignments_list_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.assignments_container)
        self.assignments_layout.addWidget(self.scroll_area)
        
        self.stack.addWidget(self.assignments_page)

        # ---------------- Create Assignment Page ----------------
        self.create_page = QWidget()
        self.create_layout = QVBoxLayout(self.create_page)
        self.create_layout.setContentsMargins(50, 50, 50, 50)
        
        self.add_widget = AddAssignmentWidget()
        self.add_widget.assignment_added.connect(self.add_new_assignment)
        self.add_widget.cancelled.connect(lambda: self.stack.setCurrentIndex(1))
        self.create_layout.addWidget(self.add_widget)
        
        self.stack.addWidget(self.create_page)
        
        # ---------------- Edit Assignment Page ----------------
        self.edit_page = QWidget()
        self.edit_layout = QVBoxLayout(self.edit_page)
        self.edit_layout.setContentsMargins(50, 50, 50, 50)
        self.edit_widget = EditAssignmentWidget()
        self.edit_widget.saved.connect(self.on_assignment_saved)
        self.edit_widget.cancelled.connect(lambda: self.stack.setCurrentIndex(1))
        self.edit_layout.addWidget(self.edit_widget)
        self.stack.addWidget(self.edit_page)

        # ---------------- Chat Page ----------------
        self.db = DatabaseManager()
        self.chat_page = ChatWidget(self.db)
        self.stack.addWidget(self.chat_page)
        
        # ---------------- Calendar Page ----------------
        self.calendar_page = CalendarPage()
        self.calendar_page.assignment_clicked.connect(self.open_editor)
        self.calendar_page.assignment_deleted.connect(self.delete_assignment)
        self.stack.addWidget(self.calendar_page)
        
        # ---------------- Timer Page ----------------
        self.timer_page = FocusWidget()
        self.stack.addWidget(self.timer_page)
        
        # ---------------- Settings Page ----------------
        self.settings_page = SettingsWidget()
        self.settings_page.settings_changed.connect(self.timer_page.refresh_settings)
        self.settings_page.settings_changed.connect(self.add_widget.load_settings)
        self.stack.addWidget(self.settings_page)

        # Database
        self.assignments = self.db.load_assignments()

        # ---------------- FAB ----------------
        self.fab = QPushButton("+", self)
        self.fab.setFixedSize(60, 60)
        self.fab.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border-radius: 30px;
                font-size: 30px;
                padding-bottom: 5px;
            }
            QPushButton:hover { background-color: #ffa726; }
            QPushButton:pressed { background-color: #f57c00; }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.fab.setGraphicsEffect(shadow)
        self.fab.clicked.connect(self.open_create_page)
        self.fab.raise_()
        
        self.update_view_buttons()
        self.stack.currentChanged.connect(self.on_page_changed)
        
        self.apply_theme()
        self.refresh_data()

    def open_create_page(self):
        self.add_widget.reset_form()
        self.stack.setCurrentIndex(2)

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        renderer = QSvgRenderer(bytearray(SVG_TASK, 'utf-8'))
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.show()

    def check_deadlines(self):
        now = QDateTime.currentDateTime()
        for assignment in self.assignments:
            if assignment.completed:
                continue
            
            secs_to_deadline = now.secsTo(assignment.deadline)
            
            if 3540 <= secs_to_deadline <= 3660:
                if assignment.id not in self.notified_ids:
                    self.send_notification(assignment)
                    self.notified_ids.add(assignment.id)

    def send_notification(self, assignment):
        title = "Deadline Approaching"
        message = f"'{assignment.title}' is due in 1 hour!"
        
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 5000)
        
        if sys.platform == 'darwin':
            safe_title = title.replace('"', '\\"')
            safe_message = message.replace('"', '\\"')
            script = f'display notification "{safe_message}" with title "{safe_title}" sound name "default"'
            try:
                subprocess.run(["osascript", "-e", script], check=False)
            except Exception as e:
                print(f"Failed to send Mac notification: {e}")

    def resizeEvent(self, event):
        self.fab.move(self.width() - 90, self.height() - 90)
        super().resizeEvent(event)

    def on_page_changed(self, index):
        if index == 2:
            self.fab.hide()
        elif index == 3: # Edit page
            self.fab.hide()
        elif index == 4: # Chat page
            self.fab.hide()
        elif index == 5: # Calendar
            self.fab.hide()
        elif index == 6: # Timer
            self.fab.hide()
        elif index == 7: # Settings
            self.fab.hide()
        else:
            self.fab.show()

    def set_view_mode(self, mode):
        self.view_mode = mode
        self.update_view_buttons()
        if mode == "Completed":
            self.btn_clear_completed.show()
        else:
            self.btn_clear_completed.hide()
        self.render_assignments_list()

    def update_view_buttons(self):
        active_style = "background-color: #ff9800; color: white; border-radius: 15px; padding: 8px; font-weight: bold;"
        inactive_style = "background-color: transparent; color: #888; border: 1px solid #ccc; border-radius: 15px; padding: 8px;"
        
        if self.view_mode == "Upcoming":
            self.btn_upcoming.setStyleSheet(active_style)
            self.btn_completed.setStyleSheet(inactive_style)
        else:
            self.btn_upcoming.setStyleSheet(inactive_style)
            self.btn_completed.setStyleSheet(active_style)

    def refresh_data(self):
        self.assignments = self.db.load_assignments()
        self.dashboard.update_dashboard(self.assignments)
        self.calendar_page.set_assignments(self.assignments)
        self.render_assignments_list()

    def add_new_assignment(self, data):
        assignment = Assignment(**data)
        self.db.add_assignment(assignment)
        self.assignments.append(assignment)
        self.render_assignments_list()
        self.dashboard.update_dashboard(self.assignments)
        self.calendar_page.set_assignments(self.assignments)
        self.stack.setCurrentIndex(1)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _filter_assignments(self):
        search_text = self.search_bar.text().lower()
        
        for assignment in self.assignments:
            if self.view_mode == "Upcoming" and assignment.completed:
                continue
            if self.view_mode == "Completed" and not assignment.completed:
                continue
            
            if search_text and not (search_text in assignment.title.lower() or search_text in (assignment.description or "").lower()):
                continue
            
            yield assignment

    def render_assignments_list(self):
        self._clear_layout(self.assignments_list_layout)
        
        for assignment in self._filter_assignments():
            widget = AssignmentWidget(assignment)
            widget.deleted.connect(self.delete_assignment)
            widget.completed.connect(self.on_assignment_completed)
            widget.clicked.connect(self.open_editor)
            widget.update_theme(self.is_light)
            self.assignments_list_layout.addWidget(widget)

    def open_editor(self, assignment):
        self.edit_widget.load_data(assignment)
        self.stack.setCurrentIndex(3)

    def on_assignment_saved(self):
        self.db.update_assignment(self.edit_widget.current_assignment)
        self.render_assignments_list()
        self.dashboard.update_dashboard(self.assignments)
        self.calendar_page.set_assignments(self.assignments)
        self.stack.setCurrentIndex(1)

    def on_assignment_completed(self, assignment, state):
        self.db.update_assignment(assignment)
        self.dashboard.update_dashboard(self.assignments)
        self.calendar_page.set_assignments(self.assignments)
        self.render_assignments_list()

    def filter_assignments_by_search(self, text):
        self.render_assignments_list()

    def show_filter_menu(self):
        menu = QMenu(self)
        
        bg = "#e0e0e0" if self.is_light else "#555555"
        fg = "#000000" if self.is_light else "#ffffff"
        menu_bg = "#ffffff" if self.is_light else "#333333"
        menu_border = "#ccc" if self.is_light else "#555"
        menu_text = "#333333" if self.is_light else "#ffffff"
        
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {menu_bg};
                border: 1px solid {menu_border};
                border-radius: 15px;
                padding: 8px;
            }}
            QMenu::item {{
                padding: 10px 25px;
                border-radius: 10px;
                margin: 2px 5px;
                color: {menu_text};
            }}
            QMenu::item:selected {{
                background-color: {bg};
                color: {fg};
            }}
        """)
        
        action_deadline = QAction("Sort by Deadline", self)
        action_difficulty = QAction("Sort by Difficulty", self)
        
        action_deadline.triggered.connect(lambda: self.sort_assignments("deadline"))
        action_difficulty.triggered.connect(lambda: self.sort_assignments("difficulty"))
        
        menu.addAction(action_deadline)
        menu.addAction(action_difficulty)
        
        menu.exec(self.filter_btn.mapToGlobal(QPoint(0, self.filter_btn.height())))

    def sort_assignments(self, criteria):
        if criteria == "deadline":
            self.assignments.sort(key=lambda x: x.deadline)
        elif criteria == "difficulty":
            diff_map = {"Easy": 1, "Low": 1, "Medium": 2, "Hard": 3, "High": 3}
            self.assignments.sort(key=lambda x: (diff_map.get(x.difficulty, 0), x.deadline))
        self.render_assignments_list()

    def delete_assignment(self, assignment):
        dialog = DeletePopup(assignment.title, self.is_light, self)
        if dialog.exec() != QDialog.Accepted:
            return
        
        if assignment in self.assignments:
            self.db.delete_assignment(assignment.id)
            self.assignments.remove(assignment)
        self.render_assignments_list()
        self.dashboard.update_dashboard(self.assignments)
        self.calendar_page.set_assignments(self.assignments)

    def clear_all_completed(self):
        dialog = DeletePopup("All Completed Assignments", self.is_light, self)
        if dialog.exec() != QDialog.Accepted:
            return

        to_remove = [a for a in self.assignments if a.completed]
        for a in to_remove:
            self.db.delete_assignment(a.id)
            self.assignments.remove(a)
        
        self.render_assignments_list()
        self.dashboard.update_dashboard(self.assignments)
        self.calendar_page.set_assignments(self.assignments)

    def toggle_theme(self):
        self.is_light = not self.is_light
        self.apply_theme()

    def apply_theme(self):
        self.settings.setValue("theme", "light" if self.is_light else "dark")
        if self.is_light:
            bg, fg, side_bg, icon = "#ffffff", "#333333", "#f0f0f0", SVG_MOON
            icon_color = "#333333"
            extra = ""
        else:
            bg, fg, side_bg, icon = "#212121", "#ffffff", "#2c2c2c", SVG_SUN
            icon_color = "#ffffff"
            extra = "QLineEdit, QTextEdit, QDateTimeEdit, QComboBox, QMenu { color: #ffffff; background-color: #333333; border: 1px solid #555; }"
        
        self.setStyleSheet(f"background-color:{bg};color:{fg};\n{extra}\n" + SCROLLBAR_STYLESHEET)
        self.sidebar_widget.setStyleSheet(f"background-color:{side_bg};")
        self.dashboard.update_theme(self.is_light)
        self.add_widget.update_theme(self.is_light)
        self.edit_widget.update_theme(self.is_light)
        self.chat_page.update_theme(self.is_light)
        self.calendar_page.update_theme(self.is_light)
        
        for i in range(self.assignments_list_layout.count()):
            w = self.assignments_list_layout.itemAt(i).widget()
            if isinstance(w, AssignmentWidget):
                w.update_theme(self.is_light)
        
        self.home_btn.set_theme(self.is_light)
        self.task_btn.set_theme(self.is_light)
        self.chat_btn.set_theme(self.is_light)
        self.cal_btn.set_theme(self.is_light)
        self.timer_btn.set_theme(self.is_light)
        
        colored_icon = icon.replace('<svg ', f'<svg fill="{icon_color}" ')
        self.theme_svg.load(bytearray(colored_icon, 'utf-8'))
        icon_hover = "#e0e0e0" if self.is_light else "#3c3c3c"
        self.theme_svg.setStyleSheet(f"""
            QSvgWidget {{ border-radius: 16px; background-color: transparent; }}
            QSvgWidget:hover {{ background-color: {icon_hover}; }}
        """)
        
        colored_settings = SVG_SETTINGS.replace('<svg ', f'<svg fill="{icon_color}" ')
        self.settings_icon.load(bytearray(colored_settings, 'utf-8'))
        self.settings_icon.setStyleSheet(f"""
            QSvgWidget {{ border-radius: 16px; background-color: transparent; padding: 4px; }}
            QSvgWidget:hover {{ background-color: {icon_hover}; }}
        """)
        
        colored_filter = SVG_FILTER.replace('<svg ', f'<svg fill="{icon_color}" ')
        self.filter_btn.load(bytearray(colored_filter, 'utf-8'))
        self.filter_btn.setStyleSheet(f"""
            QSvgWidget {{ border-radius: 4px; background-color: transparent; }}
            QSvgWidget:hover {{ background-color: {icon_hover}; }}
        """)
        
        sb_bg = "#ffffff" if self.is_light else "#333333"
        sb_fg = "#333333" if self.is_light else "#ffffff"
        sb_border = "#ccc" if self.is_light else "#555"
        self.search_bar.setStyleSheet(f"QLineEdit {{ padding: 8px; border: 1px solid {sb_border}; border-radius: 15px; font-size: 14px; background-color: {sb_bg}; color: {sb_fg}; }}")
        self.timer_page.update_theme(self.is_light)
        self.settings_page.update_theme(self.is_light)

# Run App
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName("Phantom")
    app.setApplicationName("DeadlineX")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
