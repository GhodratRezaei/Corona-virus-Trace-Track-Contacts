from flask import Flask, request, redirect
from neo4j import GraphDatabase
import csv

app = Flask(__name__)

# establish the connection
with open("credentials.txt") as f:
    data=csv.reader(f, delimiter=",")
    for row in data:
        username = row[0]
        pwd = row[1]
        uri = row[2]

driver = GraphDatabase.driver(uri=uri, auth=(username, pwd))
session = driver.session()

from app import views, requests
