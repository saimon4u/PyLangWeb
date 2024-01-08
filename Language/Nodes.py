class NumberNode:
    def __init__(self, token):
        self.token = token
        self.startPos = token.startPos
        self.endPos = token.endPos

    def __repr__(self):
        return f'{self.token}'


class BinaryOpNode:
    def __init__(self, leftNode, opTok, rightNode):
        self.leftNode = leftNode
        self.opTok = opTok
        self.rightNode = rightNode
        self.startPos = leftNode.startPos
        self.endPos = rightNode.endPos

    def __repr__(self):
        return f'({self.leftNode}, {self.opTok}, {self.rightNode})'


class UnaryOpNode:
    def __init__(self, opTok, node):
        self.opTok = opTok
        self.node = node
        self.startPos = opTok.startPos
        self.endPos = node.endPos

    def __repr__(self):
        return f'({self.opTok}, {self.node})'


class VarAccessNode:
    def __init__(self, varNameTok):
        self.varNameTok = varNameTok
        self.startPos = varNameTok.startPos
        self.endPos = varNameTok.endPos


class VarAssignNode:
    def __init__(self, varNameTok, valueNode):
        self.varNameTok = varNameTok
        self.valueNode = valueNode

        self.startPos = self.varNameTok.startPos
        self.endPos = self.valueNode.endPos


class IfNode:
    def __init__(self, cases, elseCase):
        self.cases = cases
        self.elseCase = elseCase

        self.startPos = self.cases[0][0].startPos
        self.endPos = (self.elseCase or self.cases[len(self.cases) - 1])[0].endPos


class ForNode:
    def __init__(self, varNameTok, startValueNode, endValueNode, stepValueNode, bodyNode, shouldReturnNull):
        self.varNameTok = varNameTok
        self.startValueNode = startValueNode
        self.endValueNode = endValueNode
        self.stepValueNode = stepValueNode
        self.bodyNode = bodyNode
        self.shouldReturnNull = shouldReturnNull

        self.startPos = self.varNameTok.startPos
        self.endPos = self.bodyNode.endPos


class WhileNode:
    def __init__(self, conditionNode, bodyNode, shouldReturnNull):
        self.conditionNode = conditionNode
        self.bodyNode = bodyNode
        self.shouldReturnNull = shouldReturnNull

        self.startPos = self.conditionNode.startPos
        self.endPos = self.bodyNode.endPos


class FunDefNode:
    def __init__(self, varNameTok, argNameTokens, bodyNode, shouldAutoReturn):
        self.varNameTok = varNameTok
        self.argNameTokens = argNameTokens
        self.bodyNode = bodyNode
        self.shouldAutoReturn = shouldAutoReturn

        if self.varNameTok:
            self.startPos = self.varNameTok.startPos
        elif len(self.argNameTokens) > 0:
            self.startPos = self.argNameTokens[0].startPos
        else:
            self.startPos = self.bodyNode.startPos

        self.endPos = self.bodyNode.endPos


class FunCallNode:
    def __init__(self, nodeToCall, argNodes):
        self.nodeToCall = nodeToCall
        self.argNodes = argNodes

        self.startPos = self.nodeToCall.startPos

        if len(self.argNodes) > 0:
            self.endPos = self.argNodes[len(self.argNodes)-1].endPos
        else:
            self.endPos = self.nodeToCall.endPos


class StringNode:
    def __init__(self, token):
        self.token = token
        self.startPos = token.startPos
        self.endPos = token.endPos

    def __repr__(self):
        return f'{self.token}'


class ListNode:
    def __init__(self, elementNodes, startPos, endPos):
        self.elementNodes = elementNodes
        self.startPos = startPos
        self.endPos = endPos


class ReturnNode:
    def __init__(self, nodeToReturn, startPos, endPos):
        self.nodeToReturn = nodeToReturn
        self.startPos = startPos
        self.endPos = endPos


class ContinueNode:
    def __init__(self, startPos, endPos):
        self.startPos = startPos
        self.endPos = endPos


class BreakNode:
    def __init__(self, startPos, endPos):
        self.startPos = startPos
        self.endPos = endPos
