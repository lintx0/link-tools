#-- coding:UTF-8 --
# Author:lintx
# Date:2025/02/20
import re,json,time,requests
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QSettings
from PyQt5.QtWidgets import QMessageBox, QInputDialog
from PyQt5.QtGui import QTextCursor
from openai import OpenAI

class Worker(QThread):
    # AI调用模块，实现会话功能
    response_received = pyqtSignal(str, bool)
    error_occurred = pyqtSignal(str)

    def __init__(self, config, prompt, user_input,user_input_1):
        super().__init__()
        self.config = config
        self.prompt = prompt.replace("[输入1]", user_input).replace("[输入2]", user_input_1)
        self._is_running = True

    def run(self):
        try:
            if self.config.get('api_key'):
                self.call_openai_api()
            else:
                self.call_ollama()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self._is_running = False
        self.terminate()

    def call_openai_api(self):
        try:
            client = OpenAI(
                api_key=self.config["api_key"],
                base_url=self.config["api_base"],
                timeout=my_timeout
            )
            stream = client.chat.completions.create(
                model=self.config["model"],
                messages=[{"role": "user", "content": self.prompt}],
                stream=True
            )
            for chunk in stream:
                if not self._is_running:
                    break
                content = chunk.choices[0].delta.content or ""
                self.response_received.emit(content, False)

            self.response_received.emit('\n\n', True)
        except Exception as e:
            self.error_occurred.emit(f"API请求失败: {str(e)}")

    def call_ollama(self):
        data = {
            "model": self.config["model"],
            "prompt": self.prompt,
            "stream": True
        }

        try:
            with requests.post(
                self.config["api_base"],
                json=data,
                stream=True,
                timeout=my_timeout
            ) as response:
                response.raise_for_status()
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if not self._is_running:
                            break
                        if line:
                            try:
                                chunk = json.loads(line)
                                delta = chunk.get("response", "")
                                self.response_received.emit(delta, False)
                            except Exception as e:
                                print(e)
                                continue

                    self.response_received.emit('', True)

        except Exception as e:
            self.error_occurred.emit(f"Ollama连接失败: {str(e)}")

