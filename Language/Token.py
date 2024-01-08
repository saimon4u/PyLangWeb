class Token:
    def __init__(self, tokenType, value=None, startPos=None, endPos=None):
        self.tokenType = tokenType
        self.value = value

        if startPos:
            self.startPos = startPos.copy()
            self.endPos = startPos.copy()
            self.endPos.advance()

        if endPos:
            self.endPos = endPos.copy()

    def matches(self, tokenType, value):
        return self.tokenType == tokenType and self.value == value

    def __repr__(self):
        if self.value is not None:
            return f'{self.tokenType}:{self.value}'
        return f'{self.tokenType}'
