import anl_lex
from anl_lex import Token

def run(result_lex):
    parser = Parser(result_lex)
    pars_res = parser.doParsing()
    if len(pars_res) == 0:
        pars_res.append("SUCESSO!")
    return pars_res

class Parser:
    def __init__(self, result_lex):
        self.lex_array = result_lex#array que vai ter todos os token e lexemas que o analisador sintático vai analisar
        self.pos = 0#index da lexeme_matrix
        self.lexeme_matrix = []#vai ser a matriz que guarda o valor da linha o tipo do token e o lexema de cada saída do léxico
        self.current_char = None#é uma linha inteira da matriz lexeme_matrix
        self.pars_res = []

    #a funcao cria uma matriz em que cada linha vai conter o número de linha do token, o tipo do token e o lexema em si
    def make_matrix(self):
        arr = []
        for i in range(len(self.lex_array)):#se o contador for zero quer dizer que ele está lendo um numero de linha, se o count for 1 quer dizer que ele está lendo o tipo do token e o lexema. Quando ele lê os dois ele apaga a lista auxiliar arr e recomeça o processo para a proxima linha e lexema
            if i % 2 == 0:
                arr.append(self.lex_array[i])#número de linha do lexema
            else:
                aux_char = self.lex_array[i]
                aux_char = str(aux_char)
                tkn_type = aux_char[0:3]#cortar a string para pegar apenas as três letras com o tipo to token
                lexeme = aux_char[4:]#cortar a string para pegar o lexema
                arr.append(tkn_type)
                arr.append(lexeme)
                self.lexeme_matrix.append(arr)
                arr = []
    
    def get_current_char(self, pos):
        self.make_matrix()
        return self.lexeme_matrix[pos]

    def next_char(self):
        self.pos += 1
        print("pos: " + str(self.pos))
        if self.pos < (len(self.lexeme_matrix)):
            print(len(self.lexeme_matrix))
            print(self.pos)
            self.current_char = self.lexeme_matrix[self.pos]
    
    def doParsing(self):
        self.pars_res = []
        if len(self.lex_array) > 0:# roda se houver algum resultado do analisador léxico
            self.start()# inicia a cadeia de leitura da gramática
        return self.pars_res#onde vão ser colocados os erros sintáticos ou a mensagem de sucesso no final do programa

    #####################################
    ## Derivação da "árvore" sintática ##
    #####################################

    def start(self):
        self.current_char = self.get_current_char(0)# ele precisa iniciar o current_char, mas depois o next char já atualiza automaticamente o current_char
        if self.current_char[2] == "algoritmo":
            self.next_char()
            self.algoritmo()
        elif self.current_char[2] == 'funcao':
            self.next_char()
            self.funcao()
            self.start()
        elif self.current_char[2] == 'variaveis':
            self.next_char()
            self.variaveis()
            self.a()
        elif self.current_char[2] == 'constantes':
            self.next_char()
            self.constantes()
            self.b()
        elif self.current_char[2] == 'registro':
            self.next_char()
            self.registro()
            self.start()
        else: self.erro()

    def algoritmo(self):
        if self.current_char[2] == '{':
            self.next_char()
            self.conteudo()
            #no final da checagem de conteúdo eu vejo se ele termina com um '}'
            self.next_char()
            if self.current_char[2] != '}':
                self.erro()
        else: self.erro()

    def conteudo(self):
        if self.current_char[2] == 'escreva':
            self.next_char()
            self.escreva()
        if self.current_char[2] == 'retorno':
            self.next_char()
            self.retorno()

    def escreva(self):
        if self.current_char[2] == '(':
            self.next_char()
            self.escont()
        else: self.erro()

    def retorno(self):
        self.valor()
        self.next_char()
        if self.current_char[2] != ";":
            self.erro()
    
    def valor(self):
        self.bool()

    def bool(self):
        if self.current_char[2] != 'verdadeiro' and self.current_char[2] != 'falso':
            self.erro()
    
    def erro(self):
        self.pars_res.append("NO")
        #print("I wasn't supposed to be here!")