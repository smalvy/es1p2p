#!/usr/bin/env python3
import os,sys,select,random,string

def login(p_req):
    #IPP2P=IPv4+"|"+IPv6 [55B]
    ipP2P=p_req[:55]
    #PP2P [5B]
    pP2P=p_req[55:]
    try:
        #Apro il file "peers.txt" che contiene per ogni riga "IPP2P PP2P SessionID\n"
        #Il file viene aperto in append (righe aggiunte alla fine del file e file creato se non esiste),
        #quindi la testina verrà posizionata alla fine del file, 
        #il '+' indica che é anche possibile leggerlo, la 't' indica che é un file di testo
        fpeers=open("peers.txt","a+t")
        #Riporto la testina di lettura all'inizio del file per leggerlo in modo da verificare che l'utente
        #richiedente il login non sia già registrato
        fpeers.seek(0,0)
        #Leggo una riga per volta (55+5+16+3=79B, dove il 3 tiene conto dei due spazi e dell'accapo)
        found=False
        rdata=fpeers.read(79)
    except IOError:
        print("ERRORE: apertura del file 'peers.txt' o nella lettura della prima riga di tale file")
        return '0000000000000000'
    else:
        while rdata!='' and not(found):
            if ipP2P==rdata[:55]:
                found=True
                fpeers.close()
                return '0000000000000000'
            else:
                try:
                    rdata=fpeers.read(79)
                except IOError:
                    print("ERRORE: lettura di una riga del file 'peers.txt'")
                    return '0000000000000000'
        #Se il peer non è presente fra quelli registrati allora genero un sessionID e lo scrivo nel file
        if not(found):
            #genero una stringa alfanumerica con sole lettere maiuscole da assegnare come ID di sessione ad un peer
            sessionID=''.join(random.SystemRandom().choice(string.ascii_uppercase+string.digits) for _ in range(16))
            try:
                fpeers.write(ipP2P+" "+pP2P+" "+sessionID+"\n")
                fpeers.close()
            except IOError:
                print("ERRORE: scrittura nel file 'peers.txt' di un peer")
                return '0000000000000000'
            else:
                return "ALGI"+sessionID


def logout(p_req):
    #Il p_req privato dei primi 4 bytes corrisponde al SessionID di 16 bytes
    sessionID=p_req.strip()
    #fregcount indica il numero dei file che sono stati registrati dal peer che vuole fare il logout
    fregcount=0
    try:
        #Apro il file "lista_file.txt
        flist=open("lista_file.txt","rt")
        #Apro il file "new_lista_file.txt" sul quale verranno scritti tutte le righe del file "lista_file.txt"
        #tranne quelle che contengono il SessionID del peer che ha richiesto il logout
        newflist=open("new_lista_file.txt","wt")
        #Stringa che conterrà le righe con sessionID diverso da quello dell'utente che fa il logout
        new_lines=''
        #Riga di "lista_file.txt"=sessionID;filemd5;filename;ip;porta\n=16B+1B+16B+1B+100B+1B+55B+1B+5B+1B+1B=198B
        #Leggo tutte le righe del file "lista_file.txt"
        lines=flist.readlines()
        for i in range(len(lines)):
            line_elements=lines[i].split(';')
            if(line_elements[0]==sessionID):
                fregcount=fregcount+1
            else:
                new_lines=new_lines+lines[i]  #+"\n"
        #Scrivo la stringa che contiene le righe senza sessionID dell'utente nel file "new_lista_file.txt"
        newflist.write(new_lines)
        #Chiudo i file
        flist.close()
        newflist.close()
        #Cancello il vecchio file "lista_file.txt"
        os.remove("lista_file.txt")
        #Rinomino il file "new_lista_file.txt" in "lista_file.txt"
        os.rename("new_lista_file.txt","lista_file.txt")
    except IOError:
        print("ERRORE: operazione di eliminazione dei file dell'utente con SessionID "+sessionID)
        return '0000000000000000'
    else:
        try:
            #Apro il file "peers.txt"
            plist=open("peers.txt","rt")
            #Apro il file "new_peers.txt" sul quale verranno scritte tutte le righe del file "peers.txt"
            #tranne quella che contiene il SessionID del peer che ha richiesto il logout
            newplist=open("new_peers.txt","wt")
            #Stringa che conterrà le righe con sessionID diverso da quello dell'utente che fa il logout
            new_lines=''
            #Riga di "peers.txt"=IPP2P PP2P SessionID\n=55B+1B+5B+1B+16B+1B=79B
            #Leggo tutte le righe dal file "peers.txt"
            lines=plist.readlines()
            for i in range(len(lines)):
                line_elements=lines[i].split()
                if(line_elements[2]!=sessionID):
                    new_lines=new_lines+lines[i]
            #Scrivo la stringa che contiene le righe senza sessionID dell'utente nel file "new_lista_file.txt"
            newplist.write(new_lines)
            #Chiudo i file
            plist.close()
            newplist.close()
            #Cancello il vecchio file "peers.txt"
            os.remove("peers.txt")
            #Rinomino il file "new_peers.txt" in "peers.txt"
            os.rename("new_peers.txt","peers.txt")
        except IOError:
            print("ERRORE: operazione di rimozione dell'utente "+sessionID+" dagli utenti registrati")
            return '0000000000000000'
        else:
            return "ALGO"+str(fregcount).ljust(3,' ')


