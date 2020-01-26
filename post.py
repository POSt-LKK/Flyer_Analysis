import cv2
import os
import pytesseract
from fuzzywuzzy import process, fuzz
from operator import itemgetter
import csv

pytesseract.pytesseract.tesseract_cmd = \
    r'C:\Users\Kevin Li Chen\AppData\Local\Tesseract-OCR\tesseract'

location = r'small'
location2 = r'snippets'


def string_to_list(flyer_num: str, data: str, cur_list: list) -> None:
    add_info_from_flyer(flyer_num, data, cur_list)


def add_info_from_flyer(flyer_num: str, block_text: str,
                        cur_list: list) -> None:
    new_product = []
    new_product.append(flyer_num)
    new_product.append(find_product_name(block_text))
    # new_product.append(find_unit_promo_price())
    new_product.append(1)  # append 1 for now
    new_product.append(find_uom(block_text))
    new_product.append(1)  # for now / should be least unit for promo
    new_product.append(1)  # for now / should be save_per_unit
    new_product.append(0.0)  # should be discount
    new_product.append(find_if_organic(block_text))
    cur_list.append(new_product)


def find_product_name(block_str: str) -> str:
    product_list = []
    with open('product_dictionary.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            product_list.append(', '.join(row))

    highest_name = process.extractOne(block_str, product_list)
    return highest_name[0]


def find_uom(block_str: str) -> str:
    units_list = []
    with open('units_dictionary.csv', 'r') as f:
        reader2 = csv.reader(f)
        for row in reader2:
            units_list.append(', '.join(row))

    highest_unit = process.extractOne(block_str, units_list)
    return highest_unit[0]


def find_if_organic(block_str: str) -> int:
    organic = fuzz.partial_ratio(block_str.lower(), 'organic')
    if organic > 50:
        return 1
    else:
        return 0


def write_report(data: list) -> None:
    with open('test3.csv', 'w', newline='') as fp:
        a = csv.writer(fp, delimiter=',')
        report = data
        report.insert(0, ['flyer_name', 'product_name', 'unit_promo_price',
                          'uom', 'least_unit_for_promo', 'save_per_unit',
                          'discount', 'organic'])
        a.writerows(report)


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
output_list = []
for f in os.listdir(location):
    image = cv2.imread(os.path.join(location, f))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 30)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    dilate = cv2.dilate(thresh, kernel, iterations=12)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    ROI_number = 0
    for c in cnts:
        area = cv2.contourArea(c)
        if area > 16000:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(image, (x, y), (x + w, y + h), (36, 255, 12), 3)
            if area > 160000:
                ROI = image[y:y + h, x:x + w]
                cv2.imwrite(os.path.join(location2,
                                         'ROI_{0}_{1}.png'.format(i,
                                                                  ROI_number)),
                            ROI)
                ROI_number += 1

    resize1 = ResizeWithAspectRatio(thresh, width=880)
    resize2 = ResizeWithAspectRatio(dilate, width=880)
    resize = ResizeWithAspectRatio(image, width=880)

    # cv2.imshow('thresh', resize1)
    # cv2.imshow('dilate', resize2)
    # cv2.imshow('image', resize)
    # cv2.waitKey()

    d = {}
    for snips in os.listdir(location2):
        s = cv2.imread(os.path.join(location2, snips))
        g = cv2.cvtColor(s, cv2.COLOR_BGR2GRAY)
        (thresh, bw) = cv2.threshold(g, 127, 255, cv2.THRESH_BINARY_INV)
        d[snips] = pytesseract.image_to_string(bw).replace('\n', ' ')
        string_to_list(str(f), d[snips], output_list)
    i += 1
print(d)
sorted_list = sorted(output_list, key=itemgetter(0))
print(sorted_list)
write_report(sorted_list)

os.remove(r"snippets\*.jpg")
