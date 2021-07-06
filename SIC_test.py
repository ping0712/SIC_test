import sys
import math
import re

# pass 1
def optab(command,op=[],mn=[]):
    output = 'null'
    for i in range(len(mn)):
        if command == mn[i]:
            output = op[i]
    if command == 'START':
        output = 'start'
    if command == 'END':
        output = 'end'
    if command == 'WORD' or command == 'BYTE' or command == 'RESW' or command == 'RESB':
        output = 'pesudo'
    return output

def hex_to_dec(data) :
    num = 0
    for i in range(len(data)) :
        if data[i] == 'A' :
            num = num + 10 * pow(16,(len(data) - 1 - i))
        elif data[i] == 'B' :
            num = num + 11 * pow(16,(len(data) - 1 - i))
        elif data[i] == 'C' :
            num = num + 12 * pow(16,(len(data) - 1 - i))
        elif data[i] == 'D' :
            num = num + 13 * pow(16,(len(data) - 1 - i))
        elif data[i] == 'E' :
            num = num + 14 * pow(16,(len(data) - 1 - i))
        elif data[i] == 'F' :
            num = num + 15 * pow(16,(len(data) - 1 - i))
        else :
            num = num + int(data[i]) * pow(16,(len(data) - 1 - i))
    return num

def dec_to_hex(data) :
    num = len(hex(data))
    result = hex(data)[2:num]
    return result.upper()

def comment(scan=[]):
    # 註解
    delete = 0
    dot = 0
    for i in range(len(scan)):
        if scan[i][0:1] == '.':
            dot = i
            delete = len(range(i, len(scan)))
            break
    for i in range(delete):
        del scan[dot]

def indexad(scan=[]):
    # 索引定址
    index = 0
    check = 0
    for i in range(len(scan)):
        if scan[i][len(scan[i])-1:len(scan[i])] == ',' :
            check = 1
            index = i + 1
            scan[i] = scan[i] + scan[i+1]
        elif scan[i][0:1] == ',' :
            check = 2
            index = i
            scan[i] = scan[i-1] + scan[i]
    if check == 1 :
        del scan[index]
    if check == 2 :
        del scan[index-1]
    return

def writelocctr(loc) :
    result = ""
    if len(loc) < 4 :
        result = str(0) * (4 - len(loc)) + loc
    else :
        result = loc
    return result

def findindex(data) :
    result = 0
    for i in range(len(data)) :
        if data[i] == ',' :
            result = i + 1
    return result

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    return False

def checkhex(data) :
    result = True
    for i in range(len(data)) :
        if is_number(data[i]) == False :
            if ord(data[i]) < 65 or ord(data[i]) > 70 :
                result = False
    return result

error_line = [] # 記錄錯誤行
error_content = [] # 記錄錯誤內容
loc = ""
symtab = [[],[]] # symbol tabel
end = False
start = ''
isstart = False
opcode = []
testprog = open('(test)SIC.asm','r', encoding='utf8')
progline = len(open('(test)SIC.asm','r', encoding='utf8').readlines())
middle = open('middle.txt','w', encoding='utf8')
warring_line = []
warring_content = []
pattern = '(.*)'

f = open('opCode.txt', 'r')
opf = f.readlines()
mn = []
op = []
for i in range(len(opf)):
    mn.append(opf[i].split()[0])
    op.append(opf[i].split()[1])

