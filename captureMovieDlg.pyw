# -*- coding: utf8 -*-
####################################################################################################################
# captureMovieDlg.pyw
#   captureMovieのダイアログ
#####################################################################################################################
# import sys
import cv2
import threading        # スレッド処理
import configparser     # iniファイル読込
import keiUtil          # 自作ユーティリティのインポート
# import time
import subprocess       # サブプロセス起動のモジュール

# 自作モジュールのインポート
from captureMovie import CManagementMovie
from captureMovie import CPlayMovie
from captureMovie import CMovieCapture

# GUI関係
import tkinter as tk
from tkinter import ttk, filedialog
# from tkinter.filedialog import askopenfile

# iniファイル読込
inifile = configparser.SafeConfigParser()
inifile.read("./settings.ini", encoding="utf-8")


####################################################################################################################
# CView クラス
####################################################################################################################
class CView():

    ####################################################################################################################
    # コンストラクタ
    ####################################################################################################################
    def __init__(self, parent, myVideo):
        self.parent = parent
        self.myVideo = myVideo

    ####################################################################################################################
    # オブジェクト生成　※ ボタン操作が化けるため、ダイアログ生成後に実施
    ####################################################################################################################
    def init_func(self):
        # コントロール用変数の宣言
        self.SetControlVar()

        # Viewの生成
        self.createView()

        # コントロール用変数の初期化
        self.InitControlVar()

    ####################################################################################################################
    # コントロール用変数の宣言
    ####################################################################################################################
    def SetControlVar(self):
        self.movieStr_var = tk.StringVar()  # 動画タイトル
        self.posStart_var = tk.StringVar()  # 開始位置ラベル
        self.posEnd_var = tk.StringVar()    # 終了位置ラベル
        self.frameAll_var = tk.StringVar()  # 総フレームラベルの表示用変数
        self.frameAve_var = tk.StringVar()  # 平均フレームラベルの表示用変数
        self.secStr_var = tk.StringVar()    # 再生時間ラベルの表示用変数
        self.inPathStr_var = tk.StringVar()  # 入力ファイルパス
        self.outPathStrvar = tk.StringVar()  # 出力先パス
        self.freqList_list = ("1F")	 # コンボボックス要素用配列

    ####################################################################################################################
    # コントロール用変数の初期化 ダイアログ表示時、動画の再読み込みなど
    ####################################################################################################################
    def InitControlVar(self):
        self.movieStr_var.set("Movie")
        self.frameAll_var.set("総フレーム数： -")
        self.frameAve_var.set("秒間フレーム数：- ")
        self.posStart_var.set("開始位置: -")
        self.posEnd_var.set("終了位置: -")
        self.secStr_var.set("00:00:00/ 00:00:00")

        self.freqList_list = ("1F")	 # コンボボックス要素用配列
        self.CMB_FREQ.set("1F")		 # コンボボックス設定値

    ####################################################################################################################
    # Window の View
    ####################################################################################################################
    def createView(self):

        # ウィンドウの設定
        self.main_window = self.parent.master
        self.main_window.title("Clip Movie")            # ウィンドウタイトル
        self.main_window.geometry("1200x600+100+100")   # ウィンドウサイズ(幅x高さ+位置補正)
        self.main_window.wm_minsize(width=1200, height=600)  # ウィンドウサイズ下限
