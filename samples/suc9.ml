// -*- mode: cpp -*-
// vim: set filetype=c++:
var x : int = 5;;
var resultado : int = 0;

def calcular ( x : int) : int{ # OK -> Deve permitir sombreamento
    if ( x > 0) {
        return x * calcular ( x - 1) ;
    }
    return
            1;
}

print "Calculando Fatorial de 5 🧠: " ;
set resultado = calcular ( 5) ;
print resultado ;