count = 0
while count <= progline :
    count += 1
    dataline = testprog.readline()
    tmp = ''
    bytestart = 0
    byteend = 0
    byte = 0
    
    for i in range(len(dataline)) :
        if dataline[i] == "'" :
            byte += 1
            if byte == 1 :
                bytestart = i
            elif byte == 2 :
                byteend = i
    
    data = dataline.split()
    if byte > 0 :
        tmp = re.findall(pattern,dataline[bytestart-1:byteend+1])
        data[2] = tmp[0]
        if len(data) > 3 :
            del data[3]

    comment(data)
    if len(data) > 0 : 

        if end == False :
            indexad(data)
            if len(data) == 3:
                if isstart == False and data[1] == 'START' :
                    if len(data[0]) > 6 :
                        error_line.append(count)
                        error_content.append('symbol名稱過長 ')
                    else :
                        isstart = True
                        loc = data[2]
                        start = data[0]
                        middle.write(str(count)+' '+str(writelocctr(loc))+' '+str(data[0])+' '+str(data[1])+' '+str(data[2])+' '+optab(data[1])+"\n")
                elif isstart == True and data[1] != 'START' :
                    if data[1] == 'END' :
                        error_line.append(count)
                        error_content.append('END 沒有symbol')
                        middle.write(str(count)+' '+str(writelocctr(loc))+' '+str(data[0])+' '+str(data[1])+' '+str(data[2])+' '+optab(data[1])+"\n")

                    elif optab(data[1],op,mn) == 'null' :
                        error_line.append(count)
                        error_content.append('mnemonic error')

                    elif optab(data[1],op,mn) == 'pesudo':
                        if len(data[0]) > 6 :
                            error_line.append(count)
                            error_content.append('symbol名稱過長 ')   
                        else :
                            if len(symtab[0]) > 0 :
                                if data[0] in symtab[0] :
                                    error_line.append(count)
                                    error_content.append('redefined symbol')
                            if data[0] in mn :
                                error_line.append(count)
                                error_content.append('symbol 不能等於 mnemnoic')
                            if data[1] == 'WORD' :
                                symtab[0].append(data[0])
                                symtab[1].append(loc)
                                middle.write(str(count)+' '+str(writelocctr(loc))+' '+str(data[0])+' '+str(data[1])+' '+str(data[2])+' '+str(optab(data[1],op,mn))+"\n")
                                loc = dec_to_hex(hex_to_dec(loc) + 3)      
                            elif data[1] == 'BYTE' :
                                if data[2][0:2] == "C'" :
                                    symtab[0].append(data[0])
                                    symtab[1].append(loc)
                                    middle.write(str(count)+' '+str(writelocctr(loc))+' '+str(data[0])+' '+str(data[1])+' '+str(data[2])+' '+str(optab(data[1],op,mn))+"\n")
                                    loc = dec_to_hex(hex_to_dec(loc) + len(data[2][2:len(data[2])-1]))
                                elif data[2][0:2] == "X'" :
                                    if len(data[2][2:len(data[2])-1])%2 != 0 :
                                        error_line.append(count)
                                        error_content.append('X內只能偶數')
                                    else :
                                        if checkhex(data[2][2:len(data[2])-1]) == False :
                                            error_line.append(count)
                                            error_content.append('X內只能是16進位')
                                        else :
                                            symtab[0].append(data[0])
                                            symtab[1].append(loc)
                                            middle.write(str(count)+' '+str(writelocctr(loc))+' '+str(data[0])+' '+str(data[1])+' '+str(data[2])+' '+str(optab(data[1],op,mn))+"\n")
                                            loc = dec_to_hex(hex_to_dec(loc) + 1*int(len(data[2][2:len(data[2])-1])/2))
                                else :
                                    error_line.append(count)
                                    error_content.append('BYTE 只能用C或X')
                            elif data[1] == 'RESB' :
                                symtab[0].append(data[0])
                                symtab[1].append(loc)
                                middle.write(str(count)+' '+str(writelocctr(loc))+' '+str(data[0])+' '+str(data[1])+' '+str(data[2])+' '+str(optab(data[1],op,mn))+"\n")
                                loc = dec_to_hex(hex_to_dec(loc) + int(data[2]))
                            else :
                                symtab[0].append(data[0])
                                symtab[1].append(loc)
                                middle.write(str(count)+' '+str(writelocctr(loc))+' '+str(data[0])+' '+str(data[1])+' '+str(data[2])+' '+str(optab(data[1],op,mn))+"\n")
                                loc = dec_to_hex(hex_to_dec(loc) + int(data[2]) * 3)
                    else :
                        if len(data[0]) > 6 :
                            error_line.append(count)
                            error_content.append('symbol名稱過長')   
                        else :
                            if len(symtab[0]) > 0 :
                                if data[0] in symtab[0] :
                                    error_line.append(count)
                                    error_content.append('redefined symbol')
                            if data[0] in mn :
                                error_line.append(count)
                                error_content.append('symbol 不能等於 mnemnoic')
                            if data[1] == 'RSUB' :
                                error_line.append(count)
                                error_content.append('RSUB不能有operand')
                            symtab[0].append(data[0])
                            symtab[1].append(loc)
                            middle.write(str(count)+' '+str(writelocctr(loc))+' '+str(data[0])+' '+str(data[1])+' '+str(data[2])+' '+str(optab(data[1],op,mn))+"\n")
                            loc = dec_to_hex(hex_to_dec(loc) + 3)
                elif isstart == False and data[1] != 'START' :
                    warring_line.append(count)
                    warring_content.append('還沒start哦 ')
                else :
                    error_line.append(count)
                    error_content.append('已經start了哦')

            elif len(data) == 2:
                if isstart == True : 
                    if optab(data[0],op,mn) == 'null' and data[1] != 'RSUB':
                        if optab(data[1],op,mn) != 'null' :
                            error_line.append(count)
                            error_content.append('沒有operand')
                        else :
                            error_line.append(count)
                            error_content.append('mnemonic error')
                    elif data[0] == 'END' :
                        end = True
                        middle.write(str(count)+' '+str(writelocctr(loc))+' '+'none'+' '+str(data[0])+' '+str(data[1])+' '+str(optab(data[0],op,mn))+"\n")
                    elif data[0] == 'RSUB' :
                        error_line.append(count)
                        error_content.append('RSUB不能有operand')
                    elif data[1] == 'RSUB' :
                        if len(data[0]) > 6 :
                            error_line.append(count)
                            error_content.append('symbol名稱過長')   
                        else :
                            if len(symtab[0]) > 0 :
                                if data[0] in symtab[0] :
                                    error_line.append(count)
                                    error_content.append('redefined symbol')
                            if data[0] in mn :
                                error_line.append(count)
                                error_content.append('symbol 不能等於 mnemnoic')
                            symtab[0].append(data[0])
                            symtab[1].append(loc)
                            middle.write(str(count)+' '+str(writelocctr(loc))+' '+str(data[0])+' '+str(data[1])+' '+'none'+' '+str(optab(data[1],op,mn))+"\n")
                            loc = dec_to_hex(hex_to_dec(loc) + 3)
                    else :
                        middle.write(str(count)+' '+str(writelocctr(loc))+' '+'none'+' '+str(data[0])+' '+str(data[1])+' '+str(optab(data[0],op,mn))+"\n")
                        loc = dec_to_hex(hex_to_dec(loc) + 3)
                else :
                    error_line.append(count)
                    error_content.append('還沒start哦')
            
            elif len(data) == 1 :
                if isstart == True :
                    if data[0] == 'RSUB' :
                        middle.write(str(count)+' '+str(writelocctr(loc))+' '+'none'+' '+str(data[0])+' '+'none'+' '+str(optab(data[0],op,mn))+"\n")
                        loc = dec_to_hex(hex_to_dec(loc) + 3)
                    else :
                        if optab(data[0],op,mn) != 'null' :
                            error_line.append(count)
                            error_content.append('沒有operand')
                        else :
                            error_line.append(count)
                            error_content.append('mnemonic error')
                else :
                    warring_line.append(count)
                    warring_content.append('還沒start哦')
            else :
                error_line.append(count)
                error_content.append('非3欄式')
        else :
            warring_line.append(count)
            warring_content.append('程式已經結束了哦')

