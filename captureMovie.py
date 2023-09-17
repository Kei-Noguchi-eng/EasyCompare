# -*- coding: utf8 -*-
###############################################################################
# captureMovie.py
#   動画から画像を出力する
################################################################################
import os
import cv2
import keiUtil
import tkinter as tk    # メッセージボックス表示用
import configparser
import keiUtil
import cv2
import time


# gazousyori 関係
import tkinter as tk
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
#from PIL import Image, ImageOps, ImageTk

# GUI関係
import tkinter as tk

# iniファイル読込
inifile = configparser.SafeConfigParser()
inifile.read("./settings.ini", encoding="utf-8")

###############################################################################
# ManagementMovie クラス
###############################################################################
class ManagementMovie:

    ###############################################################################
    # コンストラクタ
    ###############################################################################
    def __init__(self):
        self.path = ""

        self.crearVar()

    ###############################################################################
    # 変数の初期化 (及び確認用)
    ################################################################################
    def crearVar(self):
        # 動画の状態
        self.setMovie = False           # 動画を読み込み済みか (スレッド生存のフラグ)

        # 入力動画の情報
        self.capture:cv2.VideoCapture   # 動画のイメージ
        self.video_frame = None         # 動画から読みだしたフレーム画像
        self.path = ""                  # 動画のパス
        self.fileName = ""              # 動画のファイル名
        self.fps = 0                    # 動画の平均fps
        self.totalCount = 0             # 動画の総フレーム数の取得
        self.totalMovieCount = ""       # 動画の総再生時間(文字列)

        # 動画の出力設定
        self.playFps = 0                # 再生時の設定
        self.outputStartPos = 0         # 動画出力範囲(開始位置)
        self.outputEndPos = 0           # 動画出力範囲(終了位置)

    ###############################################################################
    # 動画ファイルの読み込み
    ###############################################################################
    def readFile(self, moviePath):
        self.path = moviePath     # 読み込みファイルのパス

        # 映像(動画)の取得
        self.capture = cv2.VideoCapture(self.path)

        self.fileName = os.path.splitext(os.path.basename(self.path))[0]  # 動画のファイル名
        tempfps = self.capture.get(cv2.CAP_PROP_FPS)                      # 動画の秒間フレーム数の取得
        self.fps= int(int((tempfps+0.5)*10)/10)                           # fpsを小数点以下で四捨五入           
        self.totalCount = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT)) # 動画の総フレーム数の取得
        self.totalMovieCount = self.getTotalMovieCount()                  # 動画の総再生時間(文字列)

        self.setMovie = True

        keiUtil.logAdd(f"動画の読込 -> {self.path}", 1)
        keiUtil.logAdd(f"「{self.fileName}」, 秒間フレーム数:{self.fps} ({self.capture.get(cv2.CAP_PROP_FPS)})")
        keiUtil.logAdd(f"総フレーム数:{self.totalCount} (再生時間：{self.totalMovieCount})")
 
    ###############################################################################
    # 動画の総再生時間を取得する
    ################################################################################
    def getTotalMovieCount(self):
        maxTime = keiUtil.secToTime((int)(self.totalCount/self.fps))
        return f"{maxTime[0]:02d}:{maxTime[1]:02d}:{maxTime[2]:02d}"

    ###############################################################################
    # イメージの解放
    ###############################################################################
    def releaseCapture(self):
        # 動画イメージの解放
        if self.setMovie == True:       # 念のためチェック
            self.capture.release()
            self.setMovie = False

    ###############################################################################
    # 動画の情報の解析
    #  引数1: str inMoviePath 入力動画のパス
    ################################################################################
    def analyzeMovie(self):
        # 動画のフォーマットチェック
        totalnum = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
        if totalnum == 0:
            self.importError()
            return False

        ret, self.video_frame = self.capture.read() # フレーム画像の読み込み
        if self.video_frame is None or ret == False:
            self.importError()
            return False

        return True

    ###############################################################################
    # 読み込んだ動画が未対応
    ###############################################################################
    def importError(self):
        # 読み込んだ動画が未対応のファイル形式だった
        errorText = f"動画が対応していないか壊れています。/n"
        tk.messagebox.showwarning(title="ImportError", message=f"{errorText}/n{self.path}")
        keiUtil.logAdd(f"{errorText} -> {self.path}") 

