// -*- mode: cpp -*-
// vim: set filetype=c++:
var resultado : int = 1;

// def calcular ( n : int, o: int ) : int{
//     if ( n > 0) {
//         return n * calcular ( n - 1, o) ;
//     }
//     return
//             o;
// }

print " Calculando Fatorial de 5 🧠: " ;
# TODO -> Melhorar mensagem de erro usando "função não declarada" ao invés de "variável não declarada"
set resultado = calcular ( 5, 2 ) ;  # OK -> Função não declarada
print resultado ;
