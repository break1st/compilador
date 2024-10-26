#---------------------------------------------------
# Tradutor para a linguagem CALC
#
# versao 1a (mar-2024)
#---------------------------------------------------
from lexico import TOKEN, Lexico
from semantico import Semantico

class Sintatico:

    def __init__(self, lexico):
        self.lexico = lexico
        self.nomeAlvo = 'alvo.out'
        self.semantico = Semantico(self.nomeAlvo)

    def traduz(self):
        self.tokenLido = self.lexico.getToken()
        try:
            self.p()
            print('Traduzido com sucesso.')
        except:
            pass
        self.semantico.finaliza()

    def consome(self, tokenAtual):
        (token, lexema, linha, coluna) = self.tokenLido
        if tokenAtual == token:
            self.tokenLido = self.lexico.getToken()
        else:
            msgTokenLido = TOKEN.msg(token)
            msgTokenAtual = TOKEN.msg(tokenAtual)
            print(f'Erro na linha {linha}, coluna {coluna}:')
            if token == TOKEN.erro:
                msg = lexema
            else:
                msg = msgTokenLido
            print(f'Era esperado {msgTokenAtual} mas veio {msg}')
            raise Exception

    def testaLexico(self):
        self.tokenLido = self.lexico.getToken()
        (token, lexema, linha, coluna) = self.tokenLido
        while token != TOKEN.eof:
            self.lexico.imprimeToken(self.tokenLido)
            self.tokenLido = self.lexico.getToken()
            (token, lexema, linha, coluna) = self.tokenLido

