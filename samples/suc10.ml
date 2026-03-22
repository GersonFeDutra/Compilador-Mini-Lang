// -*- mode: cpp -*-
// vim: set filetype=c++:
var x : int = 5.5;; # OK -> Truncamento

# FIXME -> Precisamos criar um escopo em python: Sugestão (criar uma função lambda que executa o bloco imediatamente)
{ # OK -> Deve permitir sombreamento
    var x : int = 10;
    print "O valor de x é: " ; print x ;
}
