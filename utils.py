import json
from datetime import datetime

def parse_date(date_string):
    try:
        return datetime.strptime(date_string, "%b %d, %Y").date()
    except ValueError:
        return None

def parse_csv_data(csv_reader):
    data = []
    for row in csv_reader:
        data.append({
            "appid": int(row["AppID"]),
            "name": row["Name"],
            "release_date": parse_date(row["Release date"]),
            "required_age": int(row["Required age"]),
            "price": float(row["Price"]),
            "dlc_count": int(row["DLC count"]),
            "about_the_game": row["About the game"],
            "supported_languages": json.dumps(row["Supported languages"].strip("[]").replace("'", "").split(", ")),
            "windows": row["Windows"].strip().lower() == "true",
            "mac": row["Mac"].strip().lower() == "true",
            "linux": row["Linux"].strip().lower() == "true",
            "positive": int(row["Positive"]) if row["Positive"] else 0,
            "negative": int(row["Negative"]) if row["Negative"] else 0,
            "score_rank": int(row["Score rank"]) if row["Score rank"] else 0,
            "developers": row["Developers"],
            "publishers": row["Publishers"],
            "categories": json.dumps(row["Categories"].strip("[]").replace("'", "").split(", ")),
            "genres": json.dumps(row["Genres"].strip("[]").replace("'", "").split(", ")),
            "tags": json.dumps(row["Tags"].strip("[]").replace("'", "").split(", "))
        })
    return data