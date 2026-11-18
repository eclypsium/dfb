import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ISTARI = Path(__file__).resolve().parents[1] / "istari_linters" / "istari.py"
TOOLS = ["shellcheck", "shellcheck-sarif", "hadolint", "bandit", "pylint", "mypy", "lizard",
         "njsscan", "eslint", "npm", "golangci-lint", "docker"]
HOSTILE = ["x;touch MARKER;#", "$(touch MARKER)", "`touch MARKER`", "x';touch MARKER;'",
           'x";touch MARKER;"', "x|touch MARKER", "x&&touch MARKER", "a -x", "[ab]", "*"]
# backoffice has no dockerfile strategy: use "java" there instead of "dockerfile".
LANGUAGES = ["shell", "dockerfile", "python", "go", "javascript"]
PER_DIRECTORY = {"shell", "dockerfile"}


@pytest.fixture(name="stubs")
def fixture_stubs(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "argv.jsonl"
    for tool in TOOLS:
        stub = bin_dir / tool
        stub.write_text(
            f"#!{sys.executable}\n"
            "import json, sys\n"
            f"open({str(log)!r}, 'a').write(json.dumps(sys.argv) + '\\n')\n"
            "print('[]')\n"
        )
        stub.chmod(0o755)
    return bin_dir, log


@pytest.mark.parametrize("language", LANGUAGES)
def test_hostile_names_never_reach_a_shell(tmp_path, stubs, language):
    bin_dir, log = stubs
    repo = tmp_path / "repo"
    for name in HOSTILE:
        folder = repo / "src" / name
        folder.mkdir(parents=True)
        for file_name in ("run.sh", "Dockerfile", "a.py", "a.go", "a.js", "A.java"):
            (folder / file_name).write_text("")
    before = set(repo.rglob("*"))
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}
    subprocess.run([sys.executable, str(ISTARI), "-l", language, "-f", "src", "-r"],
                   cwd=repo, env=env, check=False, timeout=120)

    assert not list(tmp_path.rglob("MARKER")), "a directory name ran as a command"
    new_files = [p for p in repo.rglob("*") if p not in before and p.is_file()]
    assert all(p.parent == repo / "linters_results" for p in new_files), new_files
    if language in PER_DIRECTORY:
        args = [arg for line in log.read_text().splitlines() for arg in json.loads(line)]
        for name in HOSTILE:
            assert any(arg.startswith(f"src/{name}/") for arg in args), name
