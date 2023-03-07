#######################################
# IMPORTS
#######################################

from erro_usando_setas import *

import string
import os
import math

#######################################
# CONSTANTS
#######################################

DIGITOS = '0123456789'
LETRAS = string.ascii_letters
LETRAS_DIGITOS = LETRAS + DIGITOS


#######################################
# ERRORS
#######################################

class Erro:
    def __init__(self, pos_inicio, pos_final, nome_erro, detalhe):
        self.pos_inicio = pos_inicio
        self.pos_final = pos_final
        self.nome_erro = nome_erro
        self.detalhe = detalhe

    def as_string(self):
        resultado = f'{self.nome_erro}: {self.detalhe}\n'
        resultado += f'File {self.pos_inicio.fileName}, line {self.pos_inicio.ln + 1}'
        resultado += '\n\n' + \
            erro_usando_setas(self.pos_inicio.ftxt,
                              self.pos_inicio, self.pos_final)
        return resultado


class IllegalCharErro(Erro):
    def __init__(self, pos_inicio, pos_final, detalhe):
        super().__init__(pos_inicio, pos_final, 'Illegal Character', detalhe)


class ExpectedCharErro(Erro):
    def __init__(self, pos_inicio, pos_final, detalhe):
        super().__init__(pos_inicio, pos_final, 'Expected Character', detalhe)


class InvalidSyntaxErro(Erro):
    def __init__(self, pos_inicio, pos_final, detalhe=''):
        super().__init__(pos_inicio, pos_final, 'Invalid Syntax', detalhe)


class RTErro(Erro):
    def __init__(self, pos_inicio, pos_final, detalhe, context):
        super().__init__(pos_inicio, pos_final, 'Runtime Erro', detalhe)
        self.context = context

    def as_string(self):
        resultado = self.generate_traceback()
        resultado += f'{self.nome_erro}: {self.detalhe}'
        resultado += '\n\n' + \
            erro_usando_setas(self.pos_inicio.ftxt,
                              self.pos_inicio, self.pos_final)
        return resultado

    def generate_traceback(self):
        resultado = ''
        pos = self.pos_inicio
        ctx = self.context

        while ctx:
            resultado = f'  File {pos.fileName}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + resultado
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return 'Traceback (most recent call last):\n' + resultado


#######################################
# POSITION
#######################################

class Position:
    def __init__(self, idx, ln, col, fileName, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fileName = fileName
        self.ftxt = ftxt

    def advance(self, _peek=None):
        self.idx += 1
        self.col += 1

        if _peek == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fileName, self.ftxt)


#######################################
# TOKENS
#######################################

TOKENTYPE_INT = 'INT'
TOKENTYPE_FLOAT = 'FLOAT'
TOKENTYPE_STRING = 'STRING'
TOKENTYPE_IDENTIFIER = 'IDENTIFIER'
TOKENTYPE_KEYWORD = 'KEYWORD'
TOKENTYPE_SUM = 'SUM'
TOKENTYPE_MINUS = 'MINUS'
TOKENTYPE_MUL = 'MUL'
TOKENTYPE_DIV = 'DIV'
TOKENTYPE_POW = 'POW'
TOKENTYPE_EQ = 'EQ'
TOKENTYPE_LPAREN = 'LPAREN'
TOKENTYPE_RPAREN = 'RPAREN'
TOKENTYPE_LSQUARE = 'LSQUARE'
TOKENTYPE_RSQUARE = 'RSQUARE'
TOKENTYPE_EE = 'EE'
TOKENTYPE_NE = 'NE'
TOKENTYPE_LT = 'LT'
TOKENTYPE_GT = 'GT'
TOKENTYPE_LTE = 'LTE'
TOKENTYPE_GTE = 'GTE'
TOKENTYPE_COMMA = 'COMMA'
TOKENTYPE_ARROW = 'ARROW'
TOKENTYPE_NEWLINE = 'NEWLINE'
TOKENTYPE_EOF = 'EOF'

KEYWORDS = [
    'VAR',
    'AND',
    'OR',
    'NOT',
    'IF',
    'ELIF',
    'ELSE',
    'FOR',
    'TO',
    'STEP',
    'WHILE',
    'DEF',
    'THEN',
    'END',
    'RETURN',
    'CONTINUE',
    'BREAK',
]


class Token:
    def __init__(self, type_, value=None, pos_inicio=None, pos_final=None):
        self.type = type_
        self.value = value

        if pos_inicio:
            self.pos_inicio = pos_inicio.copy()
            self.pos_final = pos_inicio.copy()
            self.pos_final.advance()

        if pos_final:
            self.pos_final = pos_final.copy()

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'


#######################################
# LEXER
#######################################

