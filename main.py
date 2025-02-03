#---------------------------------------------------
# Tradutor para a linguagem CALC
#
# versao 1a (mar-2024)
#---------------------------------------------------
from lexico import Lexico
from sintatico import Sintatico

class Tradutor:

    def __init__(self, nomeArq):
        self.nomeArq = nomeArq
        self.arq = None
        self.lexico = None
        self.sintatico = None

    def inicializa(self):
        self.arq = open(self.nomeArq, "r")
        self.lexico = Lexico(self.arq)
        self.sintatico = Sintatico(self.lexico)

    def traduz(self):
        print('Traduzindo...')
        self.sintatico.traduz()

    def finaliza(self):
        self.arq.close()

# inicia a traducao
if __name__ == '__main__':
    x = Tradutor('b_a_ba.txt')
    x.inicializa()
    # x.traduz()
    x.sintatico.traduz()
    x.finaliza()


