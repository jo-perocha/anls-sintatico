from types import coroutine
from typing import Counter
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
        self.lexeme_matrix = []#vai ser a matriz que guarda o valor da linha o tipo  token e o lexema de cada saída do léxico
        self.current_char = None#é uma linha inteira da matriz lexeme_matrix
        self.pars_res = []
        self.relacional_list =['<', '>', '<=', '>=', '!=', '==']
        self.aritmetica_list =['+', '-', '*', '/']
        self.aritmetica_add_list =['++', '--']
        self.logica_list =['&&', '||']
        self.bool_list =['verdadeiro', 'falso']
        self.counter = 0 #auxiliar para debugar onde aconteceu o primeiro erro

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

    #o next_char vai passar para o próximo token na cadeia. Mas ele também serve para verificar se chegou no final. Se chegou no final da cadeia ele retorna True, se não ele retorna None#
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
                    self.panic(self.current_char[0], ';')
        else: self.panic(self.current_char[0], ';')

    ##CONTEUDO##
    def conteudo(self):
        #print(self.current_char[2])
        #print(self.pars_res)
        if self.current_char[2] == 'variaveis':
            self.next_char()
            self.variaveis()
            self.next_char()
            self.conteudo()
        elif self.current_char[2] == 'constantes':
            self.next_char()
            self.constantes()
            self.next_char()
            self.conteudo()
            return True
        elif self.current_char[2] == 'se':
            self.next_char()
            if self.current_char[2] == '(':
                self.next_char()
                self.se()
                self.next_char()
                self.conteudo()
        elif self.current_char[2] == 'leia':
            self.next_char()
            self.leia()
            #self.next_char()#é pra ser retirado
            self.conteudo()
            return True
        elif self.current_char[2] == 'escreva':
            self.next_char()
            self.escreva()
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
            if not self.next_char():#é pra ver se tem next char?
                return None
            else: self.prev_char()
        else:self.panic(self.current_char[0], ';')
    
    #SE#
    def se(self):
        self.expressao()
        self.next_char()
        if self.current_char[2] == ')':
            self.next_char()
            if self.current_char[2] == '{':
                self.next_char()
                self.conteudo()#talvez precise de um next char
                if self.current_char[2] == '}':
                    self.next_char()
                    self.senao()
                else:self.panic(self.current_char[0], ';')
            else:self.panic(self.current_char[0], ';')
        else:self.panic(self.current_char[0], ';')
    
    #EXPRESSAO#
    def expressao(self):#começa com uma indeterminação entre expressão genérica e expressão aritmética
        if self.current_char[2] in self.bool_list:
            self.next_char()
            self.expressaocont()
        elif self.current_char[2] == '!':
            self.next_char()
            self.exprexc()
        elif self.current_char[1] == 'IDE':
            self.acessovar()
            if self.current_char[2] in self.relacional_list:
                self.next_char()
                self.exprelacionalb()
            elif self.current_char[2] in self.logica_list:
                self.next_char()
                self.expressao()
            elif self.current_char[2] in self.aritmetica_list:
                self.next_char()
                self.exparitmeticab()
                self.next_char()
                self.expressaocont()
        elif self.current_char[1] == 'NRO':
            self.next_char()
            if self.current_char[2] in self.relacional_list:
                self.next_char()
                self.exprelacionalb()
            elif self.current_char[2] in self.logica_list:
                self.next_char()
                self.expressao()
            elif self.current_char[2] in self.aritmetica_list:
                self.next_char()
                self.exparitmeticab()
                self.next_char()
                self.expressaocont()
        elif self.current_char[2] == '-':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.next_char()
                if self.current_char[2] in self.aritmetica_list:
                    self.next_char()
                    self.exparitmeticab()
                    self.next_char()
                    self.expressaocont()
                elif self.current_char[2] in self.relacional_list:
                    self.next_char()
                    self.exprelacionalb()
                elif self.current_char[2] in self.logica_list:
                    self.next_char()
                    self.expressao()
        #repete quase que a mesma coisa, mas para iniciar com parênteses
        elif self.current_char[2] == '(':
            self.next_char()
            if self.current_char[1] == 'IDE':
                self.acessovar()
                if self.current_char[2] == ')':
                    self.next_char()
                    self.exparitmeticacontb()
                else:
                    if self.current_char[2] in self.relacional_list:
                        self.next_char()
                        self.exprelacionalb()
                    elif self.current_char[2] in self.logica_list:
                        self.next_char()
                        self.expressao()
                    elif self.current_char[2] in self.aritmetica_list:
                        self.next_char()
                        self.exparitmeticab()
                        self.next_char()
                        self.expressaocont()
                    else: self.panic(self.current_char[0], ';')
            elif self.current_char[2] == 'NRO':
                self.next_char()
                if self.current_char[2] == ')':
                    self.next_char()
                    self.exparitmeticacontb()
                else:
                    if self.current_char[2] in self.aritmetica_list:
                        self.next_char()
                        self.exparitmeticab()
                        self.next_char()
                        self.expressaocont()
                    elif self.current_char[2] in self.relacional_list:
                        self.next_char()
                        self.exprelacionalb()
                    elif self.current_char[2] in self.logica_list:
                        self.next_char()
                        self.expressao()
                    else: self.panic(self.current_char[0], ';')
            elif self.current_char[2] == '-':
                self.next_char()
                if self.current_char[1] == 'NRO':
                    self.next_char()
                    if self.current_char[2] in self.aritmetica_list:
                        self.next_char()
                        self.exparitmeticab()
                        self.next_char()
                        self.expressaocont()
                    elif self.current_char[2] in self.relacional_list:
                        self.next_char()
                        self.exprelacionalb()
                    elif self.current_char[2] in self.logica_list:
                        self.next_char()
                        self.expressao()
                    else: self.panic(self.current_char[0], ';')
                else: self.panic(self.current_char[0], ';')
            elif self.current_char[2] == '!':
                self.next_char()
                self.exprexc()
            elif self.current_char[2] in self.bool_list:
                self.next_char()
                self.expressaocont()
            else: self.panic(self.current_char[0], ';')
        else: self.panic(self.current_char[0], ';')
    
    #EXPREXC#
    def exprexc(self):
        if self.current_char[2] == '(':
            self.next_char()
            self.expressao
            self.next_char()
            if self.current_char[2] == ')':
                self.expressaocontb()
            else: self.panic(self.current_char[0], ';')
        elif self.current_char[2] in self.bool_list:
            self.next_char()
            self.expressaocontb()
        elif self.current_char[1] == 'IDE': 
            self.acessovar()
            self.expressaocontb()
        else: self.panic(self.current_char[0], ';')
    
    #EXPRESSAOCONT#
    def expressaocont(self):
        if self.current_char[2] in self.logica_list:
            self.next_char()
            self.expressao()
        elif self.current_char[2] in self.relacional_list:
            self.next_char()
            self.exprelacionalb()
        else: self.panic(self.current_char[0], ';')
    
    #EXPRESSAOCONTB#
    def expressaocontb(self):
        if self.current_char[2] in self.logica_list:
            self.next_char()
            self.expressao()
        elif self.current_char[2] == '!=' or self.current_char[2] == '==':
            self.next_char()
            self.exprelacionalb()
    
    #EXPRELACIONALB#
    def exprelacionalb(self):
        if self.current_char[1] == 'IDE':
            self.acessovar()
            if self.current_char[2] in self.aritmetica_list:
                self.exparitmeticab()
        elif self.current_char[1] == 'CAR':
            return None
        elif self.current_char[1] == 'NRO':
            return None
        elif self.current_char[1] == '-':
            self.next_char()
            if self.current_char[1] == 'NRO':
                return None
        elif self.current_char[2] == '(':
            self.next_char()
            self.expressao()
            self.next_char()
            if self.current_char[2] == ')':
                return None
            else: self.panic(self.current_char[0], ';')
        else: self.panic(self.current_char[0], ';')

    #EXPARITMETICA#
    def exparitmetica(self):
        if self.current_char[1] == 'IDE':
            self.acessovar()
            self.exparitmeticacont()
        elif self.current_char[1] == 'NRO':
            self.next_char()
            self.exparitmeticacont()
        elif self.current_char[2] == '-':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.exparitmeticacont()
            else: self.panic(self.current_char[0], ';')
        elif self.current_char[2] == '(':
            self.next_char()
            self.exparitmeticaparen()
        else: self.panic(self.current_char[0], ';')
    
    #EXPARITMETICAPAREN#
    def exparitmeticaparen(self):
        if self.current_char[1] == 'IDE':
            self.acessovar()
            if self.current_char[2] == ')':
                self.next_char()
                self.exparitmeticacontb()
            else:
                self.exparitmeticacont()
        elif self.current_char[1] == 'NRO':
            self.next_char()
            if self.current_char[2] == ')':
                self.next_char()
                self.exparitmeticacontb()
            else: 
                self.exparitmeticacont()
        elif self.current_char[2] == '-':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.exparitmeticacont()
                self.next_char()
                if self.current_char[2] == ')':
                    self.exparitmeticacontb()
                else: self.panic(self.current_char[0], ';')
            else: 
                self.panic(self.current_char[0], ';')
        elif self.current_char[2] == '(':
            self.next_char()
            self.exparitmeticaparen()
            self.next_char()
            if self.current_char[2] == ')':
                self.exparitmeticacontb()
            else: self.panic(self.current_char[0], ';')
        else: self.panic(self.current_char[0], ';')
    
    #EXPEXPARITMETICACONT#
    def exparitmeticacont(self):
        if self.current_char[2] in self.aritmetica_list:
            self.next_char()
            self.exparitmeticab()
    
    #EXPARITMETICAB#
    def exparitmeticab(self):
        if self.current_char[1] == 'IDE':
            self.acessovar()
            self.exparitmeticacontb()
        elif self.current_char[1] == 'NRO':
            self.next_char()
            self.exparitmeticacontb()
        elif self.current_char[1] == '-':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.exparitmeticacontb()
            else: self.panic(self.current_char[0], ';')
        elif self.current_char[1] == '(':
            self.next_char()
            self.exparitmeticabparen()

    #EXPARITMETICABPAREN#
    def exparitmeticabparen(self):
        if self.current_char[1] == 'IDE':
            self.acessovar()
            if self.current_char[2] == ')':
                self.next_char()
                self.exparitmeticacontb()
            else:
                self.exparitmeticab()
        elif self.current_char[1] == 'NRO':
            self.next_char()
            if self.current_char[2] == ')':
                self.next_char()
                self.exparitmeticacontb()
            else: 
                self.exparitmeticab()
        elif self.current_char[2] == '-':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.exparitmeticab()
                self.next_char()
                if self.current_char[2] == ')':
                    self.exparitmeticacontb()
                else: self.panic(self.current_char[0], ';')
            else: 
                self.panic(self.current_char[0], ';')
        elif self.current_char[2] == '(':
            self.next_char()
            self.exparitmeticabparen()
            self.next_char()
            if self.current_char[2] == ')':
                self.exparitmeticacontb()
            else: self.panic(self.current_char[0], ';')
        else: self.panic(self.current_char[0], ';')
    
    #EXPARITMETICACONTB#
    def exparitmeticacontb(self):
        if self.current_char[2] in self.aritmetica_list:
            self.next_char()
            self.exparitmeticab()
    
    #EXPATRIBUICAO#
    def expatribuicao(self):
        self.valor()
        self.next_char()
        self.expatribuicaocont()

    #EXPATRIBUICAOCONT#
    def expatribuicaocont(self):
        if self.current_char[2] in self.aritmetica_add_list:
            self.next_char()
            if self.current_char[2] == ';':
                return None
            else: self.panic(self.current_char[0], ';')
        elif self.current_char[2] == ';':
            return None
        else: self.panic(self.current_char[0], ';')
    
    #VAlOR#
    def valor(self):
        if self.current_char[1] == 'CAR':
            return None
        elif self.current_char[1] == 'CAD':
            return None
        #elif self.current_char[1] == falta chamada de funcao
        #indeterminacao entre IDE, NRO, negativo, e (
        if self.current_char[2] == '(':
            self.next_char()
            self.paran()
        else:
            self.expressaoalt()
    
    #EXPRESSAOALT#
    def expressaoalt(self):
        if self.current_char[2] in self.bool_list:
            self.next_char()
            self.expressaocontc()
        elif self.current_char[2] == '!':
            self.next_char()
            self.exprexcalt()
        elif self.current_char[1] == 'IDE':
            self.acessovar()
            if self.current_char[2] in self.relacional_list:
                self.next_char()
                self.exprelacionalb()
            elif self.current_char[2] in self.logica_list:
                self.next_char()
                self.expressaoalt()
            elif self.current_char[2] in self.aritmetica_list:
                self.next_char()
                self.exparitmeticab()
                self.next_char()
                self.expressaocontc()
        elif self.current_char[1] == 'NRO':
            self.next_char()
            if self.current_char[2] in self.relacional_list:
                self.next_char()
                self.exprelacionalb()
            elif self.current_char[2] in self.logica_list:
                self.next_char()
                self.expressaoalt()
            elif self.current_char[2] in self.aritmetica_list:
                self.next_char()
                self.exparitmeticab()
                self.next_char()
                self.expressaocontc()
        elif self.current_char[2] == '-':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.next_char()
                if self.current_char[2] in self.aritmetica_list:
                    self.next_char()
                    self.exparitmeticab()
                    self.next_char()
                    self.expressaocontc()
                elif self.current_char[2] in self.relacional_list:
                    self.next_char()
                    self.exprelacionalb()
                elif self.current_char[2] in self.logica_list:
                    self.next_char()
                    self.expressaoalt()
        #repete quase que a mesma coisa, mas para iniciar com parênteses
        elif self.current_char[2] == '(':
            self.next_char()
            if self.current_char[1] == 'IDE':
                self.acessovar()
                if self.current_char[2] == ')':
                    self.next_char()
                    self.exparitmeticacontc()
                else:
                    if self.current_char[2] in self.relacional_list:
                        self.next_char()
                        self.exprelacionalb()
                    elif self.current_char[2] in self.logica_list:
                        self.next_char()
                        self.expressaoalt()
                    elif self.current_char[2] in self.aritmetica_list:
                        self.next_char()
                        self.exparitmeticab()
                        self.next_char()
                        self.expressaocontc()
                    else: self.panic(self.current_char[0], ';')
            elif self.current_char[2] == 'NRO':
                self.next_char()
                if self.current_char[2] == ')':
                    self.next_char()
                    self.exparitmeticacontc()
                else:
                    if self.current_char[2] in self.aritmetica_list:
                        self.next_char()
                        self.exparitmeticab()
                        self.next_char()
                        self.expressaocontc()
                    elif self.current_char[2] in self.relacional_list:
                        self.next_char()
                        self.exprelacionalb()
                    elif self.current_char[2] in self.logica_list:
                        self.next_char()
                        self.expressaoalt()
                    else: self.panic(self.current_char[0], ';')
            elif self.current_char[2] == '-':
                self.next_char()
                if self.current_char[1] == 'NRO':
                    self.next_char()
                    if self.current_char[2] in self.aritmetica_list:
                        self.next_char()
                        self.exparitmeticab()
                        self.next_char()
                        self.expressaocontc()
                    elif self.current_char[2] in self.relacional_list:
                        self.next_char()
                        self.exprelacionalb()
                    elif self.current_char[2] in self.logica_list:
                        self.next_char()
                        self.expressaoalt()
                    else: self.panic(self.current_char[0], ';')
                else: self.panic(self.current_char[0], ';')
            elif self.current_char[2] == '!':
                self.next_char()
                self.exprexcalt()
            elif self.current_char[2] in self.bool_list:
                self.next_char()
                self.expressaocontc()
            else: self.panic(self.current_char[0], ';')
        else: self.panic(self.current_char[0], ';')

    #EXPREXCALT#
    def exprexcalt(self):
        if self.current_char[2] == '(':
            self.next_char()
            self.expressaoalt()
            self.next_char()
            if self.current_char[2] == ')':
                self.expressaocontc()
            else: self.panic(self.current_char[0], ';')
        elif self.current_char[2] in self.bool_list:
            self.next_char()
            self.expressaocontc()
        elif self.current_char[1] == 'IDE':
            self.acessovar()
            self.expressaocontc()
        else: self.panic(self.current_char[0], ';')

    #EXPRESSAOCONTC#
    def expressaocontc(self):
        if self.current_char[2] in self.logica_list:
            self.next_char()
            self.expressaoalt()
        elif self.current_char[2] in self.relacional_list:
            self.next_char()
            self.exprelacionalb()

    ##VARIAVEIS##
    def variaveis(self):
        if self.current_char[2] == '{':
            self.next_char()
            self.var()
        else: self.panic(self.current_char[0], ';')

    ##VAR##
    def var(self):
        self.tipo()
        self.next_char()
        self.ide()
        self.next_char()
        self.varcont()

    ##VARCONT##
    def varcont(self):
        if self.current_char[2] == ',' or self.current_char[2] == ';':#isso permite a produção de só um ','
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
        else: self.panic(self.current_char[0], ';')

    ##CONST##
    def const(self):
        self.tipo()
        self.next_char()
        self.ide()
        self.next_char()
        self.varinit()
        print(self.current_char[2])
        self.constcont()
    
    ##TIPO##
    def tipo(self):
        if self.current_char[2] == 'inteiro':
            return None
        elif self.current_char[2] == 'real':
            return None
        elif self.current_char[2] == 'booleano':
            return None
        elif self.current_char[2] == 'cadeia':
            return None
        elif self.current_char[2] == 'char':
            return None
        elif self.current_char[2] == 'registro':
            return None
        else: self.panic(self.current_char[0], ';')

    #IDE#
    def ide(self):
        if self.current_char[1] != 'IDE':
            self.panic(self.current_char[0], ';')

    #VARINIT#
    def varinit(self):
        if self.current_char[2] == '=':
            self.next_char()
            self.valor()
            self.next_char()
            if self.current_char[2] != ',':
                if self.current_char[2] == ';':
                    return None
                else: self.panic(self.current_char[0], ';')
        elif self.current_char[2] == '[':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.next_char()
                if self.current_char[2] == ']':
                    self.next_char()
                    self.varinitcont()
                    if self.current_char[2] != ',':
                        if self.current_char[2] == ';':
                            return None
                    else: self.panic(self.current_char[0], ';')
                else: self.panic(self.current_char[0], ';')
            else: self.panic(self.current_char[0], ';')
        else: self.panic(self.current_char[0], ';')
    
    ##VARINITCONT##
    def varinitcont(self):
        if self.current_char[2] == '=':
            self.next_char()
            if self.current_char[2] == '{':
                self.next_char()
                self.vetor()
            else: self.panic(self.current_char[0], ';')
        elif self.current_char[2] == '[':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.next_char()
                if self.current_char[2] == ']':
                    self.next_char()
                    self.varinitcontmatr()
                    if self.current_char[2] != ',':
                        if self.current_char[2] == ';':
                            return None
                        else: self.panic(self.current_char[0], ';')
                else: self.panic(self.current_char[0], ';')
            else: self.panic(self.current_char[0], ';')
        else: self.panic(self.current_char[0], ';')

    ##VARINITCONTMATR##
    def varinitcontmatr(self):
        if self.current_char[2] == '=':
            self.next_char()
            if self.current_char[2] == '{':
                self.next_char()
                self.vetor()
                if self.current_char[2] == ',':
                    self.next_char()
                    if self.current_char[2] == '{':
                        self.next_char()
                        self.vetor()
                    else: self.panic(self.current_char[0], ';')
                else: self.panic(self.current_char[0], ';')
            else: self.panic(self.current_char[0], ';')
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
                            if self.current_char[2] == ',':
                                self.next_char()
                                if self.current_char[2] == '{':
                                    self.next_char()
                                    self.vetor()
                                    if self.current_char[2] == ',':
                                        self.next_char()
                                        if self.current_char[2] == '{':
                                            self.next_char()
                                            self.vetor()
                                            if self.current_char[2] == ';':
                                                return None
                                            else: self.panic(self.current_char[0], ';')
                                        else: self.panic(self.current_char[0], ';')
                                    else: self.panic(self.current_char[0], ';')
                                else: self.panic(self.current_char[0], ';')
                            else: self.panic(self.current_char[0], ';')
                        else: self.panic(self.current_char[0], ';')
                    else: self.panic(self.current_char[0], ';')
                else: self.panic(self.current_char[0], ';')
            else: self.panic(self.current_char[0], ';')
        else: self.panic(self.current_char[0], ';')

    ##VETOR##
    def vetor(self):
        self.valor()
        self.next_char()
        self.vetorcont()

    ##VETORCONT##
    def vetorcont(self):
        if self.current_char[2] == ',':
            self.next_char()
            self.vetor()
        elif self.current_char[2] == '}':
            self.next_char()

    
    # def valor(self):
    #     if self.current_char[1] == 'NRO':
    #         return None
    #     #indeterminacao entre -<NEGATIVO> e -<NEGATIVO><EXPARITMETICACONT>
    #     elif self.current_char[2] == '-':#pode ser valor negativo ou expressão aritmetica negativa. Nos dois casos ele vai ser -<negativo>, <negativo> pode ser um acessovar ou um nro
    #         self.next_char()
    #         if self.current_char[1] == 'NRO':
    #             self.next_char()
    #             if self.current_char[2] == '+' or self.current_char[2] == '-' or self.current_char[2] == '*' or self.current_char[2] == '/':
    #                 self.exparitmeticab()
    #             elif self.current_char[2] == '--' or self.current_char[2] == '++':
    #                 return None
    #             else: self.prev_char()# se ele for um -nro e não for mais nada de exparitmetica depois quer dizer que esse elemento já acabou então eu volto um character
    #         elif self.current_char[1] == 'IDE':
    #             self.acessovar()#acessovar já pula de character no final por causa da forma de sua construção
    #             if self.current_char[2] == '+' or self.current_char[2] == '-' or self.current_char[2] == '*' or self.current_char[2] == '/':
    #                 self.exparitmeticab()
    #             elif self.current_char[2] == '--' or self.current_char[2] == '++':
    #                 return None
    #             else: self.prev_char()
    #     elif self.current_char[1] == 'IDE':#indeterminação entre: explogica, exparitmetica, exprelacional, acessovar
    #         self.acessovar()
    #         if self.current_char[2] == '&&' or self.current_char[2] == '||':
    #             self.next_char()
    #             self.explogica()
    #             self.next_char()
    #             if self.current_char[2] == '==' or self.current_char[2] == '!=':
    #                 self.exprelacionalb()
    #             else: self.prev_char()
    #         elif self.current_char[2] == '+' or self.current_char[2] == '-' or self.current_char[2] == '*' or self.current_char[2] == '/':
    #                 self.exparitmeticab()
    #                 #self.next_char()
    #                 #if self.current_char[2] == '!=' or self.current_char[2] == '==' or self.current_char[2] == '>=' or self.current_char[2] == '<=' or self.current_char[2] == '<' or self.current_char[2] == '>'
    #         elif self.current_char[2] == '--' or self.current_char[2] == '++':
    #                 return None
    #     elif self.current_char[1] == 'PRE':
    #         return None#deve ter a indeterminação
    #     elif self.current_char[1] == 'CAR':
    #         return None
    #     elif self.current_char[1] == 'CAD':
    #         return None
    #     else: self.panic(self.current_char[0], ';')

        # elif self.current_char[1] == 'BOOL':#se ele for um booleano ele pode ir para dois caminhos, então se checa o que vem depois para saber qual caminho seguir
        #     self.next_char()
        #     if self.current_char[1] == 'LOG': self.explogica()
        #     elif self.current_char[2] == ';': self.prev_char(); self.bool()
        #     else: self.panic(self.current_char[0], ';')
            
    
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
            self.constcont()

    def constfim(self):
        if self.current_char[1] == 'PRE':
            self.const()
        elif self.current_char[2] == '}':
            return None
        

    def leia(self):
        if self.current_char[2] == '(':
            self.next_char()
            self.leiacont()
        else: self.panic(self.current_char[0], ';')
    
    def leiacont(self):
        self.acessovar()
        #self.next_char()
        self.leiafim()
    
    def leiafim(self):
        if self.current_char[2] == ',':
            self.next_char()
            self.leiacont()
        elif self.current_char[2] == ')':
            self.next_char()
            if self.current_char[2] != ';':
                self.panic(self.current_char[0], ';')
            else: self.next_char()
        else: self.panic(self.current_char[0], ';')

    def escreva(self):
        if self.current_char[2] == '(':
            self.next_char()
            self.escont()
        else: self.panic(self.current_char[0], ';')

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
        else: self.panic(self.current_char[0], ';')
    
    def esfim(self):
        if self.current_char[2] == ',':
            self.next_char()
            self.escont()
        elif self.current_char[2] == ')':
            self.next_char()
            if self.current_char[2] != ';':
                self.panic(self.current_char[0], ';')
            else: self.next_char()#se o último character for realmente o ';' então o escreva acabou e eu passo para o próximo character a ser analisado
        else: self.panic(self.current_char[0], ';')

    def retorno(self):
        self.valor()
        self.next_char()
        if self.current_char[2] != ";":
            self.panic(self.current_char[0], ';')

    def bool(self):
        if self.current_char[2] != 'verdadeiro' and self.current_char[2] != 'falso':
            self.panic(self.current_char[0], ';')
    
    
    #ACESSOVAR#
    def acessovar(self):
        if self.current_char[1] == 'IDE':
            self.next_char()
            self.acessovarcont()
        else: self.panic(self.current_char[0], ';')
    
    #ACESSOVARCONT#
    def acessovarcont(self):
        if self.current_char[2] == '.':
            self.next_char()
            self.acessovar()
        elif self.current_char[2] == '[':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.next_char()
                if self.current_char[2] == ']':
                    self.next_char()
                    self.acessovarcontb()
                else: self.panic(self.current_char[0], ';')
            else: self.panic(self.current_char[0], ';')
        else: return None

    #ACESSOVARCONTB#
    def acessovarcontb(self):
        if self.current_char[2] == '[':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.next_char()
                if self.current_char[2] == ']':
                    self.next_char()
                    self.acessovarcontc()
                else: self.panic(self.current_char[0], ';')
            else: self.panic(self.current_char[0], ';')
        else: return None
    
    #ACESSOVARCONTC#
    def acessovarcontc(self):
        if self.current_char[2] == '[':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.next_char()
                if self.current_char[2] == ']':
                    self.next_char()
                else: self.panic(self.current_char[0], ';')
            else: self.panic(self.current_char[0], ';')
        else: return None

    def erro(self, error):
        self.pars_res.append(error)
        #print("I wasn't supposed to be here!")
    
    def panic(self, error_line, stop_char):
        self.counter += 1
        error_message = 'Erro Sintático na linha: ' + str(error_line)
        self.pars_res.append(error_message)
        while self.current_char[2] != stop_char:
            if self.next_char():#next char retorna True caso ele chegue ao final do array, caso contrário ele simplesmente itera e retorna None
                break


    #SE#
    # def se(self):
    #     #INDETERMINAÇÕES#
    #     if self.current_char[1] == 'IDE':
    #         self.acessovar()#como o acessovar pode ser utilizado em outras produções, é melhor eu mandar para o acessovar com o current_char sendo tipo IDE, para que ele possa sempre checar se é realmente IDE
    #         if self.current_char[1] == 'LOG':
    #             self.explogicacont()
    #         elif self.current_char[2] == ')': return None#caso ele seja apenas um acessovar sozinho

    #     elif self.current_char[2] == '(':#expressão lógica, expressão relacional
    #         self.next_char()
    #         if self.current_char[1] == 'IDE':#chama acessovar?
    #             self.next_char()
    #             if self.current_char[1] == 'LOG':#O operador lógico pode ser uma expressão lógica sozinha, ou uma expressão lógica dentro de uma expressão relacionla, por isso tem que checar o que vem depois
    #                 self.next_char()
    #                 self.explogica()
    #             elif(self.current_char[2] == '>' or self.current_char[2] == '<' or self.current_char[2] == '>=' or self.current_char[2] == '<='
    #                  or self.current_char[2] == '!=' or self.current_char[2] == '==' or self.current_char[2] == '+' or self.current_char[2] == '-'
    #                  or self.current_char[2] == '*' or self.current_char[2] == '/' or self.current_char[2] == '--' or self.current_char[2] == '++'):#o que vem depois do ide nas produções
    #                  self.next_char()
    #                  self.exprelacional()
    # def se(self):
    #     #eu tenho que ter casos de indeterminação para quando ele começa com "(", e ver se ele vai ser uma expressão lógica, uma expressão relacional dentro de uma expresão
    #     #lógica, ou até uma expressão aritmetica dentro de uma expressão relacional dentro de uma expressão lógica. E eu também tenho que checar todos esses casos para quando
    #     #ele começa com IDE, ou quando ele começa com um próprio número, ou todos os casos que podem iniciar uma expressão relacional/aritmética
    #     if self.current_char[2] == '!':
    #         self.explogicaexc()
    #     elif self.current_char[2] == '(':#esse vai ser a mesma coisa das produções de baixo porque tem indeterminação no "(", mas acho que ele funciona por recursão
    #         self.explogica()
    #         self.next_char()
    #         if self.current_char[2] == ')':
    #             self.explogicacont()
    #         else: self.panic(self.current_char[0], ';')
    #     elif self.current_char[2] == 'verdadeiro' or self.current_char[2] == 'falso':
    #         self.next_char()
    #         self.explogicacont()
    #     elif self.current_char[1] == 'IDE':#indeterminação entre acessovar e exprelacional. E eu tenho que ter a mesma coisa para o caso de não começar com IDE
    #         self.acessovar()
    #         #basicamente depois de uma expressão lógica começar com IDE, ela pode continuar como uma expressão lógica normal, a && b, ou pode ter uma expressão relacional
    #         #dentro de uma expressão lógica, ou pode ter uma expressão aritmetica dentro de uma relacional, que por sua vez está dentro da expressão lógica.
    #         if self.current_char[1] == 'LOG':
    #             self.explogica()
    #         #expressão relacional dentro de logica
    #         elif(self.current_char[2] in self.relacional_list):
    #             self.next_char()
    #             self.exprelacionalb()#depois eu tenho que conferir e chamar o termino da expressão lógica
    #             self.next_char()
    #             if self.current_char[2] == '&&' or self.current_char[2] == '||':
    #                 self.explogica()
    #         #expressão aritmetica dentro de uma relacional dentro de uma logica
    #         elif(self.current_char[2] in self.aritmetica_list):#se for uma expressão aritmética dentro de uma expressão relacional dentro de uma expressão lógica. Eu chamo a aritmética e depois chamo relacionalcont e depois checa para ver o lógico que vem depois
    #             self.next_char()
    #             self.exparitmeticab()
    #         elif self.current_char[2] in self.aritmetica_add_list:#depois de '--' '++' tem que vir um operador relacional?
    #             self.next_char()
    #             if self.current_char[2] in self.relacional_list:#expressão relacional e depois a finalização da expressão lógica
    #                 self.exprelacional()
    #                 self.next_char()
    #                 if self.current_char[2] in self.logica_list:
    #                     self.explogica()
    #                 else: self.panic(self.current_char[0], ';')
    #             else: self.panic(self.current_char[0], ';')
    #         else: self.panic(self.current_char[0], ';')



    #     elif self.current_char[2] == '!':#expressão lógica
    #         self.explogica()

    #     elif self.current_char[2] == 'verdadeiro' or self.current_char[2] == 'falso':#booleano, expressão lógica, expressão relacional
    #         self.explogica()

    #     #EXPRELACIONAL#
    #     elif self.current_char[1] == 'NRO' or self.current_char[2] == '-':
    #         self.exprelacional()

        # elif self.curren_char[2] == 'verdadeiro' or if self.current_char[2] == 'falso':
        # elif self.curren_char[1] == 'NRO':
        # elif self.curren_char[2] == '-':
        # elif self.current_char[2] == '!':
        # elif self.current_char[2] == '(':
        # elif self.current_char[1] == 'CHAR':     
        # elif(self.current_char[2] == '<' or self.current_char[2] == '>' or self.current_char[2] == '!=' or self.current_char[2] == '==' or self.current_char[2] == '(' or self.current_char[2] == '-'
                 #or self.current_char[2] == '<=' or self.current_char[2] == '>=' or self.current_char[1] == 'IDE' or self.current_char[1] == 'CHAR' or self.current_char[1] == 'NRO'):   

    #EXPLOGICA#
    # def se(self):
    #     #eu tenho que ter casos de indeterminação para quando ele começa com "(", e ver se ele vai ser uma expressão lógica, uma expressão relacional dentro de uma expresão
    #     #lógica, ou até uma expressão aritmetica dentro de uma expressão relacional dentro de uma expressão lógica. E eu também tenho que checar todos esses casos para quando
    #     #ele começa com IDE, ou quando ele começa com um próprio número, ou todos os casos que podem iniciar uma expressão relacional/aritmética
    #     if self.current_char[2] == '!':
    #         self.explogicaexc()
    #     elif self.current_char[2] == '(':#esse vai ser a mesma coisa das produções de baixo porque tem indeterminação no "(", mas acho que ele funciona por recursão
    #         self.explogica()
    #         self.next_char()
    #         if self.current_char[2] == ')':
    #             self.explogicacont()
    #         else: self.panic(self.current_char[0], ';')
    #     elif self.current_char[2] == 'verdadeiro' or self.current_char[2] == 'falso':
    #         self.next_char()
    #         self.explogicacont()
    #     elif self.current_char[1] == 'IDE':#indeterminação entre acessovar e exprelacional. E eu tenho que ter a mesma coisa para o caso de não começar com IDE
    #         self.acessovar()
    #         #basicamente depois de uma expressão lógica começar com IDE, ela pode continuar como uma expressão lógica normal, a && b, ou pode ter uma expressão relacional
    #         #dentro de uma expressão lógica, ou pode ter uma expressão aritmetica dentro de uma relacional, que por sua vez está dentro da expressão lógica.
    #         if self.current_char[1] == 'LOG':
    #             self.explogica()
    #         #expressão relacional dentro de logica
    #         elif(self.current_char[2] in self.relacional_list):
    #             self.next_char()
    #             self.exprelacionalb()#depois eu tenho que conferir e chamar o termino da expressão lógica
    #             self.next_char()
    #             if self.current_char[2] == '&&' or self.current_char[2] == '||':
    #                 self.explogica()
    #         #expressão aritmetica dentro de uma relacional dentro de uma logica
    #         elif(self.current_char[2] in self.aritmetica_list):#se for uma expressão aritmética dentro de uma expressão relacional dentro de uma expressão lógica. Eu chamo a aritmética e depois chamo relacionalcont e depois checa para ver o lógico que vem depois
    #             self.next_char()
    #             self.exparitmeticab()
    #         elif self.current_char[2] in self.aritmetica_add_list:#depois de '--' '++' tem que vir um operador relacional?
    #             self.next_char()
    #             if self.current_char[2] in self.relacional_list:#expressão relacional e depois a finalização da expressão lógica
    #                 self.exprelacional()
    #                 self.next_char()
    #                 if self.current_char[2] in self.logica_list:
    #                     self.explogica()
    #                 else: self.panic(self.current_char[0], ';')
    #             else: self.panic(self.current_char[0], ';')
    #         else: self.panic(self.current_char[0], ';')
            