from guardrails import Guard, register_validator
from guardrails.validator_base import Validator, PassResult, FailResult


@register_validator(
    name="safe_response_validator",
    data_type="string",
)
class SafeResponseValidator(Validator):
    """
    Guardrails AI validator for detecting
    obviously dangerous AI responses.
    """

    def validate(self, value, metadata=None):

        text = str(value).lower()

        dangerous_patterns = [
            "how to make ransomware",
            "how to create ransomware",
            "how to build malware",
            "steal passwords",
            "steal credentials",
            "keylogger code",
            "deploy malware",
            "create a virus",
            "create a trojan",
        ]

        for pattern in dangerous_patterns:

            if pattern in text:

                return FailResult(
                    error_message=(
                        "Response contains potentially "
                        "dangerous instructions."
                    )
                )

        return PassResult()


safe_response_guard = Guard.for_string(
    validators=[
        SafeResponseValidator()
    ],
    string_description="AI assistant response",
)