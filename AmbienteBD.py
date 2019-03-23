# !/usr/bin/env python3

import sqlite3
from ConnectBD import Connect

class Ambiente:
    def __init__(self):
        # Criar conexão e cursor
        self.db = Connect('SSH_UFF.db')
        self.tb_name = "Ambientes"
        self.__cria_tabela__()


    def __cria_tabela__(self):

        cur =  self.db.cursor
        # Criar tabela Ambientes
        cur.execute("""CREATE TABLE IF NOT EXISTS %s (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome VARCHAR NOT NULL UNIQUE,
                    sigla VARCHAR NOT NULL UNIQUE,
                    ip VARCHAR NOT NULL UNIQUE,
                    descricao TEXT )""" % (self.tb_name))

    def cadastrar(self, nome, sigla, ip, descricao):
        cur = self.db.cursor
        try:
            cur.execute("""INSERT INTO %s (nome, sigla, ip, descricao)
                        VALUES (?,?,?,?)""" % (self.tb_name),
                        (nome, sigla, ip, descricao))

        except sqlite3.IntegrityError:
            return("Aviso!", "\nAlguma informação está repetida")
        self.db.commit()
        return("Dados inseridos com sucesso")

    def listar_ambientes(self):
        sql = "SELECT * FROM %s ORDER BY nome" % (self.tb_name)
        r = self.db.cursor.execute(sql)
        return r.fetchall()

    def listar_ambiente(self,id):
        sql = "SELECT * FROM  %s  WHERE ID=%d" % (self.tb_name,id)
        r = self.db.cursor.execute(sql)
        return r.fetchall()[0]

    def listar_ambiente_por_IP(self, IP):
        sql = "SELECT * FROM  %s WHERE ip='%s'" % (self.tb_name, IP)
        r = self.db.cursor.execute(sql)
        return r.fetchall()[0]

    def atualizar(self, id, nome, sigla, ip, descricao):
        try:
            # verificando se existe ambiente com o ID passado, caso exista
            c = self.listar_ambiente(id)
            if c:
                self.db.cursor.execute("""
                UPDATE %s
                SET nome = ? , sigla = ? , ip = ? , descricao = ?
                WHERE id = ?
                """ % (self.tb_name), (nome, sigla, ip, descricao, id))
                # gravando no bd
                self.db.commit()
                return("Dados atualizados com sucesso.")
            else:
                return('Não existe ambiente com o id informado.')

        except sqlite3.IntegrityError:
            return("Aviso!", "\nInformação está repetida em %s" % (self.tb_name))

        except:
            raise

    def deletar(self, id):
        try:
            # verificando se existe ambiente com o ID passado, caso exista
            c = self.listar_ambiente(id)
            if c:
                self.db.cursor.execute("""
                DELETE FROM %s WHERE id = ?
                """ % (self.tb_name), (id,))
                # gravando no bd
                self.db.commit()
                return("Registro %s excluído com sucesso." % (id))
            else:
                return('Não existe ambiente com o código informado.')

        except sqlite3.IntegrityError:
            return ("Aviso!", "\nInformação está repetida em %s" % (self.tb_name))

        except:
            raise

    def fechar_conexao(self):
        self.db.close_db()