import argparse
import glob
import hashlib
import os
import shlex
import shutil
import sys
import subprocess
import tarfile
import tempfile
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Optional, cast, Final
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent))
from linter_versions import LINTER_CHECKSUMS, LINTER_VERSIONS

# pylint: disable=too-few-public-methods

logging.basicConfig(level=logging.INFO)

@dataclass
class LinterArgs:
    exclude: List[str] = field(default_factory=list)
    recursive: bool = field(default=False)
    install: bool = field(default=False)


class LinterInterface(ABC):
    @abstractmethod
    def run_linter(self, folder: str, args: LinterArgs) -> None:
        pass


class RecursiveLinter(LinterInterface):
    pass


class SingleDirLinter(LinterInterface):
    def run_linter(self, folder: str, args: LinterArgs) -> None:
        self._lint_single_folder(folder, args)
        if args.recursive:
            for root, dirs, _ in os.walk(folder):
                for directory in dirs:
                    path = os.path.join(root, directory)
                    if not os.path.islink(path):
                        self._lint_single_folder(path, args)

    @abstractmethod
    def _lint_single_folder(self, folder: str, args: LinterArgs) -> None:
        pass


RESULTS_FOLDER: Final = "linters_results"

def get_output_file_name(tool: str, project_folder: str) -> str:
    return f"{RESULTS_FOLDER}/{tool}-{project_folder.replace('/', '-')}.sarif"  # type: ignore


def run_tool(argv: List[str], stdout_path: Optional[str] = None,
             stdin_data: Optional[bytes] = None) -> Optional[subprocess.CompletedProcess]:
    """Run a linter without a shell. stdout goes to stdout_path when given, else it's captured."""
    logging.info("Running: %s", shlex.join(argv))
    try:
        if stdout_path is None:
            return subprocess.run(argv, input=stdin_data, capture_output=True, check=False)
        with open(stdout_path, "wb") as out:
            return subprocess.run(argv, input=stdin_data, stdout=out, stderr=subprocess.PIPE,
                                  check=False)
    except FileNotFoundError:
        logging.error("%s is not installed", argv[0])
        return None


def files_in(folder: str, pattern: str) -> List[str]:
    """What sh passes for folder/pattern: the sorted matches, or the pattern itself if none match."""
    matches = sorted(glob.glob(os.path.join(glob.escape(folder), pattern)))
    return matches or [os.path.join(folder, pattern)]


def install_release(url: str, sha256: str, dest: str, member: Optional[str] = None) -> bool:
    """Download a release asset, check its SHA-256 and place it at dest.

    When member is given, the asset is a tar archive and only that file is extracted.
    """
    with tempfile.TemporaryDirectory() as tmp:
        asset = os.path.join(tmp, "asset")
        result = run_tool(["curl", "-fsSL", "-o", asset, url])
        if result is None or result.returncode != 0:
            logging.error("Could not download %s", url)
            return False
        digest = hashlib.sha256()
        with open(asset, "rb") as downloaded:
            for chunk in iter(lambda: downloaded.read(1 << 20), b""):
                digest.update(chunk)
        if digest.hexdigest() != sha256:
            logging.error("Checksum mismatch for %s: got %s", url, digest.hexdigest())
            return False
        payload = asset
        if member is not None:
            payload = os.path.join(tmp, "payload")
            try:
                with tarfile.open(asset) as archive, open(payload, "wb") as staged:
                    extracted = archive.extractfile(member)
                    if extracted is None:
                        raise KeyError(member)
                    shutil.copyfileobj(extracted, staged)
            except (KeyError, tarfile.TarError):
                logging.error("Could not extract %s from %s", member, url)
                return False
        shutil.copyfile(payload, dest)
        os.chmod(dest, 0o755)  # nosec B103 - installed tools must be executable by every user
    return True


def pip_install(package: str, version: str) -> None:
    logging.info(f"Installing {package} version {version}")
    subprocess.run(["pip", "install", f"{package}=={version}"], check=False)