if len(warring_line) > 0 :
    for i in range(len(warring_content)) :
        print('Warring: line ' + str(warring_line[i]) + ' ' + warring_content[i])

# pass 2
def writeloc(loc) : # 6位(不足前面補0)
    result = ''
    if len(loc) < 6 :
        result = str(0) * (6 - len(loc)) + loc
    else :
        result = loc
    return result

def writesym(sym) : # 6位(不足後面補空白)
    result = ""
    if len(sym) < 6 :
        result = sym + ' ' * (6 - len(sym))
    else :
        result = sym
    return result

def countloclen(num,op = [],loc = []) : # 程式長度
    loclen = ''
    for i in range(num) :
        if op[i] == 'start' :
            loclen = loc[i]
        elif op[i] == 'end' :
            loclen = writeloc(dec_to_hex(hex_to_dec(loc[i])-hex_to_dec(loclen)))
    return loclen

def returnindex(data) :
    result = data
    if findindex(data) == 0 :
        result = data
    else :
        if checkindex(data) == True :
            result = data[0:len(data)-2]
        else :
            result = data[0:findindex(data)-1]
    return result

def checkindex(data) :
    result = True
    if findindex(data) != 0 :
        if data[findindex(data):len(data)] != 'X' :
            result = False
    return result

def write_hore_rec(num,loclen,op = [],sym = [],loc = [],operand= [],symtab = [],symloc = []) : # 開頭結束
    h_rec = 'H'
    e_rec = 'E'
    for i in range(num) :
        if op[i] == 'start' :
            h_rec = h_rec + writesym(sym[i]) + writeloc(loc[i]) + loclen
        if op[i] == 'end' :
            startad = ''
            for j in range(len(symtab)) :
                if operand[i] == symtab[j] :
                    startad = writeloc(symloc[j])
            e_rec = e_rec + startad
    hore_rec = [h_rec,e_rec]
    return hore_rec

