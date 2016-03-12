import logging
import threading
import time
import socket,sys,random,string
from functions_v3 import *

#serve soltanto per fare stampe di debug, utile per i thread, questo è il layout della stampa
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

class MyThread(threading.Thread):
    def __init__(self,ip,porta,socket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.porta = porta
        self.conn=socket
        print ("[+] New thread started for "+str(ip)+":"+str(porta))

    #questa funzione viene eseguita automaticamente quando viene fatto lo start() del thread
    def run(self):
        logging.debug('Connesso al client con: '+str(self.ip)+' e porta: '+str(self.porta))
        
        while True:
            #print("Server connesso al client con IP: "+ str(addr[0])+", porta: "+str(addr[1]))
            print("In attesa di ricevere il comando ...")
            #Si è scelto un buffer di soli 256 bytes perché la richiesta più lunga da parte di un peer contiene 136 bytes
            peer_request=self.conn.recv(256).decode() #decode trasforma i bytes restituiti dalla socket in stringa (default encoding=utf-8)
            #La funzione richiesta al server è codificata nei primi 4 bytes della richiesta
            command=peer_request[:4]
            sid=peer_request[4:20]
            #Serie di if else per determinare quale funzione deve eseguire il server
            #dir_response contiene la stringa di risposta da inviare al peer
            #NOTA CHE sono stati riportati gli indici finali nello slicing
            #per far prove con netcat (netcat invia anche il carattere "\n" che
            #con questi indici viene ignorato)
            dir_response=''
            if command=="LOGI":
                lock.acquire()
                dir_response=login(peer_request[4:64])
                lock.release()
            elif command=="ADDF" and valid_sid(sid):
                lock.acquire()
                dir_response=add_file(peer_request[4:136],self.ip,self.porta)
                lock.release()
            elif command=="DELF" and valid_sid(sid):
                lock.acquire()
                dir_response=delete_file(peer_request[4:36])
                lock.release()
            elif command=="FIND" and valid_sid(sid):
                lock.acquire()
                dir_response=search_file(peer_request[4:40])
                lock.release()
            elif command=="DREG" and valid_sid(sid):
                lock.acquire()
                dir_response=notify_dowload(peer_request[4:36])
                lock.release()
            elif command=="LOGO":
                lock.acquire()
                dir_response=logout(sid)
                lock.release()
                self.conn.send(dir_response.encode())
                self.conn.close()
                print("Connessione chiusa")
                break
        
            if dir_response=='':
            #Se command non è uguale a nessuna delle stringhe precedenti (errore di un peer) allora chiudo la socket e quindi la connessione.
            #NOTA CHE questa eventualità non è prevista nelle specifiche del sistema.
                dir_response='0000000000000000'
            #Il server invia la stringa restituita da una delle funzioni e chiude la connessione
            self.conn.send(dir_response.encode())
        logging.debug('Mi sto disconnettendo da: '+str(self.ip)+' e porta: '+str(self.porta))


#--------------------------------------------------------------
#----------CODICE PROCESSO PRINCIPALE

#creo il lock
lock=threading.Lock()        
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
      
while True:
    server_socket.listen(5)
    print("Server in ascolto sulla porta "+str(server_socket.getsockname()[1])+" con indirizzo "+str(server_socket.getsockname()[0]))
    (clientsock, addr) = server_socket.accept()
    newthread = MyThread(addr[0],addr[1], clientsock) #creo il thread e gli faccio gestire la socket aperta
    newthread.start()   #avvio il thread
