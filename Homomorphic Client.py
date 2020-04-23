import random
from phe import paillier
import socket
import pickle
from time import perf_counter


def recieve_messages(s, number_of_messages=2,headersize=10, buffersize=10):
    '''Receives i message from s socket'''
    received_messeges_list = list()
    full_msg = b''
    new_msg = True
    i =0
    while i < number_of_messages:
        while True:

            if not new_msg:
                if(len(full_msg)<=msglen-buffersize):
                    msg = s.recv(buffersize)
                else:
                    msg = s.recv(msglen+headersize-len(full_msg))
            if new_msg:
                msg = s.recv(buffersize)
                #print("new msg len:",msg[:headersize])
                msglen = int(msg[:headersize])
                new_msg = False


            # print(f"full message length: {msglen}")

            full_msg += msg

            # print(len(full_msg))

            if len(full_msg)-headersize == msglen:
                #print("full msg recvd")
                #print(full_msg[headersize:])
                received_messeges_list.append(full_msg[headersize:])
                new_msg = True
                full_msg = b""
                i += 1
                break
    return received_messeges_list


def text_printer(textfile , private_key):
    print(' User view of text file: ')
    for i in textfile:
        print(i , '-', end ="")
        for j in textfile[i]:
            print(chr(private_key.decrypt(j)%127), end ="")
        print()

def generate_messagelist(myfile,mymessage, mylist, myline, myindex, insertion = False):
    start = perf_counter()
    # need to check if the user is placing something out of range
    lineExist = False
    indexExist = False
    if myline in myfile:
        lineExist = True
        if myindex <len(myfile[myline]) and not insertion:
            indexExist = True
    # encrypting letter by letter of the message
    for i in mymessage:
        indexExist = False
        if lineExist:
            if myindex <len(myTextFile[myline]) and not insertion:
                indexExist = True
        if lineExist and indexExist:
            current_text_code = priv_key.decrypt(myTextFile[myline][myindex])
            # take the mod of 127
            current_text_code = pow(current_text_code,1,127)
        else:
            current_text_code = 0

        if current_text_code < ord(i):
            enc1 = pub_key.encrypt(ord(i)-current_text_code)
        elif ord(i) < current_text_code:
            enc1 = pub_key.encrypt(127-current_text_code+ord(i))

        mylist.append(enc1)
        myindex += 1
    end = perf_counter()
    print(f"time to generate to message {end- start}")


'''
command suggestion 
1 - (ADD 3 4 "This is cool!") add at line 3 index 4
2 - (DEL 4) to delete line number 4. 
3 - (DEL 4 3) to delete letter at index 3 line 4
4 - (DEL 3 range 1 5) delete 1-5 indices at line 3
5 - (DEL LINES 1 5) delete lines from 1 to 5 
6 - (INSERT 3 4 "this is cool") insert the text at line 3 index 4 
7 - (BREAK 3 4 ) break text to next line from line 3 index 4 
8 - (MERGE 3 4 ) appending line 4 to line 3 

not possible to do:
    6 - (DEl WORD 3 4 ) delete the next full connected letters line 3 index 4
    server have no concept of first and last letter... he sees only encrypted things    


'''
# pailiar keys
# fixed public private key inorder to maintain multiple users
pub_key = paillier.PaillierPublicKey(n=20918476852815906259448091380878946374846487276650566350526469504543445663363006375980464912046003771545816024129058558897178268328832892428243240325758816116809718007069804705445565528216535257753269775084363475484444731252249136528364485880450590478550481470180234291919073001105225222550340248448357283825562788397193502321253284246970379855378912631159893549706516122724903022561898802098365905740512394253180872362469204594849288169219051343346465473138330721772474356841242103555961863230650369004568170457199923595396226384215744451385588202919741103547377489727484513916853945581587278621259117042875720155503)
priv_key = paillier.PaillierPrivateKey(pub_key,162127919283290269280246639840857152984376128770345534454954387379133669565107741679145929967169305139464406132985599825523199848861502543201746524624468267546392498038506850047552083639955866199445483369829668330463181515081488945700821695087346159892723880962977802436407090904918124717412651819069317958913,129024519313447275169104153407600537462382039221068317192702753912914946829212352013082322468333553709179856117334180594866864215722499143988924999907765966989822388186078117080629013865238831570980946370419757024192707126615938893709038793788497385450191520847855948616898056960620889743640241046243403128431)
# connect to the server and retrive the file first

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432
# starting time
start = perf_counter()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))
end = perf_counter()
print(f" connecting time {end-start} second" )
end_2 = perf_counter()
''''''
HEADERSIZE = 10
received_messeges_list = recieve_messages(s,1,HEADERSIZE,10)
print(f" time to recieve text file {end_2-end} second" )
print('recieve text file from the server:')
received_messeges_list = pickle.loads(received_messeges_list[0])
if received_messeges_list == "":
    print("server have a new empty file")
    myTextFile = dict()
else:
    print(received_messeges_list)
    myTextFile = received_messeges_list
    end_3 = perf_counter()
    text_printer(myTextFile,priv_key)
    print(f'decrypting file time: {end_3-end_2}')

