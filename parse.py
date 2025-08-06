import sys
from lex import Lexer, TokenType

'''
program ::= {statement}
statement ::= "PRINT" (expression | string) nl
    | "IF" comparison "THEN" nl {statement} "ENDIF" nl
    | "WHILE" comparison "REPEAT" nl {statement} "ENDWHILE" nl
    | "LABEL" ident nl
    | "GOTO" ident nl
    | "LET" ident "=" expression nl
    | "INPUT" ident nl
comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
expression ::= term {( "-" | "+" ) term}
term ::= unary {( "/" | "*" ) unary}
unary ::= ["+" | "-"] primary
primary ::= number | ident
nl ::= '\n'+
'''


class Parser:

    def __init__(self, lexer: Lexer):
        self.lexer = lexer

        self.symbols = set()
        self.labelsDeclared = set()
        self.labelsGotoed = set()

        self.curToken = self.lexer.getToken()
        self.peekToken = self.lexer.getToken()

    def checkToken(self, kind) -> bool:
        return kind == self.curToken.kind

    def checkPeek(self, kind) -> bool:
        return kind == self.peekToken.kind

    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected \""+kind.name +
                       "\", got \"" + self.curToken.kind.name + '"')
        self.nextToken()

    def isComparisonOperator(self):
        return self.curToken.kind.value >= 200 and \
            self.curToken.kind.value < 300

    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()

    def abort(self, message):
        sys.exit("Error. " + message)

    # program ::= {statement} |
    def program(self):
        print("PROGRAM")

        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        while not self.checkToken(TokenType.EOF):
            self.statement()

        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("GOTO undeclared label: " + label)

    def statement(self):

        # PRINT
        if self.checkToken(TokenType.PRINT):
            print("STATEMENT-PRINT (" + self.peekToken.text + ")")
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                self.nextToken()
            else:
                self.expression()
        # IF
        elif self.checkToken(TokenType.IF):
            print("STATEMENT-IF")
            self.nextToken()
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()

            while not self.checkToken(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)

        # WHILE
        elif self.checkToken(TokenType.WHILE):
            print("STATEMENT-WHILE")
            self.nextToken()
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()

            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)

        # LABEL
        elif self.checkToken(TokenType.LABEL):
            print("STATEMENT-LABEL (" + self.peekToken.text + ")")
            self.nextToken()

            if self.curToken.text in self.labelsDeclared:
                self.abort("Label already exists: " + self.curToken.text)
            self.labelsDeclared.add(self.curToken.text)

            self.match(TokenType.IDENT)

        # GOTO
        elif self.checkToken(TokenType.GOTO):
            print("STATEMENT-GOTO (" + self.peekToken.text + ")")
            self.nextToken()
            self.match(TokenType.IDENT)

        # LET
        elif self.checkToken(TokenType.LET):
            print("STATEMENT-LET (" + self.peekToken.text + ")")
            self.nextToken()

            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)

            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()

        # INPUT
        elif self.checkToken(TokenType.INPUT):
            print("STATEMENT-INPUT (" + self.peekToken.text + ")")
            self.nextToken()

            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)

            self.match(TokenType.IDENT)
        else:
            self.abort("Invalid statement at " + self.curToken.text +
                       " (" + self.curToken.kind.name + ")")

        self.nl()

    # nl ::= '\n'+
    def nl(self):
        print("NEWLINE")
        self.match(TokenType.NEWLINE)
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

    def expression(self):
        print("EXPRESSION")

        self.term()
        while self.checkToken(TokenType.PLUS) or\
                self.checkToken(TokenType.MINUS):
            self.nextToken()
            self.term()

    def term(self):
        print("TERM")

        self.unary()
        while self.checkToken(TokenType.ASTERISK) or\
                self.checkToken(TokenType.SLASH):
            self.nextToken()
            self.unary()

    def unary(self):
        print("UNARY")
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.nextToken()
        self.primary()

    def primary(self):
        print("Primary (" + self.curToken.text + ")")

        if self.checkToken(TokenType.NUMBER):
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            if self.curToken.text not in self.symbols:
                self.abort(
                    "Referencing variable before assignment: " +
                    self.curToken.text)
            self.nextToken()
        else:
            self.abort("Unexpected token at " + self.curToken.text)

    def comparison(self):
        print("COMPARISON")

        self.expression()
        if self.isComparisonOperator():
            self.nextToken()
            self.expression()
        else:
            self.abort("Expected comparison. Got: " + self.curToken.kind.name)

        while self.isComparisonOperator():
            self.nextToken()
            self.expression()
