// -*- mode: cpp -*-
// vim: set filetype=c++:
var x : real = 5;
var y:int=3;

def soma (a:int, b : real) : int {
    return a + b;
}

// -3 + +5.0
# FIXME -> Deve truncar real -> int
var z: real = (soma(-x, +y) < 4) + 1; // OK -> combinando tipos compatíveis
print z;