class tab_ai():
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.prompts = {}
        self.thinking_start = None
        self.configs = {}
        self.init_ui()
        self.load_prompts()
        self.load_configs()

    def init_ui(self):
        self.is_running = False
        self.ui.send_btn.clicked.connect(self.toggle_ai_process)
        self.ui.prompt_combo.currentTextChanged.connect(self.update_prompt)
        self.ui.prompt_combo_1.currentTextChanged.connect(self.update_prompt_1)
        self.ui.refresh_btn.clicked.connect(self.load_prompts)
        self.ui.new_btn.clicked.connect(self.new_prompt)
        self.ui.delete_btn.clicked.connect(self.delete_prompt)
        self.ui.save_prompt_btn.clicked.connect(self.save_prompt)
        self.ui.prompt_edit.textChanged.connect(self.hide_input)
        self.ui.input_edit.textChanged.connect(self.input_size)
        self.ui.input_edit_1.textChanged.connect(self.input_size_1)
        self.ui.config_combo.currentTextChanged.connect(self.update_config)
        self.ui.config_combo_1.currentTextChanged.connect(self.update_config_1)
        self.ui.new_config_btn.clicked.connect(self.new_config)
        self.ui.save_config_btn.clicked.connect(self.save_config)
        self.ui.del_config_btn.clicked.connect(self.del_config)
        self.ui.refresh_btn_2.clicked.connect(self.refresh_config)
        self.ui.config_combo.currentIndexChanged.connect(self.load_config)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)

    # 交互功能实现
    def input_size(self):
        size=len(self.ui.input_edit.toPlainText())
        self.ui.label_input1.setText(f'[输入1]  {size} tokens')
    def input_size_1(self):
        size=len(self.ui.input_edit_1.toPlainText())
        self.ui.label_input2.setText(f'[输入2]  {size} tokens')

    def toggle_ai_process(self):
        if self.is_running:
            self.handle_interrupt()
        else:
            self.on_send()

    def hide_input(self):
        text = self.ui.prompt_edit.toPlainText()
        if '[输入1]' in text:
            self.ui.input_edit.setEnabled(True)
        else:
            self.ui.input_edit.setEnabled(False)
        if '[输入2]' in text:
            self.ui.input_edit_1.setEnabled(True)
        else:
            self.ui.input_edit_1.setEnabled(False)

    def handle_interrupt(self):
        if hasattr(self, 'worker'):
            self.worker.stop()
        self.cleanup_after_interrupt()
        self.ui.output_area.append("=== 用户中止 ===")

    def cleanup_after_interrupt(self):
        self.timer.stop()
        self.ui.send_btn.setText("AI分析和处理")
        self.ui.send_btn.setStyleSheet("")
        self.is_running = False
        self.thinking_start = None

    def update_time(self):
        if self.thinking_start:
            elapsed = time.time() - self.thinking_start
            self.ui.send_btn.setText(f"中止（{elapsed:.2f}s）")

    def handle_error(self, error_msg):
        self.timer.stop()
        self.ui.output_area.append(f"\n[错误] {error_msg}")
        self.ui.send_btn.setEnabled(True)
        self.thinking_start = None
        self.ui.send_btn.setText("AI分析和处理")
        self.ui.send_btn.setStyleSheet("")
        self.is_running = False

    def update_response(self, delta, finished):
        try:
            if not self.is_running:
                return
            processed = delta.replace('<think>', '[思考]').replace('</think>', '[/思考]')
            self.ui.output_area.moveCursor(QTextCursor.End)
            self.ui.output_area.insertPlainText(processed)

            if finished:
                self.cleanup_after_interrupt()
                self.ui.output_area.append("=== 回答结束 ===")
                self.ui.output_area.moveCursor(QTextCursor.End)
        except Exception as e:
            print(e)

    def on_send(self):
        global my_timeout
        my_timeout = int(self.ui.timeout_input.text())

        if self.ui.input_edit.toPlainText() == '' and self.ui.input_edit.isEnabled() == True:
            QMessageBox.critical(self.ui, "错误", f"输入框1，未输入数据")
            return
        if self.ui.input_edit_1.toPlainText() == '' and self.ui.input_edit_1.isEnabled() == True:
            QMessageBox.critical(self.ui, "错误", f"输入框2，未输入数据")
            return
        if self.is_running:  # 如果正在运行则执行中止
            self.handle_interrupt()
            return

        self.is_running = True
        self.ui.send_btn.setText("中止（0.00s）")
        self.ui.send_btn.setStyleSheet("background-color: grey;")
        prompt = self.ui.prompt_edit.toPlainText()
        size_emit = int(self.ui.size_emit.text())
        user_input = self.ui.input_edit.toPlainText().strip()[:size_emit]
        user_input_1 = self.ui.input_edit_1.toPlainText().strip()[:size_emit]
        if not prompt or not user_input:
            return

        self.ui.output_area.clear()
        self.thinking_start = time.time()
        self.timer.start(100)

        self.config = {
            "name": self.ui.config_combo.currentText(),
                "api_base": self.ui.conf_api_base.text(),
                "api_key": self.ui.conf_api_key.text(),
                "model": self.ui.conf_model.text()
            }

        self.worker = Worker(self.config, prompt, user_input,user_input_1)
        self.worker.response_received.connect(self.update_response)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

        prompt_combo = self.ui.prompt_combo_1.currentText()
        model_combo = self.ui.config_combo.currentText()
        self.ui.output_area.append(f"[运行参数] Timeout：{my_timeout} | Size：{size_emit} | Prompt：{prompt_combo} | Model：{model_combo}\n")

    # 提示词功能实现
    def load_prompts(self):
        try:
            with open("config/提示词.md", "r", encoding="utf-8") as f:
                content = f.read()
            pattern = r"### (.*?)```(.*?)```"
            matches = re.findall(pattern, content, re.DOTALL)
            self.prompts = {title.strip(): prompt.strip() for title, prompt in matches}
            self.ui.prompt_combo.clear()
            self.ui.prompt_combo.addItems(self.prompts.keys())
            if self.prompts:
                self.ui.prompt_combo.setCurrentIndex(0)
            self.ui.prompt_combo_1.clear()
            self.ui.prompt_combo_1.addItems(self.prompts.keys())
            if self.prompts:
                self.ui.prompt_combo_1.setCurrentIndex(0)
        except Exception as e:
            print(e)
            QMessageBox.critical(self.ui, "错误", f"加载提示词失败: {str(e)}")

    def update_prompt(self):
        title = self.ui.prompt_combo.currentText()
        self.ui.prompt_edit.setPlainText(self.prompts.get(title, ""))
        self.ui.prompt_combo_1.setCurrentText(title)

    def update_prompt_1(self):
        title = self.ui.prompt_combo_1.currentText()
        self.ui.prompt_edit.setPlainText(self.prompts.get(title, ""))
        self.ui.prompt_combo.setCurrentText(title)

    def update_config(self):
        title = self.ui.config_combo.currentText()
        self.ui.config_combo_1.setCurrentText(title)

    def update_config_1(self):
        title = self.ui.config_combo_1.currentText()
        self.ui.config_combo.setCurrentText(title)

    def new_prompt(self):
        title, ok = QInputDialog.getText(self.ui, "新增提示词", "请输入提示词标题:")
        if ok and title:
            content, ok = QInputDialog.getMultiLineText(self.ui, "新增提示词", "请输入提示词内容:")
            if ok and content:
                self.prompts[title] = content
                self.save_prompts_to_file()
                self.load_prompts()
                self.ui.prompt_combo.setCurrentText(title)

    def delete_prompt(self):
        current_title = self.ui.prompt_combo.currentText()
        if not current_title:
            return
        confirm = QMessageBox.question(
            self.ui,
            "确认删除",
            f"确定要删除提示词【{current_title}】吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            del self.prompts[current_title]
            self.save_prompts_to_file()
            self.load_prompts()

    def save_prompt(self):
        current_title = self.ui.prompt_combo.currentText()
        new_content = self.ui.prompt_edit.toPlainText()
        if current_title and new_content:
            self.prompts[current_title] = new_content
            self.save_prompts_to_file()
            QMessageBox.information(self.ui, "提示", "提示词保存成功！")

    def save_prompts_to_file(self):
        try:
            content = ""
            for title, prompt in self.prompts.items():
                content += f"### {title}\n```\n{prompt}\n```\n\n"
            with open("config/提示词.md", "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(e)
            QMessageBox.critical(self.ui, "错误", f"保存提示词失败: {str(e)}")

    #AI配置功能实现
    def load_configs(self, preserve_selection=None):
        settings = QSettings("config/config_ai.ini", QSettings.IniFormat)
        self.configs = {}

        sections = settings.childGroups()
        for section in sections:
            settings.beginGroup(section)
            self.configs[section] = {
                "api_base": settings.value("api_base", ""),
                "api_key": settings.value("api_key", ""),
                "model": settings.value("model", "")
            }
            settings.endGroup()

        if not self.configs:
            self.ui.config_combo.clear()
            self.ui.config_combo_1.clear()
            return

        current_index = self.ui.config_combo.currentIndex()
        self.ui.config_combo.clear()
        self.ui.config_combo.addItems(self.configs.keys())
        self.ui.config_combo_1.clear()
        self.ui.config_combo_1.addItems(self.configs.keys())
        if preserve_selection:
            new_index = self.ui.config_combo.findText(preserve_selection)
            self.ui.config_combo.setCurrentIndex(new_index if new_index != -1 else 0)
        elif current_index >= 0:
            self.ui.config_combo.setCurrentIndex(min(current_index, self.ui.config_combo.count() - 1))

    def save_configs(self):
        settings = QSettings("config/config_ai.ini", QSettings.IniFormat)
        # 清空旧配置
        settings.clear()
        for name, config in self.configs.items():
            settings.beginGroup(name)
            settings.setValue("api_base", config["api_base"])
            settings.setValue("api_key", config["api_key"])
            settings.setValue("model", config["model"])
            settings.endGroup()

    def new_config(self):
        name, ok = QInputDialog.getText(self.ui, "新建配置", "配置名称:")
        if ok and name:
            self.configs[name] = {
                "api_base": "http://localhost:11434/api/generate",
                "api_key": "",
                "model": "deepseek-r1:1.5b"
            }
            self.save_configs()
            self.load_configs()
            self.ui.config_combo.setCurrentText(name)

    def save_config(self):
        name = self.ui.config_combo.currentText()  # 改为从下拉框获取名称
        if name:
            # 保存前记录当前选中项
            current_name = self.ui.config_combo.currentText()

            self.configs[name] = {
                "api_base": self.ui.conf_api_base.text(),
                "api_key": self.ui.conf_api_key.text(),
                "model": self.ui.conf_model.text()
            }
            self.save_configs()

            # 重新加载时保持选中状态
            self.load_configs(preserve_selection=current_name)
            QMessageBox.information(self.ui, "成功", "配置保存成功！")

    def del_config(self):
        name = self.ui.config_combo.currentText()
        if name in self.configs:
            # 确认对话框
            reply = QMessageBox.question(
                self.ui,
                "确认删除",
                f"确定要删除配置 【{name}】 吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                del self.configs[name]
                self.save_configs()
                self.refresh_config()

    def refresh_config(self):
        self.ui.config_combo.setCurrentIndex(0)
        self.ui.config_combo_1.setCurrentIndex(0)
        self.ui.conf_api_base.setText('')
        self.ui.conf_api_key.setText('')
        self.ui.conf_model.setText('')
        self.load_configs()

    def load_config(self):
        name = self.ui.config_combo.currentText()
        if name in self.configs:
            config = self.configs[name]
            self.ui.conf_api_base.setText(config["api_base"])
            self.ui.conf_api_key.setText(config["api_key"])
            self.ui.conf_model.setText(config["model"])