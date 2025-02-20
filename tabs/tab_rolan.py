#-- coding:UTF-8 --
# Author:lintx
# Date:2025/01/21
# set http_proxy=http://127.0.0.1:4780 & set https_proxy=http://127.0.0.1:4780
from PyQt5.QtWidgets import QFileIconProvider,QListWidgetItem,QMenu,QMessageBox,QFileDialog,QInputDialog
from PyQt5.QtCore import Qt, QFileInfo
from PyQt5.QtGui import QIcon,QColor
import json,os,datetime,re,xlsxwriter,traceback

class tab_rolan():
    def __init__(self, ui):
        self.ui=ui
        #rolan功能点
        self.ui.rolan_list_1.itemClicked.connect(self.read_tool)    #分组单击读取工具
        self.ui.rolan_list_1.itemChanged.connect(self.change_type)  #分组重命名
        self.ui.rolan_list_2.itemChanged.connect(self.change_tool)  #工具重命名
        self.ui.rolan_list_2.itemClicked.connect(self.the_tool0)    #工具单击读取config
        self.ui.rolan_list_2.itemDoubleClicked.connect(self.the_tool)   #工具双击启动

        self.ui.rolan_list_1.setContextMenuPolicy(Qt.CustomContextMenu) #分组右键菜单
        self.ui.rolan_list_1.customContextMenuRequested.connect(self.list_1_menu)
        self.ui.rolan_list_2.setContextMenuPolicy(Qt.CustomContextMenu) #工具右键菜单
        self.ui.rolan_list_2.customContextMenuRequested.connect(self.list_2_menu)
        self.ui.dragEnterEvent = self.dragEnterEvent    #工具拖拉启动
        self.ui.dropEvent = self.dropEvent
        self.list_1_drop = self.ui.rolan_list_1.dropEvent
        self.list_2_drop = self.ui.rolan_list_2.dropEvent
        self.ui.rolan_list_1.dropEvent = self.list_1_move    #分组移动保存
        self.ui.rolan_list_2.dropEvent = self.list_2_move    #工具移动保存


        #rapid功能点
        self.ui.rolan_Button_6.clicked.connect(self.read_file)  #导入Rapid+数据
        self.ui.rolan_list_3.itemClicked.connect(self.rapid_data_read)   #单击加载数据
        self.ui.rolan_list_4.setVisible(False)
        self.ui.rolan_list_4.itemClicked.connect(self.rapid_link_tool)
        #启动器功能点
        self.ui.rolan_textBrowser_2.textChanged.connect(self.target_list)   #数据框统计
        self.ui.rolan_Button_1.clicked.connect(self.text_add1)  #数据左增加
        self.ui.rolan_Button_2.clicked.connect(self.text_add2)  #数据右增加
        self.ui.rolan_Button_3.clicked.connect(self.text_del)   #数据删除
        self.ui.rolan_Button_7.clicked.connect(self.data_clear)  # 数据框清空
        self.ui.rolan_Button_4.clicked.connect(self.tools_run_config)   #启动工具
        self.ui.rolan_Button_5.clicked.connect(self.tool_config)    #config保存
        self.ui.rolan_Button_8.clicked.connect(self.log_open)
        self.ui.rolan_Button_9.clicked.connect(self.tips)

