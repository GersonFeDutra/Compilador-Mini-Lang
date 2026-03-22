// -*- mode: cpp -*-
// vim: set filetype=c++:
var x : real = 5;
var y:int=3;

set y = x - 2.5;

def soma (a:int, b : real) : int {
    return a + b;
}

// -3 + +5.0
// FIXME deve suportar truncamento
var z: bool = (soma(-x, +y) < 4) < 1; // OK -> Deve suportar chamada com de função com conversão de tipo.
print z;
