import argparse
import os
import sys
import subprocess
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Optional, cast, Final
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent))
from linter_versions import LINTER_VERSIONS

# pylint: disable=too-few-public-methods

logging.basicConfig(level=logging.INFO)

@dataclass
class LinterArgs:
    exclude: Optional[str] = field(default=None)
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
                    self._lint_single_folder(os.path.join(root, directory), args)

    @abstractmethod
    def _lint_single_folder(self, folder: str, args: LinterArgs) -> None:
        pass


RESULTS_FOLDER: Final = "linters_results"

def get_output_file_name(tool: str, project_folder: str) -> str:
    return f"{RESULTS_FOLDER}/{tool}-{project_folder.replace('/', '-')}.sarif"  # type: ignore

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
    def _construct_command(args: LinterArgs, folder: str, output_file: str) -> str:
        main_folder = Path.cwd()
        exclude_option = f"--exclude {args.exclude}" if args.exclude else ""
        recurse_option = "--recursive" if args.recursive else ""
        logging.info(f"Exclude option: {exclude_option}")
        return (
            f"bandit {recurse_option} {exclude_option} --format sarif --output {main_folder}/{output_file} "
            f" {folder}"
        )

    @staticmethod
    def _execute_command(command: str):
        logging.info(f"Running command: {command}")
        process = subprocess.run(command, shell=True, capture_output=True, check=False)
        if process.returncode == 0:
            logging.info("The command was successful.")
        else:
            print(f"The command failed with return code: {process.returncode}")


class ShellCheckLinter(SingleDirLinter):
    def install_linter(self) -> None:
        subprocess.run(
            "curl -L https://github.com/koalaman/shellcheck/releases/download/v0.8.0/"
            "shellcheck-v0.8.0.linux.x86_64.tar.xz | tar xJf - && "
            "mv shellcheck-v0.8.0/shellcheck /usr/local/bin/ && "
            "rm -rf shellcheck-v0.8.0",
            shell=True, check=False,
        )
        subprocess.run(
            'curl https://sh.rustup.rs -sSf | sh -s -- -y && '
            '. "$HOME/.cargo/env" && cargo install shellcheck-sarif',
            shell=True, check=False,
        )

    def _lint_single_folder(self, folder: str, args: LinterArgs) -> None:
        if args.install:
            self.install_linter()
        logging.info("Running shellcheck...")
        output_file = get_output_file_name("shellcheck", folder)
        json_file = f"{output_file}.json"
        result = subprocess.run(
            f"shellcheck -f json {folder}/*.sh",
            shell=True, capture_output=True, check=False,
        )
        Path(json_file).write_text(result.stdout.decode())
        subprocess.run(
            f"shellcheck-sarif < {json_file} > {output_file}",
            shell=True, check=False,
        )
        Path(json_file).unlink(missing_ok=True)


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
    def _construct_command(args: LinterArgs, folder: str, output_file: str) -> str:
        exclude_option = f"--ignore={args.exclude}" if args.exclude else ""
        recursive_option = "--recursive y" if args.recursive else ""
        command = (
            f"pylint {recursive_option} {folder}/*.py "
            f"--output={output_file} -f json {exclude_option}"
        )
        return command

    @staticmethod
    def _execute_command(command: str):
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            check=False,
        )
        if result.returncode > 126 or result.returncode == 1:
            logging.info("Pylint failed while running")


class MypyLinter(RecursiveLinter):
    def install_linter(self) -> None:
        pip_install("mypy", LINTER_VERSIONS['mypy'])

    def run_linter(self, folder: str, args: LinterArgs) -> None:
        if args.install:
            self.install_linter()
        output_file = get_output_file_name("mypy", folder) + ".xml"
        exclude_option = f"--exclude {args.exclude}" if args.exclude else ""
        command = (
            f"mypy --warn-return-any --warn-unreachable "
            f"--ignore-missing-imports {exclude_option} --junit-xml {output_file} {folder}"
        )
        logging.info(f"Running command: {command}")
        subprocess.run(command, shell=True, check=False)


class NjsscanLinter(RecursiveLinter):
    def install_linter(self) -> None:
        pip_install("njsscan", "0.3.6")

    def run_linter(self, folder: str, args: LinterArgs) -> None:
        if args.install:
            self.install_linter()
        logging.info("Running njsscan...")
        output_file = get_output_file_name("njsscan", folder) + ".sarif"
        result = subprocess.run(
            f"njsscan --exit-warning --sarif -o {output_file} {folder}",
            shell=True, capture_output=True, check=False,
        )
        if result.returncode > 1:
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
        exclude_option = f"--ignore-pattern {args.exclude}" if args.exclude else ""
        subprocess.run(
            f"eslint {exclude_option} --format json {folder} > {output_file}",
            shell=True,
            check=False,
        )


class NpmAuditLinter(RecursiveLinter):
    def run_linter(self, folder: str, args: LinterArgs) -> None:
        logging.info("Running npm audit...")
        output_file = get_output_file_name("npm-audit", folder) + ".json"
        subprocess.run(
            f"npm audit --audit-level=moderate --json > {output_file}",
            shell=True,
            check=False,
        )


class HadolintLinter(SingleDirLinter):
    def install_linter(self) -> None:
        version = LINTER_VERSIONS['hadolint']
        logging.info(f"Installing hadolint version {version}")
        subprocess.run(
            f"curl -L https://github.com/hadolint/hadolint/releases/download/v{version}/"
            f"hadolint-Linux-x86_64 -o /usr/local/bin/hadolint && "
            f"chmod +x /usr/local/bin/hadolint",
            shell=True, check=False,
        )

    def _lint_single_folder(self, folder: str, args: LinterArgs) -> None:
        if args.install:
            self.install_linter()
        logging.info("Running hadolint...")
        output_file = get_output_file_name("hadolint", folder) + ".sarif"
        result = subprocess.run(
            f"hadolint -f sarif {folder}/Dockerfile",
            shell=True, capture_output=True, check=False,
        )
        Path(output_file).write_text(result.stdout.decode())


class GolintersLinter(RecursiveLinter):
    def install_linter(self) -> None:
        version = LINTER_VERSIONS['golangci-lint']
        logging.info(f"Installing golangci-lint version {version}")
        subprocess.run(
            f"curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | "
            f"sh -s -- -b /usr/local/bin v{version}",
            shell=True, check=False,
        )

    def run_linter(self, folder: str, args: LinterArgs) -> None:
        if args.install:
            self.install_linter()
        logging.info("Running golangci-lint...")
        output_file = get_output_file_name("golangci", folder) + ".json"
        result = subprocess.run(
            f"golangci-lint run -v --out-format json {folder}/...",
            shell=True, capture_output=True, check=False,
        )
        Path(output_file).write_text(result.stdout.decode())


class LizardLinter(RecursiveLinter):
    def run_linter(self, folder: str, args: LinterArgs) -> None:
        logging.info("Running Lizardlint...")
        output_file = get_output_file_name("lizardlint", folder) + ".csv"
        command = f'lizard --csv "{folder}" > "{output_file}"'
        subprocess.run(
            command,
            shell=True,
            check=False,
        )

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
                strategy.run_linters(folder, LinterArgs(exclude=" ".join(args.exclude), recursive=args.recursive_dir, install=args.install))
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
        exclude=" ".join(args.exclude), recursive=args.recursive_dir, install=args.install
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
