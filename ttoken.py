#---------------------------------------------------
# Tradutor para a linguagem CALC
#
# versao 1a (mar-2024)
#---------------------------------------------------

from enum import IntEnum
class TOKEN(IntEnum):
    erro = 1
    eof = 2
    ident = 3
    num = 4
    string = 5
    IF = 6
    ELSE = 7
    WHILE = 8
    BEGIN = 9
    END = 10
    PROGRAM = 11
    abrePar = 12
    fechaPar = 13
    virg = 14
    ptoVirg = 15
    pto = 16
    FOR = 17
    oprel = 19
    porcento = 20
    doisPontos = 21
    AND = 23
    OR = 24
    NOT = 25
    mais = 26
    menos = 27
    multiplica = 28
    divide = 29
    READ = 30
    WRITE = 31
    VAR = 32
    abreChave = 33
    fechaChave = 34
    atrib = 35
    THEN = 36
    FUNCTION = 37
    ARROW = 38
    INT = 39
    FLOAT = 40
    abreCol = 41
    fechaCol = 42
    LIST = 43
    RETURN = 44
    DO = 45
    IN = 46
    RANGE = 47
    floatVal = 48
    intVal = 49
    stringVal = 50

    @classmethod
    def msg(cls, token):
        nomes = {
            1:'erro',
            2:'<eof>',
            3:'ident',
            4:'num',
            5:'string',
            6:'if',
            7:'else',
            8:'while',
            9:'begin',
            10:'end',
            11:'program',
            12:'(',
            13:')',
            14:',',
            15:';',
            16:'.',
            17: 'for',
            19: 'oprel',
            20: '%',
            21: ':',
            23:'and',
            24:'or',
            25:'not',
            26:'+',
            27:'-',
            28:'*',
            29:'/',
            30:'read',
            31:'write',
            32:'var',
            33:'{',
            34:'}',
            35:'=',
            36:'then',
            37: 'function',
            38: '->',
            39: 'int',
            40: 'float',
            41: '[',
            42: ']',
            43: 'list',
            44: 'return',
            45: 'do',
            46: 'in',
            47: 'range',
            48: 'floatVal',
            49: 'intVal',
            50: 'stringVal'
        }
        return nomes[token]

    @classmethod
    def reservada(cls, lexema):
        reservadas = {
            'program': TOKEN.PROGRAM,
            'if': TOKEN.IF,
            'while': TOKEN.WHILE,
            'begin': TOKEN.BEGIN,
            'end': TOKEN.END,
            'else': TOKEN.ELSE,
            'read': TOKEN.READ,
            'write': TOKEN.WRITE,
            'var': TOKEN.VAR,
            'and': TOKEN.AND,
            'or': TOKEN.OR,
            'not': TOKEN.NOT,
            'string': TOKEN.string,
            'num': TOKEN.num,
            'for': TOKEN.FOR,
            'then': TOKEN.THEN,
            'function': TOKEN.FUNCTION,
            'int': TOKEN.INT,
            'float': TOKEN.FLOAT,
            'list': TOKEN.LIST,
            'return': TOKEN.RETURN,
            'do': TOKEN.DO,
            'in': TOKEN.IN,
            'range': TOKEN.RANGE
        }
        if lexema in reservadas:
            return reservadas[lexema]
        else:
            return TOKEN.ident
