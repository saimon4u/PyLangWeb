from Constant import Context, SymbolTable
import Interpreter
from Error import RunningTimeError
import Run


class Value:
    def __init__(self):
        self.context = None
        self.endPos = None
        self.startPos = None

    def setPos(self, startPos=None, endPos=None):
        self.startPos = startPos
        self.endPos = endPos
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def addition(self, other):
        return None, self.illegalOperation(other)

    def subtraction(self, other):
        return None, self.illegalOperation(other)

    def multiplication(self, other):
        return None, self.illegalOperation(other)

    def division(self, other):
        return None, self.illegalOperation(other)

    def modulo(self, other):
        return None, self.illegalOperation(other)

    def power(self, other):
        return None, self.illegalOperation(other)

    def equal(self, other):
        return None, self.illegalOperation(other)

    def notEqual(self, other):
        return None, self.illegalOperation(other)

    def greaterThan(self, other):
        return None, self.illegalOperation(other)

    def greaterThanEqual(self, other):
        return None, self.illegalOperation(other)

    def lesserThan(self, other):
        return None, self.illegalOperation(other)

    def lesserThanEqual(self, other):
        return None, self.illegalOperation(other)

    def bitwiseOr(self, other):
        return None, self.illegalOperation(other)

    def bitwiseAnd(self, other):
        return None, self.illegalOperation(other)

    def notOperation(self):
        return None, self.illegalOperation()

    def execute(self, args):
        res = Interpreter.RuntimeResult()
        return res.failure(self.illegalOperation())

    def copy(self):
        raise Exception('No copy method defined')

    def isTrue(self):
        return False

    def illegalOperation(self, other=None):
        if other is None:
            other = self

        return RunningTimeError(self.startPos, self.endPos, 'Illegal Operation', self.context)


