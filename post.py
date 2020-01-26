import cv2
import os
import pytesseract
import csv

pytesseract.pytesseract.tesseract_cmd = \
    r'C:\Program Files\Tesseract-OCR\tesseract'

location = r'small'
location2 = r'snippets'


def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)

i = 0
for f in os.listdir(location):
    image = cv2.imread(os.path.join(location, f))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV,11,30)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9))
    dilate = cv2.dilate(thresh, kernel, iterations=12)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    ROI_number = 0
    for c in cnts:
        area = cv2.contourArea(c)
        if area > 10000:
            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 3)
            if area > 160000:
                ROI = image[y:y+h, x:x+w]
                cv2.imwrite(os.path.join(location2, 'ROI_{}.png'.format(ROI_number)), ROI)
                ROI_number += 1

    resize1 = ResizeWithAspectRatio(thresh, width=880)
    resize2 = ResizeWithAspectRatio(dilate, width=880)
    resize = ResizeWithAspectRatio(image, width=880)

    #cv2.imshow('thresh', resize1)
    #cv2.imshow('dilate', resize2)
    #cv2.imshow('image', resize)
    #cv2.waitKey()

    d = {}
    for snips in os.listdir(location2):
        s = cv2.imread(os.path.join(location2, snips))
        g = cv2.cvtColor(s, cv2.COLOR_BGR2GRAY)
        (thresh, bw) = cv2.threshold(g, 127, 255, cv2.THRESH_BINARY_INV)
        bw_blur = cv2.blur(bw, (5, 5))
        bw_small = ResizeWithAspectRatio(bw_blur,
                                              width=3*bw_blur.shape[1]//2,
                                              height=3*bw_blur.shape[0]//2)
        d[snips] = pytesseract.image_to_string(bw_small,
                                               lang='eng').replace('\n',
                                                                       ' ')
    i += 1
print(d)

lst = []
with open('product_dictionary.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        lst.append(', '.join(row))
print(lst)
