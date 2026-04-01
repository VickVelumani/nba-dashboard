from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
def format_game_time(datetime_str):
    try:
        dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        # Convert UTC to Eastern time (subtract 4 hours)
        dt = dt - timedelta(hours=4)
        return dt.strftime("%I:%M %p ET")
    except:
        return datetime_str
def get_nba_games(team_name=None):
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")

    url = "https://api.balldontlie.io/v1/games"
    params = {
        "dates[]": [yesterday, today],
        "per_page": 25
    }
    headers = {
        "Authorization": "b79c8ac5-9664-422e-af0b-c10a7916ad45"
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    games = data["data"]

    if team_name:
        team_name = team_name.lower()
        games = [g for g in games if team_name in g["home_team"]["full_name"].lower() or team_name in g["visitor_team"]["full_name"].lower()]
    for game in games:
        game["formatted_time"] = format_game_time(game.get("datetime", ""))
    
    return games

def get_player_stats(player_name):
    headers = {"Authorization": "b79c8ac5-9664-422e-af0b-c10a7916ad45"}

    first_word = player_name.strip().title().split()[0]

    search_url = "https://api.balldontlie.io/v1/players"
    search_res = requests.get(search_url, params={"search": first_word, "per_page": 25}, headers=headers)
    players = search_res.json()["data"]

    if not players:
        return None, None

    full_name = player_name.lower()
    player = None
    for p in players:
        name = (p["first_name"] + " " + p["last_name"]).lower()
        if full_name in name or name in full_name:
            player = p
            break

    if not player:
        player = players[0]

    return player, None

@app.route("/")
def home():
    team_name = request.args.get("team", "")
    games = get_nba_games(team_name)
    return render_template("index.html", games=games, team=team_name)

@app.route("/players")
def players():
    player_name = request.args.get("name", "")
    player, stats = get_player_stats(player_name) if player_name else (None, None)
    return render_template("players.html", player=player, stats=stats, name=player_name)

if __name__ == "__main__":
    app.run(debug=True)