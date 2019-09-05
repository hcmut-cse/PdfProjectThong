from __future__ import division
import os
import re
import numpy as np
import pdftotext
from difflib import SequenceMatcher
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


# tabula.convert_into("VN101466/SI_HANV07541400.pdf", "output.csv", output_format="csv", pages='all')

keyWord =  {"VN101466" : ["From", "To", "Booking No.", "Date", "Shipper Name & Address", "Consignee Name & Address", "Notify Party", "Port of Loading",
                        "Port of Discharge", "Place of Delivery", "Vessel", "Etd", "Container/Seal No.", "Packages", "Description of Goods", "G.W (KGS)",
                        "CBM", "Remarks", "Payment"],
            "VN103933" : ["Shipper", "Reference No.", "Booking No.", "Consignee", "TO", "FROM", "TEL", "ATTN", "E-MAIL", "M.B/L Type", "Notify",
                        "HS Code", "M.Vessel/Voyage", "ETD", "Port of Loading", "Port of Discharge", "Delivery"],
            "VN104021" : ["To", "From", "Atnn", "Remark", "SHIPPER", "DATE", "S/O NO", "CONSIGNEE", "HS CODE", "NOTIFY", "ALSO NOTIFY", "VESSEL / VOYAGE", "PLACE OF RECEIPT",
                        "PORT OF LOADING", "PORT OF DISCHARGE", "PLACE OF DELIVERY", "FINAL DESTINATION", "JOB No.", "SOB DATE", "ETD DATE", "MOVEMENT"]}


if __name__ == '__main__':
    key = list(keyWord.keys())
    for i in range(len(keyWord)):
        print("%d. %s" % (i, key[i]))
    index = input("Please choose a format: ")
    format = key[int(index)]
    file = os.listdir(format)
    file = list(filter(lambda ef: ef[0] != "." and ef[-3:] == "pdf", file))

    file = ["SI_HANV07496600.pdf"]
    for filename in file:
        result = []
        # Covert PDF to string by page
        print(filename)

        with open(format+"/"+filename, "rb") as f:
            pdf = pdftotext.PDF(f)
        if (pdf[0] != ""):
            result = pdf

        wordBlockList = [] # Store word blocks line by line
        lineList = [] # Store each line

        for page in result:
            print(page)
            page = page.replace(":", "")
            lineSplitList = page.split("\n")
            for line in lineSplitList:
                lineList.append(line)
                lineSplit = re.split(r'\s{4,}', line)
                lineSplit = [block.strip() for block in lineSplit]
                wordBlockList.append(lineSplit)
                # print(lineSplit)

        extracted = {}

        # Find information by keyWord
        for line in wordBlockList:
            lineLength = len(line)
            for i in range(lineLength):
                if (line[i] in keyWord[format]):
                    extracted[line[i]] = ""

                    # On the same line with keyWord
                    if (i + 1 < lineLength):
                        if (line[i+1] not in keyWord[format]):
                            extracted[line[i]] += line[i+1]

                    # Below keyWord line
                        # Same position in line
                    if (extracted[line[i]] == ""):
                        # print(line[i])
                        index = wordBlockList.index(line) + 1
                        stringIndex = lineList[index-1].index(line[i])
                        space = 0

                        while (True):

                            if (index == len(wordBlockList) - 1): # or i >= len(wordBlockList[index])
                                break

                            if (i + 1 < lineLength):
                                stopIndex = lineList[wordBlockList.index(line)].index(line[i+1])
                            else:
                                stopIndex = len(lineList[index])

                            informBlock = re.split(r'\s{4,}', lineList[index][stringIndex:stopIndex])
                            # print(informBlock)
                            if (set(informBlock) == {""}):
                                if (space == 1):
                                    break
                                space += 1
                                index += 1
                                continue


                            if (informBlock[0] not in keyWord[format] and informBlock[0] != ""):
                                if (informBlock[0] in wordBlockList[index]):
                                    extracted[line[i]] += informBlock[0] + '\n'
                                else:
                                    blockIndex = -1
                                    for k in range(len(wordBlockList[index])):
                                        if (SequenceMatcher(None, informBlock[0], wordBlockList[index][k]).ratio() > 0.9 and abs(lineList[index].index(wordBlockList[index][k]) - stringIndex) <= 10):
                                            print(wordBlockList[index][k])
                                            extracted[line[i]] += wordBlockList[index][k] + '\n'
                                            blockIndex = k
                                            break
                                    if (blockIndex == -1):
                                        break
                            else:
                                if (space == 1):
                                    break
                                elif (informBlock[0] == ""):
                                    space += 1
                                else:
                                    break
                            index += 1

                        # Same block order
                    if (extracted[line[i]].strip() == ""):
                        # print(line[i])
                        index = wordBlockList.index(line) + 1
                        # if (index == len(wordBlockList) - 1 or i >= len(wordBlockList[index])):
                        #     continue
                        stringIndex = lineList[index-1].index(line[i])
                        # space = 0
                        #
                        # while (True):
                        #     if (index == len(wordBlockList) - 1): # or i >= len(wordBlockList[index])
                        #         break
                        #
                        #     if (i + 1 < lineLength):
                        #         stopIndex = lineList[wordBlockList.index(line)].index(line[i+1])
                        #     else:
                        #         stopIndex = len(lineList[index])
                        #
                        #     informBlock = re.split(r'\s{4,}', lineList[index][stringIndex:stopIndex])
                        #     if (set(informBlock) == {""}):
                        #         if (space == 1):
                        #             break
                        #         space += 1
                        #         index += 1
                        #         continue
                        #
                        #     # print(informBlock)
                        #     if (informBlock[0] not in keyWord[format] and informBlock[0] in wordBlockList[index] and informBlock[0] != ""):
                        #         extracted[line[i]] += informBlock[0] + '\n'
                        #     else:
                        #         break
                        #     index += 1
                        space = 0
                        while (True):
                            if (index == len(wordBlockList) - 1 or i >= len(wordBlockList[index])): #
                                break

                            if (wordBlockList[index][i] not in keyWord[format]):
                                if (abs(lineList[index].index(wordBlockList[index][i]) - stringIndex) <= 10):
                                    extracted[line[i]] += wordBlockList[index][i] + '\n'
                                else:
                                    space += 1
                                if (space == 2):
                                    break
                            else:
                                break
                            index += 1

        with open(format+"/"+filename[:-3]+"txt", "w+") as f:
            for e in extracted:
                f.write("-----------------------\n")
                f.write(e + ":\n" + extracted[e] + "\n")

# tokens = word_tokenize(text)
# punctuations = ['(',')',';',':','[',']',',']
# stop_words = stopwords.words('english')
# keywords = [word for word in tokens if not word in stop_words and not word in punctuations]

# k = cv2.waitKey(0)
# if k == 27:
#     cv2.destroyAllWindows()
