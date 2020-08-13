from app import app
import json
import unittest
from unittest.mock import patch
import psycopg2
import dbcreate
import sys

DBNAME="dafog8344gujsl"
USER="lxhraicyyfwqpo"
PASSWORD="29c8c3c13d1e35e9a426cc6244e907c7b8245b190b336d6fc2d96504057e54c6"
HOST="ec2-54-217-204-34.eu-west-1.compute.amazonaws.com"

# teszt adatbazis letrehozasa
dbcreate.create_db(DBNAME, USER, PASSWORD, HOST)


# csatlakozas teszt adatbazishoz
def mock_connect_db():
  return psycopg2.connect(
    dbname=DBNAME,
    user=USER,
    password=PASSWORD,
    host=HOST
    )
    

class FlaskTestCase(unittest.TestCase):  
      
  # van felszereles, alkalmazott hozzaadhato e. felszereles elfogyott, nem adhato hozza
  @patch('app.connect_db')
  def test_equipmentAvailable(self, mock):

    mock.side_effect = mock_connect_db
    
    dbcreate.create_db(DBNAME, USER, PASSWORD, HOST)
    
    tester=app.test_client(self)
    
    # add location
    resp = tester.post('/api/location/', json={
      'name': 'Meki', 'address': '6345 Nagykata'
    })
    self.assertEqual(resp.status_code, 200)
    
    json_data = resp.get_json()
    locationId = json_data['Id']
    
    # add equipment
    resp_equipment = tester.post('/api/equipment/', json={ "name": "suto1", "type": "oven", "locatedat": locationId})
    self.assertEqual(resp_equipment.status_code, 200)
    equipment_json_data = resp_equipment.get_json()
    equimentId=equipment_json_data['Id']
    
    # add employee
    string = f'{{ "name": "Nagy Bela", "job": "cook", "worksat": {locationId}, "operates": {equimentId}, "salary": 300}}'
    empResponse = tester.post('/api/employee/', json=json.loads(string))
    # add employee
    empResponse2 = tester.post('/api/employee/', json=json.loads(string))
    # response error
    self.assertEqual(empResponse2.status_code, 400)
  
  
  # nem sajat hejen levo ezkoz hasznalata
  @patch('app.connect_db')
  def test_equipmentWrongPlace(self, mock):

    mock.side_effect = mock_connect_db
    
    dbcreate.create_db(DBNAME, USER, PASSWORD, HOST)
    
    tester=app.test_client(self)
    
    # add location
    loc1resp = tester.post('/api/location/', json={
      'name': 'Meki', 'address': '4567 Nagykata'
    })
    json_data = loc1resp.get_json()
    locationId1 = json_data['Id']
    
    loc2resp = tester.post('/api/location/', json={
      'name': 'KFC', 'address': '1234 nagy utca'
    })
    json_data = loc2resp.get_json()
    locationId2 = json_data['Id']
    
    # add equipment
    resp_equipment = tester.post('/api/equipment/', json={ "name": "suto1", "type": "oven", "locatedat": locationId1})
    self.assertEqual(resp_equipment.status_code, 200)
    equipment_json_data = resp_equipment.get_json()
    equimentId=equipment_json_data['Id']
    
    # add employee
    string = f'{{ "name": "Nagy Bela", "job": "cook", "worksat": {locationId2}, "operates": {equimentId}, "salary": 300}}'
    empResponse = tester.post('/api/employee/', json=json.loads(string))
  
    self.assertEqual(empResponse.status_code, 400)
  
  
  # kevesebbet keres 300-nal
  @patch('app.connect_db')
  def test_tooSmallSalary(self, mock):

    mock.side_effect = mock_connect_db
    tester=app.test_client(self)
    
    dbcreate.create_db(DBNAME, USER, PASSWORD, HOST)
    
    # add location
    loc1resp = tester.post('/api/location/', json={
      'name': 'Meki', 'address': '4321 Nagykata'
    })
    json_data = loc1resp.get_json()
    locationId1 = json_data['Id']
    
    # add equipment
    resp_equipment = tester.post('/api/equipment/', json={ "name": "suto1", "type": "oven", "locatedat": locationId1})
    self.assertEqual(resp_equipment.status_code, 200)
    equipment_json_data = resp_equipment.get_json()
    equimentId=equipment_json_data['Id']
    
    # add employee
    string = f'{{ "name": "Nagy Bela", "job": "cook", "worksat": {locationId1}, "operates": {equimentId}, "salary": 200}}'
    empResponse = tester.post('/api/employee/', json=json.loads(string))
  
    self.assertEqual(empResponse.status_code, 400)
    
  # manager kevesebbet keres az alkalmazottaknal
  @patch('app.connect_db')
  def test_managerEarnsLessThanEmployees(self, mock):

    mock.side_effect = mock_connect_db
    tester=app.test_client(self)
    
    dbcreate.create_db(DBNAME, USER, PASSWORD, HOST)
    
    # add location
    loc1resp = tester.post('/api/location/', json={
      'name': 'Meki', 'address': '4321 Nagykata'
    })
    json_data = loc1resp.get_json()
    locationId1 = json_data['Id']
    
    # add equipment
    resp_equipment = tester.post('/api/equipment/', json={ "name": "suto1", "type": "oven", "locatedat": locationId1})
    self.assertEqual(resp_equipment.status_code, 200)
    equipment_json_data = resp_equipment.get_json()
    equimentId=equipment_json_data['Id']
    
    # add employee
    string = f'{{ "name": "Nagy Bela", "job": "cook", "worksat": {locationId1}, "operates": {equimentId}, "salary": 400}}'
    empResponse = tester.post('/api/employee/', json=json.loads(string))
    
    string = f'{{ "name": "Nagy Mark", "job": "manager", "worksat": {locationId1}, "operates": "", "salary": 350}}'
    managerResponse = tester.post('/api/employee/', json=json.loads(string))
  
    self.assertEqual(managerResponse.status_code, 400)
  
  # atlagfizestol tobb mint 20%-kal elter
  @patch('app.connect_db')
  def test_salaryFarFromAverage(self, mock):

    mock.side_effect = mock_connect_db
    tester=app.test_client(self)
    
    dbcreate.create_db(DBNAME, USER, PASSWORD, HOST)
    
    # add location
    loc1resp = tester.post('/api/location/', json={
      'name': 'Meki', 'address': '4321 Nagykata'
    })
    json_data = loc1resp.get_json()
    locationId1 = json_data['Id']
    
    # add equipment
    resp_equipment = tester.post('/api/equipment/', json={ "name": "suto1", "type": "oven", "locatedat": locationId1})
    equipment_json_data = resp_equipment.get_json()
    equimentId=equipment_json_data['Id']
    
    resp_equipment = tester.post('/api/equipment/', json={ "name": "suto1", "type": "oven", "locatedat": locationId1})
    equipment_json_data = resp_equipment.get_json()
    equimentId2=equipment_json_data['Id']
    
    # add employee
    string = f'{{ "name": "Nagy Bela", "job": "cook", "worksat": {locationId1}, "operates": {equimentId}, "salary": 400}}'
    tester.post('/api/employee/', json=json.loads(string))
    
    string = f'{{ "name": "Nagy Mark", "job": "cook", "worksat": {locationId1}, "operates": {equimentId2}, "salary": 700}}'
    employeeResponse = tester.post('/api/employee/', json=json.loads(string))
  
    self.assertEqual(employeeResponse.status_code, 400)

    
if __name__ == '__main__':
  unittest.main()