// -*- mode: cpp -*-
// vim: set filetype=c++:
# FIXME -> Deve suportar veracidade (conversão int -> bool)
var x : bool = 3 + (true and true + false or true - not true) + true - 1 + not 5;

print x; # Deve suportar unário de negacao
