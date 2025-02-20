#-- coding:UTF-8 --
# Author:lintx
# Date:2025/01/07 11:00
import re
from PyQt5.QtWidgets import QApplication,QMessageBox

class tab_zz():
    def __init__(self, ui):
        self.__dict__.update(ui.__dict__)
        self.ui=ui
        self.pushButton.clicked.connect(self.display)
        self.pushButton1.clicked.connect(self.pipei)
        self.pushButton2.clicked.connect(self.copy)
        self.pushButton3.clicked.connect(self.copy1)
        self.pushButton3_2.clicked.connect(self.add1)
        self.pushButton3_3.clicked.connect(self.add2)
        self.pushButton3_4.clicked.connect(self.minus)
        self.pushButton3_5.clicked.connect(self.tihuan)
        self.pushButton3_6.clicked.connect(self.quchong)
        self.comboBox.currentIndexChanged.connect(self.zhengze0)
        self.comboBox_2.currentIndexChanged.connect(self.zhengze0)
    # ---------------------------------------------正则---------------------------------------------------
    def copy(self):
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.textBrowser.toPlainText())
            QMessageBox.about(self.ui, "提示", "复制表达式成功")
        except Exception as e:
            print(e)
    def copy1(self):
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.textBrowser1.toPlainText())
            QMessageBox.about(self.ui, "提示", "复制结果成功")
        except Exception as e:
            print(e)
    def display(self):
        begin = self.lineEdit1.text()
        end = self.lineEdit2.text()
        #转义
        begins = []
        ends=[]
        for i in begin:
            if i in "[-\/^$*+?.()|[\]{}]":
                begins.append("\\")
            begins.append(i)
        begin = "".join(begins)
        for b in end:
            if b in "[-\/^$*+?.()|[\]{}]":
                ends.append("\\")
            ends.append(b)
        end = "".join(ends)
        #数据处理
        if begin=='' or end=='':
            self.textBrowser.setText("请输入开始和结束关键字")
        elif self.checkBox1.isChecked()and self.checkBox2.isChecked()and self.checkBox3.isChecked()and self.checkBox4.isChecked():
            self.textBrowser.setPlainText(begin + "(.+?)"+end)
        elif self.checkBox1.isChecked()and self.checkBox2.isChecked()and self.checkBox3.isChecked():
            self.textBrowser.setText(begin + "(.+?)(?="+end+")")
        elif self.checkBox1.isChecked()and self.checkBox3.isChecked()and self.checkBox4.isChecked():
            self.textBrowser.setText("(?<="+begin+")(.+?)"+end)
        elif self.checkBox1.isChecked()and self.checkBox3.isChecked():
            self.textBrowser.setText("(?<="+begin+")(.+?)(?="+end+")")
        else:
            self.textBrowser.setText("自动生成报错，请重新勾选")
    def pipei(self):
        try:
            self.textBrowser1.setText("")
            text = self.textEdit.toPlainText()
            test = self.textBrowser.toPlainText()
            result=re.finditer(test,text)
            result0 = []
            for i in result:
                result0.append(i[0])
            self.textBrowser1.setPlainText('\n'.join(result0))
        except:
            self.textBrowser1.setText("匹配失败，请重试")
        if self.textBrowser1.toPlainText()=='':
            self.textBrowser1.setText("未匹配到语句，请重试")
    def zhengze0(self):
        item = self.comboBox.currentText()
        item1=self.comboBox_2.currentText()
        with open('config/正则.txt','r',encoding='utf-8')as f:
            for i in f.readlines():
                if i.count('<--->')==1:
                    if item == i.split('<--->')[0]:
                        self.textBrowser.setText(i.split('<--->')[1].strip())
                elif i.count('<--->')==2:
                    if item1 == i.split('<--->')[0]:
                        self.lineEdit2_3.setText(i.split('<--->')[1].strip())
                        self.lineEdit2_4.setText(i.split('<--->')[2].strip())
    def zhengze_list(self):
        self.ui.comboBox.clear()
        self.ui.comboBox.addItem('常用表达式')
        self.ui.comboBox_2.clear()
        self.ui.comboBox_2.addItem('常用替换模板')
        with open('config/正则.txt','r',encoding='utf-8')as f:
            list=[]
            list1=[]
            for i in f.readlines():
                if i.count('<--->') == 1:
                    list.append(i.split('<--->')[0])
                elif i.count('<--->')==2:
                    list1.append(i.split('<--->')[0])
            self.ui.comboBox.addItems(list)
            self.ui.comboBox_2.addItems(list1)
    def add1(self):
        text=self.textBrowser1.toPlainText()
        text=text.split('\n')
        self.textBrowser1.setText("")
        text0=[]
        for i in text:
            text0.append(self.lineEdit2_2.text()+i)
        self.textBrowser1.setPlainText('\n'.join(text0))
    def add2(self):
        text=self.textBrowser1.toPlainText()
        text=text.split('\n')
        self.textBrowser1.setText("")
        text0 = []
        for i in text:
            text0.append(i+self.lineEdit2_2.text())
        self.textBrowser1.setPlainText('\n'.join(text0))
    def minus(self):
        text = self.textBrowser1.toPlainText()
        text = text.split('\n')
        self.textBrowser1.setText("")
        text0 = []
        for i in text:
            text0.append(i.replace(self.lineEdit2_2.text(),''))
        self.textBrowser1.setPlainText('\n'.join(text0))
    def tihuan(self):
        text0=self.textBrowser1.toPlainText()
        try:
            text = re.sub(self.lineEdit2_3.text(), self.lineEdit2_4.text(),text0)
            self.textBrowser1.setPlainText(text)
        except:
            QMessageBox.about(self.ui, "错误", "正则匹配失败")
            self.textBrowser1.setPlainText(text0)
    def quchong(self):
        newtext = set()
        for text in self.textBrowser1.toPlainText().splitlines():
            newtext.add(text.strip())
        self.textBrowser1.setPlainText('\n'.join(newtext))
