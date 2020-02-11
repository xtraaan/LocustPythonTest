from locust import HttpLocust, TaskSet, task, TaskSequence, seq_task, events, stats
from pyquery import PyQuery
from random import *
import locust.events
import logging
import json
import re
import random
import string
import time

#logging.basicConfig(filename='test.log', level=logging.INFO)


#Start editing the file here:
class UserLoad(TaskSequence):

     @seq_task(1)
     def Index(self):
		response = self.client.get("/#!/login")

     @seq_task(2)
     def login(self):
		payload = "grant_type=password&username=s82&password=ZeroDeaths!"
		headers = {'Content-Type': "application/x-www-form-urlencoded"}
		response = self.client.post("/RoadwayAnalysisService/token",  data=payload, headers=headers)
		data = json.loads(response.content)
		self.token = data['access_token']
		
     @seq_task(3)
     def getProjects(self):
		querystring = {"userName":"s82"}
		headers = {'Authorization': "Bearer " + self.token}
		response = self.client.get("/RoadwayAnalysisService/api/Project/GetProjects", headers=headers, params=querystring)
		jsonobj = json.loads(response.content)
		Project = sample(jsonobj, 1)
		self.ProjectCode = Project[0]['projectID']
		
     @seq_task(4)
     def getProject(self):
		headers = {'Authorization': "Bearer " + self.token}
		response = self.client.get("/RoadwayAnalysisService/api/Project/GetProject/" + str(self.ProjectCode), headers=headers)
		self.projectdata = json.loads(response.content)
		randomentry = sample(self.projectdata, 1)
		
	 @seq_task(5)
     def getQuery(self):
		headers = {'Authorization': "Bearer " + self.token}
		project = self.client.get("/RoadwayAnalysisService/api/Project/GetProject/" + str(self.ProjectCode), headers=headers)
		jsonproject = json.loads(project.content)
		for crash in jsonproject
			collisions = self.client.get("/RoadwayAnalysisService/api/Warehouse/GetMannerCollisions"), headers=headers)
			jsoncollisions = json.loads(collisions.content)
			randomcollision = sample(jsoncollisions, 1)
			crash.mannerCollisionCode = randomCollision
			
			factors = self.client.get("/RoadwayAnalysisService/api/Warehouse/GetPrimaryContributingFactors"), headers=headers)
			jsonfactors = json.loads(factors.content)
			randomfactor = sample(jsonfactors, 1)
			crash.contributingFactorPrimaryCode = randomfactor
			
			surfaces = self.client.get("/RoadwayAnalysisService/api/Warehouse/GetSurfaceTypes"), headers=headers)
			jsonsurfaces = json.loads(surfaces.content)
			randomsurface = sample(jsonsurfaces, 1)
			crash.surfaceTypeCode = randomsurface
			
			crash.reviewed = true
			crash.intersection = bool(random.getrandbits(1))
			
			self.client.post("/RoadwayAnalysisService/api/Project/UpdateCrash",  data=crash, headers=headers)
			