###############################################################################
# PlayMovie クラス
###############################################################################
class PlayMovie:

    ###############################################################################
    # コンストラクタ
    ###############################################################################
    def __init__(self, parent, myVideo, view):
        self.parent = parent
        self.myVideo = myVideo
        self.view = view

    ###############################################################################
    # 現在のフレームの内容で描画を更新する
    ###############################################################################
    def PlayMovie_func(self):
        start = time.time()

        ret, self.myVideo.video_frame = self.myVideo.capture.read() # フレーム画像の読み込み

        if ret:
            self.moveCountUp(self.myVideo.video_frame)                      # 読み込んだ画像でイメージを更新する
            diff = time.time() - start
            tempWait = float((1/self.myVideo.fps) - diff - start)
            if (1/self.myVideo.fps) < float((1/self.myVideo.fps) - diff):
                time.sleep(tempWait)
            else:
                print("遅延")

        else:
            self.parent.s_st.playingMovie = False               # 再生を終了する
            self.view.enableWidget()          # コントロールの有効化

    ###############################################################################
    # 現在のフレームの内容で描画を更新する
    ###############################################################################
    def moveCountUp(self, frame):
#         if self.capture.get(cv2.CAP_PROP_POS_FRAMES) < self.capture.get(cv2.CAP_PROP_FRAME_COUNT):
#             self.capture.set(cv2.CAP_PROP_POS_FRAMES, self.capture.get(cv2.CAP_PROP_POS_FRAMES))
# #            self.capture.set(cv2.CAP_PROP_POS_FRAMES, self.capture.get(cv2.CAP_PROP_POS_FRAMES))
#             return
        # キャンバス画像を更新
        self.updateCanvasImage(frame)

        # 現在の動画位置を取得し、描画のカウントを更新する
        frame_Num = int(self.myVideo.capture.get(cv2.CAP_PROP_POS_FRAMES))
        self.updateMovieCount(frame_Num)    # 再生秒の更新

    ###############################################################################
    # キャンバス画像を更新する
    ###############################################################################
    def updateCanvasImage(self, frame):
        ret, self.video_frame = self.myVideo.capture.read()

        if ret:
            # 画像の加工
            pil = self.cvtopli_color_convert(self.myVideo.video_frame)  # 読み込んだ画像を Pillow で使えるようにする
            self.resizedImg, self.resizedImgCanvas = self.resize_image(pil, self.view.CANVAS_VIEW)   # 画像のリサイズ

            # キャンバスの画像を更新する
            self.replace_canvas_image(self.resizedImg, self.view.CANVAS_VIEW, self.resizedImgCanvas)

    ###############################################################################
    # BGR →　RGB　変換      ※ OpenCV imread()で読むと色の順番がBGRになるため
    # ※ updateCanvasImage用
    ###############################################################################
    def cvtopli_color_convert(self, video):
        rgb = cv2.cvtColor(video, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)

    ###############################################################################
    # 動画した画像をキャンバスサイズにリサイズする
    # ※ updateCanvasImage用
    ###############################################################################
    def resize_image(self, img, canvas):
        # 矩形の比率を計算
        x_ratio = self.view.canvasWidth / img.width
        y_ratio = self.view.canvasHeight / img.height

        # 画像サイズに応じてリサイズを行う
        if x_ratio < y_ratio:
            resizedImg = img.resize((self.view.canvasWidth, round(img.height * x_ratio)))
        else:
            resizedImg = img.resize((round(img.width * y_ratio), self.view.canvasHeight))

        self.pil_img = ImageTk.PhotoImage(resizedImg)
        canvas.delete("can_pic")

        # キャンバスに画像を描画する
        resizedImgCanvas = canvas.create_image(
           self.view.canvasWidth/2, self.view.canvasHeight/2,
           anchor="center", image=self.pil_img, tag="can_pic"
        )

        return resizedImg, resizedImgCanvas
    
    ###############################################################################
    # 画像の置き換え
    # ※ updateCanvasImage用
    ###############################################################################
    def replace_canvas_image(self, resizedImg, orgCanvas, resizedImgCanvas):
        orgCanvas.photo = ImageTk.PhotoImage(resizedImg)
        orgCanvas.itemconfig(resizedImgCanvas, image=orgCanvas.photo)

    ###############################################################################
    # 動画の再生時間を更新する
    ################################################################################
    def updateMovieCount(self, frameNum=0):
        if self.myVideo.setMovie == False:
            # 動画を読み込んでいなければ return
            return
        
        # スクロールバーの更新
        self.view.scale_var.set(frameNum)       

        # 動画カウントの更新
        if ( frameNum == 0 or (frameNum % (self.myVideo.fps)) == 0):
            # 動画読み込み時 or 1秒に1回更新
            currentTime = keiUtil.secToTime((int)(frameNum/self.myVideo.fps))
            self.view.secStr_var.set(f"{currentTime[0]:02d}:{currentTime[1]:02d}:{currentTime[2]:02d}/"
                f" {self.myVideo.totalMovieCount}")


