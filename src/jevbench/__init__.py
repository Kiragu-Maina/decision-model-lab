"""Jev-style typed decision benchmark."""

from .corpus import CORPUS_VERSION, build_corpus
from .runner import run_benchmark

__all__ = ["CORPUS_VERSION", "build_corpus", "run_benchmark"]
__version__ = "0.1.0"
