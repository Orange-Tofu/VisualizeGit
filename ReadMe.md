# vgit – Visual Git Educational Tool

## License
GPL-3.0-or-later

## Overview
vgit is a free and open-source interactive visualizer for Git commands.
It helps you see what Git is doing under the hood — staging, committing, fetching, amending — using terminal animations.

This project is designed for students, educators, and anyone learning Git.

## Features
* Visualize common Git operations such as status, fetch, and commit with animated terminal graphics.
* See how branches, commits, and staging areas change over time.
* Consistent, easy-to-understand animations.
* Runs entirely in the terminal — no extra GUI tools required.

## Installation
Install vgit globally via pip:

```bash
pip install vgit
```

Or, install from source:

```bash
git clone https://github.com/Orange-Tofu/VisualizeGit
cd vgit
pip install .
```

This installs the vgit command globally.

# Usage

## Getting Started
Once installed, you can use vgit by running the following command:

```bash
vgit status
```

## Other examples:

```bash
vgit fetch
vgit commit -m "Add new feature"
vgit commit --amend --no-edit
```

## During development (without installing):

```bash
python cli.py status
python cli.py fetch
python cli.py commit -m "message"
```

# Development Setup

## Getting Started
To set up vgit for development, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/Orange-Tofu/VisualizeGit
   cd vgit
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run in development mode:
   ```bash
   python cli.py status
   ```
4. Make your changes and test them live.


# Contributing

We welcome contributions! If you'd like to add new Git command animations, improve existing ones, or fix bugs, feel free to fork and submit a pull request.

## Steps to Contribute

1. Fork the repo on GitHub.
2. Create a feature branch
3. Commit your changes.
4. Push to your fork.
5. Open a Pull Request with a clear description.

## License

This project is licensed under the [GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.en.html) license. You are free to use, modify, and redistribute it under the terms of this license. This ensures the software remains free and open-source.
