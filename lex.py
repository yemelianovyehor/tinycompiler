import enum
import sys


# TokenType is our enum for all the types of tokens.
class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    # Keywords.
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111
    # Operators.
    EQ = 201
    EQEQ = 202
    PLUS = 203
    MINUS = 204
    ASTERISK = 205
    SLASH = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211


class Token:

    def __init__(self, text, kind):
        self.text = text
        self.kind = kind

    @staticmethod
    def checkIfKeyword(tokenText):
        # pyrefly: ignore
        for kind in TokenType:
            if kind.name == tokenText and kind.value >= 100 and kind.value < 200:
                return kind
        return None


class Lexer:
    def __init__(self, source):
        self.source = source + '\r'
        self.cursorPos: int = -1
        self.curChar: str = ''
        self.nextChar()

    def nextChar(self):
        self.cursorPos += 1
        if self.cursorPos >= len(self.source):
            self.curChar = '\0'
        else:
            self.curChar = self.source[self.cursorPos]

    def peek(self):
        if self.cursorPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.cursorPos+1]

    def abort(self, message):
        sys.exit("Lexin error. " + message)

    def skipWhitespace(self):
        while self.curChar in [" ", "\t", "\r"]:
            self.nextChar()

    def skipComment(self):
        if self.curChar == "#":
            while self.curChar != "\n":
                self.nextChar()

    def checkEQ(self, type):
        if self.peek() == "=":
            lastChar = self.curChar
            self.nextChar()
            return Token(lastChar + self.curChar, TokenType(type.value+1))
        else:
            return Token(self.curChar, type)

    def getToken(self):
        self.skipWhitespace()
        self.skipComment()
        token = None

        if self.curChar == '+':
            token = Token(self.curChar, TokenType.PLUS)
        elif self.curChar == '-':
            token = Token(self.curChar, TokenType.MINUS)
        elif self.curChar == '*':
            token = Token(self.curChar, TokenType.ASTERISK)
        elif self.curChar == '/':
            token = Token(self.curChar, TokenType.SLASH)
        elif self.curChar == '\n':
            token = Token(self.curChar, TokenType.NEWLINE)
        elif self.curChar == '\0':
            token = Token(self.curChar, TokenType.EOF)
        elif self.curChar == "=":
            token = self.checkEQ(TokenType.EQ)
        elif self.curChar == "<":
            token = self.checkEQ(TokenType.LT)
        elif self.curChar == ">":
            token = self.checkEQ(TokenType.GT)
        elif self.curChar == "!":
            if self.peek() == "=":
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peek())

        elif self.curChar == '"':
            self.nextChar()
            startPos = self.cursorPos
            while self.curChar != "\"":
                if self.curChar in ["\n", "\r", "\\", "%"]:
                    self.abort("Illegal character in string:" + self.curChar)
                self.nextChar()
            tokenText = self.source[startPos: self.cursorPos]
            token = Token(tokenText, TokenType.STRING)
        elif self.curChar.isdigit():
            startPos = self.cursorPos
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == ".":
                self.nextChar()

                if not self.peek().isdigit():
                    self.abort("Illegal number")
                while self.peek().isdigit():
                    self.nextChar()
            tokenText = self.source[startPos:self.cursorPos+1]
            token = Token(tokenText, TokenType.NUMBER)
        elif self.curChar.isalpha():
            startPos = self.cursorPos
            while self.peek().isalnum():
                self.nextChar()

            tokenText = self.source[startPos:self.cursorPos+1]
            keyword = Token.checkIfKeyword(tokenText)
            if keyword is None:
                token = Token(tokenText, TokenType.IDENT)
            else:
                token = Token(tokenText, keyword)
        else:
            self.abort("Unknown token: " + self.curChar)

        self.nextChar()
        return token
