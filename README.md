# Documentação Mini Lang

O projeto consiste em um interpretador de uma linguagem de programação chamda Mini Lang que foi construída em python e também baseada na linguagem python



# Funcionalidades disponíveis 

Na linguagem miniLang podemos contar com algumas funcionalidades como:

**Verificação de tipos:** Podemos ter a verificação de tipos (Number, String).

**Operações binárias:**:Operações com soma, subtração, divisão, multiplicação.
**Biblioteca para erros:** Uso de uma biblioteca que foi construída para o apresentar quais caracteres deram erro.
**Laço de repetição FOR:** Uso do laço de repetição FOR.
**Laço de repetição WHILE:** Uso do laço de repetição WHILE.
**Uso de funções:** Funções podem ser declaradas.
**IF, ELIF, ELSE:** Uso de condicionais IF, ELIF, ELSE.
**Comentários:** Uso de comentários através do operador **#**.
**Operadores de comparação:** Uso de operadores de comparação **<, >, <=, !=, >=, ==** .
**Operadores lógicos:** Uso de operadores lógicos **AND OR NOT** 
**Funções de retorno:**  função que retorna o resultado da função (**RETURN**)

## Como utilizar o interpretador 

No projeto há duas maneiras de utilizar o interpretador, podemos fazer direto no terminal ou podemos criar um arquivo de texto, esse arquivo de texto tem que estar dentro da pasta onde contém o código fonte,  sabendo disso podemos rodar o código a partir do comando: 

    RUN("teste.txt")

No código acima é utilizado para rodar o arquivo teste contendo o código fonte da linguagem Mini Lang


## Código

No código fonte do projeto da linguagem utilizamos o Lexer para o processamento de tokens e o Parser para fazer o casamento dos padrões (matche).

**Lexer:**

 O Lexer é a primeira etapa do processo de compilação, e sua função é basicamente transformar o código fonte em uma sequência de tokens. Esses tokens são basicamente uma representação simplificada de cada elemento do código fonte, como palavras-chave, símbolos e valores numéricos ou de string.

Para isso, o Lexer percorre todo o código fonte caractere por caractere, e a cada nova sequência de caracteres que forma um token, ele cria um novo objeto de token correspondente. O Lexer também ignora espaços em branco e comentários, já que eles não têm impacto no funcionamento do código.

O resultado final do processo de Tokenização é uma lista de tokens que será utilizada na etapa seguinte, o Parser, para construir uma árvore sintática que represente a estrutura do programa. 

**Parser:**

O parser é a segunda parte da etapa de compilação em que o código-fonte é transformado em uma árvore de sintaxe abstrata (AST). Essa árvore representa a estrutura gramatical do código-fonte em termos de operações, expressões e construções de linguagem.

O parser do código que foi apresentado é composto por duas classes: `Parser` e `Node`.

A classe `Node` representa um nó na árvore de sintaxe abstrata, com um tipo de nó (por exemplo, "expressão binária"), um valor (por exemplo, o operador) e filhos (por exemplo, a expressão à esquerda e à direita do operador). Cada tipo de nó corresponde a uma construção de linguagem específica, como uma atribuição, uma expressão condicional ou uma chamada de função.

A classe `Parser` é responsável por analisar a sequência de tokens produzidos pelo lexer e criar a AST correspondente. O parser usa o método `parse()` para iniciar o processo de análise. Esse método começa analisando um único token e, em seguida, invoca outros métodos para analisar a estrutura maior do código-fonte.

O método `parse_expression()` é usado para analisar expressões e operações. Ele usa um algoritmo recursivo para avaliar a precedência e associatividade dos operadores na expressão e construir a AST correspondente. O método `parse_statement()` é usado para analisar declarações e comandos, como uma atribuição ou uma estrutura de controle de fluxo.

Se o parser encontra um erro sintático durante a análise, ele gera uma mensagem de erro contendo a posição do token e o tipo de token inesperado.

Com a AST gerada pelo parser, o próximo passo é a interpretação, que é responsável por executar o código representado pela árvore.

**Biblioteca para Erro**

Em nosso projeto criamos a função `erro_usando_setas` que é responsável por gerar uma mensagem de erro detalhada que aponta a posição do erro no código-fonte. Ela recebe como entrada o `text`, que é o código-fonte da linguagem criada, a `pos_inicio` e `pos_fim`, que são objetos `Position` que indicam o início e o fim do erro.

