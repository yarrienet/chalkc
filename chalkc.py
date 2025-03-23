import sys
import os

class ChalkSyntaxError(Exception):
    pass
    
class ChalkParserError(Exception):
    pass

class ChalkUndefinedVariable(Exception):
    pass

class ChalkUndefinedStatement(Exception):
    pass

class Internals:
    globalVars = {}
    globalFuncs = {}
    def __init__(self):
        pass

class Parser:
    internals = Internals()
    run = True
    mem = []

    def __init__(self):
        pass

    def chomp(self, line):
        if line[0] == "(" and line[-1] == ")":
            lineSplit = list(line)
            for i in range(-1, 1):
                del lineSplit[i]
            return "".join(lineSplit)
        else:
            return line.replace("\t", "").lstrip()

    def saveGlobalVar(self, name, type, value):
        # format for variables
        # [type, value]
        # TYPE TABLE:
        # 0 - string
        # 1 - [RESERVED] (not yet implemented)
        # 2 - array 
        self.internals.globalVars[name] = [type, value]

    def renderGlobalVar(self, var, expectedType = 0):
        try:
            variable = self.internals.globalVars[var]
            # if the expected type is a string
            if expectedType == 0:
                if variable[0] == 0:
                    return variable[1]
                elif variable[0] == 2:
                    # automatically convert an array into a string
                    return self.stringifyArray(variable[1])
            elif expectedType == 2:
                # automatically split a string, converting it into an array
                if variable[0] == 0:
                    return [*variable[1]]
                elif variable[0] == 2:
                    return variable[1]
        except KeyError:
            raise ChalkUndefinedVariable("`%s` does not exist" % var)

    def renderString(self, line):
        # if starts and ends with double quotes
        if line[0] == "\"" and line[-1] == "\"":
            # brutishly remove the double quotes (WHY?)
            line = line.replace("\"", "")
            lineSplit = line.split(" ")
            # loop through each "word"
            for word in range(0, len(lineSplit)):
                # check if "word" starts with @ making it a variable reference
                if lineSplit[word][0] == "@":
                    # check if the variable contins a colon by splitting it
                    colonSplit = lineSplit[word][1:].split(":")
                    if len(colonSplit) > 1:
                        # if contains a colon then unpack it
                        # resolve the variable name
                        arrayValue = self.renderGlobalVar(colonSplit[0], 2)
                        indexValue = int(colonSplit[1])
                        # replace the "word" with the array with subscription
                        lineSplit[word] = arrayValue[indexValue]
                    else:
                        # replace the "word" with the resloved variable
                        lineSplit[word] = self.renderGlobalVar(lineSplit[word][1:])
            # return the finished word
            return " ".join(lineSplit)
        else:
            raise ChalkSyntaxError("Does not follow string formatting")

    def stringifyArray(self, array):
        return "[" + ", ".join(array) + "]"

    def parseArray(self, value):
        # confirm is an array, otherwise throw error
        if value[0] == "[" and value[-1] == "]":
            splitItems = value.split(" ")
            # list for parsed array items
            items = []
            pendingItem = False
            for index, item in enumerate(splitItems):
                # cut off the [ from the first item
                item = item[1:] if index == 0 else item
                # cut off the ] from the last item
                item = item[:-1] if index == len(splitItems)-1 else item
                # if the item has a comma then cut it off and expect another item
                if item[-1] == ",":
                    pendingItem = True 
                    item = item[:-1]
                else:
                    pendingItem = False
                # render the string that the item is (for now) and add to items
                items.append(self.renderString(item))
            if pendingItem:
                raise ChalkSyntaxError("Expected item in array")
            return items
        else:
            raise ChalkSyntaxError("Invalid array syntax")
        

    def compare(self, strings, operator):
        run = True
        for i in range(0, 2):
            strings[i] = self.renderString(strings[i])

        if operator == "==":
            if strings[0] != strings[1]:
                run = False
        elif operator == "!=":
            if strings[0] == strings[1]:
                run = False
        elif operator == ">":
            if int(strings[0]) < int(strings[1]):
                run = False
        elif operator == "<":
            if int(strings[0]) > int(strings[1]):
                run = False
        elif operator == ">=":
            if int(strings[0]) <= int(strings[1]):
                run = False
        elif operator == "<=":
            if int(strings[0]) >= int(strings[1]):
                run = False
        else:
            raise ChalkSyntaxError("`%s` is not a valid comparator" % line[2])

        if run != None:
            return run

    def parse(self, ln):
        buffer = []
        
        ln = self.chomp(ln)
        line = ln.split(" ")

        # comments
        if line[0][:2] == "--":
            pass

        elif line[0] == "}":
            if len(self.mem) > 0:
                self.run = True
                if self.mem[-1][0] == "function":
                    # globalFunc[function] = [[blocks], [params]]
                    # Function memory entry
                    # mem = ["function", [blocks], [name, [params]]
                    self.internals.globalFuncs[self.mem[-1][2][0]] = [self.mem[-1][1], self.mem[-1][2][1]]
                elif self.mem[-1][0] == "while":
                    # While memory entry
                    # mem = ["while", [blocks], ["true", "==", "true"]]
                    while self.compare([self.mem[-1][2][0], self.mem[-1][2][2]], self.mem[-1][2][1]):
                        for block in self.mem[-1][1]:
                            parseBuffer = self.parse(block)
                            if len(parseBuffer) > 0:
                                buffer.append(*parseBuffer)

            else:
                raise ChalkSyntaxError("Unexpected end of block")

        elif self.run == False:
            self.mem[-1][1].append(ln)

        # if param = param { .. }
        elif line[0] == "if":
            if line[4] == "{":
                self.mem.append(["if", []])
                self.run = self.compare([line[1], line[3]], line[2])
            else:
                raise ChalkSyntaxError("Expected `{` instead of `%s`" % line[4])

        # while param = param { .. }
        elif line[0] == "while":
            if line[4] == "{":
                self.run = False
                self.mem.append(["while", [], [line[1], line[2], line[3]]])
            else:
                raise ChalkSyntaxError("Expected `{` instead of `%s`" % line[4])

        # func x (param1,param2) { .. }
        elif line[0] == "func":
            if line[3] == "{":
                params = []
                paramSplit = self.chomp(line[2]).split(",")
                for param in range(0, len(paramSplit)):
                    params.append(paramSplit[param])
                self.run = False
                self.mem.append(["function", [], [line[1], params]])
            else:
                raise ChalkSyntaxError("Expected `{` instead of `%s`" % line[4])

        elif line[0] == "write":
            buffer.append(self.renderString(" ".join(line[1:])))

        # read @var
        elif line[0] == "read":
            if line[1][0] == "@":
                read = input()
                self.saveGlobalVar(line[1][1:], 0, read)
            else:
                raise ChalkSyntaxError("Expected variable for read")

        # Declares a variable
        elif len(line) >= 3:
            if line[1] == "=":
                value = " ".join(line[2:])
                if line[2][0] == "\"":
                    self.saveGlobalVar(line[0], 0, self.renderString(value))
                elif line[2][0] == "[":
                    self.saveGlobalVar(line[0], 2, self.parseArray(value))
                else:
                    raise ChalkSyntaxError("Expected string or array for variable assigment")
            elif line[1] == "+=":
                if line[2][0] == '"' and line[2][len(line) - 1] == '"':
                    self.internals.localVars[line[0]] += line[2].strip('"')
                elif line[2] == "true" or line[2] == "false":
                    self.internals.localVars[line[0]] += line[2]
                else:
                    self.internals.localVars[line[0]] += line[2]
            elif line[1] == "-=":
                if line[2][0] == '"' and line[2][len(line) - 1] == '"':
                    self.internals.localVars[line[0]] -= line[2].strip('"')
                elif line[2] == "true" or line[2] == "false":
                    self.internals.localVars[line[0]] -= line[2]
                else:
                    self.internals.localVars[line[0]] -= line[2]

        # Checks for a function
        elif line[0] in self.internals.globalFuncs:
            paramSplit = self.chomp(line[1]).split(",")
            for param in range(0, len(paramSplit)):
                self.saveGlobalVar(self.internals.globalFuncs[line[0]][1][param], 0, self.renderString(paramSplit[param]))
            for block in self.internals.globalFuncs[line[0]][0]:
                parseBuffer = self.parse(block)
                if len(parseBuffer) > 0:
                    buffer.append(*parseBuffer)

        # No statment found
        else:
            raise ChalkUndefinedStatement("`" + line[0] + "` is not a valid statement")
        return buffer

p = Parser()
for arg in sys.argv:
    if os.path.isfile(arg) and arg[-6:] == ".chalk":
        openFile = open(arg, "r")
        openFile = openFile.read().split("\n")
        for line in openFile:
            if line:
                output = p.parse(line)
                if len(output) > 0:
                    print("".join(p.parse(line)))
        break
