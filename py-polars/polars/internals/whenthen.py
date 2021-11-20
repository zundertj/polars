from typing import Any, Union

try:
    from polars.polars import when as pywhen

    _DOCUMENTING = False
except ImportError:
    _DOCUMENTING = True

from polars import internals as pli

__all__ = ["when"]


class WhenThenThen:
    """
    Utility class. See the `when` function.
    """

    def __init__(self, pywhenthenthen: Any):
        self.pywenthenthen = pywhenthenthen

    def when(self, predicate: pli.Expr) -> "WhenThenThen":
        """
        Start another when, then, otherwise layer.
        """
        return WhenThenThen(self.pywenthenthen.when(predicate._pyexpr))

    def then(self, expr: Union[pli.Expr, int, float, str]) -> "WhenThenThen":
        """
        Values to return in case of the predicate being `True`.

        See Also: the `when` function.
        """
        expr_ = pli.expr_to_lit_or_expr(expr)
        return WhenThenThen(self.pywenthenthen.then(expr_._pyexpr))

    def otherwise(self, expr: Union[pli.Expr, int, float, str]) -> pli.Expr:
        """
        Values to return in case of the predicate being `False`.

        See Also: the `when` function.
        """
        expr = pli.expr_to_lit_or_expr(expr)
        return pli.wrap_expr(self.pywenthenthen.otherwise(expr._pyexpr))


class WhenThen:
    """
    Utility class. See the `when` function.
    """

    def __init__(self, pywhenthen: Any):
        self._pywhenthen = pywhenthen

    def when(self, predicate: pli.Expr) -> WhenThenThen:
        """
        Start another when, then, otherwise layer.
        """
        return WhenThenThen(self._pywhenthen.when(predicate._pyexpr))

    def otherwise(self, expr: Union[pli.Expr, int, float, str]) -> pli.Expr:
        """
        Values to return in case of the predicate being `False`.

        See Also: the `when` function.
        """
        expr = pli.expr_to_lit_or_expr(expr)
        return pli.wrap_expr(self._pywhenthen.otherwise(expr._pyexpr))


class When:
    """
    Utility class. See the `when` function.
    """

    def __init__(self, pywhen: "pywhen"):
        self._pywhen = pywhen

    def then(self, expr: Union[pli.Expr, int, float, str]) -> WhenThen:
        """
        Values to return in case of the predicate being `True`.

        See Also: the `when` function.
        """
        expr = pli.expr_to_lit_or_expr(expr)
        pywhenthen = self._pywhen.then(expr._pyexpr)
        return WhenThen(pywhenthen)


def when(expr: pli.Expr) -> When:
    """
    Start a when, then, otherwise expression.

    Examples
    --------

    Below we add a column with the value 1, where column "foo" > 2 and the value -1 where it isn't.

    >>> lf.with_column(
        when(col("foo") > 2)
        .then(lit(1))
        .otherwise(lit(-1))
    )

    Or with multiple `when, thens` chained:

    >>> lf.with_column(
        when(col("foo") > 2).then(1)
        when(col("bar") > 2).then(4)
        .otherwise(-1)
    )
    """
    expr = pli.expr_to_lit_or_expr(expr)
    pw = pywhen(expr._pyexpr)
    return When(pw)
