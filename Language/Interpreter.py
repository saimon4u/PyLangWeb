from Values import Number, Function, String, List
import Constant
from Error import RunningTimeError


class RuntimeResult:
    def __init__(self):
        self.value = None
        self.error = None
        self.funReturnValue = None
        self.loopShouldContinue = False
        self.loopShouldBreak = False
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.funReturnValue = None
        self.loopShouldContinue = False
        self.loopShouldBreak = False

    def register(self, res):
        self.error = res.error
        self.funReturnValue = res.funReturnValue
        self.loopShouldContinue = res.loopShouldContinue
        self.loopShouldBreak = res.loopShouldBreak
        return res.value

    def success(self, value):
        self.reset()
        self.value = value
        return self

    def successReturn(self, value):
        self.reset()
        self.funReturnValue = value
        return self

    def successContinue(self):
        self.reset()
        self.loopShouldContinue = True
        return self

    def successBreak(self):
        self.reset()
        self.loopShouldBreak = True
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self

    def shouldReturn(self):
        return self.error or self.funReturnValue or self.loopShouldBreak or self.loopShouldContinue


class Interpreter:
    def visit(self, node, context):
        methodName = f'visit_{type(node).__name__}'
        method = getattr(self, methodName, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self, node, context):
        return RuntimeResult().success(Number(node.token.value).setPos(node.startPos, node.endPos).setContext(context))

    def visit_BinaryOpNode(self, node, context):
        res = RuntimeResult()
        left = res.register(self.visit(node.leftNode, context))
        if res.shouldReturn():
            return res
        right = res.register(self.visit(node.rightNode, context))
        if res.shouldReturn():
            return res

        result = None
        error = None
        if node.opTok.tokenType == Constant.TT_PLUS:
            result, error = left.addition(right)

        elif node.opTok.tokenType == Constant.TT_MINUS:
            result, error = left.subtraction(right)

        elif node.opTok.tokenType == Constant.TT_MUL:
            result, error = left.multiplication(right)

        elif node.opTok.tokenType == Constant.TT_DIV:
            result, error = left.division(right)

        elif node.opTok.tokenType == Constant.TT_POW:
            result, error = left.power(right)

        elif node.opTok.tokenType == Constant.TT_EE:
            result, error = left.equal(right)

        elif node.opTok.tokenType == Constant.TT_NE:
            result, error = left.notEqual(right)

        elif node.opTok.tokenType == Constant.TT_GT:
            result, error = left.greaterThan(right)

        elif node.opTok.tokenType == Constant.TT_GTE:
            result, error = left.greaterThanEqual(right)

        elif node.opTok.tokenType == Constant.TT_LT:
            result, error = left.lesserThan(right)

        elif node.opTok.tokenType == Constant.TT_LTE:
            result, error = left.lesserThanEqual(right)

        elif node.opTok.matches(Constant.TT_KEYWORD, 'and'):
            result, error = left.bitwiseAnd(right)

        elif node.opTok.matches(Constant.TT_KEYWORD, 'or'):
            result, error = left.bitwiseOr(right)

        if error:
            return res.failure(error)

        return res.success(result.setPos(node.startPos, node.endPos))

    def visit_UnaryOpNode(self, node, context):
        res = RuntimeResult()
        val = res.register(self.visit(node.node, context))
        if res.shouldReturn():
            return res

        error = None

        if node.opTok.tokenType == Constant.TT_MINUS:
            val, error = val.multiplication(Number(-1))

        elif node.opTok.matches(Constant.TT_KEYWORD, 'not'):
            val, error = val.notOperation()

        if error:
            return res.failure(error)
        return res.success(val.setPos(node.startPos, node.endPos))

    def visit_VarAccessNode(self, node, context):
        res = RuntimeResult()
        varName = node.varNameTok.value
        value = context.symbolTable.get(varName)

        if not value:
            return res.failure(RunningTimeError(node.startPos, node.endPos, f"'{varName}' is not defined", context))

        value = value.copy().setPos(node.startPos, node.endPos).setContext(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RuntimeResult()
        varName = node.varNameTok.value
        value = res.register(self.visit(node.valueNode, context))
        if res.shouldReturn():
            return res
        context.symbolTable.set(varName, value)
        return res.success(value)

    def visit_IfNode(self, node, context):
        res = RuntimeResult()

        for condition, expr, shouldReturnNull in node.cases:
            conditionValue = res.register(self.visit(condition, context))
            if res.shouldReturn():
                return res

            if conditionValue.isTrue():
                exprValue = res.register(self.visit(expr, context))
                if res.shouldReturn():
                    return res
                return res.success(Number(0) if shouldReturnNull else exprValue)

        if node.elseCase:
            expr, shouldReturnNull = node.elseCase
            elseValue = res.register(self.visit(expr, context))
            if res.shouldReturn():
                return res
            return res.success(Number(0) if shouldReturnNull else elseValue)

        return res.success(Number(0))

    def visit_ForNode(self, node, context):
        res = RuntimeResult()
        elements = []

        startValue = res.register(self.visit(node.startValueNode, context))
        if res.shouldReturn():
            return res

        endValue = res.register(self.visit(node.endValueNode, context))
        if res.shouldReturn():
            return res

        if node.stepValueNode is not None:
            stepValue = res.register(self.visit(node.stepValueNode, context))
            if res.shouldReturn():
                return res
        else:
            stepValue = Number(1)

        i = startValue.value

        if stepValue.value >= 0:
            condition = lambda: i < endValue.value
        else:
            condition = lambda: i > endValue.value

        while condition():
            context.symbolTable.set(node.varNameTok.value, Number(i))
            i += stepValue.value

            value = res.register(self.visit(node.bodyNode, context))

            if res.shouldReturn() and res.loopShouldBreak is False and res.loopShouldContinue is False:
                return res

            if res.loopShouldContinue:
                continue
            if res.loopShouldBreak:
                break
            elements.append(value)
        # return res.success(Number(0) if node.shouldReturnull else List(elements).setContext(context).setPos(node.startPos, node.endPos))
        return res.success(None)

    def visit_WhileNode(self, node, context):
        res = RuntimeResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.conditionNode, context))
            if res.shouldReturn():
                return res

            if not condition.isTrue():
                break

            value = res.register(self.visit(node.bodyNode, context))
            if res.shouldReturn() and res.loopShouldBreak is False and res.loopShouldContinue is False:
                return res

            if res.loopShouldContinue:
                continue
            if res.loopShouldBreak:
                break
            elements.append(value)

        # return res.success(Number(0) if node.shouldReturnNull else List(elements).setContext(context).setPos(node.startPos, node.endPos))
        return res.success(None)
    def visit_FunDefNode(self, node, context):
        res = RuntimeResult()
        funName = node.varNameTok.value if node.varNameTok else None
        bodyNode = node.bodyNode
        argNames = [argName.value for argName in node.argNameTokens]

        funcValue = Function(funName, bodyNode, argNames, node.shouldAutoReturn).setContext(context).setPos(node.startPos, node.endPos)
        if node.varNameTok:
            context.symbolTable.set(funName, funcValue)
        return res.success(funcValue)

    def visit_FunCallNode(self, node, context):
        res = RuntimeResult()
        args = []

        valueToCall = res.register(self.visit(node.nodeToCall, context))
        if res.shouldReturn():
            return res
        valueToCall = valueToCall.copy().setPos(node.startPos, node.endPos)

        for argNode in node.argNodes:
            args.append(res.register(self.visit(argNode, context)))
            if res.shouldReturn():
                return res

        returnVal = res.register(valueToCall.execute(args))
        if res.shouldReturn():
            return res

        if returnVal:
            returnVal = returnVal.copy().setContext(context).setPos(node.startPos, node.endPos)

        return res.success(returnVal)

    def visit_StringNode(self, node, context):
        res = RuntimeResult()
        return res.success(String(node.token.value).setContext(context).setPos(node.startPos, node.endPos))

    def visit_ListNode(self, node, context):
        res = RuntimeResult()
        elements = []

        for elementNode in node.elementNodes:
            elements.append(res.register(self.visit(elementNode, context)))
            if res.shouldReturn():
                return res

        return res.success(List(elements).setContext(context).setPos(node.startPos, node.endPos))

    def visit_ReturnNode(self, node, context):
        res = RuntimeResult()

        if node.nodeToReturn:
            value = res.register(self.visit(node.nodeToReturn, context))
            if res.shouldReturn():
                return res
        else:
            value = Number(0)

        return res.successReturn(value)

    def visit_ContinueNode(self, node, context):
        res = RuntimeResult()
        return res.successContinue()

    def visit_BreakNode(self, node, context):
        res = RuntimeResult()
        return res.successBreak()
