// -*- mode: cpp -*-
// vim: set filetype=c++:
// Test precedence behavior

var x: int = 3 + 2 - 7 * (4 - 1) / 3; // -2
print x;

set x = 3 + 2 - 7 * (4 - 1) - 1 / 3; // -16
print x;

// OK -> Deve coerir o tipo inteiro pra float e vice-versa
var y: real = 3 + 2 - 7 * (4 - 1) - 1 / 3; // ~−16,33333333
print y;

set x = 3 + (2 - 7 * (4 - 1) - 1) / 3; // −3
set y=3+2-7*4-1-1/3; // ~−24,33333333
print x + y; // ~-27,33333333
