
###############################################################################
# VideoFile クラス　(動画ファイルの構造体)
###############################################################################
class VideoFile:

    ###############################################################################
 	# コンストラクタ
    ###############################################################################
    def __init__(self, moviePath):
        self.path = moviePath     # 読み込みファイルのパス

    ###############################################################################
 	# 動画ファイルの読み込み
    ###############################################################################
    def readFile(self, videoFile):
        self.fileName:str = ""     # 動画のファイル名
        self.totalCount:int = 0          # 動画の総フレーム数
        self.fps:int = 0                 # 動画のfps数

###############################################################################
# MovieCapture クラス
###############################################################################
class MovieCapture:

    ###############################################################################
 	# イメージの解放
    ###############################################################################
    def release_capture(self):
        # 動画イメージの解放
        if self.bCatchedMovie == True:
            self.capture.release()
            self.bCatchedMovie = False


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
                tk.messagebox.showerror("画像取得エラー", f"{text}\n\n{frame_Num}フレーム目:{self.s_myVideo.path}")
            keiUtil.logAdd(f"{text}\n -> {frame_Num}フレーム目:{self.s_myVideo.path}", 2)
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
    # 動画が対応しているか確認する
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
        tk.messagebox.showwarning(title="ImportError", message=f"{errorText}/n{self.s_myVideo.path}")
        keiUtil.logAdd(f"{errorText} -> {self.s_myVideo.path}")

        self.capture.release()
        self.s_myVideo.path = ""
        self.inPathStrvar.set(self.s_myVideo.path)
        self.bCatchedMovie = False
        self.enableWidget()
    
    ###############################################################################
    # 動画の総時間を取得する
    ################################################################################
    def getTotalMovieCount(self):
        maxTime = keiUtil.secToTime((int)(self.s_myVideo.totalCount/self.s_myVideo.fps))
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
        pictDir = f"{outFolderPath}/{self.s_myVideo.fileName}"  # 「引数の出力先フォルダ\動画のファイル名」
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
                pictPath = f"{pictDir}/{self.s_myVideo.fileName}_{count:06}_{keiUtil.getTime()}.png"
                cv2.imwrite(pictPath, frame)
                keiUtil.logAdd(f"画像出力:{pictPath}")

            count += 1  # カウントアップ

