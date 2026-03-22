// -*- mode: cpp -*-
// vim: set filetype=c++:
var x : int = 5;
var y:real=3.2;

def soma (a:int, b : bool) : int {
    return a + b;
}

// -3 + +5.0
var z: real = (soma(-x, +y) < 4) + 1; // OK -> Erro: combinando tipos diferentes
print z;
