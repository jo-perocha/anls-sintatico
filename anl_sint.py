#from _typeshed import StrOrBytesPath
from types import coroutine, prepare_class
from typing import Counter
import anl_lex
from anl_lex import Token

############################
## Dictionary Declaration ##
############################
#the symbol table is going to be an array of dictionaries, each dictionary is going to hold the information of one declared identifier
symTable = []


def run(result_lex):
    parser = Parser(result_lex)
    pars_res, sm_res = parser.doParsing()
    if len(pars_res) == 0 and len(sm_res) == 0:
        pars_res.append("SUCESSO!")
    
    return pars_res, sm_res

class Parser:
    def __init__(self, result_lex):
        self.lex_array = result_lex#array que vai ter todos os token e lexemas que o analisador sintático vai analisar
        self.pos = 0#index da lexeme_matrix
        self.lexeme_matrix = []#vai ser a matriz que guarda o valor da linha o tipo  token e o lexema de cada saída do léxico
        self.current_char = None#é uma linha inteira da matriz lexeme_matrix
        self.pars_res = []
        self.sm_res = []
        self.relacional_list =['<', '>', '<=', '>=', '!=', '==']
        self.aritmetica_list =['+', '-', '*', '/']
        self.aritmetica_add_list =['++', '--']
        self.logica_list =['&&', '||']
        self.bool_list =['verdadeiro', 'falso']
        self.counter = 0 #auxiliar para debugar onde aconteceu o primeiro erro
        self.scope = 'global' #vai dizer ser a variável que vai determinar se eu estou denro de um escopo de função 'func' ou no escopo global 'global'. Se eu entrar em uma produção de função eu mudo para 'func' e quando acabar volta para 'global'

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
        
        #self.lexeme_matrix.append([-1, 'END', '$'])
    
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
        if 'comentario de linha' in self.lex_array: self.lex_array.remove('comentario de linha')
        if 'comentario de bloco' in self.lex_array: self.lex_array.remove('comentario de bloco')
        if len(self.lex_array) > 0:# roda se houver algum resultado do analisador léxico
            self.current_char = self.get_current_char(0)# ele precisa iniciar o current_char, mas depois o next char já atualiza automaticamente o current_char
            #isso aqui é para colocar o '$' como símbolo final da cadeia de lexemas
            size = len(self.lexeme_matrix); size -= 1
            aux = self.lexeme_matrix[size]
            self.lexeme_matrix.append([aux[0], 'END', '$'])
            ##
            self.start()# inicia a cadeia de leitura da gramática
        return self.pars_res, self.sm_res#onde vão ser colocados os erros sintáticos ou a mensagem de sucesso no final do programa

    #####################################
    ## Derivação da "árvore" sintática ##
    #####################################

    ##START##
    def start(self):
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
        else: self.panic(self.current_char)
    
    #a#
    def a(self):
        if self.current_char[2] == "algoritmo":
            self.next_char()
            self.algoritmo()
        elif self.current_char[2] == 'funcao':
            self.next_char()
            self.funcao()
            self.a()
        elif self.current_char[2] == 'constantes':
            self.next_char()
            self.constantes()
            self.c()
        elif self.current_char[2] == 'registro':
            self.next_char()
            self.registro()
            self.a()
        else: self.panic(self.current_char)
    
    #b#
    def b(self):
        if self.current_char[2] == "algoritmo":
            self.next_char()
            self.algoritmo()
        elif self.current_char[2] == 'funcao':
            self.next_char()
            self.funcao()
            self.b()
        elif self.current_char[2] == 'variaveis':
            self.next_char()
            self.variaveis()
            self.c()
        elif self.current_char[2] == 'registro':
            self.next_char()
            self.registro()
            self.b()
        else: self.panic(self.current_char)
    
    #c#
    def c(self):
        if self.current_char[2] == "algoritmo":
            self.next_char()
            self.algoritmo()
        elif self.current_char[2] == 'funcao':
            self.next_char()
            self.funcao()
            self.c()
        elif self.current_char[2] == 'registro':
            self.next_char()
            self.registro()
            self.c()
        else: self.panic(self.current_char)

    #REGISTRO#
    def registro(self):
        if self.current_char[1] == 'IDE':
            sym = dict(name = str(self.current_char[2]), type = str(self.current_char[1]), scope = 'global', line = str(self.current_char[0]), rule = 'registro')
            symTable.append(sym)
            self.next_char()
            if self.current_char[2] == '{':
                self.next_char()
                self.var()#ele já checa o fechamento de }
            else: self.panic(self.current_char, '{')
        else: self.panic(self.current_char)

    #FUNCAO#
    def funcao(self):
        if self.current_char[2] == '[':
            self.tipocont()
            if self.current_char[1] == 'IDE':
                self.next_char()
                self.funcaoinit() 
        self.tipo()
        self.next_char()
        self.tipocont()
        if self.current_char[1] == 'IDE':
            self.next_char()
            self.funcaoinit() 
    
    #TIPOCONT#
    def tipocont(self):
        if self.current_char[2] == '[':
            self.next_char()
            if self.current_char[2] == ']':
                self.vetormais()
            else: self.panic(self.current_char, ']')
        else: return None

    #VETORMAIS#
    def vetormais(self):
        if self.current_char[2] == '[':
            self.next_char()
            if self.current_char[2] == ']':
                self.vetormaisum()
            else: self.panic(self.current_char, ']')
        else: self.next_char()
    
    #VETORMAISUM#
    def vetormaisum(self):
        if self.current_char[2] == '[':
            self.next_char()
            if self.current_char[2] == ']':
                self.next_char()
            else: self.panic(self.current_char, ']')
        else: self.next_char()

    #FUNCAOINIT#
    def funcaoinit(self):
        if self.current_char[2] == '(':
            self.next_char()
            self.paraninit()
            if self.current_char[2] == '{':
                self.next_char()
                self.conteudo()
                if self.current_char[2] == '}':
                    self.next_char()#talvez esse não deva estar aqui
                else: self.panic(self.current_char, '}')
            else: self.panic(self.current_char, '}')
        else: self.panic(self.current_char, ')')
    
    #PARANINIT#
    def paraninit(self):
        self.tipo()
        self.next_char()
        if self.current_char[1] == 'IDE':
            self.next_char()
            self.paraninitcont()
        else: self.panic(self.current_char, 'Token Type: IDE')

    #PARANINITCONT#
    def paraninitcont(self):
        if self.current_char[2] == ',':
            self.next_char()
            self.paraninit()
        elif self.current_char[2] == ')':
            self.next_char()
    
    #CHAMADAFUNCAO#
    def chamadafuncao(self):
        self.acessovar()
        if self.current_char[2] == '(':
            self.next_char()
            self.paran()

    ##ALGORITMO##
    def algoritmo(self):
        if self.current_char[2] == '{':
            self.next_char()
            # if self.conteudo():# se conteudo retornar verdadeiro quer dizer que não estava vazio então ele checa no final se foi fechado a chave, se retornar falso é porque ele estava vazio
            # #no final da checagem de conteúdo eu vejo se ele termina com um '}'
            #     self.next_char()
            #     if self.current_char[2] != '}':
            #         self.panic(self.current_char[0], ';')
            self.conteudo()
            if self.current_char[2] == '}':
                return None
            else: self.panic(self.current_char, '}')
        else: self.panic(self.current_char, '}')

    ##CONTEUDO##
    def conteudo(self):
        #print(self.current_char[2])
        #print(self.pars_res)
        if self.current_char[2] == 'variaveis':
            self.next_char()
            self.variaveis()
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
                self.conteudo()
                # if self.current_char[2] == '}':
                #     self.next_char()
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
            self.next_char()
            return True
        elif self.current_char[2] == '}':#quer dizer que o conteudo foi 'conteudo{}' NAO, NAO QUER DIZER NAO, pra ver se foi conteudo{}, eu posso checar se o char anterior é {. Do contrário é uma produção vazia 

            return False
        elif self.current_char[2] == ';':
            if not self.next_char():#é pra ver se tem next char?
                return None
            else: self.prev_char()
        elif self.current_char[1] == 'IDE':
            #
            auxName = self.current_char[2]
            ##
            self.acessovar()
            if self.current_char[2] == '=':
                self.next_char()
                self.expatribuicao(auxName)#termina checando se o último character é o ';' então eu tenho que dar um next_char para chamar conteúdo 
                self.next_char()
                self.conteudo()
            else: self.panic(self.current_char, '=')
        elif self.current_char[2] == 'enquanto':
            self.next_char()
            if self.current_char[2] == '(':
                self.next_char()
                self.enquanto()
                self.conteudo()
            else: self.panic(self.current_char, '(')
        elif self.current_char[2] == 'para':
            self.next_char()
            if self.current_char[2] == '(':
                self.next_char()
                self.acessovar()
                if self.current_char[2] == '=':
                    self.next_char()
                    self.expatribuicao()
                    if self.current_char[2] == ';':
                        self.next_char()
                        self.paracont()
                        self.conteudo()
                    else: self.panic(self.current_char, ';')
                else: self.panic(self.current_char, '=')
            else: self.panic(self.current_char, '(')

    #PARACONT#
    def paracont(self):
        self.expressao()
        if self.current_char[2] == ';':
            self.next_char()
            self.parafim()
        else: self.panic(self.current_char, ';')

    #PARAFIM#
    def parafim(self):
        self.exparitmetica()
        self.next_char()
        if self.current_char[2] == ')':
            self.next_char()
            if self.current_char[2] == '{':
                self.next_char()
                self.conteudo()
                if self.current_char[2] == '}':
                    self.next_char()
                else: self.panic(self.current_char, '}')
            else: self.panic(self.current_char, '{')
        else: self.panic(self.current_char, ')')

    #ENQUANTO#
    def enquanto(self):
        self.expressao()
        if self.current_char[2] == ')':
            self.next_char()
            if self.current_char[2] == '{':
                self.next_char()
                self.conteudo()
                if self.current_char[2] == '}':
                    self.next_char()
                else: self.panic(self.current_char, '}')
            else: self.panic(self.current_char, '{')
        else: self.panic(self.current_char, ')')

    #SE#
    def se(self):
        self.expressao()
        if self.current_char[2] == ')':
            self.next_char()
            if self.current_char[2] == '{':
                self.next_char()
                self.conteudo()
                if self.current_char[2] == '}':
                    self.next_char()
                    self.senao()
                else: self.panic(self.current_char, '}')
            else: self.panic(self.current_char, '{')
        else: self.panic(self.current_char, ')')
    
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
            # if self.current_char[2] in self.relacional_list:
            #     self.next_char()
            #     self.expressao()
            # elif self.current_char[2] in self.logica_list:
            #     self.next_char()
            #     self.expressao()#outra expressão que vai poder ter a continuação de uma expressao logica ou o final?
            if self.current_char[2] in self.aritmetica_list:
                self.next_char()
                self.exparitmeticab()
                self.expressaocont()
            else: self.expressaocont()
        elif self.current_char[1] == 'NRO':
            self.next_char()
            if self.current_char[2] in self.relacional_list:
                self.next_char()
                self.expressao()
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
                    self.expressao()
                elif self.current_char[2] in self.logica_list:
                    self.next_char()
                    self.expressao()
        elif self.current_char[1] == 'CAR':
            self.next_char()
            self.expressaocont()
        elif self.current_char[1] == 'CAD':
            self.next_char()
            self.expressaocont()
        #repete quase que a mesma coisa, mas para iniciar com parênteses
        elif self.current_char[2] == '(':
            self.next_char()
            if self.current_char[1] == 'IDE':
                self.acessovar()
                if self.current_char[2] == ')':
                    self.next_char()
                    self.exparitmeticacontb()
                elif self.current_char[2] in self.aritmetica_list:
                    self.next_char()
                    self.exparitmeticab()
                    self.expressaocont()
                    # if self.current_char[2] in self.relacional_list:
                    #     self.next_char()
                    #     self.expressao()
                    # elif self.cusrrent_char[2] in self.logica_list:
                    #     self.next_char()
                    #     self.expressao()#outra expressão que vai poder ter a continuação de uma expressao logica ou o final?    
                else: self.expressaocont()
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
                        self.expressao()
                    elif self.current_char[2] in self.logica_list:
                        self.next_char()
                        self.expressao()
                    else: self.panic(self.current_char)
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
                        self.expressao()
                    elif self.current_char[2] in self.logica_list:
                        self.next_char()
                        self.expressao()
                    else: self.panic(self.current_char)
                else: self.panic(self.current_char, 'Token Type: NRO')
            elif self.current_char[2] == '!':
                self.next_char()
                self.exprexc()
            elif self.current_char[2] in self.bool_list:
                self.next_char()
                self.expressaocont()
            elif self.current_char[1] == 'CAR':
                self.next_char()
                self.expressaocont()
            elif self.current_char[1] == 'CAD':
                self.next_char()
                self.exrpessaocont()
            else: self.panic(self.current_char)
        else: self.panic(self.current_char)
    
    #EXPREXC#
    def exprexc(self):
        if self.current_char[2] == '(':
            self.next_char()
            self.expressao
            self.next_char()
            if self.current_char[2] == ')':
                self.expressaocont()
            else: self.panic(self.current_char, ')')
        elif self.current_char[2] in self.bool_list:
            self.next_char()
            self.expressaocont()
        elif self.current_char[1] == 'IDE': 
            self.acessovar()
            self.expressaocont()
        else: self.panic(self.current_char)
    
    #EXPRESSAOCONT#
    def expressaocont(self):
        if self.current_char[2] in self.logica_list:
            self.next_char()
            self.expressao()
        elif self.current_char[2] in self.relacional_list:
            self.next_char()
            self.expressao()
    
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
            else: self.panic(self.current_char, 'Token Type: NRO')
        elif self.current_char[2] == '(':
            self.next_char()
            self.exparitmeticaparen()
        else: self.panic(self.current_char)
    
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
                else: self.panic(self.current_char, ')')
            else: self.panic(self.current_char, 'Token Type: NRO')
        elif self.current_char[2] == '(':
            self.next_char()
            self.exparitmeticaparen()
            self.next_char()
            if self.current_char[2] == ')':
                self.exparitmeticacontb()
            else: self.panic(self.current_char, ')')
        else: self.panic(self.current_char)
    
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
            else: self.panic(self.current_char, 'Token Type: NRO')
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
                else: self.panic(self.current_char, ')')
            else: self.panic(self.current_char, 'Token Type: NRO')
        elif self.current_char[2] == '(':
            self.next_char()
            self.exparitmeticabparen()
            self.next_char()
            if self.current_char[2] == ')':
                self.exparitmeticacontb()
            else: self.panic(self.current_char, ')')
        else: self.panic(self.current_char)
    
    #EXPARITMETICACONTB#
    def exparitmeticacontb(self):
        if self.current_char[2] in self.aritmetica_list:
            self.next_char()
            self.exparitmeticab()
        else: return None

    
    #EXPATRIBUICAO#
    def expatribuicao(self, leftVarName = 'default'):#ela só recebe após o '=' então eu tenho que passar o nome da variável para checar na tabela
        #
        # leftVarType = self.get_type(leftVarName)
        # if self.current_char[1] == 'IDE':
        #     rightVarType = self.get_type(str(self.current_char[2]))
        #     if leftVarType != rightVarType:
        #         self.smt_err(self.current_char[2], 'Atribuição de valores diferentes')
        # print(leftVarName)
        # if self.current_char[1] == 'IDE':
        #     for i in range(len(symTable)):
        #         sym = symTable[i]
        #         if leftVarName == sym['name']:
        #             varType = sym['type']
        #             print(varType)
        # if self.current_char[1] == 'IDE':
        #     leftVarType = self.get_type(leftVarName)
        #     rightVarType = self.get_type(self.current_char[2])
        #     print(leftVarType)
        #     print(rightVarType)
        #

        #
        leftVarType = self.get_type(leftVarName)
        rightVarType = self.get_type(self.current_char[2])
        ##
        if self.current_char[1] == 'IDE':
            #
            auxChar = self.current_char
            ##
            self.acessovar()
            if self.current_char[2] in self.aritmetica_add_list:#se o tipo da direita for um IDE ++/-- a esquerda só pode ser real ou inteiro
                self.next_char()
                if self.current_char[2] != ';':
                    self.panic(self.current_char, ';')
                else:
                    #
                    if leftVarType != None:
                        if rightVarType != None:
                            if rightVarType == 'inteiro' or rightVarType == 'real':
                                if leftVarType == rightVarType:
                                    None
                                else: self.smt_err(auxChar, 'Assigned variable must be of the same type')
                            else: self.smt_err(auxChar, 'Invalid operation. Variable must be an \'Inteiro\' or a \'Real\'')
                        else: self.smt_err(auxChar, 'Varibale not declared')
                    ##
            elif self.current_char[2] in self.aritmetica_list:#se a direita for uma expressão aritmética a esquerda só pode ser real ou inteiro
                self.next_char()
                #
                auxLen = len(self.pars_res)
                ##
                self.exparitmeticab()
                self.next_char()
                if self.current_char[2] != ';':
                    self.panic(self.current_char, ';')
                #
                else:
                    if len(self.pars_res) == auxLen:
                        if leftVarType != None:
                            if rightVarType != None:
                                if rightVarType == 'inteiro' or rightVarType == 'real':
                                    if leftVarType == rightVarType:
                                        None
                                    else: self.smt_err(auxChar, 'Assigned variable must be of the same type')
                                else: self.smt_err(auxChar, 'Invalid operation. Variable must be an \'Inteiro\' or a \'Real\'')
                            else: self.smt_err(auxChar, 'Variable not declared')
                ##
            elif self.current_char[2] == '(':#qual tipo que pode ser se for um a()?
                self.next_char()
                self.paran()
                self.next_char()
                if self.current_char[2] != ';':
                    self.panic(self.current_char, ';')
            elif self.current_char[2] == ';':#se o lado direito for apenas um IDE, então o lado esquerdo pode ser de qualquer tipo, eles só tem que ser iguais
                if leftVarType != None:
                    if rightVarType != None:
                        if rightVarType != leftVarType:
                            self.smt_err(auxChar, 'Assigned variable must be of the same type')
                    else: self.smt_err(auxChar, 'Variable not declared')
                return None
            else: self.panic(self.current_char, ';')
        elif self.current_char[1] == 'NRO':
            self.next_char()
            if self.current_char[2] in self.aritmetica_add_list:
                self.next_char()
                if self.current_char[2] != ';':
                    self.panic(self.current_char, ';')
            elif self.current_char[2] in self.aritmetica_list:
                self.next_char()
                self.exparitmeticab()#depois de acabar expb ele termina no próximo character?
                self.next_char()
                if self.current_char[2] != ';':
                    self.panic(self.current_char, ';')
        elif self.current_char[2] == '-':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.next_char()
                self.exparitmeticacont()
                self.next_char()
                if self.current_char[2] != ';':
                    self.panic(self.current_char, ';')
        elif self.current_char[2] == '(':
            self.next_char()
            self.exparitmeticaparen()
            self.next_char()
            if self.current_char[2] != ';':
                self.panic(self.current_char, ';')
        elif self.current_char[2] in self.bool_list:
            self.next_char()
            if self.current_char[2] != ';':
                self.panic(self.current_char, ';')

    #VALOR#
    def valor(self):
        if self.current_char[1] == 'IDE':
            self.next_char()
            if self.current_char[2] == '(':#chamadafuncao()
                self.next_char()
                self.paran()
            else: self.prev_char(); self.expressao()
        elif self.current_char[2] == 'vazio':
            self.next_char()
        else: self.expressao()

    #PARAN#
    def paran(self):
        if self.current_char[2] == ')':
            return None
        else: self.parancont()
    
    #PARACONT#
    def parancont(self):
        self.valor()
        self.paranfim()

    #PARANFIM#
    def paranfim(self):
        if self.current_char[2] == ')':
            self.next_char()
        elif self.current_char[2] == ',':
            self.next_char()
            self.parancont()
        else: self.panic(self.current_char)

    #SE#
    # def se(self):
    #     print('hi')
    #     if self.current_char[2] in self.bool_list:
    #         self.next_char()
    #         if self.current_char[2] == ')':
    #             self.next_char()
    #             if self.current_char[2] == '{':
    #                 self.next_char()
    #                 self.conteudo()
    #                 self.next_char()
    #                 if self.current_char[2] == '}':
    #                     self.next_char()
    #                     self.senao()
    #                 else: self.panic(self.current_char[0], ';')
    #             else: self.panic(self.current_char[0], ';')
    #         else: self.prev_char(); self.seexpressao()
    #     elif self.current_char[1] == 'IDE':
    #         self.next_char()
    #         if self.current_char[2] == ')':
    #             self.next_char()
    #             if self.current_char[2] == '{':
    #                 self.next_char()
    #                 self.conteudo()
    #                 self.next_char()
    #                 if self.current_char[2] == '}':
    #                     self.next_char()
    #                     self.senao()
    #                 else: self.panic(self.current_char[0], ';')
    #             else: self.panic(self.current_char[0], ';')
    #         else: self.prev_char(); self.seexpressao()
    #     else: self.seexpressao()
    
    #SEEXPRESSAO#
    def seexpressao(self):
        self.expressao()
        if self.current_char[2] == ')':
            self.next_char()
            if self.current_char[2] == '{':
                self.next_char()
                self.conteudo()
                self.next_char()
                if self.current_char[2] == '}':
                    self.next_char()
                    self.senao()
                else: self.panic(self.current_char, '}')
            else: self.panic(self.current_char, '{')
        else: self.panic(self.current_char, ')')

    #SENAO#
    def senao(self):
        if self.current_char[2] == 'senao':
            self.next_char()
            if self.current_char[2] == '{':
                self.next_char()
                self.conteudo()
                if self.current_char[2] == '}':
                    self.next_char()
                else: self.panic(self.current_char, '}')
            else: self.panic(self.current_char, '{')
        else: return None

    ##VARIAVEIS##
    def variaveis(self):
        if self.current_char[2] == '{':
            self.next_char()
            self.var()
        else: self.panic(self.current_char, '}')

    ##VAR##
    def var(self):
        #
        auxLen = len(self.pars_res)
        type = self.current_char[2]
        sym = dict(type = self.current_char[2])#eu guardo o nome e o tipo do identificador para depois, se não houver nenhum erro sintático na declaração adicionar aquele identificador a tabela de símbolos(linha 805)
        ##
        self.tipo()
        self.next_char()
        #
        sym["name"] = self.current_char[2]; sym['scope'] = self.scope; sym['line'] = self.current_char[0]; sym['rule'] = 'VAR'
        ##
        self.ide()
        #
        if len(self.pars_res) == auxLen:# se no final de ter lido a variável e não teve erro nenhum eu coloco o identificador na tabela de símbolos
            symTable.append(sym)
        ##
        self.next_char()
        self.varcont(type)

    ##VARCONT##
    def varcont(self, type = 'default'):
        if self.current_char[2] == ',' or self.current_char[2] == ';':#isso permite a produção de só um ','
            self.varfinal(type)
        else:
            self.varinit()
            #self.next_char()
            self.varfinal(type)

    ##VARFINAL##
    def varfinal(self, type = 'default'):
        if self.current_char[2] == ',':
            self.next_char()
            self.varalt(type)
        elif self.current_char[2] == ';':
            self.next_char()
            self.varfim()

    ##VARALT##
    def varalt(self, type = 'default'):#eu tenho que voltar a chamar var para o caso do registro?
        #
        auxLen = len(self.pars_res)
        ##
        self.ide()
        #
        if len(self.pars_res) == auxLen:#uma ideia, se não for colocar símbolo errado na tabela de símbolos e checar o valor de pars-res antes e comparar depois para ver se é o mesmo, o que significa que não houv erro.
            sym = dict(name = self.current_char[2], type = type, scope = self.scope, line = str(self.current_char[0]), rule = 'VAR')
            symTable.append(sym)
        ##
        self.next_char()
        self.varcont(type)

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
        else: self.panic(self.current_char, '{')

    ##CONST##
    def const(self):
        self.tipo()
        self.next_char()
        self.ide()
        self.next_char()
        self.varinit()
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
        else: self.panic(self.current_char)

    #IDE#
    def ide(self):
        if self.current_char[1] != 'IDE':
            self.panic(self.current_char, 'Token Type: IDE')

    #VARINIT#
    def varinit(self):
        if self.current_char[2] == '=':
            self.next_char()
            self.valor()
            if self.current_char[2] != ',':
                if self.current_char[2] == ';':
                    return None
                else: self.panic(self.current_char, ';')
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
                    else: self.panic(self.current_char)
                else: self.panic(self.current_char, ']')
            else: self.panic(self.current_char, 'Token Type: NRO')
        else: self.panic(self.current_char)
    
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
                        else: self.panic(self.current_char, ';')
                else: self.panic(self.current_char, ']')
            else: self.panic(self.current_char, 'Token Type: NRO')
        else: self.panic(self.current_char, '{')

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
                    else: self.panic(self.current_char, '{')
                else: self.panic(self.current_char, ',')
            else: self.panic(self.current_char, '{')
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
                                            else: self.panic(self.current_char, ';')
                                        else: self.panic(self.current_char, '{')
                                    else: self.panic(self.current_char, ',')
                                else: self.panic(self.current_char, '{')
                            else: self.panic(self.current_char, ',')
                        else: self.panic(self.current_char, '{')
                    else: self.panic(self.current_char, '=')
                else: self.panic(self.current_char, ']')
            else: self.panic(self.current_char, 'Token Type: NRO')
        else: self.panic(self.current_char, '{')

    ##VETOR##
    def vetor(self):
        self.valor()
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
        else: self.panic(self.current_char, '(')
    
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
                self.panic(self.current_char, ';')
            else: self.next_char()
        else: self.panic(self.current_char)

    def escreva(self):
        if self.current_char[2] == '(':
            self.next_char()
            self.escont()
        else: self.panic(self.current_char, '(')

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
        else: self.panic(self.current_char)
    
    def esfim(self):
        if self.current_char[2] == ',':
            self.next_char()
            self.escont()
        elif self.current_char[2] == ')':
            self.next_char()
            if self.current_char[2] != ';':
                self.panic(self.current_char, ';')
            else: self.next_char()#se o último character for realmente o ';' então o escreva acabou e eu passo para o próximo character a ser analisado
        else: self.panic(self.current_char)

    def retorno(self):
        self.valor()
        if self.current_char[2] != ";":
            self.panic(self.current_char, ';')

    def bool(self):
        if self.current_char[2] != 'verdadeiro' and self.current_char[2] != 'falso':
            self.panic(self.current_char, 'Token Type: BOOL')
    
    
    #ACESSOVAR#
    def acessovar(self):
        if self.current_char[1] == 'IDE':
            self.next_char()
            self.acessovarcont()
        else: self.panic(self.current_char, 'Token Type: IDE')
    
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
                else: self.panic(self.current_char, ']')
            else: self.panic(self.current_char, 'Token Type: NRO')
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
                else: self.panic(self.current_char, ']')
            else: self.panic(self.current_char, 'Token Type: NRO')
        else: return None
    
    #ACESSOVARCONTC#
    def acessovarcontc(self):
        if self.current_char[2] == '[':
            self.next_char()
            if self.current_char[1] == 'NRO':
                self.next_char()
                if self.current_char[2] == ']':
                    self.next_char()
                else: self.panic(self.current_char, ']')
            else: self.panic(self.current_char, 'Token Type: NRO')
        else: return None

    def erro(self, error):
        self.pars_res.append(error)
        #print("I wasn't supposed to be here!")
    
    # def panic(self, error_line, stop_char, debug = 'normal'):
    #     self.counter += 1
    #     error_message = 'Syntax Error on line: ' + str(error_line) + '; debug: ' + debug
    #     self.pars_res.append(error_message)
    #     while self.current_char[2] != stop_char:
    #         if self.next_char():#next char retorna True caso ele chegue ao final do array, caso contrário ele simplesmente itera e retorna None
    #             break

    def get_type(self, varName):
        for i in range(len(symTable)):
            sym = symTable[i]
            if varName == sym['name']:
                return sym['type']
        return None
    
    def panic(self, error_char, expected_char = ''):
        self.counter += 1
        stop_char = [';', '}']
        if expected_char != '':
            error_message = 'Syntax Error: (' + 'Expected: \'' + expected_char + '\' Found: \'' + str(error_char[2]) + '\', line: ' + str(error_char[0]) + ')'
            self.pars_res.append(error_message)
        elif expected_char == '':
            error_message = 'Syntax Error: ' + 'invalid syntax(' + str(error_char[2]) + ', line: ' + str(error_char[0]) + ')'
            self.pars_res.append(error_message)
        while self.current_char[2] not in stop_char:
            if self.next_char():#next char retorna True caso ele chegue ao final do array, caso contrário ele simplesmente itera e retorna None
                break
    
    def smt_err(self, errorChar, errMessage = ' INVALID TYPE/DECLARATION '):
        errorMessage = 'Semantic Error: ' + errMessage + '\'' + errorChar + '\''
        self.sm_res.append(errorMessage)


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
            