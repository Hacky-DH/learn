from ply import lex, yacc
from ply.yacc import YaccProduction
from datetime import datetime

tokens = ('IDENTIFIER', 'STRING_LITERAL', 'NUMBER', 'FLOAT', 'BOOL',
          'DATETIME', 'EQUAL', 'COMMA', 'LBRACE', 'RBRACE', 'INPUT', 'START',
          'END', 'LARROW')

# 标记的正则表达式规则
t_IDENTIFIER = r'[a-zA-Z_][a-zA-Z_0-9\.]*'
t_EQUAL = r'='
t_COMMA = r','
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LARROW = r'<-'
t_ignore = ' \t'

#'LPAREN', 'RPAREN'
# t_LPAREN = r'\('
# t_RPAREN = r'\)'


def t_STRING_LITERAL(t):
    r'(\"([^\\\n]|(\\.))*?\")|(\'([^\\\n]|(\\.))*?\')'
    t.value = t.value[1:-1]
    return t


# 这里定义顺序很重要，必须是先t_DATETIME，再t_FLOAT，再t_NUMBER
def t_DATETIME(t):
    r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z'
    t.value = datetime.strptime(t.value, "%Y-%m-%dT%H:%M:%SZ")
    return t


def t_FLOAT(t):
    r'[-+]?\d+\.\d+([eE][-+]?\d+)?'
    t.value = float(t.value)
    return t


def t_NUMBER(t):
    r'[-+]?\d+'
    t.value = int(t.value)
    return t


def t_BOOL(t):
    r'true|false|True|False'
    t.value = t.value.lower() == 'true'
    return t


def t_comment(t):
    r'\#.*'
    pass


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


def t_INPUT(t):
    'input'
    return t


def t_START(t):
    'start'
    return t


def t_END(t):
    'end'
    return t


# 定义语法规则
def p_graphs(p):
    '''graphs : graphs graph
              | graph'''
    if len(p) == 3 and p[1] is not None:
        p[0] = p[1] + [p[2]]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []


def p_graph(p: YaccProduction):
    'graph : IDENTIFIER LBRACE graph_body RBRACE'
    p[0] = {"name": p[1]}
    p[0].update(p[3])


def p_graph_body(p: YaccProduction):
    '''graph_body : graph_body graph_attribute
                  | graph_body node_definitions
                  | empty'''
    if len(p) == 3 and p[1] is not None:
        p[0] = p[2]
        if p[1]:
            p[0].update(p[1])
    else:
        p[0] = {}


def p_graph_attribute(p: YaccProduction):
    '''graph_attribute : IDENTIFIER EQUAL value
                       | START EQUAL IDENTIFIER
                       | END EQUAL IDENTIFIER'''
    p[0] = {p[1]: p[3]}


def p_node_definitions(p: YaccProduction):
    '''node_definitions : node_definition
                        | node_definitions node_definition'''
    if len(p) == 3 and p[1] is not None:
        p[1]["nodes"].append(p[2])
        p[0] = p[1]
    elif len(p) == 2:
        p[0] = {"nodes": [p[1]]}
    else:
        p[0] = {}


def p_node_definition(p: YaccProduction):
    'node_definition : node_output LARROW IDENTIFIER LBRACE node_body RBRACE'
    p[0] = {'name': p[3], 'output': p[1]}
    if p[5]:
        p[0].update(p[5])


def p_node_output(p: YaccProduction):
    '''node_output : IDENTIFIER
                   | node_output COMMA IDENTIFIER'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []


def p_node_body(p: YaccProduction):
    '''node_body : node_attribute
                 | node_body node_attribute'''
    if len(p) == 3 and p[1] is not None:
        p[1].update(p[2])
        p[0] = p[1]
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = {}


def p_node_attribute(p: YaccProduction):
    '''node_attribute : INPUT EQUAL inputs
                      | IDENTIFIER EQUAL value'''
    p[0] = {p[1]: p[3]}


def p_inputs(p: YaccProduction):
    '''inputs : IDENTIFIER
              | inputs COMMA IDENTIFIER'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []


def p_value(p: YaccProduction):
    '''value : STRING_LITERAL
             | FLOAT
             | BOOL
             | DATETIME
             | NUMBER'''
    p[0] = p[1]


def p_empty(p: YaccProduction):
    'empty :'
    p[0] = []


def p_error(p: YaccProduction):
    if p:
        lineno = p.lineno
        # 计算列号
        last_cr = p.lexer.lexdata.rfind('\n', 0, p.lexpos)
        if last_cr < 0:
            column = p.lexpos + 1
        else:
            column = p.lexpos - last_cr
        print(f"Syntax error at line {lineno}, column {column}: '{p.value}'")
    else:
        print("Syntax error at EOF")


def parser_grl(content: str)->list:
    # Build the lexer and parser
    lexer = lex.lex()
    parser = yacc.yacc(debug=False, write_tables=False)
    result = parser.parse(content, lexer=lexer)
    return result

