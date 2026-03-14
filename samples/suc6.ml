// -*- mode: cpp -*-
// vim: set filetype=c++:
var x: real = 4.0; # OK -> Tipo real deve ser adicionado
var y: int = 6 / 4; // OK -> Expressão deve ser convertida para tipo inteiro.

// OK -> Resultado = 3.0
print x - y; # OK -> Deve suportar operações de tipo real e inteiro