class Lexer:
    def __init__(self, fileName, text):
        self.fileName = fileName
        self.text = text
        self.pos = Position(-1, 0, -1, fileName, text)
        self._peek = None
        self.advance()

    def advance(self):
        self.pos.advance(self._peek)
        self._peek = self.text[self.pos.idx] if self.pos.idx < len(
            self.text) else None

    def make_tokens(self):
        tokens = []

        while self._peek != None:
            if self._peek in ' \t':
                self.advance()
            elif self._peek == '#':
                self.skip_comment()
            elif self._peek in ';\n':
                tokens.append(Token(TOKENTYPE_NEWLINE, pos_inicio=self.pos))
                self.advance()
            elif self._peek in DIGITOS:
                tokens.append(self.make_number())
            elif self._peek in LETRAS:
                tokens.append(self.make_identifier())
            elif self._peek == '"':
                tokens.append(self.make_string())
            elif self._peek == '+':
                tokens.append(Token(TOKENTYPE_SUM, pos_inicio=self.pos))
                self.advance()
            elif self._peek == '-':
                tokens.append(self.make_minus_or_arrow())
            elif self._peek == '*':
                tokens.append(Token(TOKENTYPE_MUL, pos_inicio=self.pos))
                self.advance()
            elif self._peek == '/':
                tokens.append(Token(TOKENTYPE_DIV, pos_inicio=self.pos))
                self.advance()
            elif self._peek == '^':
                tokens.append(Token(TOKENTYPE_POW, pos_inicio=self.pos))
                self.advance()
            elif self._peek == '(':
                tokens.append(Token(TOKENTYPE_LPAREN, pos_inicio=self.pos))
                self.advance()
            elif self._peek == ')':
                tokens.append(Token(TOKENTYPE_RPAREN, pos_inicio=self.pos))
                self.advance()
            elif self._peek == '[':
                tokens.append(Token(TOKENTYPE_LSQUARE, pos_inicio=self.pos))
                self.advance()
            elif self._peek == ']':
                tokens.append(Token(TOKENTYPE_RSQUARE, pos_inicio=self.pos))
                self.advance()
            elif self._peek == '!':
                token, error = self.make_not_equals()
                if error:
                    return [], error
                tokens.append(token)
            elif self._peek == '=':
                tokens.append(self.make_equals())
            elif self._peek == '<':
                tokens.append(self.make_less_than())
            elif self._peek == '>':
                tokens.append(self.make_greater_than())
            elif self._peek == ',':
                tokens.append(Token(TOKENTYPE_COMMA, pos_inicio=self.pos))
                self.advance()
            else:
                pos_inicio = self.pos.copy()
                char = self._peek
                self.advance()
                return [], IllegalCharErro(pos_inicio, self.pos, "'" + char + "'")

        tokens.append(Token(TOKENTYPE_EOF, pos_inicio=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_inicio = self.pos.copy()

        while self._peek != None and self._peek in DIGITOS + '.':
            if self._peek == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self._peek
            self.advance()

        if dot_count == 0:
            return Token(TOKENTYPE_INT, int(num_str), pos_inicio, self.pos)
        else:
            return Token(TOKENTYPE_FLOAT, float(num_str), pos_inicio, self.pos)

    def make_string(self):
        string = ''
        pos_inicio = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        while self._peek != None and (self._peek != '"' or escape_character):
            if escape_character:
                string += escape_characters.get(self._peek, self._peek)
            else:
                if self._peek == '\\':
                    escape_character = True
                else:
                    string += self._peek
            self.advance()
            escape_character = False

        self.advance()
        return Token(TOKENTYPE_STRING, string, pos_inicio, self.pos)

    def make_identifier(self):
        id_str = ''
        pos_inicio = self.pos.copy()

        while self._peek != None and self._peek in LETRAS_DIGITOS + '_':
            id_str += self._peek
            self.advance()

        tok_type = TOKENTYPE_KEYWORD if id_str in KEYWORDS else TOKENTYPE_IDENTIFIER
        return Token(tok_type, id_str, pos_inicio, self.pos)

    def make_minus_or_arrow(self):
        tok_type = TOKENTYPE_MINUS
        pos_inicio = self.pos.copy()
        self.advance()

        if self._peek == '>':
            self.advance()
            tok_type = TOKENTYPE_ARROW

        return Token(tok_type, pos_inicio=pos_inicio, pos_final=self.pos)

    def make_not_equals(self):
        pos_inicio = self.pos.copy()
        self.advance()

        if self._peek == '=':
            self.advance()
            return Token(TOKENTYPE_NE, pos_inicio=pos_inicio, pos_final=self.pos), None

        self.advance()
        return None, ExpectedCharErro(pos_inicio, self.pos, "'=' (after '!')")

    def make_equals(self):
        tok_type = TOKENTYPE_EQ
        pos_inicio = self.pos.copy()
        self.advance()

        if self._peek == '=':
            self.advance()
            tok_type = TOKENTYPE_EE

        return Token(tok_type, pos_inicio=pos_inicio, pos_final=self.pos)

    def make_less_than(self):
        tok_type = TOKENTYPE_LT
        pos_inicio = self.pos.copy()
        self.advance()

        if self._peek == '=':
            self.advance()
            tok_type = TOKENTYPE_LTE

        return Token(tok_type, pos_inicio=pos_inicio, pos_final=self.pos)

    def make_greater_than(self):
        tok_type = TOKENTYPE_GT
        pos_inicio = self.pos.copy()
        self.advance()

        if self._peek == '=':
            self.advance()
            tok_type = TOKENTYPE_GTE

        return Token(tok_type, pos_inicio=pos_inicio, pos_final=self.pos)

    def skip_comment(self):
        self.advance()

        while self._peek != '\n':
            self.advance()

        self.advance()


#######################################
# NODES
#######################################

class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_inicio = self.tok.pos_inicio
        self.pos_final = self.tok.pos_final

    def __repr__(self):
        return f'{self.tok}'


class StringNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_inicio = self.tok.pos_inicio
        self.pos_final = self.tok.pos_final

    def __repr__(self):
        return f'{self.tok}'


class ListNode:
    def __init__(self, element_nodes, pos_inicio, pos_final):
        self.element_nodes = element_nodes

        self.pos_inicio = pos_inicio
        self.pos_final = pos_final


class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_inicio = self.var_name_tok.pos_inicio
        self.pos_final = self.var_name_tok.pos_final


class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_inicio = self.var_name_tok.pos_inicio
        self.pos_final = self.value_node.pos_final


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_inicio = self.left_node.pos_inicio
        self.pos_final = self.right_node.pos_final

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_inicio = self.op_tok.pos_inicio
        self.pos_final = node.pos_final

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_inicio = self.cases[0][0].pos_inicio
        self.pos_final = (
            self.else_case or self.cases[len(self.cases) - 1])[0].pos_final


class ForNode:
    def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_inicio = self.var_name_tok.pos_inicio
        self.pos_final = self.body_node.pos_final


class WhileNode:
    def __init__(self, condition_node, body_node, should_return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_inicio = self.condition_node.pos_inicio
        self.pos_final = self.body_node.pos_final


class FuncDefNode:
    def __init__(self, var_name_tok, arg_name_toks, body_node, should_auto_return):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.should_auto_return = should_auto_return

        if self.var_name_tok:
            self.pos_inicio = self.var_name_tok.pos_inicio
        elif len(self.arg_name_toks) > 0:
            self.pos_inicio = self.arg_name_toks[0].pos_inicio
        else:
            self.pos_inicio = self.body_node.pos_inicio

        self.pos_final = self.body_node.pos_final


class CallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_inicio = self.node_to_call.pos_inicio

        if len(self.arg_nodes) > 0:
            self.pos_final = self.arg_nodes[len(self.arg_nodes) - 1].pos_final
        else:
            self.pos_final = self.node_to_call.pos_final


class ReturnNode:
    def __init__(self, node_to_return, pos_inicio, pos_final):
        self.node_to_return = node_to_return

        self.pos_inicio = pos_inicio
        self.pos_final = pos_final


class ContinueNode:
    def __init__(self, pos_inicio, pos_final):
        self.pos_inicio = pos_inicio
        self.pos_final = pos_final


class BreakNode:
    def __init__(self, pos_inicio, pos_final):
        self.pos_inicio = pos_inicio
        self.pos_final = pos_final


#######################################
# PARSE RESULT
#######################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1

    def register(self, res):
        self.last_registered_advance_count = res.advance_count
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        return res.node

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
        return self


#######################################
# PARSER
#######################################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        res = self.Stmt()
        if not res.error and self.current_tok.type != TOKENTYPE_EOF:
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                "Token cannot appear after previous tokens"
            ))
        return res

    ###################################

    def Stmt(self):
        res = ParseResult()
        Stmt = []
        pos_inicio = self.current_tok.pos_inicio.copy()

        while self.current_tok.type == TOKENTYPE_NEWLINE:
            res.register_advancement()
            self.advance()

        statement = res.register(self.statement())
        if res.error:
            return res
        Stmt.append(statement)

        more_Stmt = True

        while True:
            newline_count = 0
            while self.current_tok.type == TOKENTYPE_NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_Stmt = False

            if not more_Stmt:
                break
            statement = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_Stmt = False
                continue
            Stmt.append(statement)

        return res.success(ListNode(
            Stmt,
            pos_inicio,
            self.current_tok.pos_final.copy()
        ))

    def statement(self):
        res = ParseResult()
        pos_inicio = self.current_tok.pos_inicio.copy()

        if self.current_tok.matches(TOKENTYPE_KEYWORD, 'RETURN'):
            res.register_advancement()
            self.advance()

            expr = res.try_register(self.expr())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_inicio, self.current_tok.pos_inicio.copy()))

        if self.current_tok.matches(TOKENTYPE_KEYWORD, 'CONTINUE'):
            res.register_advancement()
            self.advance()
            return res.success(ContinueNode(pos_inicio, self.current_tok.pos_inicio.copy()))

        if self.current_tok.matches(TOKENTYPE_KEYWORD, 'BREAK'):
            res.register_advancement()
            self.advance()
            return res.success(BreakNode(pos_inicio, self.current_tok.pos_inicio.copy()))

        expr = res.register(self.expr())
        if res.error:
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                "Expected 'RETURN', 'CONTINUE', 'BREAK', 'VAR', 'IF', 'FOR', 'WHILE', 'DEF', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
            ))
        return res.success(expr)

    def expr(self):
        res = ParseResult()

        if self.current_tok.matches(TOKENTYPE_KEYWORD, 'VAR'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TOKENTYPE_IDENTIFIER:
                return res.failure(InvalidSyntaxErro(
                    self.current_tok.pos_inicio, self.current_tok.pos_final,
                    "Expected identifier"
                ))

            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TOKENTYPE_EQ:
                return res.failure(InvalidSyntaxErro(
                    self.current_tok.pos_inicio, self.current_tok.pos_final,
                    "Expected '='"
                ))

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            return res.success(VarAssignNode(var_name, expr))

        node = res.register(self.bin_op(
            self.comp_expr, ((TOKENTYPE_KEYWORD, 'AND'), (TOKENTYPE_KEYWORD, 'OR'))))

        if res.error:
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                "Expected 'VAR', 'IF', 'FOR', 'WHILE', 'DEF', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
            ))

        return res.success(node)

    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(TOKENTYPE_KEYWORD, 'NOT'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(self.bin_op(self.arith_expr, (TOKENTYPE_EE, TOKENTYPE_NE,
                            TOKENTYPE_LT, TOKENTYPE_GT, TOKENTYPE_LTE, TOKENTYPE_GTE)))

        if res.error:
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                "Expected int, float, identifier, '+', '-', '(', '[', 'IF', 'FOR', 'WHILE', 'DEF' or 'NOT'"
            ))

        return res.success(node)

    def arith_expr(self):
        return self.bin_op(self.term, (TOKENTYPE_SUM, TOKENTYPE_MINUS))

    def term(self):
        return self.bin_op(self.factor, (TOKENTYPE_MUL, TOKENTYPE_DIV))

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TOKENTYPE_SUM, TOKENTYPE_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def power(self):
        return self.bin_op(self.call, (TOKENTYPE_POW,), self.factor)

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error:
            return res

        if self.current_tok.type == TOKENTYPE_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == TOKENTYPE_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxErro(
                        self.current_tok.pos_inicio, self.current_tok.pos_final,
                        "Expected ')', 'VAR', 'IF', 'FOR', 'WHILE', 'DEF', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
                    ))

                while self.current_tok.type == TOKENTYPE_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error:
                        return res

                if self.current_tok.type != TOKENTYPE_RPAREN:
                    return res.failure(InvalidSyntaxErro(
                        self.current_tok.pos_inicio, self.current_tok.pos_final,
                        f"Expected ',' or ')'"
                    ))

                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TOKENTYPE_INT, TOKENTYPE_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == TOKENTYPE_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))

        elif tok.type == TOKENTYPE_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == TOKENTYPE_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == TOKENTYPE_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxErro(
                    self.current_tok.pos_inicio, self.current_tok.pos_final,
                    "Expected ')'"
                ))

        elif tok.type == TOKENTYPE_LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error:
                return res
            return res.success(list_expr)

        elif tok.matches(TOKENTYPE_KEYWORD, 'IF'):
            if_expr = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expr)

        elif tok.matches(TOKENTYPE_KEYWORD, 'FOR'):
            for_expr = res.register(self.for_expr())
            if res.error:
                return res
            return res.success(for_expr)

        elif tok.matches(TOKENTYPE_KEYWORD, 'WHILE'):
            while_expr = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)

        elif tok.matches(TOKENTYPE_KEYWORD, 'DEF'):
            func_def = res.register(self.func_def())
            if res.error:
                return res
            return res.success(func_def)

        return res.failure(InvalidSyntaxErro(
            tok.pos_inicio, tok.pos_final,
            "Expected int, float, identifier, '+', '-', '(', '[', IF', 'FOR', 'WHILE', 'DEF'"
        ))

    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_inicio = self.current_tok.pos_inicio.copy()

        if self.current_tok.type != TOKENTYPE_LSQUARE:
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                f"Expected '['"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TOKENTYPE_RSQUARE:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(InvalidSyntaxErro(
                    self.current_tok.pos_inicio, self.current_tok.pos_final,
                    "Expected ']', 'VAR', 'IF', 'FOR', 'WHILE', 'DEF', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
                ))

            while self.current_tok.type == TOKENTYPE_COMMA:
                res.register_advancement()
                self.advance()

                element_nodes.append(res.register(self.expr()))
                if res.error:
                    return res

            if self.current_tok.type != TOKENTYPE_RSQUARE:
                return res.failure(InvalidSyntaxErro(
                    self.current_tok.pos_inicio, self.current_tok.pos_final,
                    f"Expected ',' or ']'"
                ))

            res.register_advancement()
            self.advance()

        return res.success(ListNode(
            element_nodes,
            pos_inicio,
            self.current_tok.pos_final.copy()
        ))

    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases('IF'))
        if res.error:
            return res
        cases, else_case = all_cases
        return res.success(IfNode(cases, else_case))

    def if_expr_b(self):
        return self.if_expr_cases('ELIF')

    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(TOKENTYPE_KEYWORD, 'ELSE'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type == TOKENTYPE_NEWLINE:
                res.register_advancement()
                self.advance()

                Stmt = res.register(self.Stmt())
                if res.error:
                    return res
                else_case = (Stmt, True)

                if self.current_tok.matches(TOKENTYPE_KEYWORD, 'END'):
                    res.register_advancement()
                    self.advance()
                else:
                    return res.failure(InvalidSyntaxErro(
                        self.current_tok.pos_inicio, self.current_tok.pos_final,
                        "Expected 'END'"
                    ))
            else:
                expr = res.register(self.statement())
                if res.error:
                    return res
                else_case = (expr, False)

        return res.success(else_case)

    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_tok.matches(TOKENTYPE_KEYWORD, 'ELIF'):
            all_cases = res.register(self.if_expr_b())
            if res.error:
                return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error:
                return res

        return res.success((cases, else_case))

    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TOKENTYPE_KEYWORD, case_keyword):
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                f"Expected '{case_keyword}'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TOKENTYPE_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                f"Expected 'THEN'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TOKENTYPE_NEWLINE:
            res.register_advancement()
            self.advance()

            Stmt = res.register(self.Stmt())
            if res.error:
                return res
            cases.append((condition, Stmt, True))

            if self.current_tok.matches(TOKENTYPE_KEYWORD, 'END'):
                res.register_advancement()
                self.advance()
            else:
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error:
                    return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = res.register(self.statement())
            if res.error:
                return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error:
                return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return res.success((cases, else_case))

    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TOKENTYPE_KEYWORD, 'FOR'):
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                f"Expected 'FOR'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TOKENTYPE_IDENTIFIER:
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                f"Expected identifier"
            ))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TOKENTYPE_EQ:
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                f"Expected '='"
            ))

        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TOKENTYPE_KEYWORD, 'TO'):
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                f"Expected 'TO'"
            ))

        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.matches(TOKENTYPE_KEYWORD, 'STEP'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error:
                return res
        else:
            step_value = None

        if not self.current_tok.matches(TOKENTYPE_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                f"Expected 'THEN'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TOKENTYPE_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.Stmt())
            if res.error:
                return res

            if not self.current_tok.matches(TOKENTYPE_KEYWORD, 'END'):
                return res.failure(InvalidSyntaxErro(
                    self.current_tok.pos_inicio, self.current_tok.pos_final,
                    f"Expected 'END'"
                ))

            res.register_advancement()
            self.advance()

            return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))

        body = res.register(self.statement())
        if res.error:
            return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))

    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TOKENTYPE_KEYWORD, 'WHILE'):
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                f"Expected 'WHILE'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TOKENTYPE_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                f"Expected 'THEN'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TOKENTYPE_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.Stmt())
            if res.error:
                return res

            if not self.current_tok.matches(TOKENTYPE_KEYWORD, 'END'):
                return res.failure(InvalidSyntaxErro(
                    self.current_tok.pos_inicio, self.current_tok.pos_final,
                    f"Expected 'END'"
                ))

            res.register_advancement()
            self.advance()

            return res.success(WhileNode(condition, body, True))

        body = res.register(self.statement())
        if res.error:
            return res

        return res.success(WhileNode(condition, body, False))

    def func_def(self):
        res = ParseResult()

        if not self.current_tok.matches(TOKENTYPE_KEYWORD, 'DEF'):
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                f"Expected 'DEF'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TOKENTYPE_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TOKENTYPE_LPAREN:
                return res.failure(InvalidSyntaxErro(
                    self.current_tok.pos_inicio, self.current_tok.pos_final,
                    f"Expected '('"
                ))
        else:
            var_name_tok = None
            if self.current_tok.type != TOKENTYPE_LPAREN:
                return res.failure(InvalidSyntaxErro(
                    self.current_tok.pos_inicio, self.current_tok.pos_final,
                    f"Expected identifier or '('"
                ))

        res.register_advancement()
        self.advance()
        arg_name_toks = []

        if self.current_tok.type == TOKENTYPE_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TOKENTYPE_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TOKENTYPE_IDENTIFIER:
                    return res.failure(InvalidSyntaxErro(
                        self.current_tok.pos_inicio, self.current_tok.pos_final,
                        f"Expected identifier"
                    ))

                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TOKENTYPE_RPAREN:
                return res.failure(InvalidSyntaxErro(
                    self.current_tok.pos_inicio, self.current_tok.pos_final,
                    f"Expected ',' or ')'"
                ))
        else:
            if self.current_tok.type != TOKENTYPE_RPAREN:
                return res.failure(InvalidSyntaxErro(
                    self.current_tok.pos_inicio, self.current_tok.pos_final,
                    f"Expected identifier or ')'"
                ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TOKENTYPE_ARROW:
            res.register_advancement()
            self.advance()

            body = res.register(self.expr())
            if res.error:
                return res

            return res.success(FuncDefNode(
                var_name_tok,
                arg_name_toks,
                body,
                True
            ))

        if self.current_tok.type != TOKENTYPE_NEWLINE:
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                f"Expected '->' or NEWLINE"
            ))

        res.register_advancement()
        self.advance()

        body = res.register(self.Stmt())
        if res.error:
            return res

        if not self.current_tok.matches(TOKENTYPE_KEYWORD, 'END'):
            return res.failure(InvalidSyntaxErro(
                self.current_tok.pos_inicio, self.current_tok.pos_final,
                f"Expected 'END'"
            ))

        res.register_advancement()
        self.advance()

        return res.success(FuncDefNode(
            var_name_tok,
            arg_name_toks,
            body,
            False
        ))

    ###################################

    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error:
            return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)


