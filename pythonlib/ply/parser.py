from ply import lex, yacc
from ply.lex import LexToken
from ply.yacc import YaccProduction, LRParser
from datetime import datetime
from grl.types import Variable, Ref

keywords = ('graph', 'node', 'var', 'meta', 'import', 'as', 'from', 'input',
            'depend', 'version', 'start', 'end')

tokens = ('IDENTIFIER', 'ONE_LINE_STRING', 'MULTI_LINE_STRING', 'NUMBER',
          'FLOAT', 'BOOL', 'DATETIME', 'DEFINED_BY', 'COMMA', 'LBRACE',
          'RBRACE', 'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'COLON',
          'DOT') + keywords

# 标记的正则表达式规则
t_DEFINED_BY = r'='
t_COMMA = r','
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COLON = r':'
t_DOT = r'\.'
t_ignore = ' \t'
t_graph = 'graph'
t_node = 'node'
t_var = 'var'
t_meta = 'meta'
t_input = 'input'
t_depend = 'depend'
t_version = 'version'
t_start = 'start'
t_end = 'end'


def t_MULTI_LINE_STRING(t: LexToken):
    r'("""(?:.|\n)*?""")|(\'\'\'(?:.|\n)*?\'\'\')'
    t.value = t.value[3:-3]
    t.lexer.lineno += t.value.count('\n')
    return t


def t_ONE_LINE_STRING(t: LexToken):
    r'(\"([^\\\n]|(\\.))*?\")|(\'([^\\\n]|(\\.))*?\')'
    t.value = t.value[1:-1]
    return t


# 这里定义顺序很重要，必须是先t_DATETIME，再t_FLOAT，再t_NUMBER
def t_DATETIME(t: LexToken):
    r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z'
    t.value = datetime.strptime(t.value, "%Y-%m-%dT%H:%M:%SZ")
    return t


def t_FLOAT(t: LexToken):
    r'[-+]?\d+\.\d+?([eE][-+]?\d+)?'
    t.value = float(t.value)
    return t


def t_NUMBER(t: LexToken):
    r'[-+]?\d+'
    t.value = int(t.value)
    return t


def t_BOOL(t: LexToken):
    r'true|false|True|False'
    t.value = t.value.lower() == 'true'
    return t


def t_comment(t: LexToken):
    r'\#.*'
    pass


def t_newline(t: LexToken):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t: LexToken):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


def t_IDENTIFIER(t: LexToken):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    if t.value.lower() in keywords:
        t.type = t.value.lower()
    t.value = t.value
    return t


# 定义语法规则
def p_statements(p: YaccProduction):
    '''statements : statement
                  | statement statements'''
    if len(p) == 3 and p[2] is not None:
        p[0] = _merge_stmt(p[2], p[1])
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = {}


def p_statement(p: YaccProduction):
    '''statement : vars
                 | imports
                 | graphs
                 | metas'''
    p[0] = p[1]


######################## vars 定义变量 #########################
def p_vars(p: YaccProduction):
    '''vars : var_def
            | var_def vars'''
    if len(p) == 3 and p[2] is not None:
        p[2]["vars"].append(p[1])
        p[0] = p[2]
    elif len(p) == 2:
        p[0] = {"vars": [p[1]]}
    else:
        p[0] = {}


def p_var_def(p: YaccProduction):
    '''var_def : var LBRACE var_block RBRACE
               | var LBRACE var_block RBRACE as IDENTIFIER'''
    p[0] = p[3]
    if len(p) == 7:
        p[0]['as'] = p[6]


