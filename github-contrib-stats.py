#!/usr/bin/env python3
import argparse
import requests
from tqdm import tqdm
import sys
import os


FORMAT_STRING = "{name: <{fill}}"

def main():
    args = parse_args()

    stats = Stats(["OPENED", "CLOSED", "PR"] if args.show_closed else ["OPENED", "PR"])
    issues, pull_requests = get_all_issues_and_pr(args.token, issues_url(args.owner, args.name))

    process_issues(issues, stats)
    if args.show_closed:
        process_closed_issues(args.token, issues, stats)
    process_pull_requests(pull_requests, stats)

    stats.dump()


def parse_args():
    parser = argparse.ArgumentParser(description="Github Contrib Stats: Count issues and pull requests for each contributor")
    parser.add_argument("--token",
        help="GitHub API token. Can also be set as an environment variable: GITHUB_API_TOKEN",
        default=os.environ.get("GITHUB_API_TOKEN"))
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--name", required=True, help="Repository name")
    parser.add_argument("--show-closed", action="store_true", help="Count closed issues. This may be really SLOW.")
    args = parser.parse_args()

    if not args.token:
        parser.print_usage()
        sys.exit(1)

    return args


def issues_url(owner, repo):
    return "https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=100".format(
        owner=owner,
        repo=repo)


def get_all_issues_and_pr(token, api_url):
    has_more_pages = True
    issues = []
    pull_requests = []
    while has_more_pages:
        r = requests.get(api_url, params={
            "state": "all",
        }, headers={
            "Authorization": "token " + token
        })
        json = r.json()
        issues.extend([i for i in json if "pull_request" not in i])
        pull_requests.extend([i for i in json if "pull_request" in i])
        if "next" in r.links:
            api_url = r.links["next"]["url"]
        else:
            has_more_pages = False
    return (issues, pull_requests)


def process_issues(issues, stats):
    for i in issues:
        stats.count_action(i["user"]["login"], "OPENED")


def process_closed_issues(token, issues, stats):
    for i in tqdm(issues):
        process_single_issue(token, i["url"], stats)


def process_single_issue(token, api_url, stats):
    r = requests.get(api_url, headers={
        "Authorization": "token " + token
    }).json()

    if r["closed_by"] is not None:
        stats.count_action(r["closed_by"]["login"], "CLOSED")


def process_pull_requests(pull_requests, stats):
    for pr in pull_requests:
        stats.count_action(pr["user"]["login"], "PR")


class Stats:
    def __init__(self, columns):
        self._data = {}
        self._columns = columns

    def count_action(self, user, action):
        if user not in self._data:
            self._data[user] = {}
        if action not in self._data[user]:
            self._data[user][action] = 0
        self._data[user][action] += 1

    def get_count(self, user, action):
        if user not in self._data:
            return 0
        if action not in self._data[user]:
            return 0
        return self._data[user][action]

    def dump(self):
        longest_name_len = max((len(x) for x in self._data))

        lines = []
        print(FORMAT_STRING.format(
            name="LOGIN",
            fill=longest_name_len,
        ), end="")
        for c in self._columns:
            print("  {: >6}".format(c), end="")
        print()
        for name in self._data:
            print(FORMAT_STRING.format(
                name=name,
                fill=longest_name_len,
            ), end="")
            for c in self._columns:
                print("  {: >6}".format(self.get_count(name, c)), end="")
            print()


if __name__ == "__main__":
    main()
