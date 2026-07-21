from chimera.core.interface import Interface


class Operator(Interface):
    """Interface for telescope operators."""

    def request(self, type: str, msg: str | None) -> bool:
        """
        Request operator intervention.

        @param type: The type of request (e.g., "confirm", "acquire", etc.).
        @type  type: str

        @param msg: An optional message to display to the operator.
        @type  msg: str | None

        @return: True if the operator approved the request, False otherwise.
        @rtype: bool
        """
