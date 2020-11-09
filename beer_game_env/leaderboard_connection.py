import requests
from requests.auth import HTTPBasicAuth


def post_score_to_api(score: float):  
    # authentication
    username = "pydata-leaderboatd-api-user"
    password = "svjYxP6P3Tpnp4meK32N4ZwN22H8ddD5xg4hXrhf"

    # payload data
    data = {"user": "Player1", "score": score}
    
    r = requests.post(
        url="http://127.0.0.1:8000/add-user-score",
        json=data,
        headers={"content-type": "application/json"},
        auth=HTTPBasicAuth(username, password),    
    )

    assert r.ok