def npm_install(package: str) -> None:
    logging.info(f"Installing {package}")
    subprocess.run(["npm", "install", "-g", package], check=True)


class BanditLinter(RecursiveLinter):
    def install_linter(self) -> None:
        pip_install("bandit[sarif]", LINTER_VERSIONS['bandit'])

    def run_linter(self, folder: str, args: LinterArgs) -> None:
        if args.install:
            self.install_linter()
        output_file = self._prepare_output_file("bandit", folder)
        command = self._construct_command(args, folder, output_file)
        self._execute_command(command)

    @staticmethod
    def _prepare_output_file(linter_name: str, folder: str) -> str:
        output_file = get_output_file_name(linter_name, folder)
        Path(output_file).touch()
        return output_file

    @staticmethod
    def _construct_command(args: LinterArgs, folder: str, output_file: str) -> List[str]:
        main_folder = Path.cwd()
        exclude_option = ["--exclude", ",".join(args.exclude)] if args.exclude else []
        recurse_option = ["--recursive"] if args.recursive else []
        logging.info(f"Exclude option: {exclude_option}")
        return [
            "bandit", *recurse_option, *exclude_option, "--format", "sarif",
            "--output", f"{main_folder}/{output_file}", folder,
        ]

    @staticmethod
    def _execute_command(command: List[str]):
        process = run_tool(command)
        if process is None:
            return
        if process.returncode == 0:
            logging.info("The command was successful.")
        else:
            print(f"The command failed with return code: {process.returncode}")


class ShellCheckLinter(SingleDirLinter):
    def install_linter(self) -> None:
        version = LINTER_VERSIONS['shellcheck']
        install_release(
            f"https://github.com/koalaman/shellcheck/releases/download/v{version}/"
            f"shellcheck-v{version}.linux.x86_64.tar.xz",
            LINTER_CHECKSUMS['shellcheck'], "/usr/local/bin/shellcheck",
            member=f"shellcheck-v{version}/shellcheck",
        )
        with tempfile.TemporaryDirectory() as tmp:
            rustup_init = os.path.join(tmp, "rustup-init")
            rustup_version = LINTER_VERSIONS['rustup']
            if install_release(
                f"https://static.rust-lang.org/rustup/archive/{rustup_version}/"
                f"x86_64-unknown-linux-gnu/rustup-init",
                LINTER_CHECKSUMS['rustup-init'], rustup_init,
            ):
                run_tool([rustup_init, "-y"])
                run_tool([str(Path.home() / ".cargo" / "bin" / "cargo"), "install", "shellcheck-sarif"])

    def _lint_single_folder(self, folder: str, args: LinterArgs) -> None:
        if args.install:
            self.install_linter()
        logging.info("Running shellcheck...")
        output_file = get_output_file_name("shellcheck", folder)
        result = run_tool(["shellcheck", "-f", "json", *files_in(folder, "*.sh")])
        if result is not None:
            run_tool(["shellcheck-sarif"], stdout_path=output_file, stdin_data=result.stdout)


class PylintLinter(RecursiveLinter):
    def install_linter(self) -> None:
        pip_install("pylint", LINTER_VERSIONS['pylint'])

    def run_linter(self, folder: str, args: LinterArgs) -> None:
        if args.install:
            self.install_linter()
        logging.info("Running pylint...")
        output_file = get_output_file_name("pylint", folder) + ".json"
        command = self._construct_command(args, folder, output_file)
        self._execute_command(command)


    @staticmethod
    def _construct_command(args: LinterArgs, folder: str, output_file: str) -> List[str]:
        exclude_option = [f"--ignore={','.join(args.exclude)}"] if args.exclude else []
        recursive_option = ["--recursive", "y"] if args.recursive else []
        return [
            "pylint", *recursive_option, *files_in(folder, "*.py"),
            f"--output={output_file}", "-f", "json", *exclude_option,
        ]

    @staticmethod
    def _execute_command(command: List[str]):
        result = run_tool(command)
        if result is not None and (result.returncode > 126 or result.returncode == 1):
            logging.info("Pylint failed while running")


