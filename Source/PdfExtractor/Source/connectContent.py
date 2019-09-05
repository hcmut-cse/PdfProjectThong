import numpy as np
import re
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
def longestSubstringFinder(string1, string2):
    answer = ""
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = ""
        for j in range(len2):
            if (i + j < len1 and string1[i + j] == string2[j]):
                match += string2[j]
            else:
                if (len(match) > len(answer)): answer = match
                match = ""
    return answer
def connectContent(length, extractedData):
    cString = []
    if (length >= 2):
        for key1 in list(extractedData):
            if ("2" in key1):
                break
            for key2 in list(extractedData):
                if (". . . . . . ." not in key2):
                    if (len(key1) > 4):
                        ratio = similar(key1, key2)
                        if (ratio > 0.9 and ratio < 1):
                            commonString = longestSubstringFinder(key1, key2)
                            cString.append(commonString)
                            content = extractedData[key1] + "\n" + extractedData[key2]
                            extractedData[commonString] = content
                            del extractedData[key1]
                            del extractedData[key2]
                            break
                    if (len(key1) == 4):
                        ratio = similar(key1, key2)
                        if (ratio > 0.7 and ratio < 0.8):
                            commonString = longestSubstringFinder(key1, key2)
                            cString.append(commonString)
                            content = extractedData[key1] + "\n" + extractedData[key2]
                            extractedData[commonString] = content
                            if (len(commonString) >= 2):
                                del extractedData[key1]
                                del extractedData[key2]
                                break
        if (length > 2):
            count = 0
            for common in cString:
                for key in list(extractedData):
                    if (len(key) > 4):
                        ratio = similar(common, key)
                        if (ratio > 0.9 and ratio < 1):
                            content = extractedData[common] + "\n" + extractedData[key]
                            extractedData[common] = content
                            del extractedData[key]
                    elif (len(key) == 4):
                        ratio = similar(common, key)
                        if (ratio > 0.8 and ratio < 0.9):
                            content = extractedData[common] + "\n" + extractedData[key]
                            extractedData[common] = content
                            del extractedData[key]
    return extractedData