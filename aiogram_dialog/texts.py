from dataclasses import dataclass


@dataclass
class DialogTexts:
    back: str = "< Back"
    skip: str = "Skip >"
    done: str = "Done"
    cancel: str = "Cancel"
