tutorial_tests = """
Let's try a simple generator:

    >>> def f():
    ...    yield 1
    ...    yield 2

    >>> g = f()
    >>> g.next()
    1
    >>> g.next()
    2
    >>> g.next()
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
      File "<stdin>", line 2, in g
    StopIteration

"return" stops the generator:

    >>> def f():
    ...     yield 1
    ...     return
    ...     yield 2 # never reached
    ...
    >>> g = f()
    >>> g.next()
    1
    >>> g.next()
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
      File "<stdin>", line 3, in f
    StopIteration
    >>> g.next() # once stopped, can't be resumed
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    StopIteration

"raise StopIteration" stops the generator too:

    >>> def f():
    ...     yield 1
    ...     return
    ...     yield 2 # never reached
    ...
    >>> g = f()
    >>> g.next()
    1
    >>> g.next()
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    StopIteration
    >>> g.next()
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    StopIteration

However, they are not exactly equivalent:

    >>> def g1():
    ...     try:
    ...         return
    ...     except:
    ...         yield 1
    ...
    >>> list(g1())
    []

    >>> def g2():
    ...     try:
    ...         raise StopIteration
    ...     except:
    ...         yield 42
    >>> print list(g2())
    [42]

This may be surprising at first:

    >>> def g3():
    ...     try:
    ...         return
    ...     finally:
    ...         yield 1
    ...
    >>> list(g3())
    [1]

Let's create an alternate range() function implemented as a generator:

    >>> def yrange(n):
    ...     for i in range(n):
    ...         yield i
    ...
    >>> list(yrange(5))
    [0, 1, 2, 3, 4]

Generators always return to the most recent caller:

    >>> def creator():
    ...     r = yrange(5)
    ...     print "creator", r.next()
    ...     return r
    ...
    >>> def caller():
    ...     r = creator()
    ...     for i in r:
    ...             print "caller", i
    ...
    >>> caller()
    creator 0
    caller 1
    caller 2
    caller 3
    caller 4

Generators can call other generators:

    >>> def zrange(n):
    ...     for i in yrange(n):
    ...         yield i
    ...
    >>> list(zrange(5))
    [0, 1, 2, 3, 4]

"""

# The examples from PEP 255.