server_off = False
# client
# the client must get the whole text file from the server each time
while True:

    encrypted_messages= list()

    print("type \"h\" for list of commands")
    while True:

        try:
            s.send(b'0')
        except:
            print("Server is off")
            server_off = True
            break
        m2 = input('#--->')
        command = m2.split()
        if m2 == "h":
            print(
                '1 - (ADD 3 4 "This is cool!") add at line 3 index 4 and modify any existing text\n'
                  '2 - (INSERT 3 4 "this is cool") insert the text at line 3 index 4\n'
                  '2 - (DEL 4) to delete line number 4. \n'
                  '3 - (DEL 4 3) to delete letter at index 3 line 4 \n'
                  '4 - (DEL 3 range 1 5) delete 1-5 indices at line 3 \n'
                  '5 - (DEL LINES 1 5) delete lines from 1 to 5\n'
                  '6 - (BREAK 3 4 ) break text to next line from line 3 index 4 \n'
                  '7 - (MERGE 3 4 ) appending line 4 to line 3 \n'
                  '8 - (text)   prints the text file \n'
                  '9 - (exit) disconnect and save the file on the \n'
                  '10 - (h)  for help'
            )
            continue
        if m2 == "exit":
            line = "exit"
            index = "exit"
            msg = [line ,index]
            msg = pickle.dumps(msg)
            msg = bytes(f"{len(msg):<{HEADERSIZE}}",'utf-8')+msg
            s.send(msg)
            print('Going off, bye...T_T')
            exit()
            break
        if m2 == 'text':
            text_printer(myTextFile,priv_key)
            continue
        try:
            if command[0].upper() == 'ADD':
                # (ADD 3 4 "This is cool!") add at line 3 index 4
                line = int(command[1])
                index = ['ADD',int(command[2])]
                if line < 0 or index[1] < 0:
                    print(line)
                    print(index[1])
                    print("negative numbers are not accepted")
                    continue
                message = command[3:]
                if(message[0][0] != "\""):
                    print('bad message, type (h) for the list of commands')
                    continue
                try:
                    first_index = m2.index("\"")
                    last_index = max(idx for idx, val in enumerate(m2) if val == '"')
                    if first_index == last_index or len(m2)>(last_index+1):
                        print('bad message, type (h) for the list of commands')
                        continue
                    full_msg = m2[int(first_index+1):int(last_index)]
                    generate_messagelist(myTextFile,full_msg,encrypted_messages,line,index[1])
                    index.append(encrypted_messages)
                    # print(index)
                    # print(full_msg)
                    print(f'adding "{full_msg}" at line {line} to index {index[1]}')
                    msg = [line,index]
                    msg = pickle.dumps(msg)
                    msg = bytes(f"{len(msg):<{HEADERSIZE}}",'utf-8')+msg
                    s.send(msg)
                    break
                except:
                    print(f'Please Enter the ADD command correctly, type (h) for the list of commands')
                    continue
            elif command[0].upper() == 'DEL':
                int1 = False
                int2 = False
                int3 = False
                int4 = False
                try:
                    int(command[1])
                    int1 = True
                except:
                    pass
                try:
                    int(command[2])
                    int2 = True
                except:
                    pass
                try:
                    int(command[3])
                    int3 = True
                except:
                    pass
                try:
                    int(command[4])
                    int4 = True
                except:
                    pass

                if int1:
                    if len(command) == 2:
                        # Delete line command ( DEL 4 )
                        line = int(command[1])
                        index = ['Delete']
                        if line < 0:
                            print("negative numbers are not accepted")
                            continue
                        if line not in myTextFile:
                            print(f"there is no line {line}")
                            continue
                        print('Deleting line ' , command[1])
                        msg = [line,index]
                        msg = pickle.dumps(msg)
                        msg = bytes(f"{len(msg):<{HEADERSIZE}}",'utf-8')+msg
                        s.send(msg)
                        break
                    elif int2:
                        # (DEL 4 3) to delete letter at index 3 line 4
                        line = int(command[1])
                        index = ['Delete',int(command[2])]
                        if line < 0 or index[1] < 0:
                            print("negative numbers are not accepted")
                            continue
                        if line not in myTextFile:
                            print(f"there is no line {line}")
                            continue
                        if index[1] >= len(myTextFile[line]):
                            print(f"there is no letter at index {index[1]}")
                            continue
                        print(f'Deleting index {index[1]} at line { line}')
                        msg = [line,index]
                        msg = pickle.dumps(msg)
                        msg = bytes(f"{len(msg):<{HEADERSIZE}}",'utf-8')+msg
                        s.send(msg)
                        break
                    elif command[2].lower() == 'range' and len(command) == 5 and int3 and int4:
                        # (DEL 3 range 1 5) delete 1-5 indexes at line 3
                        line = int(command[1])
                        index = list()
                        index.append('Delrange')
                        if line < 0 or int(command[3]) < 0 or int(command[4]) < 0:
                            print("negative numbers are not accepted")
                            continue
                        for i in range(int(command[3]), int(command[4])+1):
                            index.append(i)
                        if line not in myTextFile:
                            print(f"there is no line {line}")
                            continue
                        indexoutofbound = False
                        for i in index[1:]:
                            if i >= len(myTextFile[line]):
                                print(f"there is no letter at index {i}")
                                indexoutofbound = True
                                break
                        if indexoutofbound:
                            continue

                        print(f'Deleting range {index[0]} to {index[-1]} at line {line}')
                        msg = [line,index]
                        msg = pickle.dumps(msg)
                        msg = bytes(f"{len(msg):<{HEADERSIZE}}",'utf-8')+msg
                        s.send(msg)
                        break
                    else:
                        print('bad del command')
                elif command[1].upper() == 'LINES':
                    # (DEL LINES 1 5) delete lines from 1 to 5
                    if int2 and int3:
                        line = list()
                        index = ['LINES']
                        lineoutofbound = False
                        if int(command[2]) < 0 or int(command[3]) < 0:
                            print("negative numbers are not accepted")
                            continue
                        for i in range(int(command[2]), int(command[3])+1):
                            line.append(i)
                            if i not in myTextFile:
                                print(f'there is no line {i}')
                                lineoutofbound = True
                                break
                        if lineoutofbound:
                            continue
                        print(f'Deleting Lines from {line[0]} to {line[-1]}')
                        msg = [line,index]
                        msg = pickle.dumps(msg)
                        msg = bytes(f"{len(msg):<{HEADERSIZE}}",'utf-8')+msg
                        s.send(msg)
                        break
                    else:
                        print('bad lines deletion command')

                else:
                    print('bad del command')
            elif command[0].upper() == "INSERT":
                #(INSERT 3 4 "this is cool") insert the text at line index 4
                int1 = False
                int2 = False
                try:
                    int(command[1])
                    int1 = True
                except:
                    print("bad insert command, type (h) for help")
                    continue
                try:
                    int(command[2])
                    int2 = True
                except:
                    print("bad insert command, type (h) for help")
                    continue

                line = int(command[1])
                if line < 0 or int(command[2]) < 0:
                    print("negative numbers are not accepted")
                    continue
                index = ['INSERT',int(command[2])]
                message = command[3:]
                if(message[0][0] != "\""):
                    print('bad message, type (h) for the list of commands')
                    continue
                try:
                    first_index = m2.index("\"")
                    last_index = max(idx for idx, val in enumerate(m2) if val == '"')
                    if first_index == last_index or len(m2)>(last_index+1):
                        print('bad message, type (h) for the list of commands')
                        continue
                    full_msg = m2[int(first_index+1):int(last_index)]
                    generate_messagelist(myTextFile,full_msg,encrypted_messages,line,index[1],insertion= True)
                    index.append(encrypted_messages)
                    # print(index)
                    # print(full_msg)
                    print(f'adding "{full_msg}" at line {line} to index {index[1]}')
                    msg = [line,index]
                    msg = pickle.dumps(msg)
                    msg = bytes(f"{len(msg):<{HEADERSIZE}}",'utf-8')+msg
                    s.send(msg)
                    break
                except Exception as e:
                    print(e)
                    print(f'Please Enter the Insertion command correctly, type (h) for the list of commands')
                    continue
            elif command[0].upper() == "BREAK" or command[0].upper() == "MERGE":
                # (BREAK 3 4 ) break text to next line from line 3 index 4
                # (MERGE 3 4 ) appending line 4 to line 3
                int1 = False
                int2 = False
                try:
                    int(command[1])
                    int1 = True
                except:
                    print("bad BREAK or MERGE command, type (h) for help")
                    continue
                try:
                    int(command[2])
                    int2 = True
                except:
                    print("bad BREAK or MERGE command, type (h) for help")
                    continue

                line = int(command[1])
                index = ['BREAK',int(command[2])]
                if command[0].upper() == "MERGE":
                    index[0] = "MERGE"
                if line < 0 or index[1] < 0:
                    print("negative numbers are not accepted")
                    continue
                if line not in myTextFile:
                    print(f"there is no line {line}")
                    continue
                if index[1] not in myTextFile and command[0].upper() == "MERGE":
                    print(f"there is no line {line}")
                    continue
                if index[1] >= len(myTextFile[line]) and command[0].upper() == "BREAK" :
                    print(f"there is no letter at index {index[1]}")
                    continue
                msg = [line,index]
                msg = pickle.dumps(msg)
                msg = bytes(f"{len(msg):<{HEADERSIZE}}",'utf-8')+msg
                s.send(msg)
                break

            else:
                print('none existing command')
        except Exception as e:
            print(e)
            print('wrong command check help for the correct command')
    start = perf_counter()
    # so now each command will change the " line " variable
    # and the index will have what to do at index[0]
    # for add simply add
    # for del
    # if length is 1 = del line
    # if length is 2 = del index
    # if length greater than 2 then del range in indexes
    # for del word
    # knowing from index[1] delete the word
    if server_off:
        break
    received_messeges_list = recieve_messages(s,1,HEADERSIZE,10)
    myTextFile = pickle.loads(received_messeges_list[0])
    text_printer(myTextFile,priv_key)
    end = perf_counter()
    print(f"time to recieve and decrypt the file {end - start}")
