#---------------------------------------------------
# Tradutor para a linguagem CALC
#
# versao 1a (mar-2024)
#---------------------------------------------------
import inspect
from lexico import TOKEN, Lexico
from semantico import Semantico
import re

class Sintatico:

    def __init__(self, lexico):
        self.lexico = lexico
        self.identacao = 0
        self.nomeAlvo = 'alvo.py'
        self.semantico = Semantico(self.nomeAlvo)

    def traduz(self):
        self.tokenLido = self.lexico.getToken()
        try:
            self.prog()
            print('Traduzido com sucesso.')
        except Exception as e:
            print('Erro na tradução.', e)
            pass
        # self.semantico.finaliza()

    def consome(self, tokenEsperado):
        (token, lexema, linha, coluna) = self.tokenLido
        tokenAnterior = self.tokenLido
        
        # for f in inspect.stack():
        #     print(f.function)
        
        if tokenEsperado == token:
            self.tokenLido = self.lexico.getToken()
            return tokenAnterior
        else:
            msgTokenLido = TOKEN.msg(token)
            msgTokenEsperado = TOKEN.msg(tokenEsperado)
            print(f'Erro na linha {linha}, coluna {coluna}:')
            if token == TOKEN.erro:
                msg = lexema
            else:
                msg = msgTokenLido
            print(f'Era esperado {msgTokenEsperado} mas veio {msg}')
            
            raise Exception
        
    def erro(self, tokensEsperados):
        (token, lexema, linha, coluna) = self.tokenLido
        if not token in tokensEsperados:
            print(f'Erro na linha {linha}, coluna {coluna}:')
            msgTokenLido = TOKEN.msg(token)
            msgTokensEsperados = [TOKEN.msg(t) for t in tokensEsperados]
            print(f'Era esperado {msgTokensEsperados} mas veio {msgTokenLido}')
            raise Exception        

    def testaLexico(self):
        self.tokenLido = self.lexico.getToken()
        (token, lexema, linha, coluna) = self.tokenLido
        while token != TOKEN.eof:
            self.lexico.imprimeToken(self.tokenLido)
            self.tokenLido = self.lexico.getToken()
            (token, lexema, linha, coluna) = self.tokenLido

