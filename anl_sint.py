import anl_lex
from anl_lex import Token

def run(result_lex):
    parser = Parser(result_lex)
    parser_result = parser.doParsing()
    return parser_result

class Parser:
    def __init__(self, result_lex):
        self.lex_array = result_lex
        self.pos = 0
        self.current_char = result_lex[0]

    def next_char(self):
        if self.pos < (len(self.result_lex) - 1):
            self.pos += 1
            self.current_char = self.result_lex[self.pos]
    
    def doParsing(self):
        parser_result = []
        self.start(parser_result)#inicia a cadeia de leitura da gramática


