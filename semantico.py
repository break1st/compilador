# ---------------------------------------------------
# Tradutor para a linguagem B-A-BA plus
#
# versao 2a (28/nov/2024)
# ---------------------------------------------------
from ttoken import TOKEN

class Semantico:

    def __init__(self, nomeAlvo):
        self.tabelaSimbolos = list()
        self.tabelaSimbolos = [dict()] + self.tabelaSimbolos
        self.alvo = open(nomeAlvo, "wt")
        
        self.declara((TOKEN.ident, 'len', None, None),
                     (TOKEN.FUNCTION, [(None,True), (TOKEN.INT, False)]))
        self.declara((TOKEN.ident, 'num2str', None, None),
                     (TOKEN.FUNCTION, [(TOKEN.FLOAT,False), (TOKEN.string, False)]))
        self.declara((TOKEN.ident, 'str2num', None, None),
                     (TOKEN.FUNCTION, [(TOKEN.string,False), (TOKEN.FLOAT, False)]))
        self.declara((TOKEN.ident, 'trunc', None, None),
                     (TOKEN.FUNCTION, [(TOKEN.FLOAT,False), (TOKEN.INT, False)]))
        
        self.retorno = False
        
        self.tipos = {
            (TOKEN.INT, False): 'int',
            (TOKEN.FLOAT, False): 'float',
            (TOKEN.string, False): 'str',
            (TOKEN.INT, True): 'int [list]',
            (TOKEN.FLOAT, True): 'float [list]',
            (TOKEN.string, True): 'str [list]',
            (None, True): '[list]',
            None: 'None'
        }
        
        self.tiposFuncoes = {
            (TOKEN.INT, False): ' -> int',
            (TOKEN.FLOAT, False): ' -> float',
            (TOKEN.string, False): ' -> str',
            (TOKEN.INT, True): ' -> list ',
            (TOKEN.FLOAT, True): ' -> list ',
            (TOKEN.string, True): ' -> list ',
            (None, True): ' -> list ',
            None: ' -> None'
        }
        
        self.funcoesNativas = {
            'trunc': 'math.trunc',
            'len': 'len',
            'str2num': 'float',
            'num2str': 'str'
        }
        
        self.operacoes = {
            # int - int
            ((TOKEN.INT, False), TOKEN.mais, (TOKEN.INT)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.menos, (TOKEN.INT)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.multiplica, (TOKEN.INT)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.divide, (TOKEN.INT)): (TOKEN.INT, False),
            
            # int - float
            ((TOKEN.INT, False), TOKEN.mais, (TOKEN.FLOAT)): (TOKEN.FLOAT, False),
            ((TOKEN.INT, False), TOKEN.menos, (TOKEN.FLOAT)): (TOKEN.FLOAT, False),
            ((TOKEN.INT, False), TOKEN.multiplica, (TOKEN.FLOAT)): (TOKEN.FLOAT, False),
            ((TOKEN.INT, False), TOKEN.divide, (TOKEN.FLOAT)): (TOKEN.FLOAT, False),
            
            # float - float
            ((TOKEN.FLOAT, False), TOKEN.mais, (TOKEN.FLOAT)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.menos, (TOKEN.FLOAT)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.multiplica, (TOKEN.FLOAT)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.divide, (TOKEN.FLOAT)): (TOKEN.FLOAT, False),
            
            # float - int
            ((TOKEN.FLOAT, False), TOKEN.mais, (TOKEN.INT)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.menos, (TOKEN.INT)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.multiplica, (TOKEN.INT)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.divide, (TOKEN.INT)): (TOKEN.FLOAT, False),
            
            # operacao listas
            ((TOKEN.INT, True), TOKEN.mais, (TOKEN.INT, True)): (TOKEN.INT, True),
            ((TOKEN.FLOAT, True), TOKEN.mais, (TOKEN.FLOAT, True)): (TOKEN.FLOAT, True),
            ((TOKEN.string, True), TOKEN.mais, (TOKEN.string, True)): (TOKEN.string, True),
            ((TOKEN.INT, True), TOKEN.mais, (TOKEN.FLOAT, True)): (TOKEN.FLOAT, True),
            ((TOKEN.FLOAT, True), TOKEN.mais, (TOKEN.INT, True)): (TOKEN.FLOAT, True),
            ((TOKEN.INT, True), TOKEN.mais, (None, True)): (TOKEN.INT, True),
            ((TOKEN.FLOAT, True), TOKEN.mais, (None, True)): (TOKEN.FLOAT, True),
            ((TOKEN.string, True), TOKEN.mais, (None, True)): (TOKEN.string, True),
            ((None, True), TOKEN.mais, (TOKEN.INT, True)): (TOKEN.INT, True),
            ((None, True), TOKEN.mais, (TOKEN.FLOAT, True)): (TOKEN.FLOAT, True),
            ((None, True), TOKEN.mais, (TOKEN.string, True)): (TOKEN.string, True),
            
            # # lista: int - int
            # ((TOKEN.INT, True), TOKEN.mais, (TOKEN.INT)): (TOKEN.INT, True),
            # ((TOKEN.INT, True), TOKEN.menos, (TOKEN.INT)): (TOKEN.INT, True),
            # ((TOKEN.INT, True), TOKEN.multiplica, (TOKEN.INT)): (TOKEN.INT, True),
            # ((TOKEN.INT, True), TOKEN.divide, (TOKEN.INT)): (TOKEN.INT, True),
            
            # # lista: int - float
            # ((TOKEN.INT, True), TOKEN.mais, (TOKEN.FLOAT)): (TOKEN.FLOAT, True),
            # ((TOKEN.INT, True), TOKEN.menos, (TOKEN.FLOAT)): (TOKEN.FLOAT, True),
            # ((TOKEN.INT, True), TOKEN.multiplica, (TOKEN.FLOAT)): (TOKEN.FLOAT, True),
            # ((TOKEN.INT, True), TOKEN.divide, (TOKEN.FLOAT)): (TOKEN.FLOAT, True),
            
            # # lista: float - float
            # ((TOKEN.FLOAT, True), TOKEN.mais, (TOKEN.FLOAT)): (TOKEN.FLOAT, True),
            # ((TOKEN.FLOAT, True), TOKEN.menos, (TOKEN.FLOAT)): (TOKEN.FLOAT, True),
            # ((TOKEN.FLOAT, True), TOKEN.multiplica, (TOKEN.FLOAT)): (TOKEN.FLOAT, True),
            # ((TOKEN.FLOAT, True), TOKEN.divide, (TOKEN.FLOAT)): (TOKEN.FLOAT, True),
            
            # # lista: float - int
            # ((TOKEN.FLOAT, True), TOKEN.mais, (TOKEN.INT)): (TOKEN.FLOAT, True),
            # ((TOKEN.FLOAT, True), TOKEN.menos, (TOKEN.INT)): (TOKEN.FLOAT, True),
            # ((TOKEN.FLOAT, True), TOKEN.multiplica, (TOKEN.INT)): (TOKEN.FLOAT, True),
            # ((TOKEN.FLOAT, True), TOKEN.divide, (TOKEN.INT)): (TOKEN.FLOAT, True),            
            
            # string - string
            ((TOKEN.string, False), TOKEN.mais, (TOKEN.string, False)): (TOKEN.string, False),
            
            # operador logico
            ((TOKEN.INT, False), TOKEN.OR, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.AND, (TOKEN.INT, False)): (TOKEN.INT, False),
            
            # operacao com dois pontos -> sub-lista
            ((TOKEN.INT, False), TOKEN.doisPontos, (TOKEN.INT, False)): (None, True),
            
            # operacoes relacionais (<, <=, ==, !=, >, >=)
            ((TOKEN.INT, False), TOKEN.oprel, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.FLOAT, False), TOKEN.oprel, (TOKEN.FLOAT, False)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.oprel, (TOKEN.FLOAT, False)): (TOKEN.INT, False),
            ((TOKEN.FLOAT, False), TOKEN.oprel, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.string, False), TOKEN.oprel, (TOKEN.string, False)): (TOKEN.INT, False),

            # operacoes atribuicao
            ((TOKEN.INT, False), TOKEN.atrib, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.FLOAT, False), TOKEN.atrib, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.string, False), TOKEN.atrib, (TOKEN.string, False)): (TOKEN.string, False),
            ((TOKEN.FLOAT, False), TOKEN.atrib, (TOKEN.INT, False)): (TOKEN.FLOAT, False),

            # lista: operacoes atribuicao
            ((TOKEN.INT, True), TOKEN.atrib, (TOKEN.INT, True)): (TOKEN.INT, True),
            ((TOKEN.FLOAT, True), TOKEN.atrib, (TOKEN.FLOAT, True)): (TOKEN.FLOAT, True),
            ((TOKEN.string, True), TOKEN.atrib, (TOKEN.string, True)): (TOKEN.string, True),
            ((TOKEN.INT, True), TOKEN.atrib, (None, True)): (TOKEN.INT, True),
            ((TOKEN.FLOAT, True), TOKEN.atrib, (None, True)): (TOKEN.FLOAT, True),
            ((TOKEN.string, True), TOKEN.atrib, (None, True)): (TOKEN.string, True),
            ((TOKEN.FLOAT, True), TOKEN.atrib, (TOKEN.INT, True)): (TOKEN.FLOAT, True),

            # operacoes verificar tipos iguais
            ((TOKEN.INT, False), TOKEN.virg, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.FLOAT, False), TOKEN.virg, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.string, False), TOKEN.virg, (TOKEN.string, False)): (TOKEN.string, False),
            ((TOKEN.INT, False), TOKEN.virg, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.virg, (TOKEN.INT, False)): (TOKEN.FLOAT, False),
        }

    def finaliza(self):
        self.alvo.close()

    def erroSemantico(self, tokenAtual, msg):
        (token, lexema, linha, coluna) = tokenAtual
        print(f'Erro na linha {linha}, coluna {coluna}:')
        print(f'{msg}')
        raise Exception

    def gera(self, nivel, codigo):
        identacao = ' ' * 4 * nivel
        linha = identacao + codigo
        self.alvo.write(linha)

    def declara(self, tokenAtual, tipo):
        (token, nome, linha, coluna) = tokenAtual
        if self.consulta(tokenAtual) is not None:
            msg = f'Variavel {nome} redeclarada'
            self.erroSemantico(tokenAtual, msg)
        else:
            escopo = self.tabelaSimbolos[0]
            escopo[nome] = tipo

    def consulta(self, tokenAtual):
        (token, nome, linha, coluna) = tokenAtual
        for escopo in self.tabelaSimbolos:
            if nome in escopo:
                return escopo[nome]
        return None        

    def iniciaFuncao(self):
        self.retorno = False
        self.tabelaSimbolos = [dict()] + self.tabelaSimbolos

    def terminaFuncao(self):
        self.tabelaSimbolos = self.tabelaSimbolos[1:]

    def checarOperacao(self, op1, op2, operador):
        if (op1, operador, op2) in self.operacoes:
            return self.operacoes[(op1, operador, op2)]
        else:
            return None
        
    def retornoFuncao(self):
        escopo = self.tabelaSimbolos[0]
        ultimo = list(escopo.keys())[-1]
        tipoRetorno = escopo[ultimo][1][-1][1] if escopo[ultimo] else None
        return ultimo, tipoRetorno
    
    def verificarParametros(self, parametrosEsperados, parametrosPassados):
        def formatarTipos(parametros):
            return ', '.join(self.tipos[tipo] for tipo in parametros)

        tipos_esperados = formatarTipos(parametrosEsperados)
        tipos_passados = formatarTipos(parametrosPassados)

        if len(parametrosEsperados) != len(parametrosPassados):
            mensagem = (
                f"Era esperado {len(parametrosEsperados)} parâmetro(s) - ({tipos_esperados}), "
                f"mas veio {len(parametrosPassados)} parâmetro(s) - ({tipos_passados})!"
            )
            return False, mensagem

        for tipo_esperado, tipo_passado in zip(parametrosEsperados, parametrosPassados):
            if tipo_esperado == tipo_passado:
                continue

            if tipo_esperado == (None, True) and tipo_passado[1] is True:
                continue

            if tipo_esperado == (TOKEN.FLOAT, False) and tipo_passado == (TOKEN.INT, False):
                continue

            return False, f"Era esperado ({tipos_esperados}), mas veio ({tipos_passados})!"

        return True, None
    
    def verificaRetorno(self, tokenFuncao, tipoRetorno):
        if self.retorno is False and tipoRetorno is not None:
            msg = f'Função {tokenFuncao[1]} não retornou valor. Deveria retornar {self.tipos[tipoRetorno]}.'
            self.erroSemantico(tokenFuncao, msg)
            
    def imprimirEscopo(self, escopo):
        print()
        for chave, valor in self.tabelaSimbolos[0].items():
            print(f'Escopo {chave} -> {chave}, {valor}')
            
    def verificarMain(self):
        tokenMain, padraoMain = (TOKEN.FUNCTION, 'main', None, None), (TOKEN.FUNCTION, [((0, 0, 0, 0), (TOKEN.INT, False))])
        consulta = self.consulta(tokenMain)
        if consulta is None:
            self.erroSemantico(tokenMain, 'Função main não declarada.')
        
        if consulta != padraoMain:
            self.erroSemantico(tokenMain, 'Função main não está no padrão correto.')
            