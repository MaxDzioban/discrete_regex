from __future__ import annotations
from abc import ABC, abstractmethod

class State(ABC):
    def __init__(self) -> None:
        self.next_states: list[State] = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """Check if this state matches the given character"""
        pass
    
    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")

class StartState(State):
    def __init__(self) -> None:
        super().__init__()

    def check_self(self, char: str) -> bool:
        # Start state does not consume any character
        return False

class TerminationState(State):
    def __init__(self) -> None:
        super().__init__()

    def check_self(self, char: str) -> bool:
        # Termination state does not consume characters
        return False

class DotState(State):
    def __init__(self) -> None:
        super().__init__()

    def check_self(self, char: str) -> bool:
        # Matches any single character
        return True

class AsciiState(State):
    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.curr_sym = symbol

    def check_self(self, char: str) -> bool:
        return char == self.curr_sym

class StarState(State):
    def __init__(self, checking_state: State) -> None:
        super().__init__()
        self.next_states: list[State] = []
        self.checking_state = checking_state

    def check_self(self, char: str) -> bool:
        # Handled by engine, state itself does not directly match
        return False

class PlusState(State):
    def __init__(self, checking_state: State) -> None:
        super().__init__()
        self.next_states: list[State] = []
        self.checking_state = checking_state

    def check_self(self, char: str) -> bool:
        # Handled by engine, state itself does not directly match
        return False

class RegexFSM:
    curr_state: State = StartState()

    def __init__(self, regex_expr: str) -> None:
        self.states: list[State] = [StartState()]
        i = 0
        while i < len(regex_expr):
            c = regex_expr[i]
            if c == '.':
                base = DotState()
            elif c not in ['*', '+'] and c.isascii():
                base = AsciiState(c)
            else:
                raise AttributeError(f"Unsupported or misplaced character '{c}' in pattern")
            quant = None
            if i + 1 < len(regex_expr) and regex_expr[i+1] in ['*', '+']:
                quant = regex_expr[i+1]
                i += 1
            if quant == '*':
                self.states.append(StarState(base))
            elif quant == '+':
                self.states.append(PlusState(base))
            else:
                self.states.append(base)
            i += 1
        self.states.append(TerminationState())


    def check_string(self, s: str) -> bool:
        def dp(idx: int, pos: int) -> bool:
            state = self.states[idx]
            # пропустити початковий стан
            if isinstance(state, StartState):
                return dp(idx+1, pos)
            # якщо це фінальний стан і рядок закінчився
            if isinstance(state, TerminationState):
                return pos == len(s)
            if isinstance(state, StarState):
                if dp(idx+1, pos):
                    return True
                if pos < len(s) and state.checking_state.check_self(s[pos]):
                    return dp(idx, pos+1)
                return False
            if isinstance(state, PlusState):
                if pos >= len(s) or not state.checking_state.check_self(s[pos]):
                    return False
                if dp(idx, pos+1):
                    return True
                return dp(idx+1, pos+1)
            if pos < len(s) and state.check_self(s[pos]):
                return dp(idx+1, pos+1)
            return False
        return dp(0, 0)


if __name__ == "__main__":
    regex_pattern = "a*4.+hi"
    regex_compiled = RegexFSM(regex_pattern)
    print(regex_compiled.check_string("aaaaaa4uhi"))
    print(regex_compiled.check_string("4uhi"))
    print(regex_compiled.check_string("meow"))
