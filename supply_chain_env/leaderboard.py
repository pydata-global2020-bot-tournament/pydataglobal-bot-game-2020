import os
import subprocess
from pathlib import Path
from typing import Optional

import requests
from requests.auth import HTTPBasicAuth


def post_score_to_api(score: float):
    # payload data
    data = {"user": "Anonymous", "score": score}
    git_info = subprocess.check_output(
        ["git", "log", "-1", "--pretty=format:%H, %an"]
    ).decode()
    ref, git_user = git_info.split(",")
    github_user = _get_github_user(ref)
    data["user"] = github_user if github_user else git_user

    print(f"Sending data to leaderboard: User: {git_user}, score: {score}")

    # authentication
    username = os.environ["LEADERBOARD_API_USERNAME"]
    password = os.environ["LEADERBOARD_API_PASSWORD"]
    url = "https://leaderboard-server-prod.pydata-bot-tournament.eu.live.external.byp.ai/add-user-score"

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


def _get_github_user(ref: str) -> Optional[str]:
    try:
        url = f"https://api.github.com/repos/pydata-global2020-bot-tournament/pydataglobal-bot-game-2020/commits/{ref}"
        r = requests.get(url)
        if r.ok:
            commit = r.json()
            return commit.get("author", {}).get("login")
        return None
    except Exception as e:
        print("Can not get data from github api")
        print(e)
        return None
