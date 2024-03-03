import json

import openai
from openai import OpenAI
import mysql.connector
import time
from models import institution
from text.models.institution import Institution

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="InstExtraction"
)


# Set the API Key
def callModel(text:str) -> set:
  client = OpenAI(
    api_key='',  # this is also the default, it can be omitted
  )

  result = set()

  thread = client.beta.threads.create()

  message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content= text
  )

  run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id='asst_FQThHVuV6lXIUEPJEiOCDfhT',
    instructions=""
  )

  while (True):
    run = client.beta.threads.runs.retrieve(
      thread_id=thread.id,
      run_id=run.id
    )
    if run.status != 'completed':
      time.sleep(0.5)
      continue
    break

  messages = client.beta.threads.messages.list(
    thread_id=thread.id,
    limit=1
  )

  msg = messages.data[0]

  data = msg.content[0].text.value

  lines = data.split('\n')


  rawJson = '\n'.join(lines[1:-1])

  print(rawJson)

  try:
    # 尝试直接解析 JSON
    institutionInfo = json.loads(rawJson)
  except json.JSONDecodeError as e:
    # 如果解析失败，输出错误信息
    print(f"JSON decoding failed: {e}")
    revisedJson = "{\n"+rawJson+"\n}"
    print("revised Json:"+revisedJson)
    try:
      institutionInfo = json.loads(revisedJson)
    except json.JSONDecodeError:
      # 如果再次失败，输出错误并返回
      print("Json Format is still incorrect after attempts to fix!!!")
      return result

  names = [institution["name"] for institution in institutionInfo["extracted_institutions"]]
  institutions = []
  for ins in institutionInfo["extracted_institutions"]:
    if ins["name"] != 'null':
      inst = Institution(ins["name"],ins["city"],ins["country"])
      institutions.append(inst)


  client.beta.threads.delete(thread.id)

  for inst in institutions:
    result.add(inst)
  return result


def preprocess(text: str) -> str:
  text = text.replace("Univ.", "University")
  text = text.replace(",", "")
  text = text.replace("-\n", "")
  text = text.replace("\n", " ")
  text = text.replace("-", " ")
  text = text.replace("  ", " ")
  text = text.replace("  ", " ")
  print(text)
  return text

def getIdByName(name: str) -> list:
  res = []
  cursor = conn.cursor()
  sql = "SELECT * FROM RorData WHERE name = %s and status = 'active' and name not like '%fund%'"
  params = (name,)

  cursor.execute(sql, params)

  results = cursor.fetchall()
  for row in results:
    res.append(row[0])

  cursor.close()
  return res


def test_paper(file_path:str, jdugeFirst:bool) -> set:
  with open(file_path, 'r', encoding='utf-8') as file:
    file_contents = file.read()

  contents = file_contents.split("\u000C")

  if jdugeFirst:
    text = contents[0]
  else:
    text = contents[-2]
  text = preprocess(text)
  result = set()

  names = callModel(text)
  print("extracted names: ")
  print(names)
  for name in names:
    rorId = getIdByName(name)
    for id in rorId:
      result.add(id)



  return result

def getresult(path:str) -> set:
  testResult = test_paper(path, True)
  if not testResult:
    testResult = test_paper(path, False)
  return testResult

if __name__ == '__main__':
  file_path = 'papers/2201.00019v2.txt'
  res = getresult(file_path)
  print(res)
  conn.close()