A função começa calculando os índices do início e fim da linha onde ocorreu o erro usando a posição de início do erro. Em seguida, ela percorre todas as linhas afetadas pelo erro e calcula a coluna inicial e final do erro em cada linha. Para cada linha, ela adiciona ao `resultado` a linha com uma quebra de linha, seguida de um número de espaços igual à coluna inicial do erro e um número de setas (`^`) igual ao tamanho do erro.

Por fim, a função ajusta os índices para o início e fim da próxima linha e repete o processo até que todas as linhas afetadas pelo erro tenham sido processadas. A função retorna a mensagem de erro com as setas apontando para o erro no código-fonte. Qualquer caractere de tabulação (`\t`) é substituído por um espaço na mensagem de erro para garantir que as setas apontem para o local correto.

## Explicando a Gramática
Considerando a seguinte gramática
```
statements  : NEWLINE* statement (NEWLINE+ statement)* NEWLINE*

statement		: KEYWORD_RETURN expr?
						: KEYWORD_CONTINUE
						: KEYWORD_BREAK
						: expr

expr        : KEYWORD_VAR IDENTIFIER EQ expr
            : comp-expr ((KEYWORD_AND|KEYWORD_OR) comp-expr)*

comp-expr   : NOT comp-expr
            : arith-expr ((EE|LT|GT|LTE|GTE) arith-expr)*

arith-expr  :	term ((PLUS|MINUS) term)*

term        : factor ((MUL|DIV) factor)*

factor      : (PLUS|MINUS) factor
            : power

power       : call (POW factor)*

call        : atom (LPAREN (expr (COMMA expr)*)? RPAREN)?

atom        : INT|FLOAT|STRING|IDENTIFIER
            : LPAREN expr RPAREN
            : list-expr
            : if-expr
            : for-expr
            : while-expr
            : func-def

list-expr   : LSQUARE (expr (COMMA expr)*)? RSQUARE

if-expr     : KEYWORD_IF expr KEYWORD_THEN
              (statement if-expr-b|if-expr-c?)
            | (NEWLINE statements KEYWORD_END|if-expr-b|if-expr-c)

if-expr-b   : KEYWORD_ELIF expr KEYWORD_THEN
              (statement if-expr-b|if-expr-c?)
            | (NEWLINE statements KEYWORD_END|if-expr-b|if-expr-c)

if-expr-c   : KEYWORD_ELSE
              statement
            | (NEWLINE statements KEYWORD_END)

for-expr    : KEYWORD_FOR IDENTIFIER EQ expr KEYWORD_TO expr
              (KEYWORD_STEP expr)? KEYWORD_THEN
              statement
            | (NEWLINE statements KEYWORD_END)

while-expr  : KEYWORD_WHILE expr KEYWORD_THEN
              statement
            | (NEWLINE statements KEYWORD_END)

func-def    : KEYWORD_FUN IDENTIFIER?
              LPAREN (IDENTIFIER (COMMA IDENTIFIER)*)? RPAREN
              (ARROW expr)
            | (NEWLINE statements KEYWORD_END)

KEYWORD_RETURN      : RETURN
KEYWORD_CONTINUE    : CONTINUE
KEYWORD_BREAK       : BREAK
KEYWORD_VAR         : VAR
KEYWORD_AND         : AND
KEYWORD_OR          : OR
KEYWORD_IF          : IF
KEYWORD_ELIF        : ELIF
KEYWORD_ELSE        : ELSE
KEYWORD_FOR         : FOR
KEYWORD_WHILE       : WHILE
KEYWORD_FUN         : FUN
KEYWORD_END         : END

```
**Explicando a gramática**
- statements: 
Representa uma sequência de uma ou mais declarações de comandos (statements). Pode haver um ou mais NEWLINE no início, um ou mais NEWLINE entre cada declaração de comando e zero ou mais NEWLINE no final.

- statement: 
Representa uma única declaração de comando. Pode ser uma declaração de retorno (`RETURN`), um comando de interrupção de laço (`CONTINUE` ou `BREAK`), ou uma expressão (`expr`).

- expr: 
Representa uma expressão. Pode ser uma declaração de variável (`VAR`), seguida de um identificador (`IDENTIFIER`), seguida de um sinal de igualdade (`EQ`) e outra expressão. Ou pode ser uma comparação de expressões (`comp-expr`) conectadas pelos operadores lógicos `AND` ou `OR`.

- comp-expr: 
Representa uma comparação de expressões. Pode ser uma negação (`NOT`) seguida de outra comparação de expressões, ou uma expressão aritmética (`arith-expr`) conectada por um dos operadores de comparação (`EE`, `LT`, `GT`, `LTE`, `GTE`).

