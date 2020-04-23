import random
from phe import paillier
import pickle
import socket


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
                if msg == b'0':
                    return 0
                print("new msg len:",msg[:headersize])
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

pub_key = paillier.PaillierPublicKey(n=20918476852815906259448091380878946374846487276650566350526469504543445663363006375980464912046003771545816024129058558897178268328832892428243240325758816116809718007069804705445565528216535257753269775084363475484444731252249136528364485880450590478550481470180234291919073001105225222550340248448357283825562788397193502321253284246970379855378912631159893549706516122724903022561898802098365905740512394253180872362469204594849288169219051343346465473138330721772474356841242103555961863230650369004568170457199923595396226384215744451385588202919741103547377489727484513916853945581587278621259117042875720155503)

# server
# D:\KFUPM\COE449\project\my_text.txt
# C:\Users\User\IdeaProjects\python training\.idea\myfile.txt
# C:\Users\User\IdeaProjects\python training\.idea\lastcrashefile.txt
directroy = input("if you have a previous file please inter it direcroty: (else just click enter)")
directroy = directroy.strip()
# he must have a table of all positions lets say a dictonary where the key is the row and the value is columns
myTextFile = dict()
if "" == directroy:
    myTextFile = dict()
else:
    f=open(directroy,"rb")
    print('opned file')
    #my_file = f.read()
    myTextFile = pickle.load(f)
    print(myTextFile)
    '''lines = 0
    for x in f:
        myTextFile[lines] = x.split()
        lines += 1
        #print(x)'''
    f.close()

print(' server view of text file: ')
print(myTextFile)
#print(myTextFile[1][0])

# opening socket

HEADERSIZE = 10
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen(5)
print("waiting for connection")
conn, addr = s.accept()
print(f"Connection from {addr} has been established.")

# after recieveing the connection directly send the current text file, if it is new just send and empty string
# serilize then send throuh pickle
if "" == directroy:
    msg = pickle.dumps("")
    print(msg)
    msg = bytes(f"{len(msg):<{HEADERSIZE}}",'utf-8')+msg
    print(msg)
    conn.send(msg)
else:
    msg = pickle.dumps(myTextFile)
    msg = bytes(f"{len(msg):<{HEADERSIZE}}",'utf-8')+msg
    print(msg)
    conn.send(msg)

