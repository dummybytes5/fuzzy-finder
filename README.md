# Fuzzy Framework Repository Finder

## Requirements

## Installation

1. Create virtual environment

```bash
python -m venv venv
```

1. Activate virtual environment

```bash
# On Windows PowerShell
venv/Scripts/activate
```

```bash
# On Linux/Mac
source venv/bin/activate

```

## Installing requirments

```bash
pip install -r requirements.txt
```

## Usage

1. Set your GitHub API token as an environment variable

```bash
# create .env file where the scrapper.py is and add key like this
GITHUB_TOKEN="key goes here"
```

## Or just copy and paste the following in your mac or windows terminal

```bash
# On Windows PowerShell
$env:GITHUB_TOKEN="your_github_token"

# On Linux/Mac
export GITHUB_TOKEN="your_github_token"
```

2. Run the script:

```bash
python scrapper.py
```

- Result will be saved in a txt file
