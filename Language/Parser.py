import Constant
from Nodes import *
from Error import InvalidSyntaxError


class ParseResult:
    def __init__(self):
        self.toReverseCount = 0
        self.error = None
        self.node = None
        self.advanceCount = 0
        self.lastRegisteredAdvanceCount = 0

    def registerAdvance(self):
        self.lastRegisteredAdvanceCount = 1
        self.advanceCount += 1
        
    def tryRegister(self, res):
        if res.error:
            self.toReverseCount = res.advanceCount
            return None
        return self.register(res)

    def register(self, res):
        self.lastRegisteredAdvanceCount = res.advanceCount
        self.advanceCount += res.advanceCount
        if res.error:
            self.error = res.error
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.lastRegisteredAdvanceCount == 0:
            self.error = error
        return self


class Parser:
    def __init__(self, tokens):
        self.currentTok = None
        self.tokens = tokens
        self.tokIdx = -1
        self.advance()

    def advance(self):
        self.tokIdx += 1
        self.updateCurrentToken()
        return self.currentTok

    def reverse(self, amount=1):
        self.tokIdx -= amount
        self.updateCurrentToken()
        return self.currentTok

    def updateCurrentToken(self):
        if 0 <= self.tokIdx < len(self.tokens):
            self.currentTok = self.tokens[self.tokIdx]

    def parse(self):
        res = None
        if len(self.tokens) > 1:
            res = self.statements()

        if res and not res.error and self.currentTok.tokenType != Constant.TT_EOF:
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos, "Expected '+', "
                                                                                                    "'-', '*' or '/'"))

        return res

    def statements(self):
        res = ParseResult()
        statements = []
        pos = self.currentTok.startPos.copy()

        while self.currentTok.tokenType == Constant.TT_NEWLINE:
            res.registerAdvance()
            self.advance()

        statement = res.register(self.statement())
        if res.error:
            return res
        statements.append(statement)

        moreStatements = True
        while True:
            newLineCount = 0
            while self.currentTok.tokenType == Constant.TT_NEWLINE:
                res.registerAdvance()
                self.advance()
                newLineCount += 1
            if newLineCount == 0:
                moreStatements = False
            if not moreStatements:
                break
            statement = res.tryRegister(self.statement())
            if not statement:
                self.reverse(res.toReverseCount)
                moreStatements = False
                continue
            statements.append(statement)

        return res.success(ListNode(statements, pos, self.currentTok.endPos.copy()))

    def statement(self):
        res = ParseResult()
        pos = self.currentTok.startPos.copy()

        if self.currentTok.matches(Constant.TT_KEYWORD, 'return'):
            res.registerAdvance()
            self.advance()

            expr = res.tryRegister(self.expression())
            if not expr:
                self.reverse(res.toReverseCount)
            return res.success(ReturnNode(expr, pos, self.currentTok.endPos.copy()))

        if self.currentTok.matches(Constant.TT_KEYWORD, 'continue'):
            res.registerAdvance()
            self.advance()
            return res.success(ContinueNode(pos, self.currentTok.endPos.copy()))

        if self.currentTok.matches(Constant.TT_KEYWORD, 'break'):
            res.registerAdvance()
            self.advance()
            return res.success(BreakNode(pos, self.currentTok.endPos.copy()))

        expr = res.register(self.expression())
        if res.error:
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  "Expected 'let', int, float, 'if', 'for', 'while'," +
                                                  " 'fun', 'return', 'break', 'continue', identifier, '+', '-', '[' or '('"))
        return res.success(expr)

    def atom(self):
        res = ParseResult()
        token = self.currentTok

        if token.tokenType in (Constant.TT_INT, Constant.TT_FLOAT):
            res.registerAdvance()
            self.advance()
            return res.success(NumberNode(token))

        elif token.tokenType == Constant.TT_IDENTIFIER:
            res.registerAdvance()
            self.advance()
            return res.success(VarAccessNode(token))

        elif token.tokenType == Constant.TT_STRING:
            res.registerAdvance()
            self.advance()
            return res.success(StringNode(token))

        elif token.tokenType == Constant.TT_LPAREN:
            res.registerAdvance()
            self.advance()
            expr = res.register(self.expression())
            if res.error:
                return res

            if self.currentTok.tokenType == Constant.TT_RPAREN:
                res.registerAdvance()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos, "Expected ')'"))

        elif token.matches(Constant.TT_KEYWORD, 'if'):
            if_expr = res.register(self.ifExpression())
            if res.error:
                return res
            return res.success(if_expr)

        elif token.matches(Constant.TT_KEYWORD, 'for'):
            for_expr = res.register(self.forExpression())
            if res.error:
                return res
            return res.success(for_expr)

        elif token.matches(Constant.TT_KEYWORD, 'while'):
            while_expr = res.register(self.whileExpression())
            if res.error:
                return res
            return res.success(while_expr)

        elif token.matches(Constant.TT_KEYWORD, 'fun'):
            funDef = res.register(self.FunDefinition())
            if res.error:
                return res
            return res.success(funDef)

        elif token.tokenType == Constant.TT_LSQUARE:
            listExpr = res.register(self.listExpression())
            if res.error:
                return res
            return res.success(listExpr)

        return res.failure(InvalidSyntaxError(token.startPos, token.endPos,
                                              "Expected int, identifier, float, 'if', " +
                                              "'for', 'while', 'fun', '+', '-', '[' or '('"))

    def power(self):
        return self.binaryOperation(self.funCall, (Constant.TT_POW,), self.factor)

    def factor(self):
        res = ParseResult()
        token = self.currentTok

        if token.tokenType in (Constant.TT_PLUS, Constant.TT_MINUS):
            res.registerAdvance()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(token, factor))

        return self.power()

    def term(self):
        return self.binaryOperation(self.factor, (Constant.TT_MUL, Constant.TT_DIV))

    def expression(self):
        res = ParseResult()

        if self.currentTok.matches(Constant.TT_KEYWORD, 'let'):
            res.registerAdvance()
            self.advance()
            if self.currentTok.tokenType != Constant.TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(self.currentTok.startPos,
                                                      self.currentTok.endPos, 'Expected identifier'))
            varName = self.currentTok
            res.registerAdvance()
            self.advance()

            if self.currentTok.tokenType != Constant.TT_EQUAL:
                return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos, "Expected '='"))
            res.registerAdvance()
            self.advance()
            if self.currentTok.value in Constant.BUILTINFUNCTION and self.tokIdx == len(self.tokens) - 2:
                return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                      "You can't use built in function as variable assignment."))
            expr = res.register(self.expression())
            if res.error:
                return res

            return res.success(VarAssignNode(varName, expr))

        node = res.register(self.binaryOperation(self.comparisonExpression,
                                                 ((Constant.TT_KEYWORD, 'and'), (Constant.TT_KEYWORD, 'or'))))
        if res.error:
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  "Expected 'let', int, float, 'if', 'for', 'while'," +
                                                  " 'fun', identifier, '+', '-', '[' or '('"))
        return res.success(node)

    def comparisonExpression(self):
        res = ParseResult()

        if self.currentTok.matches(Constant.TT_KEYWORD, 'not'):
            opTok = self.currentTok
            res.registerAdvance()
            self.advance()

            node = res.register(self.comparisonExpression())
            if res.error:
                return res
            return res.success(UnaryOpNode(opTok, node))

        node = res.register(self.binaryOperation(self.arithmeticExpression,
                                                 (Constant.TT_EE, Constant.TT_NE, Constant.TT_LTE,
                                                  Constant.TT_LT, Constant.TT_GTE, Constant.TT_GT)))
        if res.error:
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  "Expected int, identifier, float, '+', '-', '(', '[' or 'not'"))
        return res.success(node)

    def arithmeticExpression(self):
        return self.binaryOperation(self.term, (Constant.TT_PLUS, Constant.TT_MINUS))

    def ifExpression(self):
        res = ParseResult()
        allCases = res.register(self.ifExpressionCases('if'))
        if res.error:
            return res
        cases, elseCase = allCases
        return res.success(IfNode(cases, elseCase))

    def ifExpressionB(self):
        return self.ifExpressionCases('elif')

    def ifExpressionC(self):
        res = ParseResult()
        elseCase = None

        if self.currentTok.matches(Constant.TT_KEYWORD, 'else'):
            res.registerAdvance()
            self.advance()

            if self.currentTok.tokenType == Constant.TT_NEWLINE:
                res.registerAdvance()
                self.advance()

                statements = res.register(self.statements())
                if res.error:
                    return res
                elseCase = (statements, True)

                if self.currentTok.matches(Constant.TT_KEYWORD, 'end'):
                    res.registerAdvance()
                    self.advance()
                else:
                    return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                          "Expected 'end'"))

            else:
                expr = res.register(self.statement())
                if res.error:
                    return res
                elseCase = (expr, False)

        return res.success(elseCase)

    def ifExpressionBorC(self):
        res = ParseResult()
        cases, elseCase = [], None

        if self.currentTok.matches(Constant.TT_KEYWORD, 'elif'):
            allCases = res.register(self.ifExpressionB())
            if res.error:
                return res
            cases, elseCase = allCases
        else:
            elseCase = res.register(self.ifExpressionC())
            if res.error:
                return res

        return res.success((cases, elseCase))

    def ifExpressionCases(self, caseKeyword):
        res = ParseResult()
        cases = []
        elseCase = None

        if not self.currentTok.matches(Constant.TT_KEYWORD, caseKeyword):
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  f"Expected '{caseKeyword}'"))
        res.registerAdvance()
        self.advance()

        condition = res.register(self.expression())
        if res.error:
            return res

        if not self.currentTok.matches(Constant.TT_KEYWORD, 'then'):
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  f"Expected 'then'"))

        res.registerAdvance()
        self.advance()
        
        if self.currentTok.tokenType == Constant.TT_NEWLINE:
            res.registerAdvance()
            self.advance()

            statements = res.register(self.statements())
            if res.error:
                return res
            cases.append((condition, statements, True))

            if self.currentTok.matches(Constant.TT_KEYWORD, 'end'):
                res.registerAdvance()
                self.advance()
            else:
                allCases = res.register(self.ifExpressionBorC())
                if res.error:
                    return res
                newCases, elseCase = allCases
                cases.extend(newCases)
        else:
            expr = res.register(self.statement())
            if res.error:
                return res

            cases.append((condition, expr, False))
            allCases = res.register(self.ifExpressionBorC())
            if res.error:
                return res

            newCases, elseCase = allCases
            cases.extend(newCases)

        return res.success((cases, elseCase))

    def forExpression(self):
        res = ParseResult()

        if not self.currentTok.matches(Constant.TT_KEYWORD, 'for'):
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  "Expected 'for'"))
        res.registerAdvance()
        self.advance()

        if self.currentTok.tokenType != Constant.TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  "Expected identifier"))

        varNameTok = self.currentTok
        res.registerAdvance()
        self.advance()

        if self.currentTok.tokenType != Constant.TT_EQUAL:
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  "Expected '='"))
        res.registerAdvance()
        self.advance()

        startValue = res.register(self.expression())
        if res.error:
            return res

        if not self.currentTok.matches(Constant.TT_KEYWORD, 'to'):
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  "Expected 'to'"))

        res.registerAdvance()
        self.advance()

        endValue = res.register(self.expression())
        if res.error:
            return res

        if self.currentTok.matches(Constant.TT_KEYWORD, 'step'):
            res.registerAdvance()
            self.advance()

            stepValue = res.register(self.expression())
            if res.error:
                return res
        else:
            stepValue = None

        if not self.currentTok.matches(Constant.TT_KEYWORD, 'then'):
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  "Expected 'then'"))
        res.registerAdvance()
        self.advance()

        if self.currentTok.tokenType == Constant.TT_NEWLINE:
            res.registerAdvance()
            self.advance()

            body = res.register(self.statements())
            if res.error:
                return res

            if not self.currentTok.matches(Constant.TT_KEYWORD, 'end'):
                return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                      "Expected 'end'"))

            res.registerAdvance()
            self.advance()

            return res.success(ForNode(varNameTok, startValue, endValue, stepValue, body, True))

        body = res.register(self.expression())
        if res.error:
            return res

        return res.success(ForNode(varNameTok, startValue, endValue, stepValue, body, False))

    def whileExpression(self):
        res = ParseResult()

        if not self.currentTok.matches(Constant.TT_KEYWORD, 'while'):
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  "Expected 'while'"))
        res.registerAdvance()
        self.advance()

        condition = res.register(self.expression())
        if res.error:
            return res

        if not self.currentTok.matches(Constant.TT_KEYWORD, 'then'):
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  "Expected 'then'"))
        res.registerAdvance()
        self.advance()

        if self.currentTok.tokenType == Constant.TT_NEWLINE:
            res.registerAdvance()
            self.advance()

            body = res.register(self.statements())
            if res.error:
                return res

            if not self.currentTok.matches(Constant.TT_KEYWORD, 'end'):
                return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                      "Expected 'end'"))

            res.registerAdvance()
            self.advance()

            return res.success(WhileNode(condition, body, True))

        body = res.register(self.expression())
        if res.error:
            return res

        return res.success(WhileNode(condition, body, False))

    def FunDefinition(self):
        res = ParseResult()

        if not self.currentTok.matches(Constant.TT_KEYWORD, 'fun'):
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  "Expected 'fun'"))

        res.registerAdvance()
        self.advance()

        if self.currentTok.tokenType == Constant.TT_IDENTIFIER:
            varNameTok = self.currentTok
            res.registerAdvance()
            self.advance()

            if self.currentTok.tokenType != Constant.TT_LPAREN:
                return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                      "Expected '('"))

        else:
            varNameTok = None
            if self.currentTok.tokenType != Constant.TT_LPAREN:
                return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                      "Expected identifier, '('"))
        res.registerAdvance()
        self.advance()
        argNameTokens = []

        if self.currentTok.tokenType == Constant.TT_IDENTIFIER:
            argNameTokens.append(self.currentTok)
            res.registerAdvance()
            self.advance()
            while self.currentTok.tokenType == Constant.TT_COMMA:
                res.registerAdvance()
                self.advance()

                if self.currentTok.tokenType != Constant.TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                          "Expected identifier"))

                argNameTokens.append(self.currentTok)
                res.registerAdvance()
                self.advance()

            if self.currentTok.tokenType != Constant.TT_RPAREN:
                return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                      "Expected ')' or ','"))

        else:
            if self.currentTok.tokenType != Constant.TT_RPAREN:
                return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                      "Expected identifier or ')'"))

        res.registerAdvance()
        self.advance()

        if self.currentTok.tokenType == Constant.TT_ARROW:
            res.registerAdvance()
            self.advance()

            nodeToReturn = res.register(self.expression())
            if res.error:
                return res

            return res.success(FunDefNode(varNameTok, argNameTokens, nodeToReturn, True))

        if self.currentTok.tokenType != Constant.TT_NEWLINE:
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  "Expected '->' or NEWLINE"))

        res.registerAdvance()
        self.advance()

        body = res.register(self.statements())
        if res.error:
            return res

        if not self.currentTok.matches(Constant.TT_KEYWORD, 'end'):
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  "Expected 'end'"))

        res.registerAdvance()
        self.advance()

        return res.success(FunDefNode(varNameTok, argNameTokens, body, False))

    def funCall(self):
        res = ParseResult()

        atom = res.register(self.atom())
        if res.error:
            return res

        if self.currentTok.tokenType == Constant.TT_LPAREN:
            res.registerAdvance()
            self.advance()

            argNodes = []

            if self.currentTok.tokenType == Constant.TT_RPAREN:
                res.registerAdvance()
                self.advance()
            else:
                argNodes.append(res.register(self.expression()))
                if res.error:
                    return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                          "Expected 'let', int, float, identifier, '+', '-', '(', '[' or ')'"))
                while self.currentTok.tokenType == Constant.TT_COMMA:
                    res.registerAdvance()
                    self.advance()
                    argNodes.append(res.register(self.expression()))
                    if res.error:
                        return res

                if self.currentTok.tokenType != Constant.TT_RPAREN:
                    return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                          "Expected ',' or ')'"))
                res.registerAdvance()
                self.advance()
            return res.success(FunCallNode(atom, argNodes))
        return res.success(atom)

    def binaryOperation(self, funcA, opTokens, funcB=None):
        if funcB is None:
            funcB = funcA
        res = ParseResult()
        left = res.register(funcA())
        if res.error:
            return res
        while self.currentTok.tokenType in opTokens or (self.currentTok.tokenType, self.currentTok.value) in opTokens:
            opTok = self.currentTok
            res.registerAdvance()
            self.advance()
            right = res.register(funcB())
            if res.error:
                return res

            left = BinaryOpNode(left, opTok, right)

        return res.success(left)

    def listExpression(self):
        res = ParseResult()
        elementNodes = []
        startPos = self.currentTok.startPos.copy()

        if self.currentTok.tokenType != Constant.TT_LSQUARE:
            return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                  "Expected '[' "))

        res.registerAdvance()
        self.advance()

        if self.currentTok.tokenType == Constant.TT_RSQUARE:
            res.registerAdvance()
            self.advance()
        else:
            elementNodes.append(res.register(self.expression()))
            if res.error:
                return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                      "Expected 'let', int, float, identifier, '+', '-', '(', '[' or ']'"))
            while self.currentTok.tokenType == Constant.TT_COMMA:
                res.registerAdvance()
                self.advance()
                elementNodes.append(res.register(self.expression()))
                if res.error:
                    return res

            if self.currentTok.tokenType != Constant.TT_RSQUARE:
                return res.failure(InvalidSyntaxError(self.currentTok.startPos, self.currentTok.endPos,
                                                      "Expected ',' or ']'"))
            res.registerAdvance()
            self.advance()
        return res.success(ListNode(elementNodes, startPos, self.currentTok.endPos.copy()))


