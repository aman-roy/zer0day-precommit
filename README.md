# Zer0Day Pre-commit hook

This repository provides an easy-to-install **pre-commit hook** that automates the generation of a Software Bill of Materials (SBOM), parses open-source libraries, and checks for vulnerabilities using the **Zer0Day platform**. The hook ensures that vulnerabilities are detected before commits are made to your repository.

Follow the instructions below to set this up in your own project using a single installation script.

> [!CAUTION]
> The backend API is not deployed, so it won't function as expected.

---

### Features

- **Automated SBOM generation** using **Syft**.
- **Open-source library parsing** and vulnerability checks.
- **Zer0Day platform integration** to alert you of vulnerabilities in your dependencies.
- **Simple installation** into any Git repository with just one command.

### Prerequisites

- **Git** installed on your machine.
- **Pre-commit** installed on your machine (Instruction given below).
- **Python 3** installed for running the SBOM parser.
- **Syft** installed (automatically installed by the script if not already present).

---

### Installation Instructions

#### Step 1: Navigate to Your Project's Root Directory

Before running the installation script, ensure you are in the root directory of your Git project and pre-commit is also installed.

```bash
cd /path/to/your/project
pip install pre-commit
```

#### Step 2: Run the Installation Script

Run the following command to install the pre-commit hook in your project. This will add the SBOM pre-commit repository as a submodule, install the necessary files, and ensure the pre-commit hook is active.

```bash
curl -s https://raw.githubusercontent.com/aman-roy/zer0day-precommit/main/install_hooks.sh | bash
```

#### Step 3: Set Environment Variable for setting up token

##### For linux/Mac
```
export ZER0DAY_API_TOKEN="your_api_token_here"
```

##### For Windows
```
set ZER0DAY_API_TOKEN=your_api_token_here
```

#### Step 4: Make a Commit

Once the pre-commit hook is installed, you can commit as usual:

```bash
git add .
git commit -m "Test SBOM pre-commit hook"
```

---

### Updating the Pre-Commit Hook

If the pre-commit hook or parser script gets updated in the `zer0day-precommit` repository, you can update the hook in your own project by running the following command:

```bash
git submodule update --remote sbom-precommit
```

This will pull in the latest changes from the `sbom-precommit` repository.

---

### Removing the Pre-Commit Hook

If you ever want to remove the pre-commit hook from your project, you can do so by running the following commands:

1. Remove the `.git/hooks/pre-commit` file:

```bash
rm .git/hooks/pre-commit
```

2. Remove the `sbom-precommit` submodule:

```bash
git submodule deinit -f sbom-precommit
git rm -f sbom-precommit
rm -rf .git/modules/sbom-precommit
```

---

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

### Contributing

If you’d like to contribute to this project or suggest improvements, feel free to open an issue or submit a pull request.