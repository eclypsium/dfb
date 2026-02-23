# You Shall Not Parse

![You Shall Not Parse](docs/you_shall_not_parse_icon.jpg)

## What is it about?

This is a library for parsing linters output, you give it a filenames list and an observer object. it will parse it and call the `add_issue` method with the `linter_name` and a tuple of the following parameters (`severity`, `filename`, `id`, `message`, `location`).

The entry point for this library is the `Parser` class, you need to import that class, create an object and call the `parse` method with the list with the path of each file you want to parse and an observer object.

## Linters

|Linters             | isSupported? |
|:---                |:--------:    |
|     npm-audit      |      Yes           |
|     pip-audit      |      Yes           |
| sarif-based        |      Yes           |
|     golangci       |      Yes         |
|     Mypy           |      Yes        |
|     Radon          |      Yes           |
|     Yapf            |      No        |
|      Lizard          |    Yes         |

sarif-based was tested with = bandit, eslint, gitleaks, semgrep, trivy

## Add new linter

If you want to add a new linter, you should make a new file in the `parsers` folder.

There you should create a class for your linter and set the `HANDLER` variable with the name of the class. Then your class must hesitate from `ParserHandlerImplementation` or `JmespathParserHandler`.

Your class must have defined 2 methods

- handler: Is the main method, it's called when a file is readed and you should call the `add_issue` method of the observer you get. How it works depends if you want to make the parsing by hand or using a jmespath query.

- parse_level: Given the severity string you should parse that string to a severity of the `Severity` class defined in `base_classes.py`

## Default observers

There are 3 observers already defined to use:

- `DBObserver`: This observer will create a `Database` object and add each issue to it. You can get the database with the `get_database` method

- `SarifObserver`: This observer will create a sarif based json object and if you call `get_sarif_json` it will returns a json object with the sarif standard

- `ConsoleObserver`: This observer will print each issue while each issue is arriving.
