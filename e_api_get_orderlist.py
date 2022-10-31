# -*- coding: utf-8 -*-
# Copyright (c) 2021 Tachibana Securities Co., Ltd. All rights reserved.

# 2021.07.08,   yo.
# 2022.10.20 reviced,   yo.
# Python 3.6.8 / centos7.4
# API v4r3 で動作確認
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
# 機能: ログイン、注文約定一覧取得、ログアウト。
#
# 利用方法: コード後半にある「プログラム始点」以下の設定項目を自身の設定に変更してご利用ください。
#
# == ご注意: ========================================
#   本番環境にに接続した場合、実際に市場に注文を出せます。
#   市場で約定した場合取り消せません。
# ==================================================
#

import urllib3
import datetime
import json
import time


#--- 共通コード ------------------------------------------------------

# request項目を保存するクラス。配列として使う。
# 'p_no'、'p_sd_date'は格納せず、func_make_url_requestで生成する。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = func_check_json_dquat(work_key)
        self.str_value = func_check_json_dquat(work_value)


# 口座属性クラス
class class_def_cust_property:
    def __init__(self):
        self.sUrlRequest = ''       # request用仮想URL
        self.sUrlMaster = ''        # master用仮想URL
        self.sUrlPrice = ''         # price用仮想URL
        self.sUrlEvent = ''         # event用仮想URL
        self.sZyoutoekiKazeiC = ''  # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
        self.sSecondPassword = ''   # 22.第二パスワード  APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
        self.sJsonOfmt = ''         # 返り値の表示形式指定
        


# 機能: システム時刻を"p_sd_date"の書式の文字列で返す。
# 返値: "p_sd_date"の書式の文字列
# 引数1: システム時刻
# 備考:  "p_sd_date"の書式：YYYY.MM.DD-hh:mm:ss.sss
def func_p_sd_date(int_systime):
    str_psddate = ''
    str_psddate = str_psddate + str(int_systime.year) 
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
    str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
    str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
    return str_psddate


# JSONの値の前後にダブルクオーテーションが無い場合付ける。
def func_check_json_dquat(str_value) :
    if len(str_value) == 0 :
        str_value = '""'
        
    if not str_value[:1] == '"' :
        str_value = '"' + str_value
        
    if not str_value[-1:] == '"' :
        str_value = str_value + '"'
        
    return str_value
    
    
# 受けたテキストの１文字目と最終文字の「"」を削除
# 引数：string
# 返り値：string
def func_strip_dquot(text):
    if len(text) > 0:
        if text[0:1] == '"' :
            text = text[1:]
            
    if len(text) > 0:
        if text[-1] == '\n':
            text = text[0:-1]
        
    if len(text) > 0:
        if text[-1:] == '"':
            text = text[0:-1]
        
    return text
    


