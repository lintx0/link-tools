#-- coding:UTF-8 --
# Author:lintx
# Date:2025/02/10
import sys,os
from PyQt5.QtCore import Qt,QSettings
from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox
from tabs.ui_main import Ui_Form
from tabs import tab_zz,tab_rolan,tab_ai


class MyMainForm(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        # -------------------------------------------功能加载-------------------------------------------------
        #正则
        self.tab_zz = tab_zz.tab_zz(self)
        # Rolan
        self.tab_rolan = tab_rolan.tab_rolan(self)
        # Ai
        self.tab_ai = tab_ai.tab_ai(self)

        #tab数据加载
        self.tabs_button.clicked.connect(self.tabs_save)
        tabs_names = [self.tabWidget.tabText(i) for i in range(self.tabWidget.count())]
        self.tabs_combox.addItems(tabs_names)
        tabs_settings = QSettings("link_tools", "AI")
        tabs_cname = tabs_settings.value("tabs_cname", "Rolan+")
        self.tabs_combox.setCurrentText(tabs_cname)
        self.tabWidget.setCurrentIndex(self.tabs_combox.currentIndex())
        try:
            self.tabread()
            self.tabWidget.currentChanged.connect(self.tabread)
        except Exception as e:
            QMessageBox.about(self, "错误", f"配置文件缺失，请检查config目录{e}")
            exit()

        #self.rolan_list_4.setVisible(False)

    # -------------------------------------------数据读取-------------------------------------------------
    def tabread(self):
        os.chdir(pwd)
        tabs_text=self.tabWidget.tabText(self.tabWidget.currentIndex())
        if tabs_text=='正则':
            self.tab_zz.zhengze_list()
        elif tabs_text == 'Rolan+':
            if self.tab_rolan.ui.rolan_list_1.count() ==0:
                self.tab_rolan.read_data('')
    def tabs_save(self):
        tabs_settings = QSettings("link_tools", "AI")
        tabs_cname = self.tabs_combox.currentText()
        tabs_settings.setValue("tabs_cname",tabs_cname)
        QMessageBox.information(self, "提示", "配置保存成功！")

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    pwd = os.getcwd()
    myWin = MyMainForm()
    myWin.show()
    sys.exit(app.exec_())