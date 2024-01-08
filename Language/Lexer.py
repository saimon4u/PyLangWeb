from Constant import Position
import Constant
from Token import Token
from Error import IllegalCharError, ExpectedCharError


class Lexer:
    def __init__(self, filename, text):
        self.currentChar = None
        self.filename = filename
        self.text = text
        self.position = Position(-1, 0, -1, filename, text)
        self.advance()

    def advance(self):
        self.position.advance(self.currentChar)
        self.currentChar = self.text[self.position.index] if self.position.index < len(self.text) else None

    def makeTokens(self):

        tokens = []

        while self.currentChar is not None:
            if self.currentChar in ' \t':
                self.advance()

            elif self.currentChar == '$':
                self.skipComment()

            elif self.currentChar in Constant.DIGITS:
                tokens.append(self.makeNumber())

            elif self.currentChar in Constant.LETTERS:
                tokens.append(self.makeIdentifier())

            elif self.currentChar == '+':
                tokens.append(Token(Constant.TT_PLUS, startPos=self.position))
                self.advance()

            elif self.currentChar == '-':
                tokens.append(self.makeMinusOrArrow())

            elif self.currentChar == '*':
                tokens.append(Token(Constant.TT_MUL, startPos=self.position))
                self.advance()

            elif self.currentChar == '^':
                tokens.append(Token(Constant.TT_POW, startPos=self.position))
                self.advance()

            elif self.currentChar == ',':
                tokens.append(Token(Constant.TT_COMMA, startPos=self.position))
                self.advance()

            elif self.currentChar == '/':
                tokens.append(Token(Constant.TT_DIV, startPos=self.position))
                self.advance()

            elif self.currentChar == '(':
                tokens.append(Token(Constant.TT_LPAREN, startPos=self.position))
                self.advance()

            elif self.currentChar == ')':
                tokens.append(Token(Constant.TT_RPAREN, startPos=self.position))
                self.advance()

            elif self.currentChar == '[':
                tokens.append(Token(Constant.TT_LSQUARE, startPos=self.position))
                self.advance()

            elif self.currentChar == ']':
                tokens.append(Token(Constant.TT_RSQUARE, startPos=self.position))
                self.advance()

            elif self.currentChar in ';\n':
                tokens.append(Token(Constant.TT_NEWLINE, startPos=self.position))
                self.advance()

            elif self.currentChar == '!':
                tok, error = self.makeNotEquals()
                if error:
                    return [], error
                tokens.append(tok)

            elif self.currentChar == '=':
                tokens.append(self.makeEquals())

            elif self.currentChar == '<':
                tokens.append(self.makeLessThan())

            elif self.currentChar == '>':
                tokens.append(self.makeGreaterThan())

            elif self.currentChar == '"':
                tokens.append(self.makeString())

            else:
                startPos = self.position.copy()
                char = self.currentChar
                self.advance()
                return [], IllegalCharError(startPos, self.position, "'" + char + "'")

        tokens.append(Token(Constant.TT_EOF, startPos=self.position))
        return tokens, None

    def makeNumber(self):
        numStr = ''
        dotCount = 0
        pos = self.position.copy()

        while self.currentChar is not None and self.currentChar in Constant.DIGITS + '.':
            if self.currentChar == '.':
                if dotCount == 1:
                    break
                dotCount += 1
                numStr += '.'

            else:
                numStr += self.currentChar

            self.advance()

        if dotCount == 0:
            return Token(Constant.TT_INT, int(numStr), startPos=pos, endPos=self.position)
        else:
            return Token(Constant.TT_FLOAT, float(numStr), startPos=pos, endPos=self.position)

    def makeIdentifier(self):
        identifier = ''
        pos = self.position.copy()
        while self.currentChar is not None and self.currentChar in Constant.LETTERS_DIGITS + '_':
            identifier += self.currentChar
            self.advance()

        tokenType = Constant.TT_KEYWORD if identifier in Constant.KEYWORDS else Constant.TT_IDENTIFIER

        return Token(tokenType, identifier, pos, self.position)

    def makeNotEquals(self):
        pos = self.position.copy()
        self.advance()

        if self.currentChar == '=':
            self.advance()
            return Token(Constant.TT_NE, pos, self.position), None

        self.advance()
        return None, ExpectedCharError(pos, self.position, "'=' (after '!')")

    def makeEquals(self):
        pos = self.position.copy()
        self.advance()

        tokenType = Constant.TT_EQUAL

        if self.currentChar == '=':
            self.advance()
            tokenType = Constant.TT_EE

        return Token(tokenType, startPos=pos, endPos=self.position)

    def makeGreaterThan(self):
        pos = self.position.copy()
        self.advance()

        tokenType = Constant.TT_GT

        if self.currentChar == '=':
            self.advance()
            tokenType = Constant.TT_GTE

        return Token(tokenType, startPos=pos, endPos=self.position)

    def makeLessThan(self):
        pos = self.position.copy()
        self.advance()

        tokenType = Constant.TT_LT

        if self.currentChar == '=':
            self.advance()
            tokenType = Constant.TT_LTE

        return Token(tokenType, startPos=pos, endPos=self.position)

    def makeMinusOrArrow(self):
        pos = self.position.copy()
        self.advance()
        tokenType = Constant.TT_MINUS

        if self.currentChar == '>':
            self.advance()
            tokenType = Constant.TT_ARROW

        return Token(tokenType, startPos=pos, endPos=self.position)

    def makeString(self):
        string = ''
        pos = self.position.copy()
        escChar = False
        self.advance()

        escapeChars = {
            'n': '\n',
            't': '\t'
        }

        while self.currentChar is not None and (self.currentChar != '"' or escChar):
            if escChar:
                string += escapeChars.get(self.currentChar, self.currentChar)
                escChar = False
            else:
                if self.currentChar == '\\':
                    escChar = True
                else:
                    string += self.currentChar
            self.advance()

        self.advance()
        return Token(Constant.TT_STRING, string, pos, self.position)

    def skipComment(self):
        self.advance()

        while self.currentChar != '\n' and self.currentChar is not None:
            self.advance()
        if self.currentChar is not None:
            self.advance()
