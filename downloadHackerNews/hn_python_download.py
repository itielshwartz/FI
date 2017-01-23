#!/usr/bin/env python3.6
import asyncio
import json
import logging
import time

import click
import requests
import tqdm
from aiohttp import ClientSession, TCPConnector

MAX_CONNECTION = 1000

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
# print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
# To make sure we don't kill the server/ our comp
sem = asyncio.Semaphore(MAX_CONNECTION)


async def fetch(url, session):
    async with session.get(url) as response:
        return await response.json(), url


async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        return await fetch(url, session)


async def download_with_retries(session, tasks):
    max_retry_count, retry_count, responses, retry_tasks = 5, 0, [], []
    while tasks:
        for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            response, url = await f
            if response == {'error': 'Internal server error.'}:
                retry_tasks.append(url)
            else:
                responses.append(response)
        # in case we had problem with some requests and we didn't exceeded retries - we try again
        if retry_count == max_retry_count or not retry_tasks:
            break
        retry_count += 1
        time.sleep(10)  # letting the server recover..
        logger.warning("retrying to download %s urls" % len(retry_tasks))
        tasks, retry_tasks = retry_tasks, []
    return responses


async def download_stories(max_item, n):
    url = "https://hacker-news.firebaseio.com/v0/item/{}.json"
    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    stories_conn = TCPConnector(limit=min(MAX_CONNECTION, n))
    async with ClientSession(connector=stories_conn) as session:
        tasks = [asyncio.ensure_future(bound_fetch(sem, url.format(max_item - i), session)) for i in
                 range(min(n, max_item))]
        return await download_with_retries(session, tasks)


async def download_users(users_names):
    url = "https://hacker-news.firebaseio.com/v0/user/{}.json"
    tasks = []
    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    # more connections = download faster
    conn = TCPConnector(limit=min(MAX_CONNECTION, len(users_names)))
    async with ClientSession(connector=conn) as session:
        tasks = [asyncio.ensure_future(bound_fetch(sem, url.format(user), session)) for user in users_names]
        return await download_with_retries(session, tasks)


def get_users(users_names):
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(download_users(users_names))
    return loop.run_until_complete(future)


def get_last_n_stories(n, max_item=None):
    loop = asyncio.get_event_loop()
    max_item = max_item or requests.get(
        'https://hacker-news.firebaseio.com/v0/maxitem.json').json()
    future = asyncio.ensure_future(download_stories(max_item, n))
    return loop.run_until_complete(future)


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
@click.option('--start-from', type=int, help='The item to start download from')
def last_n(n, include_users, output, users_output, start_from):
    logger.info(
        "Starting download %s posts from HN, users %s" % (n, "included" if include_users else "not included"))
    responses = get_last_n_stories(n, start_from)
    logger.info("Saving the posts to %s", output.name)
    json.dump(responses, output, indent=4)
    get_and_save_users_data(include_users, responses, users_output)


if __name__ == '__main__':
    last_n()
    # run using hn_python_download.py 1000 --include-users