#        self.main_window.resizable(False, False)       # ウィンドウサイズの固定 (現状は可変)

        # Variable setting
        self.movieFile_filter = [("Movie file", ".mp4")]    # 動画読み込み時のフィルタ

        # エリアの分割
        self.FRAME_CANVAS = tk.Frame(self.main_window)      # 動画領域 (画面左側)
        self.FRAME_CANVAS.place(relx=0.01, rely=0.01, relwidth=0.59, relheight=0.99)

        self.FRAME_MANIPURATE = tk.Frame(self.main_window)  # 操作領域 (画面右側)
        self.FRAME_MANIPURATE.place(relx=0.61, rely=0.01, relwidth=0.38, relheight=0.99)

        # 動画領域 キャンバス
        self.LBL_MOVIETITLE = tk.Label(
            self.FRAME_CANVAS, textvariable=self.movieStr_var, bg="white", relief=tk.RIDGE)  # 動画タイトル
        self.LBL_MOVIETITLE.place(relx=0.00, rely=0.00, relwidth=0.99, relheight=0.04)

        self.CANVAS_VIEW = tk.Canvas(self.FRAME_CANVAS, bg="#A9A9A9")                       # 動画表示スペース
        self.CANVAS_VIEW.place(relx=0.00, rely=0.05, relwidth=0.99, relheight=0.80)

        # 動画領域 スクロールバー周辺
        self.scale_var = tk.IntVar()    # スクロールバー値取得用変数
        self.SCR_SCALE = tk.Scale(
                        self.FRAME_CANVAS, orient=tk.HORIZONTAL,                            # スライダー
                        sliderlength=15, from_=0, to=300, resolution=1,
#                        showvalue=0,   # デバッグ終わったら有効化する (スケールの数字が消える)
                        variable=self.scale_var, command=self.parent.OnMoveSlider
        )
        self.SCR_SCALE.place(relx=0.01, rely=0.86, relwidth=0.98, relheight=0.07)

        self.playSync_var = tk.BooleanVar()  # チェックボックスの状態設定用変数
        self.CHK_PLAY_SYNC = tk.Checkbutton(self.FRAME_CANVAS, variable=self.playSync_var, text="再生速度の同期をとる",
                                            anchor=tk.W, command=self.parent.OnBtnSync)  # 再生速度同期のチェックボックス
        self.CHK_PLAY_SYNC.place(relx=0.01, rely=0.94, relwidth=0.28, relheight=0.05)
        self.CHK_PLAY_SYNC.config(state=tk.DISABLED)
        self.playSync_var.set(False)

        # 総フレームラベル
        self.LBL_FLAMEALL = tk.Label(self.FRAME_CANVAS, textvariable=self.frameAll_var, font=(0, 11), anchor=tk.NW)
        self.LBL_FLAMEALL.place(relx=0.30, rely=0.94, relwidth=0.20, relheight=0.05)

        # 平均フレームラベル
        self.LBL_FLAMEAVE = tk.Label(self.FRAME_CANVAS, textvariable=self.frameAve_var, font=(0, 11), anchor=tk.NW)
        self.LBL_FLAMEAVE.place(relx=0.51, rely=0.94, relwidth=0.20, relheight=0.05)

        # 再生時間ラベル
        self.LBL_SECCOUNT = tk.Label(self.FRAME_CANVAS, textvariable=self.secStr_var, font=(0, 12), anchor=tk.NE)
        self.LBL_SECCOUNT.place(relx=0.72, rely=0.94, relwidth=0.25, relheight=0.05)

        # 操作領域 パス入力
        self.LBL_INPUTFILE = tk.Label(self.FRAME_MANIPURATE, text="読み込みファイル", anchor=tk.W)   # 入力ファイルラベル
        self.LBL_INPUTFILE.place(relx=0.00, rely=0.00, relwidth=1.0, relheight=0.03)

        self.EDT_INPUTPATH = tk.Entry(self.FRAME_MANIPURATE, textvariable=self.inPathStr_var)       # 入力ファイルパス
        self.EDT_INPUTPATH.place(relx=0.00, rely=0.03, relwidth=0.88, relheight=0.03)
        self.EDT_INPUTPATH.config(state="readonly")

        # ファイルを開くボタン(in)
        self.BTN_INPUTPATH = self.SetBtnProp(self.FRAME_MANIPURATE, "開く", self.parent.OnBtnInputPath)
        self.BTN_INPUTPATH.place(relx=0.89, rely=0.03, relwidth=0.10, relheight=0.03)

        self.LBL_OUTPUTFILE = tk.Label(self.FRAME_MANIPURATE, text="出力先パス", anchor=tk.W)        # 出力先ラベル
        self.LBL_OUTPUTFILE.place(relx=0.00, rely=0.07, relwidth=1.0, relheight=0.03)

        self.EDT_OUTPUTPATH = tk.Entry(self.FRAME_MANIPURATE, textvariable=self.outPathStrvar)      # 出力先パス
        self.EDT_OUTPUTPATH.place(relx=0.00, rely=0.1, relwidth=0.88, relheight=0.03)
        self.EDT_OUTPUTPATH.config(state="readonly")

        # フォルダを開くボタン(out)
        self.BTN_OUTPUTPATH = self.SetBtnProp(self.FRAME_MANIPURATE, "開く", self.parent.OnBtnOutputPath)
        self.BTN_OUTPUTPATH.place(relx=0.89, rely=0.1, relwidth=0.10, relheight=0.03)

        # フォルダを開くボタン(エクスプローラー)
        self.BTN_OUTPUTFOLDER = self.SetBtnProp(self.FRAME_MANIPURATE, "出力先フォルダ", self.parent.OnBtnOutputFolder)
        self.BTN_OUTPUTFOLDER.place(relx=0.80, rely=0.14, relwidth=0.19, relheight=0.03)

        # 操作領域 動画再生
        self.BTN_PLAY = self.SetBtnProp(self.FRAME_MANIPURATE, "再生", self.parent.OnBtnPlay)      # 再生ボタン
        self.BTN_PLAY.place(relx=0.0, rely=0.26, relwidth=0.32, relheight=0.10)
        self.BTN_PLAY.config(state=tk.DISABLED)

        self.BTN_STOP = self.SetBtnProp(self.FRAME_MANIPURATE, "停止", self.parent.OnBtnStop)      # 停止ボタン
        self.BTN_STOP.place(relx=0.33, rely=0.26, relwidth=0.32, relheight=0.10)
        self.BTN_STOP.config(state=tk.DISABLED)

        self.BTN_RSTPLAY = self.SetBtnProp(self.FRAME_MANIPURATE, "再生位置リセット", self.parent.OnBtnReset)  # リセットボタン
        self.BTN_RSTPLAY.place(relx=0.66, rely=0.26, relwidth=0.32, relheight=0.10)
        self.BTN_RSTPLAY.config(state=tk.DISABLED)

        # 操作領域 出力設定1
        # 開始位置ボタン
        self.BTN_POSSTART = self.SetBtnProp(self.FRAME_MANIPURATE, "開始位置", self.parent.OnBtnSetCapturePos_Start)
        self.BTN_POSSTART.place(relx=0.0, rely=0.37, relwidth=0.32, relheight=0.05)
        self.BTN_POSSTART.config(state=tk.DISABLED)

        # 終了位置ボタン
        self.BTN_POSEND = self.SetBtnProp(self.FRAME_MANIPURATE, "終了位置", self.parent.OnBtnSetCapturePos_End)
        self.BTN_POSEND.place(relx=0.33, rely=0.37, relwidth=0.32, relheight=0.05)
        self.BTN_POSEND.config(state=tk.DISABLED)
        # リセットボタン
        self.BTN_POSRST = self.SetBtnProp(self.FRAME_MANIPURATE, "範囲リセット", self.parent.OnBtnResetCaptureRange)
        self.BTN_POSRST.place(relx=0.66, rely=0.37, relwidth=0.32, relheight=0.05)
        self.BTN_POSRST.config(state=tk.DISABLED)

        # 操作領域 出力設定2
        # 画像出力範囲ラベル
        self.LBL_POSRANGE = tk.Label(self.FRAME_MANIPURATE, text="画像出力範囲",
                                     font=(0, 11), anchor=tk.CENTER, background='#d0eaff')
        self.LBL_POSRANGE.place(relx=0.01, rely=0.58, relwidth=0.31, relheight=0.03)
        # 開始位置ラベル
        self.LBL_POSSTART = tk.Label(self.FRAME_MANIPURATE, textvariable=self.posStart_var, font=(0, 11), anchor=tk.NW)
        self.LBL_POSSTART.place(relx=0.40, rely=0.58, relwidth=0.25, relheight=0.03)
        # 終了位置ラベル
        self.LBL_POSEND = tk.Label(self.FRAME_MANIPURATE, textvariable=self.posEnd_var, font=(0, 11), anchor=tk.NW)
        self.LBL_POSEND.place(relx=0.70, rely=0.58, relwidth=0.25, relheight=0.03)

        # 1秒毎ラジオボタン
        self.radioValue = tk.IntVar(value=0)     # 初期値
        self.RDO_FRQSECOND = tk.Radiobutton(self.FRAME_MANIPURATE, text="1秒毎にキャプチャを出力する",
                                            font=(1, 9), justify="left", variable=self.radioValue, value=0)
        self.RDO_FRQSECOND.place(relx=0.00, rely=0.64, relwidth=0.40, relheight=0.03)

        self.RDO_FRQFRAME = tk.Radiobutton(self.FRAME_MANIPURATE, text="", justify="left",    # フレーム指定ラジオボタン
                                           variable=self.radioValue, value=1)
        self.RDO_FRQFRAME.place(relx=0.44, rely=0.64, relwidth=0.05, relheight=0.03)
        self.RDO_FRQFRAME.config(state=tk.DISABLED)

        self.freq_var = tk.StringVar()  # コンボボックスの選択値取得用変数
        self.CMB_FREQ = ttk.Combobox(self.FRAME_MANIPURATE, justify="right", font=(0, 9),
                                     textvariable=self.freq_var, values=self.freqList_list)     # フレーム指定コンボボックス
        self.CMB_FREQ.place(relx=0.49, rely=0.64, relwidth=0.18, relheight=0.03)
        self.CMB_FREQ.config(state=tk.DISABLED)

        self.LBL_FREQ = tk.Label(self.FRAME_MANIPURATE, text="毎にキャプチャ出力する", font=(1, 9), anchor=tk.NW)   # フレーム指定ラベル
        self.LBL_FREQ.place(relx=0.68, rely=0.64, relwidth=0.40, relheight=0.03)

        # 操作領域 操作ボタン
        self.BTN_CAP = self.SetBtnProp(self.FRAME_MANIPURATE, "キャプチャ", self.parent.OnBtnCapture)      # キャプチャボタン
        self.BTN_CAP.place(relx=0.02, rely=0.70, relwidth=0.45, relheight=0.15)
        self.BTN_CAP.config(state=tk.DISABLED)

        self.cap_var = tk.BooleanVar()  # チェックボックスの状態設定用変数
        self.CHK_CAP = tk.Checkbutton(self.FRAME_MANIPURATE, variable=self.cap_var,  # 簡易キャプチャのフラグ
                                      text="出力先指定を省略する", anchor=tk.W)
        self.CHK_CAP.place(relx=0.02, rely=0.86, relwidth=0.45, relheight=0.03)
        self.CHK_CAP.config(state=tk.DISABLED)
        self.cap_var.set(False)

        self.BTN_OUTPUT = self.SetBtnProp(self.FRAME_MANIPURATE, "出力", self.parent.OnBtnOutputCapture)   # 出力ボタン
        self.BTN_OUTPUT.place(relx=0.51, rely=0.70, relwidth=0.45, relheight=0.15)
        self.BTN_OUTPUT.config(state=tk.DISABLED)

        self.noProg_var = tk.BooleanVar()  # チェックボックスの状態設定用変数
        self.CHK_PROG = tk.Checkbutton(self.FRAME_MANIPURATE, variable=self.noProg_var,  # プログレスバーを表示しないフラグ
                                       text="プログレスバーを表示しない", anchor=tk.W, command=self.parent.OnBtnNoProg)
        self.CHK_PROG.place(relx=0.51, rely=0.86, relwidth=0.45, relheight=0.03)
        self.CHK_PROG.config(state=tk.DISABLED)
        self.noProg_var.set(False)

        self.noLog_var = tk.BooleanVar()  # チェックボックスの状態設定用変数
        self.CHK_NOTLOG = tk.Checkbutton(self.FRAME_MANIPURATE, variable=self.noLog_var,  # キャプチャ出力のログを出力しないフラグ
                                         text="キャプチャ出力情報をログに出力しない", anchor=tk.W, command=self.parent.OnBtnNoLog)
        self.CHK_NOTLOG.place(relx=0.51, rely=0.90, relwidth=0.45, relheight=0.03)
        self.CHK_NOTLOG.config(state=tk.DISABLED)
        self.noLog_var.set(False)

        self.BTN_CLOSE = self.SetBtnProp(self.FRAME_MANIPURATE, "閉じる", self.parent.OnBtnClose)          # 閉じるボタン
        self.BTN_CLOSE.place(relx=0.66, rely=0.94, relwidth=0.32, relheight=0.05)

    ####################################################################################################################
    # ボタン属性定義のテンプレート
    ####################################################################################################################
    def SetBtnProp(self, set_frame, btn_name, act_command):
        return tk.Button(set_frame, text=btn_name, width=10, command=act_command)

    ####################################################################################################################
    # ボタンの状態制御
    ####################################################################################################################
    def enableWidget(self):
        if self.myVideo.setMovie is False:
            # 画像を読み込めていない時はボタン無効
            self.BTN_PLAY.config(state=tk.DISABLED)
            self.BTN_STOP.config(state=tk.DISABLED)
            self.BTN_RSTPLAY.config(state=tk.DISABLED)
            self.BTN_POSSTART.config(state=tk.DISABLED)
            self.BTN_POSEND.config(state=tk.DISABLED)
            self.CMB_FREQ.config(state=tk.DISABLED)
            self.BTN_CAP.config(state=tk.DISABLED)
            self.SCR_SCALE.config(state=tk.DISABLED)
            self.CHK_PLAY_SYNC.config(state=tk.DISABLED)
            self.CHK_CAP.config(state=tk.DISABLED)
            self.CHK_PROG.config(state=tk.DISABLED)
            self.CHK_NOTLOG.config(state=tk.DISABLED)
            return

        self.CHK_PROG.config(state=tk.NORMAL)
        self.CHK_NOTLOG.config(state=tk.NORMAL)

        if self.parent.s_st.playingMovie is False:
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
            self.CHK_CAP.config(state=tk.NORMAL)
            self.CHK_PLAY_SYNC.config(state=tk.NORMAL)
        else:
            self.BTN_PLAY.config(state=tk.DISABLED)
            self.BTN_STOP.config(state=tk.NORMAL)    # 再生中に押せる
            self.BTN_RSTPLAY.config(state=tk.DISABLED)
            self.BTN_CLOSE.config(state=tk.DISABLED)
            self.BTN_INPUTPATH.config(state=tk.DISABLED)
            self.BTN_OUTPUTPATH.config(state=tk.DISABLED)
            if self.cap_var.get() is False:
                # 簡易キャプチャ設定時はトーンダウンしない
                self.BTN_CAP.config(state=tk.DISABLED)
            self.BTN_OUTPUT.config(state=tk.DISABLED)
            self.SCR_SCALE.config(state=tk.DISABLED)          # 再生中のスライダー操作で落ちるバグがあるため封印
            self.CHK_CAP.config(state=tk.DISABLED)
            self.CHK_PLAY_SYNC.config(state=tk.DISABLED)

    ####################################################################################################################
    # コントロールの動画の情報を更新する
    ####################################################################################################################
    def updateWidgetInfo(self):
        self.frameAve_var.set(f"秒間フレーム数：{self.myVideo.fps}")
        self.setCmbBoxItems(self.myVideo.fps)								# コンボボックスの要素を fps に応じて生成

        self.SCR_SCALE.config(to=self.myVideo.totalCount)                   # スクロールバーの最大値を動画に合わせる
        self.frameAll_var.set(f"総フレーム数： {self.myVideo.totalCount}")
        self.posStart_var.set("開始位置: 1")                # 動画表示範囲
        self.posEnd_var.set(f"終了位置: {self.myVideo.totalCount}")
        self.myVideo.outputStartPos = 1                             # 動画出力範囲
        self.myVideo.outputEndPos = self.myVideo.totalCount

        # 動画タイトルの更新
        self.movieStr_var.set(self.myVideo.fileName)

    ####################################################################################################################
    # コンボボックスの選択肢を fpsのフレーム数を上限に 更新する
    #  引数1: int fps 入力動画の秒間フレーム数
    ####################################################################################################################
    def setCmbBoxItems(self, fps):

        listItems = []                          # 変数格納用の箱を作る

        if self.myVideo.totalCount / self.myVideo.fps > 3600:
            listItems.append(f"{fps * 600}F(10分)")
        if self.myVideo.totalCount / self.myVideo.fps > 1800:
            listItems.append(f"{fps * 300}F(5分)")
        if self.myVideo.totalCount / self.myVideo.fps > 600:
            listItems.append(f"{fps * 60}F(1分)")
        if self.myVideo.totalCount / self.myVideo.fps > 300:
            listItems.append(f"{fps * 30}F(30秒)")
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
        self.CMB_FREQ.configure(values=self.freqList_list)    # コンボボックスの設定を更新
        self.CMB_FREQ.set(defFpsText)                           # 1秒毎(fps)に値を設定
        self.CMB_FREQ.config(state=tk.NORMAL)                   # コンボボックスの有効化
        self.RDO_FRQFRAME.config(state=tk.NORMAL)               # ラジオボタンの有効化


