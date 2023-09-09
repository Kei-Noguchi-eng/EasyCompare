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
        self.main_window.geometry("1200x500+100+100")   # ウィンドウサイズ(幅x高さ+位置補正)
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

        self.opr_canvas = tk.Frame(self.main_window)     # 動画用ボタン領域
        self.opr_canvas.place(relx=0.01, rely=0.76, relwidth=0.6, relheight=0.23)

        self.path_frame = tk.Frame(self.main_window)     # ファイル展開領域
        self.path_frame.place(relx=0.61, rely=0.01, relwidth=0.37, relheight=0.20)
 
        self.opr_frame = tk.Frame(self.main_window)      # ボタン関係
        self.opr_frame.place(relx=0.61, rely=0.22, relwidth=0.37, relheight=0.77)

        # 動画領域
        self.movieStrvar = tk.StringVar()
        self.movieStrvar.set("Movie")
        self.movieLabel = tk.Label(
            self.canvas_frame, textvariable=self.movieStrvar, bg="white", relief=tk.RIDGE)  # 動画タイトル
        self.movieLabel.place(relx=0.00, rely=0.00, relwidth=0.98, relheight=0.07)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#A9A9A9")                            # 動画表示スペース
        self.canvas.place(relx=0.00, rely=0.08, relwidth=0.98, relheight=0.91)

        # 動画ボタン領域
        self.scale = tk.Scale(self.opr_canvas, orient=tk.HORIZONTAL)                        # スライダー
        self.scale.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.4)

        self.secStrvar = tk.StringVar()
        self.secStrvar.set("00:00:00/ 00:00:00")
        self.sec_count = tk.Label(self.opr_canvas, textvariable=self.secStrvar, font=(0,12))             # 再生時間ラベル
        self.sec_count.place(relx=0.74, rely=0.42, relwidth=0.25, relheight=0.20)

        # 2 path_frame
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

        # 3 button
        self.button = self.opr_btn(self.opr_frame, "再生", self.on_click_start)    # 開始ボタン
        self.button.grid(row=1, column=0, sticky=tk.SE, padx=10, pady=10)

        self.button = self.opr_btn(self.opr_frame, "一時停止", self.on_click_stop)      # 停止ボタン
        self.button.grid(row=1, column=1, sticky=tk.SE, padx=10, pady=10)

        self.button = self.opr_btn(self.opr_frame, "停止", self.on_click_reset)    # リセットボタン
        self.button.grid(row=1, column=2, sticky=tk.SE, padx=10, pady=10)

        self.button = self.opr_btn(self.opr_frame, "閉じる", self.on_click_close)     # 閉じるボタン
        self.button.grid(row=3, column=3, sticky=tk.SE, padx=10, pady=10)

    ###############################################################################
    # ボタン定義の流用
    ###############################################################################
    def opr_btn(self, set_frame, btn_name, act_command):
        return tk.Button(set_frame, text=btn_name, width=10, command=act_command)

    ###############################################################################
    # ファイルを開くボタン(in) を押したときの動作
    ###############################################################################
    def on_click_moviePath(self):
        # 入力動画のパスを取得してエディットコントロールを更新
        self.get_moviePath()       #
        self.inPathStrvar.set(self.inMoviePath) #

        # フレームのデータを読み込む
        self.run_one_frame()

        # スレッドの処理を開始する
        self.thread_set = True
        self.thread_main = threading.Thread(target=self.main_thread_func)
        self.thread_main.start()

    ###############################################################################
    # ファイルを開くボタン(out) を押したときの動作
    ###############################################################################
    def on_click_folderPath(self):
        self.get_folderPath()       #
        self.outPathStrvar.set(self.outFolderPath)    #

    ###############################################################################
    # 再生ボタンを押したときの動作
    ###############################################################################
    def on_click_start(self):
        # セット済みのフレームから動画を再生する
        self.start_movie = True
        keiUtil.logAdd(f"動画の再生開始 -> {self.inMoviePath}", 1)

    ###############################################################################
    # 停止ボタンを押したときの動作
    ###############################################################################
    def on_click_stop(self):
        # 現在のフレームで再生を停止する
        self.start_movie = False
        keiUtil.logAdd(f"動画の再生停止 -> {self.inMoviePath}", 1)

    ###############################################################################
    # リセットを押したときの動作
    ###############################################################################
    def on_click_reset(self):
        self.start_movie = False
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.run_one_frame()

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
        
        # 動画情報の読み込み
        self.analyzeMovie()                 # 動画を解析する
        ret, self.video_frame = self.capture.read()         # フレーム画像の読み込み

        if self.video_frame is None:        # 読み込んだデータが空だった
            print("None")

        while self.set_movie:               # スレッド動作中

            # 再生中はループの処理を繰り返す
            if self.start_movie:            # 再生中

                ret, self.video_frame = self.capture.read() # フレーム画像の読み込み

                if ret:
                    self.updateCanvasImage()              # 読み込んだ画像でイメージを更新する
                else:
                    self.start_movie = False                # 再生を終了する

    ###############################################################################
    # run_one_frame
    ###############################################################################
    def run_one_frame(self):
        # 動画ファイルを再読み込みする
        self.capture = cv2.VideoCapture(self.inMoviePath)
        self.bCatchedMovie = True

        ret, self.video_frame = self.capture.read()     # 1フレーム分の画像データを読み込む

        if self.video_frame is None:
            # 画像が存在しない
            print("None")

        else:
            ret, self.video_frame = self.capture.read() # 1フレーム分の画像データを読み込む

            # 画像の加工
            pil = self.cvtopli_color_convert(self.video_frame) # 読み込んだ画像を Pillow で使えるようにする
            self.effect_img, self.canvas_create = self.resize_image(pil, self.canvas)   # 画像のリサイズ

            # キャンバスの画像を更新する
            self.replace_canvas_image(self.effect_img, self.canvas, self.canvas_create)

    ###############################################################################
    # キャンバス画像を更新する
    ###############################################################################
    def updateCanvasImage(self):
        # 画像の加工
        pil = self.cvtopli_color_convert(self.video_frame)
        self.effect_img, self.canvas_create = self.resize_image(pil, self.canvas)
        self.replace_canvas_image(self.effect_img, self.canvas, self.canvas_create)

        # 現在の動画位置を取得し、描画のカウントを更新する
        frame_Num = int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))
        self.updateMovieCount(frame_Num)

    ###############################################################################
    # BGR →　RGB　変換      ※ OpenCV imread()で読むと色の順番がBGRになるため
    ###############################################################################
    def cvtopli_color_convert(self, video):
        rgb = cv2.cvtColor(video, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)

    ###############################################################################
    # resize_image
    ###############################################################################
    # Model
    def resize_image(self, img, canvas):

        w = img.width
        h = img.height
        w_offset = 250 - (w * (500 / h) / 2)
        h_offset = 250 - (h * (700 / w) / 2)

        if w > h:
            resized_img = img.resize((int(w * (700 / w)), int(h * (700 / w))))
        else:
            resized_img = img.resize((int(w * (500 / h)), int(h * (500 / h))))

        self.pil_img = ImageTk.PhotoImage(resized_img)
        canvas.delete("can_pic")

        if w > h:
            resized_img_canvas = canvas.create_image(
                0, h_offset, anchor="nw", image=self.pil_img, tag="can_pic"
            )

        else:
            resized_img_canvas = canvas.create_image(
                w_offset, 0, anchor="nw", image=self.pil_img, tag="can_pic"
            )

        return resized_img, resized_img_canvas
    
    ###############################################################################
    # 画像の置き換え
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
        # 既に読み込み済みの動画があれば開放する
        if self.bCatchedMovie == True:
            self.capture.release()

        # 動画のパスからファイル名を取得する
        self.movie_FileName = os.path.splitext(os.path.basename(self.inMoviePath))[0]
        
        # 映像(動画)の取得
        self.capture = cv2.VideoCapture(self.inMoviePath)
        self.bCatchedMovie = True
        keiUtil.logAdd(f"動画の読込 -> {self.inMoviePath}", 1)

        # 動画のフレーム数の取得
        tempfps = self.capture.get(cv2.CAP_PROP_FPS)
        self.fps = int(int((tempfps+0.5)*10)/10)                    # fpsを小数点以下で四捨五入
        keiUtil.logAdd(f"「{self.movie_FileName}」, 平均フレーム数:{self.fps} ({self.capture.get(cv2.CAP_PROP_FPS)})")

        # 動画の総フレーム数の取得
        self.totalCount = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        keiUtil.logAdd(f"総フレーム数:{self.totalCount} (再生時間：{self.getTotalMovieCount()})")

        # 動画タイトルの更新
        self.movieStrvar.set(self.movie_FileName)

        # 動画の時間表示の更新
        self.updateMovieCount()

    ###############################################################################
    # 動画の再生時間を更新する
    ################################################################################
    def updateMovieCount(self, frameNum=0):
        if ( frameNum == 0 or (frameNum % self.fps) == 0):
            currentTime = keiUtil.secToTime((int)(frameNum/self.fps))
            maxTime = keiUtil.secToTime((int)(self.totalCount/self.fps))
            self.secStrvar.set(f"{currentTime[0]:02d}:{currentTime[1]:02d}:{currentTime[2]:02d}/"
                f" {self.getTotalMovieCount()}")    # 動画カウントの更新
#            self.secStrvar.set(f"{currentTime[0]:02d}:{currentTime[1]:02d}:{currentTime[2]:02d}/"
#                f"{maxTime[0]:02d}:{maxTime[1]:02d}:{maxTime[2]:02d}")    # 動画カウントの更新

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
