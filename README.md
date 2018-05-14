# Github Contributor Stats

`github-contributor-stats` is a small Python script that collects statistics
on how many issues were opened and closed as well as opened pull requests
for every contributor for a specific repository.

## Requirements
Python 3

```
sudo pip3 install -r requirements
```

## Usage
```
usage: github-contrib-stats.py [-h] --token TOKEN --owner OWNER --name NAME

Github Contrib Stats: Count issues and pull requests for each contributor

optional arguments:
  -h, --help     show this help message and exit
  --token TOKEN  GitHub API token
  --owner OWNER  Repository owner
  --name NAME    Repository name
```

## How to get a GitHub API token
Go to https://github.com/settings/tokens and click on "Generate new token".
Select the "repo" scope to allow the script access to private repos.

## Why do I need a GitHub API token?
GubHub API v3 allows
[only 60 requests per hour](https://developer.github.com/v3/#rate-limiting)
for unauthenticated requests.
That's not enough because this script has to perform a request per issue
to get the information on who closed it.