###############################################################################
# MovieCapture クラス
#   動画ファイルから画像を抽出し、キャンバスに描画する
################################################################################
class MovieCapture:

    ###############################################################################
    # コンストラクタ
    ###############################################################################
    def __init__(self, parent, myVideo, view):
        self.parent = parent
        self.myVideo = myVideo
        self.view = view

    ###############################################################################
    # キャプチャ出力
    #   引数1: 出力先ファイルパス
    ###############################################################################
    def getCapture(self, filePath):
        ret, self.myVideo.video_frame = self.myVideo.capture.read()
        if ret == False:
            # フレーム画像の取得に失敗
            frame_Num = int(self.myVideo.capture.get(cv2.CAP_PROP_POS_FRAMES))

            if self.cap_var.get() == False:
                text = "画像の取得に失敗しました。"
                tk.messagebox.showerror("画像取得エラー", f"{text}\n\n{frame_Num}フレーム目:{self.myVideo.path}")
            keiUtil.logAdd(f"{text}\n -> {frame_Num}フレーム目:{self.myVideo.path}", 2)
            return False        

        ret = self.movieOutput(self.myVideo.video_frame, filePath)
        if ret == False:
            # 画像の出力に失敗
            if self.view.cap_var.get() == False:
                text = "画像の出力に失敗しました。"
                tk.messagebox.showerror("画像出力エラー", f"{text}\n\n{filePath}")
            keiUtil.logAdd(f"{text}\n -> {filePath}", 2)

    ###############################################################################
    # キャプチャ出力 (本体)
    #  引数1: 画像イメージ
    #  引数1: 出力先パス
    ################################################################################
    def movieOutput(self, frame, pictPath):

        ret = cv2.imwrite(pictPath, frame)
        if ret == False:
            keiUtil.logAdd(f"画像出力失敗:{pictPath}", 2)
            return False

        keiUtil.logAdd(f"画像出力:{pictPath}")

    ###############################################################################
    # 動画のキャプチャ
    #  引数1: str outFolderPath 出力先フォルダ(選択場所)
    #  引数2: str StartPos      キャプチャ範囲：開始位置
    #  引数3: str EndPos        キャプチャ範囲：終了位置
    #  引数4: str captureFreq   キャプチャ頻度
    ################################################################################
    def movieCapture(self, outFolderPath, StartPos, EndPos, captureFreq):

        count = StartPos    # フレーム用カウンタ
        if count == 0:
            count = 1       # 最初からなら暫定で 1 からに変更 (0フレーム目を取得する処理をそのうち作る)

        # 出力先フォルダがなければ作成
        pictDir = f"{outFolderPath}/{self.myVideo.fileName}"  # 「引数の出力先フォルダ\動画のファイル名」
        os.makedirs(pictDir, exist_ok=True)

        # 開始位置の1つ前にキャプチャ位置を移動
        self.myVideo.capture.set(cv2.CAP_PROP_POS_FRAMES, StartPos - 1)

        keiUtil.logAdd("キャプチャ開始", 1)


        # 動画のフレームを順番に見ていく
        while True:
            # フレームの情報を読み込む
            ret, frame = self.myVideo.capture.read()
            
            if not ret or count == EndPos + 1:
                # 終了位置になるか、フレームを読み込めなければループを抜ける 
                keiUtil.logAdd("キャプチャ終了", 1)
                break

            # ファイルの出力
            if int(count % captureFreq) == 0:
                # キャプチャ頻度ごと(1秒 or コンボボックス設定値)

                # 「動画ファイル名_XXXXXX(フレーム数)_yyyymmdd_HHMMSS.png」 でファイル出力
                pictPath = f"{pictDir}/{self.myVideo.fileName}_{count:06}_{keiUtil.getTime()}.png"
                cv2.imwrite(pictPath, frame)
                keiUtil.logAdd(f"画像出力:{pictPath}")

            count += 1  # カウントアップ


        # 簡易キャプチャ用連番取得
        self.parent.updateTempcapNum()



