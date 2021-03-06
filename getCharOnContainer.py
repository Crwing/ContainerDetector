import os
from operator import itemgetter
import cv2
# sys.path.append(os.path.abspath('./util/'))
from util import util

# Read image
img = cv2.imread('2.jpg', cv2.CAP_OPENNI_GRAY_IMAGE)
# Convert to gray
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Binaryzation
_, gray = cv2.threshold(gray, 100, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
# Mser
mser = cv2.MSER_create()
regions, _ = mser.detectRegions(gray)

rects = sorted([cv2.boundingRect(p.reshape(-1, 1, 2)) for p in regions], key=itemgetter(0, 1, 2, 3))

rect_temp = set()
for idx, rect in enumerate(rects):
    flg_continue = 0
    # prune the boxes if the length-width ratio is too large than a normal character
    if rect[2] / rect[3] > 1.5 or rect[3] / rect[2] > 6:
        rect_pre = rect
        continue
    if idx > 0:
        # prune the duplicate boxes
        # if rect == rect_pre:
        #     continue
        if rect[0] == rect_pre[0] and rect[1] == rect_pre[1]:
            continue

        # prune the boxes which inside another boxes
        for rect_tmp in rect_temp:
            if rect_tmp[0] <= rect[0] < rect_tmp[0] + rect_tmp[2] \
                    and rect_tmp[1] <= rect[1] < rect_tmp[1] + rect_tmp[3]:
                flg_continue = 1
                break
        if flg_continue == 1:
            continue
        rect_temp.add(rect)
        # cv2.rectangle(img, rect[0:2], (rect[0] + rect[2], rect[1] + rect[3]), (0, 0, 255), 1)
    rect_pre = rect
    # generate new image as per box
    obj_gray = gray[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]
    obj_color = img[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]
    obj_gray = cv2.resize(obj_gray, (28, 28), interpolation=cv2.INTER_CUBIC)
    obj_color = cv2.resize(obj_color, (28, 28), interpolation=cv2.INTER_CUBIC)
    obj_gray = util.cvtBKchar2WHT(obj_gray)
    set_path = os.path.abspath('./noise_or_char') + os.path.sep
    cv2.imwrite(set_path + 'test' + str(idx) + '.jpg', obj_gray)
    cv2.imwrite(set_path + 'test_color' + str(idx) + '.jpg', obj_color)
