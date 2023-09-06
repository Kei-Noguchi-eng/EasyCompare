# -*- coding: utf8 -*-
import os
import cv2
import keiUtil

movieFileName:str = ""      # 動画のファイル名
fps:int = 0                 # 動画のfps数
capture:cv2.VideoCapture    # 映像(動画)の情報
# moviePath = r"./movie/sample/nature.mp4"    # 動画のパス(仮で固定)

###############################################################################
# 動画のクリッピング
#  引数1: str OutputTime 出力時刻(文字)
################################################################################
def clipMovie(OutputTime):
    # 変数の初期化
    count = 1           # フレーム用カウンタ
    pict_num = 0        # 出力画像の枝番

    # pythonTempフォルダがなければ作成
    os.makedirs(f"{keiUtil.managementArea}/picture/movieFileName", exist_ok=True)

    keiUtil.logAdd("クリッピング開始")
    
    # 動画のフレームを順番に見ていく
    while True:
        # フレームの情報を読み込む
        ret, frame = capture.read()
        
        if not ret:
            # フレームを読み込めなかったらループを抜ける
            keiUtil.logAdd("クリッピング終了")
            break

        # ファイルの出力
        if int(count % fps) == 0:
            # 1秒ごと(暫定、秒間フレーム数毎)

            # ファイル名の枝番を更新
            pict_num = int(count // fps)

            # 「動画ファイル名_XXXXXX(枝番)_yyyymmdd_HHMMSS.png」 でファイル出力
            pictPath = f"./picture/sample/{movieFileName}/{movieFileName}_{pict_num:06}_{keiUtil.getTime()}.png"
            cv2.imwrite(pictPath, frame)
            keiUtil.logAdd(f"画像出力:{pictPath}")
        
        count += 1  # フレームのカウントアップ

###############################################################################
# 動画の情報の解析
#  引数1: str moviePath 入力動画のパス
################################################################################
def analyzeMovie(moviePath):
    # 動画のパスからファイル名を取得する
    movieFileName = os.path.splitext(os.path.basename(moviePath))[0]    # 動画のファイル名
    
    # 映像(動画)の取得
    capture = cv2.VideoCapture(moviePath)
    keiUtil.logAdd(f"動画を読み込みました。\n ->{moviePath}")

    # 動画のフレーム数の取得
    fps = capture.get(cv2.CAP_PROP_FPS)
    keiUtil.logAdd(f"{movieFileName} フレーム数:{fps}")
