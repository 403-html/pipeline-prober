# pipeline-prober

This script analyzes GitHub workflow runs for a specified repository and workflow, identifying the most common actions that cause failures. It uses the GitHub CLI (`gh`) to fetch workflow details and runs, and processes them to determine failure reasons.

## Features

- Fetches workflow ID based on the workflow name.
- Retrieves the most recent workflow runs up to a specified limit.
- Analyzes the workflow runs to identify failed steps.
- Reports the most common failure reasons.

## Development

### Prerequisites

- Python 3.12+
- venv
- pip
- git

### Setup

```bash
$ git clone <repo>
# Clone the repository

$ cd <repo>
# Change directory to the repository

$ source prober/bin/activate
# Activate the virtual environment

$ pip install -r requirements.txt
# Install dependencies
```

### Test

```bash
$ python3 -m unittest tests/*.py
# Run all tests
```

## Run

```bash
$ python3 prober.py --help
# Show help, usage and options
```

### Sample run

```bash
$ python3 prober.py --owner <owner> --repo <repo> --workflow "<workflow name>"
# Run the prober
```

### Output

```bash
------------------
Most common failure reasons:
Install Dependencies: 5
Run Tests: 3
Build Project: 2
```

## License

MIT
