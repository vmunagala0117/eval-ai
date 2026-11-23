"""Execute lessons in fresh kernels using this interpreter; save local outputs."""
from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import AsyncKernelManager

class ProjectKernelManager(AsyncKernelManager):
    def format_kernel_cmd(self, extra_arguments=None):
        return [sys.executable, "-m", "ipykernel_launcher", "-f", self.connection_file] + (extra_arguments or [])

root = Path(__file__).resolve().parents[1]
output = root / "reports" / "executed"
output.mkdir(parents=True, exist_ok=True)
for path in sorted((root / "notebooks").glob("*.ipynb")):
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    client = NotebookClient(notebook, kernel_manager_class=ProjectKernelManager,
                            timeout=120, startup_timeout=20, allow_errors=False,
                            resources={"metadata": {"path": str(root)}})
    try:
        client.execute()
    finally:
        nbformat.write(notebook, output / path.name)
    print(f"Executed {path.name}")
