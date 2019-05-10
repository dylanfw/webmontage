import argparse
import os
import sys
import time
import tempfile

import cv2
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
import numpy as np
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
        "index",
        metavar="index",
        help="The index file relative to the root of the repo, i.e. 'index.html'",
    )
    parser.add_argument(
        "-f",
        "--file",
        help="If given, only commits that affect this file will be considered, i.e. 'main.css'",
    )
    parser.add_argument(
        "--browser-width",
        type=int,
        default=1440,
        help="Width of the browser window to load the web page in",
    )
    parser.add_argument(
        "--browser-height",
        type=int,
        default=1800,
        help="Height of the browser window to load the web page in",
    )
    parser.add_argument(
        "--video-width",
        type=int,
        default=640,
        help="Width of the slideshow window to display the montage in",
    )
    parser.add_argument(
        "--video-height",
        type=int,
        default=800,
        help="Height of the slideshow window to display the montage in",
    )
    return parser.parse_args()


def dhash(image, hash_size=8):
    # https://www.pyimagesearch.com/2017/11/27/image-hashing-opencv-python/
    resized = cv2.resize(image, (hash_size + 1, hash_size))
    diff = resized[:, 1:] > resized[:, :-1]
    return sum(2 ** i for (i, v) in enumerate(diff.flatten()) if v)


class Git:
    def __init__(self, path):
        try:
            repo = Repo(path)
            self.client = repo.git
        except (InvalidGitRepositoryError, NoSuchPathError) as e:
            raise WebMontageError(f"No git repository found at {path}")

    def history(self, filename=None):
        try:
            if filename:
                commits = self.client.log(filename, pretty='format:"%h"', follow=True)
            else:
                commits = self.client.log(pretty='format:"%h"')
        except GitCommandError as e:
            raise WebMontageError(
                f'Error occurred finding commits. Make sure {self.path}/{filename} exists and has a commit history: > git log --pretty=format:"%h" --follow -- {filename}'
            )
        commits = commits.replace('"', "").split("\n")
        self.commits = reversed(commits)
        return self.commits

    def checkout(self, commit):
        self.client.checkout(commit)

    def __enter__(self, master_branch="master"):
        self.master_branch = master_branch
        self.client.checkout(master_branch)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.checkout(self.master_branch)


class Browser:
    def __init__(self, width, height):
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("headless")
            self.driver = webdriver.Chrome(
                "chromedriver", chrome_options=chrome_options
            )
            self.driver.set_window_size(width, height)
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
        with Git(args.repo) as git, Browser(
            args.browser_width, args.browser_height
        ) as browser:
            history = list(git.history(filename=args.file))
            print(f"Searching through {len(history)} commits...")
            browser.get(f"file:///{args.repo}/{args.index}")
            images = {}
            max_width, max_height = 0, 0
            for i, commit in enumerate(history):
                git.checkout(commit)
                browser.refresh()
                filename = f"{tmp_dir}/{i}.png"
                browser.save_screenshot(filename)

                # Many commits won't have any visual difference. We only want those images that generate unique hashes
                image = cv2.imread(filename)
                image = cv2.resize(image, (args.video_width, args.video_height))
                image_hash = dhash(image)
                images[image_hash] = images.get(image_hash, image)

    print(f"Found {len(images)} visually distinct commits")
    print("Preparing slideshow...")
    previous_image = np.full((args.video_height, args.video_width, 3), 255, np.uint8)
    cv2.namedWindow("WebMontage")
    cv2.moveWindow("WebMontage", 0, 0)
    cv2.imshow(
        "WebMontage",
        cv2.putText(
            previous_image,
            "Press any key to begin...",
            (50, 50),
            cv2.FONT_HERSHEY_TRIPLEX,
            1,
            2,
        ),
    )
    cv2.waitKey(0)
    for i, image in enumerate(images.values()):
        print(f"Displaying version {i+1}/{len(images)}")
        for alpha in range(1, 11):
            alpha /= 10.0
            cv2.imshow(
                "WebMontage",
                cv2.addWeighted(image, alpha, previous_image, 1 - alpha, 0.0),
            )
            cv2.waitKey(100)
        cv2.waitKey(3000)
        previous_image = image
    cv2.waitKey(3000)
    cv2.destroyAllWindows()
