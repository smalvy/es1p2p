#!/usr/bin/env python3

import socket,select,sys,random,string

#Importo i file che contengono le funzioni della directory

from functions_v3 import *


#Porta sulla quale si mette in ascolto il server
port=3000
#Creo una socket per indirizzi IPv6 su tipo datastream
server_socket=socket.socket(socket.AF_INET6,socket.SOCK_STREAM,0)
#Per il riuso degli indirizzi locali senza dover aspettare un certo intervallo di tempo
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
#Vedi il manuale linux (man 7 ipv6) il significato del flag IPV6_V6ONLY
#Se questo flag é 0 allora la socket può essere usata per spedire e ricevere pacchetti
#per e da un indirizzo IPv6 o un indirizzo IPv6 IPv4-mapped. Se invece é diverso da 0
#allora la socket può inviare e ricevere solo pacchetti IPv6.
server_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY,0)
#Se nella bind viene specificata la stringa vuota come indirizzo, allora la socket é
#associata a qualsiasi indirizzo assegnato alla macchina.
server_socket.bind(('',port)) #all'interno della tupla sono stati omessi due elementi: flowinfo e scopeid
#Metto in attesa di richieste la socket (5 è il numero di richieste al server che possono essere accodate nella coda associata alla socket)
server_socket.listen(5)
print("Server in ascolto sulla porta "+str(server_socket.getsockname()[1])+" con indirizzo "+str(server_socket.getsockname()[0]))

while True:
    conn,addr=server_socket.accept()
    print("Server connesso al client con IP: "+ str(addr[0])+", porta: "+str(addr[1]))
    print("In attesa di ricevere il comando ...")
    #Si è scelto un buffer di soli 256 bytes perché la richiesta più lunga da parte di un peer contiene 136 bytes
    peer_request=conn.recv(256).decode() #decode trasforma i bytes restituiti dalla socket in stringa (default encoding=utf-8)
    #La funzione richiesta al server è codificata nei primi 4 bytes della richiesta
    command=peer_request[:4]
    sid=peer_request[4:20]#session id
    
    #Serie di if else per determinare quale funzione deve eseguire il server
    #dir_response contiene la stringa di risposta da inviare al peer
    #NOTA CHE sono stati riportati gli indici finali nello slicing
    #per far prove con netcat (netcat invia anche il carattere "\n" che
    #con questi indici viene ignorato)
    dir_response=''
    if command=="LOGI":
        dir_response=login(peer_request[4:64])
    elif command=="ADDF" and valid_sid(sid):
        dir_response=add_file(peer_request[4:136],addr[0],addr[1])
    elif command=="DELF" and valid_sid(sid):
        dir_response=delete_file(peer_request[4:36])
    elif command=="FIND" and valid_sid(sid):
        dir_response=search_file(peer_request[4:40])
    elif command=="DREG" and valid_sid(sid):
        dir_response=notify_dowload(peer_request[4:36])
    elif command=="LOGO":
        dir_response=logout(sid)
        
    if dir_response=='':
        #Se command non è uguale a nessuna delle stringhe precedenti (errore di un peer) allora chiudo la socket e quindi la connessione.
        #NOTA CHE questa eventualità non è prevista nelle specifiche del sistema.
        dir_response='0000000000000000'
    #Il server invia la stringa restituita da una delle funzioni e chiude la connessione
    conn.send(dir_response.encode())
    conn.close()
    print("Connessione chiusa")