class UserCreate(TaskSequence):

	canceled = False

	@seq_task(1)
	def Index(self):
		self.canceled = False
		response = self.client.get("/#!/login")

	@seq_task(2)
	def login(self):
		payload = "grant_type=password&username=s82&password=ZeroDeaths!"
		headers = {'Content-Type': "application/x-www-form-urlencoded"}
		response = self.client.post("/RoadwayAnalysisService/token",  data=payload, headers=headers)
		data = json.loads(response.content)
		self.token = data['access_token']
		
	@seq_task(3)
	def getProjects(self):
		querystring = {"userName":"s82"}
		headers = {'Authorization': "Bearer " + self.token}
		response = self.client.get("/RoadwayAnalysisService/api/Project/GetProjects", headers=headers, params=querystring)
		
	@seq_task(4)
	def InsertProject(self):
		payload = "{\"createdBy\":\"s82\",\"projectName\":\"" + "Locust " + randomString(3) + "\"}"
		headers = {'Authorization': "Bearer " + self.token , 'Content-Type': "application/json"}
		response = self.client.post("/RoadwayAnalysisService/api/Project/InsertProject", data=payload, headers=headers)
		jsonobj = json.loads(response.content)
		self.ProjectNumber = jsonobj

	@seq_task(5)	
	def GetQuery(self):
		headers = {'Authorization': "Bearer " + self.token}
		response = self.client.get("/RoadwayAnalysisService/api/Project/GetQuery/" + str(self.ProjectNumber), headers=headers)
		
	@seq_task(6)	
	def GetParishes(self):
		headers = {'Authorization': "Bearer " + self.token}
		response = self.client.get("/RoadwayAnalysisService/api/Warehouse/GetParishes", headers=headers)
		jsonobj = json.loads(response.content)
		Parish = sample(jsonobj, 1)
		self.ParishCode = Parish[0]['code']
		
	@seq_task(7)	
	def GetHighwayTypes(self):
		headers = {'Authorization': "Bearer " + self.token}
		response = self.client.get("/RoadwayAnalysisService/api/Warehouse/GetHighwayTypes", headers=headers)
		jsonobj = json.loads(response.content)
		self.HwyType = sample(jsonobj,1)[0]["hwyTypeCode"]
		
	@seq_task(8)	
	def GetHighwayNumbers(self):
		querystring = {"parishCode": self.ParishCode, "highwayType": self.HwyType}
		headers = {'Authorization': "Bearer " + self.token}
		response = self.client.get("/RoadwayAnalysisService/api/Warehouse/GetHighwayNumbers", headers=headers, params=querystring)
		words = response.content.split(",")
		preprocessedHwyNum = sample(words,1)
		self.HighwayNum = preprocessedHwyNum[0].replace('[', '').replace(']', '')
		
	@seq_task(9)
	def GetControlSection(self):
		querystring = {"parishCode": self.ParishCode, "highwayType": self.HwyType, "highwayNumber": self.HighwayNum}
		headers = {'Authorization': "Bearer " + self.token}
		response = self.client.get("/RoadwayAnalysisService/api/Warehouse/GetControlSection", headers=headers, params=querystring)
		if response.ok:
			words = response.content.split(",")
			controlsections = sample(words,1)
			self.ControlSection = controlsections[0].replace('[', '').replace(']', '').replace('"', '')
			if self.ControlSection == "":
				self.schedule_task(self.GetHighwayTypes)
				self.schedule_task(self.GetHighwayNumbers)
				self.schedule_task(self.GetControlSection)
		else:
			self.schedule_task(self.GetControlSection)
	
	@seq_task(10)
	def GetMinLogmile(self):
		headers = {'Authorization': "Bearer " + self.token}
		response = self.client.get("/RoadwayAnalysisService/api/Warehouse/GetMinLogmile/" + self.ControlSection, headers=headers)
		if response.ok:
			self.MinLogMile = response.content.strip().replace('"', '')
		else:
			self.MinLogMile = "0"

	@seq_task(11)
	def GetMaxLogmile(self):
		headers = {'Authorization': "Bearer " + self.token}
		response = self.client.get("/RoadwayAnalysisService/api/Warehouse/GetMaxLogmile/" + self.ControlSection, headers=headers)
		if response.ok:
			self.MaxLogMile = response.content.strip().replace('"', '')
		else:
			self.MaxLogMile = ".1"
			
	@seq_task(12)	
	def GetCrashes(self, enddate = "2019-01-04T06:00:00.000Z",  startdate = "2016-01-04T06:00:00.000Z", count = 0):
		if count < 10:
			self.enddate = enddate
			self.startdate = startdate
			self.randmax = round(random.uniform(float("0.0" if self.MinLogMile == "0" else self.MinLogMile), float(self.MaxLogMile)), 1)
			self.randmin = self.randmax - .1
			querystring = {"controlSection": self.ControlSection, "endDate": self.enddate, "logmileFrom": self.randmin, "logmileTo": self.randmax, "startDate":self.startdate}
			headers = {'Authorization': "Bearer " + self.token}
			response = self.client.get("/RoadwayAnalysisService/api/Warehouse/GetCrashes", headers=headers, params=querystring)
			if response.content == "[]":
				self.enddate = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())
				randtimemin = time.strptime("01 Jan 13", "%d %b %y")
				randtimemax = time.strptime("31 Dec 17", "%d %b %y")
				self.startdate = randomDate(randtimemin, randtimemax, random.random())
				args = (self.enddate,self.startdate,count + 1)
				self.schedule_task(self.GetCrashes, args=args, first=True)
			else:
				self.crashdata = json.loads(response.content)
		else:
			self.canceled = True

	@seq_task(13)	
	def SaveQuery(self):
		if self.canceled == False:
			headers = {'Authorization': "Bearer " + self.token}
			jsonobj = {'controlSection': self.ControlSection, 'endDate': self.enddate, 'highwaytypeCode': self.HwyType, 'logmileFrom': self.randmin, 'logmileTo': self.randmax, 'parishCode': self.ParishCode, 'primaryHighwayNumber': self.HighwayNum, 'projectID': str(self.ProjectNumber), 'startDate': self.startdate}
			response = self.client.post("/RoadwayAnalysisService/api/Project/SaveQuery", headers=headers, json=jsonobj)
	
	@seq_task(14)	
	def InsertProjectData(self):
		if self.canceled == False:
			for i in range(0,len(self.crashdata)):
				self.crashdata[i]['projectID'] = str(self.ProjectNumber)
			
			headers = {'Authorization': "Bearer " + self.token}
			response = self.client.post("/RoadwayAnalysisService/api/Project/InsertProjectData", headers=headers, json=self.crashdata)
		else:
			headers = {'Authorization': "Bearer " + self.token}
			response = self.client.delete("/RoadwayAnalysisService/api/Project/DeleteProject/" + str(self.ProjectNumber), headers=headers)
		
class NormalUser(HttpLocust):
	weight = 10
	task_set = UserLoad
	#host = "http://roadwayanalysisportaldev.lsu.edu"
	min_wait = 3000
	max_wait = 15000
	
class NewUser(HttpLocust):
	weight = 1
	task_set = UserCreate
	#host = "http://roadwayanalysisportaldev.lsu.edu"
	min_wait = 3000
	max_wait = 15000
	
def hook_request_success(request_type, name, response_time, response_length):
	if name == "//": name = "//Home/Index"
	logging.info("%s %s %s %d success -" % (request_type, name, NormalUser.host, response_time))

def hook_request_fail(request_type, name, response_time, exception):
    logging.info("%s %s %s %d fail %s" % (request_type, name, NormalUser.host, response_time, exception))
#Keep this ^

def randomString(stringLength=8):
    """Generate a random string of fixed length """
    letters= string.ascii_lowercase
    return ''.join(random.sample(letters,stringLength))
	
def generateDate(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(start)
    etime = time.mktime(end)

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))

def randomDate(start, end, prop):
    return generateDate(start, end, '%Y-%m-%dT%H:%M:%S', prop)
	


events.request_success += hook_request_success
events.request_failure += hook_request_fail
