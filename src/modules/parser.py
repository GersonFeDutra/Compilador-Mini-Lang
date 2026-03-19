from functools import partial
import sys
import json
from typing import Callable
from queue import SimpleQueue as Queue

from .lexer import Lexer, Num, Token, Tag, Tags, Id, Type
from .symbols import Symbol, SymTable
from ..utils.istream import InputStream, TuiInputStream
from ..utils.options import *
from ..utils.tui import Tui
from ..utils.utils import EXIT_ERROR, log, log_error
from ..utils.utils import log_warning
from ..modules.ast import (
    Program,
    Block,
    Literal,
    BinOp,
    Assignment,
    VarDecl,
    Identifier,
    ASTNode,
    VarDecl,
    PrintStmt,
    IfStmt,
    WhileStmt,
    ReturnStmt,
    FormalParam,
    FunctionCall,
    FunctionDecl,
)
from typing import List
from pprint import pformat


# Definimos uma exceção personalizada para evitar confusão
# com o "SyntaxError" nativo do Python
class ParseError(Exception):
    pass


class SyntaxError(ParseError):
    pass


class SemanticError(ParseError):
    pass


class Parser:
    _id_queue: Queue[Id]

    def __init__(
        self,
        lexer: Lexer,
        logger: Callable = log,
        warn_logger: Callable = log_warning,
        optimize: bool = True,
    ):
        self._lexer = lexer
        self._lookahead: Token = Token("")
        self._optimize = optimize
        self._sym_table = SymTable()
        self._id_queue = Queue()
        self._log = logger
        self._warn = warn_logger

        if self._optimize:
            self.accumulator: int = 0

    def start(self) -> Program:
        """Inicia o processo de análise e retorna a AST completa."""
        self._lookahead = self._lexer.scan()
        ast_root = self.program()
        self._lexer.finish()

        # imprimir arvore
        # self._log(pformat(ast_root, indent=1, width=80))
        self._log(json.dumps(ast_root.to_dict(), indent=2))

        return ast_root

    def program(self) -> Program:
        """
        Regra:
            program = `symTable=null;` stmts
        """
        lista_de_comandos = self.stmts()  # program -> stmts

        # Verifica se o último caractere é o marcador vazio (nil ⇒ EOF)
        if self._lookahead != "":
            raise SyntaxError(
                f"Erro sintático [{self._lexer.filename}:{self._lexer.line}:{self._lexer.column}]: "
                f"Token desconhecido [{self._lookahead}]."
            )

        return Program(statements=lista_de_comandos)

    def var_decl(self) -> VarDecl:
        """Regra: var <id> : <type> = <expr> ;"""
        self.match(Tags.VAR)

        name = str(self._lookahead)
        self.match(Tags.ID)
        self.match(Tag(":"))

        var_type = str(self._lookahead)
        self.match(Tags.TYPE)
        self.match(Tag("="))

        expr_node = self.opers()
        self.match(Tag(";"))

        # Verificação de tipos na declaração
        expr_type = self._infer_type(expr_node)
        if expr_type != "unknown" and var_type != expr_type:
            if not (var_type == "real" and expr_type == "int"):
                raise SemanticError(
                    f"Erro Semântico [{self._lexer.filename}:{self._lexer.line}:{self._lexer.column}]: "
                    f"A variável '[cyan]{name}[/cyan]' foi declarada como "
                    f"'[purple]{var_type}[/purple]', mas recebeu um valor do tipo "
                    f"'[purple]{expr_type}[/purple]'."
                )

        # Salvar tabelas de símbolos
        if not self._sym_table.insert(name, Symbol(name, var_type)):
            raise SemanticError(
                f"Erro semântico [{self._lexer.filename}:{self._lexer.line}:{self._lexer.column}]: "
                f"variável '[cyan]{name}[/cyan]' já declarada."
            )
        return VarDecl(name=name, var_type=var_type, value=expr_node)

    def assignment(self) -> Assignment:
        """Regra: set <id> = <expr> ;"""
        self.match(Tags.SET)

        name = str(self._lookahead)
        self.match(Tags.ID)
        self.match(Tag("="))

        expr_node = self.opers()
        self.match(Tag(";"))

        sym = self._sym_table.find(name)
        if sym:
            expr_type = self._infer_type(expr_node)
            if expr_type != "unknown" and sym.type != expr_type:
                if not (sym.type == "real" and expr_type == "int"):
                    raise SemanticError(
                        f"Erro semântico [{self._lexer.filename}:{self._lexer.line}{self._lexer.column}]: "
                        f"A variável '[cyan]{name}[/cyan]' é do tipo '[purple]{sym.type}[/purple]', "
                        f"mas está a receber um valor do tipo '[purple]{expr_type}[/purple]'."
                    )

        return Assignment(
            name=name, value=expr_node, var_type=sym.type if sym else "undefined"
        )

    def print_stmt(self) -> PrintStmt:
        """Regra: print <expr> ;"""

        self.match(Tags.PRINT)
        expr_node = self.opers()
        self.match(Tag(";"))

        return PrintStmt(expr=expr_node)

    def if_stmt(self) -> IfStmt:
        """REGRA: if( <expression> ) <bloco> [ else <block> ]"""
        self.match(Tags.IF)
        self.match(Tag("("))
        condition = self.opers()
        self.match(Tag(")"))

        true_block = self.block()
        false_block = None

        if self._lookahead.tag == Tags.ELSE:
            self.match(Tags.ELSE)
            false_block = self.block()
        return IfStmt(
            condition=condition, true_block=true_block, false_block=false_block
        )

    def while_stmt(self) -> WhileStmt:
        """Regra: while ( <expression> ) <block>"""
        self.match(Tags.WHILE)
        self.match(Tag("("))
        condition = self.opers()
        self.match(Tag(")"))
        body = self.block()
        return WhileStmt(condition=condition, body=body)

    def return_stmt(self) -> ReturnStmt:
        """Regra: return <expression> ;"""
        self.match(Tags.RETURN)
        expr_node = self.opers()
        self.match(Tag(";"))
        return ReturnStmt(expr=expr_node)

    def function_decl(self) -> FunctionDecl:
        """Regra def <id> ( [ <params>] ) : <type> <block>"""
        self.match(Tags.DEF)
        name = str(self._lookahead)
        self.match(Tags.ID)
        self.match(Tag("("))

        params = []

        if self._lookahead.tag == Tags.ID:
            while True:
                p_name = str(self._lookahead)
                self.match(Tags.ID)
                self.match(Tag(":"))
                p_type = str(self._lookahead)
                self.match(Tags.TYPE)
                params.append(FormalParam(name=p_name, param_type=p_type))

                # save parameters
                self._sym_table.insert(p_name, Symbol(p_name, p_type))

                if self._lookahead == ",":
                    self.match(Tag(","))
                else:
                    break

        self.match(Tag(")"))
        self.match(Tag(":"))
        ret_type = str(self._lookahead)
        self.match(Tags.TYPE)

        simbolos_dos_parametros = [Symbol(p.name, p.param_type) for p in params]
        self._sym_table.insert(name, Symbol(name, "function", simbolos_dos_parametros))

        body = self.block()

        return FunctionDecl(name=name, params=params, return_type=ret_type, body=body)

    def stmts(self) -> List[ASTNode]:
        """Statements
        Regras:
            <statement> = <variable-decl> ";"
                        | <assignment> ";"
                        | <print-statement> ";"
                        | <if-statement>
                        | <while-statement>
                        | <return-statement> ";"
                        | <function-decl>
                        | <block>
                        | ";" `warn "empty statement"`
        """
        statements_list = []

        while True:
            match self._lookahead.tag:
                # stmts -> var_decl
                case Tags.VAR:
                    statements_list.append(self.var_decl())
                    continue
                # stmts -> assignment
                case Tags.SET:
                    statements_list.append(self.assignment())
                    continue
                # stmts -> print_stmt
                case Tags.PRINT:
                    statements_list.append(self.print_stmt())
                    continue
                # stmts -> if_stmt
                case Tags.IF:
                    statements_list.append(self.if_stmt())
                    continue
                # stmts -> while_stmt
                case Tags.WHILE:
                    statements_list.append(self.while_stmt())
                    continue
                # stmts -> function_decl
                case Tags.DEF:
                    statements_list.append(self.function_decl())
                    continue
                # stmts -> return_stmt
                case Tags.RETURN:
                    statements_list.append(self.return_stmt())
                    continue
                # stmts -> block
                case "{":
                    statements_list.append(self.block())
                    continue
                # stmts -> ;
                case ";":
                    self.match(Tag(";"))
                    self._warn(
                        f"[{self._lexer.filename}:{self._lexer.line}:{self._lexer.column}]: "
                        "Empty statement. Remove single ';'."
                    )
                    continue
                case _:
                    return statements_list

    def expr(self) -> List[ASTNode] | None:
        """lval_lst declr_or_rval_lst | rval_lst"""
        # stmt -> lval_lst rval_lst
        if self.lval_lst():
            nodes = self.declr_or_rval_lst()
            if nodes is None:
                self.clear_queue()
                if self._lookahead == ";":
                    self._warn(
                        f"[warning] standalone expression at line :{self._lexer.line}."
                    )
                return []
            return nodes

        nodes = self.rval_lst()
        # stmt -> rval_lst
        if nodes is not None:
            if self._lookahead == ";":
                self._warn(
                    f"[warning] standalone expression at line :{self._lexer.line}."
                )
            return nodes
        return None

    def block(self) -> Block:
        """
        Regra:
            block -> { saved= symTable;
                       symTable = SymTable(previous=symTable);
                       print('{');
                     } { stmts } { symTable = saved; print('}'); }
        """
        self.match(Tag("{"))

        # 1. Salva tabela atual
        saved_table = self._sym_table  # ação semântica

        # 2. cria nova tabela aninhada
        self._sym_table = SymTable(previous=saved_table)  # ação semântica

        comando_dos_blocos = self.stmts()

        if self._lookahead != "}":
            raise SyntaxError(
                f"Erro sintático [{self._lexer.filename}:{self._lexer.line}:{self._lexer.column}]: "
                "era esperado '}' no final do bloco."
            )
        self.match(Tag("}"))

        # ação semântica: restaura tabela anterior
        self._sym_table = saved_table
        # del saved_table

        return Block(statements=comando_dos_blocos)

    def lval_lst(self) -> bool:
        """Left-value list
        Regras:
            lval_lst -> lval [, lval_lst]'
            lval -> ID { push(Id(<lookahead>)) }
        """
        ret = self._lookahead.tag == Tags.ID
        while ret:
            assert isinstance(self._lookahead, Id)
            # lval -> ID { push(ID(<lookahead>)) }
            id = self._lookahead
            self.match(Tags.ID)
            self.queue(id)  # ação semântica: empilha o Id

            # REFACTOR -> Clear
            # raise SyntaxError(f'Erro sintático [{self._lexer.filename}:{self._lexer.line}:{self._lexer.column}]:'
            #                  ' era esperado um identificador de variável,'
            #                  f'foi passado {self._lookahead.tag.name} ao invés disso.')

            # if not self.match(TAG.ID):
            #     raise SyntaxError(f"Erro sintático [{self._lexer.filename}:{self._lexer.line}:{self._lexer.column}]:"
            #                      " era esperado um identificador de variável.")

            # verifica se a variável foi declarada
            # symbol = self.find(name)
            # if symbol is None:
            #     raise SyntaxError(f"Erro sintático [{self._lexer.filename}:{self._lexer.line}:{self._lexer.column}]:"
            #                      f" a variável '{name}' não foi declarada.")
            # self._log(f'{name}', end='', flush=True)  # ação semântica

            # lval_lst -> lval , lval_lst
            if self._lookahead == ",":
                self.match(Tag(","))
            else:
                break
            ret = self._lookahead.tag == Tags.ID
        # Not a left-value
        return ret

    def declr_or_rval_lst(self) -> List[ASTNode] | None:
        """Expressions
        Regras:
            declr_or_rval_lst -> :
                type {
                    s = symTable.get(id.lexeme);
                    print(id.lexeme); print(':');
                    print(s.type);
                }
                | = rval_lst | ϵ
        """
        if self._lookahead == ":":
            # declr_or_rval_lst -> : type
            self.match(Tag(":"))

            # TODO -> declr_or_rval_lst -> : = exprs (teremos que quebrar a regra ':' em 2 derivações)
            # self.match(TAG('='))

            t = self._lookahead

            if self._lookahead.tag != Tags.TYPE:
                raise SyntaxError(
                    f"Erro sintático [{self._lexer.filename}:{self._lexer.line}:{self._lexer.column}]:"
                    " era esperado um identificador de tipo após declaração."
                )
            self.match(Tags.TYPE)
            assert isinstance(t, Type)

            declarations = []
            while not self.queue_empty():
                id_token = self.deque()
                # assert id is not None
                name = str(id_token)
                # ação semântica: declara a variável na tabela de símbolos
                if not self._sym_table.insert(name, Symbol(name, str(t))):
                    raise SemanticError(
                        f"Erro semântico [{self._lexer.filename}:{self._lexer.column}]: "
                        f"a variável '[cyan]{name}[/cyan]' já foi declarada no escopo atual."
                    )
                # cria o nó de declaraçao na ast
                declarations.append(
                    VarDecl(name=name, var_type=str(t), value=Literal(None))
                )
            return declarations

        elif self._lookahead == "=":
            # declr_or_rval_lst -> = rval_lst
            self.match(Tag("="))
            valores = self.rval_lst() or []

            assignments = []

            while not self.queue_empty():
                id_token = self.deque()
                name = str(id_token)

                val_node = valores.pop(0) if valores else Literal(None)
                assignments.append(Assignment(name=name, value=val_node))
            return assignments
        return None

    def rval_lst(self) -> List[ASTNode] | None:
        """R-value list
        Regras:
            rval_lst -> rval [, rval_lst]'
            rval -> expr { id=deque()); print(id+'=') }
        """
        exprs = []
        if self.queue_empty():
            # Standalone expression
            while self._lookahead.tag == Tags.NUM or self._lookahead in ("+", "-"):
                exprs.append(self.opers())
                if self._lookahead == ",":
                    self.match(Tag(","))
                else:
                    return exprs
            return None if not exprs else exprs

        while True:
            exprs.append(self.opers())
            if self._lookahead == ",":
                self.match(Tag(","))
            else:
                break
        return exprs

    def queue_empty(self) -> bool:
        """Checks if the id_queue is empty."""
        return self._id_queue.empty()

    def queue(self, id: Id):
        """Puts an Id onto the id_queue."""
        self._id_queue.put(id)

    def deque(self) -> Id | None:
        """Gets an Id from the id_queue."""
        if self.queue_empty():
            return None
        return self._id_queue.get()

    def clear_queue(self):
        """Clears the id_queue."""
        while not self.queue_empty():
            self.deque()

    # def decls(self):
    #     '''
    #     Regras:
    #         decls -> decl decls | ϵ
    #         decl -> ID : tipo
    #     '''
    #     while self._lookahead.tag == TAG.TYPE:
    #         type = str(self._lookahead)
    #         if not self.match(TAG.TYPE):
    #             raise SyntaxError(f"Erro sintático [{self._lexer.filename}:{self._lexer.column}]:"
    #                              " era esperado um tipo de variável.")
    #
    #     name = ''
    #     ...
    #     s = Symbol(type, name)
    #     self._log("Declarado", s)
    #
    #     # insere a variável na tabela de símbolos
    #     if not self._sym_table.insert(name, s):
    #         self._log('Erro: a variável já foi declarada no escopo atual')
    #         raise SemanticError()

    def opers(self):
        """Operations
            Op. Relacionais de menor prioridade.
        Regras:
            # TODO -> Fix grammar comment
            opers -> digit oper'
            oper -> operator digit oper*
            operator -> > | < | == | != | <= | >=
        """
        left_node = self.additive()

        while True:
            if self._lookahead in (">", "<", "==", "!=", "<=", ">="):
                op_str = str(self._lookahead)
                self.match(Tag(op_str))
                right_node = self.additive()
                left_node = BinOp(left=left_node, op=op_str, right=right_node)
                self._infer_type(left_node)

            else:
                return left_node

    def additive(self):
        """Additive
            Soma e Subtração
        Regras:
            # TODO -> Fix grammar comment
            opers -> digit oper'
            oper -> operator digit oper*
            operator -> + | -
        """
        left_node = self.multiplicative()

        while True:
            if self._lookahead in ("+", "-"):
                op_str = str(self._lookahead)
                self.match(Tag(op_str))
                right_node = self.multiplicative()
                left_node = BinOp(left=left_node, op=op_str, right=right_node)
                self._infer_type(left_node)

            else:
                return left_node

    def multiplicative(self):
        """Multiplicative
            Multiplicação e divisão
        Regras:
            opers -> digit oper'
            oper -> operator digit oper*
            operator -> * | /
        """

        left_node = self.factor()

        while True:
            if self._lookahead in ("*", "/"):
                op_str = str(self._lookahead)
                self.match(Tag(op_str))
                right_node = self.factor()
                left_node = BinOp(left=left_node, op=op_str, right=right_node)
                self._infer_type(left_node)

            else:
                return left_node

    def factor(self) -> ASTNode:

        modifier = 1
        if self._lookahead == "+":
            self.match(Tag("+"))
        elif self._lookahead == "-":
            self.match(Tag("-"))
            modifier = -1

        if self._lookahead.tag == Tags.NUM:
            val = self._lookahead.value * modifier
            self.match(Tags.NUM)
            return Literal(value=val)

        elif self._lookahead.tag == Tags.TRUE:
            self.match(Tags.TRUE)
            return Literal(value=True)
        elif self._lookahead.tag == Tags.FALSE:
            self.match(Tags.FALSE)
            return Literal(value=False)

        # É uma String (texto entre aspas)?
        elif self._lookahead.tag == Tags.STR_LIT:
            val = self._lookahead.value
            self.match(Tags.STR_LIT)
            return Literal(value=val)

        elif self._lookahead.tag == "(":
            self.match(Tag("("))
            expr_node = self.opers()
            self.match(Tag(")"))
            return expr_node

        # É uma Variável sendo usada na conta (Identificador)?
        elif self._lookahead.tag == Tags.ID:
            name = str(self._lookahead)
            self.match(Tags.ID)

            sym = self._sym_table.find(name)
            if self._sym_table.find(name) is None:
                raise SemanticError(
                    f"Erro Semântico [{self._lexer.filename}:{self._lexer.line}:{self._lexer.column}]: "
                    f"A variável '{name}' não foi encontrada."
                )

            if self._lookahead == "(":
                self.match(Tag("("))
                args = []
                if self._lookahead != ")":
                    while True:
                        args.append(self.opers())
                        if self._lookahead == ",":
                            self.match(Tag(","))
                        else:
                            break
                self.match(Tag(")"))

                if sym.type == "function":  # and sym.params_count != -1:
                    if len(args) != len(sym.params):
                        raise SyntaxError(
                            f"Erro Sintático [{self._lexer.filename}:{self._lexer.line}:{self._lexer.column}]: "
                            f"A função '[cyan]{name}[/cyan]' exige {len(sym.params)} "
                            f"argumento{'s' if len(sym.params) > 1 else ''} "
                            # WARNING -> Verificar se `to_code` é seguro de ser usado aqui!
                            f"[purple]{sym.params}[/purple], mas recebeu {len(args)} [purple]{[arg.to_code() for arg in args]}[/purple]."
                        )
                    for i, arg_node in enumerate(args):
                        arg_type = self._infer_type(arg_node)
                        param_symbol = sym.params[i]
                        expected_type = param_symbol.type
                        param_name = param_symbol.var

                        if arg_type != "unknown" and arg_type != expected_type:
                            raise SemanticError(
                                f"Erro Semântico [{self._lexer.filename}:{self._lexer.line}:{self._lexer.column}]: "
                                f"O {i+1}° parâmetro '[orange]{param_name}[/orange]' da função '[cyan]{name}[/cyan]' "
                                f"esperava [purple]{expected_type}[/purple], mas recebeu [purple]{arg_type}[/purple]."
                            )
                return FunctionCall(name=name, args=args)

            return Identifier(name=name)

        else:
            raise SyntaxError(
                f"Erro Sintático [{self._lexer.filename}:{self._lexer.line}:{self._lexer.column}]: "
                "Esperado um valor, variável, booleano, string ou '('."
            )

        # def digit(self) -> Literal:
        """
        Regra: digit -> digit { print(digit) }
        """

    #   modifier = 1
    #   if self._lookahead == "+":
    #       self.match(Tag("+"))
    #   elif self._lookahead == "-":
    #       self.match(Tag("-"))
    #       modifier = -1

    #   if self._lookahead.tag == Tags.NUM:
    #       assert isinstance(self._lookahead, Num)
    #       num_value = self._lookahead.value * modifier
    #       # self._lexer._log(f"{self._lookahead}", end=" ", flush=True)
    #       self.match(self._lookahead.tag)
    #       return Literal(value=num_value)
    #   else:
    #       log_error(
    #           f"\nErro na linha {self._lexer.line}:"
    #           f"\033[35m dígito era esperado, obteve {self._lookahead} ao invés disso."
    #        )
    #        raise ParseError()

    def _infer_type(self, node: ASTNode) -> str:
        """Descobre o tipo de uma expressão e bloqueia misturas incompatíveis."""
        if isinstance(node, Literal):
            if isinstance(node.value, bool):
                return "bool"
            if isinstance(node.value, str):
                return "str"
            if isinstance(node.value, float):
                return "real"
            if isinstance(node.value, int):
                return "int"
            return "unknown"

        elif isinstance(node, Identifier):
            sym = self._sym_table.find(node.name)
            return sym.type if sym else "unknown"

        elif isinstance(node, BinOp):
            left_type = self._infer_type(node.left)
            right_type = self._infer_type(node.right)

            if (
                left_type != "unknown"
                and right_type != "unknown"
                and left_type != right_type
            ):
                # ------#
                if (left_type == "int" and right_type == "real") or (
                    left_type == "real" and right_type == "int"
                ):
                    left_type = "real"
                # ------#
                else:
                    raise SemanticError(
                        f"Erro Semântico [{self._lexer.filename}:{self._lexer.line}:{self._lexer.column}]: "
                        f"Tipos incompatíveis na operação."
                        f"Tentativa de combinar [purple]{left_type}[/purple] com [purple]{right_type}[/purple]."
                    )
            if node.op in (">", "<", "==", "!=", ">=", "<="):
                return "bool"

            return left_type

        elif isinstance(node, FunctionCall):
            return "int"
        return "unknown"

    def match(self, t: Tag):
        """Verifica se o caractere atual corresponde ao esperado e avança."""
        if t == self._lookahead.tag:
            self._lookahead = self._lexer.scan()
        else:
            # WATCH -> Melhorar mensagens de erro
            raise SyntaxError(
                f"Erro Sintático [{self._lexer.filename}:{self._lexer.line}:{self._lexer.column}]:\n"
                f"\tEra esperado '{t.name}', mas o compilador encontrou '{self._lookahead.tag.name}'."
            )


