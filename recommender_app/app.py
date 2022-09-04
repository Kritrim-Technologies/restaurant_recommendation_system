from recommender_app.recommend import (
    get_recommendation,
    get_user_list,
    get_column_tag,
    update_dataset,
    get_tag_list,
    get_unique_user_ratings,
)
from flask import Flask, request, jsonify, render_template
import json

app = Flask(__name__)

# ----------------------------------------------------------------------------------------------------------------------------------------------------

# root api direct to index.html (home page)
@app.route("/")
def home():
    users = get_user_list()
    restaurant_and_tags = get_column_tag()
    restaurants = list(restaurant_and_tags.keys())
    tags = list(restaurant_and_tags.values())
    tag_list = get_tag_list()
    return render_template(
        "index.html",
        users=json.dumps(users),
        restaurants=json.dumps(restaurants),
        restaurant_tags=json.dumps(tags),
        tag_list=json.dumps(tag_list),
    )


@app.route("/recommend", methods=["POST"])
def recommend():
    """
    For rendering results on HTML GUI

    """
    features = [str(x) for x in request.form.values()]

    user = str(features[0])
    rest_name = str(features[2])
    rating = float(features[3])
    update_dataset(user, rest_name, rating)
    users = get_user_list()
    restaurant_and_tags = get_column_tag()
    restaurants = list(restaurant_and_tags.keys())
    tags = list(restaurant_and_tags.values())
    unique_user_ratings = get_unique_user_ratings(user)

    res, tags, likeness = get_recommendation(user)

    return render_template(
        "index.html",
        user=user,
        recommend_tags=zip(res, tags, likeness),
        unique_user_ratings=zip(
            list(unique_user_ratings.keys()),
            list(unique_user_ratings.values()),
        ),
        users=json.dumps(users),
        restaurants=json.dumps(restaurants),
        restaurant_tags=json.dumps(tags),
        tag_list=json.dumps(get_tag_list()),
    )