####################################################################################################################
# CCaptureMovieDlg クラス
####################################################################################################################
class CCaptureMovieDlg(tk.Frame):

    ####################################################################################################################
    # CControlSetting クラス　(再生・入出力など設定の構造体)
    ####################################################################################################################
    class CControlSetting:

        #######################################################################
        # コンストラクタ
        #######################################################################
        def __init__(self):
            self.playingMovie = False         # 再生中フラグ True の間フレームを更新する
            self.inputMovieFolder = inifile["MOVIE EDIT"]["inputMoviePath"]        # 読み込みファイルのデフォルトフォルダー
            self.outputFolderPath = inifile["MOVIE EDIT"]["outputPicturePath"]     # 出力先フォルダのパス
            self.playDrawFrameFreq: int = 0   # 再生時の描画頻度設定 (キャンバスの更新を何Fごとに行うか)
            self.outputFrameFreq: int = 0     # 出力時の出力頻度の設定 (何フレーム毎に出力するか)
            self.tempcapNum = 0              # 簡易キャプチャ用連番
            self.bSliderMoving = False       # スライダー移動中フラグ
            self.bStopMovieCapture = False   # 動画出力中止フラグ
            self.bSynchronizationPlayingTime = False    # 動画再生の時間を同期する
            self.bNotShowProgressBar = False            # 出力時、プログレスバーを表示しない
            self.bNotLogAtOutput = False     # 出力時、ログ出力を行わない

    ####################################################################################################################
    # コンストラクタ
    ####################################################################################################################
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.myVideo = CManagementMovie()
        self.view = CView(self, self.myVideo)
        self.playMovie = CPlayMovie(self, self.myVideo, self.view)
        self.movieCapture = CMovieCapture(self, self.myVideo, self.view)

        # 変数初期化
        self.init_var()

        # view のオブジェクト生成
        self.view.init_func()

        # 設定構造体の生成
        self.s_st = self.CControlSetting()
        self.view.outPathStrvar.set(self.s_st.outputFolderPath)  # デフォルト出力パスの指定
        self.updateTempcapNum()                                  # 簡易キャプチャ用連番更新

        # ウィンドウの x ボタンが押された時の設定
        self.master.protocol("WM_DELETE_WINDOW", self.delete_window)

    ####################################################################################################################
    # デストラクタ
    ####################################################################################################################
    def __del__(self):
        # delete_window で解放されていなかった時用
        self.myVideo.releaseCapture()

    ####################################################################################################################
    # 変数初期化　フラグ系
    ####################################################################################################################
    def init_var(self):
        self.tempcapNum = 0              # 簡易キャプチャ用連番
        self.thread_set = False          # スレッドを開始済みかのフラグ

    ####################################################################################################################
    # スレッド処理
    ####################################################################################################################
    def createThread(self):
        self.thread_set = True
        self.thread_movie = threading.Thread(target=self.main_thread_func)
        self.thread_movie.start()

    ####################################################################################################################
    # スレッド処理
    ####################################################################################################################
    def main_thread_func(self):

        self.myVideo.setMovie = True

        while self.myVideo.setMovie:

            # 再生中はループの処理を繰り返す
            if self.s_st.playingMovie:            # 再生中

                self.playMovie.playMovie_func()

    ####################################################################################################################
    # スレッドの解放
    ####################################################################################################################
    def releaseThread(self):
        # スレッドの終了を待つ
        self.thread_movie.join()

        # 動画イメージの解放
        self.myVideo.releaseCapture()

    ####################################################################################################################
    # ファイルを開くボタン(in) を押したときの動作
    ####################################################################################################################
    def OnBtnInputPath(self):
        # 入力動画のパスを取得してエディットコントロールを更新
        ret = self.get_moviePath()
        if ret is False:
            return

        # 動画の読込
        ret = self.myVideo.readFile(self.myVideo.path)    # 引数無しで問題ないが使いまわし用
        if ret is False:
            return

        # コントロールを更新、有効化する
        self.view.updateWidgetInfo()
        self.playMovie.updateMovieCount()  # 動画の時間表示の更新
        self.view.enableWidget()

        # キャンパスサイズの更新
        self.view.canvasWidth = self.view.CANVAS_VIEW.winfo_width()
        self.view.canvasHeight = self.view.CANVAS_VIEW.winfo_height()

        # フレームのデータを読み込む
        self.playMovie.moveCountUp()    # analyzeMovie()で読んだフレーム

        # スレッドの処理を開始する
        self.createThread()

    ####################################################################################################################
    # フォルダを開くボタン(out) を押したときの動作
    ####################################################################################################################
    def OnBtnOutputPath(self):
        ret = self.get_folderPath()
        if ret is False:
            return

        self.view.outPathStrvar.set(self.s_st.outputFolderPath)

    ####################################################################################################################
    # 出力フォルダを開くボタン を押したときの動作　※エクスプローラーの起動
    ####################################################################################################################
    def OnBtnOutputFolder(self):
        # 出力先フォルダを開く
        filePath = self.s_st.outputFolderPath.replace('/', "\\")
        subprocess.Popen(["explorer", filePath], shell=True)

    ####################################################################################################################
    # 再生ボタンを押したときの動作
    ####################################################################################################################
    def OnBtnPlay(self):
        if self.myVideo.setMovie is False:
            # 念のため return させる
            return

        if self.myVideo.capture.get(cv2.CAP_PROP_POS_FRAMES) == self.myVideo.totalCount:
            # 現在位置が動画の最後であれば最初に戻って再生開始する
            self.resetPlayStatus()
            ret, self.myVideo.video_frame = self.myVideo.getFramePicture()  # フレームずれ対策

        # セット済みのフレームから動画を再生する
        self.s_st.playingMovie = True
        keiUtil.logAdd(f"動画の再生開始 -> {self.myVideo.path}", 1)

        # 再生中のボタンの無効化
        self.view.enableWidget()

    ####################################################################################################################
    # 停止ボタンを押したときの動作
    ####################################################################################################################
    def OnBtnStop(self):
        # 現在のフレームで再生を停止する
        self.s_st.playingMovie = False
        keiUtil.logAdd(f"動画の再生停止 -> {self.myVideo.path}", 1)

        # ボタンの有効化
        self.view.enableWidget()                     # コントロールの有効化

    ####################################################################################################################
    # リセットボタンを押したときの動作
    ####################################################################################################################
    def OnBtnReset(self):
        self.resetPlayStatus()

    ####################################################################################################################
    #  動画出力の開始位置を指定する
    ####################################################################################################################
    def OnBtnSetCapturePos_Start(self):
        self.myVideo.outputStartPos = self.view.scale_var.get()
        self.view.posStart_var.set(f"開始位置: {self.myVideo.outputStartPos}")
        keiUtil.logAdd(f"動画出力の開始位置を設定: {self.myVideo.outputStartPos}")
        self.view.BTN_POSRST.config(state=tk.NORMAL)

    ####################################################################################################################
    #  動画出力の終了位置を指定する
    ####################################################################################################################
    def OnBtnSetCapturePos_End(self):
        self.myVideo.outputEndPos = self.view.scale_var.get()
        self.view.posEnd_var.set(f"終了位置: {self.myVideo.outputEndPos}")
        keiUtil.logAdd(f"動画出力の終了位置を設定: {self.myVideo.outputEndPos}")
        self.view.BTN_POSRST.config(state=tk.NORMAL)

    ####################################################################################################################
    #  動画出力範囲をリセットする
    ####################################################################################################################
    def OnBtnResetCaptureRange(self):
        self.myVideo.outputStartPos = 1
        self.myVideo.outputEndPos = self.myVideo.totalCount
        self.view.posStart_var.set("開始位置: 1")
        self.view.posEnd_var.set(f"終了位置: {self.myVideo.totalCount}")
        keiUtil.logAdd(f"動画出力範囲を初期化 1:{self.myVideo.totalCount}")
        self.view.BTN_POSRST.config(state=tk.DISABLED)

    ####################################################################################################################
    # スライダー操作
    ####################################################################################################################
    def OnMoveSlider(self, event=None):
        # スライダー位置の画像を取得
        self.myVideo.capture.set(cv2.CAP_PROP_POS_FRAMES, self.view.scale_var.get())
        ret, self.video_frame = self.myVideo.getFramePicture()        # フレーム画像の読み込み

        self.s_st.bSliderMoving = True  # スライダー移動中

        if ret:
            self.playMovie.moveCountUp()

        else:
            self.s_st.playingMovie = False                          # 再生を終了する
            self.myVideo.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)    # 動画の最初に戻す

            ret, self.video_frame = self.myVideo.getFramePicture()  # フレーム画像の読み込み
            self.playMovie.updateCanvasImage()

        self.s_st.bSliderMoving = False  # スライダー移動済

    ####################################################################################################################
    # 再生速度の同期 チェックボタンを押したときの動作
    ####################################################################################################################
    def OnBtnSync(self):
        # チェックボックスの状態をフラグ変数に代入する
        self.s_st.bSynchronizationPlayingTime = self.view.playSync_var.get()

    ####################################################################################################################
    # プログレスバーを表示しない チェックボタンを押したときの動作
    ####################################################################################################################
    def OnBtnNoProg(self):
        # チェックボックスの状態をフラグ変数に代入する
        self.s_st.bNotShowProgressBar = self.view.noProg_var.get()

    ####################################################################################################################
    # 出力時、ログ出力を行わない チェックボタンを押したときの動作
    ####################################################################################################################
    def OnBtnNoLog(self):
        # チェックボックスの状態をフラグ変数に代入する
        self.s_st.bNotLogAtOutput = self.view.noLog_var.get()

    ####################################################################################################################
    # 閉じるボタンを押したときの動作
    ####################################################################################################################
    def OnBtnClose(self):
        # ウィンドウを破棄する
        self.delete_window()

    ####################################################################################################################
    # キャプチャボタンを押したときの動作
    ####################################################################################################################
    def OnBtnCapture(self):

        if self.view.cap_var.get() is True:
            # 簡易キャプチャが有効になっている
            tempFilePath = f"{keiUtil.managementArea}/EDIT_POOL/picture_out/temp/\
                tempCapture_{self.myVideo.fileName}_{keiUtil.getTime()}_{self.tempcapNum:06}.png"

            # キャプチャを取得
            if self.movieCapture.getCapture(tempFilePath) is False:
                return

            self.s_st.tempcapNum += 1    # カウントアップする

        else:
            # 出力先を選択するダイアログを表示する
            tempFilePath = filedialog.asksaveasfilename(
                title="名前を付けて保存", filetypes=[("PNG Image Files", ".png")],
                initialdir=f"{keiUtil.managementArea}/EDIT_POOL/picture_out/temp", initialfile="capture.png"
            )
            if tempFilePath == "":
                return

            # キャプチャを取得
            if self.movieCapture.getCapture(tempFilePath) is False:
                return

    ####################################################################################################################
    # 出力ボタンを押したときの動作
    ####################################################################################################################
    def OnBtnOutputCapture(self):

        # パスが空なら return
        if self.view.inPathStr_var == "":
            print("ng")
            return
        elif self.view.outPathStrvar == "":
            print("ng")
            return

        if self.view.radioValue.get() == 0:
            # 1秒ごとにキャプチャを行う
            captureFreq = self.myVideo.fps
        else:
            # コンボボックスの選択値でキャプチャを行う
            strCmb = self.view.freq_var.get()
            captureFreq = int(strCmb[0:strCmb.find('F')])    # Fより前の部分を切り出す

        # 画像の出力に失敗
        messageText = f"出力ファイル：{self.myVideo.path}\n" f"出力パス：{self.s_st.outputFolderPath}\n"\
            f"キャプチャ頻度：{captureFreq}F\n" f"キャプチャ範囲： {self.myVideo.outputStartPos} ~ {self.myVideo.outputEndPos}\n\n"\
            "上記の設定でキャプチャを出力します。"
        ret = tk.messagebox.askyesno("画像出力", f"{messageText}")

        # 確認のメッセージボックス表示
        if ret is False:
            # 選択が No なら return
            return

        # OKなら出力ディレクトリ作成
        keiUtil.logAdd(f"キャプチャ範囲：{self.myVideo.outputStartPos} ~ {self.myVideo.outputEndPos}"
                       f"キャプチャ頻度：{captureFreq}", 1)
        keiUtil.logAdd(f"キャプチャ出力：{self.myVideo.path} -> {self.s_st.outputFolderPath}", 1)

        # キャプチャ出力 (スレッド作成)
        self.thread_capture = threading.Thread(target=self.movieCapture.movieCapture,
                                               args=(self.s_st.outputFolderPath, self.myVideo.outputStartPos,
                                                     self.myVideo.outputEndPos, captureFreq))

        # プログレスバーを表示するか
        if self.s_st.bNotShowProgressBar is False:
            self.createProgressbar()                        # プログレスバーを作成する
            main_window.wait_window(self.progress_window)   # キャプチャ出力終了待ち
        else:
            self.thread_capture.start()                     # 表示せずに出力を開始
