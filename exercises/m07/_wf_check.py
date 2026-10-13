"""Static checks for the CI workflow (bug04, bug05)."""
import re
import sys

import yaml

from _pyload import fail

wf = yaml.safe_load(open(f"{sys.argv[1]}/ci.yaml"))
jobs = wf["jobs"]
problems = []
for jname, job in jobs.items():
    for step in job.get("steps", []):
        run = step.get("run", "")
        if "${{ secrets." in run:
            problems.append(f"{jname}/{step.get('name')}: secret expression inlined into run:")
        if re.search(r"docker login[^\n]*\s(-p|--password)\s", run):
            problems.append(f"{jname}/{step.get('name')}: password passed as a CLI argument")
if "test" not in str(jobs["images"].get("needs", "")):
    problems.append("images: runs even when the test job fails (needs: test missing)")
for p in problems:
    print("problem:", p)
if problems:
    fail(f"{len(problems)} problem(s)")
print("OK")
