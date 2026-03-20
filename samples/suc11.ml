// -*- mode: cpp -*-
// vim: set filetype=c++:
var x : int = 5;
var y:int=3;

def soma (a:int, b : real) : int {
    return a + b;
}

// -3 + +5.0
var z: bool = (soma(-x, +y) < 4) < 1; // FIXME -> Deve suportar chamada com de função com conversão de tipo.
print z;
