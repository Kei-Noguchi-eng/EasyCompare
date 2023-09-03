import os
import cv2
import datetime

count = 1                               # フレーム用カウンタ
pict_num = 0                            # 出力画像の枝番
moviePath = r"movie/SampleMovie.mp4"    # 動画のパス(仮で固定)
movieFileName = os.path.splitext(os.path.basename(moviePath))[0]    # 動画のファイル名
strOutputTime = "{:%Y%m%d_%H%M%S}".format(datetime.datetime.now())  # ファイル出力時刻

# 映像(動画)の取得
capture = cv2.VideoCapture(moviePath)

# 動画のフレーム数の取得
fps = capture.get(cv2.CAP_PROP_FPS)
#print(fps)

# 動画のフレームを順番に見ていく
while True:
    # フレームの情報を読み込む
    ret, frame = capture.read()
    
    if not ret:
        # フレームを読み込めなかったらループを抜ける
        break

    # ファイルの出力
    if int(count % fps) == 0:
        # 1秒ごと(暫定、秒間フレーム数毎)

        # ファイル名の枝番を更新
        pict_num = int(count // fps)

        # 「動画ファイル名_XXXXXX(枝番)_yyyymmdd_HHMMSS.png」 でファイル出力
        cv2.imwrite(f"./picture/{movieFileName}_{pict_num:06}_{strOutputTime}.png", frame)
    
    count += 1  # フレームのカウントアップ