# 機能: URLエンコード文字の変換
# 引数1: 文字列
# 返値: URLエンコード文字に変換した文字列
# 
# URLに「#」「+」「/」「:」「=」などの記号を利用した場合エラーとなる場合がある。
# APIへの入力文字列（特にパスワードで記号を利用している場合）で注意が必要。
#   '#' →   '%23'
#   '+' →   '%2B'
#   '/' →   '%2F'
#   ':' →   '%3A'
#   '=' →   '%3D'
def func_replace_urlecnode( str_input ):
    str_encode = ''
    str_replace = ''
    
    for i in range(len(str_input)):
        str_char = str_input[i:i+1]

        if str_char == ' ' :
            str_replace = '%20'       #「 」 → 「%20」 半角空白
        elif str_char == '!' :
            str_replace = '%21'       #「!」 → 「%21」
        elif str_char == '"' :
            str_replace = '%22'       #「"」 → 「%22」
        elif str_char == '#' :
            str_replace = '%23'       #「#」 → 「%23」
        elif str_char == '$' :
            str_replace = '%24'       #「$」 → 「%24」
        elif str_char == '%' :
            str_replace = '%25'       #「%」 → 「%25」
        elif str_char == '&' :
            str_replace = '%26'       #「&」 → 「%26」
        elif str_char == "'" :
            str_replace = '%27'       #「'」 → 「%27」
        elif str_char == '(' :
            str_replace = '%28'       #「(」 → 「%28」
        elif str_char == ')' :
            str_replace = '%29'       #「)」 → 「%29」
        elif str_char == '*' :
            str_replace = '%2A'       #「*」 → 「%2A」
        elif str_char == '+' :
            str_replace = '%2B'       #「+」 → 「%2B」
        elif str_char == ',' :
            str_replace = '%2C'       #「,」 → 「%2C」
        elif str_char == '/' :
            str_replace = '%2F'       #「/」 → 「%2F」
        elif str_char == ':' :
            str_replace = '%3A'       #「:」 → 「%3A」
        elif str_char == ';' :
            str_replace = '%3B'       #「;」 → 「%3B」
        elif str_char == '<' :
            str_replace = '%3C'       #「<」 → 「%3C」
        elif str_char == '=' :
            str_replace = '%3D'       #「=」 → 「%3D」
        elif str_char == '>' :
            str_replace = '%3E'       #「>」 → 「%3E」
        elif str_char == '?' :
            str_replace = '%3F'       #「?」 → 「%3F」
        elif str_char == '@' :
            str_replace = '%40'       #「@」 → 「%40」
        elif str_char == '[' :
            str_replace = '%5B'       #「[」 → 「%5B」
        elif str_char == ']' :
            str_replace = '%5D'       #「]」 → 「%5D」
        elif str_char == '^' :
            str_replace = '%5E'       #「^」 → 「%5E」
        elif str_char == '`' :
            str_replace = '%60'       #「`」 → 「%60」
        elif str_char == '{' :
            str_replace = '%7B'       #「{」 → 「%7B」
        elif str_char == '|' :
            str_replace = '%7C'       #「|」 → 「%7C」
        elif str_char == '}' :
            str_replace = '%7D'       #「}」 → 「%7D」
        elif str_char == '~' :
            str_replace = '%7E'       #「~」 → 「%7E」
        else :
            str_replace = str_char

        str_encode = str_encode + str_replace
        
    return str_encode



# 機能： API問合せ文字列を作成し返す。
# 戻り値： url文字列
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第２引数： ログインは、APIのurlをセット。それ以外はログインで返された仮想url（'sUrlRequest'等）の値をセット。
# 第３引数： 要求項目のデータセット。クラスの配列として受取る。
def func_make_url_request(auth_flg, \
                          url_target, \
                          work_class_req) :
    
    str_url = url_target
    if auth_flg == True :
        str_url = str_url + 'auth/'
    
    str_url = str_url + '?{\n\t'
    
    for i in range(len(work_class_req)) :
        if len(work_class_req[i].str_key) > 0:
            str_url = str_url + work_class_req[i].str_key + ':' + work_class_req[i].str_value + ',\n\t'
        
    str_url = str_url[:-3] + '\n}'
    return str_url



# 機能: API問合せ。通常のrequest,price用。
# 返値: API応答（辞書型）
# 第１引数： URL文字列。
# 備考: APIに接続し、requestの文字列を送信し、応答データを辞書型で返す。
#       master取得は専用の func_api_req_muster を利用する。
def func_api_req(str_url): 
    print('送信文字列＝')
    print(str_url)  # 送信する文字列

    # APIに接続
    http = urllib3.PoolManager()
    req = http.request('GET', str_url)
    print("req.status= ", req.status )

    # 取得したデータを、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
    bytes_reqdata = req.data
    str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")

    print('返信文字列＝')
    print(str_shiftjis)

    # JSON形式の文字列を辞書型で取り出す
    json_req = json.loads(str_shiftjis)

    return json_req



