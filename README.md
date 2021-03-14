# CHIP-8 Emu

![Screenshot](/screenshot.png)

Este projeto é uma implementação de um emulador de CHIP-8 em Python, desenvolvido como trabalho de formatura do curso de ciência da computação do IME-USP.

Mais detalhes sobre o trabalho, incluindo a monografia final, estão em https://linux.ime.usp.br/~dpa/mac0499/


## Requisitos

Este projeto requer a versão 3.9 da linguagem Python, assim como a biblioteca Pygame instalada.

A biblioteca pygame pode ser instalado atráves do comando `pip3 install --user pygame`


## Executando o emulador

Para executar o emulador utilize o comando `python3 src/main.py <rom> <velocidade>`.

O primeiro parâmetro deve ser a ROM a ser executada e o segundo a velocidade do emulador, em instruções por segundo. A velocidade do emulador deve ser ajustada de acordo com a ROM a ser executada.

Uma pequena biblioteca de ROMs faz parte do projeto. Para utiliza-las, teste os comandos abaixo:

```
python3 src/main.py roms/chip_modern/glitchghost.ch8 8000
```

```
python3 src/main.py roms/chip_modern/danm8ku.ch8 1000000
```

```
python3 src/main.py roms/chip_games/brix.ch8 700
```


## Controles

O mapeamento entre o teclado real e o teclado de CHIP-8 é dado abaixo:

```
 Chip-8     Teclado
---------  ---------
 1 2 3 C    1 2 3 4
 4 5 6 D    q w e r
 7 8 9 E    a s d f
 A 0 B F    z x c v
```


## Debugger

Caso e emulador encontre algum erro, um modo debug simples será ativado com uma mensagem similar a abaixo:

```
InvalidOpcodeError: No handler for opcode: ff07
0: 0x02    1: 0x00    2: 0x06    3: 0x0B
4: 0x00    5: 0x00    6: 0x00    7: 0x00
8: 0x00    9: 0x00    A: 0x00    B: 0x00
C: 0x00    D: 0x00    E: 0x00    F: 0x00
I:  0x0270 - be f2 16 10
IP: 0x0CE9 - ff07
Delay: 0
Stack: [3317, 2617, 2607]
```

Essa mensagem diz o tipo de erro encontrado, assim como o estado da CPU virtual no momento do erro.

O comando `c` pode ser utilizado para ignorar a instrução que gerou o erro e continuar a execução. Qualquer outro comando termina a execução do programa.
