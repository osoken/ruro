# ruro

_ruro_ lets composition of functions in pipe notation.

Concatenating _ruro objects_ with `|` operator means composing a function which passes the return value of the lefthand side as the (first) argument of the righthand side.

## A Simple Example

```
import ruro

p = ruro.Pipeline(range) | ruro.Pipeline(sum)  # equivalent to lambda x: sum(range(x))
print(p(5))
#> 10

print(ruro.Constant(5) | p | ruro.Exec())  # equivalent to (lambda x: sum(range(x)))(5)
#> 10
```
