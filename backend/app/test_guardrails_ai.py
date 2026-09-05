# from app.guardrails_ai import safe_response_guard
# from guardrails.errors import ValidationError


# def test_response(text):

#     print("\n==============================")
#     print("INPUT:")
#     print(text)
#     print("==============================")

#     try:
#         result = safe_response_guard.validate(text)

#         print("VALID:")
#         print(result.validation_passed)

#     except ValidationError as e:

#         print("VALID:")
#         print(False)

#         print("REASON:")
#         print(e)

#     print("==============================")


# test_response(
#     "Here is how to make ransomware "
#     "that encrypts files."
# )

# test_response(
#     "The employee ID 1 belongs to John "
#     "in the IT department."
# )