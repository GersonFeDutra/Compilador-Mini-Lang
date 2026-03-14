// -*- mode: cpp -*-
// vim: set filetype=c++:
var x : int = 5;;
var resultado : int = 1;

def calcular ( n : int ) : int{
    if ( n > 0) {
        return n * calcular ( n - 1) ;
    }
    return
            1;
}

print " Calculando Fatorial de 5 🧠: " ;
set resultado = calcular ( x, x ) ; # OK -> Número na Passagem de parâmetros inválido
print resultado ;