#            self.thread_capture.join()                     # 出力完了時のメッセージボックスで固まるため一旦コメントアウト、対策検討する

    ####################################################################################################################
    # プログレスバーの作成
    ####################################################################################################################
    def createProgressbar(self):
        self.progress_window = tk.Toplevel(self)
        self.progress_window.title("キャプチャ出力")
        self.progress_window.geometry("400x70+900+500")
        self.pb_var = tk.IntVar()
        self.BAR_PROGRESS = ttk.Progressbar(self.progress_window, orient="horizontal", length=360, maximum=100,
                                            mode="determinate", variable=self.pb_var)
        self.BAR_PROGRESS.pack()
        self.rateBar_var = tk.StringVar()
        self.LBL_BARRATE = tk.Label(self.progress_window,
                                    textvariable=self.rateBar_var,
                                    text="0%", font=(0, 11), anchor=tk.CENTER)
        self.LBL_BARRATE.pack()
        self.BTN_STOPPROG = tk.Button(self.progress_window,
                                      text="STOP", command=self.OnBtnStopProg)
        self.BTN_STOPPROG.pack()
        self.progress_window.grab_set()             # モーダルにする
        self.progress_window.focus_set()            # フォーカスを新しいウィンドウをへ移す
        self.progress_window.transient(self.master)   # タスクバーに表示しない
        self.thread_capture.start()

    ####################################################################################################################
    # STOPボタン(プログレスバー)を押した
    ####################################################################################################################
    def OnBtnStopProg(self):
        # 動画出力中止フラグを立てる
        self.s_st.bStopMovieCapture = True
        self.BTN_STOPPROG.config(state=tk.DISABLED)

    ####################################################################################################################
    # 入力動画パスを取得する
    ####################################################################################################################
    def get_moviePath(self):
        # ファイルダイアログを開く
        tempMoviePath = tk.filedialog.askopenfilename(
            title="動画ファイルを選択してください", filetypes=self.view.movieFile_filter, initialdir=self.s_st.inputMovieFolder
        )

        if tempMoviePath == "":
            # ファイルを選択せずに閉じていたら return
            return False

        if self.myVideo.setMovie is True:
            # 動画読み込み済みの場合古い動画のスレッドを終了する コントロール系もここで解放
            self.myVideo.setMovie = False
            self.releaseThread()                     # 既に読み込み済みの動画があれば開放する
            self.view.CANVAS_VIEW.delete("can_pic")  # 本体側に何か書く
            self.myVideo.crearVar()                  # 動画管理用変数初期化

        # 入力動画のパスを更新
        self.myVideo.path = tempMoviePath

        # 入力動画フォルダの更新
        selectFolder = self.myVideo.path[:self.myVideo.path.rfind('/')]
        ret = keiUtil.checkIniFile("MOVIE EDIT", "inputMoviePath", selectFolder)
        if ret is True:
            self.s_st.inputMovieFolder = selectFolder

        # エディットコントロールのパスの更新
        self.view.inPathStr_var.set(self.myVideo.path)

        keiUtil.logAdd(f"入力動画パス:{self.myVideo.path}")

        return True

    ####################################################################################################################
    # 簡易キャプチャ用連番取得
    ####################################################################################################################
    def updateTempcapNum(self):
        serchPath = f"{keiUtil.managementArea}/EDIT_POOL/picture_out/ \
                        temp/tempCapture_{self.myVideo.fileName}_*_*.png"
        self.tempcapNum = keiUtil.getLastFileNumber(serchPath)

    ####################################################################################################################
    # 出力先フォルダパスを取得する
    ####################################################################################################################
    def get_folderPath(self):
        # ファイルダイアログを開く
        self.s_st.outputFolderPath = tk.filedialog.askdirectory(
            title="出力先フォルダを選択してください", initialdir=self.s_st.outputFolderPath)

        if self.s_st.outputFolderPath == "":
            # フォルダを選択せずに閉じていたら return
            return False

        # 出力動画フォルダの更新
        keiUtil.checkIniFile("MOVIE EDIT", "outputpicturepath", self.s_st.outputFolderPath)

        keiUtil.logAdd(f"出力画像パス:{self.s_st.outputFolderPath}")

    ####################################################################################################################
    # 動画の再生状態をリセットする
    #   ※リセットボタンの他、再生完了状態での再生開始でも呼ぶ
    ####################################################################################################################
    def resetPlayStatus(self):
        self.myVideo.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

        ret, self.myVideo.video_frame = self.myVideo.getFramePicture()  # フレーム画像の読み込み

        self.playMovie.moveCountUp()

        # コントロールの初期化
        self.view.scale_var.set(0)       # スライダーを開始位置に戻す
        self.view.enableWidget()         # コントロールの有効化

    ####################################################################################################################
    # ダイアログを閉じるときの処理
    #   ※ダイアログの×、閉じるボタンで呼ぶ
    ####################################################################################################################
    def delete_window(self):
        if self.s_st.playingMovie is True:
            # 再生中はメッセージを出して return
            tk.messagebox.showwarning(
                title="終了エラー",
                message="動画の再生中は終了できません。"
            )
            return

        # 終了確認のメッセージ表示
        ret = tk.messagebox.askyesno(
            title="終了確認",
            message="プログラムを終了しますか？")

        if ret is True:
            # スレッドのループから抜ける
            self.myVideo.setMovie = False

            if self.thread_set is True:
                # スレッドの終了を待つ
                self.releaseThread()

            # ウィンドウを破棄する
            self.master.destroy()

            keiUtil.logAdd("CaptureMovie 終了", 1)


####################################################################################################################
# 動作確認用
####################################################################################################################
if __name__ == "__main__":

    keiUtil.checkExitFolder(keiUtil.managementArea)  # 管理領域の作成
    keiUtil.toolName = "CaptureMovieDlg"
    keiUtil.execDay = keiUtil.getDay()  # アプリケーションの起動日の取得
    keiUtil.logAdd("CaptureMovie 起動", 1)

    main_window = tk.Tk()
    captureMovieDlg = CCaptureMovieDlg(main_window)
    main_window.mainloop()  # ウィンドウのループ処理
