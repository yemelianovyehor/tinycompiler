from lex import Lexer, TokenType


def main():
    source = "IF+-123 foo*THEN/"
    lexer = Lexer(source)

    token = lexer.getToken()
    while token is not None and token.kind != TokenType.EOF:
        print(token.kind)
        token = lexer.getToken()


main()
