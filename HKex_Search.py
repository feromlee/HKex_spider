# from requests_html import HTMLSession
import requests_html
import re


class HKex_Search:
    URL = "http://www.hkexnews.hk/sdw/search/searchsdw_c.aspx"

    def __init__(self):
        self.session = requests_html.HTMLSession()

    def get_hiddenvalues(self, url=URL):

        resu = self.session.get(url).html.html
        # print(resu)
        VIEWSTATE = re.findall(r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />', resu, re.I)
        EVENTVALIDATION = re.findall(r'input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)" />', resu, re.I)
        VIEWSTATEGENERATOR = re.findall(r'input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />', resu, re.I)

        if len(VIEWSTATE) >= 1:
            VIEWSTATE = VIEWSTATE[0]
        else:
            VIEWSTATE = ""
        if len(EVENTVALIDATION) >= 1:
            EVENTVALIDATION = EVENTVALIDATION[0]
        else:
            EVENTVALIDATION = ""

        if len(VIEWSTATEGENERATOR) >= 1:
            VIEWSTATEGENERATOR = VIEWSTATEGENERATOR[0]
        else:
            VIEWSTATEGENERATOR = ""

        return VIEWSTATE, EVENTVALIDATION, VIEWSTATEGENERATOR

    def get_data(self, searchDate, stockcode):
        '''
        因为HKEX不添加__VIEWSTATE也可以获得数据，因此我这里就只给三个参数就OK,其他忽略掉
        '''

        col_participant_id = 1
        col_participant_name = 3
        col_shareholding = 7
        col_shareholding_percent = 9
        col_default_count = 10

        postdata = {
            '__EVENTTARGET': 'btnSearch',
            # '__EVENTARGUMENT': '',
            # '__VIEWSTATE': __VIEWSTATE,
            # "__VIEWSTATEGENERATOR": "3B50BBBD",
            # "today": "20190416",
            # "sortBy": "shareholding",
            # "sortDirection": "desc",
            # "alertMsg": "",
            # "txtShareholdingDate": "2018/04/18",
            "txtShareholdingDate": searchDate,
            # "txtStockCode": "00876",
            "txtStockCode": stockcode,
            # "txtStockName": "",
            # "txtParticipantID": "",
            # "txtParticipantName": "",
            # "txtSetPartId": ""
        }

        response = self.session.post(self.URL, data=postdata)
        # print(response.html.html)

        content = response.html.find('tbody', first=True)
        if content!=None:
            # print(content.html)
            tr_list = content.find('tr', first=False)

            table_data = []
            searchDate=str(searchDate).replace("/","")
            for tr in tr_list:
                table_tr = []
                items = tr.text.split('\n')
                if len(items) == 10: #10,就是券商ID不是空的
                    table_tr.append(searchDate)
                    table_tr.append(searchDate[:6])
                    table_tr.append(searchDate[:4])
                    table_tr.append(items[col_participant_id]) #官网返回数据 ie. C00074
                    table_tr.append(items[col_participant_name]) #官网返回数据 ie. 德意志银行
                    table_tr.append(str(items[col_shareholding]).replace(",","")) #官网返回数据 2,166,010,491
                    table_tr.append(items[col_shareholding_percent]) #官网返回数据  42.95%



                    table_data.append(table_tr)
                if len(items) == 9:  # 9,就是券商ID是空的
                    table_tr.append(searchDate)
                    table_tr.append(searchDate[:6])
                    table_tr.append(searchDate[:4])
                    table_tr.append("") # 空
                    table_tr.append(items[col_participant_name-1])
                    table_tr.append(str(items[col_shareholding-1]).replace(",",""))
                    table_tr.append(items[col_shareholding_percent-1])
                    table_data.append(table_tr)

                    pass
                # table_data.append([20090417, items[col_participant_id].strip(), items[col_participant_name].strip(), items[col_shareholding].strip(), items[col_shareholding_percent].strip()])

            # print(table_data)
            return table_data
        else:
            return None


