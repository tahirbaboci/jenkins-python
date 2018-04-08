import cursor as cursor
import requests
import jenkins
import datetime
from django.db import models


def connectToJenkins(url, username, password):

    server = jenkins.Jenkins(url,
                             username=username,
                             password=password)
    return server


def addJob(jlist):
    for j in jlist:
        j = Jobs()
        j.save()


def getLastJobId(session, name):
    cursor.execute("SELECT * FROM table ORDER BY id DESC LIMIT 1")
    job = cursor.fetchone()
    if (job != None):
        return job.jen_id
    else:
        return None


class Jobs(models.Model):
    jenkins_id = models.IntegerField(max_length=1000)
    name = models.CharField(max_length=250)
    timeStamp = models.DateField()
    result = models.CharField(max_length=500)
    building = models.CharField()
    estimateDuration = models.CharField(250)


def createJobList(start, lastBuildNumber, jobName):
    jList = []
    for i in range(start + 1, lastBuildNumber + 1):
        current = server.get_build_info(jobName, i)
        current_as_jobs = Jobs()
        current_as_jobs.jen_id = current['id']
        current_as_jobs.building = current['building']
        current_as_jobs.estimatedDuration = current['estimatedDuration']
        current_as_jobs.name = jobName
        current_as_jobs.result = current['result']
        current_as_jobs.timeStamp = datetime.datetime.fromtimestamp(long(current['timestamp']) * 0.001)
        jList.append(current_as_jobs)
    return jList


url = 'http://localhost:8080'
username = input('Enter username: ')
password = input('Enter password: ')
server = connectToJenkins(url, username, password)

auth = False
try:
    server.get_whoami()
    auth = True
except jenkins.JenkinsException as e:
    print
    'Authentication error'
    authenticated = False

if auth:

    # get a list of all jobss
    jobs = server.get_all_jobs()
    for j in jobs:
        jobName = j['name']  # get job name
        print(jobName)
        lastJobId = getLastJobId(jobName)  # get last locally stored job of this name
        lastBuildNumber = server.get_job_info(jobName)['lastBuild'][
            'number']  # get last build number from Jenkins for this job

        # if job not stored, update the db with all entries
        if lastJobId == None:
            start = 0
        # if job exists, update the db with new entrie
        else:
            start = lastJobId

        # create a list of unadded job objects
        jlist = createJobList(start, lastBuildNumber, jobName)
        # add job to db
        addJob(jlist)