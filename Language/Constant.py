import string


DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_DIV = 'DIV'
TT_MUL = 'MUL'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'
TT_POW = 'POW'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'
TT_EQUAL = 'EQUAL'
TT_EE = 'EE'
TT_NE = 'NE'
TT_LT = 'LT'
TT_GT = 'GT'
TT_GTE = 'GTE'
TT_LTE = 'LTE'
TT_COMMA = 'COMMA'
TT_ARROW = 'ARROW'
TT_STRING = 'STRING'
TT_LSQUARE = 'LSQUARE'
TT_RSQUARE = 'RSQUARE'
TT_NEWLINE = 'NEWLINE'


KEYWORDS = [
    'let',
    'and',
    'or',
    'not',
    'if',
    'elif',
    'else',
    'then',
    'for',
    'to',
    'step',
    'while',
    'fun',
    'end',
    'return',
    'break',
    'continue',
]

BUILTINFUNCTION = [
    'print',
    'input',
    'inputInt',
    'isNumber',
    'isString',
    'isFunction',
    'isList',
    'push',
    'pop',
    'extend',
    'len',
    'run',
    'int',
    'float',
    'str',
    'println',
    'replace'
]


class Position:
    def __init__(self, index, lineNumber, colNumber, filename, content):
        self.lineNumber = lineNumber
        self.colNumber = colNumber
        self.index = index
        self.filename = filename
        self.content = content

    def advance(self, currentChar=None):
        self.index += 1
        self.colNumber += 1

        if currentChar == '\n':
            self.lineNumber += 1
            self.colNumber = 0

        return self

    def copy(self):
        return Position(self.index, self.lineNumber, self.colNumber, self.filename, self.content)


class Context:
    def __init__(self, displayName, parent=None, parentEntryPos=None):
        self.displayName = displayName
        self.parent = parent
        self.parentEntryPos = parentEntryPos
        self.symbolTable = None


class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]