def main(source_filename: str, options: int, *args, **kwargs):
    if options & Options.LOG:
        tui = Tui(Tui.Mode.PARSER)
        istream: TuiInputStream  # pyright: ignore[reportRedeclaration]
        try:
            istream = TuiInputStream(
                source_filename, partial(tui.log_source, end="")
            )  # pyright: ignore[reportAssignmentType]
        except FileNotFoundError:
            log_error(f"Error: The file '{source_filename}' was not found.")
            sys.exit(EXIT_ERROR)
        lexer = Lexer(
            istream,
            tui.log_tokens,  # pyright: ignore[reportPossiblyUnboundVariable]
            source_filename=source_filename,
        )
        # Inicia o Parser com o conteúdo do arquivo
        parser = Parser(
            lexer,
            tui.log_ir,
            lambda message="", *args, **kwargs: tui.log_debug(
                f"[yellow]Warning {message}[/yellow]", *args, **kwargs
            ),
            optimize=not bool(options & Options.NO_OPTIMIZE),
        )
        tui.run(
            parser.start,  # pyright: ignore[reportArgumentType]
            True,
            not bool(options & Options.NO_EXCEPT_TREATMENT),
        )
    else:
        istream: InputStream
        try:
            istream = InputStream(source_filename)
        except FileNotFoundError:
            log_error(f"Error: File '{source_filename}' not found.")
            sys.exit(EXIT_ERROR)
        lexer = Lexer(
            istream,  # pyright: ignore[reportPossiblyUnboundVariable]
            lambda *args, **kwargs: None,
            source_filename=source_filename,
        )
        # Inicia o Parser com o conteúdo do arquivo
        parser = Parser(lexer, optimize=bool(options & Options.NO_OPTIMIZE))
        if options & Options.NO_EXCEPT_TREATMENT:
            parser.start()
        else:
            try:
                parser.start()
            except Exception as e:
                log_error(f"{e}")
        parser._log()  # quebra de linha final


def parse_append(parser: ArgParser) -> None:
    from .lexer import parse_append as append

    append(parser)
    # Option flags
    # TODO -> Verificar se isso está realmente sendo usado
    parser.add_argument(
        "-no", "--no-optimize", action="store_true", help="Disable optimizations"
    )


def fetch_options(args) -> int:
    from . import lexer

    # Build options bitmask
    options = lexer.fetch_options(args)
    if args.no_optimize:
        options |= Options.NO_OPTIMIZE
    return options


if __name__ == "__main__":
    from ..utils.arg_parser import ArgParser

    parser = ArgParser(
        description="Parser layer for your MiniLang source files. Does both the Syntax and Semantic Analysis generating an AST.\n"
        "The generated output is for debugging purposes only. To fully-compile code you need to call the gen layer with the MiniLang source.",
        add_help=False,  # we'll add custom help options to match original
    )
    parse_append(parser)

    # Parse arguments
    args = parser.parse_args()
    options = fetch_options(args)

    # Call main with parsed values
    main(args.source, options)
