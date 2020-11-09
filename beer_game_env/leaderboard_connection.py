import subprocess
import requests
from requests.auth import HTTPBasicAuth


def post_score_to_api(score: float):  
    # authentication
    username = "pydata-leaderboatd-api-user"
    password = "svjYxP6P3Tpnp4meK32N4ZwN22H8ddD5xg4hXrhf"
    url = "https://leaderboard-server.pydata-bot-tournament.eu.live.external.byp.ai/add-user-score"

    # payload data
    data = {"user": "Player1", "score": score}
    git_user = subprocess.check_output(["git", "log", "-1", "--pretty=format:'%an'"])

    # git_user = os.system("git log -1 --pretty=format:'%an'")
    print(f"Sending data to leaderboard: User: {git_user}, score: {score}")
    r = requests.post(
        url=url,
        json=data,
        headers={"content-type": "application/json"},
        auth=HTTPBasicAuth(username, password),    
    )

    assert r.ok