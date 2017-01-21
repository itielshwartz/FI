#!/usr/bin/env python3.6
import asyncio
import json
import logging

import click
import requests
import tqdm
from aiohttp import ClientSession

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
sem = asyncio.Semaphore(300)


async def fetch(url, session):
    async with session.get(url) as response:
        return await response.json()


async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        return await fetch(url, session)


async def download_stories(max_item, n):
    url = "https://hacker-news.firebaseio.com/v0/item/{}.json"
    tasks = []
    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    async with ClientSession() as session:
        for i in range(min(n, max_item)):
            task = asyncio.ensure_future(
                bound_fetch(sem, url.format(max_item - i), session))
            tasks.append(task)
        responses = []
        for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            responses.append(await f)

        return responses


async def download_users(users_names):
    url = "https://hacker-news.firebaseio.com/v0/user/{}.json"
    tasks = []
    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    async with ClientSession() as session:
        for user in users_names:
            task = asyncio.ensure_future(
                bound_fetch(sem, url.format(user), session))
            tasks.append(task)
        responses = []
        for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            responses.append(await f)
        return responses


def get_users(users_names):
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(download_users(users_names))
    return loop.run_until_complete(future)


def get_last_n_stories(n, max_item=None):
    loop = asyncio.get_event_loop()
    max_item = max_item or get_hn_max_item()
    future = asyncio.ensure_future(download_stories(max_item, n))
    return loop.run_until_complete(future)


def get_hn_max_item():
    return requests.get(
        'https://hacker-news.firebaseio.com/v0/maxitem.json').json()


def get_and_save_users_data(include_users, responses, users_output):
    if include_users:
        logger.info("Start getting users data")
        users_names = set([response.get("by") for response in responses if response is not None])
        users = get_users(users_names)
        logger.info("Saving the users to %s", users_output.name)
        json.dump(users, users_output, indent=4)


@click.command()
@click.argument('n', default=10, )
@click.option('--include-users', is_flag=True, help='should download users realted to posts')
@click.option('--output', type=click.File('w'), help='the output file name', default="hn.json")
@click.option('--users-output', type=click.File('w'), help='the users output file name', default="hn_users.json")
def last_n(n, include_users, output, users_output):
    logger.info(
        "Starting download %s posts from HN, users %s" % (n, "included" if include_users else "not included"))
    responses = get_last_n_stories(n)
    logger.info("Saving the posts to %s", output.name)
    json.dump(responses, output, indent=4)
    get_and_save_users_data(include_users, responses, users_output)


if __name__ == '__main__':
    last_n()
