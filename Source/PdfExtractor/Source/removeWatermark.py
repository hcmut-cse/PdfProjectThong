from __future__ import division
from bs4 import BeautifulSoup
import os
import re
import numpy as np
import pdftotext
import pandas as pd
import matplotlib.pyplot as plt
import json

def find_anomalies(df):
	random_data = df['fontsize']
	anomalies = []

	# Set upper and lower limit to 3 standard deviation
	random_data_std = np.std(random_data)
	random_data_mean = np.mean(random_data)
	anomaly_cut_off = random_data_std * 3

	lower_limit  = random_data_mean - anomaly_cut_off
	upper_limit = random_data_mean + anomaly_cut_off

	# Generate outliers
	for index, ele in enumerate(random_data):
		# if ele > upper_limit or ele < lower_limit:
		if ele > upper_limit:
			anomalies.append([ele, df['letter'].iloc[index]] )

	return pd.DataFrame(anomalies, columns = ['outlier-fontsize', 'outlier-letter'])

def findWatermark(fileName):
	os.system('pdf2txt.py -o output.html -t html \'' + fileName + '\'')
	with open('output.html', 'r') as htmlData:
		soup = BeautifulSoup(htmlData, features = "html.parser")

	os.system('rm output.html')
	font_spans = [ data for data in soup.select('span') if 'font-size' in str(data) ]
	output = []

    # Statistics
	character_2_fontsize = list()
	for i in font_spans:
		tup = ()
		fonts_size = re.search(r'(?is)(font-size:)(.*?)(px)',str(i.get('style'))).group(2)
		sequence = str(i.text).strip()

		for letter in sequence:
			if (letter != " "):
				tup2 = (letter,fonts_size.strip())
				character_2_fontsize.append(tup2)

	df_character = pd.DataFrame(character_2_fontsize, columns= ['letter', 'fontsize'])
	df_character.fontsize  = pd.to_numeric(df_character.fontsize)

	df_out = find_anomalies(df_character)
	weirdLength=len(df_out['outlier-fontsize'].unique())

	for i in font_spans:
		tup = ()
		fonts_size = re.search(r'(?is)(font-size:)(.*?)(px)',str(i.get('style'))).group(2)
		tup = (str(i.text).strip(),fonts_size.strip())
		output.append(tup)


    # Find watermarks
	maxSize = 0
	watermark = []
	for tag in output:
		size = int(tag[1])
		for i in range(weirdLength):
			if (size == df_out['outlier-fontsize'].unique()[i]):
				string = tag[0]
				string = string.replace(' \n','\n')
				wordList = string.split('\n')
				for word in wordList:
					watermark.append(word)

	return output, watermark, weirdLength, df_out

def removeWatermark(fileName, pdf):
	output, watermark, weirdLength, df_out = findWatermark(fileName)
    # print(watermark)

	trueOrder = {}
	update = {}
	for word in watermark:
		trueOrder.update({word:0})
		update.update({word:True})


	for tag in output:
		size = int(tag[1])
		for word in watermark:
			if (update[word] == True):
				c = tag[0].count(word)
				trueOrder[word] += c

			for i in range(weirdLength):
				if (size == df_out['outlier-fontsize'].unique()[i] and word in tag[0]):
					update[word] = False
					break

	for word in watermark:
		trueOrder[word]-=1
		# print(trueOrder[word])

	order={}
	pdfOut = []
	removed = {}
	for word in watermark:
		order.update({word:0})

	for i, line in enumerate(pdf):
		for word in watermark:
			if (word.strip() == ''):
				continue

			found = line.find(word)
			if (found != -1):
				tmp = 1
				if (trueOrder[word] > 0):
					trueOrd = trueOrder[word]
					tmp = line.count(word)
					if (order[word] <= trueOrd and order[word] + tmp - 1 >= trueOrd):
						s = line.split()
						if word in s:
							pos = s.index(word)
							# print(word)
							removed[word] = [i, line.index(word), line.index(word)+len(word)]
							# s[pos] = ' '*len(word)
						line = line.replace(word,' '*len(word), 1)
				else:
					if (word in removed):
						continue
					removed[word] = [i, line.index(word), line.index(word) + len(word)]
					line = line.replace(word,' '*len(word), 1)

				order[word] += tmp
		pdfOut.append(line)

	mergeLines = list(set([removed[x][0] for x in removed]))
	for lineNum in mergeLines:
		mergeWords = list(filter(lambda x: x[1][0] == lineNum, removed.items()))
		# print(mergeWords)
		newWord = ''
		pos = [lineNum, 1000, 0]
		for i, word in enumerate(mergeWords):
			del removed[word[0]]
			if (i < len(mergeWords) - 1):
				newWord += word[0] + ' '*(mergeWords[i+1][1][1] - mergeWords[i][1][2])
			else:
				newWord += word[0]
			if word[1][1] < pos[1]:
				pos[1] = word[1][1]
			if word[1][2] > pos[2]:
				pos[2] = word[1][2]
		# print(newWord)
		removed[newWord] = pos

	# print(removed)
	return pdfOut, removed