# after client send
# server
while True:
   try:
        m = recieve_messages(conn,1,HEADERSIZE,10)
        if m == 0:
            print("verification")
            continue
        rec_m = pickle.loads(m[0])
        print(rec_m," line and inedex")


        # given line and start index
        given_line = rec_m[0]
        given_index = rec_m[1]

        if given_line == "exit":
            if directroy == "":
                f = open("myfile.txt","wb")
            else:
                f = open(directroy,"wb")
            print(pickle.dumps(myTextFile))
            pickle.dump(myTextFile,f )
            #f.write(pickle.dumps(myTextFile))
            print('file saved succefully at the specified location')
            f.close()
            break


        # editing text file


        # now i need to decide the type of operation
        del_operation = False
        del_type = 'none'
        insertion = False
        breaking = False
        if given_index[0].upper() == 'ADD':
            #index = ['ADD',int(command[2]),encrypted_messages]
            #print(given_index)
            encrypted_messages = given_index[2]
            given_index = given_index[1]
        elif given_index[0] == "INSERT":
            encrypted_messages = given_index[2]
            given_index = given_index[1]
            insertion = True
        elif given_index[0] == "BREAK":
            given_index = given_index[1]
            message_to_nextline = myTextFile[given_line][given_index:]
            # delete letters
            counter = given_index
            #while counter < len(myTextFile[given_line]):
            #if counter >= given_index:
            del myTextFile[given_line][given_index:]
            #counter += 1
            # now move the lines ahead
            mykeys = sorted(myTextFile.keys(), reverse = True)
            breaking = True
            for i in mykeys:
                if i > given_line:
                    myTextFile[i+1] = myTextFile[i]

            myTextFile[given_line+1] = message_to_nextline
            #break 3 4
        elif given_index[0] == "MERGE":
            # (MERGE 3 4 ) appending line 4 to line 3
            temp = myTextFile[given_index[1]]
            del_operation = True
            del_type = 'line'
            delete_line_number = given_index[1]
            del myTextFile[delete_line_number]
            mykeys = sorted(myTextFile.keys())
            for i in mykeys:
                if i > delete_line_number:
                    myTextFile[i-1] = myTextFile.pop(i)
            if given_line < given_index[1]:
                for i in temp:
                    myTextFile[given_line].append(i)
            else :
                for i in temp:
                    myTextFile[given_line-1].append(i)

        elif given_index[0] == 'Delete':
            if len(given_index) == 1:
                # Delete line command ( DEL 4 )
                # index = ['Delete']
                given_index = 'Delete'
                del_operation = True
                del_type = 'line'
                delete_line_number = given_line
                del myTextFile[given_line]
                mykeys = sorted(myTextFile.keys())
                for i in mykeys:
                    if i > given_line:
                        myTextFile[i-1] = myTextFile.pop(i)

            elif len(given_index) == 2:
                # (DEL 4 3) to delete letter at index 3 line 4
                # index = ['Delete',int(command[2])]
                given_index = given_index[1]
                del_operation = True
                del_type = 'index'
                del myTextFile[given_line][given_index]

        elif given_index[0] == 'Delrange':
            # (DEL 3 range 1 5) delete 1-5 indexes at line 3
            # index.append('Delrange') and the rest are the indexes to be deleted
            # list of indexes to delete
            given_index = given_index[1:]
            del_operation = True
            del_type = 'range'
            given_index.sort(reverse = True)
            for i in given_index:
                del myTextFile[given_line][i]

        elif given_index[0] == 'LINES':
            # (DEL LINES 1 5) delete lines from 1 to 5
            # index = ['LINES'] + given line have the list of lines to delete
            del_operation = True
            del_type = 'lines'
            delete_line_numbers = given_line
            for i in delete_line_numbers:
                del myTextFile[i]
            first, last = min(given_line) , max(given_line)
            mykeys = sorted(myTextFile.keys())
            current_min = first
            for i in mykeys:
                if i > last:
                    myTextFile[first] = myTextFile.pop(i)
                    first += 1

        # addition process
        if not del_operation and not breaking:
            lineExist = False
            indexExist = False
            # two types of space to make it a little harder to detect
            zero = pub_key.encrypt(random.choice([0,32]))
            #zero = pub_key.encrypt(32)
            if given_line in myTextFile:
                lineExist = True
                if given_index <len(myTextFile[given_line]):
                    indexExist = True
                else:
                    while len(myTextFile[given_line]) < given_index:
                        myTextFile[given_line].append(zero)
            else:
                try:
                    mylastKey = max(myTextFile.keys())
                except:
                    mylastKey = -1
                while mylastKey < given_line:
                    mylastKey += 1
                    myTextFile[mylastKey] = list()
                #myTextFile[give_line] = [zero,zero]
                while len(myTextFile[given_line]) < given_index:
                    myTextFile[given_line].append(zero)

            index = given_index
            for i in encrypted_messages:
                #print(myTextFile)
                #print(index)
                #print(len(myTextFile[given_line]))
                if insertion:
                    myTextFile[given_line].insert(index,i)
                else:
                    try:
                        myTextFile[given_line][index] += i
                    except:
                        myTextFile[given_line].append(i)
                index += 1

        print(' Server view of text file: ')
        print(myTextFile)

        # now we should send back the file to the user
        msg = pickle.dumps(myTextFile)
        msg = bytes(f"{len(msg):<{HEADERSIZE}}",'utf-8')+msg
        #print(msg)
        conn.send(msg)
   except Exception as e:
        print(e)
        print('client disconnected')
        f = open('lastcrashefile.txt',"wb")
        print(pickle.dumps(myTextFile))
        pickle.dump(myTextFile,f )
        #f.write(pickle.dumps(myTextFile))
        print('file saved succefully at lastcrashefile.txt due to disconnection')
        f.close()
        break
