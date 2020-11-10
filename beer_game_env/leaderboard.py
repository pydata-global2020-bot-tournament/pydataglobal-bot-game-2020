import os
import subprocess

import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path

from requests.exceptions import HTTPError


def post_score_to_api(score: float):
    # payload data
    data = {"user": "Player1", "score": score}
    git_user = subprocess.check_output(
        ["git", "log", "-1", "--pretty=format:%an"]
    ).decode()
    print(f"Sending data to leaderboard: User: {git_user}, score: {score}")

    # authentication
    username = os.environ["LEADERBOARD_API_USERNAME"]
    password = os.environ["LEADERBOARD_API_PASSWORD"]
    url = "https://leaderboard-server.pydata-bot-tournament.eu.live.external.byp.ai/add-user-score"

    ca_file = str(Path(__file__).parent.absolute() / "resources" / "CA.crt")

    r = requests.post(
        url=url,
        json=data,
        headers={"content-type": "application/json"},
        auth=HTTPBasicAuth(username, password),
        verify=ca_file,
    )

    if not r.ok:
        raise Exception(
            f"Updating score was not successful and failed with {r.status_code}"
        )
    print("post was successful")
