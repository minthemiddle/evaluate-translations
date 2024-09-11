# Translation Review Tool

This tool is designed to review and manage translations for JSON files. It includes two scripts: `review-translations-by-v-cn.py` and `review-translations-by-v-eu.py`. These scripts help in checking and reviewing translations interactively.

## Installation

### Windows

1. **Install Python**: Download and install Python from the [official website](https://www.python.org/downloads/windows/). Make sure to check the box that says "Add Python to PATH" during installation.

2. **Install Dependencies**: Open Command Prompt and run the following commands:
   ```bash
   pip install click
   pip install sqlite3
   ```

3. **Clone the Repository**: Clone the repository to your local machine using Git:
   ```bash
   git clone https://github.com/minthemiddle/evaluate-translations
   cd yourrepository
   ```

### macOS

1. **Install Python**: macOS comes with Python pre-installed. If you need to update it, you can install the latest version using Homebrew:
   ```bash
   brew install python
   ```

2. **Install Dependencies**: Open Terminal and run the following commands:
   ```bash
   pip install click
   pip install sqlite3
   ```

3. **Clone the Repository**: Clone the repository to your local machine using Git:
   ```bash
   git clone https://github.com/minthemiddle/evaluate-translations
   cd yourrepository
   ```

### Linux

1. **Install Python**: Most Linux distributions come with Python pre-installed. If not, you can install it using your package manager. For example, on Ubuntu:
   ```bash
   sudo apt-get update
   sudo apt-get install python3
   ```

2. **Install Dependencies**: Open Terminal and run the following commands:
   ```bash
   pip install click
   pip install sqlite3
   ```

3. **Clone the Repository**: Clone the repository to your local machine using Git:
   ```bash
   git clone https://github.com/minthemiddle/evaluate-translations
   cd evaluate-translations
   ```

## Usage

### review-translations-by-v-cn.py

To check and review translations interactively, run the following command:
```bash
python review-translations-by-v-cn.py --folder_path /path/to/json/files --interactive --lang en
```

### review-translations-by-v-eu.py

To review translations for specified languages, run the following command:
```bash
python review-translations-by-v-eu.py --folder /path/to/json/files --to en,es
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for more details.