# ログイン関数
# 引数1: p_noカウンター
# 引数2: アクセスするurl（'auth/'以下は付けない）
# 引数3: ユーザーID
# 引数4: パスワード
# 引数5: 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_login(int_p_no, url_base, str_userid, str_passwd, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/43 No.1 引数名:CLMAuthLoginRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLoginRequest'
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sUserId"'
    str_value = str_userid
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sPassword"'
    str_value = str_passwd
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(True, \
                                     url_base, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/43 No.2 引数名:CLMAuthLoginAck を参照してください。

    int_p_errno = int(json_return.get('p_errno'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    int_sResultCode = int(json_return.get('sResultCode'))
    # sResultCodeは、マニュアル
    # 「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、注文入力機能引数項目仕様」
    # (api_request_if_order_vOrO.pdf)
    # の p13/42 「6.メッセージ一覧」を参照ください。

    if int_p_errno ==  0 and int_sResultCode == 0:    # ログインエラーでない場合
        # ---------------------------------------------
        # ログインでの注意点
        # 契約締結前書面が未読の場合、
        # 「int_p_errno = 0 And int_sResultCode = 0」で、
        # sUrlRequest=""、sUrlEvent="" が返されログインできない。
        # ---------------------------------------------
        if len(json_return.get('sUrlRequest')) > 0 :
            # 口座属性クラスに取得した値をセット
            class_cust_property.sZyoutoekiKazeiC = json_return.get('sZyoutoekiKazeiC')
            class_cust_property.sUrlRequest = json_return.get('sUrlRequest')        # request用仮想URL
            class_cust_property.sUrlMaster = json_return.get('sUrlMaster')          # master用仮想URL
            class_cust_property.sUrlPrice = json_return.get('sUrlPrice')            # price用仮想URL
            class_cust_property.sUrlEvent = json_return.get('sUrlEvent')            # event用仮想URL
            bool_login = True
        else :
            print('契約締結前書面が未読です。')
            print('ブラウザーで標準Webにログインして確認してください。')
    else :  # ログインに問題があった場合
        print('p_errno:', json_return.get('p_errno'))
        print('p_err:', json_return.get('p_err'))
        print('sResultCode:', json_return.get('sResultCode'))
        print('sResultText:', json_return.get('sResultText'))
        print()
        bool_login = False

    return bool_login


# ログアウト
# 引数1: p_noカウンター
# 引数2: class_cust_property（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_logout(int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/43 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLogoutRequest'  # logoutを指示。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/43 No.4 引数名:CLMAuthLogoutAck を参照してください。

    int_sResultCode = int(json_return.get('sResultCode'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    if int_sResultCode ==  0 :    # ログアウトエラーでない場合
        bool_logout = True
    else :  # ログアウトに問題があった場合
        bool_logout = False

    return bool_logout

#--- 以上 共通コード -------------------------------------------------




# 参考資料（必ず最新の資料を参照してください。）
#マニュアル
#「立花証券・ｅ支店・ＡＰＩ（v4r2）、REQUEST I/F、機能毎引数項目仕様」
# (api_request_if_clumn_v4r2.pdf)
# p14/46 No.13 CLMOrderList を参照してください。
#
# 13 CLMOrderList
#  1	sCLMID	メッセージＩＤ	char*	I/O	"CLMOrderList"
#  2	sIssueCode	銘柄コード	char[12]	I/O	銘柄コード（6501 等）
#  3	sSikkouDay	注文執行予定日	char[8]	I/O	YYYYMMDD  CLMKabuCorrectOrder、CLMKabuCancelOrder、CLMOrderListDetail におけるsEigyouDayと同値
#  4	sOrderSyoukaiStatus	注文照会状態	char[1]	I/O	値無し：指定なし。 1：未約定、2：全部約定、3：一部約定、4：訂正取消(可能な注文）、5：未約定 + 一部約定
#  5	sResultCode	結果コード	char[9]	O	０：ＯＫ、０以外：CLMMsgTable.sMsgIdで検索しテキストを表示。 0～999999999、左詰め、マイナスの場合なし
#  6	sResultText	結果テキスト	char[512]	O	ShiftJis
#  7	sWarningCode	警告コード	char[9]	O	０：ＯＫ、０以外：CLMMsgTable.sMsgIdで検索しテキストを表示。 0～999999999、左詰め、マイナスの場合なし
#  8	sWarningText	警告テキスト	char[512]	O	ShiftJis
#  9	aOrderList	注文リスト （※項目数に増減がある場合は、右記のカラム数も変更すること）	char[17]	O	以下レコードを配列で設定
# 10-1	sOrderWarningCode	警告コード	char[9]	O	０：ＯＫ、０以外：CLMMsgTable.sMsgIdで検索しテキストを表示。0～999999999、左詰め、マイナスの場合なし
# 11-2	sOrderWarningText	警告テキスト	char[512]	O	ShiftJis
# 12-3	sOrderOrderNumber	注文番号	char[8]	O	0～99999999、左詰め、マイナスの場合なし
# 13-4	sOrderIssueCode	銘柄コード	char[12]	O	-
# 14-5	sOrderSizyouC	市場	char[2]	O	00：東証
# 15-6	sOrderZyoutoekiKazeiC	譲渡益課税区分	char[1]	O	1：特定、3：一般、5：NISA
# 16-7	sGenkinSinyouKubun	現金信用区分	char[1]	O	0：現物、2：新規(制度信用6ヶ月)、4：返済(制度信用6ヶ月)、6：新規(一般信用6ヶ月)、8：返済(一般信用6ヶ月)
# 17-8	sOrderBensaiKubun	弁済区分	char[2]	O	00：なし、26：制度信用6ヶ月、29：制度信用無期限、36：一般信用6ヶ月、39：一般信用無期限
# 18-9	sOrderBaibaiKubun	売買区分	char[1]	O	1：売、3：買、5：現渡、7：現引
# 19-10	sOrderOrderSuryou	注文株数	char[13]	O	照会機能仕様書 ２－７．（３）、（１）一覧 No.12。 0～9999999999999、左詰め、マイナスの場合なし
# 20-11	sOrderCurrentSuryou	有効株数	char[13]	O	0～9999999999999、左詰め、マイナスの場合なし
# 21-12	sOrderOrderPrice	注文単価	char[14]	O	0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 22-13	sOrderCondition	執行条件	char[1]	O	0：指定なし、2：寄付、4：引け、6：不成
# 23-14	sOrderOrderPriceKubun	注文値段区分	char[1]	O	△：未使用、 1：成行、2：指値、3：親注文より高い、4：親注文より低い
# 24-15	sOrderGyakusasiOrderType	逆指値注文種別	char[1]	O	0：通常、1：逆指値、2：通常＋逆指値
# 25-16	sOrderGyakusasiZyouken	逆指値条件	char[14]	O	0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 26-17	sOrderGyakusasiKubun	逆指値値段区分	char[1]	O	△：未使用、 0：成行、1：指値
# 27-18	sOrderGyakusasiPrice	逆指値値段	char[14]	O	0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 28-19	sOrderTriggerType	トリガータイプ	char[1]	O	0：未トリガー, 1：自動, 2：手動発注, 3：手動失効。 初期状態は「0」で、トリガー発火後は「1/2/3」のどれかに遷移する
# 29-20	sOrderTatebiType	建日種類	char[1]	O	△：指定なし、 1：個別指定、2：建日順、3：単価益順、4：単価損順
# 30-21	sOrderZougen	リバース増減値	char[14]	O	項目は残すが使用しない
# 31-22	sOrderYakuzyouSuryo	成立株数	char[13]	O	0～9999999999999、左詰め、マイナスの場合なし
# 32-23	sOrderYakuzyouPrice	成立単価	char[14]	O	照会機能仕様書 ２－７．（３）、（１）一覧 No.16。 0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 33-24	sOrderUtidekiKbn	内出来区分	char[1]	O	△：約定分割以外、 2：約定分割
# 34-25	sOrderSikkouDay	執行日	char[8]	O	YYYYMMDD
# 35-26	sOrderStatusCode	状態コード	char[2]	O	
                                                                #[逆指値]、[通常+逆指値]注文時以外の状態
                                                                #0：受付未済
                                                                #1：未約定
                                                                #2：受付エラー
                                                                #3：訂正中
                                                                #4：訂正完了
                                                                #5：訂正失敗
                                                                #6：取消中
                                                                #7：取消完了
                                                                #8：取消失敗
                                                                #9：一部約定
                                                                #10：全部約定
                                                                #11：一部失効
                                                                #12：全部失効
                                                                #13：発注待ち
                                                                #14：無効
                                                                #15：切替注文
                                                                #16：切替完了
                                                                #17：切替注文失敗
                                                                #19：繰越失効
                                                                #20：一部障害処理
                                                                #21：障害処理
                                                                #[逆指値]、[通常+逆指値]注文時の状態
                                                                #15：逆指注文(切替中)
                                                                #16：逆指注文(未約定)
                                                                #17：逆指注文(失敗)
                                                                #50：発注中 
# 36-27	sOrderStatus	状態	char[20]	O	
# 37-28	sOrderYakuzyouStatus	約定ステータス	char[2]	O	0：未約定、1：一部約定、2：全部約定、3：約定中
# 38-29	sOrderOrderDateTime	注文日付	char[14]	O	YYYYMMDDHHMMSS,00000000000000
# 39-30	sOrderOrderExpireDay	有効期限	char[8]	O	YYYYMMDD,00000000
# 40-31	sOrderKurikosiOrderFlg	繰越注文フラグ	char[1]	O	0：当日注文、1：繰越注文、2：無効
# 41-32	sOrderCorrectCancelKahiFlg	訂正取消可否フラグ	char[1]	O	0：可(取消、訂正)、1：否、2：一部可(取消のみ)
# 42-33	sGaisanDaikin	概算代金	char[16]	O	-999999999999999～9999999999999999、左詰め、マイナスの場合あり




# --------------------------
# 機能: 注文約定一覧の取得
# 返値: API応答（辞書型）
# 引数1： p_no
# 引数2： class_cust_property（request通番）, 口座属性クラス
# 備考:
#       銘柄コードは省略可。''：指定なし の場合、一覧全体を取得する。
def func_get_orderlist(int_p_no, str_sOrderIssueCode, class_cust_property):

    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMOrderList'  # 注文約定一覧を指定。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sIssueCode"'
    str_value = str_sOrderIssueCode     # 銘柄コード     ''：指定なし の場合、一覧全体を取得する。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)

    json_return = func_api_req(str_url)

    return json_return











    
# ======================================================================================================
# ==== プログラム始点 =================================================================================
# ======================================================================================================

# --- 利用時に変数を設定してください -------------------------------------------------------

# 接続先 設定 --------------
# デモ環境（新バージョンになった場合、適宜変更）
my_url = 'https://demo-kabuka.e-shiten.jp/e_api_v4r2/'
##my_url = 'https://demo-kabuka.e-shiten.jp/e_api_v4r3/'

# 本番環境（新バージョンになった場合、適宜変更）
# ＊＊！！実際に市場に注文が出るので注意！！＊＊
# my_url = 'https://kabuka.e-shiten.jp/e_api_v4r3/'


# ＩＤパスワード設定 ---------
my_userid = 'MY_USERID' # 自分のuseridに書き換える
my_passwd = 'MY_PASSWD' # 自分のpasswordに書き換える
my_2pwd = 'MY_2PASSWD'  # 自分の第２passwordに書き換える

# コマンド用パラメーター -------------------    
my_sOrderIssueCode = ''    # 銘柄コード     ''：指定なし の場合、一覧全体を取得する。



# --- 以上設定項目 -------------------------------------------------------------------------


class_cust_property = class_def_cust_property()     # 口座属性クラス

# ID、パスワード、第２パスワードのURLエンコードをチェックして変換
my_userid = func_replace_urlecnode(my_userid)
my_passwd = func_replace_urlecnode(my_passwd)
class_cust_property.sSecondPassword = func_replace_urlecnode(my_2pwd)

# 返り値の表示形式指定
class_cust_property.sJsonOfmt = '5'
# "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり
# ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定

print('-- login -----------------------------------------------------')
# 送信項目、戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
# p2/46 No.1 引数名:CLMAuthLoginRequest を参照してください。
int_p_no = 1
# ログイン処理
bool_login = func_login(int_p_no, my_url, my_userid, my_passwd,  class_cust_property)

# ログインOKの場合
if bool_login :

    print()
    print('-- 注文約定一覧の取得 -------------------------------------------------------------')
    int_p_no = int_p_no + 1
    json_return = func_get_orderlist(int_p_no, my_sOrderIssueCode, class_cust_property)
    # 送信項目、戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p14/46 No.13 CLMOrderList を参照してください。
        
    print("結果コード= ", json_return.get("sResultCode"))           # 5
    print("結果テキスト= ", json_return.get("sResultText"))  # 6
    list_order = json_return.get("aOrderList")
    print('注文リスト= aOrderList')
    print('件数:', len(list_order))
    print()
    
    # 'aOrderList'の返値の処理。
    # データ形式は、"aOrderList":[{...},{...}, ... ,{...}]
    for i in range(len(list_order)):
        print('No.', i+1, '---------------')
        print('警告コード:\t', list_order[i].get('sOrderWarningCode'))
        print('警告テキスト:\t', list_order[i].get('sOrderWarningText'))
        print('注文番号:\t', list_order[i].get('sOrderOrderNumber'))
        print('銘柄コード:\t', list_order[i].get('sOrderIssueCode'))
        print('市場:\t', list_order[i].get('sOrderSizyouC'))
        print('譲渡益課税区分:\t', list_order[i].get('sOrderZyoutoekiKazeiC'))
        print('現金信用区分:\t', list_order[i].get('sGenkinSinyouKubun'))
        print('弁済区分:\t', list_order[i].get('sOrderBensaiKubun'))
        print('売買区分:\t', list_order[i].get('sOrderBaibaiKubun'))
        print('注文株数:\t', list_order[i].get('sOrderOrderSuryou'))
        print('有効株数:\t', list_order[i].get('sOrderCurrentSuryou'))
        print('注文単価:\t', list_order[i].get('sOrderOrderPrice'))
        print('執行条件:\t', list_order[i].get('sOrderCondition'))
        print('注文値段区分:\t', list_order[i].get('sOrderOrderPriceKubun'))
        print('逆指値注文種別:\t', list_order[i].get('sOrderGyakusasiOrderType'))
        print('逆指値条件:\t', list_order[i].get('sOrderGyakusasiZyouken'))
        print('逆指値値段区分:\t', list_order[i].get('sOrderGyakusasiKubun'))
        print('逆指値値段:\t', list_order[i].get('sOrderGyakusasiPrice'))
        print('トリガータイプ:\t', list_order[i].get('sOrderTriggerType'))
        print('建日種類:\t', list_order[i].get('sOrderTatebiType'))
        print('リバース増減値:\t', list_order[i].get('sOrderZougen'))
        print('成立株数:\t', list_order[i].get('sOrderYakuzyouSuryo'))
        print('成立単価:\t', list_order[i].get('sOrderYakuzyouPrice'))
        print('内出来区分:\t', list_order[i].get('sOrderUtidekiKbn'))
        print('執行日:\t', list_order[i].get('sOrderSikkouDay'))
        print('状態:\t', list_order[i].get('sOrderStatus'))
        print('約定ステータス:\t', list_order[i].get('sOrderYakuzyouStatus'))
        print('注文日付:\t', list_order[i].get('sOrderOrderDateTime'))
        print('有効期限:\t', list_order[i].get('sOrderOrderExpireDay'))
        print('繰越注文フラグ:\t', list_order[i].get('sOrderKurikosiOrderFlg'))
        print('訂正取消可否フラグ:\t', list_order[i].get('sOrderCorrectCancelKahiFlg'))
        print('概算代金:\t', list_order[i].get('sGaisanDaikin'))
        print()
        
        



    
    print()
    print('-- logout -------------------------------------------------------------')
    # 送信項目、戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/46 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    int_p_no = int_p_no + 1
    bool_logout = func_logout(int_p_no, class_cust_property)
   
else :
    print('ログインに失敗しました')
