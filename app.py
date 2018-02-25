from flask import Flask, render_template
import requests
import json
import shelve

app = Flask(__name__)

userdata = shelve.open("userdata")

def getcolor(rating):
    if (rating >= 2900):
        return "legendary"
    elif (rating >= 2400):
        return "red"
    elif (rating >= 2200):
        return "orange"
    elif (rating >= 1900):
        return "violet"
    elif (rating >= 1600):
        return "blue"
    elif (rating >= 1400):
        return "cyan"
    elif (rating >= 1200):
        return "green"
    elif (rating >= 0):
        return "gray"
    else:
        return "black"

def get_user_data(userhandles, count):
    userhandles = userhandles[:]

    anyerror = 0

    while (len(userhandles) >= 1):
        currhandles = []

        while (len(userhandles) >= 1 and len(currhandles) < count):
            handle = userhandles.pop()
            if (handle not in userdata):
                currhandles.append(handle)

        url = 'http://codeforces.com/api/user.info?handles=%s' % ";".join(currhandles)
        print(url, currhandles, count)

        response = requests.get(url)
        response = response.json()
        
        if (response["status"] == "OK"):
            for user in response["result"]:
                userdata[user["handle"]] = {"country": user.get("country", 'N/A') or 'N/A',
                                            "city": user.get("city", 'N/A') or 'N/A',
                                            "organization": user.get("organization", 'N/A') or 'N/A',
                                            "rating": user.get("rating", -1500)};
        else:
            if (len(currhandles) >= 1):
                anyerror = 1

            #bad user, user handle change problem
            if (len(currhandles) == 1):
                userdata[currhandles[0]] = {
                    "country": 'N/A',
                    "city": 'N/A',
                    "organization": 'N/A',
                    "rating": -1500
                };

    return anyerror
        
@app.route('/')
def index():
    return "Something awesome here!"

@app.route('/standings/<int:contest_id>', methods=['GET'])
def get_standings_contents(contest_id):
    response = requests.get('http://codeforces.com/api/contest.standings?from=1&count=2000&contestId=%s&showUnofficial=false' % contest_id)
    response = response.json()
    result = response["result"]

    userhandles = []

    for res in result["rows"]:
        for member in res["party"]["members"]:
            userhandles.append(member["handle"])

    #best constant
    count = 512
    while (count >= 1):
        if (get_user_data(userhandles, count) == 0):
            break
        count = count // 2

    standings = []

    for res in result["rows"]:
        handle = res["party"]["members"][0]["handle"]

        data = {
            "rank": res["rank"],
            "ratingcss": "user user-" + getcolor(userdata[handle]["rating"]),
            "handle": handle,
            "points": res["points"],
            "country": userdata[handle]["country"],
            "city": userdata[handle]["city"],
            "organization": userdata[handle]["organization"],
            "problemResults": res["problemResults"],
            "successfulHackCount": res["successfulHackCount"],
            "unsuccessfulHackCount": res["unsuccessfulHackCount"]
        }

        '''
        if (data["country"] == "India"):
            #temp filter
            standings.append(data)
        '''
        
        standings.append(data)
    
    return render_template("standings.html", 
                            standings = standings, 
                            problems = result["problems"],
                            name = result["contest"]["name"],
                            id = result["contest"]["id"])

if __name__ == '__main__':
    app.run(debug=True)