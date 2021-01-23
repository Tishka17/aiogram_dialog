import operator
from typing import Union, Callable


class Whenable():
    def __init__(self, when: Union[str, Callable, None] = None):
        if isinstance(when, str):
            self.condition = operator.itemgetter(when)
        else:
            self.condition = when

    def is_(self, data):
        return (not self.condition) or self.condition(data)
