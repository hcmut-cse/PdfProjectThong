from __future__ import division
import os
import re
import numpy as np
import pdftotext
from .removeHeaderFooter import removeHeaderAndFooter
from .removeWatermark import removeWatermark

def preProcessPdf(filename, HF_CONFIG):
    # for filename in file:
    # Covert PDF to string by page
    # print(filename)

    with open(filename, "rb") as f:
        pdf = pdftotext.PDF(f)

    # Remove header & footer
    # if (len(pdf) > 1):
    #     fullPdf = removeHeaderAndFooter(pdf)
    #     # Join PDF
    #     fullPdf = [line for page in fullPdf for line in page]
    # else:
            # fullPdf = pdf[0].split('\n')

    fullPdf = removeHeaderAndFooter(pdf, HF_CONFIG)
    # Join PDF
    fullPdf = [line for page in fullPdf for line in page if line != '']

    fullPdf, removed = removeWatermark(filename, fullPdf)
    # for line in fullPdf:
    #     print(line)
    return fullPdf, removed

if __name__ == '__main__':
    file = os.listdir()
    file = list(filter(lambda ef: ef[0] != "." and ef[-3:] == "pdf", file))
    # file = ["SBL_FDS_FDSLSGN190223OS.190219164902.pdf"]
    for filename in file:
        fullPdf = preProcessPdf(filename)

        if (fullPdf[0] != ""):
            with open(filename[:-3]+"txt", "w+") as f:
                for line in fullPdf:
                    f.write(line + '\n')
