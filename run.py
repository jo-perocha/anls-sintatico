import anl_lex
import anl_sint
import os.path

def read_write_file(file_value):
    with open('input\entrada' + str(file_value) + '.txt') as file:
                #data = file.readlines()
                text = file.read() #in case it can read token by token with this methods
    open('output\saida' + str(file_value) + '.txt', 'w').close()
    result_lex, errors = anl_lex.run(text)
    result_sint, result_sm = anl_sint.run(result_lex)

    err_size = len(errors)
    result_size = len(result_sint)
    result_sm_size = len(result_sm)
    count = -1
    if errors[0] != 'SUCESSO!':
        for i in range(err_size):
            count = count + 1
            if count == 2:#quebra de linha pra cada token
                count = 0
                with open('output\saida' + str(file_value) + '.txt', 'a') as file:
                    file.write('\n')
            if count != 2:
                with open('output\saida' + str(file_value) + '.txt', 'a') as file:
                    file.write(str(errors[i]))
                    file.write(' ')
        with open('output\saida' + str(file_value) + '.txt', 'a') as file:
            file.write('\n' + '\n')
        
    for i in range(result_size):
        with open('output\saida' + str(file_value) + '.txt', 'a') as file:
                file.write(result_sint[i])
    with open('output\saida' + str(file_value) + '.txt', 'a') as file:
            file.write('\n' + '\n')
    for i in range(result_sm_size):
        with open('output\saida' + str(file_value) + '.txt', 'a') as file:
                file.write(result_sm[i])
    
    print(result_sint)

read_write_file(1)
input_list = os.listdir('input')
output_list = os.listdir('output')

for j in range(len(output_list)):
    i = j + 1
    os.remove('output\saida' + str(i) + '.txt')
for j in range(len(input_list)):
    i = j + 1
    read_write_file(i)