- arith-expr: 
Representa uma expressão aritmética. Pode ser um termo (`term`) sozinho ou seguido por um sinal de adição (`+`) ou subtração (`-`) e outro termo.

- term: 
Representa um termo. Pode ser um fator sozinho ou seguido por um sinal de multiplicação (`*`) ou divisão (`/`) e outro fator.

- factor: 
Representa um fator. Pode ser um sinal de adição (`+`) ou subtração (`-`) seguido de outro fator, ou uma potência (`power`).

- power: 
Representa uma potência. Pode ser uma chamada de função (`call`) ou outra potência seguida por um sinal de potência (`^`) e outro fator.

- call: 
Representa uma chamada de função. Pode ser um átomo (`atom`) sozinho ou seguido por um parêntese esquerdo (`LPAREN`), zero ou mais expressões separadas por vírgulas (`COMMA`) e um parêntese direito (`RPAREN`).

- atom: 
Representa um átomo. Pode ser um número inteiro (`INT`), um número de ponto flutuante (`FLOAT`), uma string (`STRING`), um identificador (`IDENTIFIER`), um parêntese esquerdo seguido de uma expressão e um parêntese direito (`LPAREN expr RPAREN`), uma expressão de lista (`list-expr`), uma expressão condicional (`if-expr`), uma expressão de loop for (`for-expr`), uma expressão de loop while (`while-expr`) ou uma definição de função (`func-def`).

- list-expr: 
Representa uma expressão de lista. Pode ser um colchete esquerdo (`LSQUARE`), zero ou mais expressões separadas por vírgulas e um colchete direito (`RSQUARE`).


-   `if-expr`: Representa uma expressão condicional. Consiste em uma palavra-chave `IF` seguida de uma expressão (`expr`), seguida de um dois-pontos (`COLON`), seguida de uma ou mais declarações de comandos (`statement`). Pode haver zero ou mais cláusulas `elif` e uma cláusula `else`.
    
-   `for-expr`: Representa uma expressão de loop for. Consiste em uma palavra-chave `FOR`, seguida de um identificador (`IDENTIFIER`), seguida de um sinal de pertence (`IN`), seguida de uma expressão (`expr`), seguida de dois pontos (`COLON`), seguida de uma ou mais declarações de comandos (`statement`).
    
-   `while-expr`: Representa uma expressão de loop while. Consiste em uma palavra-chave `WHILE`, seguida de uma expressão (`expr`), seguida de dois pontos (`COLON`), seguida de uma ou mais declarações de comandos (`statement`).
    
-   `func-def`: Representa uma definição de função. Consiste em uma palavra-chave `DEF`, seguida de um identificador (`IDENTIFIER`), seguida de um parêntese esquerdo (`LPAREN`), zero ou mais identificadores separados por vírgulas (`IDENTIFIER`), seguido de um parêntese direito (`RPAREN`), seguido de dois pontos (`COLON`), seguido de uma ou mais declarações de comandos (`statement`).
    

Essa é uma gramática bastante detalhada e permite a construção de programas complexos. Com essa gramática, é possível criar programas com loops, funções, condicionais, listas e variáveis.

## Exemplo de um simples uso da linguagem 
Uma simples implementação sobre a linguagem Mini Lang 
```
DEF printHello(word)
    VAR word = word
    PRINT(word)
END
printHello("simples assim")

PRINT("Funcionalidade FOR")
FOR i = 0 TO 100 + 1  THEN
    PRINT(i)
END

PRINT("Funcionalidade WHILE")
VAR i = 5
WHILE i != 0  THEN
    VAR i = i - 1
    PRINT(i)
END
DEF soma(a, b)
    VAR result = a + b
    RETURN result
END 

PRINT(soma(1,3))
d
```

o `d`do arquivo teste.txt ilustra o uso da biblioteca de erro

output:
```
miniLang > RUN("teste.txt")
simples assim     
Funcionalidade FOR
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
Funcionalidade WHILE
4
3
2
1
0
4
Traceback (most recent call last):
  File <stdin>, line 1, in <program>
  File <stdin>, line 1, in run
Runtime Erro: Failed to finish executing script "teste.txt"
Traceback (most recent call last):
  File teste.txt, line 24, in <program>
Runtime Erro: 'd' is not defined


d
^

RUN("teste.txt")
^^^^^^^^^^^^^^^
```
