#!/usr/bin/env python3
"""Mini-Lang to Python compiler. Uses the various modules to generated a python script.
The options above allow to control the behavior of the compiler.
Usage: python ./compiler.py <source_file> [-?] [-!] [-l|-p] [-no] [--debug-compiler] [<output_file>]
    @option [-?|--help] show help
    @option [-!|--log] log intermediary output using tui
    @option [-l|--lexer] stop on lexer. Enable log
    @option [-p|--parser] stop on parser. Enable log
    @option [-no|--no-optimize] don't use accumulator
    @option [--debug-compiler] don't catch exceptions in the Tui log to allow compiler debugging
"""
from enum import IntEnum

from .utils.arg_parser import ArgParser

from .utils.options import *
from .utils.utils import log_error, EXIT_SUCCESS


class StopOn(IntEnum):
    NONE = 0
    LEXER = 1  # Stop on Lexer
    PARSER = 2  # Stop on Parser
    INTERPRETER = 3  # Stop on Interpreter


def parse_append(parser: ArgParser) -> None:
    from .modules.gen import parse_append as append

    append(parser)
    # Option flags
    # TODO -> Allows to each IR to generate output files
    parser.add_argument(
        "-l", "--lexer", action="store_true", help="Stop on lexer. Enable log"
    )
    parser.add_argument(
        "-p", "--parser", action="store_true", help="Stop on parser. Enable log"
    )
    parser.add_argument(
        "-i", "--interpreter", action="store_true", help="Enable interpreter mode"
    )


def main(
    source_filename: str,
    options: int,
    output_filename: str = "",
    stop_on: StopOn = StopOn.NONE,
    *args,
    **kwargs,
) -> None | str:
    # TEST -> Each option execution must be verified.

    # log_error(
    #     f"Error: Multiple output files provided ('{output_file}' and '{sys.argv[i]}')"
    # )
    # endregion

    match stop_on:
        # region Lexer only
        case StopOn.LEXER:
            from .modules import lexer as lexer

            lexer.main(source_filename, bool(options & Options.LOG))
            exit(EXIT_SUCCESS)
        # endregion

        # region Stop at Parser
        case StopOn.PARSER:
            from .modules import parser

            parser.main(source_filename, options)
            exit(EXIT_SUCCESS)
        # endregion

        case _:
            # region Full compiler
            from .modules import gen

            if stop_on == StopOn.INTERPRETER:
                from .utils import interpreter

                interpreter.main(source_filename, options, output_filename)
                exit(EXIT_SUCCESS)

    gen.main(source_filename, options, output_filename)
    # endregion


if __name__ == "__main__":
    # TODO (Future) -> Serialization of compiler layers. Eg.: Lexer [TOKENS file] -> Parser [AST .json] -> Code generator [.py file]
    from .utils.utils import log_error, EXIT_ERROR
    from .modules import parser as ml_parser

    parser = ArgParser(
        description="MiniLang interpreter. Uses the gen layer to compile the MiniLang source to Python code, then executes it.\n",
        add_help=False,  # we'll add custom help options to match original
    )
    parse_append(parser)

    # Parse arguments
    args = parser.parse_args()
    options = ml_parser.fetch_options(args)

    stop_on = StopOn.NONE
    if args.lexer:
        stop_on = StopOn.LEXER
    if args.parser:
        stop_on = StopOn.PARSER
    if args.interpreter:
        stop_on = StopOn.INTERPRETER

    # Call main with parsed values
    main(
        args.source,
        options,
        args.output,
        stop_on,
    )
