# -*- coding: utf8 -*-
import tkinter as tk
from tkinter import *
from tkinter import simpledialog
import keiUtil
import configparser
#import ClipMovieDlg
#import threading

# import time
# time.sleep(1)     " 待ち時間用 1=1秒

inifile = configparser.SafeConfigParser()
inifile.read('settings.ini')

keiUtil.checkExitFolder(keiUtil.managementArea) # 管理領域の作成
keiUtil.toolName = "EasyCompareDlg"
keiUtil.execDay = keiUtil.getDay() # アプリケーションの起動日の取得
keiUtil.logAdd("EasyCompare 起動")


###############################################################################
# MainFrameクラス (tk.Frameを継承) 
###############################################################################
class MainFrame(tk.Frame):

    ###############################################################################
 	# コンストラクタ
    ###############################################################################
    def __init__(self, master = None):
        super().__init__(master)                # 継承元(tk.Frame) のコンストラクタを呼ぶ

        # ウィンドウの設定
        master.title("EasyCompare")             # ウィンドウタイトル
        master.geometry("600x400")              # ウィンドウサイズ(幅x高さ)
        master.resizable(False, False)          # 大きさの固定
     
        # 実行内容
        self.create_widget()                    # create_widget() の実行

        keiUtil.logAdd("EasyCompareDlg 起動")

    ###############################################################################
	# デストラクタ
    ###############################################################################
#    def __del__(self):
        # 呼ばれない？

    ###############################################################################
    # ウィンドウを閉じる (終了ボタン)
    ###############################################################################
    def close_window(self):
        keiUtil.logAdd("EasyCompareDlg 終了")
        root.destroy()              # Tk オブジェクト(親) から破棄する

    ###############################################################################
    # ClipMovieDlgを開く
    ###############################################################################
    def createClipMovieDlg(self):
#    def createClipMovieDlg(self, event=None):
        subWindow = ClipMovieDialog(master = mainFrame)

    ###############################################################################
    # ClipMovieスレッドを作成する
    ###############################################################################
    # def createClipMovieThread(self, event=None):
    #     th = threading.Thread(target = self.createClipMovieDlg)
    #     th.start()
    #     print("Test")

    ###############################################################################
    # create_widgetメソッドを定義
    ###############################################################################
    def create_widget(self):
 
        # # 全体の親キャンバス ※※※ 今は使わない ※※※
        # self.canvas_bg = tk.Canvas(self.master, width=600, height=400)
        # self.canvas_bg.pack()
 
        # ピクチャ用スペース (キャンバス)
        self.pictCanvas = tk.Canvas(self.master, width=560, height=150, bg="lightgreen")
        self.pictCanvas.place(x=20, y=10)
        self.pictCanvas.create_text(290, 85, text=r"画像用スペース", font=("MSゴシック体", "18","bold"))
 
        # CLIPボタン (抽出)
        self.button_clip = tk.Button(self.master, width=8, height=2, text=r"CLIP", font=("MSゴシック体", "18","bold"), command = self.createClipMovieDlg)
#        self.button_clip.bind("<1>", self.createClipMovieThread)
        self.button_clip.place(x=20, y=170, width=275, height=170)
 
        # COMPボタン (比較)
        self.button_comp = tk.Button(self.master, width=8, height=2, text=r"COMP", font=("MSゴシック体", "18","bold"))
        self.button_comp.place(x=305, y=170, width=275, height=170)
 
        # 設定ボタン
        self.button_set = tk.Button(self.master, width=27, height=2, text="SET", font=("MSゴシック体", "18","bold"))
        self.button_set.place(x=30, y=350, width=100, height=40)

        # 終了ボタン
        self.button_exit = tk.Button(self.master, width=27, height=2, text="EXIT", font=("MSゴシック体", "18","bold"), command = self.close_window)
        self.button_exit.place(x=470, y=350, width=100, height=40)


###############################################################################
# ClipMovieDialogクラス (サブダイアログ　simpledialog.Dialogを継承) 
###############################################################################
class ClipMovieDialog(tk.Frame):

    ###############################################################################
 	# コンストラクタ
    ###############################################################################
    def __init__(self, master, title=None):
    # def __init__(self, master, title=None) -> None:
        super().__init__(master,width=500,height=500,bg="beige")                # 継承元(tk.Frame) のコンストラクタを呼ぶ
        self.pack()

        # モーダルダイアログボックスの作成
        dlg_modal = tk.Toplevel(master=mainFrame)
        dlg_modal.title("Modal Dialog")         # ウィンドウタイトル
        dlg_modal.geometry("300x200+200+200")     # ウィンドウサイズ(幅x高さ+位置補正)

        # モーダルにする設定
        dlg_modal.grab_set()                    # モーダルにする
        dlg_modal.focus_set()                   # フォーカスを新しいウィンドウをへ移す
        dlg_modal.transient(mainFrame.master)   # タスクバーに表示しない

        keiUtil.logAdd("ClipMovieDlg 起動")

        self.create_widget_sub()

        # ダイアログが閉じられるまで待つ
        mainFrame.wait_window(dlg_modal)
        keiUtil.logAdd("ClipMovieDlg 終了")

    ###############################################################################
	# デストラクタ
    ###############################################################################
#    def __del__(self):
#        keiUtil.logAdd("ClipMovieDlg 終了")

    def test(self):
        print("test")

    ###############################################################################
    # create_widgetメソッドを定義
    ###############################################################################
    def create_widget_sub(self):
        # ピクチャ用スペース (キャンバス)
#        pictCanvas_sub = tk.Canvas(, width=560, height=150, bg="lightgreen")
#        pictCanvas_sub.place(x=20, y=10)
#        pictCanvas_sub.create_text(290, 85, text=r"画像用スペース", font=("MSゴシック体", "18","bold"))
 
        # CLIPボタン (抽出)
        button_clip_sub = tk.Button(self, width=8, height=2, text=r"CLIP", font=("MSゴシック体", "18","bold"))
        button_clip_sub.place(x=20, y=170, width=275, height=170)
 
        # COMPボタン (比較)
        button_comp_sub = tk.Button(self, width=8, height=2, text=r"COMP", font=("MSゴシック体", "18","bold"))
        button_comp_sub.place(x=305, y=170, width=275, height=170)
 
        # 設定ボタン
        button_set_sub = tk.Button(self, width=27, height=2, text="SET", font=("MSゴシック体", "18","bold"), command = self.test)
        button_set_sub.place(x=30, y=350, width=100, height=40)

        # 終了ボタン
        button_exit_sub = tk.Button(self, width=27, height=2, text="EXIT", font=("MSゴシック体", "18","bold"))
        button_exit_sub.place(x=470, y=350, width=100, height=40)



###############################################################################
# 処理のコール    
###############################################################################
if __name__ == "__main__":
    root = tk.Tk()                              # Tk オブジェクトの生成
    mainFrame = MainFrame(master = root)        # Tk オブジェクトを指定して フレームのウィンドウを生成
    mainFrame.mainloop()                        # 生成したウィンドウの表示 (メインループ)
    keiUtil.logAdd("EasyCompare 終了\n\n")


