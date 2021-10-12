###
# RUN
###
from typing import Counter
import os
import sys


def run(text):
    lexer = Lexer(text)
    tokens, errors = lexer.make_tokens()

    if len(errors) == 0:
        errors = ['SUCESSO!']

    return tokens, errors

###
# CONSTANTS
###
DIGITS = '0123456789'
LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
#unicode de cada linha da tabela
opAritmeticos = [42, 43, 45, 47]
delimitadores = [91, 93, 123, 125, 40, 41, 59, 44, 46]
opLogicos = [38, 124, 33]
opRelacionais = [60, 61, 62]
delComentario = [37]
reserved_words = ["algoritmo", "variaveis", "constantes", "registro",
"funcao", "retorno", "vazio", "se", "senao", "enquanto",
"para", "leia", "escreva", "inteiro", "real", "booleano", "char",
"cadeia", "verdadeiro", "falso"]
simboloNaoIncluso = [34, 39]
contraBarraValido = [92, 39]

###
# ERRORS
###
#class Error:
#    def __init__(self, pos_start, pos_end, error_name, details):
#        self.pos_start = pos_start
#        self.pos_end = pos_end
#        self.error_name = error_name
#        self.details = details
#    
#    def as_string(self):
#        result = f'{self.error_name}: {self.details}'
#       return result

#class IllegalCharError(Error):
#    def __init__(self, details):
#        super().__init__('illegal Character', details)

###
# TOKEN SIGLAS
###   
PRE = 'PRE'
IDE = 'IDE'
NRO = 'NRO'
DEL = 'DEL'
REL = 'REL'
LOG = 'LOG'
ART = 'ART'
SIB = 'SIB'
SII = 'SII'
CMF = 'CMF'
NMF = 'NMF'
CAR = 'CAR'
CaMF = 'CaMF'
CoMF = 'CoMF'
OpMF = 'OpMF'
CAD = 'CAD'

''' def verificaLetra(caracter):
    caracter = ord(caracter)
    if(caracter >= 65 and caracter <= 90):
        return True
    elif(caracter >= 97 and caracter <= 122):
        return True
    return False '''

class Token:
    def __init__(self, type_, value = None):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        if self.value: return f'{self.type} {self.value}'
        return f'{self.type}'

