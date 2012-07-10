# This file is part of Patsy
# Copyright (C) 2012 Nathaniel Smith <njs@pobox.com>
# See file COPYING for license information.

# Miscellaneous utilities that are useful to users (as compared to
# patsy.util, which is misc. utilities useful for implementing patsy).

# These are made available in the patsy.* namespace
__all__ = ["balanced", "demo_data"]

import numpy as np
from patsy import PatsyError
from patsy.compat import itertools_product

def balanced(**kwargs):
    """balanced(factor_name=num_levels, [factor_name=num_levels, ..., repeat=1])

    Create simple balanced factorial designs for testing.

    Given some factor names and the number of desired levels for each,
    generates a balanced factorial design in the form of a data
    dictionary. For example:

    .. ipython::

       In [1]: balanced(a=2, b=3)
       Out[1]:
       {'a': ['a1', 'a1', 'a1', 'a2', 'a2', 'a2'],
        'b': ['b1', 'b2', 'b3', 'b1', 'b2', 'b3']}

    By default it produces exactly one instance of each combination of levels,
    but if you want multiple replicates this can be accomplished via the
    `repeat` argument:

    .. ipython::

       In [2]: balanced(a=2, b=2, repeat=2)
       Out[2]:
       {'a': ['a1', 'a1', 'a2', 'a2', 'a1', 'a1', 'a2', 'a2'],
        'b': ['b1', 'b2', 'b1', 'b2', 'b1', 'b2', 'b1', 'b2']}
    """
    repeat = kwargs.pop("repeat", 1)
    levels = []
    names = sorted(kwargs)
    for name in names:
        level_count = kwargs[name]
        levels.append(["%s%s" % (name, i) for i in xrange(1, level_count + 1)])
    # zip(*...) does an "unzip"
    values = zip(*itertools_product(*levels))
    data = {}
    for name, value in zip(names, values):
        data[name] = list(value) * repeat
    return data

def test_balanced():
    data = balanced(a=2, b=3)
    assert data["a"] == ["a1", "a1", "a1", "a2", "a2", "a2"]
    assert data["b"] == ["b1", "b2", "b3", "b1", "b2", "b3"]
    data = balanced(a=2, b=3, repeat=2)
    assert data["a"] == ["a1", "a1", "a1", "a2", "a2", "a2",
                         "a1", "a1", "a1", "a2", "a2", "a2"]
    assert data["b"] == ["b1", "b2", "b3", "b1", "b2", "b3",
                         "b1", "b2", "b3", "b1", "b2", "b3"]

def demo_data(*names, **kwargs):
    """demo_data(*names, nlevels=2, min_rows=5)

    Create simple categorical/numerical demo data.

    Pass in a set of variable names, and this function will return a simple
    data set using those variable names.

    Names whose first letter falls in the range "a" through "m" will be made
    categorical (with `nlevels` levels). Those that start with a "p" through
    "z" are numerical.

    We attempt to produce a balanced design on the categorical variables,
    repeating as necessary to generate at least `min_rows` data
    points. Categorical variables are returned as a list of strings.

    Numerical data is generated by sampling from a normal distribution. A
    fixed random seed is used, so that identical calls to demo_data() will
    produce identical results. Numerical data is returned in a numpy array.

    Example:

    .. ipython:

       In [1]: patsy.demo_data("a", "b", "x", "y")
       Out[1]: 
       {'a': ['a1', 'a1', 'a2', 'a2', 'a1', 'a1', 'a2', 'a2'],
        'b': ['b1', 'b2', 'b1', 'b2', 'b1', 'b2', 'b1', 'b2'],
        'x': array([ 1.76405235,  0.40015721,  0.97873798,  2.2408932 ,
                     1.86755799, -0.97727788,  0.95008842, -0.15135721]),
        'y': array([-0.10321885,  0.4105985 ,  0.14404357,  1.45427351,
                     0.76103773,  0.12167502,  0.44386323,  0.33367433])}
    """
    nlevels = kwargs.pop("nlevels", 2)
    min_rows = kwargs.pop("min_rows", 5)
    if kwargs:
        raise TypeError, "unexpected keyword arguments %r" % (kwargs)
    numerical = set()
    categorical = {}
    for name in names:
        if name[0] in "abcdefghijklmn":
            categorical[name] = nlevels
        elif name[0] in "pqrstuvwxyz":
            numerical.add(name)
        else:
            raise PatsyError, "bad name %r" % (name,)
    balanced_design_size = np.prod(categorical.values())
    repeat = int(np.ceil(min_rows * 1.0 / balanced_design_size))
    num_rows = repeat * balanced_design_size
    data = balanced(repeat=repeat, **categorical)
    r = np.random.RandomState(0)
    for name in sorted(numerical):
        data[name] = r.normal(size=num_rows)
    return data
    
def test_demo_data():
    d1 = demo_data("a", "b", "x")
    assert sorted(d1.keys()) == ["a", "b", "x"]
    assert d1["a"] == ["a1", "a1", "a2", "a2", "a1", "a1", "a2", "a2"]
    assert d1["b"] == ["b1", "b2", "b1", "b2", "b1", "b2", "b1", "b2"]
    assert d1["x"].dtype == np.dtype(float)
    assert d1["x"].shape == (8,)

    d2 = demo_data("x", "y")
    assert sorted(d2.keys()) == ["x", "y"]
    assert len(d2["x"]) == len(d2["y"]) == 5

    assert len(demo_data("x", min_rows=10)["x"]) == 10
    assert len(demo_data("a", "b", "x", min_rows=10)["x"]) == 12
    assert len(demo_data("a", "b", "x", min_rows=10, nlevels=3)["x"]) == 18

    from nose.tools import assert_raises
    assert_raises(PatsyError, demo_data, "a", "b", "__123")
    assert_raises(TypeError, demo_data, "a", "b", asdfasdf=123)
