__version__ = "0.0.1"
__author__ = "osoken"
__description__ = "ruro is a package which supports pipe notation for functions."
__long_description__ = __description__
__email__ = "osoken.devel@outlook.jp"
__package_name__ = "ruro"


try:
    from .base import (
        Entry,
        Pipeline,
        Exit,
        IterableEntry,
        IterablePipeline,
        IterableExit,
        BaseEntry,
        BasePipeline,
        BaseExit,
        BaseIterableEntry,
        BaseIterablePipeline,
        BaseIterableExit,
    )
    from .basics import Constant, IterableConstant, Exec, Map, Filter, Sum
    from . import decorators

    __all__ = [
        "Entry",
        "Pipeline",
        "Exit",
        "IterableEntry",
        "IterablePipeline",
        "IterableExit",
        "IterableConstant",
        "BaseEntry",
        "BasePipeline",
        "BaseExit",
        "BaseIterableEntry",
        "BaseIterablePipeline",
        "BaseIterableExit",
        "Constant",
        "Exec",
        "Map",
        "Filter",
        "Sum",
        "decorators",
    ]
except ImportError:
    pass
