from dataclasses import dataclass


@dataclass(frozen=True)
class AuthContext:
    user_id: int
    scopes: set[str]

    def has(self, scope: str) -> bool:
        return scope in self.scopes