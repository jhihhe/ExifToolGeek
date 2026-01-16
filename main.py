import sys
import json
import subprocess
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QFileDialog, QListWidget, QListWidgetItem, QSplitter, QMessageBox,
                             QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QMimeData, QSize, QTimer
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QColor, QPalette, QFont, QIcon

# Translations
TRANSLATIONS = {
    'en': {
        'title': 'ExifGeek // Metadata Transporter',
        'source_title': 'SOURCE IMAGE',
        'target_title': 'TARGET IMAGE(S)',
        'drop_src': 'Drag Source Image Here\n(or click to select)',
        'drop_tgt': 'Drag Target Files Here\n(or click to select)',
        'src_placeholder': 'Source metadata will appear here...',
        'inject_btn': '>>> INJECT METADATA >>>',
        'clear_btn': 'CLEAR ALL',
        'ready': 'Ready',
        'processing': 'Processing...',
        'completed': 'Completed: {}/{} files processed.',
        'task_complete': 'Task Complete',
        'success_msg': 'Successfully injected metadata into {} files.',
        'select_file': 'Select File',
        'select_files': 'Select Files',
        'copy_exif': 'COPY',
        'save_exif': 'EXPORT TXT'
    },
    'zh': {
        'title': 'ExifGeek // 元数据传输器',
        'source_title': '源图片',
        'target_title': '目标图片',
        'drop_src': '拖拽源图片到这里\n(或点击选择)',
        'drop_tgt': '拖拽目标文件到这里\n(或点击选择)',
        'src_placeholder': '源图片元数据将显示在这里...',
        'inject_btn': '>>> 注入元数据 >>>',
        'clear_btn': '清空所有',
        'ready': '就绪',
        'processing': '处理中...',
        'completed': '完成: {}/{} 个文件已处理',
        'task_complete': '任务完成',
        'success_msg': '成功将元数据注入到 {} 个文件',
        'select_file': '选择文件',
        'select_files': '选择文件',
        'copy_exif': '复制',
        'save_exif': '导出 TXT'
    }
}

# Dracula Theme Colors
DRACULA = {
    'bg': '#282a36',
    'curr_line': '#44475a',
    'fg': '#f8f8f2',
    'comment': '#6272a4',
    'cyan': '#8be9fd',
    'green': '#50fa7b',
    'orange': '#ffb86c',
    'pink': '#ff79c6',
    'purple': '#bd93f9',
    'red': '#ff5555',
    'yellow': '#f1fa8c'
}

STYLESHEET = f"""
QMainWindow {{
    background-color: {DRACULA['bg']};
}}
QWidget {{
    color: {DRACULA['fg']};
    font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
    font-size: 12px;
}}
QTextEdit {{
    background-color: {DRACULA['curr_line']};
    color: {DRACULA['green']};
    border: 1px solid {DRACULA['purple']};
    border-radius: 5px;
    padding: 10px;
}}
QListWidget {{
    background-color: {DRACULA['curr_line']};
    color: {DRACULA['cyan']};
    border: 1px solid {DRACULA['comment']};
    border-radius: 5px;
}}
QPushButton {{
    background-color: {DRACULA['purple']};
    color: {DRACULA['bg']};
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {DRACULA['pink']};
}}
QPushButton:pressed {{
    background-color: {DRACULA['cyan']};
}}
QLabel#Title {{
    font-size: 18px;
    font-weight: bold;
    color: {DRACULA['purple']};
}}
QFrame#DropZone {{
    border: 2px dashed {DRACULA['comment']};
    border-radius: 10px;
    background-color: rgba(68, 71, 90, 0.5);
}}
QFrame#DropZone:hover {{
    border-color: {DRACULA['green']};
    background-color: rgba(68, 71, 90, 0.8);
}}
"""

class ExifTool:
    @staticmethod
    def get_cmd_prefix():
        # Check for bundled resource in py2app
        if 'RESOURCEPATH' in os.environ:
            bundled_path = os.path.join(os.environ['RESOURCEPATH'], 'exiftool_src', 'exiftool')
            if os.path.exists(bundled_path):
                return ['perl', bundled_path]
        return ['exiftool']

    @staticmethod
    def get_metadata(path):
        try:
            # Check if exiftool is available
            cmd = ExifTool.get_cmd_prefix() + ['-j', path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data[0] if data else {}
            return {"Error": "Failed to read metadata"}
        except FileNotFoundError:
            return {"Error": "exiftool not found in PATH"}
        except Exception as e:
            return {"Error": str(e)}

    @staticmethod
    def copy_metadata(src, dest):
        try:
            # -overwrite_original avoids creating _original backup files
            cmd = ExifTool.get_cmd_prefix() + ['-TagsFromFile', src, '-all:all', '-overwrite_original', dest]
            subprocess.run(cmd, check=True, capture_output=True)
            return True, "Success"
        except subprocess.CalledProcessError as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)

