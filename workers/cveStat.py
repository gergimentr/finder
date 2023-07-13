import os

os.system('pip3 install pytesseract numpy matplotlib opencv-python pillow')
os.system('apt-get update&&apt-get install -y tesseract-ocr')

import requests
import pytesseract
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import re
import json
import sys
import time

if time.localtime().tm_hour != 16:
    sys.exit(0)
try:
#    pass_7z = sys.argv[1]
    bot_token = sys.argv[2]
    bot_chatID = sys.argv[3]
except IndexError:
    print("not all parameters")
    sys.exit(0)



def telegram_bot_sendtext(bot_message,bot_token,bot_chatID):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)

def sendImage(bot_image,bot_token,bot_chatID):
    url = "https://api.telegram.org/bot"+bot_token+"/sendPhoto";
    files = {'photo': open(bot_image, 'rb')}
    data = {'chat_id' : bot_chatID}
    r= requests.post(url, files=files, data=data)

gitCvelist = '/tmp/cvelist/'
if os.path.exists(gitCvelist):
    os.system('rm -rf '+gitCvelist)
os.system('git clone https://github.com/CVEProject/cvelist.git '+gitCvelist)
fileListHash = []
for r, d, f in os.walk(gitCvelist):
  for file in f:
    if file.endswith('.json'):
      fileListHash.append(os.path.join(r, file))

img_data = requests.get('https://www.first.org/epss/figures/top_cve_last_30_days-1.png').content
with open('image_name.jpg', 'wb') as handler:
    handler.write(img_data)
image = cv2.imread("image_name.jpg")
string = pytesseract.image_to_string(image)

telegram_bot_sendtext(str(time.localtime().tm_hour),bot_token,bot_chatID)
sendImage("image_name.jpg",bot_token,bot_chatID)

listCVE=[]
for i in re.split('\n| |CVE|CWE',string):
    if i.startswith('-') and len(re.findall('-',i))==2:
      listCVE.append('CVE'+i)
st = ''
for i in sorted(listCVE):
    st+=i+','

for i in fileListHash:
    if i.split('/')[-1].split('.json')[0] in listCVE:
      with open(i) as f:
        try:
            dictJsonTmp = json.load(f)
        except:
            print(i)
            continue
        if 'description' in dictJsonTmp and 'description_data' in dictJsonTmp['description'] and 'value' in dictJsonTmp['description']['description_data'][0]:
            telegram_bot_sendtext('https://nvd.nist.gov/vuln/detail/'+i.split('/')[-1].split('.json')[0],bot_token,bot_chatID)
            telegram_bot_sendtext(dictJsonTmp['description']['description_data'][0]['value'],bot_token,bot_chatID)
