import time
import datetime
from PyQt5.QtWidgets import QMessageBox


def get_date_list(start=None, end=None):
    '''
    start: date formatted string, ie, "2019/06/23"
    end: date formatted string
    '''

    def gen_dates(b_date, days):
        day = datetime.timedelta(days=1)
        for i in range(days):
            yield b_date + day * i

    d1 = datetime.datetime.strptime(start, '%Y/%m/%d')
    d2 = datetime.datetime.strptime(end, '%Y/%m/%d')
    # days_gap = (d2 - d1).days

    data = []
    for d in gen_dates(d1, (d2 - d1).days):
        data.append(d.strftime('%Y/%m/%d'))
    data.append(end)
    return data

def show_confirm_dialog(title="",main_text="",additional_text=""):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setText(main_text)
    msg.setInformativeText(additional_text)
    msg.setWindowTitle(title)
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    retval = msg.exec_()
    return retval
