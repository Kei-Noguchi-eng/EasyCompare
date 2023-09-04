# -*- coding: utf8 -*-
import tkinter as tk 
import keiUtil

keiUtil.toolName = "EasyCompareDlg"
keiUtil.logAdd("[Info] EasyCompare 起動")

# MainWindowDlgクラス
class MainWindowDlg(tk.Frame):
	# コンストラクタ
    def __init__(self, master = None):
        super().__init__(master)

        # ウィンドウの設定
        master.title("EasyCompare")       # ウィンドウタイトル
        master.geometry("600x400")        # ウィンドウサイズ(幅x高さ)

        keiUtil.logAdd("[Info] EasyCompareDlg 起動")

       # 実行内容
        self.pack()
        self.create_widget()

	# デストラクタ
    def __del__(self):
        keiUtil.logAdd("[Info] EasyCompareDlg 終了\n\n")

    # ウィンドウを閉じる (終了ボタン)
    def close_window():
        root.destroy()

    # create_widgetメソッドを定義
    def create_widget(self):
 
        # 全体の親キャンバス
        self.canvas_bg = tk.Canvas(self.master, width=600, height=400)
        self.canvas_bg.pack()
 
        # ピクチャ用スペース (キャンバス)
        self.pictCanvas = tk.Canvas(self.canvas_bg, width=560, height=150, bg="lightgreen")
        self.pictCanvas.place(x=20, y=10)
        self.pictCanvas.create_text(290, 85, text=r"画像用スペース", font=("MSゴシック体", "18","bold"))
#        self.pictCanvas.pack()
  
        # CLIPボタン (抽出)
        self.button_clip = tk.Button(self.canvas_bg, width=8, height=2, text=r"CLIP", font=("MSゴシック体", "18","bold"))
        self.button_clip.place(x=20, y=170, width=275, height=170)
 
        # COMPボタン (比較)
        self.button_comp = tk.Button(self.canvas_bg, width=8, height=2, text=r"COMP", font=("MSゴシック体", "18","bold"))
        self.button_comp.place(x=305, y=170, width=275, height=170)
 
        # 設定ボタン
        self.button_set = tk.Button(self.canvas_bg, width=27, height=2, text="SET", font=("MSゴシック体", "18","bold"))
        self.button_set.place(x=30, y=350, width=100, height=40)

        # 終了ボタン
        self.button_exit = tk.Button(self.canvas_bg, width=27, height=2, text="EXIT", font=("MSゴシック体", "18","bold"), command = MainWindowDlg.close_window)
        self.button_exit.place(x=470, y=350, width=100, height=40)


if __name__ == "__main__":

    root = tk.Tk()
    app = MainWindowDlg(master = root)
    app.mainloop()   


