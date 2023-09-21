# -*- coding: utf8 -*-
import os
import datetime
import configparser
import glob

toolName: str = ""   # ツール名称用変数
execDay: str = ""    # 起動した日
managementArea: str = "c:/pythonTemp"
inifile = configparser.SafeConfigParser()
inifile.read("./settings.ini", encoding="utf-8")


####################################################################################################################
# ログファイルにテキスト出力する
#  引数1: str text      ログ文章
#  引数2: int nStatus   ログのステータス 0:INFO 1:ALERT 2:ERROR 3:CRITICAL
####################################################################################################################
def logAdd(text, nMode=0):
    match nMode:
        case 0:
            label = "-------"   # 通常ログ
        case 1:
            label = "【INF】"   # info 情報
        case 2:
            label = "【ALT】"   # alert 警告
        case 3:
            label = "【ERR】"   # error エラー
        case 4:
            label = "【CRT】"   # critical 致命的なエラー
        case _:
            label = "【OTH】"   # other その他
    f = open(f"{managementArea}\\log_{toolName}_{execDay}.txt", 'a', encoding='UTF-8')
    now = datetime.datetime.now()
    text = f"{label}[{now:%Y/%m/%d(%a) %H:%M:%S}] {text}"
    print(text)    # print文に出力
    f.write(f"{text}\n")       # ログファイルに出力
    f.close()


####################################################################################################################
# フォルダの存在確認 (なければ作成)
#  引数1: str dir_path      確認するフォルダのパス
####################################################################################################################
def checkExitFolder(dir_path):
    if (dir_path != "") & (os.path.isfile(dir_path) is False):
        os.makedirs(dir_path, exist_ok=True)


####################################################################################################################
# 日付の取得 YYMMDD のフォーマット文字列
####################################################################################################################
def getDay():
    now = datetime.datetime.now()
    today = f"{now:%Y%m%d}"
    return today


####################################################################################################################
# 現在時刻の取得 YYMMDD_HHMMSS のフォーマット文字列
####################################################################################################################
def getTime():
    now = datetime.datetime.now()
    nowTime = f"{now:%Y%m%d_%H%M%S}"
    return nowTime


####################################################################################################################
# 秒数　→　時、分、秒　に変換
#  引数1: int nSec      変換元の秒数
####################################################################################################################
def secToTime(nSec):
    hh, temp = divmod(nSec, 3600)
    mm, ss = divmod(temp, 60)
    list_time = [hh, mm, ss]
#    print(f"{hh}:{mm}:{ss}")   # デバッグ用
    return list_time


####################################################################################################################
# ini ファイルの項目と一致するか確認
#  引数1: str section   対象のiniファイルのセクション名
#  引数2: str key       対象のiniファイルのkey値
#  引数3: str value     新しい設定値
####################################################################################################################
def checkIniFile(section, key, value):
    if value != inifile[section][key]:
        # 設定と iniファイルの値が異なる場合

        if inifile.has_section(section) is False:
            # セクションが存在しなければ作成
            inifile[section] = {}

        # iniファイルに書き込み
        inifile.set(section, key, value)
        with open("./settings.ini", 'w') as file:
            inifile.write(file)

        return True
    else:
        return False


####################################################################################################################
# 探索するフォルダ内の枝番の末尾を取得する (???_XXX.extフォーマット制限)
#  引数1: str serchPath   探索するパス
####################################################################################################################
def getLastFileNumber(serchPath):
    maxNum = -1

    files = glob.glob(serchPath)

    # パスと一致するファイルを探索する
    for file in files:
        # .ext 前の XXX 部分の切り取り
        strNum = file[file.rfind('_') + 1:file.rfind('.')]
        if strNum.isdecimal():
            tempNum = int(strNum)
            if tempNum > maxNum:
                maxNum = tempNum

    return maxNum + 1   # インクリメントして return
