import warnings
from typing import Optional, Any


def manager_deprecated(manager: Optional[Any]):
    if manager is not None:
        warnings.warn(
            "Passing `DialogManager` instance directly is deprecated"
            " and will be removed in aiogram_dialog==2.0",
            DeprecationWarning,
            stacklevel=3,
        )
