# -*- coding: utf8 -*-
import tkinter as tk
import keiUtil
import configparser
import clipMovie

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
        master.resizable(False, False)          # ウィンドウサイズの固定
     
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
    # ClipMovieDlgを開く
    ###############################################################################
    def createClipMovieDlg(self):

        # ClipMovieDlg の作成
        subWindowClip = tk.Toplevel(self)           # サブウィンドウを開く
        clipMovie.clipMovie(subWindowClip) # Viewクラス生成

        # # モーダルにする設定
        subWindowClip.grab_set()                    # モーダルにする
        subWindowClip.focus_set()                   # フォーカスを新しいウィンドウをへ移す
        subWindowClip.transient(mainFrame.master)   # タスクバーに表示しない

        keiUtil.logAdd("ClipMovieDlg 起動")

        # ダイアログが閉じられるまで待つ
        mainFrame.wait_window(subWindowClip)
        keiUtil.logAdd("ClipMovieDlg 終了")


###############################################################################
# 処理のコール    
###############################################################################
if __name__ == "__main__":
    root = tk.Tk()                              # Tk オブジェクトの生成
    mainFrame = MainFrame(master = root)        # Tk オブジェクトを指定して フレームのウィンドウを生成
    mainFrame.mainloop()                        # 生成したウィンドウの表示 (メインループ)
    keiUtil.logAdd("EasyCompare 終了\n\n")


