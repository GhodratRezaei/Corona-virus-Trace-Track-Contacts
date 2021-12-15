import datetime

from flask import jsonify, render_template

from app import app, driver, session

counter = 1000


# def execute_query(query):
#     try:
#         result = session.run(query)
#         data = result.data()
#         return jsonify(data)
#     except Exception as e:
#         return str(e)

@app.route("/possibility_of_infection/<string:person_name>", methods=["GET", "POST"])
def possibility_of_user_infection(person_name):
    req = []
    find_groups = 'Match(p:Person)-[b:BelongsTo]->(g_p:Group) where p.name = "' + person_name + '"'
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
           '\nreturn placeOfInfection1.name as placetype1Name,sum(hist.infection)*1.0 as totalInfected1,sum(hist.total) as totalPeople1' \
           ', placeOfInfection2.name as placetype2Name, ' \
           'sum(hist2.infection)*1.0 as totalInfected2,sum(hist2.total)as totalPeople2'

    query = find_groups + first_type + second_type + prob

    print(query)
    try:
        result = session.run(query)
        data = result.data()
        return jsonify(data)
    except Exception as e:
        return str(e)


@app.route("/most_dangerous_place")
def most_dangerous_place():
    query = "match (p:PlaceHistory)-[h:HistoryArc]->(t:TimeHistory) return p.name as placeName,sum(h.infection)*1.0/sum(h.total) " \
            "as DangerRate order by DangerRate DESC"

    try:
        result = session.run(query)
        data = result.data()
        return jsonify(data)
    except Exception as e:
        return str(e)


@app.route("/most_dangerous_time")
def most_danger_time():
    morning = "match (p:PlaceHistory)-[h:HistoryArc]->(t:TimeHistory) where t.type =\"morning\" " \
              "return sum(h.infection)*1.0/sum(h.total) as MorningDangerRate"
    afternoon = "match (p:PlaceHistory)-[h:HistoryArc]->(t:TimeHistory) where t.type =\"afternoon\"" \
                " return sum(h.infection)*1.0/sum(h.total) as AfternoonDangerRate"
    night = "match (p:PlaceHistory)-[h:HistoryArc]->(t:TimeHistory) where t.type =\"night\" " \
            "return sum(h.infection)*1.0/sum(h.total) as NightDangerRate"

    queries = [morning, afternoon, night]
    results = []
    for q in queries:
        try:
            result = session.run(q)
            data = result.data()
            results.append(data)
        except Exception as e:
            return str(e)

    return jsonify(results)


@app.route("/most_dangerous_time_of_place/<string:place_name>", methods=["GET", "POST"])
def most_danger_time_of_a_place(place_name):
    morning = "match (p:PlaceHistory)-[h:HistoryArc]->(t:TimeHistory) where " \
              "p.name =\"" + place_name + "\" and t.type =\"morning\"return sum(h.infection)*1.0/sum(h.total) as MorningDangerRate"
    afternoon = "match (p:PlaceHistory)-[h:HistoryArc]->(t:TimeHistory) where " \
                "p.name =\"" + place_name + "\" and t.type =\"afternoon\"return sum(h.infection)*1.0/sum(h.total) as AfternoonDangerRate"
    night = "match (p:PlaceHistory)-[h:HistoryArc]->(t:TimeHistory) where " \
            "p.name =\"" + place_name + "\" and t.type =\"night\"return sum(h.infection)*1.0/sum(h.total) as NightDangerRate"

    queries = [morning, afternoon, night]
    results = []
    for q in queries:
        try:
            result = session.run(q)
            data = result.data()
            results.append(data)
        except Exception as e:
            return str(e)

    return jsonify(results)


@app.route("/person_history/<string:person_name>", methods=["GET", "POST"])
def history(person_name):
    query = "match(p:Person)-[b:BelongsTo]->(g:Group),(g)-[h:HasGoneTo]->(pl:Place) " \
            "where p.name = \"" + person_name + "\" return pl.name as placeName"
    print(query)
    try:
        result = session.run(query)
        data = result.data()
        for d in data:
            for atr in d:
                if d[atr] != None and 'ExDate' in d[atr]:
                    d[atr]['ExDate'] = d[atr]['ExDate'].isoformat()
        return jsonify(data)
    except Exception as e:
        return str(e)


