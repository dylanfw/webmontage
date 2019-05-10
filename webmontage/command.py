import argparse
import os
import sys
import time
import tempfile

import cv2
import imutils
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from selenium import webdriver


class WebMontageError(Exception):
    pass


def get_args():
    parser = argparse.ArgumentParser(
        description="WebMontage - Static site montage generator using git history"
    )
    parser.add_argument(
        "repo",
        metavar="repository",
        help="The absolute path to the root of the git repository for the web page",
    )
    parser.add_argument(
        "index", metavar="index", help="The index file relative to the root of the repo"
    )
    return parser.parse_args()


def dhash(image, hash_size=8):
    # https://www.pyimagesearch.com/2017/11/27/image-hashing-opencv-python/
    resized = cv2.resize(image, (hash_size + 1, hash_size))
    diff = resized[:, 1:] > resized[:, :-1]
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])


class Git:
    def __init__(self, path):
        try:
            repo = Repo(path)
            self.client = repo.git
        except (InvalidGitRepositoryError, NoSuchPathError) as e:
            raise WebMontageError(f"No git repository found at {path}")

    def file_history(self, filename):
        try:
            commits = self.client.log(filename, pretty='format:"%h"', follow=True)
            commits = commits.replace('"', "").split("\n")
        except GitCommandError as e:
            raise WebMontageError(
                f'Error occurred finding commits. Make sure {self.path}/{filename} exists and has a commit history: > git log --pretty=format:"%h" --follow -- {filename}'
            )
        return reversed(commits)

    def checkout(self, commit):
        self.client.checkout(commit)

    def __enter__(self, master_branch="master"):
        self.master_branch = master_branch
        self.client.checkout(master_branch)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.checkout(self.master_branch)


class Browser:
    def __init__(self):
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("headless")
            self.driver = webdriver.Chrome(
                "chromedriver", chrome_options=chrome_options
            )
        except Exception:
            raise WebMontageError(
                'Unable to create headless Chrome instance. Make sure "chromedriver" is installed and is in the PATH'
            )

    def __enter__(self):
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()


def main():
    args = get_args()
    with tempfile.TemporaryDirectory() as tmp_dir:
        with Git(args.repo) as git, Browser() as browser:
            history = git.file_history(args.index)
            browser.get(f"file:///{args.repo}/{args.index}")
            images = {}
            for i, commit in enumerate(history):
                git.checkout(commit)
                browser.refresh()
                filename = f"{tmp_dir}/{i}.png"
                body = browser.find_element_by_tag_name("body")
                body.screenshot(filename)

                # Many commits won't have any visual difference. We only want those images that generate unique hashes
                image = cv2.imread(filename)
                image_hash = dhash(image)
                images[image_hash] = images.get(image_hash, image)

    for image in images.values():
        cv2.imshow("Image", image)
        time.sleep(5)
