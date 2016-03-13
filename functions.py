#!/usr/bin/env python3
import os,sys,select,random,string
import sqlite3

def login(p_req, db_conn, cursor):
    #IPP2P=IPv4+"|"+IPv6 [55B]
    ip_peer=p_req[:55]
    #PP2P [5B]
    porta_peer=p_req[55:]
    try:
    	query_string = "select count(*) from Users where sessionID= '%s'" % sessionID.strip()
    	result = cursor.execute(query_string)
    	num = result.fetchone()
    except Exception as e:
		print(e)
        return '0000000000000000'
    else:
    	if(num[0] == 0):
    		return '0000000000000000'
        #Se il peer non è presente fra quelli registrati allora genero un sessionID e lo scrivo nel file
        elif:
            #genero una stringa alfanumerica con sole lettere maiuscole da assegnare come ID di sessione ad un peer
            sessionID=''.join(random.SystemRandom().choice(string.ascii_uppercase+string.digits) for _ in range(16))
            try:
            	cursor.execute("INSERT INTO Utente (sessionID, ip, porta) values (?, ?, ?)", (sessionID, ip_peer,porta_peer))
        		db_conn.commit()
        		print("User inserito: \tsessionID: %s \t ip: %s \t port: %s" % (sessionID, ip_peer,porta_peer))
            except Exception as e:
				print(e)
                return '0000000000000000'
            else:
                return "ALGI"+sessionID

def logout(p_req, db_conn, cursor):
    #Il p_req privato dei primi 4 bytes corrisponde al SessionID di 16 bytes
    sessionID=p_req.strip()
    try:
    	query_string = "SELECT count(*) from Utenti WHERE sessionID= '%s'" % sessionID
    	result = cursor.execute(query_string)
    	num = result.fetchone()
    	num_file_eliminati = num[0]		#numero di file eliminati
    	query_string = "DELETE FROM Users WHERE sessionID = '%s'" % sessionID
    	cursor.execute(query_string)
    	db_conn.commit()	
    	print("User deleted:\nsessionID: %s n.deleted files: %s" % (session_id, num_file_eliminati)
    except Exception as e:
		print(e)
        return '0000000000000000'
    return "ALGO"+str(result).ljust(3)


def notify_dowload(request,db_conn, cursor):
	count=0
	peer_request=request
	sessionid=peer_request[0:16].strip()
	filemd5=peer_request[16:32].strip()
	sessionID = str(sessionID)
	filemd5=str(filemd5)
	#recupero dei dati dalla stringa
	try:
		cursor.execute("UPDATE files SET file_count = file_count+1 WHERE file_md5=?", (filemd5),)
		db_conn.commit()
	except Exception as e:
		print(e)
	result = cursor.execute("SELECT * FROM files WHERE file_md5", (filemd5),)
	num_download = result.fetchone()
	print("Numero download: " + num_download[0])
	num_download = str(num_download[0].ljust(5))
	return "ADRE" + num_download


def search_file(request,db_conn, cursor):

	#La risposta è quindi articolata nel numero complessivo di identificativi md5 #idmd5
	#dove per ognuno di essi viene riportato 
	#l’identificativo md5, il nome del file e il numero di copie presenti #copy,
	#mentre per ogni copia viene riportato l’IP e la porta del peer. 
    peer_request = request.strip()
    titolo = peer_request[16:36]
    titolo = "'%"+titolo+"%'"			#nella query prende tutto quello che comprende "titolo" 
    query_string = "SELECT count(file_md5) FROM files WHERE file_name like %s" % titolo
    result = cursor.execute(query_string)
    num_md5 = result.fetchone()
    num_md5 = str(num_md5[0].ljust(3))		#estrazione del numero di md5 corrispondenti

    query_string = "SELECT file_md5, file_name, count(file_md5) FROM Utente WHERE file_name like %s" % titolo
    #prendo la riga di informazioni di ogni cosa che somiglia alla stringa cercata
    result=cursor.execute(query_string)
    rows = result.fetchall()
    #row[0] = file_md5 row[1] = file_name

    msg = "AFIN" + str(num_md5) #AFIN+numero di copie corrispondenti
    #encode?

    for row in rows:
    	query_string = "SELECT count(file_name) FROM Users WHERE file_md5 =?", (row[0],)
    	result= cursor.execute(query_string)
    	num_file = result.fetchone()
    	num_file = num_file[0]
    	#“AFIN”[4B].#idmd5[3B].{Filemd5_i[16B].Filename_i[100B].#copy_i[3B].{IPP2P_i_j[55B].PP2P_i_j[5B]}}(j=1..#copy_i)}
    	msg = msg + row[0] + row[1] + str(num_file).ljust(3) #manca il pezzo dell'IP e della porta
    	#o ci faccio mille query per risalire dai vari md5 agli utenti e da utenti ai loro IP e Porte o ci sarà altro modo
    	#msg = msg.encode()
    return msg

def add_file(request,ip_peer,porta_peer,db_conn, cursor):
    #ip=ip_peer[7:]
    porta=porta_peer
    #peer_request="1234567812345678aaaaaaaa12345678pippolon.txt                 "
    peer_request=request
    sessionID=peer_request[0:16].strip()
    filemd5=peer_request[16:32].strip()
    filename=peer_request[32:].strip()
    try:
    	cursor.execute("DELETE from files where session_id=? AND file_md5=? AND file_name=?", (sessionID, filemd5, filename))
       	db_conn.commit()
        cursor.execute('INSERT INTO files (session_id, file_md5, file_name) values(?, ?, ?)', (session_id, filemd5, filename))
        db_conn.commit()
        result = cursor.execute("SELECT count(*) FROM files WHERE file_md5=?", (filemd5,))
        num = result.fetchone()
  	except Exception as e:
  		print(e)

  	str_count=str(num[0])
  	return ("AADD"+ str_count.ljust(3))

def delete_file(request,db_conn, cursor): 
    peer_request=request
    #peer_request="1234567812345678aaaaaaaa12345678pippo.txt                 "
    sessionID=peer_request[0:16].strip()
    filemd5=peer_request[16:32].strip()
    filename=peer_request[32:].strip()
    #ip="172.30.11.4"
    #ip="fc00::b:4"
    result = cursor.execute("SELECT COUNT(*) FROM files WHERE session_id = ? AND file_md5 = ?", (sessionID, filemd5))
    num = result.fetchone()
    if num[0] > 0:	#c'è qualcosa da cancellare
    	try:
    		cursor.execute("DELETE FROM files WHERE session_id = ? AND file_md5 = ?", (sessionID, filemd5))
    		db_conn.commit()
    	except Exception as e:
    		print(e)
    	result = cursor.execute("SELECT COUNT(*) FROM files WHERE file_md5 = ?", (filemd5,))
    	num_md5 = result.fetchone()		#numero file con questo md5 rimasti
    	num_md5 = str(num_md5[0]).ljust(3)
    	msg="ADEL"+ str(num_md5)
   	else
   		msg="ADEL999"
   	return msg