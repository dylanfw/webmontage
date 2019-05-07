import argparse
import sys
import time

from git import Repo
from git.exc import (
    GitCommandError,
    InvalidGitRepositoryError,
    NoSuchPathError,
)



class WebMontageError(Exception):
    pass


def get_args():
    parser = argparse.ArgumentParser(description='WebMontage - Static site montage generator using git history')
    parser.add_argument('repo', metavar='repository', help='The absolute path to the root of the git repository for the web page')
    parser.add_argument('index', metavar='index', help='The index file relative to the root of the repo')
    return parser.parse_args()


def main():
    args = get_args()

    try:
        repo = Repo(args.repo)
        git = repo.git
    except (InvalidGitRepositoryError, NoSuchPathError):
        sys.stderr.write(f'No git repository found at: {args.repo}\n')
        sys.exit(1)

    git.checkout('master')
    try:
        index_commits = git.log(args.index, pretty='format:"%h"', follow=True)
    except GitCommandError:
        sys.stderr.write(f'Error occurred finding commits. Make sure {args.repo}/{args.index} exists and has a commit history: > git log --pretty=format:"%h" --follow -- {args.index}\n')
        sys.exit(1)

    index_commits = index_commits.replace('"', '').split('\n')
    index_commits.reverse()
    for i, commit in enumerate(index_commits):
        git.checkout(commit)
        # TODO Load page and take screenshot
    git.checkout('master')
    # TODO Combine screenshots into timelapse video
