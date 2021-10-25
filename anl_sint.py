from types import coroutine
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
        #print("pos: " + str(self.pos))
        if self.pos < (len(self.lexeme_matrix)):
            #print(len(self.lexeme_matrix))
            #print(self.pos)
            self.current_char = self.lexeme_matrix[self.pos]
            return None
        else: return True
    
    def prev_char(self):
        if self.pos != 0:
            self.pos -= 1
            self.current_char = self.lexeme_matrix[self.pos]
    
    def doParsing(self):
        self.pars_res = []
        if len(self.lex_array) > 0:# roda se houver algum resultado do analisador léxico
            self.start()# inicia a cadeia de leitura da gramática
        return self.pars_res#onde vão ser colocados os erros sintáticos ou a mensagem de sucesso no final do programa

    #####################################
    ## Derivação da "árvore" sintática ##
    #####################################

    ##START##
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
        else: self.erro('CMMF')

    ##ALGORITMO##
    def algoritmo(self):
        if self.current_char[2] == '{':
            self.next_char()
            if self.conteudo():# se conteudo retornar verdadeiro quer dizer que não estava vazio então ele checa no final se foi fechado a chave, se retornar falso é porque ele estava vazio
            #no final da checagem de conteúdo eu vejo se ele termina com um '}'
                self.next_char()
                if self.current_char[2] != '}':
                    self.panic('CMMFalgoritmo', ';')
        else: self.panic('CMMF', ';')

    ##CONTEUDO##
    def conteudo(self):
        if self.current_char[2] == 'variavies':
            self.next_char()
            self.variaveis()
            self.next_char()
            self.conteudo()
        print(self.current_char[2])
        if self.current_char[2] == 'constantes':
            self.next_char()
            self.constantes()
            self.next_char()
            self.conteudo()
            return True
        if self.current_char[2] == 'leia':
            self.next_char()
            self.leia()
            self.next_char()
            self.conteudo()
            return True
        elif self.current_char[2] == 'escreva':
            self.next_char()
            self.escreva()
            print(self.current_char[2])
            self.next_char()
            print(self.current_char[2])
            self.conteudo()
            return True
        elif self.current_char[2] == 'retorno':
            self.next_char()
            self.retorno()
            return True
        elif self.current_char[2] == '}':#quer dizer que o conteudo foi 'conteudo{}'
            self.next_char()
            return False
        elif self.current_char[2] == ';':
            if self.next_char():
                return None
            else: self.prev_char()
        else:self.panic('CFMF1', ';')

    ##VARIAVEIS##
    def variavies(self):
        if self.current_char[2] == '{':
            self.next_char()
            self.var()
        else: self.panic('CMF', ';')

    ##VAR##
    def var(self):
        self.tipo()
        self.next_char()
        self.ide()
        self.next_char()
        self.varcont()
        self.next_char()

    ##VARCONT##
    def varcont(self):
        if self.current_char[2] == ',' or self.current_char[2] == ';':
            self.varfinal()
        else:
            self.varinit()
            self.next_char()
            self.varfinal()

    ##VARFINAL##
    def varfinal(self):
        if self.current_char[2] == ',':
            self.next_char()
            self.varalt()
        elif self.current_char[2] == ';':
            self.next_char()
            self.varfim()

    ##VARALT##
    def varalt(self):
        self.ide()
        self.next_char()
        self.varcont()

    ##VARFIM##
    def varfim(self):
        if self.current_char[2] == '}':
            self.next_char()
        else:
            self.var()

    ##CONSTANTES##
    def constantes(self):
        if self.current_char[2] == '{':
            self.next_char()
            self.const()
        else: self.panic('CMMF', ';')

    ##CONST##
    def const(self):
        self.tipo()
        self.next_char()
        self.ide()
        self.next_char()
        self.varinit()
        self.next_char()
        self.constcont()
    
    ##TIPO##
    def tipo(self):
        if (self.current_char[2] != 'inteiro' and self.current_char[2] != 'real' and self.current_char[2] != 'boolenao' 
            and self.current_char[2] != 'cadeia' and self.current_char[2] != 'char' and self.current_char[2] != 'registro'):
            self.panic('VMF', ';')

    def ide(self):
        if self.current_char[1] != 'IDE':
            self.panic('VMF', ';')

    def varinit(self):
        if self.current_char[2] == '=':
            self.next_char()
            self.valor()
        elif self.current_char[2] == '[':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.next_char()
                if self.current_char == ']':
                    self.next_char()
                    self.varinitcont()
                else: self.panic('VMF', ';')
            else: self.panic('VMF', ';')
        else: self.panic('VMF', ';')
    
    ##VARINITCONT##
    def varinitcont(self):
        if self.current_char[2] == '{':
            self.next_char()
            self.vetor()
            self.next_char()
        elif self.current_char[2] == '[':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.next_char()
                if self.current_char[2] == ']':
                    self.next_char()
                    self.varinitcontmatr()
                else: self.panic('VMF', ';')
            else: self.panic('VMF', ';')
        else: self.panic('CMF', ';')

    ##VARINITCONTMATR##
    def varinitcontmatr(self):
        if self.current_char[2] == '{':
            self.next_char()
            self.vetor()
            self.next_char()
            if self.current_char[2] == ',':
                self.next_char()
                if self.current_char[2] == '{':
                    self.next_char()
                    self.vetor()
                else: self.panic('VMF', ';')
            else: self.panic('VMF', ';')
        elif self.current_char[2] == '[':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.next_char()
                if self.current_char[2] == ']':
                    self.next_char()
                    if self.current_char[2] == '=':
                        self.next_char()
                        if self.current_char[2] == '{':
                            self.next_char()
                            self.vetor()
                            self.next_char()
                            if self.current_char[2] == ',':
                                self.next_char()
                                if self.current_char[2] == '{':
                                    self.next_char()
                                    self.vetor()
                                    self.next_char()
                                    if self.current_char[2] == ',':
                                        self.next_char()
                                        if self.current_char[2] == '{':
                                            self.next_char()
                                            self.vetor()
                                            self.next_char()
                                        else: self.panic('VMF', ';')
                                    else: self.panic('VMF', ';')
                                else: self.panic('VMF', ';')
                            else: self.panic('VMF', ';')
                        else: self.panic('VMF', ';')
                    else: self.panic('VMF', ';')
                else: self.panic('VMF', ';')
            else: self.panic('VMF', ';')
        else: self.panic('VMF', ';')

    ##VETOR##
    def vetor(self):
        self.valor()
        self.next_char()
        self.vetorcont()
        self.next_char()

    ##VETORCONT##
    def vetorcont(self):
        if self.current_char[2] == ',':
            self.next_char()
            self.vetor()
        elif self.current_char[2] == '}':
            self.next_char()
    
    def valor(self):
        if self.current_char[1] == 'REAL':
            return None
        elif self.current_char[2] == '-':
            self.next_char()
            if self.current_char[1] != 'NRO':
                self.panic('AMF', ';')
        #elif self.current_char[1] == 'IDE' or self.current_char[1] == 'NRO' or self.current_char[1] == ''#indeterminação no caso do negativo que pode ser um -<REAL> ou - em <exparitme>
        elif self.current_char[1] == 'BOOL':#se ele for um booleano ele pode ir para dois caminhos, então se checa o que vem depois para saber qual caminho seguir
            self.next_char()
            if self.current_char[1] == 'LOG': self.explogica()
            elif self.current_char[2] == ';': self.prev_char(); self.bool()
            else: self.panic('AMF', ';')
            
    
    def constcont(self):
        if self.current_char[2] == ',':
            self.next_char()
            self.constalt()
        elif self.current_char[2] == ';':
            self.next_char()
            self.constfim()

    def constalt(self):
        if self.current_char[1] == 'IDE':
            self.next_char()
            self.varinit()
            self.next_char()
            self.constcont()

    def constfim(self):
        self.const()

    def leia(self):
        if self.current_char[2] == '(':
            self.next_char()
            self.leiacont()
        else: self.erro('CFMF')
    
    def leiacont(self):
        self.acessovar()
        self.leiafim()
    
    def leiafim(self):
        if self.current_char == ',':
            self.next_char()
            self.leiacont()
        elif self.current_char == ')':
            self.next_char()
            if self.current_char != ';':
                self.erro()
            else: self.next_char()
        else: self.erro('CFMF')

    def escreva(self):
        if self.current_char[2] == '(':
            self.next_char()
            self.escont()
        else: self.erro('CFMF')

    def escont(self):#nessa produção ele gera outras três produções de não terminal, então é analisado o tipo to token para saber qual caminho prosseguir
        if self.current_char[1] == 'IDE':
            self.next_char()
            #self.acessovar()
            self.esfim()
        elif self.current_char[1] == 'CAD':
            self.next_char()
            #self.cadeia()#teoricamente não precisa porque ele já identificou que é uma cadeia ou um caractere, então ele só chama esfim para ver se tem mais
            self.esfim()
        elif self.current_char[1] == 'CAR':
            self.next_char()
            #self.char()
            self.esfim()
        else: self.erro('CFMF')
    
    def esfim(self):
        if self.current_char[2] == ',':
            self.next_char()
            self.escont()
        elif self.current_char[2] == ')':
            self.next_char()
            if self.current_char[2] != ';':
                self.erro('CFMF2')
            else: self.next_char();#se o último character for realmente o ';' então o escreva acabou e eu passo para o próximo character a ser analisado
        else: self.erro('CFMF')

    def retorno(self):
        self.valor()
        self.next_char()
        if self.current_char[2] != ";":
            self.erro('CMMF')
    
    def valor(self):
        self.bool()

    def bool(self):
        if self.current_char[2] != 'verdadeiro' and self.current_char[2] != 'falso':
            self.panico('VMF', ';')
    
    def acessovar(self):
        if self.current_char[1] == 'IDE':
            self.next_char()
            self.acessovarcont()
    
    def erro(self, error):
        self.pars_res.append(error)
        #print("I wasn't supposed to be here!")
    
    def panic(self, error, stop_char):
        self.pars_res.append(error)
        while self.current_char[2] != stop_char:
            if self.next_char():#next char retorna True caso ele chegue ao final do array, caso contrário ele simplesmente itera e retorna None
                break
            