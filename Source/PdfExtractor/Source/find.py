from __future__ import division
import os
import json
import numpy as np
from difflib import SequenceMatcher
import pdftotext
from preprocess import preProcessPdf
from processData import extractData
from removeHeaderFooter import removeHeaderAndFooter
from removeWatermark import removeWatermark
import re
import string

CURR_KW = {}
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
def countKeyword(CONFIG):
    count = 0
    for key1 in CONFIG:
        key1 = key1.lower()
        if (len(CURR_KW) == 0):
            CURR_KW[key1] = 1
        else:
            if key1 in CURR_KW:
                CURR_KW[key1] = CURR_KW[key1] + 1
            elif key1 not in CURR_KW:
                for key2 in list(CURR_KW):
                    ratio = similar(key1,key2)
                    if (ratio >= 0.85):
                        CURR_KW[key2] = CURR_KW[key2] + 1
                        break
                    else:
                        count = count + 1
                        if (count == len(CURR_KW)):
                            CURR_KW[key1] = 1
                            count = 0
def detectInData(fullPdf, listCheck):
    listPdf = []
    for line in fullPdf:
        line = line.lower()
        listLine = []
        listLine = re.split("\\s \\s+", line)
        listPdf.append(listLine)
    #print(listPdf)  
    # for listLine in listPdf:
    #     for key in list(CURR_KW):
    #         for ele in listLine:
    #             ratio = similar(ele, key)
    #             if (ratio >= 0.8):
    #                 ele = ele.replace(":","")
    #                 ele = ele.strip()
    #                 if ele not in listCheck:
    #                     listCheck.append(ele)
    #                     note = ele + " is a new keyword"
    #                     print(note)
    for listLine in listPdf:
        for key in list(CURR_KW):
            for ele in listLine:
                ratio = similar(ele, key)
                if (ratio >= 0.8):
                    ele = ele.replace(":","")
                    ele = ele.strip()
                    if ele not in listCheck:
                        listCheck.append(ele)
                        note = ele + " is a new keyword"
                        print(note)
def detectNotInData(fullPdf, listCheck):
    listPdf = []
    for line in fullPdf:
        line = line.lower()
        listLine = []
        listLine = re.split("\\s \\s+", line)
        listPdf.append(listLine)
    for listLine in listPdf:
        for ele in listLine:
            result = re.findall(r'[\s\w\\/\\."]+[\s]*:', ele)
            for i in result:
                if ":" in i:
                    x = re.search(":", i)
                    keyword = i[0:x.start()]
                    keyword = keyword.strip()
                    #print(keyword)
                    if keyword not in listCheck:
                        keyword = keyword + " is a new keyword"
                        print(keyword)
if __name__ == '__main__':
    PDF = ["1","2","3","5","6","7","8","9","10","11","12","16","17"]

    # take keyword from folder 4 to check
    with open('../' + "4" + '/' + "4" + '.json', 'r', encoding='utf8') as json_file:
        ORIGINAL_CONFIG_CHECK = json.load(json_file)
    CONFIG_CHECK = ORIGINAL_CONFIG_CHECK[0].copy()
    listCheck = []
    for key in CONFIG_CHECK:
        key = key.lower()
        key = re.sub(r'[0-9]+', '', key)
        key = key.replace("_","")
        listCheck.append(key)

    # Take keyword from others template to make data
    for PDF_TYPE in PDF:
        fileName = list(filter(lambda pdf: pdf[-3:] == 'pdf' ,os.listdir('../' + PDF_TYPE)))
        with open('../' + PDF_TYPE + '/' + PDF_TYPE + '.json', 'r', encoding='utf8') as json_file:
            ORIGINAL_CONFIG = json.load(json_file)
        for file in fileName:
	        # Reset Current CONFIG
            CONFIG = ORIGINAL_CONFIG[0].copy()
            HF_CONFIG = ORIGINAL_CONFIG[1].copy()
            CURR_CONFIG = {}

	        # Sort CONFIG from top to bottom, from left to right
            configByColumn = dict(sorted(CONFIG.items(), key=lambda kv: kv[1]['column'][0]))
            CONFIG = dict(sorted(configByColumn.items(), key=lambda kv: kv[1]['row'][0]))
	        # print(CONFIG)

	        # Create config for current pdf
            for key in CONFIG:
                CURR_CONFIG[key] = {}
                CURR_CONFIG[key]['row'] = CONFIG[key]['row'].copy()
                CURR_CONFIG[key]['column'] = CONFIG[key]['column'].copy()
            countKeyword(CURR_CONFIG)

    print("----------------------------------------------------------------")
    print("Keyword in data:")
    for kw in CURR_KW:
        print(kw)
    print("----------------------------------------------------------------")
    print("Keyword in CONFIG 4:")
    for key in listCheck:
        print(key)
    print("----------------------------------------------------------------")
    PDF_TYPETEST = "4"
    file = "SGNV56782400_1_SI.pdf"
    print(file)
    fullPdf, removed = preProcessPdf('../' + PDF_TYPETEST + '/' + file, HF_CONFIG)
    detectInData(fullPdf, listCheck)
    detectNotInData(fullPdf, listCheck)