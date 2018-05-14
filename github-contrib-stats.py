#!/bin/env python3
import argparse
import requests
from tqdm import tqdm


FORMAT_STRING = "{name: <{fill}}  {author: >6}  {closed: >6}  {pr: >5}"


def main():
    args = parse_args()

    token = args.token
    stats = Stats()
    print("Get all issues...")
    issues, pull_requests = get_all_issues_and_pr(token, issues_url(args.owner, args.name))

    process_issues(token, issues, stats)
    process_pull_requests(pull_requests, stats)

    print(stats)


def parse_args():
    parser = argparse.ArgumentParser(description="Github Contrib Stats: Count issues and pull requests for each contributor")
    parser.add_argument("--token", required=True, help="GitHub API token")
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--name", required=True, help="Repository name")
    return parser.parse_args()


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


def process_issues(token, issues, stats):
    for i in tqdm(issues):
        process_single_issue(token, i["url"], stats)


def process_single_issue(token, api_url, stats):
    r = requests.get(api_url, headers={
        "Authorization": "token " + token
    }).json()

    stats.count_action(r["user"]["login"], "author")
    if r["closed_by"] is not None:
        stats.count_action(r["closed_by"]["login"], "closed")


def process_pull_requests(pull_requests, stats):
    for pr in pull_requests:
        stats.count_action(pr["user"]["login"], "pr")


class Stats:
    def __init__(self):
        self._data = {}

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

    def __str__(self):
        longest_name_len = max((len(x) for x in self._data))

        lines = []
        lines.append(FORMAT_STRING.format(
            name="LOGIN",
            author="OPENED",
            closed="CLOSED",
            pr="PR",
            fill=longest_name_len,
        ))
        for name in self._data:
            lines.append(FORMAT_STRING.format(
                name=name,
                author=self.get_count(name, "author"),
                closed=self.get_count(name, "closed"),
                pr=self.get_count(name, "pr"),
                fill=longest_name_len,
            ))
        return "\n".join(lines)


if __name__ == "__main__":
    main()
