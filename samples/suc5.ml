// -*- mode: cpp -*-
// vim: set filetype=c++:
var resultado: int = 4;
print resultado ;

{
    var resultado: int = 5; # OK -> Variáveis de mesmo nome em escopos diferentes
    print resultado ;
}