class MypyLinter(RecursiveLinter):
    def install_linter(self) -> None:
        pip_install("mypy", LINTER_VERSIONS['mypy'])

    def run_linter(self, folder: str, args: LinterArgs) -> None:
        if args.install:
            self.install_linter()
        output_file = get_output_file_name("mypy", folder) + ".xml"
        exclude_option = [arg for pattern in args.exclude for arg in ("--exclude", pattern)]
        run_tool([
            "mypy", "--warn-return-any", "--warn-unreachable", "--ignore-missing-imports",
            *exclude_option, "--junit-xml", output_file, folder,
        ])


class NjsscanLinter(RecursiveLinter):
    def install_linter(self) -> None:
        pip_install("njsscan", "0.3.6")

    def run_linter(self, folder: str, args: LinterArgs) -> None:
        if args.install:
            self.install_linter()
        logging.info("Running njsscan...")
        output_file = get_output_file_name("njsscan", folder) + ".sarif"
        result = run_tool(["njsscan", "--exit-warning", "--sarif", "-o", output_file, folder])
        if result is not None and result.returncode > 1:
            logging.warning(f"njsscan failed with return code: {result.returncode}")


class EslintLinter(RecursiveLinter):
    def install_linter(self) -> None:
        npm_install(f"eslint@{LINTER_VERSIONS['eslint']}")

    def run_linter(self, folder: str, args: LinterArgs) -> None:
        if args.install:
            self.install_linter()
        logging.info("Running eslint...")
        subprocess.run(["npm", "ci"], check=False)
        output_file = get_output_file_name("eslint", folder) + ".sarif"
        exclude_option = [arg for pattern in args.exclude for arg in ("--ignore-pattern", pattern)]
        run_tool(["eslint", *exclude_option, "--format", "json", folder], stdout_path=output_file)


class NpmAuditLinter(RecursiveLinter):
    def run_linter(self, folder: str, args: LinterArgs) -> None:
        logging.info("Running npm audit...")
        output_file = get_output_file_name("npm-audit", folder) + ".json"
        run_tool(["npm", "audit", "--audit-level=moderate", "--json"], stdout_path=output_file)


class HadolintLinter(SingleDirLinter):
    def install_linter(self) -> None:
        version = LINTER_VERSIONS['hadolint']
        logging.info(f"Installing hadolint version {version}")
        install_release(
            f"https://github.com/hadolint/hadolint/releases/download/v{version}/hadolint-Linux-x86_64",
            LINTER_CHECKSUMS['hadolint'], "/usr/local/bin/hadolint",
        )

    def _lint_single_folder(self, folder: str, args: LinterArgs) -> None:
        if args.install:
            self.install_linter()
        logging.info("Running hadolint...")
        output_file = get_output_file_name("hadolint", folder) + ".sarif"
        run_tool(["hadolint", "-f", "sarif", os.path.join(folder, "Dockerfile")],
                 stdout_path=output_file)


class GolintersLinter(RecursiveLinter):
    def install_linter(self) -> None:
        version = LINTER_VERSIONS['golangci-lint']
        logging.info(f"Installing golangci-lint version {version}")
        name = f"golangci-lint-{version}-linux-amd64"
        install_release(
            f"https://github.com/golangci/golangci-lint/releases/download/v{version}/{name}.tar.gz",
            LINTER_CHECKSUMS['golangci-lint'], "/usr/local/bin/golangci-lint",
            member=f"{name}/golangci-lint",
        )

    def run_linter(self, folder: str, args: LinterArgs) -> None:
        if args.install:
            self.install_linter()
        logging.info("Running golangci-lint...")
        output_file = get_output_file_name("golangci", folder) + ".json"
        run_tool(["golangci-lint", "run", "-v", "--out-format", "json", f"{folder}/..."],
                 stdout_path=output_file)


