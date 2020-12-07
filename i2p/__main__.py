from re import RegexFlag
from sys import path
from github import Github
from os import chdir, environ, system
from argparse import ArgumentParser
from slugify import slugify
import re
import subprocess

parser = ArgumentParser()

parser.add_argument("-r",
                    "--repo",
                    default="Financial-Times/origami")

parser.add_argument("-i",
                    "--issue",
                    required=True,
                    type=int)

# TODO get repo from this
parser.add_argument("-d",
                    "--directory",
                    help="directory of checked out repo",
                    required=True)

args = parser.parse_args()

access_token = environ.get("GITHUB_ACCESS_TOKEN")
if not access_token:
    raise RuntimeError("You don't have a GITHUB_ACCESS_TOKEN")

github = Github(access_token)

repo = github.get_repo(args.repo)
issue = repo.get_issue(args.issue)

title = re.sub(
    "proposal:? ",
    "",
    issue.title,
    flags=RegexFlag.IGNORECASE
)

slug = slugify(title)
body = f"""# {title}
{issue.body}
"""

branch = f"proposals/{slug}"
filename=f"0000-{slug}.md".replace("proposal-", "")
email=issue.user.email
user=issue.user.name
if not email:
    email = user.replace(" ", ".").lower() + "@ft.com"
author=f"{user} <{email}>"
date=issue.created_at.isoformat()
commit_env = {
    "GIT_COMMITTER_NAME": user,
    "GIT_COMMITTER_EMAIL": email,
    "GIT_COMMITTER_DATE": date,
    "GIT_AUTHOR_NAME": user,
    "GIT_AUTHOR_EMAIL": email,
    "GIT_AUTHOR_DATE": date,

}

chdir(args.directory)
with open(f"proposals/accepted/{filename}", "w+") as file:
    file.write(body)

system(f"git branch {branch}")
system(f"git checkout {branch}")
system(f"git add proposals")
subprocess.call(["git", "commit", "--author", author, "--date", date, "-m", issue.title], env=commit_env)
system(f"git push")
system(f"git checkout main")
pullbody = f"""From #{issue.number}.

see [rendered proposal](https://github.com/{args.repo}/blob/{branch}/proposals/accepted/{filename})
"""

comments = list(issue.get_comments())

if len(comments):
    pullbody += "\n\n## comments from issue\n\n"

for comment in issue.get_comments():
    pullbody += "---\n\n"
    pullbody += f"**{comment.user.login}** "
    pullbody += f"_on {comment.created_at.isoformat()}_\n\n"
    pullbody += comment.body
    pullbody += "\n\n---\n\n"

pull = repo.create_pull(issue.title,
                        body=pullbody,
                        base="main",
                        head=branch)


issue.edit(state="closed")
for label in issue.labels:
    pull.add_to_labels(label)

print(issue.comments_url)
print(f"#{pull.number}")
