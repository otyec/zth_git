from flask import Flask, request, g, Response, make_response, jsonify
from flask.cli import with_appcontext

import psycopg2
from psycopg2 import sql

from http import HTTPStatus
import copy, math
import dbcreate
from threading import Thread
import socket
from _thread import *
import threading
import time
import re


app = Flask(__name__)

DBNAME="d2vlsnbelmcc11"
USER="awvaabzaiazhmk"
PASSWORD="6354df7bd023ad2b6ff1b7156b368a185785cc65abb0e2768b687eb30ed19e00"
HOST="ec2-54-217-213-79.eu-west-1.compute.amazonaws.com"

# dbcreate.create_db(DBNAME, USER, PASSWORD, HOST)

lock = threading.Lock()

def fozes(c): 
  while True: 
  
    # data received from client 
    data = c.recv(1024) 
    
    if not data: 
      print_lock.release() 
      break
      
    time.sleep(5.0)
    c.send(data) 

  c.close()

class Szakacs(Thread):
  def __init__(self):
    Thread.__init__(self)
    self.daemon = True
    self.start()
  def run(self):
    host = "127.0.0.1" 
    port = 3223
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((host, port))  
    s.listen(5) 

    while True: 

      c, addr = s.accept() 

      lock.acquire() 

      start_new_thread(fozes, (c,))
    s.close() 

# szakacs thread es socket inditasa
Szakacs()


def connect_db():
  return psycopg2.connect(
    dbname=DBNAME,
    user=USER,
    password=PASSWORD,
    host=HOST
    )

@app.before_request
def before_request():
  g.db = connect_db()

@app.teardown_request
def after_request(response):
  if g.db is not None:
    g.db.close()
  return response


@app.route('/', methods=['GET'])
def hello_world():
  return 'Hello World!'

  
# rendeles socketen
@app.route('/api/rendeles', methods=['GET'])
def Rendeles():
  try:
    rendeles = request.args.get('rendeles')
  except:
    return HTTPStatus(400).description

  s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
  host = "127.0.0.1" 
  port = 3223
  s.connect((host,port)) 

  s.send(rendeles.encode('ascii')) 

  data = s.recv(1024) 
 
  s.close()
  return Response(str(data.decode('ascii')), status=200, mimetype='http/text')
 
    
@app.route('/http-status/getStatusDescription', methods=['GET'])
def StatusDescription():

  try:
    statusCode = int(request.args.get('statusCode'))
  except:
    return HTTPStatus(400).description
    
  try:
    response = HTTPStatus(statusCode).description
  except:
    response = HTTPStatus(400).description
    
  return response
  
class point:
  def __init__(self, x, y):
    self.x=x
    self.y=y
  def __eq__(self, other):
    return (self.x==other.x and self.y==other.y)
  
@app.route('/squares/getNumberOfSquares', methods=['GET'])
def NumberOfSquares():
  
  request_data = request.json
  
  #lista pont elemekkel a dictionarik helyett
  point_list=[]
  for i in request_data:
  
    p = point(x=i["x"], y=i["y"])
    
    #csak kulonbozo pontok kerulnek be
    if p not in point_list: 
      point_list.append(p)
      
  #negyzetek szama
  count=0
  
  while len(point_list)>=4:
  
    cur=point_list.pop(0)
    
    point_list_2 = copy.deepcopy(point_list)
    
    while len(point_list_2)>=3:
      cur2=point_list_2.pop(0)
      
      iranyvektor = point(x=cur.x-cur2.x, y=cur.y-cur2.y)
      normalvektor = point(x=iranyvektor.y, y=-iranyvektor.x)
      
      if point(x=cur.x+normalvektor.x, y=cur.y+normalvektor.y) in point_list_2 and point(x=cur2.x+normalvektor.x, y=cur2.y+normalvektor.y) in point_list_2:
        count=count+1
      if point(x=cur.x-normalvektor.x, y=cur.y-normalvektor.y) in point_list_2 and point(x=cur2.x-normalvektor.x, y=cur2.y-normalvektor.y) in point_list_2:
        count=count+1
      print(count)
  return Response(str(count), status=200, mimetype='http/text')

  
