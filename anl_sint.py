import anl_lex
from anl_lex import Token

def run(result_lex):
    parser = Parser(result_lex)
    pars_res = parser.doParsing()
    return pars_res

class Parser:
    def __init__(self, result_lex):
        self.lex_array = result_lex#array que vai ter todos os token e lexemas que o analisador sintático vai analisar
        self.pos = 1# já começa no primeiro token e não no número de linha
        self.current_char = None
        self.pars_res = []

    # A função de next_char deve pegar a cadeia de tokens e lexemas e ler apenas a parte de cada lexema. Então quando ele der um next char, a função tem que pular o número de linha
    # , ou seja ela vai andar dois de cada vez, e pular os três primeiros caracteres que são o identificador de Token(ex. CAD).
    def next_char(self):
        if self.pos < (len(self.result_lex) - 1):
            self.pos += 2
            self.current_char = self.get_current_char()

    # A função vai pegar o token e o lexema e vai partir a string para retornar como current char apenas o lexema escrito
    def get_current_char(self):
        character = self.lex_array[self.pos]
        character = str(character)
        character = character[4:]
        return character
        
    
    def doParsing(self):
        if len(self.lex_array) > 0:# roda se houver algum resultado do analisador léxico
            self.start()# inicia a cadeia de leitura da gramática
        return self.pars_res#onde vão ser colocados os erros sintáticos ou a mensagem de sucesso no final do programa

    def start(self):
        self.current_char = self.get_current_char()# ele precisa iniciar o current_char, mas depois o next char já atualiza automaticamente o current_char
        if self.current_char == 'algortimo':
            self.next_char()
            self.algoritmo()
        elif self.current_char == 'funcao':
            self.next_char()
            self.funcao()
            self.start()
        elif self.current_char == 'variaveis':
            self.next_char()
            self.variaveis()
            self.a()
        elif self.current_char == 'constantes':
            self.next_char()
            self.constantes()
            self.b()
        elif self.current_char == 'registro':
            self.next_char()
            self.registro()
            self.start()
        else: self.erro()

    def algoritmo(self):
        if self.current_char == '{':
            self.next_char()
            self.conteudo()
        #no final da checagem de conteúdo eu vejo se ele termina com um '}'
        self.next_char()
        if self.current_char != '}':
            self.erro()

    def conteudo(self):
        if self.current_char == 'escreva':
            self.next_char()
            self.escreva()
        if self.current_char == 'retorno':
            self.next_char()
            self.retorno()

    def escreva(self):
        if self.current_char == '(':
            self.next_char()
            self.escont()
        else: self.erro()

    def retorno(self):
        self.valor()
        self.next_char()
        if self.current_char != ";":
            self.erro()
    
    def valor(self):
        self.bool()

    def bool(self):
        if self.current_char != 'verdadeiro' or self.current_char != 'falso':
            self.erro()