# -*- coding: utf8 -*-
####################################################################################################################
# captureMovie.py
#   動画から画像を出力する
####################################################################################################################
import os
import cv2
import keiUtil
import configparser
import time

# 画像処理 関係
import tkinter as tk
from PIL import Image, ImageTk

# GUI関係
from tkinter import messagebox

# iniファイル読込
inifile = configparser.SafeConfigParser()
inifile.read("./settings.ini", encoding="utf-8")


####################################################################################################################
# CManagementMovie クラス
####################################################################################################################
class CManagementMovie:

    ####################################################################################################################
    # コンストラクタ
    ####################################################################################################################
    def __init__(self):
        self.path = ""

        self.crearVar()

    ####################################################################################################################
    # 変数の初期化 (及び確認用)
    ####################################################################################################################
    def crearVar(self):
        # 動画の状態
        self.setMovie = False           # 動画を読み込み済みか (スレッド生存のフラグ)

        # 入力動画の情報
        self.capture: cv2.VideoCapture  # 動画のイメージ
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

    ####################################################################################################################
    # 動画ファイルの読み込み
    ####################################################################################################################
    def readFile(self, moviePath):
        self.path = moviePath     # 読み込みファイルのパス

        # 映像(動画)の取得
        self.capture = cv2.VideoCapture(self.path)

        # 動画の情報の解析
        ret = self.analyzeMovie()
        if ret is False:
            self.capture = None
            keiUtil.logAdd(f"動画の読込に失敗 -> {self.path}", 3)
            return False

        self.fileName = os.path.splitext(os.path.basename(self.path))[0]   # 動画のファイル名
        tempfps = self.capture.get(cv2.CAP_PROP_FPS)                       # 動画の秒間フレーム数の取得
        self.fps = int(int((tempfps+0.5)*10)/10)                           # fpsを小数点以下で四捨五入
        self.totalCount = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))  # 動画の総フレーム数の取得
        self.totalMovieCount = self.getTotalMovieCount()                   # 動画の総再生時間(文字列)

        self.setMovie = True

        keiUtil.logAdd(f"動画の読込 -> {self.path}", 1)
        keiUtil.logAdd(f"「{self.fileName}」, 秒間フレーム数:{self.fps} ({self.capture.get(cv2.CAP_PROP_FPS)})")
        keiUtil.logAdd(f"総フレーム数:{self.totalCount} (再生時間：{self.totalMovieCount})")

        return True

    ####################################################################################################################
    # 動画の情報の解析
    #  引数1: str inMoviePath 入力動画のパス
    ####################################################################################################################
    def analyzeMovie(self):
        # 動画のフォーマットチェック
        totalnum = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
        if totalnum == 0:
            self.importError()
            return False

        ret, self.video_frame = self.getFramePicture()  # フレーム画像の読み込み
        if self.video_frame is None or ret is False:
            self.importError()
            return False

        return True

    ####################################################################################################################
    # 読み込んだ動画が未対応
    ####################################################################################################################
    def importError(self):
        # 読み込んだ動画が未対応のファイル形式だった
        errorText = "動画が対応していないか壊れています。/n"
        tk.messagebox.showwarning(title="ImportError", message=f"{errorText}/n{self.path}")
        keiUtil.logAdd(f"{errorText} -> {self.path}")

    ####################################################################################################################
    # 動画の総再生時間を取得する
    ####################################################################################################################
    def getTotalMovieCount(self):
        maxTime = keiUtil.secToTime((int)(self.totalCount/self.fps))
        return f"{maxTime[0]:02d}:{maxTime[1]:02d}:{maxTime[2]:02d}"

    ####################################################################################################################
    # イメージの解放
    ####################################################################################################################
    def releaseCapture(self):
        # 動画イメージの解放
        if self.setMovie is True:       # 念のためチェック
            self.capture.release()
            self.setMovie = False

    ####################################################################################################################
    # フレームに画像の取得
    ####################################################################################################################
    def getFramePicture(self):
        # フレームに画像の取得
        ret, self.video_frame = self.capture.read()
        if ret is False:
            # フレーム画像の取得に失敗
            frame_Num = int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))

            if frame_Num != self.totalCount:
                text = "画像の取得に失敗しました。"
#               tk.messagebox.showerror("画像取得エラー", f"{text}\n\n{frame_Num}フレーム目:{self.myVideo.path}")
                keiUtil.logAdd(f"{text}\n -> {frame_Num}フレーム目:{self.path}", 3)
                self.video_frame = None

        return ret, self.video_frame

    ####################################################################################################################
    # 動画の総再生時間を取得する
    ####################################################################################################################
    def checkAndReadVideoFrame(self):
        if self.video_frame is None:
            # フレームに画像がない時、画像を取得
            ret = self.getFramePicture()
            if ret is False:
                return False

        return True