####################################################Rolan功能实现####################################################
    #Tips
    def tips(self):
        QMessageBox.about(self.ui, "数据参数说明", "[file]： -f [file] ，数据写入一个临时文件，由工具运行\n"
                                           "[ip][port]： -ip [ip] -p [port] ，数据按':'进行分割，并逐行（批量）运行\n"
                                                   "[target]： -u [target] ，数据无处理，并逐行（批量）运行\n"
                                                   "[log]： -o [log] ,统一格式和位置：[logpath]/log-[tool_name]-[date].txt\n\t当使用[log]时[输出/日志]按钮打开统一位置，否则为工具所在目录\n"
                                                   "[date]：当前时间\n"
                                                   "[logpath]：统一位置")
    #打开配置文件
    def open_config(self):
        os.system('start "" "config/Data+.txt"')
    #数据框清空
    def data_clear(self):
        self.ui.rolan_textBrowser_2.clear()
        self.ui.rolan_list_4.setVisible(False)
    def read_file(self):
        try:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("提示")
            msg_box.setText("导入Rapid数据类型")
            msg_box.setIcon(QMessageBox.Question)
            yes_button = msg_box.addButton("dir", QMessageBox.AcceptRole)
            no_button = msg_box.addButton("file", QMessageBox.NoRole)
            close_button = msg_box.addButton("close", QMessageBox.RejectRole)
            msg_box.exec_()
            try:
                filepath=''
                if msg_box.clickedButton() == yes_button:
                    filepath = QFileDialog.getExistingDirectory(self.ui, "选择文件夹")
                elif msg_box.clickedButton() == no_button:
                    file = QFileDialog.getOpenFileName(self.ui, "选择文件")[0]
                    if file != '':
                        self.ui.rolan_list_3.clear()
                        filepath=self.rapid_data(file)
                        if filepath =='':
                            QMessageBox.about(self.ui, "提示", "请重新选择数据1")
                if filepath != '':
                    self.ui.rolan_list_3.clear()
                    self.ui.rolan_line_7.setText(filepath)
                    for root, dirs, filenames in os.walk(filepath + '/server'):
                        for filename in filenames:
                            filename = filename.replace('.txt', '')
                            self.ui.rolan_list_3.addItem(filename)
                            self.ui.rolan_list_3.setEnabled(True)
                    for root, dirs, filenames in os.walk(filepath + '/source'):
                        for filename in filenames:
                            filename = filename.replace('.txt', '')
                            self.ui.rolan_list_3.addItem(filename)
                            self.ui.rolan_list_3.setEnabled(True)
                    if self.ui.rolan_list_3.count() == 0:
                        QMessageBox.about(self.ui, "提示", "请重新选择数据2")
            except Exception as e:
                print(e)
                traceback.print_exc()
                pass
        except:
            QMessageBox.about(self.ui, "错误", "请重新选择数据3")
    def rapid_data(self,file):
        def load_finger(file_name, data_dict):  # 读取指纹数据
            with open(file_name, "r") as f:
                for i in f.readlines():
                    data = json.loads(i)
                    for i in data:
                        data_dict[i] = data[i]

        def match_finger(ip_port, finger_data):  # 指纹分类
            types = 'unknown'
            for i in finger:  # 关键字
                if types not in finger:
                    if i in finger_data:
                        types = finger[i]
                else:
                    break
            for i in finger_diy:  # 自定义
                if types not in finger_diy:
                    if i in finger_data:
                        types = finger_diy[i]
                else:
                    break
            if types == 'unknown':  # 端口默认服务
                for i in finger_port:
                    if types not in finger_port:
                        port = re.findall(r'\b' + i + r'\b', ip_port)
                        if port:
                            types = finger_port[i]
                    else:
                        break
            if 'http-' in types:
                save_finger('http', ip_port, finger_data)
            save_finger(types, ip_port, finger_data)

        def save_finger(types, ip_port, data):  # 结果保存
            # 根据服务保存
            with open(filedir + '/server/' + types + '.txt', 'a', encoding='utf-8') as f:
                if types == 'other':
                    f.write(data)
                else:
                    f.write(ip_port + '\t' + data)
                    if ip_port.split(":")[0] not in ip_all:
                        ip_all.append(ip_port.split(":")[0])
                    if ip_port not in ips_all:
                        ips_all.append(ip_port)
            # 根据端口保存
            if 'http' in types or types == 'msrcp' or types == 'none' or types == 'unknown' or types == 'jdwp' or types == 'JavaRMI' or types == 'nullpacket':  # 服务端口杂多，不输出
                pass
            else:
                with open(filedir + '/port/' + types + '-' + ip_port.split(":")[1] + '.txt', 'a',
                          encoding='utf-8') as f:
                    f.write(ip_port.split(":")[0] + '\n')


        def save_all():
            # 保存源数据
            os.popen('copy ' + file.replace('/', '\\') + ' ' + filedir.replace('/', '\\') + '\source\scan_result.txt')
            # 保存ip_all和ips_all
            with open(filedir + '/source/ip_all.txt', 'a', encoding='utf-8') as f:
                for i in ip_all:
                    f.write(i + '\n')
            with open(filedir + '/source/ips_all.txt', 'a', encoding='utf-8') as f:
                for i in ips_all:
                    f.write(i + '\n')
            # 保存成excel
            f = xlsxwriter.Workbook(filedir + '/server.xls')
            for root, dirs, filenames in os.walk(filedir + '/server/'):
                for i in filenames:
                    sheetname = i.replace('.txt', '')
                    worksheet = f.add_worksheet(sheetname)
                    row = 2
                    title = ['IP-PORT', 'SERVER', 'FINGER']
                    worksheet.write_row('A1', title)
                    with open(filedir + '/server/' + i, 'r', encoding='utf-8') as g:
                        codes = g.readlines()
                    for code in codes:
                        worksheet.set_column(0, 0, 22)
                        worksheet.set_column(1, 1, 15)
                        worksheet.set_column(2, 2, 100)
                        ip_port = re.findall(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d+', code)
                        if ip_port:
                            fingers = re.sub(r'\s+', ' ', code.replace(ip_port[0], '').replace('\t', ' '))
                            worksheet.write('A' + str(row), ip_port[0])
                            worksheet.write('B' + str(row), sheetname)
                            worksheet.write('C' + str(row), fingers)
                        else:
                            worksheet.write('A' + str(row), code)

                        row += 1
                    with open(filedir + '/server/' + i, 'r', encoding='utf-8') as h:
                        ser = re.sub('\t.*', '', h.read())
                        with open(filedir + '/server/' + i, 'w', encoding='utf-8') as i:
                            i.write(ser)
            f.close()

        def run_finger(datas):  # 主程序运行
            counts = 0
            ip_port_all = re.findall(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d+', ''.join(datas))
            if ip_port_all:
                for i in datas:
                    data = i
                    counts += 1
                    current_time = datetime.datetime.now()
                    print('\r[*] [{}] [Rapid] 数据处理进度：{}/{}'.format(current_time,counts, len(datas)), end='', flush=True)
                    ip_port = re.findall(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d+', data)
                    if ip_port:  # RapidScanner
                        finger_data = data.replace(ip_port[0], '')
                        match_finger(ip_port[0], finger_data)
                return 1
            else:
                return 0
        current_time = datetime.datetime.now()
        with open(file, 'r', encoding='utf-8') as f:
            try:
                datas = f.readlines()
            except:
                print('\n[-] [{}] [Rapid] {}编码出错，请将数据另存为UTF-8编码'.format(current_time,file))
                exit()

        now = datetime.datetime.now()
        filedir = f'result/{now.strftime("%Y%m%d")}/rapid_result_{str(int(now.timestamp()))[-6:]}'
        os.makedirs(filedir + '/port')
        os.makedirs(filedir + '/server')
        os.makedirs(filedir + '/source')


        finger = {}
        finger_diy = {}
        finger_port = {}
        load_finger("config/finger/finger.ini", finger)
        load_finger("config/finger/finger_diy.ini", finger_diy)
        load_finger("config/finger/finger_port.ini", finger_port)

        ip_all = []
        ips_all = []
        if run_finger(datas) == 1:
            current_time = datetime.datetime.now()
            print('\n[+] [{}] [Rapid] 数据处理完毕，数据来源：{}'.format(current_time,file))
            print('[+] [{}] [Rapid] 数据结果保存至目录：{}'.format(current_time, filedir))
            save_all()
        else:
            filedir=filedir.replace('/', '\\')
            os.popen(f"rmdir {filedir} /S/Q")
            filedir=''
        return filedir

    def rapid_data_read(self):
        current_data = self.ui.rolan_list_3.selectedItems()[0].text()
        try:
            with open(self.ui.rolan_line_7.text()+'/server/'+current_data+'.txt','r',encoding='utf-8') as f:
                self.ui.rolan_textBrowser_2.setText(f.read().strip())
        except:
            try:
                with open(self.ui.rolan_line_7.text()+'/source/'+current_data+'.txt','r',encoding='utf-8') as f:
                    self.ui.rolan_textBrowser_2.setText(f.read().strip())
            except:
                QMessageBox.about(self.ui, "提示", "读取数据错误")
        if current_data in Service_type:
            self.ui.rolan_list_4.clear()
            for i in Service_type[current_data]:
                self.ui.rolan_list_4.addItem(i)
            self.ui.rolan_list_4.setVisible(True)
        else:
            self.ui.rolan_list_4.clear()
            self.ui.rolan_list_4.setVisible(False)
    def rapid_link_tool(self):
        try:
            current_service = self.ui.rolan_list_3.selectedItems()[0].text()
            current_tool = self.ui.rolan_list_4.selectedItems()[0].text()
            for i in range(self.ui.rolan_list_1.count()):
                item = self.ui.rolan_list_1.item(i)
                if item.text() == Service_type[current_service][current_tool]:
                    self.ui.rolan_list_1.setCurrentItem(item)
                    self.ui.rolan_list_1.itemClicked.emit(item)
            for i in range(self.ui.rolan_list_2.count()):
                item = self.ui.rolan_list_2.item(i)
                if item.text() == current_tool:
                    self.ui.rolan_list_2.setCurrentItem(item)
                    self.ui.rolan_list_2.itemClicked.emit(item)
        except:
            pass

    #读取data
    def read_data(self,clearstate):
        if not clearstate:
            self.ui.setAcceptDrops(True)
            self.ui.rolan_frame_1.setEnabled(False)
            self.ui.rolan_list_1.clear()
            self.ui.rolan_list_2.clear()
            self.ui.rolan_line_1.clear()
            self.ui.rolan_line_2.clear()
            self.ui.rolan_line_3.clear()
            self.ui.rolan_line_4.clear()
            self.ui.rolan_radio_1.setChecked(True)
        if not os.path.exists('config/Data+.txt'):
            os.system('echo {"\\u793a\\u4f8b\\u5206\\u7ec4": {"\\u53c2\\u6570\\u6f14\\u793a": {"Path": "[toolpath]\\\\config\\\\Data+.txt","config_1": "echo python3 tool.py -f [file] -o [log]","config_2": "echo python2 tool.py -i [ip] -p [port]","config_3": "echo tool.exe -l [target]","tool_key": "first","tool_tip": "\\u4f7f\\u7528echo\\u6f14\\u793abat\\u542f\\u52a8\\u6548\\u679c\\uff08\\u66f4\\u591a\\u53c2\\u6570\\u70b9\\u51fb\\u8bf4\\u660e\\u6309\\u94ae\\u67e5\\u770b\\uff09","tool_service": "\\u670d\\u52a1\\u7c7b\\u578b"},"RapidScanner": {"Path": "[toolpath]\\\\tools\\\\RapidScanner.exe","config_1": "1\\u3001\\u5de5\\u5177\\u652f\\u6301\\u62d6\\u62c9\\u65b0\\u589e\\u6216\\u8005\\u53f3\\u952e\\u65b0\\u589e","config_2": "2\\u3001\\u652f\\u6301\\u4e09\\u6761\\u81ea\\u5b9a\\u4e49\\u542f\\u52a8\\u547d\\u4ee4","config_3": "3\\u3001\\u901a\\u8fc7\\u8fd0\\u884cbat\\u65b9\\u5f0f\\u6267\\u884c\\u542f\\u52a8\\u547d\\u4ee4","tool_key": "first","tool_tip": "\\u652f\\u6301\\u76f4\\u63a5\\u53cc\\u51fb\\u6253\\u5f00\\uff0c\\u53f3\\u952e\\u6253\\u5f00,\\u6309\\u94ae\\u6253\\u5f00\\uff08\\u9700\\u547d\\u4ee4\\u7f6e\\u7a7a\\uff09","tool_service": "\\u670d\\u52a1\\u7c7b\\u578b"}}}>config/Data+.txt')
        with open('config/Data+.txt','r',encoding='utf-8')as f:
            global Tools_type,Service_type
            Tools_type={}
            Service_type={}
            try:
                Tools_type=json.loads(f.read())
            except:
                pass
            
            for i in Tools_type:
                theItem = QListWidgetItem(i)
                theItem.setFlags(theItem.flags() | Qt.ItemIsEditable)
                if not clearstate:
                    self.ui.rolan_list_1.addItem(theItem)
                for b in Tools_type[i]:
                    try:
                        servicetext=Tools_type[i][b]['tool_service']
                        if servicetext not in Service_type:
                            Service_type[servicetext]= {b:i}
                        else:
                            Service_type[servicetext][b]=i
                    except:
                        pass
        if not clearstate:
            self.read_service('')

    def read_service(self,tool_service):
        self.ui.comboBox_3.clear()
        if tool_service:
            self.ui.comboBox_3.addItem(tool_service)
            self.ui.comboBox_3.addItem('服务类型')
        else:
            self.ui.comboBox_3.addItem('服务类型')
        list = []
        with open('config/finger/finger.ini', 'r', encoding='utf-8') as f:
            for i in f.readlines():
                jsontext = json.loads(i)
                for b in jsontext:
                    servicetext = jsontext[b]
                    if servicetext not in list:
                        list.append(jsontext[b])
        with open('config/finger/finger_diy.ini', 'r', encoding='utf-8') as f:
            for i in f.readlines():
                jsontext = json.loads(i)
                for b in jsontext:
                    servicetext = jsontext[b]
                    if servicetext not in list:
                        list.append(jsontext[b])
        list.sort()
        self.ui.comboBox_3.addItems(list)

    #加载工具列表
    def read_tool(self):
        try:
            self.ui.rolan_frame_1.setEnabled(False)
            self.ui.rolan_list_2.verticalScrollBar().setValue(0)
            self.ui.rolan_list_2.clear()
            item=self.ui.rolan_list_1.selectedItems()[0].text()
            try:
                tools = Tools_type[item]
            except:
                pass
            for tool in tools:
                pwd=os.getcwd()
                tool_path=tools[tool]['Path'].replace('[toolpath]', pwd)
                file_Info = QFileInfo(tool_path)
                try:
                    if '.jar' in tool_path:
                        java_path = 'config/ico/java.ico'
                        file_Info = QFileInfo(java_path)
                    if '.py' in tool_path:
                        java_path = 'config/ico/python.ico'
                        file_Info = QFileInfo(java_path)
                except:
                    pass
                iconProvider = QFileIconProvider()
                if os.path.exists(file_Info):
                    icon = iconProvider.icon(file_Info)
                    theItem = QListWidgetItem(QIcon(icon), tool)
                else:
                    theItem =QListWidgetItem(tool)
                theItem.setFlags(theItem.flags() | Qt.ItemIsEditable)
                # if pwd not in tool_path:
                #     theItem.setForeground(QColor('gray'))
                self.ui.rolan_list_2.addItem(theItem)
        except:
            pass


    #打开工具
    def the_tool(self):
        self.tools_run('start')
        self.read_config()
    # 选中工具
    def the_tool0(self):
        self.read_config()
        self.ui.rolan_frame_1.setEnabled(True)
        
    #拖放文件
    def dragEnterEvent(self, event):
        self.ui.rolan_frame_1.setEnabled(False)
        tabs_text = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
        if tabs_text == 'Rolan+' and self.ui.rolan_list_1.selectedItems():
            if event.mimeData().hasUrls():
                event.acceptProposedAction()

    def dropEvent(self, event):
        self.ui.rolan_frame_1.setEnabled(False)
        tabs_text = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
        if tabs_text == 'Rolan+' and self.ui.rolan_list_1.selectedItems():
            if event.mimeData().hasUrls():
                for url in event.mimeData().urls():
                    path = url.toLocalFile()
                    self.tools_add(path)
        event.acceptProposedAction()

    #tools_add
    def tools_add(self,path):
        current_type = self.ui.rolan_list_1.selectedItems()[0].text()
        fileInfo = QFileInfo(path)
        if fileInfo.isSymLink():
            fileInfo = QFileInfo(fileInfo.symLinkTarget())
        filename = os.path.splitext(fileInfo.fileName())[0]
        while filename in [i for i in Tools_type[current_type]]:
            filename += '_new'
        # 数据处理
        file_path = fileInfo.filePath().replace('/', '\\')
        if os.getcwd() in os.path.dirname(file_path):
            file_path = file_path.replace(os.getcwd(),'[toolpath]')
        Tools_type[current_type][filename] = {"Path": file_path}
        # 列表增加
        iconProvider = QFileIconProvider()
        icon = iconProvider.icon(fileInfo)
        theItem = QListWidgetItem(QIcon(icon), filename)
        theItem.setFlags(theItem.flags() | Qt.ItemIsEditable)
        # if '[toolpath]' not in file_path:
        #     theItem.setForeground(QColor('gray'))
        self.ui.rolan_list_2.addItem(theItem)
        self.ui.rolan_frame_1.setEnabled(False)
        self.save_config()

    #target_list
    def target_list(self):
        if self.ui.rolan_textBrowser_2.toPlainText() == '':
            self.ui.rolan_line_6.setText('Count:0')
        else:
            self.ui.rolan_line_6.setText('Count:' + str(len(self.ui.rolan_textBrowser_2.toPlainText().split('\n'))))

    # list_1_menu
    def list_1_menu(self, post):
        menu = QMenu()
        item1 = menu.addAction("刷新")
        item2 = menu.addAction("新增")
        item3 = menu.addAction("重命名")
        item4 = menu.addAction("删除")
        action = menu.exec_(self.ui.rolan_list_1.mapToGlobal(post))
        if action == item1:
            self.read_data('')
        if action == item2:
            try:
                dir,ok = QInputDialog.getText(None, "提示", "新增分组：")
                if dir:
                    while dir in Tools_type:
                        dir+='_new'
                    Tools_type[dir] = {}
                    theItem = QListWidgetItem(dir)
                    theItem.setFlags(theItem.flags() | Qt.ItemIsEditable)
                    self.ui.rolan_list_1.addItem(theItem)
                    self.ui.rolan_frame_1.setEnabled(False)
                    self.save_config()
                else:
                    QMessageBox.about(self.ui, "提示", "分组不能为空")
            except:
                pass
        if action == item3:
            try:
                self.ui.rolan_list_1.editItem(self.ui.rolan_list_1.selectedItems()[0])
            except:
                pass
        if action == item4:
            try:
                current_type=self.ui.rolan_list_1.selectedItems()[0].text()
                checkif = QMessageBox.question(self.ui, "提示", f"确定删除[{current_type}]分组？", QMessageBox.No | QMessageBox.Yes,QMessageBox.No)
                if checkif == QMessageBox.Yes:
                    del Tools_type[current_type]
                    current_row = self.ui.rolan_list_1.currentRow()
                    self.ui.rolan_list_1.takeItem(current_row)
                    self.save_config()
                    self.read_data('')
            except:
                pass

    # list_2_menu
    def list_2_menu(self,post):
        global Tools_type
        menu = QMenu()
        item2 = menu.addAction("打开")
        item3 = menu.addAction("打开目录")
        item1 = menu.addAction("刷新")
        item4 = menu.addAction("新增")
        item5 = menu.addAction("重命名")
        item6 = menu.addAction("删除")
        item7 = menu.addAction("Config")
        item8 = menu.addMenu("移动分组")
        action_dirs=[]
        for i in Tools_type:
            action_dirs.append(item8.addAction(i))
        action =menu.exec_(self.ui.rolan_list_2.mapToGlobal(post))
        if action in action_dirs:
            try:
                current_type = self.ui.rolan_list_1.selectedItems()[0].text()
                current_tool = self.ui.rolan_list_2.selectedItems()[0].text()
                moveto_dir = action.text()
                checkif0 = ''
                checkif = QMessageBox.question(self.ui, "提示", f"确定移动 [{current_tool}] 到分组 [{moveto_dir}] ？",
                                               QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
                if checkif == QMessageBox.Yes:
                    if current_tool in [i for i in Tools_type[moveto_dir]]:
                        checkif0=QMessageBox.question(self.ui, "提示", f"分组 [{moveto_dir}] 已存在 [{current_tool}] ，是否移动？",
                                             QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
                        if checkif0 == QMessageBox.Yes:
                            current_tool0 = current_tool+'_new'
                        else:
                            return
                    if checkif0:
                        Tools_type[moveto_dir][current_tool0] = Tools_type[current_type][current_tool]
                    else:
                        Tools_type[moveto_dir][current_tool]=Tools_type[current_type][current_tool]
                    if moveto_dir != current_type:
                        del Tools_type[current_type][current_tool]
                    self.save_config()
                    self.read_tool()
            except:
                pass
        if action == item1:
            self.read_tool()
        if action == item2:
            self.tools_run('start')
            self.read_config()
        if action == item3:
            self.tools_run('dir')
            self.read_config()
        if action == item4:
            try:
                self.ui.rolan_list_1.selectedItems()[0].text()
                msg_box = QMessageBox()
                msg_box.setWindowTitle("提示")
                msg_box.setText("选择要新增的类型？")
                msg_box.setIcon(QMessageBox.Question)
                yes_button = msg_box.addButton("dir",QMessageBox.AcceptRole)
                no_button = msg_box.addButton("file", QMessageBox.NoRole)
                close_button = msg_box.addButton("close", QMessageBox.RejectRole)
                msg_box.exec_()
                try:
                    if msg_box.clickedButton() == yes_button:
                        filepath = QFileDialog.getExistingDirectory(self.ui, "选择要添加的目录")
                    elif msg_box.clickedButton() == no_button:
                        filepath = QFileDialog.getOpenFileName(self.ui, "选择要添加的工具")[0]
                    if filepath:
                        self.tools_add(filepath)
                except:
                    pass
            except:
                QMessageBox.about(self.ui, "错误", "请先选择分组")
        if action == item5:
            try:
                self.ui.rolan_list_2.editItem(self.ui.rolan_list_2.selectedItems()[0])
            except:
                pass
        if action == item6:
            try:
                current_type = self.ui.rolan_list_1.selectedItems()[0].text()
                current_tool = self.ui.rolan_list_2.selectedItems()[0].text()
                checkif = QMessageBox.question(self.ui, "提示", f"确定删除[{current_tool}]？",
                                               QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
                if checkif == QMessageBox.Yes:
                    del Tools_type[current_type][current_tool]
                    current_row = self.ui.rolan_list_2.currentRow()
                    self.ui.rolan_list_2.takeItem(current_row)
                    self.ui.rolan_frame_1.setEnabled(False)
                    self.save_config()
            except:
                pass
        if action == item7:
            self.open_config()

    # 顺序移动保存
    def list_1_move(self, event):
        self.ui.rolan_frame_1.setEnabled(False)
        self.list_1_drop(event)
        global Tools_type
        item_names = [self.ui.rolan_list_1.item(i).text() for i in range(self.ui.rolan_list_1.count())]
        Tools_type_0 = {}
        for b,i in enumerate(item_names):
            try:
                Tools_type_0[i] = Tools_type[i]
            except:
                pass
        if len(Tools_type) == len(Tools_type_0):
            Tools_type = Tools_type_0
            self.ui.rolan_list_2.clear()
            self.save_config()

    def list_2_move(self, event):
        self.ui.rolan_frame_1.setEnabled(False)
        self.list_2_drop(event)
        global Tools_type
        item_names = [self.ui.rolan_list_2.item(i).text() for i in range(self.ui.rolan_list_2.count())]
        Tools_type_0 = {}
        for b,i in enumerate(item_names):
            try:
                global type
                type = self.ui.rolan_list_1.selectedItems()[0].text()
                Tools_type_0[i] = Tools_type[type][i]
            except:
                pass
        if len(Tools_type[type]) == len(Tools_type_0):
            Tools_type[type] = Tools_type_0
            self.save_config()

    #change_type
    def change_type(self):
        current_type = self.ui.rolan_list_1.selectedItems()[0].text()
        current_row = self.ui.rolan_list_1.currentRow()
        global Tools_type
        histry_type = [i for i in Tools_type][current_row]
        item_names = [self.ui.rolan_list_1.item(i).text() for i in range(self.ui.rolan_list_1.count())]
        Tools_type_0 = {}
        if current_type != histry_type:
            checkif = QMessageBox.question(self.ui, "提示", f"确定修改为[{current_type}]分组？",
                                           QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
            if checkif == QMessageBox.Yes:
                while current_type in [i for i in Tools_type]:
                    QMessageBox.about(self.ui, "错误", "分组名称重复，请重新修改")
                    self.read_data('')
                    return
                for i in item_names:
                    if i == current_type:
                        Tools_type_0[i] = Tools_type[histry_type]
                    else:
                        Tools_type_0[i] = Tools_type[i]
                if len(Tools_type) == len(Tools_type_0):
                    Tools_type = Tools_type_0
                    self.save_config()
            self.read_data('')

    #change_tool
    def change_tool(self):
        current_type = self.ui.rolan_list_1.selectedItems()[0].text()
        current_tool = self.ui.rolan_list_2.selectedItems()[0].text()
        current_row = self.ui.rolan_list_2.currentRow()
        global Tools_type
        histry_tool = [i for i in Tools_type[current_type]][current_row]
        item_names = [self.ui.rolan_list_2.item(i).text() for i in range(self.ui.rolan_list_2.count())]
        Tools_type_0 = {}
        if current_tool != histry_tool:
            checkif = QMessageBox.question(self.ui, "提示", f"确定修改为[{current_tool}]？",
                                           QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
            if checkif == QMessageBox.Yes:
                while current_tool in [i for i in Tools_type[current_type]]:
                    QMessageBox.about(self.ui, "错误", "工具名称重复，请重新修改")
                    self.read_tool()
                    return
                for i in item_names:
                    if i == current_tool:
                        Tools_type_0[i] = Tools_type[current_type][histry_tool]
                    else:
                        Tools_type_0[i] = Tools_type[current_type][i]
                if len(Tools_type[current_type]) == len(Tools_type_0):
                    Tools_type[current_type] = Tools_type_0
                    self.save_config()
            self.read_tool()


    #save_config
    def save_config(self):
        with open('config/Data+.txt','w',encoding='utf-8')as f:
            f.write(json.dumps(Tools_type,indent=4))

####################################################启动功能实现####################################################
    #tool_config
    def tool_config(self):
        try:
            tool_tip=self.ui.rolan_line_1.text()
            config_1=self.ui.rolan_line_2.text()
            config_2=self.ui.rolan_line_3.text()
            config_3=self.ui.rolan_line_4.text()
            if self.ui.rolan_radio_1.isChecked() == True:
                tool_key='first'
            elif self.ui.rolan_radio_2.isChecked() == True:
                tool_key = 'second'
            elif self.ui.rolan_radio_3.isChecked() == True:
                tool_key = 'third'
            current_type = self.ui.rolan_list_1.selectedItems()[0].text()
            current_tool = self.ui.rolan_list_2.selectedItems()[0].text()
            Tools_type[current_type][current_tool]['config_1'] = config_1
            Tools_type[current_type][current_tool]['config_2'] = config_2
            Tools_type[current_type][current_tool]['config_3'] = config_3
            Tools_type[current_type][current_tool]['tool_key'] = tool_key
            Tools_type[current_type][current_tool]['tool_tip'] = tool_tip
            current_service = self.ui.comboBox_3.currentText()
            if current_service != '服务类型':
                Tools_type[current_type][current_tool]['tool_service'] = current_service
            else:
                Tools_type[current_type][current_tool]['tool_service'] = '服务类型'
            self.save_config()
            QMessageBox.about(self.ui, "提示", "已保存")
            self.read_data('change')
        except Exception as e:
                QMessageBox.about(self.ui, "错误", f"保存配置异常：{e}")
    #read_config
    def read_config(self):
        self.ui.rolan_line_1.clear()
        self.ui.rolan_line_2.clear()
        self.ui.rolan_line_3.clear()
        self.ui.rolan_line_4.clear()
        self.ui.rolan_radio_1.setChecked(True)
        self.read_service('')
        current_type = self.ui.rolan_list_1.selectedItems()[0].text()
        current_tool = self.ui.rolan_list_2.selectedItems()[0].text()
        try:
            config_1 = Tools_type[current_type][current_tool]['config_1']
            config_2 = Tools_type[current_type][current_tool]['config_2']
            config_3 = Tools_type[current_type][current_tool]['config_3']
            tool_key = Tools_type[current_type][current_tool]['tool_key']
            try:
                tool_tip = Tools_type[current_type][current_tool]['tool_tip']
                self.ui.rolan_line_1.setText(tool_tip)
                self.ui.rolan_line_1.setToolTip(tool_tip)
            except:
                pass
            try:
                tool_service = Tools_type[current_type][current_tool]['tool_service']
                self.read_service(tool_service)
                try:
                    if self.ui.rolan_list_4.selectedItems()[0].text() != current_tool:
                        self.ui.rolan_list_4.setVisible(False)
                except:
                    self.ui.rolan_list_4.setVisible(False)
                    pass
            except:
                self.ui.rolan_list_4.setVisible(False)
                self.read_service('')
                pass
            self.ui.rolan_line_2.setText(config_1)
            self.ui.rolan_line_3.setText(config_2)
            self.ui.rolan_line_4.setText(config_3)
            self.ui.rolan_line_2.setToolTip(config_1)
            self.ui.rolan_line_3.setToolTip(config_2)
            self.ui.rolan_line_4.setToolTip(config_3)
            self.ui.rolan_line_1.setCursorPosition(0)
            self.ui.rolan_line_2.setCursorPosition(0)
            self.ui.rolan_line_3.setCursorPosition(0)
            self.ui.rolan_line_4.setCursorPosition(0)
            if tool_key == 'first':
                self.ui.rolan_radio_1.setChecked(True)
            elif tool_key == 'second':
                self.ui.rolan_radio_2.setChecked(True)
            elif tool_key == 'third':
                self.ui.rolan_radio_3.setChecked(True)
        except:
            self.ui.rolan_list_4.setVisible(False)
            pass
    def text_add1(self):
        text=self.ui.rolan_textBrowser_2.toPlainText()
        text=text.split('\n')
        self.ui.rolan_textBrowser_2.setText("")
        text0 = []
        for i in text:
            text0.append(self.ui.rolan_line_5.text()+i)
        self.ui.rolan_textBrowser_2.setPlainText('\n'.join(text0))
    def text_add2(self):
        text=self.ui.rolan_textBrowser_2.toPlainText()
        text=text.split('\n')
        self.ui.rolan_textBrowser_2.setText("")
        text0 = []
        for i in text:
            text0.append(i+self.ui.rolan_line_5.text())
        self.ui.rolan_textBrowser_2.setPlainText('\n'.join(text0))
    def text_del(self):
        text = self.ui.rolan_textBrowser_2.toPlainText()
        text = text.split('\n')
        self.ui.rolan_textBrowser_2.setText("")
        text0 = []
        for i in text:
            text0.append(i.replace(self.ui.rolan_line_5.text(),''))
        self.ui.rolan_textBrowser_2.setPlainText('\n'.join(text0))
    #tools_run_config
    def tools_run_config(self):
        try:
            tool_name = self.ui.rolan_list_2.selectedItems()[0].text()
            type = self.ui.rolan_list_1.selectedItems()[0].text()
            item = self.ui.rolan_list_2.selectedItems()[0].text()
            cmds = Tools_type[type][item]['Path']
            pwd = os.getcwd()
            cmds = cmds.replace('[toolpath]',pwd)
            current_time = datetime.datetime.now()
            current_date = current_time.strftime("%Y%m%d")
            current_dates = current_time.strftime("%Y%m%d%S")
            temp_data = f"{os.getcwd()}\\config\\temp_run.data"
            logpath = f'{pwd}\\result\\{current_date}'
            if not os.path.exists(logpath):
                os.makedirs(logpath)

            if self.ui.rolan_radio_1.isChecked() == True:
                tool_config=self.ui.rolan_line_2.text()
            elif self.ui.rolan_radio_2.isChecked() == True:
                tool_config=self.ui.rolan_line_3.text()
            elif self.ui.rolan_radio_3.isChecked() == True:
                tool_config=self.ui.rolan_line_4.text()

            logs=f'[*] [{current_time}] [{tool_name}] {tool_config}'
            print(logs)
            with open(f'{logpath}\\logs-run-{current_date}.txt', 'a', encoding='utf-8') as tool_log:
                print(logs,file=tool_log)

            try:
                with open('config/env.ini', "r") as f:
                    env = json.loads(f.read())
                current_env = tool_config.split(' ')[0]
                if current_env in env:
                    if env[current_env]:
                        tool_config = tool_config.replace(current_env+' ',pwd+'/'+env[current_env]+' ')
            except:
                pass

            tool_config = tool_config.replace('[tool]',cmds)
            tool_config = tool_config.replace('[date]',current_dates)
            tool_config = tool_config.replace('[log]', f'{logpath}\\log-{tool_name}-{current_dates}.txt')
            tool_config = tool_config.replace('[logpath]', logpath)
            if tool_config:
                with open(temp_data, 'w', encoding='utf-8') as f:
                    f.write(self.ui.rolan_textBrowser_2.toPlainText())
                if '[file]' in tool_config or '%TARGETS%' in tool_config:
                    tool_config = tool_config.replace('[file]', temp_data).replace('%TARGETS%', temp_data)
                elif '[ip]' in tool_config or '!IP!' in tool_config:
                    if ':' in self.ui.rolan_textBrowser_2.toPlainText():
                        tool_config = tool_config.replace('[ip]','%%a').replace('[port]','%%b').replace('!IP!','%%a').replace('!PORT!','%%b')
                        tool_config = f"for /f \"tokens=1,2 delims=:\" %%a in ({temp_data}) do {tool_config}"
                    else:
                        QMessageBox.about(self.ui, "错误", f"启动异常：当前数据非[ip]:[port]格式")
                        return
                elif '[target]' in tool_config or '!TARGET!' in tool_config:
                    tool_config = tool_config.replace('[target]','%%a').replace('!TARGET!','%%a')
                    tool_config = f"for /f %%a in ({temp_data}) do {tool_config}"
                os.chdir(os.path.dirname(cmds))
                with open(f'{item}_run.bat', 'w', encoding='utf-8') as f:
                    #f.write('chcp 65001\n'+tool_config)
                    f.write(tool_config)
                os.chdir(pwd)
                self.tools_run('run')
            else:
                QMessageBox.about(self.ui, "提示", "未配置数据，直接启动")
                self.tools_run('start')
        except Exception as e:
            os.chdir(pwd)
            QMessageBox.about(self.ui, "错误", f"启动异常：请先选中工具")
            print('[-] [{}] [{}] [错误] '.format(current_time,item),e)

    #tools_run
    def tools_run(self,key=''):
        try:
            type=self.ui.rolan_list_1.selectedItems()[0].text()
            item=self.ui.rolan_list_2.selectedItems()[0].text()
            cmds=Tools_type[type][item]['Path']
            pwd = os.getcwd()
            cmds = cmds.replace('[toolpath]', pwd)
            os.chdir(os.path.dirname(cmds))
            if key == 'dir':
                cmds = f'start "" "{os.path.dirname(cmds)}"'
            elif key == 'run':
                cmds = f'start "" "{item}_run.bat"'
            elif key == 'start':
                cmds = f'start "" "{cmds}"'
                if '.jar' in cmds:
                    current_time = datetime.datetime.now()
                    print("[*] [{}] [提示] Java程序打开或双击无反应，可使用启动按钮打开".format(current_time))
            else:
                try:
                    if Tools_type[type][item]['config_1']:
                        cmds = 'REM'
                    else:
                        cmds = f'start "" "{cmds}"'
                except:
                    cmds = f'start "" "{cmds}"'
            os.system(cmds)
            os.chdir(pwd)
        except:
            pass

    #log_open
    def log_open(self):
        pwd = os.getcwd()
        current_time = datetime.datetime.now()
        current_date = current_time.strftime("%Y%m%d")
        logpath = f'{pwd}\\result\\{current_date}'
        logpath0 = f'{pwd}\\result'
        if self.ui.rolan_radio_1.isChecked() == True:
            tool_config = self.ui.rolan_line_2.text()
        elif self.ui.rolan_radio_2.isChecked() == True:
            tool_config = self.ui.rolan_line_3.text()
        elif self.ui.rolan_radio_3.isChecked() == True:
            tool_config = self.ui.rolan_line_4.text()
        if '[log]' in tool_config or '[logpath]' in tool_config:
            if os.path.exists(logpath):
                cmds = f'start "" "{logpath}"'
            else:
                cmds = f'start "" "{logpath0}"'
            os.system(cmds)
        else:
            self.tools_run('dir')