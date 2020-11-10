'''
========================================================
部分代码参考：https://github.com/Sbwillbealier/screenshots
'''

import sys
from PyQt5.QtGui import QPainter, QFont, QIcon, QKeySequence
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QCheckBox, QRadioButton, QLineEdit, QMessageBox, QTextBrowser, QFileDialog, QSystemTrayIcon, QAction, QMenu, QShortcut
from PyQt5.QtCore import Qt, pyqtSignal, QAbstractNativeEventFilter, QAbstractEventDispatcher
import logging
import datetime
import os
from pyqtkeybind import keybinder
import json
import time

from PacooLib import ImageProcessor, OcrProcessor
ip = ImageProcessor()
op = OcrProcessor()


class MyWin(QMainWindow):
    def __init__(self, settings):
        super(MyWin, self).__init__()
        self.settings = settings
        self.is_processing = False
        self.initUi(settings)

    def initUi(self, settings):
        self.setWindowTitle("Pacoo")
        self.setWindowIcon(QIcon('logo.jpg'))
        if settings['window_height'] == "all":
            self.resize(580, 700)
        else:
            self.resize(580, 300)
        self.btn = QPushButton('识别公式', self)
        self.btn.setGeometry(40, 40, 200, 130)
        self.btn.setFont(QFont(QFont("FangSong", 20)))
        self.btn.clicked.connect(self.click_btn)
        # QShortcut(QKeySequence(self.tr("Shift+A")), self, self.click_btn) #快捷键

        label = QLabel(self)
        # label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        label.setFont(QFont(QFont("FangSong", 20)))
        label.setGeometry(300, 40, 240, 40)
        label.setText("选择格式：")

        self.rb_word = QRadioButton("Word 2016+", self)
        self.rb_word.setFont(QFont(QFont("FangSong", 20)))
        self.rb_word.setGeometry(300, 90, 240, 40)
        self.rb_latex = QRadioButton("LaTex", self)
        self.rb_latex.setFont(QFont(QFont("FangSong", 20)))
        self.rb_latex.setGeometry(300, 130, 240, 40)
        if settings["result_format"] == "word":
            self.rb_word.setChecked(True)
        else:
            self.rb_latex.setChecked(True)

        line_label = QLabel(self)
        # line_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        line_label.setFont(QFont("FangSong", 20))
        line_label.setGeometry(40, 180, 200, 40)
        line_label.setText("剩余次数：")

        self.left_label = QLabel(self)
        # self.left_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.left_label.setGeometry(200, 180, 160, 40)
        self.left_label.setFont(QFont("Helvetica", 20, QFont.Bold))
        self.left_label.setText("???")

        self.dev_api_cb = QCheckBox("开发者账号", self)
        self.dev_api_cb.setGeometry(300, 180, 220, 40)
        self.dev_api_cb.setFont(QFont("FangSong", 20))
        if settings["use_dev_api"]:
            self.dev_api_cb.setChecked(True)

        lb0 = QLabel(self)
        lb0.setGeometry(40, 200, 500, 80)
        lb0.setFont(QFont('KaiTi', 9))
        lb0.setText("在公众号(Pacoo)回复“桌面版”，将获取的动态链接复制粘贴到下面：")
        self.link_le = QLineEdit(self)
        self.link_le.setGeometry(40, 250, 500, 40)
        self.link_le.setText(settings["link"])
        lb = QLabel(self)
        lb.setGeometry(40, 300, 500, 10)
        lb.setText("----------------------------------------------------------------")

        self.account_le = QLineEdit(self)
        self.password_le = QLineEdit(self)
        account_label = QLabel(self)
        account_label.setGeometry(40, 320, 200, 40)
        account_label.setText("API_id：")
        account_label.setFont(QFont(QFont("FangSong", 16)))
        password_label = QLabel(self)
        password_label.setGeometry(40, 370, 200, 40)
        password_label.setText("API_key：")
        password_label.setFont(QFont(QFont("FangSong", 16)))
        self.account_le.setGeometry(170, 320, 370, 40)
        self.account_le.setText(settings["account"])
        self.password_le.setGeometry(170, 370, 370, 40)
        self.password_le.setText(settings["passwd"])

        bottom_info = QLabel(self)
        bottom_info.setGeometry(40, 400, 500, 80)
        bottom_info.setFont(QFont("KaiTi", 16))
        bottom_info.setText("遇到问题，联系客服。微信：pacoo1614")

        lb01 = QLabel(self)
        lb01.setGeometry(40, 470, 500, 40)
        lb01.setFont(QFont("KaiTi", 10))
        lb01.setText("* 感谢以以下参加内测版的同学 *")

        self.textBrowser_3 = QTextBrowser(self)
        self.textBrowser_3.setGeometry(40, 500, 500, 170)
        self.textBrowser_3.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                              "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                              "p, li { white-space: pre-wrap; }\n"
                                              "</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                                              "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Avenir\'; font-size:14px; color:#606266; background-color:#ecf5ff;\">康婷    惘卿心    ꧁꫞꯭z꯭e꯭r꯭0꫞꧂    </span></p>\n"
                                              "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Avenir\'; font-size:14px; color:#606266; background-color:#ecf5ff;\">战神    海洋    LLLLLiang</span></p>\n"
                                              "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Avenir\'; font-size:14px; color:#606266; background-color:#ecf5ff;\">养一只猴子_陪我看夕阳    这个我不确定啊</span></p>\n"
                                              "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Avenir\'; font-size:14px; color:#606266; background-color:#ecf5ff;\">Sun    Erigeron    大舟</span></p>\n"
                                              "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Avenir\'; font-size:14px; color:#606266; background-color:#ecf5ff;\">淘气包马婷    🇼 🇭 🇭    刘心玉</span></p>\n"
                                              "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Avenir\'; font-size:14px; color:#606266; background-color:#ecf5ff;\">书华    </span><span style=\" font-family:\'Avenir\'; font-size:14px; color:#606266; background-color:#ffffff;\">葛江峡    </span><span style=\" font-family:\'Avenir\'; font-size:14px; color:#606266; background-color:#ecf5ff;\">好孩纸 kimi</span></p>\n"
                                              "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Avenir\'; font-size:14px; color:#606266; background-color:#ecf5ff;\">北凉    0.007    HG Deng</span></p>\n"
                                              "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Avenir\'; font-size:14px; color:#606266; background-color:#ecf5ff;\">嚼不断的浓痰</span></p></body></html>")

    def set_process_status(self, status):
        self.is_processing = status

    def click_btn(self):
        print("is_processing", self.is_processing)
        if self.is_processing:
            op.play_sound("failed")
            QMessageBox.about(self, "Pacoo", "你有一个识别正在进行，请等待。")
            return None
        else:
            self.is_processing = True
        self.showMinimized()
        self.screenshot = ScreenShotsWin(self)

    def start_math_ocr(self):
        print("start_math_ocr")
    def start_math_ocr_wx(self):
        print("start_math_ocr_wx")


    def update_settings(self):
        '''
        保存设置
        :return:
        '''
        account = self.account_le.text()
        passwd = self.password_le.text()
        link = self.link_le.text()
        # print(account, passwd, link)
        if (account == "" or passwd == "") and (link == ""):
            self.settings['window_height'] = "all"
        else:
            self.settings['window_height'] = "half"
        self.settings['account'] = account
        self.settings['passwd'] = passwd
        self.settings['link'] = link
        self.settings['result_format'] = "word" if self.rb_word.isChecked() else "latex"
        self.settings['use_dev_api'] = True if self.dev_api_cb.isChecked() else False
        homeDir = os.path.expanduser("~")
        with open(homeDir+"\\pacoo.conf", "w") as f:
            json.dump(self.settings, f)

    def closeEvent(self, event):
        '''
        添加一个退出的提示事件，在退出时保存设置。
        :param event:
        :return:
        '''
        reply = QMessageBox.question(self, 'Message', "确定关闭程序?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # 判断返回值，如果点击的是Yes按钮，我们就关闭组件和应用，否则就忽略关闭事件
        if reply == QMessageBox.Yes:
            event.accept()
            self.update_settings()
        else:
            event.ignore()


class ScreenShotsWin(QMainWindow):
    # 定义一个信号
    oksignal = pyqtSignal()

    def __init__(self, ui):
        super(ScreenShotsWin, self).__init__()
        self.ui = ui
        self.is_shoting = True
        self.start = (0, 0)  # 开始坐标点
        self.end = (0, 0)  # 结束坐标点
        self.initUI()

    def initUI(self):
        self.showFullScreen()
        self.setWindowOpacity(0.5)
        self.oksignal.connect(lambda: self.screenshots(self.start, self.end))

    def screenshots(self, start, end):
        '''
        截图功能
        :param start:截图开始点
        :param end:截图结束点
        :return:
        '''
        # logger.debug('开始截图,%s, %s', start, end)

        x = min(start[0], end[0])
        y = min(start[1], end[1])
        width = abs(end[0] - start[0])
        height = abs(end[1] - start[1])

        des = QApplication.desktop()
        screen = QApplication.primaryScreen()

        if screen:
            self.setWindowOpacity(0.0)
            pix = screen.grabWindow(des.winId(), x, y, width, height)

        fold = datetime.datetime.now().strftime("PacooData/%Y%m/%d/")
        file = datetime.datetime.now().strftime("%H%M%S_img.png")
        op.push_results_to_clipboard("Recognizing " + fold + file+ " picture, please wait.")

        if not os.path.exists(fold):
            os.makedirs(fold)
        is_up = False
        if width > 10 or height > 10:
            img_name = os.path.join(fold, file)
            pix.save(img_name)
            is_up, img_url = ip.upload_img(img_name)
            print("成功截图：", img_name)
        if is_up:
            print("成功转换：", img_name)
            api_settings = {
                'account': self.ui.account_le.text(),
                'passwd': self.ui.password_le.text(),
                'link': self.ui.link_le.text()
            }
            if self.ui.dev_api_cb.isChecked():
                print("开始识别：调用自己的开发者账号接口...")
                if self.ui.password_le.text() == "" or self.ui.account_le.text() == "":
                    is_ocr = False
                    ocr_respond = {'err_msg':"account info is null"}
                else:
                    is_ocr, ocr_respond = op.request_ocr(api_settings, img_url)
            else:
                print("开始识别：调用Pacoo提供的服务...")
                if self.ui.link_le.text() == "":
                    is_ocr = False
                    ocr_respond = {'err_msg': "link is null"}
                else:
                    is_ocr, ocr_respond = op.ocr_by_post(api_settings, img_url)

            if is_ocr:
                if self.ui.rb_word.isChecked():
                    op.push_results_to_clipboard(ocr_respond["mathml_wd"])
                else:
                    op.push_results_to_clipboard(ocr_respond["latex_stl"])
                print("成功识别：已经将结果复制到剪贴板。")
                op.play_sound("success")
                self.ui.left_label.setText(str(ocr_respond['left_times']))
                with open(img_name[:-3] + "txt", "w", encoding="utf-8") as f:
                    f.write(ocr_respond["latex_stl"] + "\n\n" + ocr_respond["mathml_wd"])
            else:
                warning_msg = "公式识别失败！错误原因：\n"
                if ocr_respond['err_msg'] == "version too old":
                    warning_msg = warning_msg + "软件版本过低，请升级软件。"
                if ocr_respond['err_msg'] == "link is null":
                    warning_msg = warning_msg + "动态链接为空。请至公众号生成链接并粘贴。"
                if ocr_respond['err_msg'] == "account info is null":
                    warning_msg = warning_msg + "开发者账号信息不完整！"
                if ocr_respond['err_msg'] == "Illegal user parameter":
                    warning_msg = warning_msg + "动态链接已经失效！请至公众号重新生成链接。"
                if ocr_respond['err_msg'] == "p-value is too small":
                    warning_msg = warning_msg + "剩余次数不足！请至公众号回复[充值]。"
                if ocr_respond['err_msg'] == "Network error, try again later":
                    warning_msg = warning_msg + "调用API时出错，请重试"
                if ocr_respond['err_msg'] == "Image is too hard":
                    warning_msg = warning_msg + "图片太难，换张图片"
                if ocr_respond['err_msg'] == "error":
                    warning_msg = warning_msg + "可能是账号信息有误、网络连接不好、公式过于复杂等。"
                op.play_sound("failed")
                QMessageBox.about(self, "Pacoo", warning_msg )
        else:
            op.play_sound("failed")
            QMessageBox.about(self, "Pacoo", "图片不存在！可能是你没有截图。" )
        self.ui.set_process_status(False)
        self.close()


    def paintEvent(self, event):
        '''
        给出截图的辅助线
        :param event:
        :return:
        '''
        # logger.debug('开始画图')
        x = self.start[0]
        y = self.start[1]
        w = self.end[0] - x
        h = self.end[1] - y

        pp = QPainter(self)
        pp.drawRect(x, y, w, h)

    def mousePressEvent(self, event):

        # 点击左键开始选取截图区域
        if event.button() == Qt.LeftButton:
            self.start = (event.pos().x(), event.pos().y())
            # print('开始坐标:', self.start)

    def mouseReleaseEvent(self, event):

        # 鼠标左键释放开始截图操作
        if event.button() == Qt.LeftButton:
            self.end = (event.pos().x(), event.pos().y())
            # print('结束坐标:', self.end)

            self.oksignal.emit()
            # logger.debug('信号提交')
            # 进行重新绘制
            self.update()

    def mouseMoveEvent(self, event):

        # 鼠标左键按下的同时移动鼠标绘制截图辅助线
        if event.buttons() and Qt.LeftButton:
            self.end = (event.pos().x(), event.pos().y())
            # 进行重新绘制
            self.update()


def main():
    default_settings = {
        "window_height": "all",  # all, half
        "result_format": "latex",  # latex, word
        "use_dev_api": False,
        "shot_hot_key": "Alt+D",
        "ocr_hot_key": "Alt+S",
        "link": "",  # "",
        "account": "",  # 手机号或者开发者账号
        "passwd": ""  # 动态密码或者开发者密码
    }
    welcom_msg = '''
    Pacoo 公式识别桌面版
    【在 2020.10.31 下载使用本软件可向客服（微信号：pacoo1614）领取66次免费识别次数。】
    
    使用说明：
    1. 按下快捷键：Alt+D
    2. 框出要识别的公式
    3. 在需要插入公式的地方粘贴
    '''
    print(welcom_msg)
    op.play_sound("welcome")
    try:
        homeDir = os.path.expanduser("~")
        with open(homeDir+"\\pacoo.conf", "r") as f:
            settings = json.load(f)
    except:
        settings = default_settings
    app = QApplication(sys.argv)
    window = MyWin(settings)

    keybinder.init()
    unregistered = False
    def callback():
        print("hello world")

    def start_oct():
        window.click_btn()

    def exit_app():
        window.close()

    def unregister():
        keybinder.unregister_hotkey(window.winId(), "Shift+Ctrl+A")
        print("unregister and register previous binding")
        keybinder.register_hotkey(window.winId(), "Shift+Ctrl+A", callback)

    keybinder.register_hotkey(window.winId(), "Shift+Ctrl+A", callback)
    keybinder.register_hotkey(window.winId(), "Alt+D", start_oct)

    # Install a native event filter to receive events from the OS
    win_event_filter = WinEventFilter(keybinder)
    event_dispatcher = QAbstractEventDispatcher.instance()
    event_dispatcher.installNativeEventFilter(win_event_filter)

    window.show()
    sys.exit(app.exec_())

class WinEventFilter(QAbstractNativeEventFilter):
    def __init__(self, keybinder):
        self.keybinder = keybinder
        super().__init__()

    def nativeEventFilter(self, eventType, message):
        ret = self.keybinder.handler(eventType, message)
        return ret, 0

if __name__ == '__main__':
    text = "ddd"
    main()
