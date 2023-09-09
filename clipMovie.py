# -*- coding: utf8 -*-
###############################################################################
# clipMovie.py
#   動画からフレーム単位で画像を抽出する
################################################################################
import os
import sys
import time
import cv2
import threading    # スレッド処理
import keiUtil

# GUI関係
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from PIL import Image, ImageOps, ImageTk

# https://qiita.com/yutaka_m/items/f3bb883a5ffc860fcfca 参考
# qiita の yutaka_m(yuta mori) 様のページを参考にしています

###############################################################################
# ClipMovieクラス
###############################################################################
class clipMovie:
 
    ###############################################################################
 	# コンストラクタ
    ###############################################################################
    def __init__(self, main_window):

        self.inMoviePath:str             # 読み込みファイルのパス
        self.folderPath:str              # 読み込みファイルのパス
        self.movie_FileName:str = ""     # 動画のファイル名
        self.totalCount:int = 0          # 動画の総フレーム数
        self.fps:int = 0                 # 動画の総fps数
        self.capture:cv2.VideoCapture    # 映像(動画)の情報
        self.bCatchedMovie = False       # 動画ファイルを読み込み済みか
       
        # Viewの生成
        self.createView()

    ###############################################################################
 	# デストラクタ
    ###############################################################################
    def __del__(self):
        # 動画イメージの解放
        if self.bCatchedMovie == True:
            self.capture.release()
            self.bCatchedMovie = False

    ###############################################################################
    # Window の View
    ###############################################################################
    def createView(self):

        # ウィンドウの設定
        self.main_window = main_window
        self.main_window.title("Clip Movie")            # ウィンドウタイトル
        self.main_window.geometry("1200x700+100+100")   # ウィンドウサイズ(幅x高さ+位置補正)
