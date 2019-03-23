import  socket, threading, time
from JanelaAtendimento import JanelaAtendimento
from VideoDisplay import Player

class CallServer(threading.Thread):

     def __init__(self, host, port):
         threading.Thread.__init__(self)
         self.running = True
         self.isIncoming=False
         self.incomingClient=None

         self.host = host
         self.port = port
         self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
         self.sock.bind((self.host, self.port))
         #self.sock.settimeout(10)
         #GObject.threads_init()


     def try_to_stop(self):
         # Nota: nunca se sabe quando o servidor vai fechar
         self.sock.close()
         self.running = False

     def send(self,msg,client):
         self.sock.sendto(msg, client)


     def _mainloop(self, data, client, address):
         try:
             if self.incomingClient == address and data == "CANCEL":
                 self.atendimentoUI.on_close()
                 print("{} cancelou a Chamada!!!".format(address))
                 return True

             elif self.isIncoming is True:
                 print("{} se conectou!!!".format(address))
                 self.send(str("BLOCKED").encode(),client)
                 return True

             elif address == "127.0.0.1":
                 print("Foi aceita a chamada  por localhost !!!")
                 self.send(str("OK").encode(), client)
                 return True

             if data == "Ola":
                 print("{} se conectou!!!".format(address))
                 self.incomingClient = address
                 self.isIncoming = True

                 self.atendimentoUI = JanelaAtendimento(address)
                 response = self.atendimentoUI.run()
                 if response is True:
                     p = Player(ip=address)
                     p.run()
                     print("Foi aceita a chamada para {} !!!".format(address))
                     self.send(str("OK").encode(),client)
                 elif response is False:
                     print("Foi rejeitada a chamada para {}".format(address))
                     self.send(str("NO").encode(),client)
                 elif response is None:
                     print("{}: Timeout!!!".format(address))
                     self.send(str("Timeout").encode(),client)

                 self.incomingClient = None
                 self.isIncoming = False
                 return True

             else:
                 self.incomingClient = None
                 self.isIncoming = False
                 return False

         except Exception as erro:
             print(erro)
             self.incomingClient = None
             self.isIncoming = False
             return False

     def run(self):
         while self.running:
             self.sock.settimeout(0.5)
             # Espera uma conexao chegar no socket
             try:
                 data, address = self.sock.recvfrom(1024)
                 print(data, address)
                 # Alguem conectou
                 Thread = threading.Thread(target=self._mainloop,args=(data.decode(), address, address[0],))
                 Thread.start()
                 # self._mainloop(client, address)
             except Exception as e:
                 continue

# Chamada do servidor socket
if __name__ == "__main__":
    pode_criar_servidor = True
    while pode_criar_servidor:
        try:
            if servidor.isAlive():
                 time.sleep(0.1) # Evita sobrecarregar o computador
        except KeyboardInterrupt:
             pode_criar_servidor = False
             servidor.try_to_stop()
        except:
             if pode_criar_servidor:
                 servidor = CallServer('', 9999)
                 print("Iniciando Servidor")
                 servidor.start()
