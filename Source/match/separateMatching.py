import glob
from match.utils import *

def findTemplateSeparateVersion(path,file,jsonDir):
	jsonFiles=glob.glob(jsonDir)
	minDistance=100000
	starPos=jsonDir.find('*')
	for jsonFile in jsonFiles:
		CONFIG,HF_CONFIG=initCONFIG(jsonFile) # HF_CONFIG for fun
		lineList=preProcessPdf(file)
		lineList=fixScript(lineList)
		for key in CONFIG: key=fixSpaceColonString(key)
		configString=createStringList(CONFIG)
		sList,aliasDict=createListOfStringLineList(CONFIG,lineList,configString)
		# New keys
		newKwList=generateListNewKws(file,jsonFile[starPos:-5],CURR_KW,jsonDir)
		for key in newKwList:
			for tmpKey in aliasDict:
				found=0
				for element in aliasDict[tmpKey]:
					if element.find(key)!=-1: 
						newKwList.remove(key)
						found=1
						break
				if (found): break
		for s in sList:
			dis=getDamerauDistance(configString,s,aliasDict)
			dis+=len(newKwList)*0.5

			# Testing===========================================================================
			# print('=========================================================================')
			# print('Standard string:',configString)
			# print('Target S:',s)
			# print('Distance:',dis)
			# print('Template:',jsonFile[starPos:-5])
			# print('=========================================================================')
			# Testing==========================================================================
			if (minDistance>dis): 
				minDistance=dis
				ans=jsonFile[starPos:-5]
				targetConfigString=configString
				targetS=s
				targetCONFIG=CONFIG
				targetAliasDict=aliasDict
				targetNewKwList=newKwList

				# Testing===========================================================================
				print('=========================================================================')
				print('Standard string:',configString)
				print('Target S:',s)
				print('Distance:',minDistance)
				print('Template:',jsonFile[starPos:-5])
				print('New keywords:',newKwList)
				print('=========================================================================')
				if (minDistance==0 or minDistance>15): break
				# Testing==========================================================================
		if (minDistance==0): break

	# print(file)
	if (minDistance>8): return -1
	
	return ans

# def main():
# 	path='matching/random'
# 	jsonDir='template/*json'
# 	pdfFiles=glob.glob('matching/random/*pdf')
# 	for file in pdfFiles:
# 		print(file[16:],findTemplateSeparateVersion(path,file,jsonDir))

# if __name__=='__main__': main()