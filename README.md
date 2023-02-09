# Welcome!
This is the home for our Python/FastAPI AWS backend for senior design. Please refer to the following sections for what you need.

# Getting Started

## Prerequisites
- Install [Python](https://www.python.org/).
- Install [Serverless Framework](https://www.serverless.com/).

```sh
# Install dependencies (Ubuntu)
sudo apt-get install python3.8 python3.8-venv

# Install Serverless CLI + plugins
npm install -g serverless
serverless plugin install -n serverless-python-requirements
```


## Dev Environment Setup
1. Clone repository.
2. Set up a Python virtual environment and install modules from `requirements.txt`.
3. Set up Serverless CLI with AWS credentials (ask Quikks1lver for credentials).

```sh
# Clone repository
git clone git@github.com:ContentWarnings/Backend.git
cd Backend

# Configure venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
python3 -m pip install -r requirements.txt

# Configure Serverless with AWS keys
serverless config credentials --provider aws --key <aws_key> --secret <aws_secret>
```

# How to Contribute
1. Create a new feature branch using your name. Example: `adam/bug-fix`.
2. Make relevant code changes in `src/`.
3. **Very important:** Test your code by spinning up the AWS resources in your testing stage! To do so, open `serverless.yaml`, and edit names for `stage`, DynamoDB tables, and `apiKey`. To deploy your changes, run `sls deploy`. Remember to revert `yaml` changes prior to PR.
4. Ensure you run the `black` command to format code prior to attempting a merge.
5. Add any new modules to `requirements.txt`.
6. Cite your sources! (see guide below)
7. Submit a pull request (PR), and ensure any testing/formatting pipelines pass. Fill out PR template fully, attaching images if necessary to help your reviewers.
8. Respond to other teammate's comments and merge in when approved.
9. Delete your feature branch (should automatically do so on GitHub), and start the process over again for new changes.

```sh
# Create new branch
git checkout -B adam/bug-fix

# Enter venv
source venv/bin/activate

# Run Black to make sure formatting is compliant.
black src/*

# Run Pytest tests
pytest

# Push to Git.
git add .
git commit -m "Push bug fix"
git push origin adam/bug-fix
```

## Local Development Guide

```sh
# (in project root)
python3 -m pip install gunicorn
python3 -m gunicorn src.main:app --worker-class uvicorn.workers.UvicornWorker
```

# Citation Guide

1. Ask yourself if the resource can be cited at all. If the resource is a tutorial, you can implicitly use the technique, but without a license, do not reference or use any code.
2. If referencing code using a permissive license (ex: MIT, Apache 2.0, etc.), cite via a comment in relevant code file(s). This can be as simple as a URL since we will cite more.
3. Create a full APA citation and attach to our senior design document bibliography.
4. This last step is if you use/reference code, not necessarily for general help: include the license copyright in `licenses_references/`, in the relevant file.

# Questions?
Reach out to Quikks1lver; he's happy to help!
