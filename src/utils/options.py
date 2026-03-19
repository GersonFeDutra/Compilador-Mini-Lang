class Options:
    NONE = 0
    LOG = 1  # Log to stderr
    NO_OPTIMIZE = 2  # Optimize parser: use accumulator
    NO_EXCEPT_TREATMENT = (
        4  # Don't catch exceptions in gen() and start() to allow debugging
    )

    def __or__(self, other) -> int:
        return self.value | other.value

    def __and__(self, other) -> int:
        return self.value & other.value

    def __bool__(self) -> bool:
        return self.value != 0

    def __xor__(self, other) -> int:
        return self.value ^ other.value

    def __invert__(self) -> int:
        return ~self.value

    def __init__(self, value: int) -> None:
        super().__init__()
        self.value = value
