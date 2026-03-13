// -*- mode: cpp -*-
// vim: set filetype=c++:
var x : int = 5;;
var resultado : int = 1;

def soma (a:int, b : int) : int {
    return a + b;
}

print "Somando a + b: ";
set resultado = soma(x, x); # OK -> Múltiplos argumentos
print resultado;
