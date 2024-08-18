import json
import sys
from enum import Enum

import typer
import yaml


class OutputFormat(str, Enum):
    yaml = "yaml"
    json = "json"
    raw = "raw"


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # Encode all iterables as lists
        # Derived from
        # - https://stackoverflow.com/a/8230505
        if hasattr(obj, "__iter__"):
            return list(obj)
        # Serialize date
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def cli_print_retval(ret: dict | list, output_format: OutputFormat, **kwargs):
    if output_format == OutputFormat.yaml:
        print(yaml.dump(ret, default_flow_style=False))
    elif output_format == OutputFormat.json:
        print(json.dumps(ret, indent=2, cls=CustomJSONEncoder))
    elif output_format == OutputFormat.raw:
        sys.stdout.write(ret)
    else:
        raise ValueError(f"Unknown output format: {output_format}")


app = typer.Typer(result_callback=cli_print_retval)


@app.callback()
# This function is used to add global CLI options
def main(output_format: OutputFormat = OutputFormat.yaml):
    pass
