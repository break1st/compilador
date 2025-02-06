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
        self.declara((TOKEN.ident,'len',0,0),
                     (TOKEN.FUNCTION, [(None,True), (TOKEN.INT, False)]))
        self.declara((TOKEN.ident,'num2str',0,0),
                     (TOKEN.FUNCTION, [(TOKEN.FLOAT,False), (TOKEN.string, False)]))
        self.declara((TOKEN.ident,'str2num',0,0),
                     (TOKEN.FUNCTION, [(TOKEN.string,False), (TOKEN.FLOAT, False)]))
        self.declara((TOKEN.ident,'trunc',0,0),
                     (TOKEN.FUNCTION, [(TOKEN.FLOAT,False), (TOKEN.INT, False)]))
        self.retorno = False
        self.operacoes = {
            ((TOKEN.INT, False), TOKEN.mais, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.menos, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.multiplica, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.divide, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.porcento, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.FLOAT, False), TOKEN.mais, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.menos, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.multiplica, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.divide, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.string, False), TOKEN.mais, (TOKEN.string, False)): (TOKEN.string, False),
            ((TOKEN.INT, False), TOKEN.mais, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.INT, False), TOKEN.menos, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.INT, False), TOKEN.multiplica, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.INT, False), TOKEN.divide, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.mais, (TOKEN.INT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.menos, (TOKEN.INT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.multiplica, (TOKEN.INT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.divide, (TOKEN.INT, False)): (TOKEN.FLOAT, False),
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
            ((TOKEN.INT, False), TOKEN.OR, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.AND, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.doisPontos, (TOKEN.INT, False)): (None, True),
            ((TOKEN.INT, False), TOKEN.oprel, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.FLOAT, False), TOKEN.oprel, (TOKEN.FLOAT, False)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.oprel, (TOKEN.FLOAT, False)): (TOKEN.INT, False),
            ((TOKEN.FLOAT, False), TOKEN.oprel, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.string, False), TOKEN.oprel, (TOKEN.string, False)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.atrib, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.FLOAT, False), TOKEN.atrib, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.string, False), TOKEN.atrib, (TOKEN.string, False)): (TOKEN.string, False),
            ((TOKEN.FLOAT, False), TOKEN.atrib, (TOKEN.INT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.INT, True), TOKEN.atrib, (TOKEN.INT, True)): (TOKEN.INT, True),
            ((TOKEN.FLOAT, True), TOKEN.atrib, (TOKEN.FLOAT, True)): (TOKEN.FLOAT, True),
            ((TOKEN.string, True), TOKEN.atrib, (TOKEN.string, True)): (TOKEN.string, True),
            ((TOKEN.INT, True), TOKEN.atrib, (None, True)): (TOKEN.INT, True),
            ((TOKEN.FLOAT, True), TOKEN.atrib, (None, True)): (TOKEN.FLOAT, True),
            ((TOKEN.string, True), TOKEN.atrib, (None, True)): (TOKEN.string, True),
            ((TOKEN.FLOAT, True), TOKEN.atrib, (TOKEN.INT, True)): (TOKEN.FLOAT, True),
            ((TOKEN.INT, False), TOKEN.virg, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.FLOAT, False), TOKEN.virg, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.string, False), TOKEN.virg, (TOKEN.string, False)): (TOKEN.string, False),
            ((TOKEN.INT, False), TOKEN.virg, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.virg, (TOKEN.INT, False)): (TOKEN.FLOAT, False),
            ((None, True), TOKEN.atrib, (TOKEN.INT, True)): (TOKEN.INT, True),
            ((None, True), TOKEN.atrib, (TOKEN.FLOAT, True)): (TOKEN.FLOAT, True),
            ((None, True), TOKEN.atrib, (TOKEN.string, True)): (TOKEN.string, True),
        }

        self.tipoRetornoFuncoes = {
            (TOKEN.INT, False): ' -> int',
            (TOKEN.FLOAT, False): ' -> float',
            (TOKEN.string, False): ' -> str',
            (TOKEN.INT, True): ' -> list',
            (TOKEN.FLOAT, True): ' -> list',
            (TOKEN.string, True): ' -> list',
            (None, True): ' -> list',
            None: ' -> None',
        }

        self.funcoesNativas = {
            'len': 'len',
            'num2str': 'str',
            'str2num': 'float',
            'trunc': 'math.trunc',
        }

        self.tipos = {
            (TOKEN.INT, False): 'int',
            (TOKEN.FLOAT, False): 'float',
            (TOKEN.string, False): 'str',
            (TOKEN.INT, True): 'int [list]',
            (TOKEN.FLOAT, True): 'float [list]',
            (TOKEN.string, True): 'str [list]',
            (None, True): '[list]',
            None: 'None',
        }
        
    def finaliza(self):
        self.alvo.close()

    def erroSemantico(self, tokenAtual, msg):
        (token, lexema, linha, coluna) = tokenAtual
        print(f'Erro na linha {linha}, coluna {coluna}:')
        print(f'{msg}')
        raise Exception

    def retornoFuncao(self):
        escopo = self.tabelaSimbolos[1]
        ultimo_escopo = list(escopo.keys())[-1]
        return ultimo_escopo, escopo[ultimo_escopo][1][-1][1] if escopo[ultimo_escopo] else None

    def gera(self, nivel, codigo):
        identacao = ' ' * 3 * nivel
        linha = identacao + codigo
        self.alvo.write(linha)

    def declara(self, tokenAtual:tuple, tipo:tuple):
        """ nome = lexema do ident
            tipo = (base, lista)
            base = int | float | strig | function | None # listas genericas
            Se base in [int,float,string]
                lista = boolean # True se o tipo for lista
            else
                Lista = lista com os tipos dos argumentos, mais tipo do retorno
        """
        (token, nome, linha, coluna) = tokenAtual
        if not self.consulta(tokenAtual) is None:
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

    def iniciaFuncao(self, tokenAtual):
        self.retorno = False
        self.tabelaSimbolos = [dict()] + self.tabelaSimbolos

    def terminaFuncao(self):
        self.tabelaSimbolos = self.tabelaSimbolos[1:]
    

    def checaOperacao(self, op1, op2 = None, operacao = None):
        return self.operacoes.get((op1, operacao, op2), None)
        
    def verificaRetornoFuncao(self,token_atual, tipo_retorno):
        if self.retorno is False and tipo_retorno is not None:
            msg = f'O retorno esperado para a {token_atual[1]} é {tipo_retorno} mas foi encontrado "None"'
            self.erroSemantico(token_atual, msg)

    def verificaParametros(self, parametros_esperados, parametros_passados):

        esperados = ', '.join(self.tipos[tipo] for tipo in parametros_esperados)
        passados = ', '.join(self.tipos[tipo] for tipo in parametros_passados)

        if len(parametros_esperados) != len(parametros_passados):
            return False, (f'Era esperado {len(parametros_esperados)} parâmetro(s) - ({esperados}), '
                           f'mas veio {len(parametros_passados)} parâmetro(s) - ({passados})!')

        for tipo_esperado, tipo_passado in zip(parametros_esperados, parametros_passados):

            if tipo_esperado != tipo_passado:
                if tipo_esperado == (None, True) and tipo_passado[1] is True:
                    return True, None
                elif tipo_esperado == (TOKEN.FLOAT, False) and tipo_passado == (TOKEN.INT, False):
                    return True, None
                else:
                    return False, f'Era esperado ({esperados}), mas veio ({passados})!'

        return True, None
    
    
    def verificaMain(self):
        token_main, padrao_main = (TOKEN.FUNCTION, 'main', None, None), (TOKEN.FUNCTION, [((0, 0, 0, 0), (TOKEN.INT, False))])
        consulta = self.consulta(token_main)
        if consulta is None:
            msg = '[!] - ERRO -> Função \'main\' não declarada!'
            self.erroSemantico(token_main, msg)

        if consulta != padrao_main:
            msg = ('[!] - ERRO -> Formato incorreto para função \'main\'!\n'
                   'Formato esperado: function main() -> int')
            self.erroSemantico(token_main, msg)


