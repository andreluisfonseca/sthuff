'''
Classe para realizar a tentativa de chamada,
A requisição de chamada para host online está funcionado,
Para tentativas com host offline a mesma ainda precisa de ajustes,
portanto ainda ainda será reformulada.

A interface em ambiente Grafico dessa classe so funciona se mesma for
executada como um subprocesso.
'''

import socket, threading, time,sys
from JanelaRequisicao import JanelaRequisicao

class RequisicaoChamada:

    def __init__(self, host="127.0.0.1", port=9999,data="Ola"):
        self.running = True
        self.__host = host
        self.__port = port
        self.__address = (host,port)
        self.__data = data
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.isCanceled = False
        self.request = False
        #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.sock.bind((self.__host, self.__port))


    def __request_Call_UI(self):
        self.requisicaoUI = JanelaRequisicao(self.__host)
        request = self.requisicaoUI.run()
        if request is not True:
            self.isCanceled = True
            self.sock.sendto(str("CANCEL").encode(),self.__address)
            self.stop()
            print("CANCEL")
        return request

    def stop(self):
        self.running = False

    def __request_call(self,size=1024):
        self.sock.sendto(str(self.__data).encode(),self.__address)
        self.sock.settimeout(0.5)
        while self.running:
            try:
                data = self.sock.recvfrom(size)[0].decode()
                if data:
                    if data == "BLOCKED":
                        self.request = False
                    if data == "OK":
                        self.request = True
                    elif data == "NO":
                        self.request = False
                    elif data == "Timeout":
                        self.request = False
                    print(data)
                    self.stop()
            except:
                continue

        if self.isCanceled is False:
            self.requisicaoUI.on_close()

    def close(self):
        self.sock.close()

    def run(self):
        ThreadUI = threading.Thread(target=self.__request_Call_UI, args=())
        ThreadUI.start()
        time.sleep(0.150)
        self.__request_call()

if __name__ == "__main__":
    r = RequisicaoChamada(sys.argv[1],9999)
    try:
        r.run()
    except Exception as err:
        print(err)