# ----------------------------------------- GRAMÁTICA -----------------------------------------
    def prog(self):
        # <prog> -> <funcao> <RestoFuncoes>
        self.gerar_codigo_inicial()
        self.funcao()
        self.restoFuncoes()
        self.semantico.verificarMain()
        self.consome(TOKEN.eof)
        self.gerar_codigo_final()
        
    def restoFuncoes(self):
        # <RestoFuncoes> -> <funcao> <RestoFuncoes> | LAMBDA
        if self.tokenLido[0] == TOKEN.FUNCTION:
            self.funcao()
            self.restoFuncoes()
        else:
            pass
        
    def funcao(self):
        # <funcao> -> function ident ( <params> ) <tipoResultado> <corpo>
        self.consome(TOKEN.FUNCTION)
        IDENT = self.consome(TOKEN.ident)
        self.consome(TOKEN.abrePar)
        ARGS, codigoUm = self.params()
        self.consome(TOKEN.fechaPar)
        RETURN, codigoDois = self.tipoResultado()
        self.semantico.declara(IDENT, (TOKEN.FUNCTION, ARGS + RETURN))
        self.semantico.iniciaFuncao()
        
        for arg in ARGS:
            (tt, (tipo, info)) = arg
            self.semantico.declara(tt, (tipo, info))
            
        codigo = 'def ' + IDENT[1] + '(self' + codigoUm + '):' + codigoDois + ':\n'
        self.semantico.gera(1, codigo)
        
        self.corpo()
        self.semantico.verificaRetorno(IDENT, RETURN[0][1])
        self.semantico.terminaFuncao()
        
    def tipoResultado(self):
        # <tipoResultado> -> LAMBDA | -> <tipo>
        if self.tokenLido[0] == TOKEN.ARROW:
            self.consome(TOKEN.ARROW)
            tipo = self.tipo()
        else:
            tipo = None
        randomToken = (0, 0, 0, 0)
        return [(randomToken, tipo)], self.semantico.tiposFuncoes[tipo]
        
    def params(self):
        # <params> -> <tipo> ident <restoParams> | LAMBDA
        if self.tokenLido[0] in [TOKEN.INT, TOKEN.string, TOKEN.FLOAT]:
            tipo = self.tipo()
            IDENT = self.consome(TOKEN.ident)
            params, codigo = self.restoParams()
            tipoArgs = [(IDENT, tipo)] + params
            return tipoArgs, ', ' + IDENT[1] + codigo
        else:
            return [], ''
        
    def restoParams(self):
        # <restoParams> -> LAMBDA | , <tipo> ident <restoParams> 
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            tipo = self.tipo()
            IDENT = self.consome(TOKEN.ident)
            tipoParam = (IDENT, tipo)
            resto, codigo = self.restoParams()
            tiposArgs = [tipoParam] + resto
            return tiposArgs, ', ' + IDENT[1] + codigo
        else:
            return [], ''
        
    def corpo(self):
        # <corpo> -> begin <declaracoes> <calculo> end
        self.consome(TOKEN.BEGIN)
        self.identacao = 2
        self.declaracoes()
        self.calculo()
        self.consome(TOKEN.END)
        self.semantico.gera(self.identacao, '\n')
        
    def declaracoes(self):
        # <declaracoes> -> <declara> <declaracoes> | LAMBDA
        if self.tokenLido[0] in [TOKEN.INT, TOKEN.string, TOKEN.FLOAT]:
            self.declara()
            self.declaracoes()
        else:
            pass
        
    def declara(self):
        # <declara> -> <tipo> <idents> ;
        tipo = self.tipo()
        salvar_idents = self.idents()
        self.consome(TOKEN.ptoVirg)

        for identificador in salvar_idents:
            self.semantico.declara(identificador, tipo)

        if tipo == (TOKEN.INT, False):
            self.gerar_codigo_declaracoes(salvar_idents, '0')
        elif tipo == (TOKEN.FLOAT, False):
            self.gerar_codigo_declaracoes(salvar_idents, '0.0')
        elif tipo == (TOKEN.string, False):
            self.gerar_codigo_declaracoes(salvar_idents, '""')
        elif tipo[1] is True:
            self.gerar_codigo_declaracoes(salvar_idents, '[]')
        
    def idents(self):
        # <idents> -> ident <restoIdents>
        IDENT = self.consome(TOKEN.ident)
        resto = self.restoIdents()
        return [IDENT] + resto
        
    def restoIdents(self):
        # <restoIdents> -> , ident <restoIdents> | LAMBDA 
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            IDENT = self.consome(TOKEN.ident)
            return [IDENT] + self.restoIdents()
        else:
            return []
        
    def tipo(self):
        # <tipo> -> string <opcLista> | int <opcLista> | float <opcLista> 
        if self.tokenLido[0] == TOKEN.string:
            self.consome(TOKEN.string)
            opcLista = self.opcLista()
            tipo = TOKEN.string
        elif self.tokenLido[0] == TOKEN.INT:
            self.consome(TOKEN.INT)
            opcLista = self.opcLista()
            tipo = TOKEN.INT
        elif self.tokenLido[0] == TOKEN.FLOAT:
            self.consome(TOKEN.FLOAT)
            opcLista = self.opcLista()
            tipo = TOKEN.FLOAT
        else:
            self.erro([TOKEN.string, TOKEN.INT, TOKEN.FLOAT])
        return tipo, opcLista
            
    def opcLista(self):
        # <opcLista> -> [ list ] | LAMBDA
        if self.tokenLido[0] == TOKEN.abreCol:
            self.consome(TOKEN.abreCol)
            self.consome(TOKEN.LIST)
            self.consome(TOKEN.fechaCol)
            return True
        else:
            return False
        
    # def p(self):
    #     self.consome(TOKEN.BEGIN)
    #     lexema = self.tokenLido[1]
    #     self.calculo()
    #     self.consome(TOKEN.END)
    #     self.consome(TOKEN.eof)

    def calculo(self):
        # <calculo> -> LAMBDA | <com> <calculo>
        entrou = False
        while self.tokenLido[0] in [TOKEN.ident, TOKEN.IF, TOKEN.WRITE, 
                                 TOKEN.READ, TOKEN.abreChave, TOKEN.WHILE, 
                                 TOKEN.FOR, TOKEN.RETURN]:
            self.com()
            entrou = True
        if not entrou:
            self.semantico.gera(self.identacao, 'pass\n')
        
    def com(self):
        # <com> -> <atrib>|<if>|<leitura>|<impressao>|<bloco>|<for>|<while>|<retorna>|<call>
        if self.tokenLido[0] == TOKEN.ident:
            IDENT = self.tokenLido
            tipoIdent = self.semantico.consulta(IDENT)
            if tipoIdent is None:
                msg = f'Variavel {IDENT[1]} nao declarada'
                self.semantico.erroSemantico(IDENT, msg)
            else:
                (tipo, info) = tipoIdent
                if tipo == TOKEN.FUNCTION:
                    _, codigo = self.call()
                    self.consome(TOKEN.ptoVirg)
                    codigo = codigo + '\n'
                    self.semantico.gera(self.identacao, codigo)
                else:
                    self.atrib()
        elif self.tokenLido[0] == TOKEN.IF:
            self.IF()
        elif self.tokenLido[0] == TOKEN.WRITE:
            self.impressao()
        elif self.tokenLido[0] == TOKEN.READ:
            self.leitura()
        elif self.tokenLido[0] == TOKEN.abreChave:
            self.bloco()
        elif self.tokenLido[0] == TOKEN.FOR:
            self.FOR()
        elif self.tokenLido[0] == TOKEN.WHILE:
            self.WHILE()
        elif self.tokenLido[0] == TOKEN.RETURN:
            self.retorna()            
        else:
            self.erro([TOKEN.ident, TOKEN.IF, TOKEN.WRITE, TOKEN.READ, TOKEN.abreChave, TOKEN.FOR, TOKEN.WHILE, TOKEN.RETURN])
            
    def retorna(self):
        # <retorna> -> return <expOpc> ;
        RETURN = self.consome(TOKEN.RETURN)
        tipoExp, codigo = self.expOpc()
        
        funcao, tipoRetorno = self.semantico.retornoFuncao()
        
        if tipoRetorno != tipoExp:
            msg = f'Funcao {funcao} - Tipo de retorno invalido. Esperado {tipoRetorno}, recebido {tipoExp}'
            self.semantico.erroSemantico(RETURN, msg)
        
        self.semantico.retorno = True
        self.consome(TOKEN.ptoVirg)
        codigo = 'return ' + codigo + '\n'
        self.semantico.gera(self.identacao, codigo)
        
    def expOpc(self):
        # <expOpc> -> LAMBDA | <exp>
        if self.tokenLido[0] in [TOKEN.INT, TOKEN.ident, 
                                 TOKEN.abrePar, TOKEN.FLOAT, 
                                 TOKEN.NOT, TOKEN.mais, 
                                 TOKEN.menos, TOKEN.string]:
            tipoExp, codigo = self.exp()
            return tipoExp, codigo
        else:
            return None, ''
        
    def WHILE(self):
        # <while> -> while ( <exp> ) <com>
        IDENT = self.consome(TOKEN.WHILE)
        self.consome(TOKEN.abrePar)
        tipoExp, codigo = self.exp()
        
        if tipoExp != (TOKEN.INT, False):
            msg = f'ERROR: While esperava parametro inteiro, mas recebeu {tipoExp}'
            self.semantico.erroSemantico(IDENT, msg)
        
        self.consome(TOKEN.fechaPar)
        codigo = 'while ' + codigo + ':\n'
        self.semantico.gera(self.identacao, codigo)
        self.identacao = self.identacao + 1
        self.com()
        self.identacao = self.identacao - 1
        
    def FOR(self):
        # <for> -> for ident in <range> do <com>
        self.consome(TOKEN.FOR)
        if self.semantico.consulta(self.tokenLido) is not None:
            IDENT = self.consome(TOKEN.ident)
            tipoIdent = self.semantico.consulta(IDENT)
            self.consome(TOKEN.IN)
            tipoRange, codigo = self.range()
            
            if tipoIdent[0] != tipoRange[0] and tipoRange[1] is True:
                msg = f'ERROR: Variavel {IDENT[1]} e range de tipos diferentes'
                self.semantico.erroSemantico(IDENT, msg)
            elif tipoIdent != (TOKEN.INT, False) and tipoRange == (TOKEN.INT, False):
                msg = f'ERROR: Variavel {IDENT[1]} deve ser do tipo inteiro'
                self.semantico.erroSemantico(IDENT, msg)
            
            self.consome(TOKEN.DO)
            codigo = 'for ' + IDENT[1] + ' in ' + codigo + ':\n'
            self.semantico.gera(self.identacao, codigo)
            self.identacao = self.identacao + 1
            self.com()
            self.identacao = self.identacao - 1
        else:
            msg = f'ERROR: Variavel {self.tokenLido[1]} nao declarada'
            self.semantico.erroSemantico(self.tokenLido, msg)
        
    def range(self):
        # <range> -> <lista> | range ( <exp> , <exp> <opcRange> )
        if self.tokenLido[0] == TOKEN.RANGE:
            IDENT = self.consome(TOKEN.RANGE)
            self.consome(TOKEN.abrePar)
            tipoExp, codigo = self.exp()
            
            if tipoExp != (TOKEN.INT, False):
                msg = 'O primeiro parametro deve ser um inteiro'
                self.semantico.erroSemantico(tipoExp, msg)
            self.consome(TOKEN.virg)
            
            tipoExp2, codigo2 = self.exp()
            if tipoExp2 != (TOKEN.INT, False):
                msg = 'O segundo parametro deve ser um inteiro'
                self.semantico.erroSemantico(tipoExp2, msg)
            
            tipoOpcRange, codigo3 = self.opcRange()
            if tipoOpcRange != (TOKEN.INT, False) and tipoOpcRange is not None:
                msg = 'O terceiro parametro deve ser um inteiro'
                self.semantico.erroSemantico(tipoOpcRange, msg)
                
            self.consome(TOKEN.fechaPar)
            codigo = 'range(' + codigo + ', ' + codigo2 + codigo3 + ')'
            return (TOKEN.INT, False), codigo
        else:
            tipoLista, codigo = self.lista()
            return tipoLista, codigo
            
    def lista(self):
        # <lista> -> ident <opcIndice> | [ <elemLista> ] 
        if self.tokenLido[0] == TOKEN.ident:
            IDENT = self.tokenLido
            tipoIdent = self.semantico.consulta(IDENT)
            if tipoIdent is None:
                msg = f'Variavel {IDENT[1]} nao declarada'
                self.semantico.erroSemantico(IDENT, msg)
            else:
                self.consome(TOKEN.ident)
                tipoOpcIndice, codigo = self.opcIndice(tipoIdent)
                return tipoOpcIndice, IDENT[1] + codigo
        else:
            IDENT = self.consome(TOKEN.abreCol)
            tipoElemLista, codigo = self.elemLista()
            if tipoElemLista is None:
                msg = f'ERROR: Lista deve conter elementos do mesmo tipo'
                self.semantico.erroSemantico(IDENT, msg)
            self.consome(TOKEN.fechaCol)
            return tipoElemLista, '[' + codigo + ']'
            
    def elemLista(self):
        # <elemLista> -> LAMBDA | <elem> <restoElemLista>
        if self.tokenLido[0] in [TOKEN.intVal, TOKEN.ident, TOKEN.stringVal, TOKEN.floatVal]:
                tipoElem, codigo = self.elem()
                tipoRestoElem, codigo2 = self.restoElemLista(tipoElem)
                if tipoRestoElem is not None:
                    tipoRestoElem = (tipoRestoElem[0], True)
                return tipoRestoElem, codigo + codigo2
        else:
            return (None, True), ''
        
    def restoElemLista(self, tipo):
        # <restoElemLista> -> LAMBDA | , <elem> <restoElemLista>
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            tipoElem, codigo = self.elem()
            tipoElem = self.semantico.checarOperacao(tipo, tipoElem, TOKEN.virg)
            tipoRestoElem, codigo2 = self.restoElemLista(tipoElem)
            return tipoRestoElem, ', ' + codigo + codigo2
        else:
            return tipo, ''
        
    def elem(self):
        # <elem> -> intVal | floatVal | strVal | ident 
        if self.tokenLido[0] == TOKEN.intVal:
            codigo = self.tokenLido[1]
            self.consome(TOKEN.intVal)
            return (TOKEN.INT, False), codigo
        elif self.tokenLido[0] == TOKEN.floatVal:
            codigo = self.tokenLido[1]
            self.consome(TOKEN.floatVal)
            return (TOKEN.FLOAT, False), codigo
        elif self.tokenLido[0] == TOKEN.stringVal:
            codigo = self.tokenLido[1]
            self.consome(TOKEN.stringVal)
            return (TOKEN.string, False), codigo
        elif self.tokenLido[0] == TOKEN.ident:
            if self.semantico.consulta(self.tokenLido) is not None:
                IDENT = self.consome(TOKEN.ident)
                tipoIdent = self.semantico.consulta(IDENT)
                return tipoIdent, IDENT[1]
            else:
                msg = f'ERROR: Variavel {self.tokenLido[1]} nao declarada'
                self.semantico.erroSemantico(self.tokenLido, msg)
        
    def opcRange(self):
        # <opcRange> -> , <exp> | LAMBDA
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            tipoExp, codigo = self.exp()
            return tipoExp, ', ' + codigo
        else:
            return None, ''
        
    def atrib(self):
        # <atrib> -> ident <opcIndice> = <exp> ;
        if self.semantico.consulta(self.tokenLido) is None:
            msg = f'ERROR: Variavel {self.tokenLido[1]} nao declarada'
            self.semantico.erroSemantico(self.tokenLido, msg)
        else:
            IDENT = self.consome(TOKEN.ident)
            tipoIdent = self.semantico.consulta(IDENT)
            tipoOpcIndice, codigo = self.opcIndice(tipoIdent)
            
            self.consome(TOKEN.atrib)
            tipoExp, codigo2 = self.exp()
            
            if self.semantico.checarOperacao(tipoOpcIndice, tipoExp, TOKEN.atrib) is None:
                msg = f'ERROR: Atribuicao invalida'
                self.semantico.erroSemantico(IDENT, msg)
            
            self.consome(TOKEN.ptoVirg)
            codigo = IDENT[1] + codigo + ' = ' + codigo2 + '\n'
            self.semantico.gera(self.identacao, codigo)
        
    def IF(self):
        # <if> -> if ( <exp> ) then <com> <else_opc>
        IDENT = self.consome(TOKEN.IF)
        self.consome(TOKEN.abrePar)
        tipoExp, codigo = self.exp()
        
        if tipoExp != (TOKEN.INT, False):
            msg = f'ERROR: If esperava parametro inteiro, mas recebeu {tipoExp}'
            self.semantico.erroSemantico(IDENT, msg)
            
        self.consome(TOKEN.fechaPar)
        codigo = 'if ' + codigo + ':\n'
        self.semantico.gera(self.identacao, codigo)
        self.consome(TOKEN.THEN)
        self.identacao = self.identacao + 1
        self.com()
        self.identacao = self.identacao - 1
        self.elseOpc()
        
    def elseOpc(self):
        # <else_opc> -> LAMBDA | else <com>
        if self.tokenLido[0] == TOKEN.ELSE:
            self.consome(TOKEN.ELSE)
            codigo = 'else:\n'
            self.semantico.gera(self.identacao, codigo)
            self.identacao = self.identacao + 1
            self.com()
            self.identacao = self.identacao - 1
        else:
            pass
        
    def leitura(self):
        # <leitura> -> read ( string, ident );
        IDENT = self.consome(TOKEN.READ)
        self.consome(TOKEN.abrePar)
        tipoExp, codigo = self.exp()
        
        if tipoExp != (TOKEN.string, False):
            msg = f'ERROR: Read esperava parametro string, mas recebeu {tipoExp}'
            self.semantico.erroSemantico(IDENT, msg)
            
        self.consome(TOKEN.virg)
        tipoIdent = self.semantico.consulta(self.tokenLido)
        salvarIdent = self.tokenLido[1]
        
        if tipoIdent is None:
            msg = f'ERROR: Variavel {self.tokenLido[1]} nao declarada'
            self.semantico.erroSemantico(self.tokenLido, msg)
        else:
            self.consome(TOKEN.ident)
        self.consome(TOKEN.fechaPar)
        self.consome(TOKEN.ptoVirg)
        
        if tipoIdent[1] is True:
            msg = f'ERROR: Variavel {salvarIdent} e do tipo lista'
            self.semantico.erroSemantico(IDENT, msg)
            
        tipoInput = self.semantico.tipos[tipoIdent]
        codigo = salvarIdent + ' = ' + tipoInput + '(input(' + codigo + '))\n'
        self.semantico.gera(self.identacao, codigo)
        
    def impressao(self):
        # <impressao> -> write ( <lista_out> );
        self.consome(TOKEN.WRITE)
        self.consome(TOKEN.abrePar)
        args, codigo = self.listaOut()
        self.consome(TOKEN.fechaPar)
        self.consome(TOKEN.ptoVirg)
        codigo = 'print(' + codigo + ')\n'
        self.semantico.gera(self.identacao, codigo)
        
    def listaOuts(self):
        # <lista_outs> -> <out> <restoLista_outs>
        args, codigo = self.out()
        restoArgs, restoCodigo = self.restoListaOuts()
        return [args] + restoArgs, codigo + restoCodigo
    
    def restoListaOuts(self):
        # <restoLista_outs> -> LAMBDA | , <out> <restoLista_outs>
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            arg, codigo = self.out()
            restoArgs, restoCodigo = self.restoListaOuts()
            return [arg] + restoArgs, ', ' + codigo + restoCodigo
        else:
            return [], ''
        
    def out(self):
        # <out> -> <folha>
        tipo, codigo = self.folha()
        return tipo, codigo
        
    def bloco(self):
        # <bloco> -> { <calculo> }
        self.consome(TOKEN.abreChave)
        self.calculo()
        self.consome(TOKEN.fechaChave)
    
    def exp(self):
        # <exp> -> <disj>
        tipo, codigo = self.disj()
        return tipo, codigo
        
    def disj(self):
        # <disj> -> <conj> <restodisj>
        tipo, codigo = self.conj()
        tipoRestoDisj, codigo2 = self.restoDisj(tipo)
        return tipoRestoDisj, codigo + codigo2
        
    def restoDisj(self, tipo):
       # <restoDisj> -> LAMBDA | or <conj> <restoDisj>
       if self.tokenLido[0] == TOKEN.OR:
           self.consome(TOKEN.OR)
           tipoConj, codigo = self.conj()
           tipoAux = self.semantico.checarOperacao(tipo, tipoConj, TOKEN.OR)
           tipoRestoDisj, codigo2 = self.restoDisj(tipoAux)
           return tipoRestoDisj, ' or ' + codigo + codigo2
       else:
           return tipo, ''

    def conj(self):
        # <conj> -> <nao> <restoConj>
        tipo, codigo = self.nao()
        tipoRestoConj, codigo2 = self.restoConj(tipo)
        return tipoRestoConj, codigo + codigo2
        
    def restoConj(self, tipo):
       # <restoDisj> -> LAMBDA | and <nao> <restoConj>
        if self.tokenLido[0] == TOKEN.AND:
            self.consome(TOKEN.AND)
            tipoNao, codigo = self.nao()
            tipoAux = self.semantico.checarOperacao(tipo, tipoNao, TOKEN.AND)
            tipoRestoConj, codigo2 = self.restoConj(tipoAux)
            return tipoRestoConj, ' and ' + codigo + codigo2
        else:
            return tipo, ''
        
    def nao(self):
        # <nao> -> not <nao> | <rel>
        if self.tokenLido[0] == TOKEN.NOT:
            self.consome(TOKEN.NOT)
            tipo, codigo = self.nao()
            return tipo, 'not ' + codigo
        else:
            tipo, codigo = self.rel()
            return tipo, codigo
            
    def rel(self):
        # <rel> -> <soma> <restoRel>
        tipo, codigo = self.soma()
        tipoResto, codigo2 = self.restoRel(tipo)
        return tipoResto, codigo + codigo2
        
    def restoRel(self, tipo):
        # <restoRel> -> LAMBDA | oprel <soma>
        if self.tokenLido[0] == TOKEN.oprel:
            salvarOprel = self.consome(TOKEN.oprel)
            tipoSoma, codigo = self.soma()
            tipoAux = self.semantico.checarOperacao(tipo, tipoSoma, TOKEN.oprel)
            # TODO
            return tipoAux, ' ' + salvarOprel[1] + ' ' + codigo
        else:
            return tipo, ''
    
    def soma(self):
        # <soma> -> <mult> <restoSoma>
        tipoMult, codigo1 = self.mult()
        tipoRestoMult, codigo2 = self.restoSoma(tipoMult)
        return tipoRestoMult, codigo1 + codigo2
        
    def restoSoma(self, tipo):
        # <restoSoma> -> LAMBDA | + <mult> <restoSoma> | - <mult> <restoSoma>
        if self.tokenLido[0] == TOKEN.mais:
            self.consome(TOKEN.mais)
            tipoMult, codigo = self.mult()
            tipoAux = self.semantico.checarOperacao(tipo, tipoMult, TOKEN.mais)
            tipoRestoSoma, codigo2 = self.restoSoma(tipoAux)
            return tipoRestoSoma, ' + ' + codigo + codigo2
        elif self.tokenLido[0] == TOKEN.menos:
            self.consome(TOKEN.menos)
            tipoMult, codigo = self.mult()
            tipoAux = self.semantico.checarOperacao(tipo, tipoMult, TOKEN.menos)
            tipoRestoSoma, codigo2 = self.restoSoma(tipoAux)
            return tipoRestoSoma, ' - ' + codigo + codigo2
        else:
            return tipo, ''
        
    def mult(self):
        # <mult> -> <uno> <restoMult>
        tipo, codigo = self.uno()
        tipoRestoMult, codigo2 = self.restoMult(tipo)
        return tipoRestoMult, codigo + codigo2
        
    def restoMult(self, tipo):
        # <restoMult> -> <restoMult> -> LAMBDA | / <uno> <restoMult> | * <uno> <restoMult> | % <uno> <restoMult>
        if self.tokenLido[0] == TOKEN.divide:
            self.consome(TOKEN.divide)
            tipoUno, codigo = self.uno()
            tipoAux = self.semantico.checarOperacao(tipo, tipoUno, TOKEN.divide)
            tipoRestoMult, codigo2 = self.restoMult(tipoAux)
            return tipoRestoMult, ' / ' + codigo + codigo2
        elif self.tokenLido[0] == TOKEN.multiplica:
            self.consome(TOKEN.multiplica)
            tipoUno, codigo = self.uno()
            tipoAux = self.semantico.checarOperacao(tipo, tipoUno, TOKEN.multiplica)
            tipoRestoMult, codigo2 = self.restoMult(tipoAux)
            return tipoRestoMult, ' * ' + codigo + codigo2
        elif self.tokenLido[0] == TOKEN.porcento:
            self.consome(TOKEN.porcento)
            tipoUno, codigo = self.uno()
            tipoAux = self.semantico.checarOperacao(tipo, tipoUno, TOKEN.porcento)
            tipoRestoMult, codigo2 = self.restoMult(tipoAux)
            return tipoRestoMult, ' % ' + codigo + codigo2
        else:
            return tipo, ''
        
    def uno(self):
        # <uno> -> + <uno> | - <uno> | <folha>
        if self.tokenLido[0] == TOKEN.mais:
            self.consome(TOKEN.mais)
            tipoUno, codigo = self.uno()
            return tipoUno, ' + ' + codigo
        elif self.tokenLido[0] == TOKEN.menos:
            self.consome(TOKEN.menos)
            tipoUno, codigo = self.uno()
            return tipoUno, ' - ' + codigo
        else:
            tipo, codigo = self.folha()
            return tipo, codigo
            
    def folha(self):
        #<folha> -> intVal | floatVal | strVal | <call> | <lista> | ( <exp> ) 
        if self.tokenLido[0] == TOKEN.intVal:
            codigo = self.consome(TOKEN.intVal)
            return (TOKEN.INT, False), codigo
        elif self.tokenLido[0] == TOKEN.floatVal:
            codigo = self.consome(TOKEN.floatVal)
            return (TOKEN.FLOAT, False), codigo
        elif self.tokenLido[0] == TOKEN.stringVal:
            codigo = self.consome(TOKEN.stringVal)
            return (TOKEN.string, False), codigo
        elif self.tokenLido[0] == TOKEN.ident or self.tokenLido[0] == TOKEN.abreCol:
            tokenLido = self.tokenLido
            result = self.semantico.consulta(tokenLido)
            if tokenLido[0] == TOKEN.abreCol:
                tipoLista, codigo = self.lista()
                return tipoLista, codigo
            elif result is None:
                msg = f"Variavel {tokenLido[1]} nao declarada"
                self.semantico.erroSemantico(tokenLido, msg)
            else:
                (tipo, info) = result
                if tipo == TOKEN.FUNCTION:
                    tipoCall, codigo = self.call()
                    return tipoCall, codigo
                else:
                    tipoLista, codigo = self.lista()
                    return tipoLista, codigo
        else:
            self.consome(TOKEN.abrePar)
            tipoExp, codigo = self.exp()
            self.consome(TOKEN.fechaPar)
            return tipoExp, '(' + codigo + ')'
            
    def call(self):
        # <call> -> ident ( <lista_outs_opc> )
        salvarFunction = self.tokenLido
        self.consome(TOKEN.ident)
        self.consome(TOKEN.abrePar)
        args, codigo = self.listaOutsOpc()
        self.consome(TOKEN.fechaPar)
        argsFunction = self.semantico.consulta(salvarFunction)
        
        if salvarFunction[1] in ['trunc', 'len', 'str2num', 'num2str']:
            infos = argsFunction[1][:-1]
            params, msgAux = self.semantico.verificarParametros(infos, args)
            
            if params is False:
                msg = f'ERROR: Funcao {salvarFunction[1]} recebeu parametros invalidos'
                self.semantico.erroSemantico(salvarFunction, msg)
                
            codigoFunction = self.semantico.funcoesNativas[salvarFunction[1]]
            
            retorno = argsFunction[1][-1]
            return retorno, codigoFunction + '(' + codigo + ')'
        else:
            infos = [arg[1] for arg in argsFunction[1][:-1]]
            params, msgAux = self.semantico.verificarParametros(infos, args)
            
            if params is False:
                msg = f'ERROR: Funcao {salvarFunction[1]} recebeu parametros invalidos'
                self.semantico.erroSemantico(salvarFunction, msg)
            
            retorno = argsFunction[1][-1][-1]
            return retorno, 'self.' + salvarFunction[1] + '(' + codigo + ')'
        
    def opcIndice(self, tipo):
        # <opcIndice> -> LAMBDA | [ <exp> <restoElem> ]
        if self.tokenLido[0] == TOKEN.abreCol:
            
            if tipo[1] is not True:
                msg = f'ERROR: Variavel {self.tokenLido[1]} nao e uma lista'
                self.semantico.erroSemantico(self.tokenLido, msg)
                
            salvarToken = self.tokenLido            
            self.consome(TOKEN.abreCol)
            tipoExp, codigo = self.exp()
            
            if tipoExp != (TOKEN.INT, False):
                msg = f'ERROR: Indice de lista deve ser do tipo inteiro'
                self.semantico.erroSemantico(salvarToken, msg)
                
            tipoRestoElem, codigo2 = self.restoElem(tipoExp)
            
            if tipoRestoElem != (TOKEN.INT, False) and tipoRestoElem != (None, True):
                msg = f'ERROR: Indice de lista deve ser do tipo inteiro'
                self.semantico.erroSemantico(salvarToken, msg)
            
            if tipoRestoElem == (None, True):
                tipoRestoElem = (tipo[0], True)
            else:
                tipoRestoElem = (tipo[0], False)
            
            self.consome(TOKEN.fechaCol)
            return tipoRestoElem, '[' + codigo + codigo2 + ']'
        else:
            return tipo, ''
        
    def restoElem(self, tipo):
        # <restoElem> -> LAMBDA | : <exp>
        if self.tokenLido[0] == TOKEN.doisPontos:
            self.consome(TOKEN.doisPontos)
            tipoExp, codigo = self.exp()
            tipoAux = self.semantico.checarOperacao(tipo, tipoExp, TOKEN.doisPontos)
            return tipoAux, ': ' + codigo
        else:
            return tipo, ''
        
    def listaOutsOpc(self):
        # <lista_outs_opc> -> <lista_outs> | LAMBDA
        if self.tokenLido[0] in [TOKEN.intVal, TOKEN.floatVal, TOKEN.stringVal, TOKEN.ident, TOKEN.abrePar]:
            args, codigo = self.listaOuts()
            return args, codigo
        else:
            return [], ''
        