#-------- segue a gramatica -----------------------------------------
    def p(self):
        # <p> --> program ident ; <declaracoes> <corpo> .
        self.consome(TOKEN.PROGRAM)
        lexema = self.tokenLido[1]
        self.consome(TOKEN.ident)
        self.consome(TOKEN.ptoVirg)
        self.semantico.gera(0, '# Codigo gerado pelo compilador Calc\n')
        nomeClasse = 'Prog' + lexema
        codigoInicial = \
            'class ' + nomeClasse + ':\n' + \
            '    def __init__(self):\n' + \
            '        pass\n'

        self.semantico.gera(0, codigoInicial)
        self.declaracoes()
        self.corpo()
        self.consome(TOKEN.pto)
        codigoFinal = \
            'if __name__ == \'__main__\':\n' + \
            '    _prog = ' + nomeClasse + '()\n' + \
            '    -prog._declaracoes()\n' + \
            '    _prog._corpo()'
        self.semantico.gera(0, codigoFinal)

    def declaracoes(self):
        # < declaracoes > -> LAMBDA | var <listavars>;
        if self.tokenLido[0] == TOKEN.VAR:
            self.consome(TOKEN.VAR)
            codigo = 'def _declaracoes(self):\n'
            self.semantico.gera(1, codigo)
            self.listavars()
            self.consome(TOKEN.ptoVirg)
        else:
            self.semantico.gera(1, 'def _declaracoes(self):\n')
            self.semantico.gera(2, 'pass\n')

    def listavars(self):
        # <listavars> -> ident <restoListavars>
        salva = self.tokenLido # salva possivel ident
        self.consome(TOKEN.ident)
        nomeVar = salva[1]
        self.semantico.gera(2, 'self.'+nomeVar+' = 0 \n')
        self.semantico.declara(salva)
        self.restoListavars()

    def restoListavars(self):
        # <restoListavars> -> LAMBDA | , <listavars>
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            self.listavars()
        else:
            pass

    def corpo(self):
        # <corpo> -> begin <cons> end
        self.consome(TOKEN.BEGIN)
        self.semantico.gera(1, 'def _corpo(self):\n')
        self.identacao = 2
        self.cons()
        self.consome(TOKEN.END)

    def cons(self):
        # <cons> -> LAMBDA | <com> <cons>
        entrou = False
        while self.tokenLido[0] in [TOKEN.ident,
            TOKEN.IF, TOKEN.WHILE, TOKEN.READ, TOKEN.PRINT]:
            self.com()
            entrou = True
        if not entrou:
            self.semantico.gera(self.identacao, 'pass\n')

    def com(self):
        # <com> -> <atrib> | <if> | <while> | <ler> | <escrever> | <bloco>
        if self.tokenLido[0] == TOKEN.ident:
            self.atrib()
        elif self.tokenLido[0] == TOKEN.IF:
            self.se()
        elif self.tokenLido[0] == TOKEN.WHILE:
            self.enquanto()
        elif self.tokenLido[0] == TOKEN.READ:
            self.ler()
        elif self.tokenLido[0] == TOKEN.PRINT:
            self.escrever()
        else:
            self.bloco()

    def atrib(self):
        # <atrib> -> ident = <exp> ;
        lexema = self.tokenLido[1]
        self.consome(TOKEN.ident)
        self.consome(TOKEN.atrib)
        codigo = self.exp()
        self.consome(TOKEN.ptoVirg)
        self.semantico.gera(self.identacao, lexema + ' = ' + codigo + '\n')

    def se(self):
        # <if> -> if ( <exp> ) <com> <elseopc>
        self.consome(TOKEN.IF)
        self.consome(TOKEN.abrePar)
        codigo = self.exp()
        self.consome(TOKEN.fechaPar)
        self.semantico.gera(self.identacao, 'if ' + codigo + ':\n')
        self.identacao += 1
        self.com()
        self.identacao -= 1
        self.elseopc()

    def elseopc(self):
        # <elseopc> -> LAMBDA | else <com>
        if self.tokenLido[0] == TOKEN.ELSE:
            self.consome(TOKEN.ELSE)
            self.semantico.gera(self.identacao, 'else: \n')
            self.identacao += 1
            self.com()
            self.identacao -= 1
        else:
            pass

    def bloco(self):
        # <bloco> -> { <cons> }
        self.consome(TOKEN.abreChave)
        #self.identacao += 1
        self.cons()
        self.consome(TOKEN.fechaChave)
        #self.identacao -= 1

    def ler(self):
        # <ler> -> read ( string , ident ) ;
        self.consome(TOKEN.READ)
        self.consome(TOKEN.abrePar)
        prompt = self.tokenLido[1]
        self.consome(TOKEN.string)
        self.consome(TOKEN.virg)
        variavel = self.tokenLido[1]
        self.consome(TOKEN.ident)
        self.consome(TOKEN.fechaPar)
        self.consome(TOKEN.ptoVirg)
        self.semantico.gera(self.identacao,
            variavel + ' = int(input(' + prompt + '))\n')

    def escrever(self):
        # <escrever> -> print ( <msg> ) ;
        self.consome(TOKEN.PRINT)
        self.consome(TOKEN.abrePar)
        codigo = self.msg()
        self.consome(TOKEN.fechaPar)
        self.consome(TOKEN.ptoVirg)
        self.semantico.gera(self.identacao, 'print(' + codigo + ')\n')

    def msg(self):
        # <msg> -> <coisa> <restomsg>
        parte1 = self.coisa()
        parte2 = self.restomsg()
        return parte1 + parte2

    def coisa(self):
        # <coisa> -> string | ident
        lexema = self.tokenLido[1]
        if self.tokenLido[0] == TOKEN.string:
            self.consome(TOKEN.string)
        else:
            self.consome(TOKEN.ident)
        return lexema

    def restomsg(self):
        # <restomsg> -> LAMBDA | , <msg>
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            parte1 = self.msg()
            return ',' + parte1
        else:
            return ''

    def enquanto(self):
        # <while> -> while ( <exp> ) <com>
        self.consome(TOKEN.WHILE)
        self.consome(TOKEN.abrePar)
        self.consome(TOKEN.fechaPar)
        self.exp()
        self.com()

    def exp(self):
        # <exp> -> <or>
        codigo = self.ou()
        return codigo

    def ou(self):
        # <or> -> <and> <restoOr>
        parte1 = self.e()
        parte2 = self.restoOr()
        return parte1 + parte2

    def restoOr(self):
        # <restoOr> -> or <and> <restoOr> | LAMBDA
        if self.tokenLido[0] == TOKEN.OR:
            self.consome(TOKEN.OR)
            parte1 = self.e()
            parte2 = self.restoOr()
            return ' or ' + parte1 + parte2
        else:
            return ''

    def e(self):
        # <and> -> <not> <restoAnd>
        parte1 = self.nao()
        parte2 = self.restoAnd()
        return parte1 + parte2

    def restoAnd(self):
        # <restoAnd> -> and <not> <restoAnd> | LAMBDA
        if self.tokenLido[0] == TOKEN.AND:
            self.consome(TOKEN.AND)
            parte1 = self.nao()
            parte2 = self.restoAnd()
            return ' and ' + parte1 + parte2
        else:
            return ''

    def nao(self):
        # <not> -> not <not> | <rel>
        if self.tokenLido[0] == TOKEN.NOT:
            self.consome(TOKEN.NOT)
            parte1 = self.nao()
            return ' not ' + parte1
        else:
            return self.rel()

    def rel(self):
        # <rel> -> <uno> <restoRel>
        parte1 = self.uno()
        parte2 = self.restoRel()
        return parte1 + parte2

    def restoRel(self):
        # <restoRel> -> LAMBDA | <oprel> <uno>
        if self.tokenLido[0] in [TOKEN.igual, TOKEN.diferente, TOKEN.menor,
                              TOKEN.menorIgual, TOKEN.maior, TOKEN.maiorIgual]:
            parte1 = self.oprel()
            parte2 = self.uno()
            return parte1 + parte2
        else:
            return ''

    def oprel(self):
        # <oprel> -> == | != | < | > | <= | >=
        salva = ' ' + self.tokenLido[1] + ' '
        if self.tokenLido[0] == TOKEN.igual:
            self.consome(TOKEN.igual)
        elif self.tokenLido[0] == TOKEN.diferente:
            self.consome(TOKEN.diferente)
        elif self.tokenLido[0] == TOKEN.menor:
            self.consome(TOKEN.menor)
        elif self.tokenLido[0] == TOKEN.maior:
            self.consome(TOKEN.maior)
        elif self.tokenLido[0] == TOKEN.menorIgual:
            self.consome(TOKEN.menorIgual)
        elif self.tokenLido[0] == TOKEN.maiorIgual:
            self.consome(TOKEN.maiorIgual)
        return salva

    def uno(self):
        # <uno> -> + <uno> | - <uno> | <soma>
        if self.tokenLido[0] == TOKEN.mais:
            self.consome(TOKEN.mais)
            parte1 = self.uno()
            return ' + ' + parte1
        elif self.tokenLido[0] == TOKEN.menos:
            self.consome(TOKEN.menos)
            parte1 = self.uno()
            return ' - ' + parte1
        else:
            return self.soma()

    def soma(self):
        # <soma> -> <mult> <restosoma>
        parte1 = self.mult()
        parte2 = self.restosoma()
        return parte1 + parte2

    def restosoma(self):
        # <restosoma> -> + <mult> <restosoma> | - <mult> <restosoma> | LAMBDA
        if self.tokenLido[0] == TOKEN.mais:
            self.consome(TOKEN.mais)
            parte1 = self.mult()
            parte2 = self.restosoma()
            return ' + ' + parte1 + parte2
        elif self.tokenLido[0] == TOKEN.menos:
            self.consome(TOKEN.menos)
            parte1 = self.mult()
            parte2 = self.restosoma()
            return ' - ' + parte1 + parte2
        else:
            return ''

    def mult(self):
        # <mult> -> < folha > < restomult >
        parte1 = self.folha()
        parte2 = self.restomult()
        return parte1 + parte2

    def restomult(self):
        # < restomult > -> * < folha > < restomult > | / < folha > < restomult > | LAMBDA
        if self.tokenLido[0] == TOKEN.multiplica:
            self.consome(TOKEN.multiplica)
            parte1 = self.folha()
            parte2 = self.restomult()
            return ' * ' + parte1 + parte2
        elif self.tokenLido[0] == TOKEN.divide:
            self.consome(TOKEN.divide)
            parte1 = self.folha()
            parte2 = self.restomult()
            return  ' / ' + parte1 + parte2
        else:
            return ''

    def folha(self):
        # <folha> -> num | ident | ( <exp> )
        if self.tokenLido[0] == TOKEN.num:
            salva = self.tokenLido[1]
            self.consome(TOKEN.num)
        elif self.tokenLido[0] == TOKEN.ident:
            salva = self.tokenLido[1]
            self.consome(TOKEN.ident)
        else:
            self.consome(TOKEN.abrePar)
            salva = self.exp()
            self.consome(TOKEN.fechaPar)
            salva = '(' + salva + ')'
        return salva

if __name__ == '__main__':
    print("Para testar, chame o Tradutor")