#        self.main_window.resizable(False, False)       # ウィンドウサイズの固定 (現状は可変)

        # Variable setting
        self.movieFile_filter = [("Movie file", ".mp4")]    # 動画読み込み時のフィルタ
        self.bCatchedMovie = False  # 動画を読み込み済みかのフラグ (解放用)
        self.set_movie = True       # スレッドのループのフラグ
        self.thread_set = False     # スレッドを開始済みかのフラグ
        self.start_movie = False    # 再生中フラグ True の間フレームを更新する
        self.video_frame = None

        # エリアの分割
        self.canvas_frame = tk.Frame(self.main_window)  # 動画領域
        self.canvas_frame.place(relx=0.01, rely=0.01, relwidth=0.6, relheight=0.75)

        self.opr_canvas = tk.Frame(self.main_window)     # 動画コントロール領域
        self.opr_canvas.place(relx=0.01, rely=0.76, relwidth=0.6, relheight=0.23)

        self.path_frame = tk.Frame(self.main_window)     # ファイルパス領域
        self.path_frame.place(relx=0.61, rely=0.01, relwidth=0.37, relheight=0.20)
 
        self.opr_frame = tk.Frame(self.main_window)      # コントロール領域
        self.opr_frame.place(relx=0.61, rely=0.22, relwidth=0.37, relheight=0.77)

        # 動画領域
        self.movieStrvar = tk.StringVar()
        self.movieStrvar.set("Movie")
        self.movieLabel = tk.Label(
            self.canvas_frame, textvariable=self.movieStrvar, bg="white", relief=tk.RIDGE)  # 動画タイトル
        self.movieLabel.place(relx=0.00, rely=0.00, relwidth=0.98, relheight=0.07)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#A9A9A9")                            # 動画表示スペース
        self.canvas.place(relx=0.00, rely=0.08, relwidth=0.98, relheight=0.91)

        # 動画コントロール領域
        self.scale_var = tk.IntVar()
        self.scale = tk.Scale(
                        self.opr_canvas, orient=tk.HORIZONTAL,                              # スライダー
                        sliderlength=15, from_=0, to=300, resolution=1,
#                        showvalue=0,   # デバッグ終わったら有効化する (スケールの数字が消える)
                        variable = self.scale_var, command = self.onSliderScroll
        )                        
        self.scale.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.4)

        self.secStrvar = tk.StringVar()
        self.secStrvar.set("00:00:00/ 00:00:00")
        self.sec_count = tk.Label(self.opr_canvas, textvariable=self.secStrvar, font=(0,12))# 再生時間ラベル
        self.sec_count.place(relx=0.74, rely=0.42, relwidth=0.25, relheight=0.20)

        # 操作ボタン領域
        self.label_input = tk.Label( self.path_frame, text="読み込みファイル", anchor=tk.W)   # 読み込みファイルラベル
        self.label_input.place(relx=0.00, rely=0.00, relwidth=0.98, relheight=0.24)

        self.inPathStrvar = tk.StringVar()                                                    # 読み込みファイルパス
        self.path_input = tk.Entry(self.path_frame, textvariable=self.inPathStrvar)
        self.path_input.place(relx=0.00, rely=0.25, relwidth=0.88, relheight=0.24)

        self.button_input = self.opr_btn(self.path_frame, "開く", self.on_click_moviePath)    # ファイルを開くボタン(in)
        self.button_input.place(relx=0.89, rely=0.25, relwidth=0.10, relheight=0.24)

        self.label_output = tk.Label( self.path_frame, text="出力先パス", anchor=tk.W)        # 出力先ラベル
        self.label_output.place(relx=0.00, rely=0.50, relwidth=0.98, relheight=0.24)

        self.outPathStrvar = tk.StringVar()
        self.path_output = tk.Entry(self.path_frame, textvariable=self.outPathStrvar)           # 出力先パス
        self.path_output.place(relx=0.00, rely=0.75, relwidth=0.88, relheight=0.24)

        self.button_output = self.opr_btn(self.path_frame, "開く", self.on_click_folderPath) # ファイルを開くボタン(out)　
        self.button_output.place(relx=0.89, rely=0.75, relwidth=0.10, relheight=0.24)

        # コントロール領域
        self.button_play = self.opr_btn(self.opr_frame, "再生", self.on_click_start)    # 再生ボタン
        self.button_play.place(relx=0.00, rely=0.00, relwidth=0.32, relheight=0.20)
        self.button_play.config(state=tk.DISABLED)

        self.button_stop = self.opr_btn(self.opr_frame, "停止", self.on_click_stop)      # 停止ボタン
        self.button_stop.place(relx=0.33, rely=0.00, relwidth=0.32, relheight=0.20)
        self.button_stop.config(state=tk.DISABLED)

        self.button_Capture = self.opr_btn(self.opr_frame, "キャプチャ", self.on_click_reset)    # キャプチャボタン
        self.button_Capture.place(relx=0.66, rely=0.00, relwidth=0.32, relheight=0.20)
        self.button_Capture.config(state=tk.DISABLED)

        self.button_PosStart = self.opr_btn(self.opr_frame, "開始位置", self.onSetStart)      # 開始位置ボタン
        self.button_PosStart.place(relx=0.00, rely=0.21, relwidth=0.32, relheight=0.10)
        self.button_PosStart.config(state=tk.DISABLED)

        self.button_PosEnd = self.opr_btn(self.opr_frame, "終了位置", self.onSetEnd)      # 終了位置ボタン
        self.button_PosEnd.place(relx=0.33, rely=0.21, relwidth=0.32, relheight=0.10)
        self.button_PosEnd.config(state=tk.DISABLED)

        self.button_reset = self.opr_btn(self.opr_frame, "リセット", self.on_click_reset)    # リセットボタン
        self.button_reset.place(relx=0.66, rely=0.21, relwidth=0.32, relheight=0.10)
        self.button_reset.config(state=tk.DISABLED)

        self.button_close = self.opr_btn(self.opr_frame, "閉じる", self.on_click_close)     # 閉じるボタン
        self.button_close.place(relx=0.66, rely=0.89, relwidth=0.32, relheight=0.10)

    ###############################################################################
    # ボタン定義
    ###############################################################################
    def opr_btn(self, set_frame, btn_name, act_command):
        return tk.Button(set_frame, text=btn_name, width=10, command=act_command)

    # ###############################################################################
    # # ボタン位置定義
    # ###############################################################################
    # def opr_BtnPos(self, relxPos, relyPos, relwidthSize, relheightSize):
    #     return "relx=relxPos", "rely=relyPos", "relwidth=relwidthSize", "relheight=relheightSize"

    ###############################################################################
    # ファイルを開くボタン(in) を押したときの動作
    ###############################################################################
    def on_click_moviePath(self):
        # 入力動画のパスを取得してエディットコントロールを更新
        self.get_moviePath()       #
        self.inPathStrvar.set(self.inMoviePath)

        ret = self.analyzeMovie()
        if ret == False:
            return

        # フレームのデータを読み込む
        self.moveCountUp()
