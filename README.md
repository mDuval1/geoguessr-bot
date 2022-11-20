# Requirements

Install Chrome webdriver, place the executable in `/usr/local/bin/chromedriver`.

# Installation

Install python dependencies

```
conda create -n geoguessr python=3.10
conda activate geoguessr
pip install -r requirements.txt
```

Launch a session, use a cookie manager to get the following cookies from your computer.

Write a file `cookies.json` at the root

```
{
  "G_ENABLED_IDPS": "google",
  "_ncfa": <long character string>,
  "devicetoken": <~10 character string>
}
```

# Usage

`python main.py`