####################################################################################################################
# CPlayMovie クラス
####################################################################################################################
class CPlayMovie:

    ####################################################################################################################
    # コンストラクタ
    ####################################################################################################################
    def __init__(self, parent, myVideo, view):
        self.parent = parent
        self.myVideo = myVideo
        self.view = view

    ####################################################################################################################
    # スレッドループでの処理      ※ 現在のフレームの内容で描画を更新する
    ####################################################################################################################
    def playMovie_func(self):

        if self.parent.s_st.bSynchronizationPlayingTime is True:
            start = time.time()

        # フレーム画像の読み込み
        ret, self.myVideo.video_frame = self.myVideo.getFramePicture()

        if ret:
            self.moveCountUp()      # 読み込んだ画像でイメージを更新する

            if self.parent.s_st.bSynchronizationPlayingTime is True:
                diff = time.time() - start  # 処理にかかった時間
                tempWait = float((1/self.myVideo.fps) - diff)
                if (1/self.myVideo.fps) > diff:
                    # 処理時間が早い場合待つ
                    time.sleep(tempWait)
                else:
                    print("遅延")     # デバッグ用

        else:
            self.parent.s_st.bPlayingMovie = False  # 再生を終了する
            self.view.duringPlayMovie(False)        # コントロールの有効化

    ####################################################################################################################
    # 現在のフレームの内容で描画を更新する
    ####################################################################################################################
    def moveCountUp(self):
        # キャンバス画像を更新
        self.updateCanvasImage()

        # 現在の動画位置を取得し、描画のカウントを更新する
        frame_Num = int(self.myVideo.capture.get(cv2.CAP_PROP_POS_FRAMES))
        self.updateMovieCount(frame_Num)    # 再生秒の更新

    ####################################################################################################################
    # キャンバス画像を更新する
    ####################################################################################################################
    def updateCanvasImage(self):
        # フレーム画像の有無の確認
        if self.myVideo.video_frame is None:
            # フレーム画像の取得に失敗しているときは更新しない
            return

        # 画像の加工
        pil = self.cvtopli_color_convert(self.myVideo.video_frame)  # 読み込んだ画像を Pillow で使えるようにする
        resizedImg, resizedImgCanvas = self.resize_image(pil, self.view.CANVAS_VIEW)   # 画像のリサイズ

        # キャンバスの画像を更新する
        self.replace_canvas_image(resizedImg, self.view.CANVAS_VIEW, resizedImgCanvas)

    ####################################################################################################################
    # BGR →　RGB　変換      ※ OpenCV imread()で読むと色の順番がBGRになるため
    # ※ updateCanvasImage用
    ####################################################################################################################
    def cvtopli_color_convert(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)

    ####################################################################################################################
    # 変換した画像をキャンバスサイズにリサイズする
    # ※ updateCanvasImage用
    ####################################################################################################################
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

    ####################################################################################################################
    # 画像の置き換え
    # ※ updateCanvasImage用
    ####################################################################################################################
    def replace_canvas_image(self, resizedImg, orgCanvas, resizedImgCanvas):
        orgCanvas.photo = ImageTk.PhotoImage(resizedImg)
        orgCanvas.itemconfig(resizedImgCanvas, image=orgCanvas.photo)

    ####################################################################################################################
    # 動画の再生時間を更新する
    ####################################################################################################################
    def updateMovieCount(self, frameNum=0):
        if self.myVideo.setMovie is False:
            # 動画を読み込んでいなければ return
            return

        # スクロールバーの更新
        self.view.scale_var.set(frameNum)

        # 動画カウントの更新
        if (frameNum == 0 or (frameNum % (self.myVideo.fps)) == 0 or self.parent.s_st.bSliderMoving is True):
            # 動画読み込み時 or 1秒に1回更新
            currentTime = keiUtil.secToTime((int)(frameNum/self.myVideo.fps))
            self.view.secStr_var.set(f"{currentTime[0]:02d}:{currentTime[1]:02d}:{currentTime[2]:02d}/"
                                     f" {self.myVideo.totalMovieCount}")


