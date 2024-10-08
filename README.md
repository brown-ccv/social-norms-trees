# Social Norms Trees
Experiments on teaching social norms to autonomous agents.

## Developer Setup

Prerequisites:
- Python 3.11+
- git

Clone the repository:
```bash
git clone https://github.com/brown-ccv/social-norms-trees
```

Enter the repository directory:
```bash
cd social-norms-trees
```

Create a virtual environment:
```bash
python3 -m venv .venv
```

Activate the environment:
```bash
. .venv/bin/activate
```

Install the package in editable mode for development:
```bash
pip install --editable ".[test]"
```

Run the tests:
```bash
pytest
```

Run the example experiment:
```bash
social-norms-trees example-experiments/entering-a-room.json
```

