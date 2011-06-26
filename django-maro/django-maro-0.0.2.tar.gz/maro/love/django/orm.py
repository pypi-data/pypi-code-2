# -*- coding:utf-8 -*- 
from django.db.models import Q

AND, OR = Q.__and__, Q.__or__
NOT = lambda q: ~q

class Formula(object):
    """タプルで構成される式の表現を短縮する為のオブジェクトです。
    以下の機能を持ちます。

    + prefix付きでQを生成できます(CONSTメソッド)。
    + コンストラクタに渡した辞書を属性として参照できます。
    + 真偽判定を簡潔に行うことができます(IFメソッド)。
    """
    def __init__(self, dct, prefix=""):
        self.dct = dct
        self.prefix = prefix

    @property
    def CONST(self):
        def cnst(**kwargs):
            keys = [self.prefix + k for k in kwargs.keys()]
            return Q(**dict(zip(keys, kwargs.values())))
        return cnst

    @property
    def IF(self):
        return lambda b: b

    def __getattr__(self, name):
        return self.dct.get(name)

def formula(cons, value, prefix=""):
    """引数consからQを生成して返します。
    consは(AND, "foo", "bar", ...)という形式のタプルを期待します。
    """
    operator, fields = cons[0], cons[1:]
    if not callable(operator): 
        # ただのタプルが来たらORを使うよう初期化します。
        operator, fields = OR, cons
    if operator == NOT:
        return operator(formula(fields, value, prefix))
    def operand(field, value):
        if isinstance(field, basestring):
            # 文字列が来たら即座にQを作ります。
            return Q(**{prefix+field : value})
        elif type(field) == Q:
            # Qが来たらQをそのまま使います。
            return field
        else:
            # それ以外が来たら条件式とみなして再評価します。
            return formula(field, value, prefix)
    return reduce(operator, [operand(field, value) for field in fields])

def query(criterion, prefix="", ope=AND):
    """formula関数で処理可能なタプルを一括評価してQを生成します。
    -----------------
    usage
    -----------------
    >>> prefix = "fk__"
    >>> f = Formula(dict(first_name="imagawa", last_name="yoshimoto",
    ...                     age=30, year_of_birth=1519), prefix)
    >>> IF = f.IF
    >>> CONST = f.CONST
    >>> # このようなタプルで構成される式を作ってquery関数に渡すとQオブジェクトが生成されます。
    >>> criterion = (
    ...     (IF(f.first_name), f.first_name, (AND, "daimyo__sei", "hatamoto__sei")),
    ...     (IF(f.last_name), f.last_name, (OR, "daimyo__mei", "hatamoto__mei")),
    ... )
    >>> q1 = query(criterion, prefix)
    >>> q2 = ((Q(fk__daimyo__sei="imagawa") & Q(fk__hatamoto__sei="imagawa"))
    ...         & (Q(fk__daimyo__mei="yoshimoto") | Q(fk__hatamoto__mei="yoshimoto")))
    >>> str(q1) == str(q2)
    True
    
    >>> # タプルの第2要素がQオブジェクトの場合はそのまま使います。
    >>> criterion = (
    ...     (IF(not f.job), CONST(is_neet=True)),
    ... )
    >>> str(query(criterion, prefix)) == str(Q(fk__is_neet=True))
    True
    
    >>> # つまり、このような使い方も可能です。
    >>> q3 = (CONST(django="cool") & CONST(pyramid="very cool")) | CONST(django="easy")
    >>> criterion = (
    ...     (IF(f.age > 25 or f.salary > 300), q3),
    ... )
    >>> str(query(criterion, prefix)) == str(q3)
    True
    
    >>> # 否定条件を作るとき、Qオブジェクトの~(チルダ)を使えばいいですが、
    >>> # NOTを用いた式を使用することも可能です。
    >>> criterion = (
    ...     (IF(True), "kemari", (NOT, (OR, "hobby", "like"))),
    ... )
    >>> str(query(criterion, prefix)) == str(~(CONST(hobby="kemari") | CONST(like="kemari")))
    True

    >>> # 一つも条件を満たさなかった場合、Noneを返します。
    >>> criterion = (
    ...     (IF(False), Q()), (False, Q()), ("", Q()),
    ... )
    >>> query(criterion, prefix) is None
    True
    """
    result = []
    append = result.append
    for args in criterion:
        if_ = args[0]
        if not if_:
            continue

        if len(args) == 2:
            value = args[1]
            """
            第2要素がQであり、かつ要素数が2つならばQを結合して次のループに飛ばします。
            例: ("foo is not null", Q(foo__isnull=False))
            """
            if type(value) == Q:
                append(value)
                continue
        else:
            value, cons = args[1:]
        
        new_q = formula(cons, value, prefix)
        append(new_q)
    return reduce(ope, [x for x in result if x]) if result else None

def static_query(dct, criterion, prefix="", ope=AND):
    """検索条件dctと所定の条件式criterionからQオブジェクトを生成する。
    タプルの第1要素を文字列(辞書のキー)とみなして処理する点がqueryと違います。
    ----------
    usage
    ----------
    >>> criterion = (
    ...     ("foo", (AND, "name", "name_kana")),
    ...     ("bar", (OR, "code", "customer__code")),
    ...     ("baz", ( # ただのタプルを渡すとORで処理されます。
    ...                 (AND, "price", "item__price"),
    ...                 (AND, "order__number", "order__index")
    ...             )
    ...     ),
    ... )
    >>> dct = dict(foo="foo", baz=0)
    >>> q1 = static_query(dct, criterion, "fk__")
    >>> q2 = ((Q(fk__name="foo") & Q(fk__name_kana="foo"))
    ...         & ((Q(fk__price=0) & Q(fk__item__price=0))
    ...             | (Q(fk__order__number=0) & Q(fk__order__index=0))))
    >>> str(q1) == str(q2)
    True
    """
    result = []
    append = result.append
    for key, cons in criterion:
        value = dct.get(key)
        if value is None or value == "":
            # Noneまたは空文字列はスキップします。0やFalseはスキップしません。
            continue
        new_q = formula(cons, value, prefix)
        append(new_q)
    return reduce(ope, [x for x in result if x]) if result else None

if __name__ == "__main__":
    import doctest
    doctest.testmod()

