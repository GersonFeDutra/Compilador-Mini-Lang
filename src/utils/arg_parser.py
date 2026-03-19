import sys
import argparse
from .utils import EXIT_ERROR


class ArgParser(argparse.ArgumentParser):
    def error(self, message):  # pyright: ignore[reportIncompatibleMethodOverride]
        self.print_usage(sys.stderr)
        self.exit(EXIT_ERROR, "\033[31m" f"Error: {message}\033[0m\n")
