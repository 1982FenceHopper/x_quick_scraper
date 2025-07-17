# Quick X Scraper

## Requirements

Python >= 3.11.9

## Quick Start

First, pull the repository

```bash
git pull --depth=1 https://github.com/1982FenceHopper/x_quick_scraper
```

Make sure to populate a .env with these values

```toml
USERNAME="example_user" /* Username */
EMAIL="user@example.com" /* Email */
PASSWORD="somepass" /* Password */
```

Then, populate a new file called `_users.txt`, this is where you define which account you want to pull from, and how much you want to pull (Handle always without the @ sign), separated by newlines

```txt
handle:count
```

For example

```txt
_someonesaccount_:50
helloimaguy:250
```

Setup the environment

```bash
# Windows
.\setup.ps1

# Linux
./setup.sh
```

Then simply run the following command (.ps1 on Windows, .sh on Linux)

```bash
# Windows
.\run.ps1

# Linux
./run.sh
```

Subsequent runs only need you to execute the run script (unless you delete the env folder that was created, in that case, run the setup script before)

```bash
# Windows
.\run.ps1

# Linux
./run.sh
```

CSV files should be outputted to the 'output/' folder in your current working directory

## License

```
This project is licensed under the MIT license, read LICENSE for more details
```
