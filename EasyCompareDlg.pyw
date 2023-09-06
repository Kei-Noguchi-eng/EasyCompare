# -*- coding: utf8 -*-
import tkinter as tk
from tkinter import *
from tkinter import simpledialog
import keiUtil
import configparser
#import ClipMovieDlg
import threading

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

        # # フレームの設定
        self.config(bg="whitesmoke")            # 背景色を指定
        self.propagate(False)                   # フレームのpropagate設定 (この設定がTrueだと内側のwidgetに合わせたフレームサイズになる)
     
        # 実行内容
        self.pack()                             # フレームを配置
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
        # メイン画面非表示化
        self.pack_forget()
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
        self.pictCanvas = tk.Canvas(self.master, width=560, height=150, bg="lightgreen")
        self.pictCanvas.place(x=20, y=10)
        self.pictCanvas.create_text(290, 85, text=r"画像用スペース", font=("MSゴシック体", "18","bold"))
 
        # CLIPボタン (抽出)
        self.button_clip = tk.Button(self.master, width=8, height=2, text=r"CLIP", font=("MSゴシック体", "18","bold"), command = self.createClipMovieDlg)
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
class ClipMovieDialog(simpledialog.Dialog):

    ###############################################################################
 	# コンストラクタ
    ###############################################################################
    def __init__(self, master, title=None) -> None:
        parent = master

        # ダイアログの初期化
        # 背景色を変えるためにオーバーライドしている。
#        Toplevel.__init__(self, parent, bg="red")  # 背景色の変更
        Toplevel.__init__(self, parent)  # 背景色の変更

        keiUtil.logAdd("ClipMovieDlg 起動")
    
        self.withdraw()                 # この時点ではまだ非表示

        # タスクバーに表示しない
        if parent.winfo_viewable():
            self.transient(parent)  

        self.title("ClipMovie") # タイトルの指定
        self.parent = parent

        self.result = None

        self.create_widget_sub()

        if not self.initial_focus:
            self.initial_focus = self

        # ウィンドウを閉じるイベントの設定 
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        # ウィンドウの表示位置を調整する
        if self.parent is not None:
            self.geometry("800x600+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        # ウィンドウ表示制御
        self.deiconify()                # ここで表示
        self.initial_focus.focus_set()  # フォーカスを新しいウィンドウをへ移す
        self.wait_visibility()          # ウィンドウが画面に表示されるまで待ち、grab_set を呼ぶ
        self.grab_set()                 # モーダルにする
 
        # ダイアログが閉じられるまで待つ
        self.wait_window(self)

        # 最後にボタンを復元
        mainFrame.pack()
        keiUtil.logAdd("ClipMovieDlg 終了")

    ###############################################################################
	# デストラクタ
    ###############################################################################
    def __del__(self):
        # 最後にボタンを復元
        mainFrame.pack()
        keiUtil.logAdd("ClipMovieDlg 終了")

    def test(self):
        print("test")

    ###############################################################################
    # create_widgetメソッドを定義
    ###############################################################################
    def create_widget_sub(self):
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
#        self.buttonbox()
        # ピクチャ用スペース (キャンバス)
        # pictCanvas_sub = tk.Canvas(body, width=560, height=150, bg="lightgreen")
        # pictCanvas_sub.place(x=20, y=10)
        # pictCanvas_sub.create_text(290, 85, text=r"画像用スペース", font=("MSゴシック体", "18","bold"))
 
        # CLIPボタン (抽出)
        button_clip_sub = tk.Button(body, width=8, height=2, text=r"CLIP", font=("MSゴシック体", "18","bold"))
        button_clip_sub.place(x=20, y=170, width=275, height=170)
 
        # COMPボタン (比較)
        button_comp_sub = tk.Button(body, width=8, height=2, text=r"COMP", font=("MSゴシック体", "18","bold"))
        button_comp_sub.place(x=305, y=170, width=275, height=170)
 
        # 設定ボタン
        button_set_sub = tk.Button(body, width=27, height=2, text="SET", font=("MSゴシック体", "18","bold"), command = self.test)
        button_set_sub.place(x=30, y=350, width=100, height=40)

        # 終了ボタン
        button_exit_sub = tk.Button(body, width=27, height=2, text="EXIT", font=("MSゴシック体", "18","bold"))
        button_exit_sub.place(x=470, y=350, width=100, height=40)



###############################################################################
# 処理のコール    
###############################################################################
if __name__ == "__main__":
    root = tk.Tk()                              # Tk オブジェクトの生成
    mainFrame = MainFrame(master = root)        # Tk オブジェクトを指定して フレームのウィンドウを生成
    mainFrame.mainloop()                        # 生成したウィンドウの表示 (メインループ)


