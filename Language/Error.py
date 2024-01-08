from StringWithArrow import string_with_arrows


class Error:
    def __init__(self, startPos, endPos, errorName, details):
        self.startPos = startPos
        self.endPos = endPos
        self.errorName = errorName
        self.details = details

    def as_string(self):
        result = f'{self.errorName}: {self.details}\n'
        result += f'File {self.startPos.filename}, line {self.startPos.lineNumber + 1}'
        result += '\n' + string_with_arrows(self.startPos.content, self.startPos, self.endPos)
        return result


class IllegalCharError(Error):
    def __init__(self, startPos, endPos, details):
        super().__init__(startPos, endPos, 'Illegal Character', details)


class InvalidSyntaxError(Error):
    def __init__(self, startPos, endPos, details):
        super().__init__(startPos, endPos, 'Invalid Syntax', details)


class ExpectedCharError(Error):
    def __init__(self, startPos, endPos, details):
        super().__init__(startPos, endPos, 'Expected Character', details)


class RunningTimeError(Error):
    def __init__(self, startPos, endPos, details, context):
        super().__init__(startPos, endPos, 'Runtime Error', details)
        self.context = context

    def as_string(self):
        result = self.generateTrace()
        result += f'{self.errorName}: {self.details}\n'
        result += '\n' + string_with_arrows(self.startPos.content, self.startPos, self.endPos)
        return result

    def generateTrace(self):
        result = ''
        pos = self.startPos.copy()
        ctx = self.context

        while ctx:
            result = f' File {pos.filename}, line {str(pos.lineNumber + 1)}, in {ctx.displayName}\n' + result
            pos = ctx.parentEntryPos
            ctx = ctx.parent

        return 'Traceback (most recent call last): \n' + result