def delete_expired_contacts():
    return ["match (p:Place) where date() > p.ExDate detach delete p"]


def find_dangerous_contact(name):
    req = []
    req.extend(delete_expired_contacts())
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
                  ':HasGoneTo]->(placeOfInfection2)' \
                  '\nreturn placeOfInfection1, placeOfInfection2'
    req.append(find_groups + first_type + second_type)

    return req


@app.route("/update_test_result/<string:test_result>&<string:person_name>", methods=["GET", "POST"])
def update_test_result(test_result, person_name):
    queries = []
    if test_result == "positive":

        queries.append(
            "match(p:Person) ,(p)-[b:BelongsTo]->(g:Group) where p.name =\"" + person_name + "\" set p.test=\"positive\"" \
                                                                                             " ,g.test=\"positive\"return p,b,g")
        queries.extend(find_dangerous_contact(person_name))
    else:
        queries.append("match(p:Person) where p.name =\"" + person_name + "\" set p.test=\"negative\" return p")
        queries.append("MATCH(u:Group) where u.test = \"positive\" set u.test=\"negative\" return u ")
        queries.append("MATCH(u:Group) where u.test = \"positive\" set u.test=\"negative\" return u ")

    results = []
    for q in queries:
        try:
            result = session.run(q)
            data = result.data()
            for d in data:
                for atr in d:
                    if d[atr] != None and 'ExDate' in d[atr]:
                        d[atr]['ExDate'] = d[atr]['ExDate'].isoformat()
            results.append(data)
        except Exception as e:
            return str(e)

    return jsonify(results)


@app.route("/update_history_graph/<string:place_name>&<string:time>&<string:type_of_inc>", methods=["GET", "POST"])
def update_history_graph(place_name, time, type_of_inc):
    if type_of_inc == "positive":
        query = "match(p:PlaceHistory)-[h:HistoryArc]->(t:TimeHistory) where p.name = \"" + place_name + "\" and t.type = \"" + \
                time + "\" set h.infection = h.infection + 1 return p,h,t"
        try:
            result = session.run(query)
            data = result.data()
            return jsonify(data)
        except Exception as e:
            return str(e)
    else:
        query = "match(p:PlaceHistory)-[h:HistoryArc]->(t:TimeHistory) where p.name = \"" + place_name + "\" and t.type = \"" + \
                time + "\" set h.total = h.total + 1 return p,h,t"
        try:
            result = session.run(query)
            data = result.data()
            return jsonify(data)
        except Exception as e:
            return str(e)


@app.route("/contact_occurs/<string:place_name>&<string:time>&<string:type>&<string:list_of_individuals>",
           methods=["GET", "POST"])
def contact_occurs(place_name, time, type, list_of_individuals):
    queries = []
    global counter
    counter += 1
    list_of_individuals = list_of_individuals.split('-')
    for name in list_of_individuals:
        persons_groups = 'Match(p:Person)-[b:BelongsTo]->(g_p:Group) where p.name ="' + name + '"'

        if place_name != "Meeting":
            time_plce_node = '\nMerge(pl: Place{name:"' + place_name + '"' + ',time:"' + time + '"})' \
                             + 'on create set pl.name="' + place_name + '", pl.time="' + time + \
                             '", pl.type="' + type + '"'
            contact = "\nMerge (g_p)-[x:HasGoneTo]->(pl)"
            queries.append(persons_groups + time_plce_node + contact)
        else:
            create_meeting_instance = '\nMerge(pl:Place{name:"Meeting' + str(counter) + '"' + \
                                      'on create set pl.name="Meeting' + str(counter) + '"'
            contact = "\ncreate (g_p)-[x:HasGoneTo]->(pl)"
            queries.append(persons_groups + create_meeting_instance + contact)

    update_history = "match(p:PlaceHistory)-[h:HistoryArc]->(t:TimeHistory) where p.name = \"" + place_name + "\" and t.type = \"" + \
                     time + "\" set h.total = h.total + 1 return p,h,t"
    queries.append(update_history)

    results = []
    for q in queries:
        try:
            result = session.run(q)
            data = result.data()
            results.append(data)
        except Exception as e:
            return str(e)
    print(jsonify(results))
    return jsonify(results)