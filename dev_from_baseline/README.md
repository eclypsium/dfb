
Welcome to the Backoffice repository.
This is a mono-repo structure where projects are in first level folders.

When creating a new project:
* Add a README file with a good explanation
* Configure the CI pipelines. The Backoffice repo uses a [Parent-Child pipeline](https://docs.gitlab.com/ee/ci/pipelines/downstream_pipelines.html#parent-child-pipelines), when adding a new project that has a pipeline follow that standard and create a trigger job in the main pipeline and the child pipeline within your project's directory.
* Ensure that all files have a trailing newline
* Configure your editor appropriately
    * newlines at end of file
    * spaces, no tabs
    * spell checker
* Add DFG as a reviewer to the code reviews
* Remember: make it pretty, make it work, make it fast.
* The Backoffice Repo uses [towncrier](https://github.com/twisted/towncrier) as changelog/release notes management tool. To make towncrier work in a monorepo like backoffice's one is necessary to put towncrier's toml configuration file of your project in the root and adding the flag `--config towncrier_your_project.toml` when calling towncrier (for more information check this [github issue](https://github.com/twisted/towncrier/issues/433)). When setting up the child pipeline of your project add towncrier `check` as one of the jobs to assure you're adding at least a fragment to your future merge requests.

When creating a new python project:
* Use pytest and 80% minimum coverage
* Use poetry
* Use typer for arguments parsing
* Use mypy and avoid type ```any```
* Use sphinx docstrings
* If it is a module, add it to the Gitlab package registry

# dev_from_baseline
Based in a json baseline file with previous number of issues, this script resolves if there are more findings after a sast tool analysis, useful for ci-pipelines.

Usage: ```$ dev-from-baseline --basefile [BASEFILE] --report-file [NEW_REPORT] [--generate] [--verbose]```

If `--generate` is present:
* `BASEFILE`, if the file doesn't exit, it will be created. If is it exists and if the
reports have new information, then it will be updated, else nothing happens
* `NEW_REPORT(s)` are the linter's output. You could add several reports at once, each one preceded
with the flag --report-file

If --generate is not present:
* `BASEFILE`, if the file doesn't exit, it will throw an error. If is it exists then will
show a table with the files that have more findings in the NEW_REPORT comparing with
the results stored in the baseline file, and the exit code will be 1 (for CI/CD pipelines).
If no files shows more findings compared with the baseline, the exit code will be 0 and
only the results stored in the baseline are shown.
* `NEW_REPORT(s)`, if the BASEFILE doesn't have an entry for the linter in this report, then it will
show a message to run the tool with the --generate flag to add it, else it will compared the
results with the ones stored in the BASEFILE, showing the files with more errors than before.
