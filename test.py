
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

# import wda
# import time


if __name__ == '__main__':
    # client = wda.Client('http://localhost:8100')
    # s = client.session('vo.threes.free')
    # w, h = s.window_size()
    # print('sleep 2')
    # time.sleep(2)
    # print('start')
    # print('left')
    # s.swipe(w/2, h/2, 0, h/2, 0.01), # left
    # print('right')
    # s.swipe(w/2, h/2, w, h/2, 0.01), # right
    # print('up')
    # s.swipe(w/2, h/2, w/2, 0, 0.01), # up
    # print('down')
    # s.swipe(w/2, h/2, w/2, h, 0.01)  # down
    img = '/Users/zx/study/zxGit/threes-ai/ocr/exemplars/iphone/tile/3.2.png'
    print(Image.open(img))
    print(pytesseract.image_to_string(Image.open(img), config='-psm 6'))