def write_t_rec(num,op=[],mn=[],loc=[],operand=[],symtab=[],symloc=[]) :
    t_arr = []
    t_tmp = ''
    t_start = ''
    for i in range(num) :
        if op[i] != 'pesudo' :
            if op[i] == 'start' :
                t_tmp = ''
            elif op[i] == 'end' :
                lentt = hex(int(len(t_tmp)/2))
                lent = lentt[2:len(lentt)].upper()
                if len(lent) < 2 :
                    lent = '0' + lent
                t_ins = 'T'+t_start+lent+t_tmp
                t_arr.append(t_ins)
                t_tmp = ''
            else :
                if t_tmp == '' :
                    t_start = writeloc(loc[i])
                if len(t_tmp) == 60 or (len(t_tmp) + len(writeloc(loc[i]))) > 60:
                    lentt = hex(int(len(t_tmp)/2))
                    lent = lentt[2:len(lentt)].upper()
                    if len(lent) < 2 :
                        lent = '0' + lent
                    t_ins = 'T'+t_start+lent+t_tmp
                    t_arr.append(t_ins)
                    t_tmp = ''
                    t_start = writeloc(loc[i])
                    
                if op[i] == '4C' :
                    t_tmp = t_tmp + op[i] + '0000'
                else :
                    t_tmp = t_tmp + op[i] + dataloc(operand[i],symtab,symloc)
        else :
            if  mn[i] == 'RESB' or mn[i] == 'RESW' :
                if t_tmp != '' :
                    lentt = hex(int(len(t_tmp)/2))
                    lent = lentt[2:len(lentt)].upper()
                    if len(lent) < 2 :
                        lent = '0' + lent
                    t_ins = 'T'+t_start+lent+t_tmp
                    t_arr.append(t_ins)
                    t_tmp = ''
                    t_start = ''
            elif mn[i] == 'BYTE' :
                if operand[i][0:1] == 'X' :
                    t_tmp = t_tmp + operand[i][2:len(operand[i])-1]
                else :
                    tmp = operand[i][2:len(operand[i])-1]
                    tmp2 = ''
                    for i in range(len(tmp)) :
                        tmp2 = tmp2 + hex(ord(tmp[i]))[2:len(hex(ord(tmp[i])))]
                    t_tmp = t_tmp + tmp2.upper()
            elif mn[i] == 'WORD' :
                operand[i] = int(operand[i])
                tmp = hex(operand[i])[2:len(hex(operand[i]))]
                for i in range(6) :
                    if len(tmp) < 6 :
                        tmp = '0' + tmp
                t_tmp = t_tmp + tmp
        
    return t_arr

def dataloc(data,symtab = [],symloc = []) :
    result = ''
    for i in range(len(symtab)) :
        if returnindex(data) == symtab[i] :
            if data[len(data)-2:len(data)] == ',X' :
                result = dec_to_hex(hex_to_dec(symloc[i])+hex_to_dec('8000'))
            else :
                result = writelocctr(symloc[i])
    return result

def undefinedsym(num,line=[],operand=[],op=[],symtab=[],error_line=[],error_content=[]) :
    for i in range(num) :
        if operand[i] != 'none' and op[i] != 'start' and op[i] != 'pesudo' :
            check = False
            if returnindex(operand[i]) in symtab :
                check = True
            if check == False :
                error_line.append(line[i])
                error_content.append('undefined symbol')

middle = open('middle.txt','r',encoding='utf8')
object_program = open('object_program.txt','w',encoding='utf8')

progline = len(open('middle.txt','r',encoding='utf8').readlines())
data = [[] for i in range(6)]
end = False
num = 0 # 可執行的行數
count = 0
while count <= progline : 
    count += 1
    if end != True :
        midline = middle.readline()
        bytestart = 0
        byteend = 0
        byte = 0
        bytestart = 0
        byteend = 0
        byte = 0
        tmp = ''
        
        for i in range(len(midline)) :
            if midline[i] == "'" :
                byte += 1
                if byte == 1 :
                    bytestart = i
                elif byte == 2 :
                    byteend = i
        mid = midline.split()

        if byte > 0 :
            tmp = re.findall(pattern,midline[bytestart-1:byteend+1])
            mid[4] = tmp[0]
            if len(mid) > 6 :
                del mid[5]
        if mid[5] == 'end' :
            end = True
        for i in range(len(mid)) :
            data[i].append(mid[i])
        num += 1

for i in range(num) :
    if checkindex(data[4][i]) == False :
        error_line.append(data[0][i])
        error_content.append('index 錯誤')
undefinedsym(num,data[0],data[4],data[5],symtab[0],error_line,error_content)
if len(error_line) > 0:
    for i in range(len(error_line)) :
        print('Error: line '+str(error_line[i])+' '+str(error_content[i]))
else :
    loclen = countloclen(num,data[5],data[1])
    h_rec = write_hore_rec(num,loclen,data[5],data[2],data[1],data[4],symtab[0],symtab[1])[0]
    e_rec = write_hore_rec(num,loclen,data[5],data[2],data[1],data[4],symtab[0],symtab[1])[1]
    t_rec = write_t_rec(num,data[5],data[3],data[1],data[4],symtab[0],symtab[1])
    print(h_rec)
    object_program.write(h_rec+'\n')
    for i in range(len(t_rec)) :
        print(t_rec[i])
        object_program.write(t_rec[i]+'\n')
    print(e_rec)
    object_program.write(e_rec+'\n')

