// Current
z : bool

a, b : int  # single-line multiple declarations

# old.TODO -> single-line multiple assignments
#a, b = 1, 2

/* /* /*/ */* */ */ # nested comments

# old.TODO -> Captures
# [a]
{
    # single-line multiple expressions
    b : bool; a : bool; b = 2 + 3

    a = 3
    + 2

    # line continuation
    a = 3\
        + 2
    
    # * 4 - 5 / 6
    /* 7 : char */ # ERROR
}

/* old.TODO
for (i := 0; i < 10; i ++)
{
    cout << 10 << " "
}
*/

#< Also supports this format.
Could be used as annotation-blocks in the future.
>#
