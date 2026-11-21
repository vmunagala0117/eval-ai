# VS Code setup

Choose one operating environment per checkout. Recommended: Ubuntu WSL if already installed. Native Windows PowerShell is also supported by the starter. Use Python 3.11 or 3.12. Do not share a `.venv` between Windows and WSL.

## Ubuntu WSL

Open Ubuntu. Install prerequisites if missing:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git
```

Keep the checkout in the Linux home directory. While the starter PR is unmerged:

```bash
mkdir -p ~/projects
cd ~/projects
git clone --branch project/lesson-00 https://github.com/vmunagala0117/eval-ai.git
cd eval-ai
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
python -m ipykernel install --user --name eval-ai-wsl --display-name "Python (eval-ai WSL)"
code .
```

Confirm VS Code shows a WSL connection. Install the Microsoft Python and Jupyter extensions in that WSL environment.

## Windows PowerShell

Install Python 3.12, Git, and VS Code first. Run from your intended projects folder:

```powershell
git clone --branch project/lesson-00 https://github.com/vmunagala0117/eval-ai.git
cd eval-ai
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m ipykernel install --user --name eval-ai-windows --display-name "Python (eval-ai Windows)"
code .
```

Explicit interpreter paths work without changing PowerShell execution policy. Activation is optional: `.\.venv\Scripts\Activate.ps1`. If policy blocks activation, continue using the explicit Python path.

## Select interpreter AND notebook kernel

1. Open the repository folder in VS Code.
2. Run **Python: Select Interpreter** and choose this checkout's `.venv`.
3. Open `notebooks/00_success_contract.ipynb`.
4. Use **Select Kernel** and choose the matching `.venv` / registered eval-ai kernel.
5. Run the first cell. `sys.executable` must point into this checkout's `.venv`.
6. Select **Run All**. Expected verdicts: pass, fail, fail; a missing review is unverifiable.

## Verify

WSL, with the environment activated:

```bash
python -m pytest -q
python scripts/run_notebooks.py
```

PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/run_notebooks.py
```

Executed outputs go into ignored `reports/executed/`. Source notebooks contain no saved outputs. The direct dependencies are pinned; this is not yet a complete transitive cross-platform lock.

If the notebook cannot import `finance_evals`, install `-e .` using the exact interpreter selected as its kernel. If you move the checkout, recreate its environment and re-register the kernel. After the PR is merged, new checkouts can clone the default branch.

No Azure deployment or key is required for Lesson 00. Live Azure integration will be configured in the agent lesson; never commit credentials or place them in notebook cells or outputs.

References: [VS Code Python environments](https://code.visualstudio.com/docs/python/environments), [Jupyter kernel selection](https://code.visualstudio.com/docs/datascience/jupyter-kernel-management).
