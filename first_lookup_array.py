#a ideia é criar uma função que vai ler a gramática, e colocar todos os não terminais e seus conjuntos first em um array
with open('anls-sintatico\input\entrada' + str(file_value) + '.txt') as file:
                #data = file.readlines()
                text = file.read()