def notify_dowload(request):
	count=0
	peer_request=request
	#sessionid=peer_request[0:16].replace(" ","")
	#filemd5=peer_request[16:32].replace(" ","")
	sessionid=peer_request[0:16].strip(" ")
	filemd5=peer_request[16:32].strip(" ")
	sessionid = str(sessionid)
	filemd5=str(filemd5)
	file = open("lista_download.txt", "a")
	file.write(sessionid+";"+filemd5+";\n")
	file.close()

	file = open("lista_download.txt","r")
	lines = file.readlines()
	for line in lines:
		if line == "":
			break
		params = line.split(";")
		if(params[1] == filemd5):
			count = count+1		#in teoria se tutto va bene becca almeno quello appena aggiunto, count sempre >= 1
	file.close()	


	#tempo di aggiungere gli spazi necessari a "#download"
	str_count = str(count)
	n = len(str_count)
	str_count = ""
	if(n<5):
		i=5-n
		for j in range(0,i):
			str_count = str_count+" "
	str_count = str_count+str(count)

	#Tempo di inviare il conteggio al peer che mi ha segnalato il download
	ack = "ADRE"+str_count
	return ack


def search_file(request):
    peer_request = request.strip()
    titolo = peer_request[16:36]
    if titolo == "*":
        titolo=""
    print("Titolo:",titolo)
    #---Modulo di ricerca e salvataggio---# Scorre tutto il file e salva una matrice e un array con tutti i dati necessari
    c=0
    md5arr = [] #Array degli md5 unici trovati con len() secondo paramentro risposta
    filesmd5 = Matrix = [[0 for x in range(4)] for x in range(99)]  #Matrice MD5 Nomefile IP
    with open("lista_file.txt") as f:
        for line in f:
            if titolo in line:
                params=line.split(";")
                filemd5=params[1]
                #--Valutazione unicità--#
                intc=0
                for md5 in md5arr:
                    if(md5==filemd5):#Conto ricorrenze, per costruzione ritorna 0 o 1
                        intc+= 1
                if(intc==0):# Non c'è l'md5 nell'array
                    md5arr.append(filemd5) # Lo inserisco
                #--Fine Valutazione Unicità--#
            
                filesmd5[c][0]=filemd5
                filesmd5[c][1]=params[2]#Titolo
                filesmd5[c][2]=params[3]#Ip
                filesmd5[c][3]=params[4]#Porta
            c+= 1
    f.close()
    #---Fine Modulo di ricerca e salvataggio---#

    #Primo parametro di risposta
    inizior='AFIN'
    
    #Secondo parametro di risposta
    idmd5=len(md5arr)

    #Terzo parametro di risposta
    terzo=""
    for md5 in md5arr:
        c=0 #contatore occorrenze, terzoi
        primoi=md5.ljust(16)
        arrip=""
        for md5b in filesmd5:
            if md5b[0]==md5:
                secondoi=md5b[1].ljust(100) #Titolo
                c+= 1
                #Metto in un array di stringhe tutti gli ip:porta per quella risorsa, separati da ;
                arrip=arrip+';'+md5b[2].ljust(55)+';'+md5b[3].ljust(5)
        terzo=terzo+primoi+secondoi+";"+str(c).ljust(3)+";"+arrip

    cleaned=inizior+str(idmd5).ljust(3)+terzo
    cleaned=cleaned.replace(';','')  #Ho usato i ; per rendere i risultati human readable, per la risposta al client ripulisco
    print("Risposta:\n"+cleaned)
    return cleaned


