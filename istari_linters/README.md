# Istari Linters

The linter is runned using bash. I recommend to run it inside a virtualenv or something like that to avoid install al tools an dependencies it's going to use in our machine.

The script receives differents kinds of parameters:

- `-e <directory>` this flag indicates directories to be ignored to linting (not folders inside a project).
- `-n` to indicate to run the linters inside the folder, but not recursively in subfolders
- `-l <language>` set the language to be linted (this will choose which linters run)
- `-f <folder>` folder to run linters and to analyze subfolders if `-n` isn't present