#######################################
# RUNTIME RESULT
#######################################

class RTResult:
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_should_continue = False
        self.loop_should_break = False

    def register(self, res):
        self.error = res.error
        self.func_return_value = res.func_return_value
        self.loop_should_continue = res.loop_should_continue
        self.loop_should_break = res.loop_should_break
        return res.value

    def success(self, value):
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        return self

    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self

    def should_return(self):
        # Note: this will allow you to continue and break outside the current function
        return (
            self.error or
            self.func_return_value or
            self.loop_should_continue or
            self.loop_should_break
        )


#######################################
# VALUES
#######################################

class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_inicio=None, pos_final=None):
        self.pos_inicio = pos_inicio
        self.pos_final = pos_final
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def powed_by(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self, other):
        return None, self.illegal_operation(other)

    def execute(self, args):
        return RTResult().failure(self.illegal_operation())

    def copy(self):
        raise Exception('No copy method defined')

    def is_true(self):
        return False

    def illegal_operation(self, other=None):
        if not other:
            other = self
        return RTErro(
            self.pos_inicio, other.pos_final,
            'Illegal operation',
            self.context
        )


class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTErro(
                    other.pos_inicio, other.pos_final,
                    'Division by zero',
                    self.context
                )

            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def powed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_inicio, self.pos_final)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
