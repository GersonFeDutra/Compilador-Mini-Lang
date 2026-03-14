// -*- mode: cpp -*-
// vim: set filetype=c++:
var x: real = 4.0; # OK -> Tipo real deve ser adicionado
var y: int = 6 / 4; // FIXME -> Expressão deve ser convertida para tipo inteiro.

// FIXME -> Resultado = 3
print x - y; # OK -> Deve suportar operações de tipo real e inteiro