@app.route('/api/location/', methods=['POST'])
def location():

  if request.mimetype != "application/json":
    return Response("", status=400, mimetype='http/text')
    
  req_data = request.get_json()
  try:
    name = req_data['name']
    address = req_data['address']
  except:
    return Response("", status=400, mimetype='http/text')
  
  #eleje negy szam, max 2 szo
  if not bool(re.match("^[0-9]{4}\s*\w*\s*\w*", address)):
    return Response("", status=400, mimetype='http/text')
    
  cursor = g.db.cursor()
  cursor.execute("INSERT INTO Location (Name, Address) VALUES (%s, %s)",(name, address))
  

  query=sql.SQL("SELECT Id FROM Location WHERE Name = %s")
  cursor.execute(query, [name])
  id=cursor.fetchone()[0]
  
  
  g.db.commit()
  cursor.close()
  return jsonify(Id = id)
  
@app.route('/api/equipment/', methods=['POST'])
def equipment():
  if request.mimetype != "application/json":
    return Response("", status=400, mimetype='application/json')
    
  req_data = request.get_json()
  
  try:
    name = req_data['name']
    type  = req_data['type']
    locatedat = req_data['locatedat']
  except:
    return Response("", status=400, mimetype='http/text')
  
  cursor = g.db.cursor()
  cursor.execute("INSERT INTO Equipment (Name, Type, LocatedAt) VALUES (%s, %s, %s)",(name, type, locatedat))
  
  query=sql.SQL("SELECT Id FROM Equipment WHERE Name = %s")
  cursor.execute(query, [name])
  id=cursor.fetchone()[0]
  
  g.db.commit()
  cursor.close()

  return jsonify(Id=id)