class LizardLinter(RecursiveLinter):
    def run_linter(self, folder: str, args: LinterArgs) -> None:
        logging.info("Running Lizardlint...")
        output_file = get_output_file_name("lizardlint", folder) + ".csv"
        run_tool(["lizard", "--csv", folder], stdout_path=output_file)

    def install_linter(self) -> None:
        logging.info("Installing Lizardlint...")
        pip_install("lizard", LINTER_VERSIONS['lizardlint'])

class LinterStrategy(ABC):
    def __init__(self):
        self.linters: List[LinterInterface] = []

    def run_linters(self, folder: str, args: LinterArgs) -> None:
        for linter in self.linters:
            linter.run_linter(folder, args)


class PythonLinterStrategy(LinterStrategy):
    def __init__(self):
        super().__init__()
        self.linters = [
            BanditLinter(),
            PylintLinter(),
            MypyLinter(),
            LizardLinter(),
        ]
    def install_linter(self):
        for linter in self.linters:
            linter.install_linter()


class GoLinterStrategy(LinterStrategy):
    def __init__(self):
        super().__init__()
        self.linters = [GolintersLinter()]


class JavaScriptLinterStrategy(LinterStrategy):
    def __init__(self):
        super().__init__()
        self.linters = [NjsscanLinter(), EslintLinter(), NpmAuditLinter()]


class ShellLinterStrategy(LinterStrategy):
    def __init__(self):
        super().__init__()
        self.linters = [ShellCheckLinter()]


class DockerfileLinterStrategy(LinterStrategy):
    def __init__(self):
        super().__init__()
        self.linters = [HadolintLinter()]


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Linting script")
    parser.add_argument(
        "-e", "--exclude", action="append", default=[], help="Directories to exclude"
    )
    parser.add_argument(
        "-l",
        "--language",
        choices=["python", "go", "javascript", "shell", "dockerfile"],
        required=False,
    )
    parser.add_argument("-f", "--folders", nargs='+', required=False)
    parser.add_argument(
        "-r",
        "--recursive-dir",
        action="store_true",
        help="Run linters on all subdirectories",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install the required linters before running",
    )
    return parser


def create_strategies() -> dict:
    return {
        "python": PythonLinterStrategy(),
        "go": GoLinterStrategy(),
        "javascript": JavaScriptLinterStrategy(),
        "shell": ShellLinterStrategy(),
        "dockerfile": DockerfileLinterStrategy(),
    }


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    if args.install:
        logging.info("Installing required linters...")
        strategies = create_strategies()

        if args.language and args.folders:
            strategy = cast(LinterStrategy, strategies.get(args.language))
            if not strategy:
                logging.info(f"No linter strategy found for language: {args.language}")
                return

            for folder in args.folders:
                strategy.run_linters(folder, LinterArgs(exclude=args.exclude, recursive=args.recursive_dir, install=args.install))
        else:
            for strategy in strategies.values():
                if hasattr(strategy, 'install_linter'):
                    strategy.install_linter()
                else:
                    logging.warning(f"{type(strategy).__name__} does not support installation.")
        return

    if not args.language or not args.folders:
        parser.error("The --language and --folders arguments are required if --install is not used.")

    linter_args = LinterArgs(
        exclude=args.exclude, recursive=args.recursive_dir, install=args.install
    )

    Path(RESULTS_FOLDER).mkdir(exist_ok=True, mode=0o777)

    strategies = create_strategies()

    strategy = cast(LinterStrategy, strategies.get(args.language))
    if not strategy:
        logging.info(f"No linter strategy found for language: {args.language}")
        return

    for folder in args.folders:
        strategy.run_linters(folder, linter_args)


if __name__ == "__main__":
    main()
