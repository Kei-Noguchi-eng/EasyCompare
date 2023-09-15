# -*- coding: utf8 -*-
###############################################################################
# captureMovie.py
#   動画からフレーム単位で画像を抽出する
################################################################################
import os
#import sys
#import time
import cv2
import threading    # スレッド処理
import keiUtil
import configparser # これは後で外す

# GUI関係
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
#from PIL import Image, ImageOps, ImageTk

# iniファイル読込
inifile = configparser.SafeConfigParser()
inifile.read("./settings.ini", encoding="utf-8")


# 単体起動の間ここに追加
keiUtil.checkExitFolder(keiUtil.managementArea) # 管理領域の作成
keiUtil.toolName = "CaptureMovieDlg"
keiUtil.execDay = keiUtil.getDay() # アプリケーションの起動日の取得
keiUtil.logAdd("CaptureMovie 起動", 1)

# https://qiita.com/yutaka_m/items/f3bb883a5ffc860fcfca 参考
# qiita の yutaka_m(yuta mori) 様のページを参考にしています

###############################################################################
# captureMovie クラス
###############################################################################
class captureMovie(tk.Frame):
 
    ###############################################################################
 	# コンストラクタ
    ###############################################################################
    def __init__(self, main_window=None):
        super().__init__(main_window)

        # 変数初期化
        self.init_var()
       
        # Viewの生成
        self.createView()

        # ウィンドウの x ボタンが押された時
        self.master.protocol("WM_DELETE_WINDOW", self.delete_window)

    ###############################################################################
 	# デストラクタ
    ###############################################################################
    def __del__(self):
        # 動画イメージの解放
        self.release_capture()

    ###############################################################################
 	# 変数初期化
    ###############################################################################
    def init_var(self):
        self.inMovieFolder = inifile["MOVIE EDIT"]["inputMoviePath"]        # 読み込みファイルのデフォルトフォルダー
        self.inMoviePath:str             # 読み込みファイルのパス
        self.movie_FileName:str = ""     # 動画のファイル名
        self.outFolderPath = inifile["MOVIE EDIT"]["outputPicturePath"]     # 出力先フォルダのパス
        self.totalCount:int = 0          # 動画の総フレーム数
        self.fps:int = 0                 # 動画のfps数
        self.outputStartPos:int = 0      # 出力範囲の開始位置
        self.outputEndPos:int = 0        # 出力範囲の終了位置
        self.outputFreq:int = 0          # 出力頻度の設定(何フレーム毎に出力するか)
        self.capture:cv2.VideoCapture    # 映像(動画)の情報
        self.bCatchedMovie = False       # 動画ファイルを読み込み済みか
        self.bCatchedMovie = False       # 動画を読み込み済みかのフラグ (解放用)
        self.set_movie = True            # スレッドのループのフラグ
        self.thread_set = False          # スレッドを開始済みかのフラグ
        self.start_movie = False         # 再生中フラグ True の間フレームを更新する
        self.video_frame = None
        self.tempcapNum = 0              # 簡易キャプチャ用連番

    ###############################################################################
 	#  ウィンドウの×ボタンでの終了
    ###############################################################################
    def delete_window(self):
        if self.start_movie == True:
            # 再生中はメッセージを出して return
            tk.messagebox.showwarning(
            title = "終了エラー",
            message = "動画の再生中は終了できません。")
            return


        # 終了確認のメッセージ表示
        ret = tk.messagebox.askyesno(
            title = "終了確認",
            message = "プログラムを終了しますか？")

        if ret == True:
            self.release_capture()      # 動画イメージの解放
            self.master.destroy()
            keiUtil.logAdd("CaptureMovie 終了", 1)

    ###############################################################################
 	# イメージの解放
    ###############################################################################
    def release_capture(self):
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
        self.main_window.geometry("1200x600+100+100")   # ウィンドウサイズ(幅x高さ+位置補正)
        self.main_window.wm_minsize(width=1200, height=600) # ウィンドウサイズ下限
