// -*- mode: cpp -*-
// vim: set filetype=c++:
var x : int = 5;;
var y : bool =  x < 3 + 1; # OK -> Deve suportar veracidade (conversão int -> bool)
var resultado : int = x + y; # OK -> Conversão de bool para int
print resultado;
print not resultado; # Ok -> Negação em int
