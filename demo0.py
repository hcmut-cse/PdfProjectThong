from __future__ import division
import os
import re
import numpy as np
import pdftotext

if __name__ == '__main__':
    # file = os.listdir()
    # file = list(filter(lambda ef: ef[0] != "." and ef[-3:] == "pdf", file))
    folder = "PdfToExtract"
    files = list(filter(lambda pdf: pdf[-3:] == 'pdf' ,os.listdir(folder)))
    for filename in files:
        # Covert PDF to string by page
        # print(filename)

        with open(folder + '/' + filename, "rb") as f:
        #     for i in f:
        #         print(i)
            pdf = pdftotext.PDF(f)
        if (pdf[0] != ""):
            with open(folder + '/' + filename[:-3]+"txt", "w+") as f:
                for page in pdf:
                    f.write(page)
