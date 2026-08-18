import cv2
import numpy as np
import mss
import pytesseract
from pynput.keyboard import Controller
import time

# pynputのキーボードコントローラー（遅延ゼロで入力可能）
keyboard = Controller()

def main():
    # 【重要】読み取る画面の範囲
    # MacのRetinaディスプレイの場合、実際のピクセル数は2倍になることが多いです。
    # 例: 画面上で 500x600 の位置でも、ここでは 1000x1200 と指定する必要があるかもしれません。
    monitor = {"top": 600, "left": 500, "width": 400, "height": 60}

    print("3秒後に開始します。寿司打の画面を準備してください...")
    time.sleep(3)
    print("爆速モード起動！ (終了するにはターミナルで Ctrl+C)")

    last_text = ""

    try:
        # mss（超高速キャプチャ）を起動
        with mss.mss() as sct:
            while True:
                # 1. 画面キャプチャ（pyautoguiの数倍〜数十倍高速）
                img = np.array(sct.grab(monitor))

                # 2. 画像の前処理
                # mssはBGRA形式で画像を取得するので、グレースケールに変換
                gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
                
                # 寿司打の文字色（白や黒）に合わせて二値化
                # ※背景を消して文字だけをくっきりさせる処理。ここの数値調整が命です。
                _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

                # 3. OCR (設定を最速モードの --psm 7 に指定)
                # psm 7 は「画像全体を1行のテキストとして扱う」モードで処理が速いです
                custom_config = r'--psm 7 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz-!?'
                text = pytesseract.image_to_string(binary, lang='eng', config=custom_config).strip().lower()

                # 4. キー入力 (pynputでインターバル0の瞬間入力)
                if text and text != last_text:
                    print(f"認識: {text}")
                    
                    # 取得した文字列を一瞬で（遅延0で）叩き込む
                    keyboard.type(text) 
                    
                    last_text = text

    except KeyboardInterrupt:
        print("\n終了しました。")

if __name__ == "__main__":
    main()