def main(message):
    summ = message
    if summ != 'check ':
        summ = summ[summ.index('k') + 1:]

        while ' ' in summ:  # delete spaces
            smth = summ.index(' ')
            summ = summ[0:smth]+summ[smth+1:len(summ)]
        if summ == '' or summ[0] == '=':  # preparing a string
            mistake = True 
        if not('=0' in summ):
            summ += '=0'

        mistake, coeff, unknown = stringToList(summ)

        if mistake or coeff[-1] == 0:
            return 'Вы неправильно ввели уравнение'

        # the main part
        table, korni, coeff_line, divs = resutCalc(coeff)

        # output part
        output = ''
        for i in range(len(korni)):  # usual answers to x
            if korni[i] > 0:
                output = output + '(' + unknown + str(-korni[i]) +  ')'
            else:
                output = output + '('+ unknown + '+' + str(-korni[i]) + ')'

        if table[len(table) - 1][len(table[len(table) - 1]) - 1] != 0 and korni == []:
            return 'Нет решения через схему Горнера'  # if Discriminant havent got square root

        elif (len(table[0]) >= 4):
            output += '('
            for i in range(1, len(table[0])):
                if table[coeff_line][i] > 0:
                    output += '+'
                if i == len(table[0]) - 1:
                    output += str(table[coeff_line][i]) + ')'
                elif i == len(table[0]) - 2:
                    output += str(table[coeff_line][i]) + unknown
                else:
                    output += str(table[coeff_line][i]) + unknown + '^' + str(len(table[0]) - i - 1)

        else: # last number 
            if table[divs][2] > 0:
                output = output + '(' + unknown + '+' + str(table[divs][2]) +  ')'
            else:
                output = output + '('+ unknown + str(table[divs][2]) + ')'

        if output != '':
            output = output + '=0'
            return output


def stringToList(summ):
    coeff, i, unknown, mistake = [0], 0, '', False
    while summ[0] != '=':  # putting coefficients on the list 
        if "^" in summ:   # find ^ index which will say where the number ends
            b = summ.index('^')
            i = b 
            if not(summ[b + 1].isdigit()):  # user has written not number
                mistake = True
                break

        while summ[i] != '+' and summ[i] != '-' and summ[i] != '=':  # find end of x's end index
            i += 1 
            if i == len(summ) - 1:
                mistake = True
                break

        if coeff == [0] and '^' in summ:  # if this is the first cycle add all numbers
                for _ in range(int(summ[b + 1]) + 1):
                        coeff.append(0)
                unknown = summ[b - 1]

        if "^" in summ:
            if summ[b + 1: i].isdigit() :
                if summ[0: b - 1] == '' or summ[0: b - 1] == '+':
                    coeff[len(coeff) - int(summ[b + 1: i]) - 1] = 1
                elif summ[0: b - 1] == '-':
                    coeff[len(coeff) - int(summ[b + 1: i]) - 1] = -1
                elif summ[: b - 1].isdigit() or summ[1: b - 1].isdigit():
                    coeff[len(coeff) - int(summ[b + 1: i]) - 1] = int(summ[0: b - 1])
                else:
                    mistake = True
                    break
            else:
                mistake = True
                break 

        elif unknown in summ:
            if summ[0: i - 1] == '' or summ[0:i - 1] == '+':
                coeff[len(coeff) - 2] = 1
            elif summ[0:i - 1] == '-':
                coeff[len(coeff) - 2] = -1
            elif summ[0: i - 1].isdigit() or summ[1: i - 1].isdigit():
                coeff[len(coeff) - 2] = int(summ[0: i - 1])
            else:
                mistake = True
                break

        elif summ[: summ.index('=')].isdigit() or summ[1: summ.index('=')].isdigit():
            coeff[len(coeff) - 1] = int(summ[0: summ.index('=')])  # the last num is left
        else:
            mistake = True
            break
        summ = summ [i:]
        i = 1
        
    return mistake, coeff, unknown


def resutCalc(coeff):
    divs, ko = 0, 1
    coeff_line = 0

    table, korni = [coeff], []  # finding divs of last num and making a table
    last_coeff = abs(table[0][- 1])
    for i in range(1, last_coeff + 1):
        if last_coeff % i == 0:
            table.append([i])
            table.append([-i])


    while (len(table[0]) > 3) and (divs < len(table) - 1):
        while table[divs][ko] != 0 and divs < len(table)-1:
            divs += 1
            for ko in range(1, len(table[0])):
                if ko == 1:
                    table[divs].append(table[coeff_line][1])
                else:
                    table[divs].append(table[divs][0] * table[divs][ko - 1] + table[coeff_line][ko])

        if divs >= len(table) - 1:
            break
        korni.append(table[divs][0])

        for ko in range (1, len(table[0])):
            table[divs - 1][ko] = table[divs][ko]

        table[0] = table[0][:-1]
        table[divs] = table[divs][:1]
        divs -=1
        ko, coeff_line = 1, divs
    
    return table, korni, coeff_line, divs
