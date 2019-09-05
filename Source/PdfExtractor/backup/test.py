import pdftotext
import json
import numpy as np
import os
import re
from difflib import SequenceMatcher

PDF_TYPE = "VN101466"
# CURR_CONFIG = {}
#
# with open(PDF_TYPE + '/' + PDF_TYPE + '.json', 'r', encoding='utf8') as json_file:
#     CONFIG = json.load(json_file)


fileName = list(filter(lambda pdf: pdf[-3:] == 'pdf' ,os.listdir(PDF_TYPE)))
# fileName = ["SI-SGNV27883400.pdf"]

if __name__ == '__main__':
    for file in fileName:
        # Reset Current CONFIG
        with open(PDF_TYPE + '/' + PDF_TYPE + '.json', 'r', encoding='utf8') as json_file:
            CONFIG = json.load(json_file)
        CURR_CONFIG = {}

        # Load PDF
        with open(PDF_TYPE + '/' + file, "rb") as f:
            pdf = pdftotext.PDF(f)

        # Remove header & footer
        if (len(pdf) > 1):
            fullPdf = []
            for i in range(len(pdf)):
                fullPdf.append(pdf[i].split('\n'))
            # Remove header
            row = 0
            continueRemove = True
            while (True):
                for i in range(len(fullPdf) - 1):
                    if SequenceMatcher(None, ''.join(fullPdf[0][row].split()), ''.join(fullPdf[i+1][row].split())).ratio() < 0.8:
                        continueRemove = False
                        break
                if (continueRemove):
                    for i in range(len(fullPdf)):
                        del(fullPdf[i][row])
                else:
                    break

            # Remove footer
            continueRemove = True
            while (True):
                row = [len(page)-1 for page in fullPdf]
                for i in range(len(fullPdf) - 1):
                    if SequenceMatcher(None, ''.join(fullPdf[0][row[0]].split()), ''.join(fullPdf[i+1][row[i+1]].split())).ratio() < 0.8:
                        continueRemove = False
                        break
                if (continueRemove):
                    for i in range(len(fullPdf)):
                        del(fullPdf[i][row[i]])
                else:
                    break

            # Join PDF
            fullPdf = [line for page in fullPdf for line in page]
        else:
            fullPdf = pdf[0].split('\n')

        # print("Number of lines in PDF: %d" % len(fullPdf))

        # Sort CONFIG from top to bottom, from left to right
        configByColumn = dict(sorted(CONFIG.items(), key=lambda kv: kv[1]['column'][0]))
        CONFIG = dict(sorted(configByColumn.items(), key=lambda kv: kv[1]['row'][0]))
        # print(CONFIG)

        # Create config for current pdf
        for key in CONFIG:
            CURR_CONFIG[key] = {}
            CURR_CONFIG[key]['row'] = CONFIG[key]['row']
            CURR_CONFIG[key]['column'] = CONFIG[key]['column']

        # Display fullPdf
        for i in fullPdf:
            print(i)

        extracted = []
        # Extract data
        extractedData = {}
        for key in CONFIG:
            # print(key)
            if (not CONFIG[key]['isFlex']): # For fixxed elements
                row = CURR_CONFIG[key]['row']
                column = CURR_CONFIG[key]['column']
            else:
                for margin in CONFIG[key]['endObject']:
                    if (CONFIG[key]['endObject'][margin] == -1):
                        # If not define object for margin, it will use absolute location
                        continue
                    else:
                        if (margin == 'top'):
                            # Find nearest upper block
                            if (len(extracted) > 0):
                                keyIndex = -1
                                minDistance = len(fullPdf)
                                for keyE in extracted:
                                    if (CONFIG[keyE]['row'][1] - 1 < CONFIG[key]['row'][0] and minDistance > abs(CONFIG[keyE]['row'][1] - CONFIG[key]['row'][0])):
                                        keyIndex = extracted.index(keyE)
                                        minDistance = abs(CONFIG[keyE]['row'][1] - CONFIG[key]['row'][0])

                                if (keyIndex == -1):
                                    startRow = 0
                                else:
                                    startRow = CURR_CONFIG[extracted[keyIndex]]['row'][1]
                            else:
                                startRow = 0

                            # Get keyword
                            if (CONFIG[key]['endObject']['top'][:4] == 'same'):
                                topFinding = CONFIG[key]['endObject'][CONFIG[key]['endObject']['top'][-4:]]
                                sameLine = 0
                            else:
                                topFinding = CONFIG[key]['endObject']['top']
                                sameLine = 1

                            # Find first row that has keyword from startRow
                            while (True):
                                if (re.search(topFinding, fullPdf[startRow])):
                                    distance = startRow - CURR_CONFIG[key]['row'][0] + sameLine

                                    for keyE in CURR_CONFIG:
                                        if (keyE != key and CONFIG[keyE]['row'][0] == CONFIG[key]['row'][0]):
                                            CURR_CONFIG[keyE]['row'][0] += distance

                                    CURR_CONFIG[key]['row'][0] += distance
                                    break;

                                else:
                                    startRow += 1
                                    if (startRow == len(fullPdf)):
                                        break

                        elif (margin == 'bottom'):
                            # Bottom object is under Top object
                            # print("running bottom")
                            startRow = CURR_CONFIG[key]['row'][0] + 1
                            # print(CURR_CONFIG[key]['row'])
                            # Find first row that has keyword from startRow
                            while (True):
                                if (re.search(CONFIG[key]['endObject']['bottom'], fullPdf[startRow])):
                                    # print(startRow)
                                    distance = startRow - CURR_CONFIG[key]['row'][1]
                                    nearestKey = key
                                    minDistance = len(fullPdf)

                                    for keyE in CURR_CONFIG:
                                        if (keyE not in extracted and keyE != key and CONFIG[keyE]['row'][0] >= CONFIG[key]['row'][1]):
                                            if abs(CURR_CONFIG[keyE]['row'][0] - CURR_CONFIG[key]['row'][1]) < minDistance:
                                                nearestKey = keyE
                                                minDistance = abs(CURR_CONFIG[keyE]['row'][0] - CURR_CONFIG[key]['row'][1])
                                    # print(nearestKey)

                                    upperKey = key
                                    minDistance = len(fullPdf)

                                    for keyE in CURR_CONFIG:
                                        if (keyE != key  and keyE != nearestKey and CONFIG[keyE]['row'][1] <= CONFIG[nearestKey]['row'][0]):
                                            if abs(CURR_CONFIG[keyE]['row'][1] - CURR_CONFIG[nearestKey]['row'][0]) < minDistance:
                                                upperKey = keyE
                                                minDistance = abs(CURR_CONFIG[keyE]['row'][1] - CURR_CONFIG[nearestKey]['row'][0])

                                    # Find distance to move down
                                    if (distance > 0):

                                        if (CURR_CONFIG[upperKey]['row'][1] < CURR_CONFIG[key]['row'][1] + distance):
                                            distance = CURR_CONFIG[key]['row'][1] + distance - CURR_CONFIG[upperKey]['row'][1]
                                        else:
                                            CURR_CONFIG[key]['row'][1] += distance
                                            break

                                    # Find distance to move up and move under block up
                                    elif (distance < 0):

                                        if (CURR_CONFIG[upperKey]['row'][1] > CURR_CONFIG[key]['row'][1] + distance):
                                            CURR_CONFIG[key]['row'][1] += distance
                                            distance = CURR_CONFIG[upperKey]['row'][1] - CONFIG[nearestKey]['row'][0]
                                            for keyE in CURR_CONFIG:
                                                if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[upperKey]['row'][1] and keyE != upperKey):

                                                    CURR_CONFIG[keyE]['row'] =  [i + distance for i in CURR_CONFIG[keyE]['row']]
                                            break

                                    else:
                                        break

                                    # Move current block
                                    for keyE in CURR_CONFIG:
                                        if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][1] and keyE != key):
                                            CURR_CONFIG[keyE]['row'] =  [i + distance for i in CURR_CONFIG[keyE]['row']]
                                    CURR_CONFIG[key]['row'][1] += distance

                                    break
                                else:
                                    startRow += 1
                                    if (startRow == len(fullPdf)):
                                        break

                        elif (margin == 'left'):
                            if (CURR_CONFIG[key]['column'][0] == None):
                                continue

                            # Get startRow to find left keyword
                            startRow = CURR_CONFIG[key]['row'][0]
                            leftFinding = CONFIG[key]['endObject'][margin]
                            # if (CONFIG[key]['endObject']['top'][:4] != 'same' and leftFinding.strip() != ""):
                            #     startRow -= 1

                            # Find first row that has key word
                            while (True):
                                if (re.search(leftFinding, fullPdf[startRow])):
                                    break;
                                else:
                                    startRow += 1
                                    if (startRow == len(fullPdf)):
                                        break
                            if (startRow == len(fullPdf)):
                                continue

                            # Get startCol to find left keyword
                            if (len(extracted) > 0):
                                startCol = 0

                                for keyE in extracted:
                                    if (CURR_CONFIG[keyE]['row'][0] > startRow):
                                        if (CURR_CONFIG[keyE]['column'][1] > startCol):
                                            startCol = CURR_CONFIG[keyE]['column'][1]

                            else:
                                startCol = 0

                            # print(key)
                            # Find left keyword and calculate distance
                            startCol = startCol + re.search(CONFIG[key]['endObject'][margin], fullPdf[startRow][startCol:]).span(0)[0]
                            distance = startCol + len(CONFIG[key]['endObject'][margin]) - CURR_CONFIG[key]['column'][0]

                            # Move other right block
                            for keyE in CURR_CONFIG:
                                if (keyE not in extracted and keyE != key and ((CURR_CONFIG[keyE]['row'][0] < CURR_CONFIG[key]['row'][1] and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][0])
                                                                            or (CURR_CONFIG[keyE]['row'][1] <= CURR_CONFIG[key]['row'][1] and CURR_CONFIG[keyE]['row'][1] > CURR_CONFIG[key]['row'][0]))):

                                    for i in range(len(CURR_CONFIG[keyE]['column'])):
                                        if (CURR_CONFIG[keyE]['column'][i] != None):
                                            CURR_CONFIG[keyE]['column'][i] += distance
                                        else:
                                            CURR_CONFIG[keyE]['column'][i] = None

                            # Move current block
                            for i in range(len(CURR_CONFIG[key]['column'])):
                                if (CURR_CONFIG[key]['column'][i] != None):
                                    CURR_CONFIG[key]['column'][i] += distance
                                else:
                                    CURR_CONFIG[key]['column'][i] = None

                        elif (margin == 'right'):
                            if (CURR_CONFIG[key]['column'][1] == None):
                                continue

                            # Get startRow to find right keyword
                            startRow = CURR_CONFIG[key]['row'][0]
                            rightFinding = CONFIG[key]['endObject'][margin]
                            if (CONFIG[key]['endObject']['top'][:4] != 'same' and rightFinding.strip() != ""):
                                startRow -= 1

                            # Find first row that has key word
                            while (True):
                                if (re.search(rightFinding, fullPdf[startRow])):
                                    break;
                                else:
                                    startRow += 1
                                    if (startRow == len(fullPdf)):
                                        break

                            if (startRow == len(fullPdf)):
                                continue

                            # Find right keyword and calculate distance
                            startCol = CURR_CONFIG[key]['column'][0] + re.search(CONFIG[key]['endObject'][margin], fullPdf[startRow][CURR_CONFIG[key]['column'][0]:]).span(0)[0]
                            distance = startCol - CURR_CONFIG[key]['column'][1]

                            # Move other right block
                            for keyE in CURR_CONFIG:
                                if (keyE not in extracted and keyE != key and ((CURR_CONFIG[keyE]['row'][0] < CURR_CONFIG[key]['row'][1] and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][0])
                                                                            or (CURR_CONFIG[keyE]['row'][1] <= CURR_CONFIG[key]['row'][1] and CURR_CONFIG[keyE]['row'][1] > CURR_CONFIG[key]['row'][0]))):
                                    for i in range(len(CURR_CONFIG[keyE]['column'])):
                                        if (CURR_CONFIG[keyE]['column'][i] != None):
                                            CURR_CONFIG[keyE]['column'][i] += distance
                                        else:
                                            CURR_CONFIG[keyE]['column'][i] = None

                            # Move current block
                            CURR_CONFIG[key]['column'][1] += distance

            # Get row and column
            row = CURR_CONFIG[key]['row']
            column = CURR_CONFIG[key]['column']

            print(key)
            print(row)
            print(column)
            # print(CURR_CONFIG)
            # Extract data and mark it as 'extracted'
            lines = fullPdf[row[0]:row[1]]
            extractedData[key] = '\n'.join([x[column[0]:column[1]].strip() for x in lines])
            extracted.append(key)

        # Process the subfields
        for key in CONFIG:
            if ('hasSubfield' in CONFIG[key]):
                if (CONFIG[key]['hasSubfield']):
                    for subs in CONFIG[key]['subfields']:
                        pos = 0
                        reg = CONFIG[key]['subfields'][subs]
                        if (reg != 10):
                            result = re.search(reg, extractedData[key]).span()
                            extractedData[key + '_' + subs] = extractedData[key][result[0]:result[1]]
                            pos = result[1]
                        else:
                            extractedData[key+'_'+subs] = extractedData[key][pos:]
                    del extractedData[key]

        # Print data extracted
        # for key in extractedData:
        #     print("------------------------------------")
        #     print("%s: %s" % (key, extractedData[key]))
        #     print("------------------------------------")

        # Save extracted result
        with open(PDF_TYPE + '/' + file[:-3] + 'txt', 'w', encoding='utf8') as resultFile:
            for key in extractedData:
                resultFile.write("------------------------------------\n")
                resultFile.write("%s:\n%s\n" % (key, extractedData[key]))
                resultFile.write("------------------------------------\n")
