# Welcome!
This is the home for our Python/FastAPI AWS backend for senior design. Please refer to the following sections for what you need.

# Getting Started

## Prerequisites
- Install [Python](https://www.python.org/).
- Install [Serverless Framework](https://www.serverless.com/).

## Dev Environment Setup
1. Clone repository.
2. Set up a Python virtual environment and install modules from `requirements.txt`.
3. Set up Serverless CLI with AWS credentials (ask Quikks1lver for credentials).

# How to Contribute
1. Create a new feature branch using your name. Example: `adam/bug-fix`.
2. Make relevant code changes in `src/`.
3. **Very important:** Test your code by spinning up the AWS resources in your testing stage! To do so, open `serverless.yaml`, and edit `stage`. Example: `adam-dev`. To deploy your changes, run `sls deploy`. Remember to remove your stage's name and replace with `prod` prior to a pull request.
4. Ensure you run the `black` command to format code prior to attempting a merge.
5. Submit a pull request (PR), and ensure any testing/formatting pipelines pass. Fill out PR template fully, attaching images if necessary to help your reviewers.
6. Respond to other teammate's comments and merge in when approved.
7. Delete your feature branch (should automatically do so on GitHub), and start the process over again for new changes.

# Citation Guide

1. Ask yourself if the resource can be cited at all. If the resource is a tutorial, you can implicitly use the technique, but without a license, do not reference or use any code.
2. If referencing code using a permissive license (ex: MIT, Apache 2.0, etc.), cite via a comment in relevant code file(s). This can be as simple as a URL since we will cite more.
3. Create a full APA citation and attach to our senior design document bibliography.
4. This last step is if you use/reference code, not necessarily for general help: include the license copyright in our GitHub Wiki section, in the relevant file.

# Questions?
Reach out to Quikks1lver; he's happy to help!