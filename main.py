import os
import time
import smtplib
import requests

from bs4 import BeautifulSoup


DOMAIN  = os.environ['MAIL_DOMAIN'] 
KEY     = os.environ['MAIL_KEY'] 
MY_MAIL = os.environ['MY_MAIL'] 

PORT   = 587

REFRESH_TIME = 15 # [s]


def getTelexLegfrissebb():
  r = requests.get('https://telex.hu/legfrissebb')

  data = r.text
  parsed_html = BeautifulSoup(data)

  data = []

  for sclass in parsed_html.body.findAll('div', attrs={'class':'list__item__info'}):
    cim = sclass.find('a', attrs={'class': "list__item__title"})
    item = {}
    item['cim'] = cim.text.strip()
    item['link'] = "telex.hu"+cim["href"]
    item['rovat'] = item['link'].split('/')[1]
    data.append(item)

  return data


def isDifferent(olds, news):
  if olds[0]['cim'] != news[0]['cim']:
    return True
  return False

def getDiffCount(olds, news):
  count = news.index(olds[0])
  return count

def sendMail(hir,link):
  smtpObj = smtplib.SMTP(SERVER, PORT)
  smtpObj.ehlo()

  smtpObj.starttls()
  smtpObj.ehlo()

  smtpObj.login(DOMAIN, KEY)

  # Send an email
  from_address = DOMAIN
  to_address = MY_MAIL
  message = """\
  Subject: [Telex] [{}]

  {}
  """.format(hir, link)
  message = message.encode()

  smtpObj.sendmail(from_address, to_address, message)

  # Quit the SMTP session
  smtpObj.quit()

def saveErrorLog(data):
  with open("errorLog.txt", "w") as f:
    f.write(data)


breakFlag = False
newData   = getTelexLegfrissebb()

while not breakFlag:
  try:
    time.sleep(REFRESH_TIME)
    oldData = newData
    newData = getTelexLegfrissebb()
    if isDifferent(oldData, newData):
      print(time.ctime(time.time()))
      for i in range(getDiffCount(oldData, newData)):
        sendMail(newData[i]['cim'], newData[i]['link'])

  except KeyboardInterrupt:
    print('KeyboardInterruption')
    saveErrorLog('KeyboardInterruption')
    breakFlag = True
  except Exception as error:
    print(error)
    saveErrorLog(str(error))
    breakFlag = True

  if breakFlag:
    print('Progress ending')

if __name__ == "__main__":
    app.run()