#        self.updateCanvasImage()

        # スレッドの処理を開始する
        self.thread_set = True
        self.thread_main = threading.Thread(target=self.main_thread_func)
        self.thread_main.start()

    ###############################################################################
    # ファイルを開くボタン(out) を押したときの動作
    ###############################################################################
    def on_click_folderPath(self):
        self.get_folderPath()
        self.outPathStrvar.set(self.outFolderPath)

    ###############################################################################
    # 
    ###############################################################################
    def onSetStart(self):
        print("start")

    ###############################################################################
    # 
    ###############################################################################
    def onSetEnd(self):
        print("endpos")

    ###############################################################################
    # スライダー操作
    ###############################################################################
    def onSliderScroll(self, event=None):
        # スライダー位置の画像を取得
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, self.scale_var.get())
        ret, self.video_frame = self.capture.read()         # フレーム画像の読み込み

        if ret:
            self.moveCountUp()
#            self.updateCanvasImage()                        # 読み込んだ画像でイメージを更新する
            self.updateMovieCount(int(self.scale_var.get()/self.fps) * self.fps)
        else:
            self.start_movie = False                        # 再生を終了する
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)    # 動画の最初に戻す
            self.updateCanvasImage()
            self.updateMovieCount()
    
    ###############################################################################
    # 再生ボタンを押したときの動作
    ###############################################################################
    def on_click_start(self):
        if self.bCatchedMovie == False:
            # 念のため return させる
            return

        if self.capture.get(cv2.CAP_PROP_POS_FRAMES) == self.totalCount:
            # 現在位置が動画の最後であれば最初に戻って再生開始する
            self.resetPlayStatus()

        # セット済みのフレームから動画を再生する
        self.start_movie = True
        keiUtil.logAdd(f"動画の再生開始 -> {self.inMoviePath}", 1)

        # 再生中のボタンの無効化
        self.enableWidget()

    ###############################################################################
    # 停止ボタンを押したときの動作
    ###############################################################################
    def on_click_stop(self):
        # 現在のフレームで再生を停止する
        self.start_movie = False
        keiUtil.logAdd(f"動画の再生停止 -> {self.inMoviePath}", 1)

        # ボタンの有効化
        self.enableWidget()                     # コントロールの有効化

    ###############################################################################
    # 動画の再生状態をリセットする
    ###############################################################################
    def on_click_reset(self):
        self.resetPlayStatus()

    ###############################################################################
    # リセットボタンを押したときの動作
    ###############################################################################
    def resetPlayStatus(self):
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
#        self.updateCanvasImage()
        self.moveCountUp()

        # コントロールの初期化
        self.scale_var.set(0)       # スライダーを開始位置に戻す