def add_file(request,ip_peer,porta_peer):
    count=0
    #ip=ip_peer[7:]
    porta=porta_peer
    #peer_request="1234567812345678aaaaaaaa12345678pippolon.txt                 "
    peer_request=request
    sessionid=peer_request[0:16].replace(" ", "")
    filemd5=peer_request[16:32].replace(" ", "")
    filename=peer_request[32:].replace(" ", "").strip()
    ip=get_ip(sessionid)
    print(ip)

    #leggo tutto il file
    modificato=False
    file = open("lista_file.txt","r")
    lines = file.readlines()
    file.close()
    #scrivo il file con le linee modificate se ci sono    (update)
    file = open("lista_file.txt","w")
    for line in lines:
        if line=="":
             break
        params=line.split(";")
        if ((params[1]==filemd5) and (params[0]==sessionid)):
            file.write(sessionid+";"+filemd5+";"+filename+";"+ip+";"+str(porta)+';\n')
            modificato=True
        else:
            file.write(line)



    #scrivo file- aggiungo il record in fondo al file
    if modificato==False:
        file = open("lista_file.txt","a")
        file.write(sessionid+";"+filemd5+";"+filename+";"+ip+";"+str(porta)+';\n')
        file.close()

    #leggo il file e conto il num di copie
    file = open("lista_file.txt","r")
    while 1:
        in_line = file.readline()
        if(in_line==""):
                print("break")
                break
        params=in_line.split(";")
        print(params[0]+" "+params[1]+" "+params[2]+" "+params[3]+" "+params[4]+" memorizzato") #sessionid,filemd5,filename
        if(params[1]==filemd5):
                count=count+1
    print("il numero di copie :"+str(count))

    str_count=str(count)
    n=len(str_count)
    str_count=""

    #aggiungo gli spazi al numero di copie se e meno di 3 caratteri
    if(n<3):
        i=3-n
        for j in range(0,i):
            str_count=str_count+" "
    str_count=str_count+str(count)

    ack="AADD"+str_count
    file.close()
    return ack


def delete_file(request): 
    count=0
    peer_request=request
    #peer_request="1234567812345678aaaaaaaa12345678pippo.txt                 "
    sessionid=peer_request[0:16].replace(" ", "")
    filemd5=peer_request[16:32].replace(" ", "")
    filename=peer_request[32:].replace(" ", "").strip()
    #ip="172.30.11.4"
    #ip="fc00::b:4"

    #leggo tutto il file
    modificato=False
    count=0
    eliminati=0
    file = open("lista_file.txt","r")
    lines = file.readlines()
    file.close()
    #scrivo il file con le linee modificate se ci sono
    file = open("lista_file.txt","w")
    for line in lines:
        params=line.split(";")
        if ((params[1]==filemd5) and (params[0]==sessionid)):
                modificato=True
                eliminati=eliminati+1
                print(line)
                #print("fatto")
        elif ((params[1]==filemd5) and (params[0]!=sessionid)):
                count=count+1
                file.write(line)
        else:
                file.write(line)


    str_count=str(count)
    n=len(str_count)
    str_count=""
    #aggiungo gli spazi al numero di copie se è meno di 3 caratteri
    if(n<3):
            i=3-n
            for j in range(0,i):
                str_count=str_count+" "
    str_count=str_count+str(count)

    ack="ADEL"+str_count
    if(modificato==True):
            print("ACK di risposta: "+ack+" file eliminati: "+str(eliminati))
    else:
            ack="ADEL999"
            print("File non esistente: "+ack)
    file.close() 
    return ack


def get_ip(session_id):
    sessionid=session_id
    file = open("peers.txt","r")
    while 1:
        in_line = file.readline().strip()
        if(in_line==""):
                print("break")
                break
        params=in_line.split(" ")
        if(params[2]==sessionid):
            return params[0]


def valid_sid(id):
    found=False
    with open("peers.txt") as f:
        for line in f:
            if id in line:
                found=True
    f.close()
    return found