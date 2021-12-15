from flask import Flask, request, jsonify
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

# queries = open("queries.txt", ).read().split('\n')
# print(len(queries))

# for q in queries:
#     try:
#         session.run(q)

#     except Exception as e:
#         print(str(e))

def possibility_of_user_infection(name):
    req = []
    find_groups = 'Match(p:Person)-[b:BelongsTo]->(g_p:Group) where p.name = "' + name + '"'
    first_type = '\nMatch (g_p)-[x:HasGoneTo]->(pl:Place)\noptional Match (group_first_type:Group)' \
                 '\nwhere (group_first_type)-[:HasGoneTo]->(pl) and group_first_type.test = "positive"' \
                 ' \noptional Match(placeOfInfection1:Place) \nwhere (group_first_type)-[:HasGoneTo]->' \
                 '(placeOfInfection1) and (g_p)-[:HasGoneTo]->(placeOfInfection1)'
    second_type = '\noptional Match(group_in_same_place: Group)' \
                  '\nwhere (group_in_same_place)-[:HasGoneTo]->(pl)' \
                  '\noptional Match (group_in_same_place)-[:HasGoneTo]->(pl_second_type:Place)' \
                  '\noptional Match(group_second_type:Group)' \
                  '\nwhere group_first_type IS NULL and (group_second_type)-[:HasGoneTo]->(pl_second_type) and ' \
                  'group_second_type.test = "positive"' \
                  '\noptional Match(placeOfInfection2:Place)' \
                  '\nwhere (group_second_type)-[:HasGoneTo]->(placeOfInfection2) and (group_in_same_place)-[' \
                  ':HasGoneTo]->(placeOfInfection2)'
    prob = '\noptional match(phist:PlaceHistory)-[hist:HistoryArc]->(thist:TimeHistory) where phist.name = placeOfInfection1.name and ' \
           'thist.type = placeOfInfection1.time ' \
           '\noptional match(phist2:PlaceHistory)-[hist2:HistoryArc]->(thist2:TimeHistory) where phist2.name = placeOfInfection2.name and ' \
           'thist2.type = placeOfInfection2.time ' \
           '\nreturn placeOfInfection1,sum(hist.infection)*1.0,sum(hist.total), placeOfInfection2, ' \
           'sum(hist2.infection)*1.0,sum(hist2.total)'

    req.append(find_groups + first_type + second_type + prob)
    return req

def most_danger_place():
    return ["match (p:PlaceHistory)-[h:HistoryArc]->(t:TimeHistory) return p,sum(h.infection)*1.0/sum(h.total) " \
           "as prob order by prob DESC"]

def most_danger_time():
    morning = "match (p:PlaceHistory)-[h:HistoryArc]->(t:TimeHistory) where t.type =\"morning\" " \
              "return sum(h.infection)*1.0/sum(h.total) as prob"
    afternoon = "match (p:PlaceHistory)-[h:HistoryArc]->(t:TimeHistory) where t.type =\"afternoon\"" \
                " return sum(h.infection)*1.0/sum(h.total) as prob"
    night = "match (p:PlaceHistory)-[h:HistoryArc]->(t:TimeHistory) where t.type =\"night\" " \
            "return sum(h.infection)*1.0/sum(h.total) as prob"
    return [morning, afternoon, night]

query = possibility_of_user_infection("Ali")

for q in query:
    print(q)
    results = session.run(q)
    data=results.data()
    print(data)