@app.route('/api/employee/', methods=['POST'])
def employee():
  if request.mimetype != "application/json":
    return Response("", status=400, mimetype='application/json')
    
  req_data = request.get_json()
  
  try:
    name = req_data['name']
    job  = req_data['job']
    worksat = req_data['worksat']
    operates = req_data['operates']
    salary = req_data['salary']
  except:
    return Response("", status=400, mimetype='http/text')
    
  # dolgozó neve 2/3 szóból áll
  if not bool(re.match("\w+\s+\w+\s*\w*", name)):
    return Response("", status=400, mimetype='http/text')
  
  cursor = g.db.cursor()

  # ott van e a gep ahol az alkalmazott
  if job != "manager":
    query = sql.SQL("SELECT LocatedAt FROM Equipment WHERE Id = %s")
    cursor.execute(query, (str(operates)))
    equipmentLoc = cursor.fetchone()
    if equipmentLoc == None:
      return Response("", status=400, mimetype='application/json')
      print("gep mashol van")
    elif worksat != equipmentLoc[0]:
      print("gep mashol van")
      return Response("", status=400, mimetype='application/json')
    
  # van e mar manager
  if job == "manager":
    query = sql.SQL("SELECT COUNT (Id) FROM Employee WHERE Job = 'manager' AND WorksAt = %s")
    cursor.execute(query, (str(worksat)))
    count = cursor.fetchone()[0]
    
    if count != 0:
      print("van manager")
      return Response("", status=400, mimetype='application/json')
    
  # van e szabad suto
  if job == "cook":
    query = sql.SQL("SELECT COUNT (Id) FROM Equipment WHERE Type = 'oven' AND LocatedAt = %s")
    cursor.execute(query, [str(worksat)])
    oven_count = cursor.fetchone()[0]
    query =  sql.SQL("SELECT COUNT (Id) FROM Employee WHERE Job = 'cook' AND WorksAt = %s")
    cursor.execute(query, [str(worksat)])
    cook_count = cursor.fetchone()[0]
    if oven_count <= cook_count:
      print("nincs szabad suto")
      return Response("", status=400, mimetype='application/json')
  
  # van e szabad kassza
  if job == "cashier":
    query = sql.SQL("SELECT COUNT (Id) FROM Equipment WHERE Type = 'cash register' AND LocatedAt = %s")
    cursor.execute(query, (str(worksat)))
    register_count = cursor.fetchone()[0]
    
    query =  sql.SQL("SELECT COUNT (Id) FROM Employee WHERE Job = 'cashier' AND WorksAt = %s")
    cursor.execute(query, (str(worksat)))
    cashier_count = cursor.fetchone()[0]
    
    if register_count <= cashier_count:
      print("nincs szabad kassza")
      return Response("", status=400, mimetype='application/json')
  
  # szakacs sutot, kasszas kasszat hasznal e
  if job != "manager":
    query=sql.SQL("SELECT Type FROM Equipment WHERE id = %s")
    cursor.execute(query, (str(operates)))
    equipment_type=cursor.fetchone()[0]
    
    if(job == "cashier" and equipment_type != "cash register"):
      print("nem jo gepet hasznal")
      return Response("", status=400, mimetype='application/json')
      
    if(job == "cook" and equipment_type != "oven"):
      print("nem jo gepet hasznal")
      return Response("", status=400, mimetype='application/json')
      
  # ne keressenek 300-nal kevesebbet
  if salary < 300:
    print("300-nal kisebb kereset")
    return Response("", status=400, mimetype='application/json')
    
  # manager fizetese nem lehet kisebb masenal
  if job == "manager":
    query=sql.SQL("SELECT MAX(salary) FROM Employee WHERE WorksAt = %s")
    cursor.execute(query, (str(worksat)))
    maxSalary=cursor.fetchone()[0]
    
    if salary <= maxSalary:
      print("manager fizetese nem lehet kevesebb az alkalmazottaketol")
      return Response("", status=400, mimetype='application/json')
    
  # alkalmazott keresete nem terhet el az adott munkakor atlagkeresetetol tobb mint 20 szazalekkal
  if job != "manager":
    query=sql.SQL("SELECT AVG(salary) FROM Employee WHERE Job = %s")
    cursor.execute(query, [job])
    averageSalary=cursor.fetchone()[0]
    if averageSalary != None:
      difference = averageSalary/salary
      if difference < 0.8 or difference > 1.2:
        print("atlagkeresettol tulsagosan elter")
        return Response("", status=400, mimetype='application/json')
      
      
    
  
  print("added to database")
  cursor.execute("INSERT INTO Employee (Name, Job, WorksAt, Operates, salary) VALUES (%s, %s, %s, %s, %s)",(name, job, worksat, operates, salary))
  g.db.commit()
  
  cursor.close()

  return Response("", status=201, mimetype='application/json')
  
@app.route('/api/location/<id>', methods=['PUT', 'DELETE'])
def location_id(id):
    
  cursor = g.db.cursor()
    
  req_data = request.get_json()
  
  if request.method == "PUT":
  
    if request.mimetype != "application/json":
      return Response("", status=400, mimetype='application/json')
    try:
      name = req_data['name']
      address = req_data['address']
    except:
      return Response("", status=400, mimetype='http/text')
    
    if not bool(re.match("^[0-9]{4}\s*\w*\s*\w*", address)):
      return Response("", status=400, mimetype='http/text')
    
    cursor.execute("UPDATE Location SET Name = %s, Address = %s WHERE Id = %s", [name, address, id])
    
    g.db.commit()
    
    return "put"
  
  if request.method == "DELETE":
    query = sql.SQL("DELETE FROM Location WHERE Id = %s")
    cursor.execute(query, (str(id)))
    g.db.commit()
    return "delete"
    
  cursor.close()
  
