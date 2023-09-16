import configparser

# iniファイル読込
inifile = configparser.SafeConfigParser()
inifile.read("./settings.ini", encoding="utf-8")



###############################################################################
# DrawPicture クラス
###############################################################################
class DrawPicture:

    ###############################################################################
    # ControlSetting クラス　(再生・入出力など設定の構造体)
    ###############################################################################
    class ControlSetting:

        ###############################################################################
        # コンストラクタ
        ###############################################################################
        def __init__(self):
            self.inputMovieFolder = inifile["MOVIE EDIT"]["inputMoviePath"]        # 読み込みファイルのデフォルトフォルダー
            self.outputFolderPath = inifile["MOVIE EDIT"]["outputPicturePath"]     # 出力先フォルダのパス
            self.playDrawFrameFreq:int = 0   # 再生時の描画頻度設定 (キャンバスの更新を何Fごとに行うか)
            self.outputFrameFreq:int = 0     # 出力時の出力頻度の設定 (何フレーム毎に出力するか)
            self.outputStartPos:int = 0      # 出力範囲の開始位置
            self.outputEndPos:int = 0        # 出力範囲の終了位置

    ###############################################################################
    # スレッド処理
    ###############################################################################
    def main_thread_func(self):

        while self.set_movie:
            
            # 再生中はループの処理を繰り返す
            if self.start_movie:            # 再生中
                start = time.time()

                ret, self.video_frame = self.capture.read() # フレーム画像の読み込み

                if ret:
                    self.moveCountUp()                      # 読み込んだ画像でイメージを更新する
#                    oldEnd = end
#                    end = time.time()
                    diff = time.time() - start
#                    tempwait = float((1/self.fps) - diff)
                    tempwait = float((1/self.s_myVideo.fps) - diff - start)
                    if (1/self.s_myVideo.fps) < float((1/self.s_myVideo.fps) - diff):
                        time.sleep(tempwait)
#                        print(f"{tempwait}")
                    else:
                        print("遅延")
#                    print(f"{end- oldEnd}")
#                    print(f"start:{start}_end:{end}_diff:{diff}_delay:{((1/self.fps) - diff)/1000}")
#                    num += 1
                else:
                    self.start_movie = False                # 再生を終了する
                    self.enableWidget()                     # コントロールの有効化

    ###############################################################################
    # 再生中の処理
    ###############################################################################
    def frameCountUp(self):
        
        # if self.start_movie:
        #     self.after(self.timer, self.frameCountUp())

        ret, self.video_frame = self.capture.read() # フレーム画像の読み込み

        if ret:
            self.moveCountUp()                      # 読み込んだ画像でイメージを更新する
        else:
            self.start_movie = False                # 再生を終了する
            self.enableWidget()                     # コントロールの有効化


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
    # 動画の再生時間を更新する
    ################################################################################
    def updateMovieCount(self, frameNum=0):
        if self.bCatchedMovie == False:
            # 動画を読み込んでいなければ return
            return
        
        # スクロールバーの更新
        self.scale_var.set(frameNum)       

        # 動画カウントの更新
        if ( frameNum == 0 or (frameNum % (self.s_myVideo.fps)) == 0):
            # 動画読み込み時 or 1秒に1回更新
            currentTime = keiUtil.secToTime((int)(frameNum/self.s_myVideo.fps))
            self.secStrvar.set(f"{currentTime[0]:02d}:{currentTime[1]:02d}:{currentTime[2]:02d}/"
                f" {self.getTotalMovieCount()}")

