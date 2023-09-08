# -*- coding: utf8 -*-
import os
import datetime

toolName:str = ""   # ツール名称用変数
execDay:str = ""    # 起動した日
managementArea:str = r"c:\pythonTemp"

###############################################################################
# ログファイルにテキスト出力する
#  引数1: str text      ログ文章
#  引数2: int nStatus   ログのステータス 0:INFO 1:ALERT 2:ERROR 3:CRITICAL    
###############################################################################
def logAdd(text, nMode = 0):
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

###############################################################################
# フォルダの存在確認 (なければ作成)
#  引数1: str dir_path      確認するフォルダのパス
###############################################################################
def checkExitFolder(dir_path):
    if (dir_path != "") & (os.path.isfile(dir_path) == False):
        os.makedirs(dir_path, exist_ok=True)

###############################################################################
# 日付の取得 YYMMDD のフォーマット文字列
###############################################################################
def getDay():
    now = datetime.datetime.now()
    today = f"{now:%Y%m%d}"
    return today

###############################################################################
# 現在時刻の取得 YYMMDD_HHMMSS のフォーマット文字列
###############################################################################
def getTime():
    now = datetime.datetime.now()
    nowTime = f"{now:%Y%m%d_%H%M%S}"
    return nowTime
