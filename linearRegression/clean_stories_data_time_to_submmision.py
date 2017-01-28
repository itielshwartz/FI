#!/usr/bin/env python3.6

import csv
import gzip
import json

import arrow

with gzip.open('hn_users_13249654_to_13449650.json.gz') as r:
    users = json.loads(r.read())
    # with gzip.open('hn_posts_13249654_to_13449650.json.gz') as r:
    #   posts = json.loads(r.read())  # We change the users to a dict stracture, so it will be easier to work with
# users = {user["id"]: user for user in users if user is not None}
user_time_to_stories = []
# we are going from the most recent story, to the oldest story
for user in users:
    if user is not None and user["submitted"] and len(user["submitted"]) > 1000:
        user_time_to_stories.append(((arrow.now() - arrow.get(user["created"])).days, len(user["submitted"])))

with open("training_set_data.csv", "w") as file:
    writer = csv.writer(file)
    for days_to_user_submitted in user_time_to_stories:
        writer.writerow(days_to_user_submitted)
