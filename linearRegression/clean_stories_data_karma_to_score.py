#!/usr/bin/env python3.6

import csv
import gzip
import json

# first step is to open the gzip files
with gzip.open('hn_users_13249654_to_13449650.json.gz') as r:
    users = json.loads(r.read())
with gzip.open('hn_posts_13249654_to_13449650.json.gz') as r:
    posts = json.loads(r.read())
# We change the users to a dict stracture, so it will be easier to work with
users = {user["id"]: user for user in users if user is not None}
user_karma_to_score = {}
# we are going from the most recent story, to the oldest story
for post in posts:
    if post is not None and post.get("type") == "story" and not post.get("deleted"):
        user = users.get(post.get("by"))
        if user:
            # the user karma while posting is :
            # his karma - this story - all stories this user posted in the future
            user["karma_while_posting"] = user.get(
                "karma_while_posting", user.get("karma")) - post["score"]
            user_karma_to_score[post["id"]] = (
                user["karma_while_posting"], post["score"],)

# len(stories_with_correct_user_karma should)=27,644
print(len(user_karma_to_score))

with open("training_set_data_karma_to_score.csv", "w") as file:
    writer = csv.writer(file)
    for karma_to_score in user_karma_to_score.values():
        writer.writerow(karma_to_score)
