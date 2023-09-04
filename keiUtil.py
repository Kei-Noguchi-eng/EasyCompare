import os
import datetime

toolName = ""   # ツール名称用変数

# pythonTempフォルダがなければ作成
managementArea = r"c:\pythonTemp"
os.makedirs(managementArea, exist_ok=True)

# アプリケーションの起動日の取得
execDay = "{:%Y%m%d}".format(datetime.datetime.now())  # yyyymmdd


# ログに出力
def logAdd(text):
    f = open(f"{managementArea}\\log_{toolName}_{execDay}.txt", 'a', encoding='UTF-8')
    strNowTime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    f.write(f"[{strNowTime}] {text}\n")
    f.close()

# フォルダの存在確認 (なければ作成)
def checkExitFolder(dir_path):
    if dir_path != "" & os.path.isfile(dir_path) == False:
        os.makedirs(dir_path, exist_ok=True)