@app.route('/api/equipment/<id>', methods=['PUT', 'DELETE'])
def equipment_id(id):

    
  cursor = g.db.cursor()  
  
  req_data = request.get_json()
  
  if request.method == "PUT":
  
    if request.mimetype != "application/json":
      return Response("", status=400, mimetype='application/json')
    
    try:
      name = req_data['name']
      type  = req_data['type']
      locatedat = req_data['locatedat']
    except:
      return Response("", status=400, mimetype='http/text')
    
    cursor.execute("UPDATE Equipment SET Name = %s, Type = %s, LocatedAt = %s WHERE Id = %s", [name, type, locatedat, id])
    
    g.db.commit()
    
    return "put"
  
  if request.method == "DELETE":
    query = sql.SQL("DELETE FROM Equipment WHERE Id = %s")
    cursor.execute(query, (str(id)))
    g.db.commit()
    return "delete"

  cursor.close()  

@app.route('/api/employee/<id>', methods=['PUT', 'DELETE'])
def employee_id(id):
  
  cursor = g.db.cursor()
  
  req_data = request.get_json()
  
  if request.method == "PUT":
  
    if request.mimetype != "application/json":
      return Response("", status=400, mimetype='application/json')
     
    try:
      name = req_data['name']
      job  = req_data['job']
      worksat = req_data['worksat']
      operates = req_data['operates']
    except:
      return Response("", status=400, mimetype='http/text')
    
    if not bool(re.match("\w+\s+\w+\s*\w*", name)):
      return Response("", status=400, mimetype='http/text')
    
    cursor.execute("UPDATE Employee SET Name = %s Job = %s WorksAt = %s Operates = %s WHERE Id = %s", [name, job, worksat, operates, id])
    
    g.db.commit()
    
    return "put"
  
  if request.method == "DELETE":
    query = sql.SQL("DELETE FROM Employee WHERE Id = %s")
    cursor.execute(query, (str(id)))
    g.db.commit()
    return "delete"
  
  cursor.close()

  
def NumberOfSteps(stairsRemaining, stepSizeList, actualSteps = {}): # int, ascending int[], int{int}
  
  stairsRem = copy.deepcopy(stairsRemaining)
  stepSizeL = copy.deepcopy(stepSizeList)
  actSteps = copy.deepcopy(actualSteps)
  
  collectedResults = []
  if len(stepSizeL)>0:
  
    curStepSize =  stepSizeL.pop()
  
    collectedResults.extend(NumberOfSteps(stairsRem, stepSizeL, actSteps))
    numCurSteps = 1
  
    while stairsRem - curStepSize >= 0:
    
      actSteps[curStepSize] = numCurSteps
      stairsRem = stairsRem - curStepSize
    
      if stairsRem == 0:
        collectedResults.append(actSteps)
      else:
        recur = (NumberOfSteps(stairsRem, stepSizeL, actSteps))
        if len(recur)>0:
          collectedResults.extend(recur)
    
      numCurSteps = numCurSteps + 1
  return collectedResults
  

@app.route('/number-of-steps/getNumberOfSteps', methods= ['GET'])
def getNumberOfSteps():

  numberOfStair = int(request.args.get('numberOfStair'))
  stepSizeList = list(map(int, request.args.get('stepSizeList').split(",")))
  stepSizeList.sort()
  
  # dictionary lista, mekkorabol mennyit lep
  stepPossibilities = NumberOfSteps(numberOfStair, stepSizeList)
  
  # lepesek ismetleses permutacioja osszesitve
  stepVariations=0
  for p in stepPossibilities:
    n = 0
    for j in p.values():
      n = n+j
    n = math.factorial(n)
    for stepCount in p.values():
      n = n/math.factorial(stepCount)
      
    stepVariations = stepVariations + n
   
  return Response(str(stepVariations), status=200, mimetype='http/text')
   
  
if __name__ == '__main__':
  app.run()


