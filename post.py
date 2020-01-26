import cv2
import os
import pytesseract
from fuzzywuzzy import process, fuzz
from operator import itemgetter
import csv
from typing import List

pytesseract.pytesseract.tesseract_cmd = \
    r'C:\Program Files\Tesseract-OCR\tesseract'

location = r'small'
location2 = r'snippets'


def clean_string(s: str) -> str:
    product_list = []
    condition = False
    with open('product_dictionary.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            product_list.append(', '.join(row))
    list_of_words = s.split()
    for word in list_of_words:
        for product in product_list:
            if word in product:
                condition = True
        if not condition:
            list_of_words.remove(word)
    final_string = ''
    for w in list_of_words:
        final_string += w + ' '
    return final_string


def get_list_of_numbers(block_str: str) -> list:
    new_list =[]
    for letter in block_str:
        if letter.isnumeric():
            if float(letter) > 100:
                letter = str(float(letter)/100)
            i = block_str.index(letter)
            k= 0
            while k < 2:
                right_limit = block_str[i + 1:block_str.find(' ')]
                i = block_str.find(' ')
                k += 1
            i = block_str.index(letter)
            condition = True
            n = i
            j = 0
            while condition:
                if block_str[n] == ' ' and j < 2:
                    j + 1
                elif block_str[n] == ' ':
                    left_limit = block_str[n + 1:i]
                    condition = False
                n - 1
            new_list.append(left_limit + block_str[i] + right_limit)
            return new_list


def get_unit_promo_price(lst: list) -> float:
    for val in lst:
        if '$' in val:
            if '/' in val and val(val.find('/') + 1).isnumeric():
                return val[val.find('/') + 1]/val[val.find('/') - 1]
            elif 'save' in val:
                None
            return val[val.find('$') + 1]


def get_least_unit_promo_price(lst: list, block_str: str) -> int:
    for val in lst:
        if '/' in val and val(val.find('/') + 1).isnumeric():
            return val[val.find('/') - 1]
        elif 'buy one' in block_str or 'get one free' in block_str:
            return 2
    return 1


def get_save_per_unit(lst: list):
    for val in lst:
        if 'save' in val:
            for c in val:
                if c.isnumeric():
                    return val[val.find(c): val.find(' ')]


def string_to_list(flyer_num: str, data: str, cur_list: list) -> None:
    add_info_from_flyer(flyer_num, data, cur_list)


def add_info_from_flyer(flyer_num: str, block_text: str,
                        cur_list: list) -> None:
    info_list = get_list_of_numbers(block_text)
    new_product = []
    new_product.append(flyer_num)
    new_product.append(find_product_name(block_text))
    new_product.append(get_unit_promo_price(info_list))  # append 1 for now
    new_product.append(find_uom(block_text))
    new_product.append(get_least_unit_promo_price(info_list, block_text))  # for now / should be least unit for promo
    new_product.append(get_save_per_unit(info_list))  # for now / should be save_per_unit
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

dictionaries = open('dictionary of words', 'r')
list_of_snips = dictionaries.readlines()
dictionaries.close()
output_list = []
d ={}
for snips in list_of_snips:
    date = snips[:snips.find(':::')]
    string = snips[snips.find(':::') + 2:]
    clean_string = clean_string(string)
    if d.get(date, 'Na') == 'Na':
        d[date] = clean_string
    else:
        d[date] += ' ' + clean_string()
    string_to_list(date, d[date], output_list)
sorted_list = sorted(output_list, key=itemgetter(0))
print(sorted_list)
write_report(sorted_list)
