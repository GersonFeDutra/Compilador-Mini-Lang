// -*- mode: cpp -*-
// vim: set filetype=c++:
var x : int = 5;;
var resultado : int = 1;

def calcular ( n : int, o: int ) : int{
    if ( n > 0) {
        return n * calcular ( n - 1) ;
    }
    return
            o;
}

print " Calculando Fatorial de 5 🧠: " ;
set resultado = calcular ( x ) ; # FIXME -> Número na Passagem de parâmetros inválido
print resultado ;
