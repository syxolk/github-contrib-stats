#!/bin/env python3
import argparse
import requests
from tqdm import tqdm

def main():
    args = parse_args()

    token = args.token
    stats = {}
    print("Get all issues...")
    issues, pull_requests = get_all_issues_and_pr(token, issues_url(args.owner, args.name))
    for i in tqdm(issues):
        issue = get_issue(token, i["url"])

        author_stats = stats.get(issue["author"], {"author": 0, "closed": 0, "pr": 0})
        author_stats["author"] += 1
        stats[issue["author"]] = author_stats

        closer_stats = stats.get(issue["closed_by"], {"author": 0, "closed": 0, "pr": 0})
        closer_stats["closed"] += 1
        stats[issue["closed_by"]] = closer_stats

    for pr in pull_requests:
        pr_stats = stats.get(pr["user"]["login"], {"author": 0, "closed": 0, "pr": 0})
        pr_stats["pr"] += 1
        stats[pr["user"]["login"]] = pr_stats

    for name in stats:
        print(name)
        print("\topened: {}".format(stats[name]["author"]))
        print("\tclosed: {}".format(stats[name]["closed"]))
        print("\tpr:     {}".format(stats[name]["pr"]))


def parse_args():
    parser = argparse.ArgumentParser(description="Github Stats: Issues and Pull Requests for each Contributor")
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


def get_issue(token, api_url):
    r = requests.get(api_url, headers={
        "Authorization": "token " + token
    }).json()
    return {
        "author": r["user"]["login"],
        "closed_by": r["closed_by"]["login"] if r["closed_by"] is not None else None,
    }


if __name__ == "__main__":
    main()