class Position:#mantem o valor da linha e coluna
    def __init__(self, indx, ln, col):
        self.indx = indx
        self.ln = ln
        self.col = col
    
    def advance(self, current_char):
        self.indx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0
        return self
    
    def retreat(self, current_char):
        if self.col != 0:
            self.indx -= 1 
            self.col -= 1
        return self
    
    def copy(self):
        return Position(self.indx, self.ln, self.col)


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = Position(-1, 1, -1)
        self.current_char = None
        self.next_char()
    
    def next_char(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.indx] if self.pos.indx < len(self.text) else None
    
    def prev_char(self):
        self.pos.retreat(self.current_char)
        self.current_char = self.text[self.pos.indx] 

    def make_tokens(self):# função que vai iniciar a máquina de estados no estado q0
        tokens = []
        errors = []
        while self.current_char != None:
            self.q0(tokens, errors)
        return tokens, errors   
    
    def q0(self, tokens, errors):#q0 vai ser o node inicial da máquina e vai chamar os outros nodes. 
                         #Cada node vai corresponder a uma classificação na tabela de expressão regular (ex. Operadores aritméticos é o node q2)
        #                         
        # ESPAÇO OU TAB
        #
        if self.current_char in ' \t\n':
            self.next_char()
        #
        # IDENTIFICADORES
        #
        elif self.current_char in LETTERS:
            tokens.append(self.pos.ln)
            tk_out_str = self.identificador()
            tokens.append(tk_out_str)
        #
        # DIGITOS
        #
        elif self.current_char in DIGITS:
            tok_list, er_list = self.q1()
            if tok_list != None:
                tokens.append(self.pos.ln)
                tokens.append(tok_list)
            elif er_list != None:
                errors.append(self.pos.ln)
                errors.append(er_list)
        #
        # OPERADORES ARITMÉTICOS
        #
        elif ord(self.current_char) in opAritmeticos:
            tokens.append(self.pos.ln) 
            tokens.append(self.q2())
            self.next_char()
        
        elif ord(self.current_char) in delimitadores:
            tok_list, er_list, begin_line = self.q3()
            if tok_list != None:
                if begin_line != None:
                    tokens.append(begin_line)
                    tokens.append(tok_list)
                elif begin_line == None:
                    tokens.append(self.pos.ln)
                    tokens.append(tok_list)
            elif er_list != None:
                if begin_line != None:
                    errors.append(begin_line)
                    errors.append(er_list)
                elif begin_line == None:
                    errors.append(self.pos.ln)
                    errors.append(er_list)
            self.next_char()
        
        elif ord(self.current_char) in delComentario:
            tok_list, er_list = self.q4('')
            if tok_list != None:
                tokens.append(self.pos.ln)
                tokens.append(tok_list)
            elif er_list != None:
                errors.append(self.pos.ln)
                errors.append(er_list)
            self.next_char()
            
        elif ord(self.current_char) in opLogicos:
            tok_list, er_list = self.q5()
            if tok_list != None:
                tokens.append(self.pos.ln)
                tokens.append(tok_list)
            elif er_list != None:
                errors.append(self.pos.ln)
                errors.append(er_list)
            self.next_char()
        
        elif ord(self.current_char) in opRelacionais:
            tokens.append(self.pos.ln)
            tokens.append(self.operadorRelacional())
            self.next_char()

        elif self.current_char == '"':
            tok_list, er_list = self.cadeiaCaracteres('')
            if tok_list != None:
                tokens.append(self.pos.ln)
                tokens.append(tok_list)
            elif er_list != None:
                errors.append(self.pos.ln)
                errors.append(er_list)
            self.next_char()
        
        elif self.current_char == "'":
            tok_list, er_list = self.caractere()
            if tok_list != None:
                tokens.append(self.pos.ln)
                tokens.append(tok_list)
            elif er_list != None:
                errors.append(self.pos.ln)
                errors.append(er_list)
            self.next_char()

        elif ord(self.current_char) >= 32 and ord(self.current_char) <= 255:
            errors.append(self.pos.ln)
            errors.append(self.simbolos())
            self.next_char()


        
        else:
            errors.append(self.pos.ln)
            errors.append(self.q14())
            self.next_char()
            
        #return tokens, None

    def q1(self):# Vai definir os tokens de digitos, ints e pontos flutuantes
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: return self.num_loop_i(num_str)
                dot_count +=1
                num_str += '.'
            else: 
                num_str += self.current_char
            self.next_char()

        if self.current_char != None and self.is_valid_end_of_num():# se ele não for letra nem número nem ponto
            if dot_count == 0:
                return Token(NRO, num_str), None
            elif dot_count == 1:
                if num_str[-1] == '.':
                    return None, Token(NMF, num_str)
                else:
                    return Token(NRO, num_str), None

        if self.current_char == None:
            if dot_count == 1:
                return None, Token(NMF, num_str)
            elif dot_count == 0:
                return Token(NRO, num_str), None
        
        else:
            return self.num_loop_i(num_str)

    def num_loop_i(self, num_str):
        while self.current_char != None and not self.is_valid_end_of_num() and self.current_char != '\n':
            num_str += self.current_char
            self.next_char()
        return None, Token(NMF, num_str)
        
        

    def q2(self):#vai definir os operadores aritméticos
        if self.current_char == '+':
            token_str = self.current_char
            self.next_char()
            if self.current_char == '+':
                token_str += self.current_char
                return Token(ART, token_str)
            else:
                self.prev_char()
                return Token(ART, token_str)
        elif self.current_char == '-':
            token_str = self.current_char
            self.next_char()
            if self.current_char == '-':
                token_str += self.current_char
                return Token(ART, token_str)
            else:
                self.prev_char()
                return Token(ART, token_str)
        elif self.current_char == '/':
            return Token(ART, self.current_char)
        elif self.current_char == '*':
            return Token(ART, self.current_char)
        else:
            return self.q14()
        
    def q3(self):#vai definir os delimitadores
        if self.current_char == ';':
            return Token(DEL, self.current_char), None, None
        elif self.current_char == ',':
            return Token(DEL, self.current_char), None, None
        elif self.current_char == '.':
            return Token(DEL, self.current_char), None, None
        elif self.current_char == '[':
            return Token(DEL, self.current_char), None, None
        elif self.current_char == ']':
           return Token(DEL, self.current_char), None, None
        elif self.current_char == '(':
            return Token(DEL, self.current_char), None, None
        elif self.current_char   == ')':
            return Token(DEL, self.current_char), None, None
        elif self.current_char == '{':
            comment_str = self.current_char
            self.next_char()
            if self.current_char == '#':
                return self.q4(comment_str)
            self.prev_char()
            return Token(DEL, self.current_char), None, None
        elif self.current_char == '}':
            return Token(DEL, self.current_char), None, None
    
    def q4(self, comment_str):
        if self.current_char ==  '%':
            while self.current_char != '\n' and self.pos.indx != len(self.text):#enquanto ele não chegar ao final da linha e consequentemente do comentário, 
                self.next_char()
            ret_str = 'comentario de linha'
            return ret_str, None                                            #ou no final do arquivo, caso seja um comentário no final do arquivo
                                                                                #ele vai continuar lendo os caracteres até chegar o fim do comentário
        elif self.current_char == '#':
            begin_line = self.pos.ln
            comment_str += self.current_char
            return self.comment_loop_i(comment_str, begin_line)

    def comment_loop_i(self, comment_str, begin_line):
       while self.current_char != None:
           self.next_char()
           if self.current_char != None and self.current_char == "#":
               comment_str += self.current_char
               return self.comment_loop_ii(comment_str, begin_line)
           elif self.current_char != None:
                if self.current_char == '\n':
                    comment_str += ' '
                else:
                    comment_str += self.current_char
       return None, Token(CoMF, comment_str), begin_line
    
    def comment_loop_ii(self, comment_str, begin_line):
        self.next_char()
        if self.current_char != None and self.current_char == "}":
            ret_str = 'comentario de bloco'
            return ret_str, None, begin_line
        elif self.current_char != None: 
            if self.current_char == '\n':
                comment_str += ' '
            else:
                comment_str += self.current_char
        return self.comment_loop_i(comment_str, begin_line)

    def q5(self):
        if self.current_char ==  '&':
            lex = self.current_char
            self.next_char()
            if self.current_char == '&':
               lex += self.current_char
               return Token(LOG, lex), None
            self.prev_char()
            return None, Token(OpMF, lex)

        elif self.current_char ==  '|':
            lex = self.current_char
            self.next_char()
            if self.current_char == '|':
               lex += self.current_char
               return Token(LOG, lex), None
            self.prev_char()
            return None, Token(OpMF, lex)

        elif self.current_char == '!':
            lex = self.current_char
            self.next_char()
            if self.current_char == '=':
                lex += self.current_char
                return Token(REL, lex), None
            self.prev_char()
            return Token(LOG, lex), None

        return None, None



    def identificador(self):
        lex = self.current_char
        
        self.next_char()
        while self.current_char in LETTERS or self.current_char in DIGITS or self.current_char == '_':
            lex += self.current_char
            self.next_char()
            if(self.current_char == None):
                break


        if(lex in reserved_words):
            return Token(PRE, lex)
        return Token(IDE, lex)

    def operadorRelacional(self):
        if self.current_char ==  '=':
            lex = self.current_char
            self.next_char()
            if self.current_char == '=':
               lex += self.current_char
               return Token(REL, lex)
            self.prev_char()
            return Token(REL, self.current_char)

        elif self.current_char ==  '>':
            lex = self.current_char
            self.next_char()
            if self.current_char == '=':
               lex += self.current_char
               return Token(REL, lex)
            self.prev_char()
            return Token(REL, self.current_char)

        elif self.current_char == '<':
            lex = self.current_char
            self.next_char()
            if self.current_char == '=':
               lex += self.current_char
               return Token(REL, lex)
            self.prev_char()
            return Token(REL, self.current_char)

    def cadeiaCaracteres(self, lex):
        lex += self.current_char
        self.next_char()
        while self.current_char != None and self.current_char != '\n':
            if self.current_char == '"': return self.cadCarIV(lex)
            elif self.current_char == '\\': return self.cadCarII(lex)
            else:
                lex += self.current_char
                self.next_char()
        return None, Token(CMF, lex)
    
    def cadCarII(self, lex):
        lex += self.current_char
        self.next_char()
        if self.current_char != None and self.current_char != '\n':
            if self.current_char == '"': return self.cadCarIII(lex)
            else: return self.cadeiaCaracteres(lex)
        return None, Token(CMF, lex)

    def cadCarIII(self, lex):
        lex += self.current_char
        self.next_char()
        while self.current_char != None and self.current_char != '\n':
            if self.current_char == '\\': return self.cadCarII(lex)
            elif self.current_char == '"': return self.cadCarIV(lex)
            else:
                lex += self.current_char
                self.next_char()
        return None, Token(CMF, lex)

    def cadCarIV(self, lex):
        lex += self.current_char
        erro = False
        for i in range(len(lex)):
            if not self.is_valid_cad_car_input(lex[i]): erro = True
        if erro == True:
            return None, Token(CMF, lex)
        else:
            return Token(CAD, lex), None

    def caractere(self):
        lex = self.current_char
        count = 0
        erro = False
        is_slash = False

        while True:
            self.next_char()
            if self.current_char == "\n" or self.current_char == None:
                count = 4
                break
            else:
                lex += self.current_char
                count += 1
                
            if(self.current_char == "'" and lex[-2] != "\\" or self.current_char ==  "'" and lex[-2] == '\\' and lex[-3] == '\\'):
                is_slash = True
                break

            elif(not self.is_valid_car()):
                erro = True
                count = 4
            # print(lex)
        if count <= 2:
            if erro == True:
                return None, Token(CaMF, lex)
            else:
                return Token(CAR, lex), None
        elif count <=3:
            if is_slash == True:
                if ord(lex[-2]) in contraBarraValido:
                    return Token(CAR, lex), None
                else: return None, Token(CaMF, lex)
            else:
                return None, Token(CaMF, lex)
        else: return None, Token(CaMF, lex)


    def simbolos(self):
        if self.isSimbol():
            return Token(SIB, self.current_char)
        else:
            return Token(SII, self.current_char)
        
    def q14(self):#Erro de símbolo inválido
        return Token(SII, self.current_char)

    def isSimbol(self):
        if ord(self.current_char) >= 32 and ord(self.current_char) <= 126 and ord(self.current_char) not in simboloNaoIncluso:
            return True
        return False

    def is_valid_end_of_num(self):
        if self.current_char not in LETTERS and self.current_char not in DIGITS and self.current_char != ".":
            return True
        return False

    def is_valid_cad_car(self):
        if ord(self.current_char) >= 32 and ord(self.current_char) <= 126 and ord(self.current_char) != 39:
            return True
        return False
    
    def is_valid_cad_car_input(self, i):
        if ord(i) >= 32 and ord(i) <= 126 and ord(i) != 39:
            return True
        return False

    def is_valid_car(self):
        if ord(self.current_char) >= 32 and ord(self.current_char) <= 126 and ord(self.current_char) != 34:
            return True
        return False

    def isOperator(self):
        if ord(self.current_char) in opAritmeticos or ord(self.current_char) in opLogicos or ord(self.current_char) in opRelacionais:
            return True
        return False