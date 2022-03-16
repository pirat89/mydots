#!/usr/bin/python3

import os
import socket
import sys

from github import Github

GH_TOKEN='<your-token>'

class AuthenticationError(Exception):
    pass


class UserStats(object):
    """
    """
    def __init__(self, login):
        self.login = login
        self.reviews = 0
        self.comments = 0
        self.merges = 0
    def pretty_print_stats(self):
        print('====================')
        print('USER: {}'.format(self.login))
        print('  Reviews : {}'.format(self.reviews))
        print('  Comments: {}'.format(self.comments))
        print('  Merges  : {}'.format(self.merges))
        print('====================')


class GithubPullStats(object):
    """
    """

    def __init__(self, pull):
        self._pull = pull
        print("[INFO] Init pull: {}".format(pull))
        print("[INFO] Get reviews: {}".format(pull))
        self._reviews =  [review for review in self._pull.get_reviews()]
        print("[INFO] Get comments: {}".format(pull))
        self._comments = [comment for comment in self._pull.get_comments()]
        self.author = self._pull.user.login
        print("[INFO] Setup rws: {}".format(pull))
        self.reviewers = set([review.user for review in self._reviews])
        print("[INFO] Setup commentators: {}".format(pull))
        self.commentators = set([comm.user for comm in self._comments])

    def get_reviewers(self):
        return self.reviewers

    def get_commentators(self):
        return self.commentators

    def is_merged(self):
        return self._pull.is_merged()

    def merged_by(self):
        if self.is_merged():
            return self._pull.merged_by.login
        return None


class GithubRepoStats(object):
    """
    TODO
    """

    def _get_pulls(self):
        return {pr.number:GithubPullStats(pr) for pr in self._repo.get_pulls(state='all')}

    def _get_issues(self):
        raise NotImplemented("This has not been implemented yet..")

    def _calc_users_stats(self):
        users = {}
        timeout_counter = 0

        def __calculation(pull):
            for user in pull.get_reviewers():
                username = user.login
                if username not in users:
                    users[username] = UserStats(username)
                users[username].reviews += 1
            for user in pull.get_commentators():
                username = user.login
                if username not in users:
                    users[username] = UserStats(username)
                users[username].comments += 1
            username = pull.merged_by()
            if username:
                if username not in users:
                    users[username] = UserStats(username)
                users[username].merges += 1

        try:
            for pull_number,pull in self._pulls.items():
                try:
                    print("[INFO] Calculation pull: {}".format(pull_number), file=sys.stderr)
                    __calculation(pull)
                except socket.timeout as e:
                    print("[ERROR] Socket nested timeout hit: {}".format(e), file=sys.stderr)
                    if timeout_counter >= 3:
                        break
                    timeout_counter += 1
        except socket.timeout as e:
            print("[ERROR] Socket timeout hit: {}".format(e), file=sys.stderr)
        return users


    def __init__(self, repo):
        print("[INFO] initialisation GHRS: {}".format(repo), file=sys.stderr)
        self._repo = repo
        print("[INFO] Getting pulls GHRS: {}".format(repo), file=sys.stderr)
        self._pulls = self._get_pulls()
        print("[INFO] Calculation begins GHRS: {}".format(repo), file=sys.stderr)
        self.users = self._calc_users_stats()


class GithubStats(object):
    """
    Make easier collecting of statistics about the user's work.

    Just a class to be able to collect some additional information about the
    authenticated user or about events in repositories to which user has
    access.
    """

    def __init__(self, access_token=None):
        if not access_token:
            raise ValueError("The access_token must be specified.")
        self.client = Github(login_or_token=GH_TOKEN)
        self._user = self.client.get_user()
        if self._user.login is None:
            raise AuthenticationError("Cannot authenticate to the Github.")
        self._repos = {repo.full_name:repo for repo in self.client.get_user().get_repos()}
        self._orgs = {org.login:org for org in self._user.get_orgs()}

    def reload(self):
        """
        Reload all cached data.
        """
        raise NotImplemented("This has not been implemented yet..")

    def get_repos(self):
        return self._repos

    # TODO: think just about list of strings and work all the time with repos
    # # # # only
    def get_orgs(self):
        return self._orgs

    def get_org_repos(self, org_name):
        return {repo.name:repo for repo in self.get_orgs()[org_name].get_repos()}


gstat = GithubStats(access_token=GH_TOKEN)
oamg_repos = gstat.get_org_repos('<org-repos>')
repostats = {}
for reponame,repo in oamg_repos.items():
    repostats[reponame] = GithubRepoStats(repo)

for st in repostats.values():
    print("#######################################")
    for user in st.users:
        user.pretty_print_stats()

