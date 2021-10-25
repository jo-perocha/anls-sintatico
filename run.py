import anl_lex
import anl_sint
import os.path

def read_write_file(file_value):
    with open('input\entrada' + str(file_value) + '.txt') as file:
                #data = file.readlines()
                text = file.read() #in case it can read token by token with this methods

    result_lex, errors = anl_lex.run(text)
    result_sint = anl_sint.run(result_lex)#ainda não tem tratamento de erros então por enquanto roda somente o que deu certo
                                        #depois quando tiver o resultado do sintático fazer a mesma coisa do run_lexer para imprimir o resultado no arquivo.
    print(result_sint)

read_write_file(1)