#        self.updateMovieCount()     # 動画の再生位置の表示を更新する
        self.enableWidget()         # コントロールの有効化

    ###############################################################################
    # 閉じるボタンを押したときの動作
    ###############################################################################
    def on_click_close(self):
        # スレッドのループから抜ける
        self.set_movie = False

        # スレッドの終了を待つ
        if self.thread_set == True:
            self.thread_main.join()

        # ウィンドウを破棄する
        self.main_window.destroy()

    ###############################################################################
    # スレッド処理
    ###############################################################################
    def main_thread_func(self):

        while self.set_movie:               # self.set_movie が True の間

            # 再生中はループの処理を繰り返す
            if self.start_movie:            # 再生中

                ret, self.video_frame = self.capture.read() # フレーム画像の読み込み

                if ret:
                    self.moveCountUp()                      # 読み込んだ画像でイメージを更新する
                else:
                    self.start_movie = False                # 再生を終了する
                    self.enableWidget()                     # コントロールの有効化

    ###############################################################################
    # ボタンの状態制御
    ###############################################################################
    def enableWidget(self):
        if self.bCatchedMovie == False:
            # 画像を読み込めていない時はボタン無効
            self.button_play.config(state=tk.DISABLED)
            self.button_stop.config(state=tk.DISABLED)
            self.button_reset.config(state=tk.DISABLED)
            self.button_PosStart.config(state=tk.DISABLED)
            self.button_PosEnd.config(state=tk.DISABLED)
            self.button_Capture.config(state=tk.DISABLED)
            self.scale.config(state=tk.DISABLED)
            return

        if self.start_movie == False:
            # 動画を再生していない (≒再生可能)
            self.button_play.config(state=tk.NORMAL)
            self.button_stop.config(state=tk.DISABLED)    # 再生中に押せない
            self.button_reset.config(state=tk.NORMAL)
            self.button_close.config(state=tk.NORMAL)
            self.button_input.config(state=tk.NORMAL)
            self.button_output.config(state=tk.NORMAL)
            self.button_PosStart.config(state=tk.NORMAL)    # 常に押せる (動画読み込み時に有効化)
            self.button_PosEnd.config(state=tk.NORMAL)      # 常に押せる (動画読み込み時に有効化)
            self.button_Capture.config(state=tk.NORMAL)
            self.scale.config(state=tk.NORMAL)          # 再生中のスライダー操作で落ちるバグがあるため封印
        else:
            self.button_play.config(state=tk.DISABLED)
            self.button_stop.config(state=tk.NORMAL)    # 再生中に押せる
            self.button_reset.config(state=tk.DISABLED)
            self.button_close.config(state=tk.DISABLED)
            self.button_input.config(state=tk.DISABLED)
            self.button_output.config(state=tk.DISABLED)
            self.button_Capture.config(state=tk.DISABLED)
            self.scale.config(state=tk.DISABLED)          # 再生中のスライダー操作で落ちるバグがあるため封印

    ###############################################################################
    # 現在のフレームの内容で描画を更新する
    ###############################################################################
    def moveCountUp(self):
        # キャンバス画像を更新
        self.updateCanvasImage()

        # 現在の動画位置を取得し、描画のカウントを更新する
        frame_Num = int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))
        self.updateMovieCount(frame_Num)    # 再生秒の更新
        self.scale_var.set(frame_Num)       # スクロールバーの更新

    ###############################################################################
    # キャンバス画像を更新する
    ###############################################################################
    def updateCanvasImage(self):
        ret, self.video_frame = self.capture.read()         # 1フレーム分の画像データを読み込む

        if ret:
            # 画像の加工
            pil = self.cvtopli_color_convert(self.video_frame)  # 読み込んだ画像を Pillow で使えるようにする
            self.effect_img, self.canvas_create = self.resize_image(pil, self.canvas)   # 画像のリサイズ

            # キャンバスの画像を更新する
            self.replace_canvas_image(self.effect_img, self.canvas, self.canvas_create)

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
        # 取得した画像のサイズ
        w = img.width
        h = img.height

        # 画像サイズに応じてリサイズを行う
        if w > h:
            resizedImg = img.resize((int(w * (self.canvasWidth / w)), int(h * (self.canvasWidth / w))))
        else:
            rresizedImg = img.resize((int(w * (self.canvasHeight / h)), int(h * (self.canvasHeight / h))))

        self.pil_img = ImageTk.PhotoImage(resizedImg)
        canvas.delete("can_pic")

        # キャンバスに画像を描画する
        resizedImgCanvas = canvas.create_image(
           self.canvasWidth/2, self.canvasHeight/2,
           anchor="center", image=self.pil_img, tag="can_pic"
        )

        return resizedImg, resizedImgCanvas
    
    ###############################################################################
    # 画像の置き換え
    # ※ updateCanvasImage用
    ###############################################################################
    def replace_canvas_image(self, pic_img, canvas_name, canvas_name_create):
        canvas_name.photo = ImageTk.PhotoImage(pic_img)
        canvas_name.itemconfig(canvas_name_create, image=canvas_name.photo)

    ###############################################################################
    # 入力動画パスを取得する
    ###############################################################################
    def get_moviePath(self):
        # ファイルダイアログを開く
        self.inMoviePath = tk.filedialog.askopenfilename(title="動画ファイルを選択してください,", filetypes=self.movieFile_filter)
        keiUtil.logAdd(f"入力動画パス:{self.inMoviePath}")
        return

    ###############################################################################
    # 出力先フォルダパスを取得する
    ###############################################################################
    def get_folderPath(self):
        # ファイルダイアログを開く
        self.outFolderPath = tk.filedialog.askdirectory(title="出力先フォルダを選択してください,")
        keiUtil.logAdd(f"出力画像パス:{self.outFolderPath}")
        return
    
    ###############################################################################
    # 動画の情報の解析
    #  引数1: str inMoviePath 入力動画のパス
    ################################################################################
    def analyzeMovie(self):
        self.canvasWidth = self.canvas.winfo_width()    # キャンバスサイズの取得    ※どこに置くべきか
        self.canvasHeight = self.canvas.winfo_height()  # キャンバスサイズの取得    ※どこに置くべきか

        # 既に読み込み済みの動画があれば開放する
        if self.bCatchedMovie == True:
            self.capture.release()
            self.canvas.delete("can_pic")
            self.video_frame = None
            self.bCatchedMovie = False

        # 動画のパスからファイル名を取得する
        self.movie_FileName = os.path.splitext(os.path.basename(self.inMoviePath))[0]
        
        # 映像(動画)の取得
        self.capture = cv2.VideoCapture(self.inMoviePath)
        self.bCatchedMovie = True
        keiUtil.logAdd(f"動画の読込 -> {self.inMoviePath}", 1)

        # 動画のフォーマットチェック
        if False == self.checkMovieFormat():
            # self.inMoviePath = ""
            # self.inPathStrvar.set(self.inMoviePath)
            # self.enableWidget()
            return False

        # 動画のフレーム数の取得
        tempfps = self.capture.get(cv2.CAP_PROP_FPS)
        self.fps = int(int((tempfps+0.5)*10)/10)                    # fpsを小数点以下で四捨五入
        keiUtil.logAdd(f"「{self.movie_FileName}」, 平均フレーム数:{self.fps} ({self.capture.get(cv2.CAP_PROP_FPS)})")

        # 動画の総フレーム数の取得
        self.totalCount = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        keiUtil.logAdd(f"総フレーム数:{self.totalCount} (再生時間：{self.getTotalMovieCount()})")

        self.scale.config(to=self.totalCount)

        # 動画タイトルの更新
        self.movieStrvar.set(self.movie_FileName)

        # 動画の時間表示の更新
        self.updateMovieCount()

        # コントロールを有効化する
        self.enableWidget()

    ###############################################################################
    # 読み込んだ動画が未対応
    ###############################################################################
    def checkMovieFormat(self):
        totalnum = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
        if totalnum == 0:
           self.importError()
           return False

        self.video_frame = self.capture.read() # フレーム画像の読み込み
        if self.video_frame is None:
           self.importError()
           return False

        return True

    ###############################################################################
    # 読み込んだ動画が未対応
    ###############################################################################
    def importError(self):
        # 読み込んだ動画が未対応のファイル形式だった
        errorText = f"動画が対応していないか壊れています。/n"
        tk.messagebox.showwarning(title="ImportError", message=f"{errorText}/n{self.inMoviePath}")
        keiUtil.logAdd(f"{errorText} -> {self.inMoviePath}")

        self.inMoviePath = ""
        self.inPathStrvar.set(self.inMoviePath)
        self.bCatchedMovie = False
        self.enableWidget()
    
    ###############################################################################
    # 動画の再生時間を更新する
    ################################################################################
    def updateMovieCount(self, frameNum=0):
        if self.bCatchedMovie == False:
            return

        if ( frameNum == 0 or (frameNum % self.fps) == 0):
            currentTime = keiUtil.secToTime((int)(frameNum/self.fps))
            maxTime = keiUtil.secToTime((int)(self.totalCount/self.fps))
            self.secStrvar.set(f"{currentTime[0]:02d}:{currentTime[1]:02d}:{currentTime[2]:02d}/"
                f" {self.getTotalMovieCount()}")    # 動画カウントの更新

    ###############################################################################
    # 動画の総時間を取得する
    ################################################################################
    def getTotalMovieCount(self):
        maxTime = keiUtil.secToTime((int)(self.totalCount/self.fps))
        return f"{maxTime[0]:02d}:{maxTime[1]:02d}:{maxTime[2]:02d}"

    ###############################################################################
    # 動画のクリッピング
    #  引数1: str OutputTime 出力時刻(文字)
    ################################################################################
    def movieClipping(self, OutputTime):
        # 変数の初期化
        count = 1           # フレーム用カウンタ
        pict_num = 0        # 出力画像の枝番

        # pythonTempフォルダがなければ作成
        os.makedirs(f"{keiUtil.managementArea}/picture/{self.movie_FileName}", exist_ok=True)

        keiUtil.logAdd("クリッピング開始, 1")
        
        # 動画のフレームを順番に見ていく
        while True:
            # フレームの情報を読み込む
            ret, frame = self.capture.read()
            
            if not ret:
                # フレームを読み込めなかったらループを抜ける
                keiUtil.logAdd("クリッピング終了, 1")
                break

            # ファイルの出力
            if int(count % self.fps) == 0:
                # 1秒ごと(暫定、秒間フレーム数毎)

                # ファイル名の枝番を更新
                pict_num = int(count // self.fps)

                # 「動画ファイル名_XXXXXX(枝番)_yyyymmdd_HHMMSS.png」 でファイル出力
                pictPath = f"./picture/sample/{self.movie_FileName}/{self.movie_FileName}_{pict_num:06}_{keiUtil.getTime()}.png"
                cv2.imwrite(pictPath, frame)
                keiUtil.logAdd(f"画像出力:{pictPath}")
            
            count += 1  # フレームのカウントアップ


###############################################################################
# 動作確認用
###############################################################################
if __name__ == "__main__":
    main_window = tk.Tk()
    clipMovie(main_window)    # Viewクラス生成
    main_window.mainloop()  # 　フレームループ処理
