from dataclasses import dataclass


@dataclass(frozen=True)
class AuthContext:
    """
    Authentication context data class.

    Stores user authentication information including user ID and scopes.
    """
    user_id: int
    scopes: set[str]

    def has(self, scope: str) -> bool:
        """
        Check if the user has a specific scope.

        Parameters
        ----------
        scope : str
            Scope to check

        Returns
        ----------
        bool
            True if user has the scope, False otherwise.
        """
        return scope in self.scopes