def p_var_block(p: YaccProduction):
    '''var_block :
                 | attr_defs'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = {}


def p_attr_defs(p: YaccProduction):
    '''attr_defs : attr_def
                 | attr_def attr_defs'''
    if len(p) == 3 and p[2] is not None:
        if inter := _interset_dict(p[2], p[1]):
            inter = ','.join(inter)
            raise ValueError(f"属性 {inter} 重复定义")
        p[2].update(p[1])
        p[0] = p[2]
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = {}


def p_attr_def(p: YaccProduction):
    'attr_def : IDENTIFIER DEFINED_BY value'
    p[0] = {p[1]: p[3]}


######################## imports 定义导入文件 #########################
# import语法 有参考 https://docs.python.org/3/reference/grammar.html
def p_imports(p: YaccProduction):
    '''imports : import_def
               | import_def imports'''
    if len(p) == 3 and p[2] is not None:
        p[2]["imports"].extend(p[1])
        p[0] = p[2]
    elif len(p) == 2:
        p[0] = {"imports": p[1]}
    else:
        p[0] = {}


def p_import_def(p: YaccProduction):
    '''import_def : import_name
                  | import_from'''
    p[0] = p[1]


def p_import_name(p: YaccProduction):
    'import_name : import dotted_as_names'
    p[0] = p[2]


def p_dotted_as_names(p: YaccProduction):
    '''dotted_as_names : dotted_as_name
                       | dotted_as_name COMMA dotted_as_names'''
    if len(p) == 4 and p[3] is not None:
        p[3].append(p[1])
        p[0] = p[3]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []


def p_dotted_as_name(p: YaccProduction):
    '''dotted_as_name : dotted_name
                      | dotted_name as IDENTIFIER'''
    if len(p) == 4:
        p[0] = {'import': p[1], 'as': p[3]}
    elif len(p) == 2:
        p[0] = {'import': p[1]}
    else:
        p[0] = {}


def p_dotted_name(p: YaccProduction):
    '''dotted_name : IDENTIFIER
                   | IDENTIFIER DOT dotted_name'''
    if len(p) == 4 and p[3]:
        p[0] = f"{p[1]}.{p[3]}"
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ''


def p_import_from(p: YaccProduction):
    '''import_from : from dotted_name import IDENTIFIER'''
    raise NotImplementedError('不支持from import语法')


######################## graph 定义 #########################
def p_graphs(p: YaccProduction):
    '''graphs : graph_def
              | graph_def graphs'''
    if len(p) == 3 and p[2] is not None:
        p[2]["graphs"].append(p[1])
        p[0] = p[2]
    elif len(p) == 2:
        p[0] = {"graphs": [p[1]]}
    else:
        p[0] = {}


def p_graph_def(p: YaccProduction):
    '''graph_def : graph LBRACE graph_block RBRACE
                 | graph LBRACE graph_block RBRACE as IDENTIFIER'''
    p[0] = p[3]
    if len(p) == 7:
        p[0]['as'] = p[6]


def p_graph_block(p: YaccProduction):
    '''graph_block : 
                   | graph_stmt
                   | graph_stmt graph_block'''
    if len(p) == 3 and p[2] is not None:
        if 'nodes' in p[1] and 'nodes' in p[2]:
            if inter := _interset_dict(p[1]['nodes'], p[2]['nodes']):
                inter = ','.join(inter)
                raise ValueError(f'graph中节点的输出 {inter} 重复定义')
            p[2]['nodes'].update(p[1]['nodes'])
        else:
            if inter := _interset_dict(p[2], p[1]):
                inter = ','.join(inter)
                raise ValueError(f"graph属性 {inter} 重复定义")
            p[2].update(p[1])
        p[0] = p[2]
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = {}


def p_graph_stmt(p: YaccProduction):
    '''graph_stmt : attr_def
                   | ref_def
                   | graph_attr
                   | node_as_def'''
    p[0] = p[1]


def p_ref_def(p: YaccProduction):
    'ref_def : IDENTIFIER DEFINED_BY dotted_name'
    p[0] = {p[1]: Ref(p[3])}


def p_graph_attr(p: YaccProduction):
    '''graph_attr : version_def
                   | start DEFINED_BY dotted_identifiers
                   | end DEFINED_BY dotted_identifiers'''
    if len(p) == 4:
        p[0] = {p[1]: p[3]}
    elif len(p)==2:
        p[0] = p[1]
    else:
        p[0] = {}


def p_identifiers(p: YaccProduction):
    '''identifiers : IDENTIFIER
                   | IDENTIFIER COMMA identifiers'''
    if len(p) == 4 and p[3] is not None:
        p[3].append(p[1])
        p[0] = p[3]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []


def p_dotted_identifiers(p: YaccProduction):
    '''dotted_identifiers : dotted_name
                          | dotted_name COMMA dotted_identifiers'''
    if len(p) == 4 and p[3] is not None:
        p[3].append(p[1])
        p[0] = p[3]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []


def p_node_as_def(p: YaccProduction):
    '''node_as_def : node_def
                   | node_def as IDENTIFIER'''
    if len(p) == 4:
        p[0] = {'nodes': {p[3]: next(iter(p[1]['nodes'].values()))}}
    else:
        p[0] = p[1]


def p_node_def(p: YaccProduction):
    '''node_def : dotted_identifiers DEFINED_BY node LBRACE node_block RBRACE
                | IDENTIFIER DEFINED_BY node LBRACE node_block RBRACE'''
    if isinstance(p[1], list):
        p[1].reverse()
        output_key = ','.join(p[1])
    else:
        output_key = p[1]
        p[1] = [p[1]]
    p[0] = {'nodes': {output_key: {'output': p[1]}}}
    if p[5]:
        p[0]['nodes'][output_key].update(p[5])


def p_node_block(p: YaccProduction):
    '''node_block : 
                  | node_stmt
                  | node_stmt node_block'''
    if len(p) == 3 and p[2] is not None:
        if 'input' in p[1] and 'input' in p[2]:
            if inter := _interset_dict(p[1]['input'], p[2]['input']):
                inter = ','.join(inter)
                raise ValueError(f'graph中节点的input的key {inter} 重复定义')
            p[2]['input'].update(p[1]['input'])
        else:
            if inter := _interset_dict(p[2], p[1]):
                inter = ','.join(inter)
                raise ValueError(f"node属性 {inter} 重复定义")
            p[2].update(p[1])
        p[0] = p[2]
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = {}


def p_node_stmt(p: YaccProduction):
    '''node_stmt : attr_def
                 | ref_def
                 | node_attr'''
    p[0] = p[1]


def p_node_attr(p: YaccProduction):
    '''node_attr : version_def
                 | depend DEFINED_BY IDENTIFIER
                 | input DEFINED_BY identifiers
                 | input DOT dotted_name DEFINED_BY identifiers'''
    if len(p) == 6:
        p[0] = {p[1]: {p[3]: p[5]}}
    elif len(p) == 4:
        p[0] = {p[1]: p[3]}
    elif len(p)==2:
        p[0] = p[1]
    else:
        p[0] = {}


######################## value 定义 #########################
def p_value(p: YaccProduction):
    '''value : MULTI_LINE_STRING
             | ONE_LINE_STRING
             | FLOAT
             | BOOL
             | DATETIME
             | NUMBER
             | dict_stmt
             | list_stmt
             | tuple_stmt
             | set_stmt'''
    p[0] = p[1]


def p_dict_stmt(p: YaccProduction):
    '''dict_stmt : LBRACE dict_block RBRACE'''
    p[0] = p[2]


def p_dict_block(p: YaccProduction):
    '''dict_block : 
                  | key_value
                  | key_value COMMA dict_block'''
    if len(p) == 4 and p[3]:
        if inter := _interset_dict(p[3], p[1]):
            inter = ','.join(inter)
            raise ValueError(f"dict的key {inter} 重复")
        p[3].update(p[1])
        p[0] = p[3]
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = {}


def p_key_value(p):
    'key_value : ONE_LINE_STRING COLON value'
    p[0] = {p[1]: p[3]}


def p_list_stmt(p: YaccProduction):
    '''list_stmt : LBRACKET list_block RBRACKET'''
    p[0] = p[2]


def p_list_block(p):
    '''list_block :
                  | value
                  | value COMMA list_block'''
    if len(p) == 4 and p[3]:
        p[3].append(p[1])
        p[0] = p[3]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []


def p_tuple_stmt(p: YaccProduction):
    '''tuple_stmt : LPAREN tuple_block RPAREN'''
    p[0] = p[2]


def p_tuple_block(p):
    '''tuple_block :
                   | value
                   | value COMMA tuple_block'''
    if len(p) == 4 and p[3]:
        p[0] = (p[1], ) + p[3]
    elif len(p) == 2:
        p[0] = (p[1], )
    else:
        p[0] = ()


def p_set_stmt(p: YaccProduction):
    '''set_stmt : LBRACE set_block RBRACE'''
    p[0] = p[2]


def p_set_block(p):
    '''set_block : value
                 | value COMMA set_block'''
    if len(p) == 4 and p[3]:
        p[0] = {p[1]} | p[3]
    else:
        p[0] = {p[1]}


def p_version_def(p: YaccProduction):
    '''version_def : version DEFINED_BY ONE_LINE_STRING'''
    p[0] = {p[1]: p[3]}


######################## meta 定义变量 #########################
def p_metas(p: YaccProduction):
    '''metas : meta_def
             | meta_def metas'''
    graph_meta = [m['graph'] for m in p[1] if 'graph' in m and m['graph']]
    node_meta = [m['node'] for m in p[1] if 'node' in m and m['node']]
    if len(p) == 3 and p[2] is not None:
        if graph_meta:
            p[2]["metas"]['graph'].append(graph_meta)
        if node_meta:
            p[2]["metas"]['node'].append(node_meta)
        p[0] = p[2]
    else:
        p[0] = {"metas": {'graph': graph_meta, 'node': node_meta}}



def p_meta_def(p: YaccProduction):
    '''meta_def : meta LBRACE meta_block RBRACE'''
    p[0] = p[3]


def p_meta_block(p: YaccProduction):
    '''meta_block : 
                  | meta_stmt
                  | meta_stmt meta_block'''
    if len(p) == 3 and p[2] is not None:
        p[2].append(p[1])
        p[0] = p[2]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []


def p_meta_stmt(p: YaccProduction):
    '''meta_stmt : graph_meta
                 | node_meta'''
    p[0] = p[1]


def p_graph_meta(p: YaccProduction):
    '''graph_meta : graph LBRACE graph_meta_block RBRACE'''
    p[0] = {'graph': p[3]}


def p_graph_meta_block(p: YaccProduction):
    '''graph_meta_block : 
                        | meta_attr_stmt
                        | meta_attr_stmt graph_meta_block'''
    if len(p) == 3 and p[2] is not None:
        if inter := _interset_dict(p[2], p[1]):
            inter = ','.join(inter)
            raise ValueError(f"graph meta属性 {inter} 重复定义")
        p[2].update(p[1])
        p[0] = p[2]
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = {}


def p_meta_attr_stmt(p: YaccProduction):
    '''meta_attr_stmt : attr_def
                      | version_def
                      | input_meta_def'''
    p[0] = p[1]


def p_node_meta(p: YaccProduction):
    '''node_meta : node LBRACE node_meta_block RBRACE'''
    p[0] = {'node': p[3]}


def p_node_meta_block(p: YaccProduction):
    '''node_meta_block : 
                       | meta_attr_stmt
                       | meta_attr_stmt node_meta_block'''
    if len(p) == 3 and p[2] is not None:
        if inter := _interset_dict(p[2], p[1]):
            inter = ','.join(inter)
            raise ValueError(f"node meta属性 {inter} 重复定义")
        p[2].update(p[1])
        p[0] = p[2]
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = {}


def p_input_meta_def(p: YaccProduction):
    '''input_meta_def : input DEFINED_BY value'''
    p[0] = {p[1]: p[3]}


def p_error(p: LexToken):
    if p:
        lineno = p.lineno
        # 计算列号
        last_cr = p.lexer.lexdata.rfind('\n', 0, p.lexpos)
        if last_cr < 0:
            column = p.lexpos + 1
        else:
            column = p.lexpos - last_cr
        raise ValueError(
            f"Syntax error at line {lineno}, column {column}: '{p.value}'")
    else:
        raise ValueError("Syntax error at EOF")


def _merge_stmt(stmt1: dict, stmt2: dict):
    for key, value in stmt2.items():
        if key in stmt1:
            if isinstance(stmt1[key], list):
                stmt1[key].extend(value)
            elif isinstance(stmt1[key], dict):
                stmt1[key].update(value)
            else:
                stmt1[key] = value
        else:
            stmt1[key] = value
    return stmt1


def _interset_dict(left: dict, right: dict) -> set:
    return set(left.keys()) & set(right.keys())


def parse_grl(content: str, debug=False) -> list:
    # Build the lexer and parser
    lexer = lex.lex()
    parser: LRParser = yacc.yacc(debug=False, write_tables=False)
    result = parser.parse(content, lexer=lexer, debug=debug)
    return result