class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.context = None
        self.endPos = None
        self.startPos = None
        self.value = value

    def addition(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def subtraction(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def multiplication(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def modulo(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RunningTimeError(other.startPos, other.endPos, "Modulo by zero", self.context)
            return Number(self.value % other.value).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def power(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def division(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RunningTimeError(other.startPos, other.endPos, "Division by zero", self.context)
            return Number(self.value / other.value).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def equal(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def notEqual(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def greaterThan(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def greaterThanEqual(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def lesserThan(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def lesserThanEqual(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def bitwiseAnd(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def bitwiseOr(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def notOperation(self):
        return Number(1 if self.value == 0 else 0).setContext(self.context), None

    def isTrue(self):
        return self.value != 0

    def copy(self):
        copy = Number(self.value)
        copy.setPos(self.startPos, self.endPos)
        copy.setContext(self.context)
        return copy

    def __repr__(self):
        return str(self.value)


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def addition(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def multiplication(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).setContext(self.context), None
        else:
            return None, Value.illegalOperation(self, other)

    def isTrue(self):
        return len(self.value) > 0

    def copy(self):
        copy = String(self.value)
        copy.setContext(self.context)
        copy.setPos(self.startPos, self.endPos)
        return copy

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'"{self.value}"'


class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def addition(self, other):
        newList = self.copy()
        newList.elements.append(other)
        return newList, None

    def multiplication(self, other):
        if isinstance(other, List):
            newList = self.copy()
            newList.elements.extend(other.elements)
            return newList, None
        else:
            return None, Value.illegalOperation(self, other)

    def subtraction(self, other):
        if isinstance(other, Number):
            newList = self.copy()
            try:
                newList.elements.pop(other.value)
                return newList, None
            except:
                return None, RunningTimeError(other.startPos, other.endPos,
                                              "Element at this index could not be removed from the list because" +
                                              "index is out of bounds", self.context)
        else:
            return None, Value.illegalOperation(self, other)

    def division(self, other):
        if isinstance(other, Number):
            try:
                val = other.value
                return self.elements[val], None
            except:
                return None, RunningTimeError(other.startPos, other.endPos,
                                              "Element at this index could not be retrieved from the list because" +
                                              "index is out of bounds", self.context)
        else:
            return None, Value.illegalOperation(self, other)

    def copy(self):
        copy = List(self.elements)
        copy.setPos(self.startPos, self.endPos)
        copy.setContext(self.context)
        return copy

    # def __str__(self):
    #     return ",".join([str(x) for x in self.elements])

    def __repr__(self):
        return f'[{",".join([str(x) for x in self.elements])}]'


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generateNewContext(self):
        newContext = Context(self.name, self.context, self.startPos)
        newContext.symbolTable = SymbolTable(newContext.parent.symbolTable)
        return newContext

    def checkArgs(self, argNames, args):
        res = Interpreter.RuntimeResult()

        if len(args) > len(argNames):
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                f"{len(args) - len(argNames)} too many args passed into '{self.name}'",
                                                self.context))

        if len(args) < len(argNames):
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                f"{len(argNames) - len(args)} too few args passed into '{self.name}'",
                                                self.context))
        return res.success(None)

    def populateArgs(self, argNames, args, context):
        res = Interpreter.RuntimeResult()
        for i in range(len(args)):
            argName = argNames[i]
            argValue = args[i]
            argValue.setContext(context)
            context.symbolTable.set(argName, argValue)
        return res.success(None)

    def checkAndPopulateArgs(self, argNames, args, context):
        res = Interpreter.RuntimeResult()
        res.register(self.checkArgs(argNames, args))
        if res.shouldReturn():
            return res
        res.register(self.populateArgs(argNames, args, context))
        if res.shouldReturn():
            return res
        return res.success(None)


class Function(BaseFunction):
    def __init__(self, name, bodyNode, argNames, shouldAutoReturn):
        super().__init__(name)
        self.bodyNode = bodyNode
        self.argNames = argNames
        self.shouldAutoReturn = shouldAutoReturn

    def execute(self, args):
        res = Interpreter.RuntimeResult()
        interpreter = Interpreter.Interpreter()

        newContext = self.generateNewContext()

        res.register(self.checkAndPopulateArgs(self.argNames, args, newContext))
        if res.shouldReturn():
            return res

        value = res.register(interpreter.visit(self.bodyNode, newContext))
        if res.shouldReturn() and res.funReturnValue is None:
            return res

        returnVal = (value if self.shouldAutoReturn else None) or res.funReturnValue or None
        return res.success(returnVal)

    def copy(self):
        copy = Function(self.name, self.bodyNode, self.argNames, self.shouldAutoReturn)
        copy.setContext(self.context)
        copy.setPos(self.startPos, self.endPos)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"


class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        res = Interpreter.RuntimeResult()

        context = self.generateNewContext()

        methodName = f'execute_{self.name}'
        method = getattr(self, methodName, self.noExecuteMethod)

        res.register(self.checkAndPopulateArgs(method.argNames, args, context))
        if res.shouldReturn():
            return res

        returnValue = res.register(method(context))
        if res.shouldReturn():
            return res

        return res.success(returnValue)

    def execute_print(self, context):
        res = Interpreter.RuntimeResult()
        print(str(context.symbolTable.get('value')), end="")
        return res.success(None)
    execute_print.argNames = ['value']

    def execute_println(self, context):
        res = Interpreter.RuntimeResult()
        print(str(context.symbolTable.get('value')))
        return res.success(Number(0))
    execute_println.argNames = ['value']

    def execute_input(self, context):
        res = Interpreter.RuntimeResult()
        text = input()
        return res.success(String(text))
    execute_input.argNames = []

    def execute_inputInt(self, context):
        res = Interpreter.RuntimeResult()
        text = ''
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again!")

        return res.success(Number(number))
    execute_inputInt.argNames = []

    def execute_inputFloat(self, context):
        res = Interpreter.RuntimeResult()
        text = ''
        while True:
            text = input()
            try:
                number = float(text)
                break
            except ValueError:
                print(f"'{text}' must be a float. Try again!")

        return res.success(Number(number))
    execute_inputFloat.argNames = []

    def execute_isNumber(self, context):
        res = Interpreter.RuntimeResult()
        isNumber = isinstance(context.symbolTable.get('value'), Number)
        return res.success(Number(1) if isNumber else Number(0))
    execute_isNumber.argNames = ['value']

    def execute_isString(self, context):
        res = Interpreter.RuntimeResult()
        isNumber = isinstance(context.symbolTable.get('value'), String)
        return res.success(Number(1) if isNumber else Number(0))
    execute_isString.argNames = ['value']

    def execute_isList(self, context):
        res = Interpreter.RuntimeResult()
        isNumber = isinstance(context.symbolTable.get('value'), List)
        return res.success(Number(1) if isNumber else Number(0))
    execute_isList.argNames = ['value']

    def execute_isFunction(self, context):
        res = Interpreter.RuntimeResult()
        isNumber = isinstance(context.symbolTable.get('value'), BaseFunction)
        return res.success(Number(1) if isNumber else Number(0))
    execute_isFunction.argNames = ['value']

    def execute_push(self, context):
        res = Interpreter.RuntimeResult()
        mList = context.symbolTable.get('list')
        value = context.symbolTable.get('value')

        if not isinstance(mList, List):
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                "First argument must be a List", context))

        mList.elements.append(value)
        return res.success(Number(0))
    execute_push.argNames = ['list', 'value']

    def execute_pop(self, context):
        res = Interpreter.RuntimeResult()
        mList = context.symbolTable.get('list')
        index = context.symbolTable.get('index')

        if not isinstance(mList, List):
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                "First argument must be a List", context))

        if not isinstance(index, Number):
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                "Second argument must be a Number", context))

        try:
            element = mList.elements.pop(index.value)
        except:
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                "Element at this index could not be removed" +
                                                " from the list because index is out of bounds.", context))
        return res.success(element)
    execute_pop.argNames = ['list', 'index']

    def execute_replace(self, context):
        res = Interpreter.RuntimeResult()
        mList = context.symbolTable.get('list')
        index = context.symbolTable.get('index')
        value = context.symbolTable.get('value')

        if not isinstance(mList, List):
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                "First argument must be a List", context))

        if not isinstance(index, Number):
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                "Second argument must be a Number", context))

        try:
            if isinstance(value, Number):
                mList.elements[index.value] = Number(value.value)
            elif isinstance(value, String):
                mList.elements[index.value] = String(value.value)
            elif isinstance(value, List):
                mList.elements[index.value] = List(value.elements)
        except:
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                "Element at this index could not be replaced" +
                                                " because index is out of bounds.", context))
        return res.success(Number(0))
    execute_replace.argNames = ['list', 'index', 'value']

    def execute_extend(self, context):
        res = Interpreter.RuntimeResult()
        listA = context.symbolTable.get('listA')
        listB = context.symbolTable.get('listB')

        if not isinstance(listA, List):
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                "First argument must be a List", context))

        if not isinstance(listB, List):
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                "Second argument must be a List", context))

        listA.elements.extend(listB.elements)
        return res.success(Number(0))
    execute_extend.argNames = ['listA', 'listB']

    def noExecuteMethod(self, context):
        raise Exception("No execute method found!")

    def execute_len(self, context):
        res = Interpreter.RuntimeResult()
        mList = context.symbolTable.get('list')

        if not isinstance(mList, List):
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                "Argument must be a List", context))

        return res.success(Number(len(mList.elements)))
    execute_len.argNames = ['list']

    def execute_int(self, context):
        res = Interpreter.RuntimeResult()
        val = context.symbolTable.get('value')

        if not isinstance(val, Number):
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                "Argument must be a Number", context))

        return res.success(Number(int(val.value)))
    execute_int.argNames = ['value']

    def execute_float(self, context):
        res = Interpreter.RuntimeResult()
        val = context.symbolTable.get('value')

        if not isinstance(val, Number):
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                "Argument must be a Number", context))

        return res.success(Number(float(val.value)))
    execute_float.argNames = ['value']

    def execute_str(self, context):
        res = Interpreter.RuntimeResult()
        val = context.symbolTable.get('value')

        return res.success(String(str(val.value)))
    execute_str.argNames = ['value']

    def execute_run(self, context):
        res = Interpreter.RuntimeResult()
        filename = context.symbolTable.get('fn')

        if not isinstance(filename, String):
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                "Argument must be a string.", context))

        filename = filename.value
        try:
            with open(filename, 'r') as f:
                script = f.read()
                f.close()
        except Exception as e:
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                f"Failed to load script \"{filename}\"\n" + str(e), context))
        p, error = Run.run(filename, script)

        if error:
            return res.failure(RunningTimeError(self.startPos, self.endPos,
                                                f"Failed to finish executing script \"{filename}\"\n" +
                                                error.as_string(), context))

        return res.success(Number(0))
    execute_run.argNames = ['fn']

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.setContext(self.context)
        copy.setPos(self.startPos, self.endPos)
        return copy

    def __repr__(self):
        return f"<built-in function {self.name}>"