pep_tests = """

Specification: Return

    Note that return isn't always equivalent to raising StopIteration:  the
    difference lies in how enclosing try/except constructs are treated.
    For example,

        >>> def f1():
        ...     try:
        ...         return
        ...     except:
        ...        yield 1
        >>> print list(f1())
        []

    because, as in any function, return simply exits, but

        >>> def f2():
        ...     try:
        ...         raise StopIteration
        ...     except:
        ...         yield 42
        >>> print list(f2())
        [42]

    because StopIteration is captured by a bare "except", as is any
    exception.

Specification: Generators and Exception Propagation

    >>> def f():
    ...     return 1/0
    >>> def g():
    ...     yield f()  # the zero division exception propagates
    ...     yield 42   # and we'll never get here
    >>> k = g()
    >>> k.next()
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
      File "<stdin>", line 2, in g
      File "<stdin>", line 2, in f
    ZeroDivisionError: integer division or modulo by zero
    >>> k.next()  # and the generator cannot be resumed
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    StopIteration
    >>>

Specification: Try/Except/Finally

    >>> def f():
    ...     try:
    ...         yield 1
    ...         try:
    ...             yield 2
    ...             1/0
    ...             yield 3  # never get here
    ...         except ZeroDivisionError:
    ...             yield 4
    ...             yield 5
    ...             raise
    ...         except:
    ...             yield 6
    ...         yield 7     # the "raise" above stops this
    ...     except:
    ...         yield 8
    ...     yield 9
    ...     try:
    ...         x = 12
    ...     finally:
    ...         yield 10
    ...     yield 11
    >>> print list(f())
    [1, 2, 4, 5, 8, 9, 10, 11]
    >>>


Guido's binary tree example.

    >>> # A binary tree class.
    >>> class Tree:
    ...
    ...     def __init__(self, label, left=None, right=None):
    ...         self.label = label
    ...         self.left = left
    ...         self.right = right
    ...
    ...     def __repr__(self, level=0, indent="    "):
    ...         s = level*indent + `self.label`
    ...         if self.left:
    ...             s = s + "\\n" + self.left.__repr__(level+1, indent)
    ...         if self.right:
    ...             s = s + "\\n" + self.right.__repr__(level+1, indent)
    ...         return s
    ...
    ...     def __iter__(self):
    ...         return inorder(self)

    >>> # Create a Tree from a list.
    >>> def tree(list):
    ...     n = len(list)
    ...     if n == 0:
    ...         return []
    ...     i = n / 2
    ...     return Tree(list[i], tree(list[:i]), tree(list[i+1:]))

    >>> # Show it off: create a tree.
    >>> t = tree("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    >>> # A recursive generator that generates Tree leaves in in-order.
    >>> def inorder(t):
    ...     if t:
    ...         for x in inorder(t.left):
    ...             yield x
    ...         yield t.label
    ...         for x in inorder(t.right):
    ...             yield x

    >>> # Show it off: create a tree.
    ... t = tree("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    ... # Print the nodes of the tree in in-order.
    ... for x in t:
    ...     print x,
    A B C D E F G H I J K L M N O P Q R S T U V W X Y Z

    >>> # A non-recursive generator.
    >>> def inorder(node):
    ...     stack = []
    ...     while node:
    ...         while node.left:
    ...             stack.append(node)
    ...             node = node.left
    ...         yield node.label
    ...         while not node.right:
    ...             try:
    ...                 node = stack.pop()
    ...             except IndexError:
    ...                 return
    ...             yield node.label
    ...         node = node.right

    >>> # Exercise the non-recursive generator.
    >>> for x in t:
    ...     print x,
    A B C D E F G H I J K L M N O P Q R S T U V W X Y Z

"""

# A few examples from Iterator-List and Python-Dev email.

email_tests = """

The difference between yielding None and returning it.

>>> def g():
...     for i in range(3):
...         yield None
...     yield None
...     return
>>> list(g())
[None, None, None, None]

Ensure that explicitly raising StopIteration acts like any other exception
in try/except, not like a return.

>>> def g():
...     yield 1
...     try:
...         raise StopIteration
...     except:
...         yield 2
...     yield 3
>>> list(g())
[1, 2, 3]
"""

# Fun tests (for sufficiently warped notions of "fun").

fun_tests = """

Build up to a recursive Sieve of Eratosthenes generator.

>>> def firstn(g, n):
...     return [g.next() for i in range(n)]

>>> def intsfrom(i):
...     while 1:
...         yield i
...         i += 1

>>> firstn(intsfrom(5), 7)
[5, 6, 7, 8, 9, 10, 11]

>>> def exclude_multiples(n, ints):
...     for i in ints:
...         if i % n:
...             yield i

>>> firstn(exclude_multiples(3, intsfrom(1)), 6)
[1, 2, 4, 5, 7, 8]

>>> def sieve(ints):
...     prime = ints.next()
...     yield prime
...     not_divisible_by_prime = exclude_multiples(prime, ints)
...     for p in sieve(not_divisible_by_prime):
...         yield p

>>> primes = sieve(intsfrom(2))
>>> firstn(primes, 20)
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
"""

__test__ = {"tut": tutorial_tests,
            "pep": pep_tests,
            "email": email_tests,
            "fun": fun_tests}

# Magic test name that regrtest.py invokes *after* importing this module.
# This worms around a bootstrap problem.
# Note that doctest and regrtest both look in sys.argv for a "-v" argument,
# so this works as expected in both ways of running regrtest.
def test_main():
    import doctest, test_generators
    doctest.testmod(test_generators)

# This part isn't needed for regrtest, but for running the test directly.
if __name__ == "__main__":
    test_main()
