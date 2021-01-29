"""
Package for the application library(Mulit-Column Primary Keys)
"""

from .cpkmodel import CPkModel
from .cpkquery import (
    CPkQuery,
    CPkDeleteQuery,
    CPkUpdateQuery,
    CPkQuerySet,
)

__all__ = [
    'CPkModel','CPkQuery','CPkDeleteQuery','CPkUpdateQuery','CPkQuerySet'
]