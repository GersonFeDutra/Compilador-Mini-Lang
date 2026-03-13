// -*- mode: cpp -*-
// vim: set filetype=c++:
var x : int = 5;;
var resultado : int = 1;

def calcular ( n:int ) : int {
    return (
        n * calcular ( n - 1) ); # FIXME -> return deve aceitar expressões entre "(" ")"
}
