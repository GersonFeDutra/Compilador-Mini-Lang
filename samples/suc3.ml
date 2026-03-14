// -*- mode: cpp -*-
// vim: set filetype=c++:
var x : int = 5;;
var resultado : int = 1;

def calcular ( n:int ) : int {
    if (n == 0) {
        return (1);
    }
    else { if (n == 1) {
        return 2;
    }
    else {
        return (
            n * calcular ( n - 1) ); # OK -> return deve aceitar expressões entre "(" ")"
    }}
}

set resultado = calcular(x);
print resultado;
