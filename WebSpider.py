#!/usr/bin/python
# -*- coding: UTF-8 -*-

from form_main import *
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
import mysql.connector
from myutils import *
import datetime
from datetime import timedelta, datetime
from HKex_Search import *
import configparser


class MainTest(QMainWindow, Ui_MainWindow):
    myDB = None

    def __init__(self, parent=None):
        super(MainTest, self).__init__(parent)
        self.setupUi(self)
        self.init_db()
        self.init_gui()

    def init_db(self):
        try:
            conf = configparser.ConfigParser()
            conf.read("settings.ini")
            host_val = conf.get("mysql", "host")
            database_val = conf.get("mysql", "database")
            user_val = conf.get("mysql", "user")
            password_val = conf.get("mysql", "password")
            self.myDB = mysql.connector.connect(host=host_val, user=user_val, passwd=password_val, database=database_val)
            self.gui_connect()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("MYSQL数据库连接失败")
            msg.exec()
            exit(0)



    def init_gui(self):
        self.gui_refresh_cb_security()
        # self.gui_refresh_table_security()
        self.gui_startdate.setDate(datetime.today() + timedelta(-1))
        self.gui_enddate.setDate(datetime.today() + timedelta(-1))
        self.tabWidget.removeTab(2)  # 临时关闭这个页面
        self.tabWidget.removeTab(1)  # 临时关闭这个页面

    def gui_refresh_cb_security(self):
        mycursor = self.myDB.cursor()
        mycursor.execute("SELECT security_id,security_name FROM security")
        security_id = mycursor.column_names.index('security_id')
        security_name = mycursor.column_names.index('security_name')
        myresult = mycursor.fetchall()
        self.cb_security.clear()
        for row in myresult:
            self.cb_security.addItem(str(row[security_id]) + ":" + row[security_name])
            # self.cb_security.addItem("aaaa")

    def gui_refresh_table_security(self):
        mycursor = self.myDB.cursor()
        mycursor.execute("SELECT security_id,security_name FROM security")
        security_id = mycursor.column_names.index('security_id')
        security_name = mycursor.column_names.index('security_name')
        result = mycursor.fetchall()
        self.table_security.clearContents()
        self.table_security.setRowCount(0)
        row_count = 0
        for row in result:
            self.table_security.setRowCount(row_count + 1)
            self.table_security.setItem(row_count, 0, QTableWidgetItem(str(row[security_id])))
            self.table_security.setItem(row_count, 1, QTableWidgetItem(row[security_name]))
            row_count = row_count + 1
        mycursor.close()

    def do_search(self):
        mysearch = HKex_Search()
        starddate = self.gui_startdate.text()
        enddate = self.gui_enddate.text()
        security = self.cb_security.currentText().split(':')
        security_id = security[0].zfill(5)
        security_name = security[1]

        date_list = get_date_list(starddate, enddate)
        self.table_task.clearContents()
        self.table_task.setRowCount(0)
        row_count = 0
        search_list = []
        for sdate in date_list:
            self.table_task.setRowCount(row_count + 1)
            self.table_task.setItem(row_count, 0, QTableWidgetItem(sdate))
            self.table_task.setItem(row_count, 1, QTableWidgetItem(security_id))
            self.table_task.setItem(row_count, 2, QTableWidgetItem(security_name))
            self.table_task.setItem(row_count, 3, QTableWidgetItem('---'))
            search_list.append([sdate, security_id])
            row_count = row_count + 1
            app.processEvents()

        table_name = 'rawdata_' + str(security_id)

        mycursor = self.myDB.cursor()
        row_count = 0
        for item in search_list:
            self.table_task.scrollToItem(self.table_task.item(row_count, 0))
            target_date = item[0].replace("/", "")
            target_security_id = item[1]
            self.table_task.setItem(row_count, 3, QTableWidgetItem('正在从港交所获取数据'))
            app.processEvents()
            r = mysearch.get_data(item[0], item[1])
            # 批量加入
            if r != None:
                sqlstr = ""
                try:
                    sql_str = 'delete from ' + table_name + " where dday=" + target_date
                    mycursor.execute(sql_str)
                    self.myDB.commit()
                    # self.table_task.setItem(row_count, 3, QTableWidgetItem('删除旧数据'))
                    # app.processEvents()
                    # time.sleep(0.5)

                    self.table_task.setItem(row_count, 3, QTableWidgetItem('更新最新数据'))
                    app.processEvents()
                    time.sleep(0.5)
                    sql = 'INSERT INTO ' + table_name + " (security_id,security_name,dday,dmonth,dyear,broker_id,broker_name,shareholding,holding_percent) values(" + security_id + ",'" + security_name + "',%s,%s,%s,%s,%s,%s,%s)"
                    # 批量插入
                    mycursor.executemany(sql, r)
                    self.myDB.commit()
                    self.table_task.setItem(row_count, 3, QTableWidgetItem('完成'))
                    app.processEvents()

                    pass
                except Exception as e:
                    self.table_task.setItem(row_count, 3, QTableWidgetItem(e))
                    app.processEvents()
                    # print(e)
                    self.myDB.rollback()
                    pass
            else:
                self.table_task.setItem(row_count, 3, QTableWidgetItem('无数据'))
                app.processEvents()
                pass
            time.sleep(0.5)
            row_count = row_count + 1
            app.processEvents()

        mycursor.close()

    def gui_connect(self):
        self.btn_grapdata.clicked.connect(self.do_search)
        self.btn_delete.clicked.connect(self.delete_security)

    def delete_security(self):
        row_id = self.table_security.currentRow()
        security_id = QTableWidgetItem(self.table_security.item(row_id, 0)).text()
        if security_id != '':
            r = show_confirm_dialog("删除", "确认删除证券" + str(security_id) + "吗？", "其相关的数据将会一并删除")
            if r == QMessageBox.Ok:
                mycursor = self.myDB.cursor()
                mycursor.execute("delete from security where security_id='" + str(security_id) + "'")
                self.myDB.commit()
                self.gui_refresh_cb_security()
                self.gui_refresh_table_security()
                pass


#

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MainTest()
    # myWin.showMaximized()
    myWin.show()
    sys.exit(app.exec_())