# ------------------------------------------------ GERAÇÃO DE CÓDIGO ------------------------------------------------ #

    def verificar_import_math(self):
        fonte = re.sub(r'#.*', '', self.lexico.fonte)
        pattern = r'(?<=\s|[+\-*/%=<>,;!():])trunc\('  # Expressão Regular que controla o import math (math.trunc())
        return 'import math\n\n\n' if re.findall(pattern, fonte) else ''

    def gerar_codigo_inicial(self):
        codigo_inicial = self.verificar_import_math()

        codigo_inicial += \
            'class ' + 'Program' + ':\n' + \
            '    def __init__(self):\n' + \
            '        pass\n\n'
        self.semantico.gera(0, codigo_inicial)

    def gerar_codigo_final(self):
        codigo_final = \
            '\nif __name__ == \'__main__\':\n' + \
            '    prog = ' + 'Program' + '()\n' + \
            '    prog.main()\n'
        self.semantico.gera(0, codigo_final)

    def gerar_codigo_declaracoes(self, idents, atrib):
        codigo_1, codigo_2 = '', ' = '
        for identificador in idents:
            codigo_1 += identificador[1] + ', '
            codigo_2 += atrib + ', '
        codigo = codigo_1[:-2] + codigo_2[:-2] + '\n'
        self.semantico.gera(self.identacao, codigo)

        
if __name__ == '__main__':
    print("Para testar, chame o Tradutor")