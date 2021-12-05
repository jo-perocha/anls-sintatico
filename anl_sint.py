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
        if self.pos < (len(self.lexeme_matrix)):
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
            self.scope = 'algoritmo'
            self.algoritmo()
        elif self.current_char[2] == 'funcao':
            self.next_char()
            self.funcao()
            self.start()
        elif self.current_char[2] == 'variaveis':
            self.next_char()
            self.scope = 'global'
            self.variaveis()
            self.a()
        elif self.current_char[2] == 'constantes':
            self.next_char()
            self.scope = 'global'
            isConstant = True
            self.constantes(isConstant)
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
            self.scope = 'algoritmo'
            self.algoritmo()
        elif self.current_char[2] == 'funcao':
            self.next_char()
            self.funcao()
            self.a()
        elif self.current_char[2] == 'constantes':
            self.next_char()
            self.scope = 'global'
            isConstant = True
            self.constantes(isConstant)
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
            self.scope = 'algoritmo'
            self.algoritmo()
        elif self.current_char[2] == 'funcao':
            self.next_char()
            self.funcao()
            self.b()
        elif self.current_char[2] == 'variaveis':
            self.next_char()
            self.scope = 'global'
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
        #
        auxLen = len(self.pars_res)
        funcDeclarationError = False#This variable is going to be the aux to determine if there was any syntax error during the function declaration
        ##
        if self.current_char[2] == '[':#what is this?
            self.tipocont()
            if self.current_char[1] == 'IDE':
                self.next_char()
                self.funcaoinit() 
        #
        auxType = self.current_char[2]
        ##
        self.tipo()
        self.next_char()
        self.tipocont()
        if self.current_char[1] == 'IDE':
            #
            self.scope = self.current_char[2]#set the scope with the name of the function
            funcName = self.current_char[2]
            ##
            self.next_char()
            if len(self.pars_res) == auxLen:
                funcDeclarationError = False
            else: funcDeclarationError == True
            self.funcaoinit(funcName, auxType, funcDeclarationError)#I'm going to pass to the funcaoinit the name of the function so I can put it in the table later in funcaoinit 
    
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
    def funcaoinit(self, funcName, retrnType, funcDeclarationError):
        #
        sym = dict(name = funcName, type = 'function', returnType = retrnType, paramList = None, scope = self.scope, rule = 'FUNC', line = self.current_char[0])
        ##
        if self.current_char[2] == '(':
            self.next_char()
            self.paraninit(sym, funcDeclarationError)#I have to pass sym to continue updating the symbol table with this function's informations
            if self.current_char[2] == '{':
                self.next_char()
                self.scope = sym['name']
                returnType = self.conteudo()#in case there is a return conteudo() returns the return type so that I can check the semantic of returns in functions
                #Here, at the end of the function I need to remove the variables that belong to this function
                #
                self.remove_function_variables(sym['paramList'])
                if returnType != None:
                    if returnType != sym['returnType']:
                        self.smt_err(self.current_char[0], returnType, ' Return does not match the function\'s return type')
                else: self.smt_err(self.current_char[0], sym['name'], ' No return statement in the function')
                ##
                if self.current_char[2] == '}':
                    self.next_char()#talvez esse não deva estar aqui
                else: self.panic(self.current_char, '}')
            else: self.panic(self.current_char, '}')
        else: self.panic(self.current_char, ')')
    
    #PARANINIT#
    def paraninit(self, sym, funcDeclarationError):
        #
        if sym['paramList'] == None:
            params = []
        else: 
            params = sym['paramList']
        auxLen = len(self.pars_res)
        ##
        self.tipo()
        #
        if len(self.pars_res) == auxLen:
            params.append(self.current_char[2])
        else: funcDeclarationError == True
        ##
        self.next_char()
        if self.current_char[1] == 'IDE':
            #
            if len(self.pars_res) == auxLen:
                #If the name of the param variable I'm declaring is already on the symbol table I cannot declare the function with this paramater
                if self.is_declared_all_scopes(self.current_char[2]):
                    params.pop()#and I have to remove the type of the parameter that was added in line 271
                    self.smt_err(self.current_char[0], self.current_char[2], ' Two variables cannot be declared with the same name')
                    funcDeclarationError == True
                else:
                    params.append(self.current_char[2])
                    sym['paramList'] = params
            else: funcDeclarationError == True
            ##
            self.next_char()
            self.paraninitcont(sym, funcDeclarationError)
        else: self.panic(self.current_char, 'Token Type: IDE')

    #PARANINITCONT#
    def paraninitcont(self, sym, funcDeclarationError):
        if self.current_char[2] == ',':
            self.next_char()
            self.paraninit(sym, funcDeclarationError)
        elif self.current_char[2] == ')':
            #
            #I think I can check all the function problems here before appending it to the table. And I have to check if there isn't any error before appending it to the table either way
            if funcDeclarationError == False:
                # if self.is_declared_type(funcName, 'function') == 1:#found the objtect declared as a function
                # sym = self.get_item(funcName)
                # if auxType == sym['returntype']:#if both functions have the same return type
                #     funcDeclarationError == False
                # else: funcDeclarationError == True
                # elif self.is_declared_type(funcName, 'function') == -1:#found the object declared, but not as a function
                #     funcDeclarationError == True
                #     self.smt_err(self.current_char[0], funcName, ' Functions and variables cannot be declared with the same name ')
                # else:#didn't find any object declared with that name
                #     funcDeclarationError == False
                if self.is_declared_type(sym['name'], 'function') == 1:#found the object declared as a function
                    existentFunction = self.get_item(sym['name'])#get the function that is already declared with the name to compare the return type and the parameters
                    if sym['returnType'] == existentFunction['returnType']:#if the return types are the same I compare the parameters
                        params1 = sym['paramList']
                        params2 = existentFunction['paramList']
                        if params1 == params2: self.smt_err(self.current_char[0], sym['name'], ' Two functions cannot be declared with the same name, return type and parameters')
                        else: 
                            symTable.append(sym)
                            #after I checked that the declaration of the function is all right and I added it to the symbol table, I need to add it's parameters as variables in the symbol table
                            params = sym['paramList']
                            for i in range(len(params)):
                                if i % 2 == 0:
                                    insertSym = dict(scope = sym['scope'], rule = 'VAR', line = sym['line'])
                                    insertSym['type'] = params[i]
                                else:
                                    insertSym['name'] = params[i]
                                    symTable.append(insertSym)
                    else: self.smt_err(self.current_char[0], sym['name'], ' Cannot declare two functions with the same name and different return types ')
                elif self.is_declared_type(sym['name'], 'function') == -1:#found the object, but not declared as a function
                    self.smt_err(self.current_char[0], sym['name'], ' Cannot declare a function and a variable with the same name ')
                else:#the object hasn't been declared, so I add him to the table
                    symTable.append(sym)
                    params = sym['paramList']
                    for i in range(len(params)):
                        if i % 2 == 0:
                            insertSym = dict(scope = sym['scope'], rule = 'VAR', line = sym['line'])
                            insertSym['type'] = params[i]
                        else:
                            insertSym['name'] = params[i]
                            symTable.append(insertSym)
            ##
            self.next_char()
    
    #CHAMADAFUNCAO#
    def chamadafuncao(self):
        funcName = self.current_char[2]
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
        if self.current_char[2] == 'variaveis':
            self.next_char()
            self.variaveis()
            self.conteudo()
        elif self.current_char[2] == 'constantes':
            self.next_char()
            self.constantes(True)
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
            returnType = self.retorno()
            self.next_char()
            #this is the line i'm supposed to change if something goes wrong, also no return in retorno()
            #return True
            return returnType
        elif self.current_char[2] == '}':#quer dizer que o conteudo foi 'conteudo{}' NAO, NAO QUER DIZER NAO, pra ver se foi conteudo{}, eu posso checar se o char anterior é {. Do contrário é uma produção vazia 

            return False
        elif self.current_char[2] == ';':
            if not self.next_char():#é pra ver se tem next char?
                return None
            else: self.prev_char()
        elif self.current_char[1] == 'IDE':#Here three things can happen. I can make an atribution for a variable, a constant or I can call a function
            #
            auxName = self.current_char[2]
            varType = self.get_type(self.current_char[2], self.scope)
            valueRule = self.get_rule(self.current_char[2], self.scope)
            checkDeclaration = self.is_declared(auxName, self.scope)
            ##
            self.acessovar()
            if self.current_char[2] == '=':
                #
                if valueRule == 'CONST':
                    self.smt_err(self.current_char[0], auxName, ' The value of constants cannot be changed')
                else:
                    if checkDeclaration == -1: self.smt_err(self.current_char[0], auxName, ' Variable out of scope')
                    elif checkDeclaration == 0: self.smt_err(self.current_char[0], auxName, ' Variable not declared')
                ##
                self.next_char()
                self.expatribuicao(auxName)#termina checando se o último character é o ';' então eu tenho que dar um next_char para chamar conteúdo 
                self.next_char()
                self.conteudo()
            elif self.current_char[2] == '(':
                if varType == None: self.smt_err(self.current_char[0],auxName , ' Function not declared')
                self.next_char()
                self.paran(auxName)
                self.conteudo()
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
        leftVarType = self.get_type(leftVarName, self.scope)
        rightVarType = self.get_type(self.current_char[2], self.scope)
        ##
        if self.current_char[1] == 'IDE':
            #
            auxChar = self.current_char[2]
            auxLine = self.current_char[0]
            declarationCheck = self.is_declared(auxChar, self.scope)# here we have the result of the declaration of the variable on the right
            ##
            self.acessovar()
            if self.current_char[2] in self.aritmetica_add_list:#se o tipo da direita for um IDE ++/-- a esquerda só pode ser real ou inteiro
                self.next_char()
                if self.current_char[2] != ';':
                    self.panic(self.current_char, ';')
                else:
                    #
                    # if leftVarType != None:
                    #     if rightVarType != None:
                    #         if rightVarType == 'inteiro' or rightVarType == 'real':
                    #             if leftVarType == rightVarType:
                    #                 None
                    #             else: self.smt_err(auxLine, auxChar, '', leftVarType)
                    #         else: self.smt_err(auxLine, auxChar, 'Invalid operation. Variable must be an \'Inteiro\' or a \'Real\'')
                    #     else: self.smt_err(auxLine, auxChar, 'Varibale not declared')
                    if leftVarType != None:
                        if declarationCheck == 1:
                            if rightVarType == 'inteiro' or rightVarType == 'real':
                                if leftVarType == rightVarType:
                                    None
                                else: self.smt_err(auxLine, auxChar, '', leftVarType)
                            else: self.smt_err(auxLine, auxChar, 'Invalid operation. Variable must be an \'Inteiro\' or a \'Real\'')
                        elif declarationCheck == -1: self.smt_err(auxLine, auxChar, ' Variable out of scope ')
                        elif declarationCheck == 0: self.smt_err(auxLine, auxChar, ' Varibale not declared ')
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
                            if declarationCheck == 1:
                                if rightVarType == 'inteiro' or rightVarType == 'real':
                                    if leftVarType == rightVarType:
                                        None
                                    else: self.smt_err(auxLine, auxChar, '', leftVarType)
                                else: self.smt_err(auxLine, auxChar, 'Invalid operation. Variable must be an \'Inteiro\' or a \'Real\'')
                            elif declarationCheck == -1: self.smt_err(auxLine, auxChar, ' Variable out of scope ')
                            elif declarationCheck == 0: self.smt_err(auxLine, auxChar, ' Varibale not declared ')
                    ##
            elif self.current_char[2] == '(':#qual tipo que pode ser se for um a()?
                self.next_char()
                self.paran()
                self.next_char()
                if self.current_char[2] != ';':
                    self.panic(self.current_char, ';')
            elif self.current_char[2] == ';':#se o lado direito for apenas um IDE, então o lado esquerdo pode ser de qualquer tipo, eles só tem que ser iguais
                #
                if leftVarType != None:
                    if declarationCheck == 1:
                        if rightVarType != leftVarType:
                            self.smt_err(auxLine, auxChar, '', leftVarType)
                    elif declarationCheck == -1: self.smt_err(auxLine, auxChar, ' Variable out of scope ')
                    elif declarationCheck == 0: self.smt_err(auxLine, auxChar, ' Varibale not declared ')
                ##
                return None
            else: self.panic(self.current_char, ';')
        elif self.current_char[1] == 'NRO':
            #
            auxChar = self.current_char[2]
            auxLine = self.current_char[0]
            declarationCheck = self.is_declared(auxChar, self.scope)# here we have the result of the declaration of the variable on the right
            ##
            self.next_char()
            if self.current_char[2] in self.aritmetica_add_list:
                self.next_char()
                if self.current_char[2] != ';':
                    self.panic(self.current_char, ';')
                #
                else: 
                    if leftVarType != None:
                        if leftVarType != 'inteiro':
                                self.smt_err(auxLine, auxChar, '', leftVarType)
                ##
            elif self.current_char[2] in self.aritmetica_list:
                self.next_char()
                #
                auxLen = len(self.pars_res)
                ##
                self.exparitmeticab()#depois de acabar expb ele termina no próximo character?
                self.next_char()
                if self.current_char[2] != ';':
                    self.panic(self.current_char, ';')
                #
                else: 
                    if auxLen == len(self.pars_res):
                        if leftVarType != None:
                            if rightVarType != None:
                                if rightVarType != leftVarType:
                                    self.smt_err(auxLine, auxChar, '', leftVarType)
                            else: self.smt_err(auxLine, auxChar, 'Varibale not declared')
                ##
            elif self.current_char[2] == ';':#I think I had forgotten to add this one. If it assigns only a number
                if leftVarType != None:
                    if leftVarType != 'inteiro':
                        self.smt_err(auxLine, auxChar, '', leftVarType)

        elif self.current_char[2] == '-':
            self.next_char()
            if self.current_char[1] == 'NRO':
                # self.next_char()
                # self.exparitmeticacont()
                # self.next_char()
                # if self.current_char[2] != ';':
                #     self.panic(self.current_char, ';')
                #
                auxChar = self.current_char[2]
                auxLine = self.current_char[0]
                ##
                self.next_char()
                if self.current_char[2] in self.aritmetica_add_list:
                    self.next_char()
                    if self.current_char[2] != ';':
                        self.panic(self.current_char, ';')
                    #
                    else: 
                        if leftVarType != None:
                            if rightVarType != None:
                                if rightVarType != leftVarType:#como ele já é NRO, eu só preciso checar se o tipo do lado esquerdo é igual ao do direito
                                    self.smt_err(auxLine, auxChar, '', leftVarType)
                            else: self.smt_err(auxLine, auxChar, 'Varibale not declared')
                    ##
                elif self.current_char[2] in self.aritmetica_list:
                    self.next_char()
                    #
                    auxLen = len(self.pars_res)
                    ##
                    self.exparitmeticab()#depois de acabar expb ele termina no próximo character?
                    self.next_char()
                    if self.current_char[2] != ';':
                        self.panic(self.current_char, ';')
                    #
                    else: 
                        if auxLen == len(self.pars_res):
                            if rightVarType != None:
                                if rightVarType != None:
                                    if rightVarType != leftVarType:
                                        self.smt_err(auxLine, auxChar, '', leftVarType)
                                else: self.smt_err(auxLine, auxChar, 'Varibale not declared')
                    ##
                elif self.current_char[2] == ';':#I think I had forgotten to add this one. If it assigns only a number
                    #
                    if leftVarType != None:
                        if rightVarType != None:
                            if rightVarType != leftVarType:
                                self.smt_err(auxLine, auxChar, '', leftVarType)
                        else: self.smt_err(auxLine, auxChar, 'Varibale not declared')
                    ##
        elif self.current_char[2] == '(':
            self.next_char()
            self.exparitmeticaparen()
            self.next_char()
            if self.current_char[2] != ';':
                self.panic(self.current_char, ';')
        elif self.current_char[2] in self.bool_list:
            #
            auxChar = self.current_char[2]
            auxLine = self.current_char[0]
            ##
            self.next_char()
            if self.current_char[2] != ';':
                self.panic(self.current_char, ';')
            #
            else: 
                if rightVarType != leftVarType:
                    self.smt_err(auxLine, auxChar, '', leftVarType)
            ##
        #
        elif self.current_char[1] == 'CAD':
            #
            auxChar = self.current_char[2]
            auxLine = self.current_char[0]
            ##
            self.next_char()
            if self.current_char[2] != ';':
                self.panic(self.current_char, ';')
            #
            else: 
                if leftVarType != 'cadeia':
                    self.smt_err(auxLine, auxChar, '', leftVarType)
            ##
        elif self.current_char[1] == 'CAR':
            #
            auxChar = self.current_char[2]
            auxLine = self.current_char[0]
            ##
            self.next_char()
            if self.current_char[2] != ';':
                self.panic(self.current_char, ';')
            #
            else: 
                if leftVarType != 'char':
                    self.smt_err(auxLine, auxChar, '', leftVarType)
            ##
        ##
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
    def paran(self, funcName = None):
        if self.current_char[2] == ')':#if this happens it means the function was called without parameters
            return None
        else: 
            params = []
            self.parancont(params, funcName)#otherwise I have to pass the list of parameters from paran to paranfim to check with the original function
    
    #PARACONT#
    def parancont(self, params, funcName):
        #
        params.append(self.current_char[1])
        params.append(self.current_char[2])
        ##
        self.valor()
        self.paranfim(params, funcName)

    #PARANFIM#
    def paranfim(self, params, funcName):
        if self.current_char[2] == ')':
            self.next_char()
            if self.current_char[2] != ';':
                self.panic(self.current_char, ';')
            else:
                #
                resulta, resultb = self.are_parameters_equal(funcName, params)
                if resulta == 'number of parameters does not match':
                    self.smt_err(self.current_char[0], funcName, ' The number of parameters does not match the function declaration')
                elif resulta == 'parameters are not declared':
                    self.smt_err(self.current_char[0], resultb, ' Parameter(s) are not declared')
                elif resultb != None:
                    self.smt_err(self.current_char[0], funcName, ' Parameter ' + '\'' + str(resulta) + '\'' + ' is supposed to be of the type: ' + '\'' + str(resultb) + '\'')
                ##
                self.next_char()
        elif self.current_char[2] == ',':
            self.next_char()
            self.parancont(params, funcName)
        else: self.panic(self.current_char)

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
            if self.is_declared(sym['name'], self.scope) == 0:#I also need to check whether the variable has been declared or not
                symTable.append(sym)
            else: 
                self.smt_err(self.current_char[0], self.current_char[2], ' Two variables cannot be declared with the same name ')
        ##
        self.next_char()
        self.varcont(type)

    ##VARCONT##
    def varcont(self, type = 'default'):
        if self.current_char[2] == ',' or self.current_char[2] == ';':#isso permite a produção de só um ','
            self.varfinal(type)
        else:
            self.varinit(type)
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
            if self.is_declared(sym['name'], self.scope) == 0:
                symTable.append(sym)
            else:
                self.smt_err(self.current_char[0], self.current_char[2], ' Two variables cannot be declared with the same name ')
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
    def constantes(self, isConstant):
        if self.current_char[2] == '{':
            self.next_char()
            self.const(isConstant)
        else: self.panic(self.current_char, '{')

    ##CONST##
    def const(self, isConstant):
        #
        auxLen = len(self.pars_res)
        ##
        self.tipo()
        #
        auxTipo = self.current_char[2]
        ##
        self.next_char()
        self.ide()
        #
        auxName = self.current_char[2]
        ##
        self.next_char()
        self.varinit(auxTipo, isConstant)
        #
        if auxLen == len(self.pars_res):
            sym = dict(name = auxName, type = auxTipo, rule = 'CONST', scope = self.scope)
            symTable.append(sym)
        ##
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
    def varinit(self, leftVarType = None, isConstant = False):
        if self.current_char[2] == '=':
            #when I'm declaring a constant or a variable with an attribution, I need to check if both the right and left values match types. For that I can pass the type of the left
            #value as a parameter, and check with the current value being assigned.
            self.next_char()
            #
            if leftVarType != None:
                if not self.is_type_equal(leftVarType, self.current_char[1]):#I can't compare both types directly because the type TOKEN is different from the written programming language
                    auxType = self.current_char[1]
                    if auxType == 'CAR' or auxType == 'CAD' or auxType == 'NRO' or auxType == 'verdadeiro' or auxType == 'falso':
                        self.smt_err(self.current_char[0], self.current_char[2], ' Invalid type attribution')
                    else:
                        if isConstant == True: 
                            self.smt_err(self.current_char[0], self.current_char[2], ' Constants can only be declared with an explicit value. Invalid')
                        else: 
                            self.smt_err(self.current_char[0], self.current_char[2], ' Invalid type attribution')
            ##
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
            self.next_char()
        

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
        returnType = self.current_char[1]
        self.valor()
        if self.current_char[2] != ";":
            self.panic(self.current_char, ';')
        return returnType

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
    
    def remove_table(self, type, name):
        remove = []
        for i in range(len(symTable)):
            sym = symTable[i]
            if sym['name'] == name and sym['type'] == type:
                remove.append(i)#to avoid having problems from altering the list while iterating it, I'm gonna keep the indexes of the positions to remove on another list
        for i in range(len(remove)):
            symTable.pop(remove[i])

    #this functino goes through the list of the variables to be removed from the list and calls the remove functin for each variable
    def remove_function_variables(self, params):
        for i in range(len(params)):
            if i % 2 == 0:
                auxType = params[i]
            else: 
                auxName = params[i]
                self.remove_table(auxType, auxName)

    def are_parameters_equal(self, funcName, callParams):
        for i in range(len(symTable)):#search for the the funcion with the same name as the one in the function call
            sym = symTable[i]
            if sym['name'] == funcName:
                funcParams = sym['paramList']#if I find a declared function with the same name, I'm gonna get the list of parameters to compare

                # for i in range(len(funcParams)):#Here I'm just cutting the list to only have the type of the parameters on the declaration of the function, and I put that into compareParams
                #     if i % 2 == 0:
                #         compareParams.append[funcParams[i]]

                if len(callParams) != len(funcParams):#it means there are not enough, or there are too many parameters on the function call
                    return 'number of parameters does not match', None
                else:
                    for i in range(len(callParams)):#I'm going to iterate through the list of parameters
                        if i % 2 == 0:#as both lists have the type of the paremeter and then the parameter name on them, I only need to look at their types
                            paramC = callParams[i]
                            paramF = funcParams[i]
                            if paramC != 'IDE':
                                if not self.is_type_equal(paramF, paramC):#if one of them is different, then I return the ones that are different
                                    return callParams[i+1], paramF#type paramC was supposed to be paramF
                            else:#if the parameter in the function calling is an IDE, I have to search for it's type on the symbol table
                                callParamType = None
                                for j in range(len(symTable)):
                                    sym1 = symTable[j]
                                    if callParams[i+1] == sym1['name']:#as I am skipping the name of the parameters I have to add 1 to the index to get the name of the parameter I'm analysing at the moment
                                        callParamType = sym1['type']
                                        break
                                if callParamType != None:# that means I found the IDE parameter on the symTable, and have it's type to compare with the function declaration
                                    if callParamType != paramF:
                                        return callParams[i+1], paramF#callParamType was supposed to be type paramF
                                else: return 'parameters are not declared', callParams[i+1]
                    return 'parameters are equal', None
        return None, None

    
    #it returns the rule of the value, if it is a constant, a variable, registro, etc.
    def get_rule(self, varName, scope):
        for i in range(len(symTable)):
            sym = symTable[i]
            if varName == sym['name']:
                if sym['scope'] == scope or sym['scope'] == 'global':
                    return sym['rule']
    #for some reason it was not working to insert the itmes on the symbol table directly on the function. So the function retutnrs
    #the list of parameters for them to be inserted on the symbol table as variables
    def add_parameters_to_table(self, funcSym):
        params = funcSym['paramList']
        insert_table = []
        auxLen = len(params)
        for i in range(auxLen):
            # if (i%2) == 0:
            #     print(params[i])
            if (i % 2) == 0:
                sym = dict(scope = funcSym['scope'], rule = 'VAR', line = funcSym['line'])
                sym['type'] = params[i]
            else: 
                sym['name'] = params[i]
                insert_table.append(sym)
        return insert_table
                

    #it returns the type of a given variable, if the variable has been declared
    #it takes as paramater the name of the variable
    def get_type(self, varName, scope):

        for i in range(len(symTable)):
            sym = symTable[i]
            if varName == sym['name']:
                return sym['type']
        return None
    #it returns an item from the symbol table that has the same type as the one passed in the argument
    #if it finds the object you're looking for it returns it, if it finds the object but with a different type it returns -1
    #if it doesn't find it in the list it returns 0
    def is_declared_type(self, varName, varType):
        for i in range(len(symTable)):
            sym = symTable[i]
            if varName == sym['name']:
                if varType == sym['type']:
                    return 1
                return -1
        return 0

    def is_type_equal(self, leftVarType, rightVarType):
        #se o valor a direita for um IDE eu tenho que olhar o tipo dele, se não é só comparar o tipo direto do valor
        if leftVarType == 'inteiro' and rightVarType == 'NRO':
            return True
        elif leftVarType == 'cadeia' and rightVarType == 'CAD':
            return True
        elif leftVarType == 'char' and rightVarType == 'CAR':
            return True
        elif leftVarType == 'real' and rightVarType == 'NRO':
            return True
        elif leftVarType == 'booleano' and (rightVarType == 'verdadeiro' or rightVarType == 'falso'):
            return True
        

    #returns an item from the symbolTable
    def get_item(self, varName):
        for i in range(len(symTable)):
            sym = symTable[i]
            if varName == sym['name']:
                return sym
        return None

    #def is_declared_within_function

    #it check if the variable/constant/etc is declared independent of the scope
    #used to check for value declaration with the same name
    def is_declared_all_scopes(self, varName):
        for i in range(len(symTable)):
            sym = symTable[i]
            if varName == sym['name']:
                return True
        return False
    
    #tells if the variable/constant/etc is declared withing the scope, out of the scope or if it hasn't been declared at all
    #used to check the usage of variables on different scopes
    def is_declared(self, varName, scope):
        if scope != 'global':
            for i in range(len(symTable)):
                sym = symTable[i]
                if varName == sym['name']:#it means that it is in the table
                    if sym['scope'] == scope or sym['scope'] == 'global':#it means it is in the avaliable scope
                        return 1
                    else: 
                        return -1#it means that it is declared, but it is out of scope
            else: return 0#it means it is not declared
        elif scope == 'global':
            for i in range(len(symTable)):
                sym = symTable[i]
                if varName == sym['name']:#it means that it is in the table
                    if sym['scope'] == 'global':#it means it is in the avaliable scope
                        return 1
                    else: 
                        return -1#it means that it is declared, but it is out of scope
            else: return 0#it means it is not declared

    
    def panic(self, error_char, expected_char = ''):
        #self.counter += 1
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
    
    def smt_err(self, errorLine, errorChar, errMessage = ' INVALID TYPE/DECLARATION ', type = 'default'):
        if type != 'default':
            errorMessage = 'Semantic Error: ' + 'line: ' + str(errorLine) + ', Assigned value ' + '(' + errorChar + ')' + ' must be of type: ' + type 
        else:
            errorMessage = 'Semantic Error: ' + 'line: ' + str(errorLine) + ',' + errMessage + ' \'' + errorChar + '\''
        self.sm_res.append(errorMessage)