#        self.main_window.resizable(False, False)       # ウィンドウサイズの固定 (現状は可変)

        # Variable setting
        self.movieFile_filter = [("Movie file", ".mp4")]    # 動画読み込み時のフィルタ

        # エリアの分割
        self.FRAME_CANVAS = tk.Frame(self.main_window)  # 動画領域
        self.FRAME_CANVAS.place(relx=0.01, rely=0.01, relwidth=0.6, relheight=0.85)

        self.FRAME_CANVAS_OPR = tk.Frame(self.main_window)     # 動画コントロール領域
        self.FRAME_CANVAS_OPR.place(relx=0.01, rely=0.86, relwidth=0.6, relheight=0.13)

        self.FRAME_PATH = tk.Frame(self.main_window)     # ファイルパス領域
        self.FRAME_PATH.place(relx=0.61, rely=0.05, relwidth=0.37, relheight=0.15)
 
        self.FRAME_COMMAND_OPR = tk.Frame(self.main_window)      # コントロール領域
        self.FRAME_COMMAND_OPR.place(relx=0.61, rely=0.30, relwidth=0.37, relheight=0.69)

        # 動画領域
        self.movieStrvar = tk.StringVar()
        self.movieStrvar.set("Movie")
        self.movieLabel = tk.Label(
            self.FRAME_CANVAS, textvariable=self.movieStrvar, bg="white", relief=tk.RIDGE)  # 動画タイトル
        self.movieLabel.place(relx=0.00, rely=0.00, relwidth=0.98, relheight=0.07)

        self.canvas = tk.Canvas(self.FRAME_CANVAS, bg="#A9A9A9")                            # 動画表示スペース
        self.canvas.place(relx=0.00, rely=0.08, relwidth=0.98, relheight=0.91)

        # 動画コントロール領域
        self.scale_var = tk.IntVar()
        self.SCR_SCALE = tk.Scale(
                        self.FRAME_CANVAS_OPR, orient=tk.HORIZONTAL,                              # スライダー
                        sliderlength=15, from_=0, to=300, resolution=1,
#                        showvalue=0,   # デバッグ終わったら有効化する (スケールの数字が消える)
                        variable = self.scale_var, command = self.onSliderScroll
        )                        
        self.SCR_SCALE.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.65)

        self.frameAll_var = tk.StringVar()
        self.frameAll_var.set("総フレーム数： -")
        self.LBL_FLAMEALL = tk.Label( self.FRAME_CANVAS_OPR, textvariable=self.frameAll_var, font=(0,11), anchor=tk.NW)   # 走フレームラベル
        self.LBL_FLAMEALL.place(relx=0.30, rely=0.66, relwidth=0.20, relheight=0.30)

        self.frameAve_var = tk.StringVar()
        self.frameAve_var.set("秒間フレーム数：- ")
        self.LBL_FLAMEAVE = tk.Label( self.FRAME_CANVAS_OPR, textvariable=self.frameAve_var, font=(0,11), anchor=tk.NW)   # 平均フレームラベル
        self.LBL_FLAMEAVE.place(relx=0.51, rely=0.66, relwidth=0.20, relheight=0.30)

        self.secStrvar = tk.StringVar()
        self.secStrvar.set("00:00:00/ 00:00:00")
        self.LBL_SECCOUNT = tk.Label(self.FRAME_CANVAS_OPR, textvariable=self.secStrvar, font=(0,12))# 再生時間ラベル
        self.LBL_SECCOUNT.place(relx=0.72, rely=0.66, relwidth=0.25, relheight=0.30)

        # 操作ボタン領域
        self.LBL_INPUTFILE = tk.Label( self.FRAME_PATH, text="読み込みファイル", anchor=tk.W)   # 読み込みファイルラベル
        self.LBL_INPUTFILE.place(relx=0.00, rely=0.00, relwidth=0.98, relheight=0.24)

        self.inPathStrvar = tk.StringVar()                                                    # 読み込みファイルパス
        self.EDT_INPUTPATH = tk.Entry(self.FRAME_PATH, textvariable=self.inPathStrvar)
        self.EDT_INPUTPATH.place(relx=0.00, rely=0.25, relwidth=0.88, relheight=0.24)
        self.EDT_INPUTPATH.config(state="readonly")

        self.BTN_INPUTPATH = self.opr_btn(self.FRAME_PATH, "開く", self.on_click_moviePath)    # ファイルを開くボタン(in)
        self.BTN_INPUTPATH.place(relx=0.89, rely=0.25, relwidth=0.10, relheight=0.24)

        self.LBL_OUTPUTFILE = tk.Label( self.FRAME_PATH, text="出力先パス", anchor=tk.W)        # 出力先ラベル
        self.LBL_OUTPUTFILE.place(relx=0.00, rely=0.50, relwidth=0.98, relheight=0.24)

        self.outPathStrvar = tk.StringVar()
        self.EDT_OUTPUTPATH = tk.Entry(self.FRAME_PATH, textvariable=self.outPathStrvar)           # 出力先パス
        self.EDT_OUTPUTPATH.place(relx=0.00, rely=0.75, relwidth=0.88, relheight=0.24)
        self.EDT_OUTPUTPATH.config(state="readonly")

        self.BTN_OUTPUTPATH = self.opr_btn(self.FRAME_PATH, "開く", self.on_click_folderPath) # ファイルを開くボタン(out)　
        self.BTN_OUTPUTPATH.place(relx=0.89, rely=0.75, relwidth=0.10, relheight=0.24)

        # コントロール領域：ビデオ
        self.BTN_PLAY = self.opr_btn(self.FRAME_COMMAND_OPR, "再生", self.on_click_start)    # 再生ボタン
        self.BTN_PLAY.place(relx=0.00, rely=0.00, relwidth=0.32, relheight=0.20)
        self.BTN_PLAY.config(state=tk.DISABLED)

        self.BTN_STOP = self.opr_btn(self.FRAME_COMMAND_OPR, "停止", self.on_click_stop)      # 停止ボタン
        self.BTN_STOP.place(relx=0.33, rely=0.00, relwidth=0.32, relheight=0.20)
        self.BTN_STOP.config(state=tk.DISABLED)

        self.BTN_RSTPLAY = self.opr_btn(self.FRAME_COMMAND_OPR, "再生位置リセット", self.on_click_reset)    # リセットボタン
        self.BTN_RSTPLAY.place(relx=0.66, rely=0.00, relwidth=0.32, relheight=0.20)
        self.BTN_RSTPLAY.config(state=tk.DISABLED)

        # コントロール領域：画像出力範囲
        self.BTN_POSSTART = self.opr_btn(self.FRAME_COMMAND_OPR, "開始位置", self.onSetStart)      # 開始位置ボタン
        self.BTN_POSSTART.place(relx=0.00, rely=0.21, relwidth=0.32, relheight=0.10)
        self.BTN_POSSTART.config(state=tk.DISABLED)

        self.BTN_POSEND = self.opr_btn(self.FRAME_COMMAND_OPR, "終了位置", self.onSetEnd)      # 終了位置ボタン
        self.BTN_POSEND.place(relx=0.33, rely=0.21, relwidth=0.32, relheight=0.10)
        self.BTN_POSEND.config(state=tk.DISABLED)

        self.BTN_POSRST = self.opr_btn(self.FRAME_COMMAND_OPR, "範囲リセット", self.onResetRange)    # リセットボタン
        self.BTN_POSRST.place(relx=0.66, rely=0.21, relwidth=0.32, relheight=0.10)
        self.BTN_POSRST.config(state=tk.DISABLED)

        # コントロール領域：映像情報
        self.LBL_POSRANGE = tk.Label( self.FRAME_COMMAND_OPR, text="画像出力範囲", font=(0,11), anchor=tk.CENTER, background='#d0eaff')   #画像出力範囲ラベル
        self.LBL_POSRANGE.place(relx=0.01, rely=0.38, relwidth=0.31, relheight=0.05)

        self.posStart_var = tk.StringVar()
        self.posStart_var.set("開始位置: -")
        self.LBL_POSSTART = tk.Label( self.FRAME_COMMAND_OPR, textvariable=self.posStart_var, font=(0,11), anchor=tk.NW)                # 開始位置ラベル
        self.LBL_POSSTART.place(relx=0.40, rely=0.38, relwidth=0.25, relheight=0.05)

        self.posEnd_var = tk.StringVar()
        self.posEnd_var.set("終了位置: -")
        self.LBL_POSEND = tk.Label( self.FRAME_COMMAND_OPR, textvariable=self.posEnd_var, font=(0,11), anchor=tk.NW)                    # 終了位置ラベル
        self.LBL_POSEND.place(relx=0.70, rely=0.38, relwidth=0.25, relheight=0.05)

     
        self.radioValue = tk.IntVar(value = 0)     # 初期値
        self.RDO_FRQSECOND = tk.Radiobutton(self.FRAME_COMMAND_OPR, text = "1秒毎にキャプチャを出力する", font=(1,9), justify="left",       # 1秒毎ラジオボタン
                           variable = self.radioValue, value = 0)
        self.RDO_FRQSECOND.place(relx=0.00, rely=0.47, relwidth=0.40, relheight=0.05)

        self.RDO_FRQFRAME = tk.Radiobutton(self.FRAME_COMMAND_OPR, text = "", justify="left",           # フレーム指定ラジオボタン
                           variable = self.radioValue, value = 1) 
        self.RDO_FRQFRAME.place(relx=0.44, rely=0.47, relwidth=0.05, relheight=0.05)
        self.RDO_FRQFRAME.config(state=tk.DISABLED)
 
        self.freq_var = tk.StringVar()  # コンボボックスの選択値取得用変数
        self.freqList_list = ("1F")                                                                      # コンボボックス要素用変数
        self.CMB_FREQ = ttk.Combobox(self.FRAME_COMMAND_OPR, justify="right", font=(0,9),
                                     textvariable=self.freq_var, values=self.freqList_list)             # フレーム指定コンボボックス
        self.CMB_FREQ.set("1F")
        self.CMB_FREQ.place(relx=0.49, rely=0.47, relwidth=0.18, relheight=0.05)
        self.CMB_FREQ.config(state=tk.DISABLED)

        self.LBL_FREQ = tk.Label( self.FRAME_COMMAND_OPR, text="毎にキャプチャ出力する", font=(1,9), anchor=tk.NW)   # フレーム指定ラベル
        self.LBL_FREQ.place(relx=0.68, rely=0.47, relwidth=0.40, relheight=0.05)

        # コントロール領域：キャプチャ、出力、閉じるボタン
        self.BTN_CAP = self.opr_btn(self.FRAME_COMMAND_OPR, "キャプチャ", self.onBtnCapture)    # キャプチャボタン
        self.BTN_CAP.place(relx=0.02, rely=0.55, relwidth=0.45, relheight=0.30)
        self.BTN_CAP.config(state=tk.DISABLED)

        self.cap_var = tk.BooleanVar()
        self.CHK_CAP = tk.Checkbutton(self.FRAME_COMMAND_OPR, variable=self.cap_var, text="出力先指定を省略する", anchor = tk.W) # 簡易キャプチャのフラグ
        self.CHK_CAP.place(relx=0.02, rely=0.86, relwidth=0.45, relheight=0.05)
        self.CHK_CAP.config(state=tk.DISABLED)
        self.cap_var.set(False)

        self.BTN_OUTPUT = self.opr_btn(self.FRAME_COMMAND_OPR, "出力", self.onBtnOutputPicture)    # 出力ボタン
        self.BTN_OUTPUT.place(relx=0.51, rely=0.55, relwidth=0.45, relheight=0.30)
        self.BTN_OUTPUT.config(state=tk.DISABLED)

        self.BTN_CLOSE = self.opr_btn(self.FRAME_COMMAND_OPR, "閉じる", self.on_click_close)     # 閉じるボタン
        self.BTN_CLOSE.place(relx=0.66, rely=0.89, relwidth=0.32, relheight=0.10)

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
        ret = self.get_moviePath()
        if ret == False:
            return

        self.inPathStrvar.set(self.inMoviePath)

        ret = self.analyzeMovie()
        if ret == False:
            return

        # フレームのデータを読み込む
        self.moveCountUp()

        # スレッドの処理を開始する
        self.thread_set = True
        self.thread_main = threading.Thread(target=self.main_thread_func)
        self.thread_main.start()

    ###############################################################################
    # フォルダを開くボタン(out) を押したときの動作
    ###############################################################################
    def on_click_folderPath(self):
        ret = self.get_folderPath()
        if ret == False:
            return

        self.outPathStrvar.set(self.outFolderPath)

    ###############################################################################
    #  動画出力の開始位置を指定する
    ###############################################################################
    def onSetStart(self):
        self.outputStartPos = self.scale_var.get()
        self.posStart_var.set(f"開始位置: {self.outputStartPos}")
        keiUtil.logAdd(f"動画出力の開始位置を設定: {self.outputStartPos}")
        self.BTN_POSRST.config(state=tk.NORMAL)

    ###############################################################################
    #  動画出力の終了位置を指定する 
    ###############################################################################
    def onSetEnd(self):
        self.outputEndPos = self.scale_var.get()
        self.posEnd_var.set(f"終了位置: {self.outputEndPos}")
        keiUtil.logAdd(f"動画出力の終了位置を設定: {self.outputEndPos}")
        self.BTN_POSRST.config(state=tk.NORMAL)

    ###############################################################################
    #  動画出力範囲をリセットする
    ###############################################################################
    def onResetRange(self):
        self.outputStartPos = 0
        self.outputEndPos = self.totalCount
        self.posStart_var.set("開始位置: 0")
        self.posEnd_var.set(f"終了位置: {self.totalCount}")
        keiUtil.logAdd(f"動画出力範囲を初期化　0:{self.totalCount}")
        self.BTN_POSRST.config(state=tk.DISABLED)

    ###############################################################################
    # スライダー操作
    ###############################################################################
    def onSliderScroll(self, event=None):
        # スライダー位置の画像を取得
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, self.scale_var.get())
        ret, self.video_frame = self.capture.read()         # フレーム画像の読み込み

        if ret:
            self.moveCountUp()
            self.updateMovieCount(int(self.scale_var.get()/self.fps) * self.fps)    # 更新フレームずれ対策
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
            ret, self.video_frame = self.capture.read() # フレームずれ対策

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
        self.moveCountUp()

        # コントロールの初期化
        self.scale_var.set(0)       # スライダーを開始位置に戻す
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

        keiUtil.logAdd("CaptureMovie 終了", 1)

    ###############################################################################
    # キャプチャボタンを押したときの動作
    ###############################################################################
    def onBtnCapture(self):

        if self.cap_var.get() == True:
            # 簡易キャプチャが有効になっている
            tempFilePath = f"{keiUtil.managementArea}/EDIT_POOL/picture_out/temp/tempCapture_{self.movie_FileName}_{keiUtil.getTime()}_{self.tempcapNum:06}.png"

            # # ファイル名のファイルの枝番を見る
            # while True:
            #     searchFilepath = f"{keiUtil.managementArea}/EDIT_POOL/picture_out/temp/tempCapture_{self.movie_FileName}_*_{self.tempcapNum:06}.png"
            #     print(os.path.exists(searchFilepath)) # debug
            #     if os.path.exists(searchFilepath):
            #         self.tempcapNum += 1
            #     else:
            #         tempFilePath = f"{keiUtil.managementArea}/EDIT_POOL/picture_out/temp/tempCapture_{self.movie_FileName}_{keiUtil.getTime()}_{self.tempcapNum:06}.png"
            #         break
            
            # キャプチャを取得
            if False == self.getCapture(tempFilePath):
                return
            
            self.tempcapNum += 1    # カウントアップする
           

        else:
            # 出力先を選択するダイアログを表示する
            tempFilePath = filedialog.asksaveasfilename(
                title="名前を付けて保存", filetypes=[("PNG Image Files", ".png")],
                initialdir=f"{keiUtil.managementArea}/EDIT_POOL/picture_out/temp", initialfile="capture.png"
            )
            if tempFilePath == "":
                return

            # キャプチャを取得
            if False == self.getCapture(tempFilePath):
                return

    ###############################################################################
    # キャプチャ取得本体
    ###############################################################################
    def getCapture(self, filePath):
        ret, frame = self.capture.read()
        if ret == False:
            # フレーム画像の取得に失敗
            frame_Num = int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))

            if self.cap_var.get() == False:
                text = "画像の取得に失敗しました。"
                tk.messagebox.showerror("画像取得エラー", f"{text}\n\n{frame_Num}フレーム目:{self.inMoviePath}")
            keiUtil.logAdd(f"{text}\n -> {frame_Num}フレーム目:{self.inMoviePath}", 2)
            return False        

        ret = self.movieOutput(frame, filePath)
        if ret == False:
            # 画像の出力に失敗
            if self.cap_var.get() == False:
                text = "画像の出力に失敗しました。"
                tk.messagebox.showerror("画像出力エラー", f"{text}\n\n{filePath}")
            keiUtil.logAdd(f"{text}\n -> {filePath}", 2)

    ###############################################################################
    # キャプチャ出力
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
    # 出力ボタンを押したときの動作
    ###############################################################################
    def onBtnOutputPicture(self):
        
        # パスが空なら return
        if self.inPathStrvar == "":
            print("ng")
            return
        elif  self.outPathStrvar == "":
            print("ng")
            return


        if self.radioValue.get() == 0:
            # 1秒ごとにキャプチャを行う
            captureFreq = self.fps
        else:
            # コンボボックスの選択値でキャプチャを行う
            strCmb = self.freq_var.get()
            captureFreq = int(strCmb[0:strCmb.find('F')])    # Fより前の部分を切り出す

        # 画像の出力に失敗
        messageText = f"出力ファイル：{self.inMoviePath}\n"\
                        f"出力パス：{self.outFolderPath}\n"\
                        f"キャプチャ頻度：{captureFreq}F\n"\
                        f"キャプチャ範囲： {self.outputStartPos} ~ {self.outputEndPos}\n\n"\
                        "上記の設定でキャプチャを出力します。"
        ret = tk.messagebox.askyesno("画像出力", f"{messageText}")

        # 確認のメッセージボックス表示
        if ret == False:
            # 選択が No なら return
            return
        
        # OKなら出力ディレクトリ作成
        keiUtil.logAdd(f"キャプチャ範囲：{self.outputStartPos} ~ {self.outputEndPos}  "\
                       f"キャプチャ頻度：{captureFreq}", 1)
        keiUtil.logAdd(f"キャプチャ出力：{self.inMoviePath} -> {self.outFolderPath}", 1)

        # キャプチャ出力
        self.movieCapture(self.outFolderPath, self.outputStartPos, self.outputEndPos, captureFreq)

    ###############################################################################
    # スレッド処理
    ###############################################################################
    def main_thread_func(self):

        while self.set_movie:

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
            self.BTN_PLAY.config(state=tk.DISABLED)
            self.BTN_STOP.config(state=tk.DISABLED)
            self.BTN_RSTPLAY.config(state=tk.DISABLED)
            self.BTN_POSSTART.config(state=tk.DISABLED)
            self.BTN_POSEND.config(state=tk.DISABLED)
            self.CMB_FREQ.config(state=tk.DISABLED)
            self.BTN_CAP.config(state=tk.DISABLED)
            self.SCR_SCALE.config(state=tk.DISABLED)
            self.CHK_CAP.config(state=tk.DISABLED)
            return

        if self.start_movie == False:
            # 動画を再生していない (≒再生可能)
            self.BTN_PLAY.config(state=tk.NORMAL)
            self.BTN_STOP.config(state=tk.DISABLED)    # 再生中に押せない
            self.BTN_RSTPLAY.config(state=tk.NORMAL)
            self.BTN_CLOSE.config(state=tk.NORMAL)
            self.BTN_INPUTPATH.config(state=tk.NORMAL)
            self.BTN_OUTPUTPATH.config(state=tk.NORMAL)
            self.BTN_POSSTART.config(state=tk.NORMAL)    # 常に押せる (動画読み込み時に有効化)
            self.BTN_POSEND.config(state=tk.NORMAL)      # 常に押せる (動画読み込み時に有効化)
            self.BTN_CAP.config(state=tk.NORMAL)
            self.BTN_OUTPUT.config(state=tk.NORMAL)
            self.SCR_SCALE.config(state=tk.NORMAL)          # 再生中のスライダー操作で落ちるバグがあるため封印
        else:
            self.BTN_PLAY.config(state=tk.DISABLED)
            self.BTN_STOP.config(state=tk.NORMAL)    # 再生中に押せる
            self.BTN_RSTPLAY.config(state=tk.DISABLED)
            self.BTN_CLOSE.config(state=tk.DISABLED)
            self.BTN_INPUTPATH.config(state=tk.DISABLED)
            self.BTN_OUTPUTPATH.config(state=tk.DISABLED)
            if self.cap_var.get() == False:
                # 簡易キャプチャ設定時はトーンダウンしない
                self.BTN_CAP.config(state=tk.DISABLED)
            self.BTN_OUTPUT.config(state=tk.DISABLED)
            self.SCR_SCALE.config(state=tk.DISABLED)          # 再生中のスライダー操作で落ちるバグがあるため封印

    ###############################################################################
    # 現在のフレームの内容で描画を更新する
    ###############################################################################
    def moveCountUp(self):
