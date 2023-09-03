import cv2
import numpy as np

# 処理本体
def main():
    # 取得画像
    img = cv2.imread('picture\sample\SampleMovie_000020_20230903_155039.png')

    # 探索画像(パーツ)
    template = cv2.imread('parts\sample\parts_01.png')

    # テンプレートマッチを行う
    templateMatching(img, template)


# 画像のテンプレートマッチを行う
def templateMatching(img, template):
    
    # 画像の読み込み + グレースケール化
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # 処理対象画像に対して、テンプレート画像との類似度を算出する
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # マッチング結果の取得
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(res) # 類似度最小、最大、最小の座標、最大の座標

    # 閾値の指定
    threshold = 0.95
#    threshold = 0.8

#    # 類似度の高い部分を検出する
#    loc = np.where(res >= threshold)
#
    # テンプレート画像の高さ、幅を取得する
    h, w = template_gray.shape
#
#    # 検出した部分に赤枠をつける
#    for pt in zip(*loc[::-1]):
#        cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
##        print('hit')

    if maxVal > threshold:
        # テンプレートマッチの結果が閾値以上

        # 類似度が最大の場所を基準に赤枠で囲む
        cv2.rectangle(img, maxLoc, (maxLoc[0] + w, maxLoc[1] + h), (0, 0, 255), 2)

        # 画像の保存
        cv2.imwrite('comp/tpl_match_after.png', img)

# 処理のコール
if __name__ == "__main__":
    main()