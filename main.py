#!/usr/bin/python3
from enum import Enum
from abc import ABCMeta


class Comparable(metaclass=ABCMeta):
    def __eq__(self, other):
        if other is None:
            return False
        d1 = self.__dict__
        d2 = other.__dict__
        if len(d1) != len(d2):
            return False
        for k1 in d1.keys():
            v1 = d1.get(k1)
            v2 = d2.get(k1)
            # print(k1)
            # print(f'⌜{v1}\n⌞{v2}')
            if isinstance(v1, Any) and unifications.get(v1.element) is not None:
                v1 = unifications.get(v1.element)
            if isinstance(v2, Any) and unifications.get(v2.element) is not None:
                v2 = unifications.get(v2.element)

            if v1 != v2:
                return False
        return True

    def __hash__(self):
        return sum([hash(e) for e in self.__dict__])


class Statement(Enum):
    IS_AUTHOR_OF = 1
    IS_MAIN_ACTOR_OF = 2
    LIVED_EARLIER_THAN = 3

    def equals(self, other):
        return self == other


class DoublePredicate(Comparable):
    def __init__(self, x, statement: Statement, y, is_transitive=False):
        self.statement = statement
        self.X = x
        self.Y = y
        self.is_transitive = is_transitive

    def __str__(self):
        return f'({self.X} {self.statement} {self.Y})'


class Characters(Enum):
    PUSHKIN = 1
    DOSTOEVSKY = 2
    PRESTUPLENIE_I_NAKAZANIE = 3
    VUSTREL = 4
    IDIOT = 5
    SILVIO = 6
    RASCOLNIKOV = 7
    MISHKIN = 8

    def equals(self, other):
        return self == other


class Answer(Comparable):
    def __init__(self, caption):
        self.caption = caption

    def __str__(self):
        return f'answer={self.caption}'


class DoubleOperator(Comparable):
    def __init__(self, first, second):
        self.second = second
        self.first = first


class And(DoubleOperator):
    def __str__(self):
        return f'({self.first} ^ {self.second})'


class Or(DoubleOperator):
    def __str__(self):
        return f'({self.first} | {self.second})'


class SingleOperator(Comparable):
    def __init__(self, element):
        self.element = element


class Not(SingleOperator):
    def __str__(self):
        return f'-{self.element}'


class Any(Comparable):
    def __init__(self, element):
        self.element = element

    def __str__(self):
        return f'' \
               f'' \
               f'{self.element if unifications.get(self.element) is None else unifications[self.element]}:A'


def invert(query):
    if isinstance(query, DoubleOperator):
        first, second = query.first, query.second
        if isinstance(query, And):
            return Or(invert(first), invert(second))
        elif isinstance(query, Or):
            return And(invert(first), invert(second))
    elif isinstance(query, Not):
        return query.element
    elif isinstance(query, DoublePredicate):
        return Not(query)
    elif isinstance(query, Answer):
        return query


def enroll(assumption):
    if isinstance(assumption, Or):
        return [*enroll(assumption.first), *enroll(assumption.second)]
    return [assumption]


unifications = dict()
def unificate(p1: DoublePredicate, p2: DoublePredicate):
    pc1 = p1
    if isinstance(p1, Not):
        pc1 = p1.element

    pc2 = p2
    if isinstance(p2, Not):
        pc2 = p2.element

    if isinstance(pc1.X, Any):
        if unifications.get(pc1.X.element) is not None:
            pc1.X = unifications[pc1.X.element]
        elif pc1.Y == pc2.Y:
            unifications[pc1.X.element] = pc2.X
            pc1.X = pc2.X
    if isinstance(pc1.Y, Any):
        if unifications.get(pc1.Y.element) is not None:
            pc1.Y = unifications[pc1.Y.element]
        elif pc1.X == pc2.X:
            unifications[pc1.Y.element] = pc2.Y
            pc1.Y = pc2.Y

    if isinstance(pc2.X, Any):
        if unifications.get(pc2.X.element) is not None:
            pc2.X = unifications[pc2.X.element]
        elif pc2.Y == pc1.Y:
            unifications[pc2.X.element] = pc1.X
            pc2.X = pc1.X
    if isinstance(pc2.Y, Any):
        if unifications.get(pc2.Y.element) is not None:
            pc2.Y = unifications[pc2.Y.element]
        elif pc2.X == pc1.X:
            unifications[pc2.Y.element] = pc1.Y
            pc2.Y = pc1.Y

    return p1, p2


def resolute(first, second):
    resoluted = []
    for f in enroll(first):
        if isinstance(f, Answer):
            continue
        for s in enroll(second):
            if isinstance(s, Answer):
                continue
            f, s = unificate(f, s)

            # print(f'{f}\n{invert(s)}\n\n\n')

            if f in resoluted:
                continue

            if f == invert(s):
                resoluted.append(f)
            else:
                pass

    a = None
    b = None
    for f in enroll(first):
        if f not in resoluted:
            if a is None:
                a = f
            else:
                a = Or(a, f)
    for s in enroll(second):
        if invert(s) not in resoluted:
            if b is None:
                b = s
            else:
                b = Or(b, s)

    return a, b


def resolution(assumptions):
    prevlen = len(assumptions)
    while True:
        for i in range(len(assumptions)):
            assumption1 = assumptions[i]
            for j in range(len(assumptions)):
                assumption2 = assumptions[j]
                if assumption1 == assumption2:
                    continue
                if assumption1 is None or assumption2 is None:
                    continue
                r1, r2 = resolute(assumption1, assumption2)
                assumptions[i] = r1
                assumptions[j] = r2
        tmp = []
        for i in range(len(assumptions)):
            if assumptions[i] is not None:
                tmp.append(assumptions[i])
        assumptions = tmp

        if prevlen == len(assumptions):
            break
        prevlen = len(assumptions)
    return assumptions


def main():
    c = Characters
    s = Statement
    p = DoublePredicate
    database = [
        p(c.PUSHKIN, s.IS_AUTHOR_OF, c.VUSTREL),
        p(c.DOSTOEVSKY, s.IS_AUTHOR_OF, c.PRESTUPLENIE_I_NAKAZANIE),
        p(c.DOSTOEVSKY, s.IS_AUTHOR_OF, c.IDIOT),
        p(c.SILVIO, s.IS_MAIN_ACTOR_OF, c.VUSTREL),
        p(c.RASCOLNIKOV, s.IS_MAIN_ACTOR_OF, c.PRESTUPLENIE_I_NAKAZANIE),
        p(c.MISHKIN, s.IS_MAIN_ACTOR_OF, c.IDIOT),
        p(c.PUSHKIN, s.LIVED_EARLIER_THAN, c.DOSTOEVSKY)
    ]

    query = And(
                And(
                    And(
                        Answer(Any('X')),
                        p(Any('X'), s.LIVED_EARLIER_THAN, Any('Y'))
                    ),
                    p(Any('Y'), s.IS_AUTHOR_OF, Any('Z'))
                ),
                p(c.MISHKIN, s.IS_MAIN_ACTOR_OF, Any('Z'))
            )

    q = invert(query)
    database.append(q)
    resoluted = resolution(database)
    # for r in resoluted:
        # print(r)

    print(f'Answer is: {unifications["X"]}')
    print(f'Unifications: {unifications}')

    assert unifications["X"] == c.PUSHKIN
    assert unifications["Y"] == c.DOSTOEVSKY
    assert unifications["Z"] == c.IDIOT


if __name__ == '__main__':
    main()