class DropZone(QFrame):
    def __init__(self, parent_win, is_multiple=False, text_key=''):
        super().__init__()
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.parent_win = parent_win
        self.is_multiple = is_multiple
        self.text_key = text_key
        
        layout = QVBoxLayout()
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(f"color: {DRACULA['comment']}; font-size: 14px;")
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.update_text()
        
    def update_text(self, filename=None):
        if filename:
            self.label.setText(filename)
        else:
            self.label.setText(self.parent_win.tr(self.text_key))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_multiple:
                title = self.parent_win.tr('select_files')
                files, _ = QFileDialog.getOpenFileNames(self, title)
                if files:
                    self.parent_win.handle_tgt_drop(files)
            else:
                title = self.parent_win.tr('select_file')
                file, _ = QFileDialog.getOpenFileName(self, title)
                if file:
                    self.parent_win.handle_src_drop([file])

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            if self.is_multiple:
                self.parent_win.handle_tgt_drop(files)
            else:
                self.parent_win.handle_src_drop(files)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.curr_lang = 'zh'
        self.setWindowTitle("ExifGeek")
        self.resize(1000, 700)
        
        # Apply Stylesheet
        self.setStyleSheet(STYLESHEET)
        
        # Enable Transparency/Blur effect (Mocking transparency for now)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.98) 
        
        # Main Layout
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {DRACULA['bg']}; border-radius: 10px;")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        self.btn_lang_zh = QPushButton("中文")
        self.btn_lang_en = QPushButton("English")
        self.btn_lang_zh.setFixedWidth(60)
        self.btn_lang_en.setFixedWidth(80)
        self.btn_lang_zh.clicked.connect(lambda: self.change_language('zh'))
        self.btn_lang_en.clicked.connect(lambda: self.change_language('en'))
        header_layout.addWidget(self.btn_lang_zh)
        header_layout.addWidget(self.btn_lang_en)
        
        self.header_label = QLabel()
        self.header_label.setObjectName("Title")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.header_label)
        
        main_layout.addLayout(header_layout)
        
        # Splitter for Source and Target
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- Source Section ---
        src_widget = QWidget()
        src_layout = QVBoxLayout(src_widget)
        
        self.src_label_title = QLabel()
        self.src_label_title.setStyleSheet(f"color: {DRACULA['pink']}; font-weight: bold;")
        src_layout.addWidget(self.src_label_title)
        
        self.src_drop = DropZone(self, is_multiple=False, text_key='drop_src')
        self.src_drop.setFixedHeight(100)
        src_layout.addWidget(self.src_drop)
        
        self.btn_copy_src = QPushButton()
        self.btn_copy_src.setMinimumHeight(32)
        self.btn_copy_src.setMinimumWidth(80)
        self.btn_copy_src.clicked.connect(self.copy_src_info)
        
        self.btn_save_src = QPushButton()
        self.btn_save_src.setMinimumHeight(32)
        self.btn_save_src.setMinimumWidth(100)
        self.btn_save_src.clicked.connect(self.save_src_info)
        
        copy_style = f"""
            QPushButton {{
                background-color: {DRACULA['cyan']};
                color: {DRACULA['bg']};
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 14px;
            }}
            QPushButton:hover {{
                background-color: {DRACULA['fg']};
                color: {DRACULA['bg']};
            }}
            QPushButton:pressed {{
                background-color: {DRACULA['pink']};
                color: {DRACULA['bg']};
            }}
        """
        save_style = f"""
            QPushButton {{
                background-color: {DRACULA['orange']};
                color: {DRACULA['bg']};
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 14px;
            }}
            QPushButton:hover {{
                background-color: {DRACULA['yellow']};
                color: {DRACULA['bg']};
            }}
            QPushButton:pressed {{
                background-color: {DRACULA['pink']};
                color: {DRACULA['bg']};
            }}
        """
        self.btn_copy_src.setStyleSheet(copy_style)
        self.btn_save_src.setStyleSheet(save_style)

        self.src_info = QTextEdit()
        self.src_info.setReadOnly(True)
        src_layout.addWidget(self.src_info)
        
        self.src_path = None
        
        splitter.addWidget(src_widget)
        
        # --- Target Section ---
        tgt_widget = QWidget()
        tgt_layout = QVBoxLayout(tgt_widget)
        
        self.tgt_label_title = QLabel()
        self.tgt_label_title.setStyleSheet(f"color: {DRACULA['cyan']}; font-weight: bold;")
        tgt_layout.addWidget(self.tgt_label_title)
        
        self.tgt_drop = DropZone(self, is_multiple=True, text_key='drop_tgt')
        self.tgt_drop.setFixedHeight(100)
        tgt_layout.addWidget(self.tgt_drop)
        
        self.tgt_list = QListWidget()
        tgt_layout.addWidget(self.tgt_list)
        
        splitter.addWidget(tgt_widget)
        
        main_layout.addWidget(splitter)
        
        # Actions
        action_layout = QHBoxLayout()
        
        self.btn_copy = QPushButton()
        self.btn_copy.clicked.connect(self.run_injection)
        self.btn_copy.setEnabled(False)
        self.btn_copy.setMinimumHeight(40)
        self.btn_copy.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.btn_copy.setStyleSheet(f"""
            QPushButton {{
                background-color: {DRACULA['green']};
                color: {DRACULA['bg']};
                font-size: 16px;
                padding: 15px;
            }}
            QPushButton:disabled {{
                background-color: {DRACULA['curr_line']};
                color: {DRACULA['comment']};
            }}
        """)
        
        self.btn_clear = QPushButton()
        self.btn_clear.setMinimumHeight(32)
        self.btn_clear.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.btn_clear.setStyleSheet(f"""
            QPushButton {{
                background-color: {DRACULA['red']};
                color: {DRACULA['bg']};
                font-size: 14px;
                padding: 10px 15px;
            }}
        """)
        self.btn_clear.clicked.connect(self.clear_all)
        
        left_actions_widget = QWidget()
        left_actions_layout = QVBoxLayout(left_actions_widget)
        left_actions_layout.setContentsMargins(0, 0, 0, 0)
        left_actions_layout.setSpacing(6)
        
        top_src_actions = QHBoxLayout()
        top_src_actions.setSpacing(6)
        top_src_actions.addWidget(self.btn_copy_src)
        top_src_actions.addWidget(self.btn_save_src)
        
        left_actions_layout.addLayout(top_src_actions)
        left_actions_layout.addWidget(self.btn_clear)
        
        left_actions_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        action_layout.addWidget(left_actions_widget)
        action_layout.addWidget(self.btn_copy)
        action_layout.setSpacing(12)
        action_layout.setStretchFactor(left_actions_widget, 1)
        action_layout.setStretchFactor(self.btn_copy, 1)
        
        main_layout.addLayout(action_layout)
        
        # Status Bar
        self.status_label = QLabel()
        self.status_label.setStyleSheet(f"color: {DRACULA['comment']};")
        main_layout.addWidget(self.status_label)
        
        # Initialize Text
        self.update_ui_text()

    def tr(self, key):
        return TRANSLATIONS[self.curr_lang].get(key, key)

    def change_language(self, lang):
        self.curr_lang = lang
        self.update_ui_text()

    def update_lang_buttons(self):
        active = f"background-color: {DRACULA['green']}; color: {DRACULA['bg']}; padding: 4px 10px; border-radius: 4px;"
        inactive = f"background-color: {DRACULA['curr_line']}; color: {DRACULA['comment']}; padding: 4px 10px; border-radius: 4px;"
        if self.curr_lang == 'zh':
            self.btn_lang_zh.setStyleSheet(active)
            self.btn_lang_en.setStyleSheet(inactive)
        else:
            self.btn_lang_zh.setStyleSheet(inactive)
            self.btn_lang_en.setStyleSheet(active)

    def update_ui_text(self):
        self.header_label.setText(self.tr('title'))
        self.src_label_title.setText(self.tr('source_title'))
        self.tgt_label_title.setText(self.tr('target_title'))
        self.src_info.setPlaceholderText(self.tr('src_placeholder'))
        self.btn_copy.setText(self.tr('inject_btn'))
        self.btn_clear.setText(self.tr('clear_btn'))
        self.btn_copy_src.setText(self.tr('copy_exif'))
        self.btn_save_src.setText(self.tr('save_exif'))
        self.update_lang_buttons()
        
        # Update DropZones if they don't have files
        if not self.src_path:
            self.src_drop.update_text()
        self.tgt_drop.update_text()
        
        if not self.src_path and self.tgt_list.count() == 0:
            self.status_label.setText(self.tr('ready'))

    def handle_src_drop(self, files):
        if not files: return
        self.src_path = files[0]
        self.src_drop.update_text(os.path.basename(self.src_path))
        
        # Get Metadata
        meta = ExifTool.get_metadata(self.src_path)
        self.current_meta = meta # Store for copy/save
        
        html = self.format_exif_html(meta)
        self.src_info.setHtml(html)
        self.check_ready()

    def format_exif_html(self, data):
        html = f'<div style="font-family: monospace; line-height: 1.4;">'
        html += f'<span style="color: {DRACULA["fg"]}">{{</span><br>'
        
        key_colors = [DRACULA["pink"], DRACULA["cyan"], DRACULA["orange"], DRACULA["green"], DRACULA["purple"]]
        value_cycle = [DRACULA["yellow"], DRACULA["fg"], DRACULA["green"]]
        idx = 0
        
        for key, value in data.items():
            val_str = str(value).replace('<', '&lt;').replace('>', '&gt;')
            key_color = key_colors[idx % len(key_colors)]
            if isinstance(value, (int, float)):
                val_color = DRACULA["cyan"]
            elif isinstance(value, (list, dict)):
                val_color = DRACULA["orange"]
                val_str = json.dumps(value, ensure_ascii=False)
            else:
                val_color = value_cycle[idx % len(value_cycle)]
            html += f'&nbsp;&nbsp;<span style="color: {key_color}">{key}</span>: '
            html += f'<span style="color: {val_color}">{val_str}</span><span style="color: {DRACULA["fg"]}">,</span><br>'
            idx += 1
            
        html += f'<span style="color: {DRACULA["fg"]}">}}</span>'
        html += "</div>"
        return html

    def copy_src_info(self):
        if hasattr(self, 'current_meta') and self.current_meta:
            clipboard = QApplication.clipboard()
            clipboard.setText(json.dumps(self.current_meta, indent=2))
            
    def save_src_info(self):
        if hasattr(self, 'current_meta') and self.current_meta:
            fname, _ = QFileDialog.getSaveFileName(self, self.tr('save_exif'), "exif.txt")
            if fname:
                try:
                    with open(fname, 'w', encoding='utf-8') as f:
                        f.write(json.dumps(self.current_meta, indent=2, ensure_ascii=False))
                except Exception as e:
                    print(f"Error saving: {e}")

    def handle_tgt_drop(self, files):
        for f in files:
            # Check if directory
            if os.path.isdir(f):
                for root, dirs, filenames in os.walk(f):
                    for name in filenames:
                        if not name.startswith('.'): # Ignore hidden files
                            self.add_target_item(os.path.join(root, name))
            else:
                self.add_target_item(f)
        self.check_ready()

    def format_path_html(self, path):
        directory, filename = os.path.split(path)
        name, ext = os.path.splitext(filename)
        parts = ['<div style="font-family: monospace;">']
        if directory:
            parts.append(f'<span style="color:{DRACULA["comment"]}">{directory}/</span>')
        if name:
            parts.append(f'<span style="color:{DRACULA["green"]}">{name}</span>')
        if ext:
            parts.append(f'<span style="color:{DRACULA["purple"]}">{ext}</span>')
        parts.append('</div>')
        return ''.join(parts)

    def add_target_item(self, path):
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, path)
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 0, 4, 0)
        label = QLabel()
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setText(self.format_path_html(path))
        layout.addWidget(label)
        item.setSizeHint(widget.sizeHint())
        self.tgt_list.addItem(item)
        self.tgt_list.setItemWidget(item, widget)

    def check_ready(self):
        if self.src_path and self.tgt_list.count() > 0:
            self.btn_copy.setEnabled(True)
        else:
            self.btn_copy.setEnabled(False)

    def clear_all(self):
        self.src_path = None
        self.src_drop.update_text() # Reset to default text
        self.src_info.clear()
        self.tgt_list.clear()
        self.btn_copy.setEnabled(False)
        self.status_label.setText(self.tr('ready'))

    def run_injection(self):
        if not self.src_path: return
        
        count = self.tgt_list.count()
        success_count = 0
        
        self.status_label.setText(self.tr('processing'))
        QApplication.processEvents()
        
        for i in range(count):
            item = self.tgt_list.item(i)
            dest_path = item.data(Qt.ItemDataRole.UserRole) or item.text()
            ok, msg = ExifTool.copy_metadata(self.src_path, dest_path)
            if ok:
                success_count += 1
            else:
                print(f"Failed for {dest_path}: {msg}")
                
        self.status_label.setText(self.tr('completed').format(success_count, count))
        QMessageBox.information(self, self.tr('task_complete'), self.tr('success_msg').format(success_count))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
