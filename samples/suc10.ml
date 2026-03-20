// -*- mode: cpp -*-
// vim: set filetype=c++:
var x : int = 5;;

{ # OK -> Deve permitir sombreamento
    var x : int = 10;
    print "O valor de x é: " ; print x ;
}
