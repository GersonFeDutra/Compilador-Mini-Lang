#!/usr/bin/env python3
"""
Usage: python ./compyler.py <source_file> [-?] [-!] [-l|-p] [-no] [--debug-compiler] [<output_file>]
    @option [-?|--help] show help
    @option [-!|--log] log intermediary output using tui
    @option [-l|--lexer] stop on lexer. Enable log
    @option [-p|--parser] stop on parser. Enable log
    @option [-no|--no-optimize] don't use accumulator
    @option [--debug-compiler] don't catch exceptions in the Tui log to allow compiler debugging
"""

import sys
from utils.options import *
from utils.utils import log_error, EXIT_SUCCESS, EXIT_ERROR


def show_help():
    # TODO -> Requires the output file for the --out option
    print(
        "\033[34m"
        f"Usage: python {sys.argv[0]} <source_file> [<output_file>] [-!|--log] [-no|--no-optimize] [--interpreter|-l|-p]\n"
        "\t<source_file>: The source code file to compile\n"
        "\t[<output_file>]: Optional. If provided, the generated code will be saved to this file.\n"
        "\t[-?|--help] show this help\n"
        "\t[-!|--log] log intermediary output using tui\n"
        "\t[-i|--interpreter] execute the generated code. If no output file is provided, the interpreter will run the generated code in memory\n"
        "\t[-l|--lexer] stop on lexer. Enable log\n"
        "\t[-p|--parser] stop on parser. Enable log\n"
        "\t[-no|--no-optimize] don't use accumulator\n"
        "\033[m"
    )


if __name__ == "__main__":
    # region Options
    options: int = Options.NONE  # type: ignore
    is_interpreter = False
    output_file = ""
    # endregion

    # region 1. Verifica se o usuário passou o nome do arquivo
    if len(sys.argv) < 2:
        log_error("Error: No file name provided")
        show_help()
        sys.exit(EXIT_ERROR)
    # endregion
    # region 2. Verifica se foram passadas opções
    elif len(sys.argv) > 2:
        # TEST -> Each option execution must be verified.
        for i in range(2, len(sys.argv)):
            # TODO -> Grouped options parsing
            match sys.argv[i]:
                case "-?" | "--help":
                    show_help()
                    sys.exit()
                case "-i" | "--interpreter":
                    is_interpreter = True
                case "-l" | "--lexer":
                    options |= Options.LEXER
                    # TODO -> Allow running the lexer without Tui
                    options |= Options.LOG
                case "-p" | "--parser":
                    options |= Options.PARSER
                    # TODO -> Allow running the parser without Tui
                    options |= Options.LOG
                case "-!" | "--log":
                    options |= Options.LOG
                case "-no" | "--no-optimize":
                    # Allows the parser to use an accumulator to process results directly
                    options |= Options.NO_OPTIMIZE
                case "--debug-compiler":
                    options |= Options.NO_EXCEPT_TREATMENT
                case _:
                    if sys.argv[i].startswith("-"):
                        log_error(f"Error: Unknown option '{sys.argv[i]}'")
                        show_help()
                        sys.exit(EXIT_ERROR)
                    elif output_file:
                        log_error(
                            f"Error: Multiple output files provided ('{output_file}' and '{sys.argv[i]}')"
                        )
                        show_help()
                        sys.exit(EXIT_ERROR)
                    else:
                        output_file = sys.argv[i]

    # endregion

    source_filename = sys.argv[1]

    # region Lexer only
    if options & Options.LEXER:
        import modules.lexer as lexer

        lexer.main(source_filename, bool(options & Options.LOG))
        exit(EXIT_SUCCESS)
    # endregion

    # region Stop at Parser
    if options & Options.PARSER:
        import modules.parser as parser

        parser.main(source_filename, options)
        exit(EXIT_SUCCESS)
    # endregion

    # region Full compiler
    import modules.gen as code_gen

    if is_interpreter:
        if output_file:
            code_gen.main(source_filename, options, output_file=output_file)
            # TODO -> Add a panel in the Tui to the interpreted file.
            import subprocess

            p = subprocess.Popen(
                f"python {output_file}", shell=True
            )  # pyright: ignore[reportUndefinedVariable]
            p.wait()
            sys.exit(p.returncode)

        else:
            code_string = code_gen.main(source_filename, options, is_hybrid_out=True)
            try:
                exec(code_string)  # pyright: ignore[reportArgumentType]
            except Exception as e:
                log_error(f"Error during execution: {e}")
                import traceback
                from utils.utils import log

                log(f"{traceback.format_exc()}")
                sys.exit(EXIT_ERROR)
            exit(EXIT_SUCCESS)
    else:
        code_gen.main(source_filename, options, output_file=output_file)
        exit(EXIT_SUCCESS)

    # endregion
