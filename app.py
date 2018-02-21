from flask import Flask, jsonify
import requests
import json
import shelve

app = Flask(__name__)

userdata = shelve.open("userdata")

def get_user_data(userhandles, count):
    userhandles = userhandles[:]

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
                                            "organization": user.get("organization", 'N/A') or 'N/A'};
        else:
            #bad user, user handle change problem
            if (len(currhandles) == 1):
                userdata[currhandles[0]] = {"country": 'N/A',
                                            "city": 'N/A',
                                            "organization": 'N/A'};
        
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

    #best constants
    get_user_data(userhandles, 343)
    get_user_data(userhandles, 49)
    get_user_data(userhandles, 7)
    get_user_data(userhandles, 1)

    print(list(userdata.keys()))
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)