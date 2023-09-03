import os
import cv2
import glob
import numpy as np

hitMode = 1         # 0:類似度が最大の場所を選択する #1:基準値以上場所を選択する
threshold = 0.95    # 閾値の指定

# 取得画像、探索画像の指定
# サンプルfolderの場合
#imgPicturePath = r"./picture/sample/folder/folder.png" # 取得画像のパス
#serchFilesPath = r"./parts/sample/folder/*"            # 探索画像フォルダのパス
# サンプルnatureの場合
imgPicturePath = r"./picture/sample/nature/nature_compTest.png"  # 取得画像のパス
serchFilesPath = r"./parts/sample/nature/*"             # 探索画像フォルダのパス

# 画像のファイル名を取得 (出力ファイルのフォーマット用)
resultPictureName = os.path.splitext(os.path.basename(imgPicturePath))[0]

# 画像の読み込み
img = cv2.imread(imgPicturePath)    # 取得画像(探索される対象)
files = glob.glob(serchFilesPath)   # 探索画像フォルダのパス               

# 処理本体
def main():
    
    for fname in files:
        # 探索画像の数だけ繰り返す

        # 探索画像の指定
        template = cv2.imread(fname)

        # テンプレートマッチを行う
        templateMatching(img, template, hitMode)    # 暫定で複数箇所 hit で制作


# 画像のテンプレートマッチを行う
def templateMatching(img, template, hitMode):
    
    # グレースケール化
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # テンプレート画像の高さ、幅を取得する
    h, w = template_gray.shape

    # 処理対象画像に対して、テンプレート画像との類似度を算出する
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # hitMode により処理分岐 (Python3.10以降で match 文対応)
    match hitMode:  

        case 0: # 類似度最大の場所を選択

            # マッチング結果の取得
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(res) # 類似度最小、最大、最小の座標、最大の座標

            if maxVal > threshold:
                # テンプレートマッチの結果が閾値以上

                # 類似度が最大の場所を基準に赤枠で囲む
                cv2.rectangle(img, maxLoc, (maxLoc[0] + w, maxLoc[1] + h), (0, 0, 255), 2)

        case 1: # 類似度が閾値以上の場所を選択

            # 類似度の高い部分を検出する
            loc = np.where(res >= threshold)

            # 検出した箇所をループで回り、赤枠で囲む
            for pt in zip(*loc[::-1]):
                # ※ 同じ場所で複数回描画している部分は要修正

                # 検出箇所を赤枠で囲む
                cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
#                print("hit"+ str(pt))   # デバッグ用

#        case _: # default

    # 画像の保存
    cv2.imwrite(f"./comp/{resultPictureName}_templateMatching_result.png", img)


# 処理のコール
if __name__ == "__main__":
    main()