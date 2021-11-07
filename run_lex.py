import anl_lex
import anl_sint
import os.path

def read_write_file(file_value):
    with open('D:\\HUB\\UEFS\\desk-clone\\anls-sintatico\\input\\entrada' + str(file_value) + '.txt') as file:
                #data = file.readlines()
                text = file.read() #in case it can read token by token with this methods

    result, errors = anl_lex.run(text)
    result_syntax = anl_lex.run(result)

    er_size = len(errors)
    re_synt_size = len(result_syntax)

    test = result[1]
    test = str(test)
    test = test[4:]
    print(test)

    open('anls-sintatico\output\saida' + str(file_value) + '.txt', 'w').close()#limpa o arquivo de saída para o novo output
    count = -1
    # for i in range(re_size):
    #    count = count + 1
    #    if count == 2:#quebra de linha pra cada token
    #        count = 0
    #        with open('anls-sintatico\output\saida' + str(file_value) + '.txt', 'a') as file:
    #            file.write('\n')
    #    if count != 2:
    #        with open('anls-sintatico\output\saida' + str(file_value) + '.txt', 'a') as file:
    #            file.write(str(result[i]))
    #            file.write(' ')

    # with open('anls-sintatico\output\saida' + str(file_value) + '.txt', 'a') as file:
    #    file.write('\n')

    for i in range(er_size):
       count = count + 1
       if count == 2:#quebra de linha pra cada token
           count = 0
           with open('anls-sintatico\output\saida' + str(file_value) + '.txt', 'a') as file:
               file.write('\n')
       if count != 2:
           with open('anls-sintatico\output\saida' + str(file_value) + '.txt', 'a') as file:
               file.write(str(errors[i]))
               file.write(' ')
    with open('anls-sintatico\output\saida' + str(file_value) + '.txt', 'a') as file: file.write('\n')
    for i in range(re_synt_size):
        with open('anls-sintatico\output\saida' + str(file_value) + '.txt', 'a') as file:
            file.write(str(result_syntax[i]))

input_list = os.listdir('D:\\HUB\\UEFS\\desk-clone\\anls-sintatico\\input')
output_list = os.listdir('D:\\HUB\\UEFS\\desk-clone\\anls-sintatico\\output')

for j in range(len(output_list)):
    i = j + 1
    os.remove('D:\\HUB\\UEFS\\desk-clone\\anls-sintatico\\output\\saida' + str(i) + '.txt')
for j in range(len(input_list)):
    i = j + 1
    read_write_file(i)