Number.math_PI = Number(math.pi)


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def is_true(self):
        return len(self.value) > 0

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_inicio, self.pos_final)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'"{self.value}"'


class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def added_to(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None

    def subbed_by(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, RTErro(
                    other.pos_inicio, other.pos_final,
                    'Element at this index could not be removed from list because index is out of bounds',
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RTErro(
                    other.pos_inicio, other.pos_final,
                    'Element at this index could not be retrieved from list because index is out of bounds',
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)

    def copy(self):
        copy = List(self.elements)
        copy.set_pos(self.pos_inicio, self.pos_final)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        return ", ".join([str(x) for x in self.elements])

    def __repr__(self):
        return f'[{", ".join([repr(x) for x in self.elements])}]'


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_inicio)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        res = RTResult()

        if len(args) > len(arg_names):
            return res.failure(RTErro(
                self.pos_inicio, self.pos_final,
                f"{len(args) - len(arg_names)} too many args passed into {self}",
                self.context
            ))

        if len(args) < len(arg_names):
            return res.failure(RTErro(
                self.pos_inicio, self.pos_final,
                f"{len(arg_names) - len(args)} too few args passed into {self}",
                self.context
            ))

        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return():
            return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, should_auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_auto_return = should_auto_return

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(
            self.arg_names, args, exec_ctx))
        if res.should_return():
            return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.should_return() and res.func_return_value == None:
            return res

        ret_value = (
            value if self.should_auto_return else None) or res.func_return_value or Number.null
        return res.success(ret_value)

    def copy(self):
        copy = Function(self.name, self.body_node,
                        self.arg_names, self.should_auto_return)
        copy.set_context(self.context)
        copy.set_pos(self.pos_inicio, self.pos_final)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"


class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        res = RTResult()
        exec_ctx = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(
            method.arg_names, args, exec_ctx))
        if res.should_return():
            return res

        return_value = res.register(method(exec_ctx))
        if res.should_return():
            return res
        return res.success(return_value)

    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_inicio, self.pos_final)
        return copy

    def __repr__(self):
        return f"<built-in function {self.name}>"

    #####################################

    def execute_print(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get('value')))
        return RTResult().success(Number.null)

    execute_print.arg_names = ['value']

    def execute_print_ret(self, exec_ctx):
        return RTResult().success(String(str(exec_ctx.symbol_table.get('value'))))

    execute_print_ret.arg_names = ['value']

    def execute_input(self, exec_ctx):
        text = input()
        return RTResult().success(String(text))

    execute_input.arg_names = []

    def execute_input_int(self, exec_ctx):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again!")
        return RTResult().success(Number(number))

    execute_input_int.arg_names = []

    def execute_clear(self, exec_ctx):
        os.system('cls' if os.name == 'nt' else 'cls')
        return RTResult().success(Number.null)

    execute_clear.arg_names = []

    def execute_is_number(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RTResult().success(Number.true if is_number else Number.false)

    execute_is_number.arg_names = ["value"]

    def execute_is_string(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RTResult().success(Number.true if is_number else Number.false)

    execute_is_string.arg_names = ["value"]

    def execute_is_list(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RTResult().success(Number.true if is_number else Number.false)

    execute_is_list.arg_names = ["value"]

    def execute_is_function(self, exec_ctx):
        is_number = isinstance(
            exec_ctx.symbol_table.get("value"), BaseFunction)
        return RTResult().success(Number.true if is_number else Number.false)

    execute_is_function.arg_names = ["value"]

    def execute_append(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")

        if not isinstance(list_, List):
            return RTResult().failure(RTErro(
                self.pos_inicio, self.pos_final,
                "First argument must be list",
                exec_ctx
            ))

        list_.elements.append(value)
        return RTResult().success(Number.null)

    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")

        if not isinstance(list_, List):
            return RTResult().failure(RTErro(
                self.pos_inicio, self.pos_final,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(index, Number):
            return RTResult().failure(RTErro(
                self.pos_inicio, self.pos_final,
                "Second argument must be number",
                exec_ctx
            ))

        try:
            element = list_.elements.pop(index.value)
        except:
            return RTResult().failure(RTErro(
                self.pos_inicio, self.pos_final,
                'Element at this index could not be removed from list because index is out of bounds',
                exec_ctx
            ))
        return RTResult().success(element)

    execute_pop.arg_names = ["list", "index"]

    def execute_extend(self, exec_ctx):
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")

        if not isinstance(listA, List):
            return RTResult().failure(RTErro(
                self.pos_inicio, self.pos_final,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(listB, List):
            return RTResult().failure(RTErro(
                self.pos_inicio, self.pos_final,
                "Second argument must be list",
                exec_ctx
            ))

        listA.elements.extend(listB.elements)
        return RTResult().success(Number.null)

    execute_extend.arg_names = ["listA", "listB"]

    def execute_len(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")

        if not isinstance(list_, List):
            return RTResult().failure(RTErro(
                self.pos_inicio, self.pos_final,
                "Argument must be list",
                exec_ctx
            ))

        return RTResult().success(Number(len(list_.elements)))

    execute_len.arg_names = ["list"]

    def execute_run(self, exec_ctx):
        fileName = exec_ctx.symbol_table.get("fileName")

        if not isinstance(fileName, String):
            return RTResult().failure(RTErro(
                self.pos_inicio, self.pos_final,
                "Second argument must be string",
                exec_ctx
            ))

        fileName = fileName.value

        try:
            with open(fileName, "r") as f:
                script = f.read()
        except Exception as e:
            return RTResult().failure(RTErro(
                self.pos_inicio, self.pos_final,
                f"Failed to load script \"{fileName}\"\n" + str(e),
                exec_ctx
            ))

        _, error = run(fileName, script)

        if error:
            return RTResult().failure(RTErro(
                self.pos_inicio, self.pos_final,
                f"Failed to finish executing script \"{fileName}\"\n" +
                error.as_string(),
                exec_ctx
            ))

        return RTResult().success(Number.null)

    execute_run.arg_names = ["fileName"]


BuiltInFunction.print = BuiltInFunction("print")
BuiltInFunction.print_ret = BuiltInFunction("print_ret")
BuiltInFunction.input = BuiltInFunction("input")
BuiltInFunction.input_int = BuiltInFunction("input_int")
BuiltInFunction.clear = BuiltInFunction("clear")
BuiltInFunction.is_number = BuiltInFunction("is_number")
BuiltInFunction.is_string = BuiltInFunction("is_string")
BuiltInFunction.is_list = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append = BuiltInFunction("append")
BuiltInFunction.pop = BuiltInFunction("pop")
BuiltInFunction.extend = BuiltInFunction("extend")
BuiltInFunction.len = BuiltInFunction("len")
BuiltInFunction.run = BuiltInFunction("run")


#######################################
# CONTEXT
#######################################

class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None


#######################################
# SYMBOL TABLE
#######################################

class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


#######################################
# INTERPRETER
#######################################

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    ###################################

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(
                node.pos_inicio, node.pos_final)
        )

    def visit_StringNode(self, node, context):
        return RTResult().success(
            String(node.tok.value).set_context(context).set_pos(
                node.pos_inicio, node.pos_final)
        )

    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context)))
            if res.should_return():
                return res

        return res.success(
            List(elements).set_context(context).set_pos(
                node.pos_inicio, node.pos_final)
        )

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(RTErro(
                node.pos_inicio, node.pos_final,
                f"'{var_name}' is not defined",
                context
            ))

        value = value.copy().set_pos(node.pos_inicio, node.pos_final).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.should_return():
            return res

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.should_return():
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.should_return():
            return res

        if node.op_tok.type == TOKENTYPE_SUM:
            resultado, error = left.added_to(right)
        elif node.op_tok.type == TOKENTYPE_MINUS:
            resultado, error = left.subbed_by(right)
        elif node.op_tok.type == TOKENTYPE_MUL:
            resultado, error = left.multed_by(right)
        elif node.op_tok.type == TOKENTYPE_DIV:
            resultado, error = left.dived_by(right)
        elif node.op_tok.type == TOKENTYPE_POW:
            resultado, error = left.powed_by(right)
        elif node.op_tok.type == TOKENTYPE_EE:
            resultado, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TOKENTYPE_NE:
            resultado, error = left.get_comparison_ne(right)
        elif node.op_tok.type == TOKENTYPE_LT:
            resultado, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TOKENTYPE_GT:
            resultado, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TOKENTYPE_LTE:
            resultado, error = left.get_comparison_lte(right)
        elif node.op_tok.type == TOKENTYPE_GTE:
            resultado, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(TOKENTYPE_KEYWORD, 'AND'):
            resultado, error = left.anded_by(right)
        elif node.op_tok.matches(TOKENTYPE_KEYWORD, 'OR'):
            resultado, error = left.ored_by(right)

        if error:
            return res.failure(error)
        else:
            return res.success(resultado.set_pos(node.pos_inicio, node.pos_final))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return():
            return res

        error = None

        if node.op_tok.type == TOKENTYPE_MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.matches(TOKENTYPE_KEYWORD, 'NOT'):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_inicio, node.pos_final))

    def visit_IfNode(self, node, context):
        res = RTResult()

        for condition, expr, should_return_null in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return():
                return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return():
                    return res
                return res.success(Number.null if should_return_null else expr_value)

        if node.else_case:
            expr, should_return_null = node.else_case
            expr_value = res.register(self.visit(expr, context))
            if res.should_return():
                return res
            return res.success(Number.null if should_return_null else expr_value)

        return res.success(Number.null)

    def visit_ForNode(self, node, context):
        res = RTResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.should_return():
            return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.should_return():
            return res

        if node.step_value_node:
            step_value = res.register(
                self.visit(node.step_value_node, context))
            if res.should_return():
                return res
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >= 0:
            def condition(): return i < end_value.value
        else:
            def condition(): return i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False:
                return res

            if res.loop_should_continue:
                continue

            if res.loop_should_break:
                break

            elements.append(value)

        return res.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(
                node.pos_inicio, node.pos_final)
        )

    def visit_WhileNode(self, node, context):
        res = RTResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return():
                return res

            if not condition.is_true():
                break

            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False:
                return res

            if res.loop_should_continue:
                continue

            if res.loop_should_break:
                break

            elements.append(value)

        return res.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(
                node.pos_inicio, node.pos_final)
        )

    def visit_FuncDefNode(self, node, context):
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(
            node.pos_inicio, node.pos_final)

        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.should_return():
            return res
        value_to_call = value_to_call.copy().set_pos(node.pos_inicio, node.pos_final)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.should_return():
                return res

        return_value = res.register(value_to_call.execute(args))
        if res.should_return():
            return res
        return_value = return_value.copy().set_pos(
            node.pos_inicio, node.pos_final).set_context(context)
        return res.success(return_value)

    def visit_ReturnNode(self, node, context):
        res = RTResult()

        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context))
            if res.should_return():
                return res
        else:
            value = Number.null

        return res.success_return(value)

    def visit_ContinueNode(self, node, context):
        return RTResult().success_continue()

    def visit_BreakNode(self, node, context):
        return RTResult().success_break()


