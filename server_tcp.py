import socket,select

def main():
    while True:   
      address=('',30000)
      sock=[0 for i in range(2)] #crea array di dim 2 {0,1}
      sock[0]=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock[0].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      sock[0].bind(address)
      print('Messo in attesa ipv4.....')
      sock[0].listen(5)
      
      address1=('',40000)
      sock[1] = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
      sock[1].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      sock[1].bind(address1)
      sock[1].listen(5)
      print('Messo in attesa ipv6.....')


      ready_socks,a,b = select.select(sock, [], []) #
      for s in ready_socks:
        conn, addr =s.accept()
        print("Connesso ad IP: "+ str(addr[0])+", porta: "+str(addr[1]))
        print("In attesa di ricevere il comando ...")
        data="Pronto..."
        #while data:
          #data=conn.recv(4096)
          #print(data)
        data=conn.recv(1024)
        data=data.strip() #dall'altro lato viene inviato nche un carattere di \n

        print(data)
        if data == "logi":
          print("login")
        else:
          print("error")
        
        s.close()



if __name__ == '__main__':
    main()
