#!/usr/bin/python3
import os
os.system('sudo apt-get update&&sudo apt-get install -y p7zip-full python3-pip python3-setuptools python3-pandas')
import sys
from multiprocessing import Process
import time
import requests
import re
import csv
import urllib.request 
import pandas as pd

try:
    pass_7z = sys.argv[1]
except IndexError:
    print("not all parameters")
    sys.exit(1)

def readListFromFile(pFileName):
    listLocal = []
    if os.path.exists(pFileName):
        fileTmp = open(pFileName,'a+')
        fileTmp.seek(0, 0)
        listLocal = fileTmp.readlines()
        fileTmp.close()
        return listLocal
    else:
        print("no links file")
        sys.exit(1)
def addRowCve(fileAddRow,searchLine,yearLine,pattrnLine,hashFile):
    outCSV = dict()
    outCSV['SEARCH'] = searchLine
    outCSV['YEARS'] = yearLine
    outCSV['PATTRN'] = pattrnLine
    outCSV['HASHfile'] = hashFile
    
    if not os.path.exists(fileAddRow):
        with open(fileAddRow,'w') as f:
            w = csv.DictWriter(f, outCSV.keys())
            w.writeheader()
    with open(fileAddRow, 'a+') as fileCSV:
        w = csv.DictWriter(fileCSV, outCSV.keys())
        w.writerow(outCSV)

def funcForFind(i,readFileResultBefore):
    pattern = re.compile(i.splitlines()[0].split("_:_")[1])
    fileListHash = []
    for r, d, f in os.walk('/tmp/work/'):
        for file in f:
            fileListHash.append(os.path.join(r, file))
    fileCSV = []
    for r, d, f in os.walk('/tmp/filesCSV/'):
        for file in f:
            if file.endswith('.csv'):
                fileCSV.append(os.path.join(r, file))

    for fileForSearchTMP in fileListHash:
        if fileForSearchTMP.split('/')[-1] in str(readFileResultBefore):
            continue
        with open('./skeep/'+i.splitlines()[0].split("_:_")[0]+'.skeep','a+') as ft:
            ft.write(fileForSearchTMP.split('/')[-1])
            ft.write('\n')
        if os.path.isfile(fileForSearchTMP):
            with open(fileForSearchTMP, encoding="utf8", errors='ignore') as fileReadContent:
                dataInFile = fileReadContent.read()
                matchTXT = re.findall(pattern, dataInFile)
                if len(matchTXT):
                    trimMatchTXT = (matchTXT[0][:33] + '..') if len(matchTXT[0]) > 33 else matchTXT[0]

                    fileYear = ' '
                    for fileIndexTmp in fileCSV:
                            df=pd.read_csv(fileIndexTmp)
                            df1 = df.loc[df['aaahashFile'] == fileForSearchTMP.split('/')[-1]]
                            if df1.empty == False:
                                fileYear += fileIndexTmp.split('_')[1].split('.csv')[0]
                                fileYear += ' '
                    addRowCve('./results/'+i.splitlines()[0].split("_:_")[0]+".csv",
                              trimMatchTXT ,
                              fileYear,
                              i.splitlines()[0].split("_:_")[1],
                              fileForSearchTMP)

allDataLinks = readListFromFile('./data/drb.links')
allSearchPattern = readListFromFile('./regexp/list1.FbyF')

if len(allSearchPattern) == 0 or len(allDataLinks) == 0:
    print("no data in pattern or links")
    sys.exist(1)
url7zFileForWork = ''
name7zFile = ''
if os.path.exists('./skeep/general.skeep'):
    fileTmp = open('./skeep/general.skeep','a+')
    fileTmp.seek(0, 0)
    listTmp = fileTmp.readlines()
    for i in allDataLinks:
        if not i.split("?")[0].split("/")[-1] in str(listTmp):
            fileTmp.write(i.split("?")[0].split("/")[-1])
            fileTmp.write('\n')
            url7zFileForWork = i
            name7zFile = url7zFileForWork.split("?")[0].split("/")[-1]
            break
    fileTmp.close()
    # retart general loop on archive files
    if name7zFile == '':
        with open('./skeep/general.skeep', 'w') as fileTmp:
            fileTmp.write(allDataLinks[0].split("?")[0].split("/")[-1])
            fileTmp.write('\n')
        url7zFileForWork = allDataLinks[0]
        name7zFile = url7zFileForWork.split("?")[0].split("/")[-1]
else:
    with open('./skeep/general.skeep', 'w') as fileTmp:
        fileTmp.write(allDataLinks[0].split("?")[0].split("/")[-1])
        fileTmp.write('\n')
    url7zFileForWork = allDataLinks[0]
    name7zFile = url7zFileForWork.split("?")[0].split("/")[-1]

urlTmp = urllib.request.urlopen(url7zFileForWork)
dataTmp = urlTmp.read()
urlTmp.close()
with open('/tmp/'+url7zFileForWork.split("?")[0].split("/")[-1], "wb") as fileTmp :
    fileTmp.write(dataTmp)
os.system('mkdir /tmp/work')
os.system('7z x /tmp/'+url7zFileForWork.split("?")[0].split("/")[-1]+' -p'+pass_7z+' -o/tmp/work/')
os.system('7z x ./data/filesCSV.7z -p'+pass_7z+' -o/tmp/')

procsAll = []
for i in allSearchPattern:
    fileTmp = open('./skeep/'+i.splitlines()[0].split("_:_")[0]+".skeep",'a+')
    fileTmp.seek(0, 0)
    readTmp = fileTmp.readlines()
    fileTmp.write(name7zFile)
    fileTmp.write('\n')
    fileTmp.close()
    
    procTmp = Process(target=funcForFind, args=(i,readTmp))
    procsAll.append(procTmp)
    procTmp.start()

for i in range(5):
    flagTmp = 0
    time.sleep(1*60*60)
    for procTmp in procsAll:
        procTmp.join(timeout=0)
        if procTmp.is_alive():
            flagTmp = 1
    if flagTmp == 0:
        print('end all process')
        sys.exit(0)
print('end works')
os._exit(0)
