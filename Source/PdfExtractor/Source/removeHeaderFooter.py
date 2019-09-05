from difflib import SequenceMatcher

def remove_at(s, i):
    return s[:i] + s[i+1:]

def removeHeaderAndFooter(pdf, HF_CONFIG):

    fullPdf = []
    for i in range(len(pdf)):
        if (pdf[i].strip() != ''):
            fullPdf.append(pdf[i].split('\n'))
    # if (len(fullPdf) == 1):
    #     return fullPdf
    # # Remove header
    # row = 0
    # continueRemove = True
    # while (True):
    #     for i in range(len(fullPdf) - 1):
    #         if SequenceMatcher(None, ''.join(fullPdf[0][row].split()), ''.join(fullPdf[i+1][row].split())).ratio() < 0.8:
    #             continueRemove = False
    #             break
    #     if (continueRemove):
    #         for i in range(len(fullPdf)):
    #             del(fullPdf[i][row])
    #     else:
    #         break
    #
    # # Remove footer
    # continueRemove = True
    # while (True):
    #     row = [len(page)-1 for page in fullPdf]
    #     for i in range(len(fullPdf) - 1):
    #         if SequenceMatcher(None, ''.join(fullPdf[0][row[0]].split()), ''.join(fullPdf[i+1][row[i+1]].split())).ratio() < 0.8:
    #             continueRemove = False
    #             break
    #     if (continueRemove):
    #         for i in range(len(fullPdf)):
    #             del(fullPdf[i][row[i]])
    #     else:
    #         break
    for part in HF_CONFIG:
        if HF_CONFIG[part]['pages'] == 'all':
            stopPage = len(pdf)
        elif HF_CONFIG[part]['pages'] == 'first':
            stopPage = 1

        for page in range(stopPage-1, -1, -1):
            if HF_CONFIG[part]['row'][0] < 0:
                startRowIndex = len(fullPdf[page]) + HF_CONFIG[part]['row'][0]
            else:
                startRowIndex = HF_CONFIG[part]['row'][0]
            if HF_CONFIG[part]['row'][1] == None:
                stopRowIndex = len(fullPdf[page])
            else:
                stopRowIndex = HF_CONFIG[part]['row'][1]

            for row in range(startRowIndex, stopRowIndex):
                if stopPage > 1:
                    if HF_CONFIG[part]['row'][0] < 0:
                        rowI = row - len(fullPdf[page]) + len(fullPdf[0])
                    else:
                        rowI = row

                    if SequenceMatcher(None, ''.join(fullPdf[0][rowI].split()), ''.join(fullPdf[page][row].split())).ratio() >= 0.8:
                        fullPdf[page][row] = ''
                    else:
                        if (part == "Header" and row < stopRowIndex) or (part == "Footer" and row > stopRowIndex):
                            HF_CONFIG[part]['row'][1] = row
                else:

                    startColIndex = HF_CONFIG[part]['column'][0]
                    if HF_CONFIG[part]['column'][1] == None:
                        stopColIndex = len(fullPdf[page][row])
                    else:
                        stopColIndex = HF_CONFIG[part]['column'][1]

                    fullPdf[page][row] = fullPdf[page][row][0:startColIndex] + fullPdf[page][row][stopColIndex:len(fullPdf[page][row])]

    return fullPdf
