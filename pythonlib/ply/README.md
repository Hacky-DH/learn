# 图表示语言（GRL，Graph Representation Language

语法类似python和toml格式，比较易于上手。

用途：使用简单的语法描述图编排以及元数据。

# 第一个GRL
```
graph {
  version = "1.0.0"
  description=""
  node1 = node {
    id = 'builtin.node'
    version='1.1.0'
  }
}
```

定义了一个图，图中version和description两个属性，只有一个节点node1。

## 安装grl
`pip install grl`

## 编译解析
```
import grl
result = grl.compile('hello.grl')
```
输出
```
{'graphs': [{'description': '',
             'nodes': {'node1': {'id': 'builtin.node',
                                 'output': ['node1'],
                                 'version': '1.1.0'}},
             'version': '1.0.0'}]}
```

# GRL语言结构

GRL语言基础组成有graph,var,import,meta，一个grl文件可以包括0个或多个结构。

## graph块

graph用于定义图编排。
```
graph {
    version = '1.0.0'
    start = node1
    end = node2
    attr1 = 45
    node1 = node {
        id = 'builtin.node'
        version = '1.0.0'
        input = input1
    } as n1
} as graph1
```
graph块可以定义多个属性，其中保留属性有
1. version指定图的版本，只能用字符串表示。
1. start指定图的起点，可以指定多个起点，使用,分割，可选，当图中存在环且起点在环中时必须指定。
1. end指定图的终点，可选。
1. as是可选的，指定时可以在其他图中当作子图引用。

node块用于定义图中的节点。
等号前是节点输出，节点输出格式如下
1. `value1`表示节点的全部输出
1. `value1,value2,...`表示指定节点的多个输出，需要节点的输出是tuple或list等类似类型
1. `name.value1,name.value2,...`表示指定节点的多个输出，需要节点的输出是dict等类似类型,可以按输出的key指定。

**node块支持同一个op实现定义多个node**，通过node的输出或as区别不同的节点。

as是可选的，指定时可以在其他节点中引用。具体的含义不同的执行器可以有不同的解释。

node块中可以定义多个属性，其中保留属性有
1. version指定node的版本，只能用字符串表示。
1. input指定当前节点的输入数据依赖，当节点的输出是dict时可以指定具体的输出key，input.key=input2
1. depend指定控制依赖其他节点或图，控制依赖是指不依赖数据，只控制前后执行顺序。

## var块
用于定义变量，可以在graph块或node块中引用。一般在需要定义多次同一属性时使用。
```
var {
   var1 = 48
   var2 = {'name': 'bar'}
} as A
```
变量名需要是合法的标识符，不能是关键字。

引用时直接使用变量名var1引用。

as是可选的，可以理解是变量的命名空间，指定时可以解决不同var块变量同名的问题

## import块
用于导入文件中的var定义，as用于重命名
```
import foo, foo as bar
import bar.joo, bar.foo as koo
```
其中foo是文件名，默认会找foo.grl文件；bar.joo表示bar目录下的joo.grl文件

查找文件优先级：
1. grl文件同级目录
1. 当前目录
1. 指定目录

## meta块
用于定义图和节点的元数据，图和节点的元数据可以定义version,input,output等等属性

meta中可以定义多个graph和node元数据块。
```
meta {
    graph {
        version='1.0.0'
        name = 'graph1'
        description = 'graph1 description'
        input = [{"name":"data", "type":"str"}]
        output = [{"name":"a", "type":"str"},{"name":"b", "type":"int"}]
    }
    node {
        version='1.1.0'
        name='node1'
        description="node1 description"
        input = [{"name":"data", "type":"str"}]
        output = [{"name":"a", "type":"str"},{"name":"b", "type":"int"}]
        attr1="demo attr示例属性"
        attr2=true
    }
    graph {
        other = "abc"
    }
    node {
        node_attr = "def"
    }
}
```

# GRL语言基础语法
## 注释
使用#注释

空格换行制表符会忽略

## 标识符
用来命名变量，命名规则同Python和Java中的变量

## 属性值类型
1. 字符串：支持单引号'',双引号"",单双引号只能单行，三引号''''''或""""""，三引号可以包含回车，支持多行字符串。可以包含中文。
1. 数字，目前只支持十进制
1. 浮点数，支持2.3，或1.0e3
1. 布尔值，支持true或false
1. 日期，支持固定格式2024-12-02T10:32:00Z
1. dict，和python中dict格式一致 `{'key': value}` value可以是其他属性值，也即支持嵌套
1. list，和python中list格式一致 `[value,value]` value可以是其他属性值，也即支持嵌套
1. tuple，和python中tuple格式一致 `(value,value)` value可以是其他属性值，也即支持嵌套
1. set，和python中set格式一致 `{value,value}` value可以是其他属性值，也即支持嵌套

## 关键字
有graph,node,var,meta,import,as,input,depend,version,start,end，关键字不能作为变量名。

# API 参考
grl.compile