#         if self.capture.get(cv2.CAP_PROP_POS_FRAMES) < self.capture.get(cv2.CAP_PROP_FRAME_COUNT):
#             self.capture.set(cv2.CAP_PROP_POS_FRAMES, self.capture.get(cv2.CAP_PROP_POS_FRAMES))
# #            self.capture.set(cv2.CAP_PROP_POS_FRAMES, self.capture.get(cv2.CAP_PROP_POS_FRAMES))
#             return

        # キャンバス画像を更新
        self.updateCanvasImage()

        # 現在の動画位置を取得し、描画のカウントを更新する
        frame_Num = int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))
        self.updateMovieCount(frame_Num)    # 再生秒の更新

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
            resizedImg = img.resize((int(w * (self.canvasHeight / h)), int(h * (self.canvasHeight / h))))

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
        self.inMoviePath = tk.filedialog.askopenfilename(title="動画ファイルを選択してください", filetypes=self.movieFile_filter, initialdir=self.inMovieFolder)

        if self.inMoviePath == "":
            # ファイルを選択せずに閉じていたら return
            return False

        # 入力動画フォルダの更新
        selectFolder = self.inMoviePath[:self.inMoviePath.rfind('/')]
        ret = keiUtil.checkIniFile("MOVIE EDIT", "inputMoviePath", selectFolder)
        if ret == True:
            self.inMovieFolder = selectFolder

        keiUtil.logAdd(f"入力動画パス:{self.inMoviePath}")

    ###############################################################################
    # 出力先フォルダパスを取得する
    ###############################################################################
    def get_folderPath(self):
        # ファイルダイアログを開く
        self.outFolderPath = tk.filedialog.askdirectory(title="出力先フォルダを選択してください", initialdir=self.outFolderPath)

        if self.outFolderPath == "":
            # フォルダを選択せずに閉じていたら return
            return False

        # 出力動画フォルダの更新
        keiUtil.checkIniFile("MOVIE EDIT", "outputpicturepath", self.outFolderPath)

        keiUtil.logAdd(f"出力画像パス:{self.outFolderPath}")
    
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
        
        # 簡易キャプチャ用連番取得
        self.updateTempcapNum()

        # 映像(動画)の取得
        self.capture = cv2.VideoCapture(self.inMoviePath)
        self.bCatchedMovie = True
        keiUtil.logAdd(f"動画の読込 -> {self.inMoviePath}", 1)

        # 動画のフォーマットチェック
        if False == self.checkMovieFormat():
            return False

        # 動画の秒間フレーム数の取得
        tempfps = self.capture.get(cv2.CAP_PROP_FPS)
        self.fps = int(int((tempfps+0.5)*10)/10)                    # fpsを小数点以下で四捨五入
        keiUtil.logAdd(f"「{self.movie_FileName}」, 秒間フレーム数:{self.fps} ({self.capture.get(cv2.CAP_PROP_FPS)})")
        self.frameAve_var.set(f"秒間フレーム数：{self.fps}")
        self.setCmbBoxItems(self.fps)								# コンボボックスの要素を fps に応じて生成

        # 動画の総フレーム数の取得
        self.totalCount = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        keiUtil.logAdd(f"総フレーム数:{self.totalCount} (再生時間：{self.getTotalMovieCount()})")
        self.SCR_SCALE.config(to=self.totalCount)                   # スクロールバーの最大値を動画に合わせる
        self.frameAll_var.set(f"総フレーム数： {self.totalCount}")
        self.posStart_var.set("開始位置: 0")                # 動画表示範囲
        self.posEnd_var.set(f"終了位置: {self.totalCount}")
        self.outputStartPos = 0                             # 動画出力範囲
        self.outputEndPos = self.totalCount

        # 動画タイトルの更新
        self.movieStrvar.set(self.movie_FileName)

        # 動画の時間表示の更新
        self.updateMovieCount()

        # コントロールを有効化する
        self.enableWidget()

        self.CHK_CAP.config(state=tk.NORMAL) # 動作確認　もっといい場所に移動

    ###############################################################################
    # 簡易キャプチャ用連番取得
    ################################################################################
    def updateTempcapNum(self):
        serchPath = f"{keiUtil.managementArea}/EDIT_POOL/picture_out/temp/tempCapture_{self.movie_FileName}_*_*.png"
        self.tempcapNum = keiUtil.getLastFileNumber(serchPath)

    ###############################################################################
    # コンボボックスの選択肢を fpsのフレーム数を上限に 更新する
    #  引数1: int fps 入力動画の秒間フレーム数
    ################################################################################
    def setCmbBoxItems(self, fps):

        listItems = []                          # 変数格納用の箱を作る

        listItems.append(f"{fps * 10}F(10秒)")
        listItems.append(f"{fps * 5}F(5秒)")
        listItems.append(f"{fps * 3}F(3秒)")
        listItems.append(f"{fps * 2}F(2秒)")

        defFpsText = f"{fps * 1}F(1秒)"
        listItems.append(defFpsText)

        # 1Fになるまでフレーム数を 1/2 にしていく
        oldFrame = fps
        while oldFrame != 1 or oldFrame < 1:
            frame = int(oldFrame/2)
            sec = frame/fps
            listItems.append(f"{frame}F({sec:.2}秒)")
            oldFrame = frame

        self.freqList_list = listItems                          # コンボボックスの要素用変数を上書き
        self.CMB_FREQ.configure(values = self.freqList_list)    # コンボボックスの設定を更新
        self.CMB_FREQ.set(defFpsText)                           # 1秒毎(fps)に値を設定
        self.CMB_FREQ.config(state=tk.NORMAL)                   # コンボボックスの有効化
        self.RDO_FRQFRAME.config(state=tk.NORMAL)               # ラジオボタンの有効化

    ###############################################################################
    # 読み込んだ動画が未対応
    ###############################################################################
    def checkMovieFormat(self):
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
        tk.messagebox.showwarning(title="ImportError", message=f"{errorText}/n{self.inMoviePath}")
        keiUtil.logAdd(f"{errorText} -> {self.inMoviePath}")

        self.capture.release()
        self.inMoviePath = ""
        self.inPathStrvar.set(self.inMoviePath)
        self.bCatchedMovie = False
        self.enableWidget()
    
    ###############################################################################
    # 動画の再生時間を更新する
    ################################################################################
    def updateMovieCount(self, frameNum=0):
        if self.bCatchedMovie == False:
            # 動画を読み込んでいなければ return
            return
        
        # スクロールバーの更新
        self.scale_var.set(frameNum)       

        # 動画カウントの更新
        if ( frameNum == 0 or (frameNum % (self.fps)) == 0):
            # 動画読み込み時 or 1秒に1回更新
            currentTime = keiUtil.secToTime((int)(frameNum/self.fps))
            self.secStrvar.set(f"{currentTime[0]:02d}:{currentTime[1]:02d}:{currentTime[2]:02d}/"
                f" {self.getTotalMovieCount()}")

    ###############################################################################
    # 動画の総時間を取得する
    ################################################################################
    def getTotalMovieCount(self):
        maxTime = keiUtil.secToTime((int)(self.totalCount/self.fps))
        return f"{maxTime[0]:02d}:{maxTime[1]:02d}:{maxTime[2]:02d}"

    ###############################################################################
    # 動画のキャプチャ
    #  引数1: str outFolderPath 出力先フォルダ(選択場所)
    #  引数1: str StartPos      キャプチャ範囲：開始位置
    #  引数1: str EndPos        キャプチャ範囲：終了位置
    #  引数1: str captureFreq   キャプチャ頻度
    ################################################################################
    def movieCapture(self, outFolderPath, StartPos, EndPos, captureFreq):

        count = StartPos    # フレーム用カウンタ
        if count == 0:
            count = 1       # 最初からなら暫定で 1 からに変更 (0フレーム目を取得する処理をそのうち作る)

        # 出力先フォルダがなければ作成
        pictDir = f"{outFolderPath}/{self.movie_FileName}"  # 「引数の出力先フォルダ\動画のファイル名」
        os.makedirs(pictDir, exist_ok=True)

        # 開始位置の1つ前にキャプチャ位置を移動
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, StartPos - 1)

        keiUtil.logAdd("キャプチャ開始", 1)


        # 動画のフレームを順番に見ていく
        while True:
            # フレームの情報を読み込む
            ret, frame = self.capture.read()
            
            if not ret or count == EndPos + 1:
                # 終了位置になるか、フレームを読み込めなければループを抜ける 
                keiUtil.logAdd("キャプチャ終了", 1)
                break

            # ファイルの出力
            if int(count % captureFreq) == 0:
                # キャプチャ頻度ごと(1秒 or コンボボックス設定値)

                # 「動画ファイル名_XXXXXX(フレーム数)_yyyymmdd_HHMMSS.png」 でファイル出力
                pictPath = f"{pictDir}/{self.movie_FileName}_{count:06}_{keiUtil.getTime()}.png"
                cv2.imwrite(pictPath, frame)
                keiUtil.logAdd(f"画像出力:{pictPath}")

            count += 1  # カウントアップ


###############################################################################
# 動作確認用
###############################################################################
if __name__ == "__main__":
    main_window = tk.Tk()
    captureMovie(main_window)    # Viewクラス生成
    main_window.mainloop()  # 　フレームループ処理
