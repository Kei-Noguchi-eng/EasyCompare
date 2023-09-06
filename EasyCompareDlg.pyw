# -*- coding: utf8 -*-
import tkinter as tk
import tkinter.ttk as ttk
import keiUtil
import configparser
#import ClipMovieDlg
import aaa
from tkinter import *
from tkinter import simpledialog

inifile = configparser.SafeConfigParser()
inifile.read('settings.ini')

keiUtil.toolName = "EasyCompareDlg"
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
        master.title("EasyCompare")        # ウィンドウタイトル
        master.geometry("600x400")         # ウィンドウサイズ(幅x高さ)
        master.resizable(False, False)     # 大きさの固定

        # # フレームの設定
        # self.config(bg="whitesmoke")            # 背景色を指定
        # self.propagate(False)                   # フレームのpropagate設定 (この設定がTrueだと内側のwidgetに合わせたフレームサイズになる)
     
        # 実行内容
    #    self.pack()                             # フレームを配置
        self.create_widget()                    # create_widget() の実行

        keiUtil.logAdd("EasyCompareDlg 起動")


    ###############################################################################
	# デストラクタ
    ###############################################################################
    def __del__(self):
        keiUtil.logAdd("EasyCompareDlg 終了\n\n")

    ###############################################################################
    # ClipMovieDlgを開く
    ###############################################################################
    def createClipMovieDlg(self):
        self.sub_root = ClipMovieDialog(root)
#        self.sub_root_failure = None

    ###############################################################################
    # ウィンドウを閉じる (終了ボタン)
    ###############################################################################
    def close_window(self):
        root.destroy()              # Tk オブジェクト(親) から破棄する

    ###############################################################################
    # create_widgetメソッドを定義
    ###############################################################################
    def create_widget(self):
 
        # # 全体の親キャンバス ※※※ 今は使わない ※※※
        # self.canvas_bg = tk.Canvas(self.master, width=600, height=400)
        # self.canvas_bg.pack()
 
        # ピクチャ用スペース (キャンバス)
        pictCanvas = tk.Canvas(self.master, width=560, height=150, bg="lightgreen")
        pictCanvas.place(x=20, y=10)
        pictCanvas.create_text(290, 85, text=r"画像用スペース", font=("MSゴシック体", "18","bold"))
 
        # CLIPボタン (抽出)
        button_clip = tk.Button(self.master, width=8, height=2, text=r"CLIP", font=("MSゴシック体", "18","bold"), command = self.createClipMovieDlg)
        button_clip.place(x=20, y=170, width=275, height=170)
 
        # COMPボタン (比較)
        button_comp = tk.Button(self.master, width=8, height=2, text=r"COMP", font=("MSゴシック体", "18","bold"))
        button_comp.place(x=305, y=170, width=275, height=170)
 
        # 設定ボタン
        button_set = tk.Button(self.master, width=27, height=2, text="SET", font=("MSゴシック体", "18","bold"))
        button_set.place(x=30, y=350, width=100, height=40)

        # 終了ボタン
        button_exit = tk.Button(self.master, width=27, height=2, text="EXIT", font=("MSゴシック体", "18","bold"), command = self.close_window)
        button_exit.place(x=470, y=350, width=100, height=40)


###############################################################################
# ClipMovieDialogクラス (tk.Frameを継承) 
###############################################################################
class ClipMovieDialog(simpledialog.Dialog):

    ###############################################################################
 	# コンストラクタ
    ###############################################################################
    def __init__(self, master, title=None) -> None:
        parent = master

        # ダイアログの初期化
        # 背景色を変えるためにオーバーライドしている。
        Toplevel.__init__(self, parent, bg="red")  # 背景色の変更
        #super().__init__(master)

        self.withdraw()  # この時点ではまだ非表示


        if parent.winfo_viewable():
            # ウィンドウが表示済みか
            self.transient(parent)  # タスクバーに表示しない

        # if title:
        #     # self.title(title)
        #     self.title("ClipMovie")
        self.title("ClipMovie")

        self.parent = parent

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                      parent.winfo_rooty() + 50))

        self.deiconify()  # become visible now

        self.initial_focus.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()

        self.grab_set()         # モーダルにする
 
        # ダイアログが閉じられるまで待つ
        self.wait_window(self)
        keiUtil.logAdd("ClipMovieDlg 終了")

    ###############################################################################
    # create_widgetメソッドを定義
    ###############################################################################
#    def create_widget(self):


###############################################################################
# 処理のコール    
###############################################################################
if __name__ == "__main__":
    root = tk.Tk()                              # Tk オブジェクトの生成
    mainFrame = MainFrame(master = root)        # Tk オブジェクトを指定して フレームのウィンドウを生成
    mainFrame.mainloop()                        # 生成したウィンドウの表示 (メインループ)