####################################################################################################################
# CMovieCapture クラス
#   動画ファイルから画像を抽出し、キャンバスに描画する
####################################################################################################################
class CMovieCapture:

    ####################################################################################################################
    # コンストラクタ
    ####################################################################################################################
    def __init__(self, parent, myVideo, view):
        self.parent = parent
        self.myVideo = myVideo
        self.view = view

        self.pb_Var = tk.IntVar()       # 出力時プログレスバー用変数

    ####################################################################################################################
    # キャプチャ
    #   引数1: 出力先ファイルパス
    ####################################################################################################################
    def getCapture(self, filePath):
        ret = self.myVideo.checkAndReadVideoFrame()
        if ret is False:
            # フレーム画像の取得に失敗
            return False

        ret = self.movieOutput(self.myVideo.video_frame, filePath)
        if ret is False:
            # 画像の出力に失敗
            if self.view.cap_var.get() is False:
                text = "画像の出力に失敗しました。"
                tk.messagebox.showerror("画像出力エラー", f"{text}\n\n{filePath}")
                keiUtil.logAdd(f"{text}\n -> {filePath}", 2)

    ####################################################################################################################
    # キャプチャ (本体)
    #  引数1: 画像イメージ
    #  引数1: 出力先パス
    ####################################################################################################################
    def movieOutput(self, frame, pictPath):

        ret = cv2.imwrite(pictPath, frame)
        if ret is False:
            keiUtil.logAdd(f"画像出力失敗:{pictPath}", 2)
            return False

        keiUtil.logAdd(f"画像出力:{pictPath}")

    ####################################################################################################################
    # 動画の出力
    #  引数1: str outFolderPath 出力先フォルダ(選択場所)
    #  引数2: str StartPos      キャプチャ範囲：開始位置
    #  引数3: str EndPos        キャプチャ範囲：終了位置
    #  引数4: str captureFreq   キャプチャ頻度
    ####################################################################################################################
    def movieCapture(self, outFolderPath, StartPos, EndPos, captureFreq):

        # 出力中のボタントーンダウン
        self.parent.s_st.bOutputingPicture = True
        self.parent.view.duringOutputPicture(True)

        # 出力先フォルダがなければ作成
        pictDir = f"{outFolderPath}/{self.myVideo.fileName}/{keiUtil.getTime()}"  # 「引数の出力先フォルダ\動画のファイル名」
        os.makedirs(pictDir, exist_ok=True)

        # キャプチャ位置を開始位置に移動
        self.myVideo.capture.set(cv2.CAP_PROP_POS_FRAMES, StartPos - 1)

        # 変数の初期化
        self.parent.s_st.bStopMovieCapture = False  # 出力中止フラグの初期化
        surplus = 0                         # 出力開始位置フレームずれ用変数の初期化
        count = StartPos                    # ファイル名称フレーム用のカウンタ
        frameCount = EndPos - StartPos      # 出力範囲のフレーム数の取得
        surplus = StartPos % captureFreq    # フレームずれの取得
        if self.parent.s_st.bNotShowProgressBar is False:
            self.parent.pb_var.set(0)       # プログレスバーの値変数の初期化

        keiUtil.logAdd("キャプチャ開始", 1)

        # 動画のフレームを順番に見ていく
        while True:
            # 出力の中止
            if self.parent.s_st.bStopMovieCapture is True:
                messagebox.showinfo("キャプチャ出力", "出力を中止しました。")
                keiUtil.logAdd("キャプチャ出力中止", 3)
                if self.parent.s_st.bNotShowProgressBar is False:
                    self.parent.progress_window.destroy()
                break

            # フレームの情報を読み込む
            ret, frame = self.myVideo.getFramePicture()

            # フレームを読み込めなければループを抜ける ※ 正常終了であれば下のメッセージボックスで抜けるはず
            if ret is False:
                text = f"キャプチャ異常終了 ({count + StartPos} フレーム)"
                keiUtil.logAdd(text, 3)
                messagebox.showinfo("キャプチャ出力", f"{text}。")
                if self.parent.s_st.bNotShowProgressBar is False:
                    self.parent.progress_window.destroy()
                break

            # ファイルの出力　※キャプチャ頻度ごと(1秒 or コンボボックス設定値)
            if int(count % captureFreq) == 0 + surplus:
                # 「動画ファイル名_XXXXXX(フレーム数)_yyyymmdd_HHMMSS.png」 でファイル出力
                pictPath = f"{pictDir}/{self.myVideo.fileName}_{count:06}.png"
                cv2.imwrite(pictPath, frame)
                if self.parent.s_st.bNotLogAtOutput is False:
                    # ログを出力する
                    keiUtil.logAdd(f"画像出力:{pictPath}")
                else:
                    # ログ出力を行わない
                    print(f"画像出力:{pictPath}")

            pbNum = int(((count - StartPos)/frameCount) * 100)
            if self.parent.s_st.bNotShowProgressBar is False:
                # プログレスバー表示の更新

                self.parent.pb_var.set(pbNum)           # プログレスバーを進める
                self.parent.rateBar_var.set(f"{count - StartPos}/ {frameCount}  ({pbNum} %)")
            else:
                self.view.btnOutput_var.set(f"出力中 {pbNum}%")

            # 進捗率が100になればメッセージボックスを表示
            if count == frameCount + StartPos:
                keiUtil.logAdd("キャプチャ終了", 1)
                messagebox.showinfo("キャプチャ出力", "処理が完了しました。")
                if self.parent.s_st.bNotShowProgressBar is False:
                    self.parent.progress_window.destroy()
                break

            # カウントアップ
            count += 1

        # while END

        # 出力完了後のボタントーンアップ
        self.parent.s_st.bOutputingPicture = False
        self.parent.view.duringOutputPicture(False)


