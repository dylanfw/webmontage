import argparse
import os
import sys
import time

from git import Repo
from git.exc import (
    GitCommandError,
    InvalidGitRepositoryError,
    NoSuchPathError,
)
from selenium import webdriver


class WebMontageError(Exception):
    pass


def get_browser():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    return webdriver.Chrome('chromedriver', chrome_options=chrome_options)


def get_git(path):
    try:
        repo = Repo(path)
        client = repo.git
    except (InvalidGitRepositoryError, NoSuchPathError) as e:
        raise WebMontageError(f'No git repository found at {path}')
    return client


def get_history(git, filename):
    try:
        commits = git.log(filename, pretty='format:"%h"', follow=True)
        commits = commits.replace('"', '').split('\n')
        commits.reverse()
    except GitCommandError as e:
        raise WebMontageError(f'Error occurred finding commits. Make sure {self.path}/{filename} exists and has a commit history: > git log --pretty=format:"%h" --follow -- {filename}')
    return commits


def get_args():
    parser = argparse.ArgumentParser(description='WebMontage - Static site montage generator using git history')
    parser.add_argument('repo', metavar='repository', help='The absolute path to the root of the git repository for the web page')
    parser.add_argument('index', metavar='index', help='The index file relative to the root of the repo')
    return parser.parse_args()


def main():
    args = get_args()

    git = get_git(args.repo)
    git.checkout('master')
    history = get_history(git, args.index)
    browser = get_browser()
    for i, commit in enumerate(history):
        git.checkout(commit)
        browser.get(f'file:///{args.repo}/{args.index}')
        screenshot = browser.save_screenshot(f'{i}.png')
    browser.quit()
    git.checkout('master')
    # TODO Combine screenshots into timelapse video
