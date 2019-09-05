from __future__ import division
import argparse
import os
import json
import numpy as np
from PdfExtractor.Source.preProcess import preProcessPdf
from PdfExtractor.Source.processData import extractData
from PdfExtractor.Source.posProcess import posProcessData
from PdfExtractor.Source.connectContent import connectContent
import pdftotext


def extractingData(file, PDF_TYPE):
    with open('../Template/' + PDF_TYPE + '.json', 'r', encoding='utf8') as json_file:
        ORIGINAL_CONFIG = json.load(json_file)

    CONFIG = ORIGINAL_CONFIG[0].copy()
    HF_CONFIG = ORIGINAL_CONFIG[1].copy()
    CURR_CONFIG = {}
    with open('../PdfToExtract/' + file, "rb") as f:
        pdf = pdftotext.PDF(f)

    if (PDF_TYPE == "15"):
        if (len(pdf) == 2):
            CONFIG = CONFIG["multi"]
        elif (len(pdf) == 3):
            CONFIG = CONFIG["3"]
        elif (len(pdf) == 1):
            CONFIG = CONFIG["1"]

    # Sort CONFIG from top to bottom, from left to right
    configByColumn = dict(sorted(CONFIG.items(), key=lambda kv: kv[1]['column'][0]))
    CONFIG = dict(sorted(configByColumn.items(), key=lambda kv: kv[1]['row'][0]))
    # print(CONFIG)

    # Create config for current pdf
    for key in CONFIG:
        CURR_CONFIG[key] = {}
        CURR_CONFIG[key]['row'] = CONFIG[key]['row'].copy()
        CURR_CONFIG[key]['column'] = CONFIG[key]['column'].copy()

    # Preproces PDF
    fullPdf, removed = preProcessPdf('../PdfToExtract/' + file, HF_CONFIG)
    # for line in fullPdf:
    #     print(line)
    # Extract data from PDF
    extractedData = extractData(fullPdf, CONFIG, CURR_CONFIG, removed)

    # extractedData = posProcessData(extractedData, CURR_CONFIG, removed)

    length = len(pdf)
    if (length > 1):
        extractedData = connectContent(length, extractedData)
    # for word in removed:
    #     if (removed[word])
    # Save extracted result to file
    with open('../Result/' + file[:-3] + 'txt', 'w', encoding='utf8') as resultFile:
        for key in extractedData:
            resultFile.write("------------------------------------\n")
            resultFile.write("%s:\n%s\n" % (key, extractedData[key]))
            resultFile.write("------------------------------------\n")
