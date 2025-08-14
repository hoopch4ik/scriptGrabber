## Telegram Post Grabber Script

This script allows you to grab posts from Telegram channels and forward them to other channels or groups.

**Requirements:**

•   Python 3.0 or higher
•   Telegram account API ID and API HASH (see instructions below)

**Getting API ID and API HASH:**

1.  Go to [https://my.telegram.org/auth?to=apps](https://my.telegram.org/auth?to=apps)
2.  Log in with your Telegram account.
3.  Create a new app to obtain your `API_ID` and `API_HASH`.

**Important Note:** The first time you run the script, you will be prompted to enter your phone number, the code sent to your Telegram account, and your 2FA password if enabled.

## Configuration

Edit the configuration files located in the `./grabber/config` directory:

•   **`info_channels.txt`**: List of source channels.
•   **`to_channels.txt`**: List of destination channels.

**Format:**

•   One channel per line.
•   For private channels, enter the channel ID.  You can use a bot like [@UserInfoToBot](https://t.me/UserInfoToBot) to retrieve the channel ID.

## Installation and Usage (Windows)

1.  **Create a virtual environment:**
```python -m venv .venv  # or python3 -m venv .venv, or py -m venv .venv```

2.  Activate the virtual environment:
```.venv/Scripts/activate```

3.  Install dependencies:
```pip install -r requirements.txt```

4.  Run the script:
```python main.py```