#######################################
# RUN
#######################################

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number.null)
global_symbol_table.set("FALSE", Number.false)
global_symbol_table.set("TRUE", Number.true)
global_symbol_table.set("MATH_PI", Number.math_PI)
global_symbol_table.set("PRINT", BuiltInFunction.print)
global_symbol_table.set("PRINT_RET", BuiltInFunction.print_ret)
global_symbol_table.set("INPUT", BuiltInFunction.input)
global_symbol_table.set("INPUT_INT", BuiltInFunction.input_int)
global_symbol_table.set("CLEAR", BuiltInFunction.clear)
global_symbol_table.set("CLS", BuiltInFunction.clear)
global_symbol_table.set("IS_NUM", BuiltInFunction.is_number)
global_symbol_table.set("IS_STR", BuiltInFunction.is_string)
global_symbol_table.set("IS_LIST", BuiltInFunction.is_list)
global_symbol_table.set("IS_DEF", BuiltInFunction.is_function)
global_symbol_table.set("APPEND", BuiltInFunction.append)
global_symbol_table.set("POP", BuiltInFunction.pop)
global_symbol_table.set("EXTEND", BuiltInFunction.extend)
global_symbol_table.set("LEN", BuiltInFunction.len)
global_symbol_table.set("RUN", BuiltInFunction.run)


def run(fileName, text):
    # Generate tokens
    lexer = Lexer(fileName, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    # Run program
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    resultado = interpreter.visit(ast.node, context)

    return resultado.value, resultado.error
