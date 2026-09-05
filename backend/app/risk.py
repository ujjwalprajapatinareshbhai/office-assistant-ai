import json

from app.agent import llm


async def check_tool_risk(
    user_request: str,
    tool_name: str,
    tool_description: str,
    arguments: dict,
) -> dict:

    prompt = f"""
You are the safety evaluator for an AI office assistant.

Your job is to determine whether HUMAN APPROVAL is required
for THIS SPECIFIC TOOL CALL that is about to execute.

IMPORTANT:

Evaluate the CURRENT tool call only.

Do NOT assign HIGH risk to a read-only tool merely because
the user's overall request contains a later action such as
sending an email, deleting something, or modifying data.

For example:

User request:
"Find employee 1 and send his details by email."

Current tool:
find_employee_id

The find_employee_id operation only reads employee information,
so it should normally be LOW risk.

Later, when the email tool is executed:

send_a_email

THAT tool call should be HIGH risk because it sends information
externally.

--------------------------------------------------
CURRENT TOOL CALL
--------------------------------------------------

Tool name:
{tool_name}

Tool description:
{tool_description}

Tool arguments:
{arguments}

--------------------------------------------------
USER REQUEST
--------------------------------------------------

{user_request}

--------------------------------------------------
RISK RULES
--------------------------------------------------

LOW RISK:

Use LOW when the CURRENT tool call is only:

- reading information
- searching information
- listing files
- reading files
- retrieving employee information
- retrieving database records
- checking weather
- calculating values
- checking status
- performing another read-only operation

LOW risk means the current tool call itself does not create
a significant external side effect.

--------------------------------------------------

MEDIUM RISK:

Use MEDIUM when the CURRENT tool call changes data but the
consequences are relatively limited and reversible.

Examples:

- updating a non-critical record
- renaming a file
- moving a file
- creating a normal file

--------------------------------------------------

HIGH RISK:

Use HIGH when the CURRENT tool call itself:

- deletes data
- permanently removes information
- sends an email
- sends an external message
- sends information outside the organization
- exposes sensitive information externally
- changes important employee information
- changes salary or financial information
- performs a financial transaction
- creates an irreversible action
- causes a significant external side effect

--------------------------------------------------
IMPORTANT EXAMPLE
--------------------------------------------------

User request:

"Find employee 1 and send his details to john@gmail.com"

Current tool:

find_employee_id

Arguments:

{{"employee_id": 1}}

Correct result:

{{
    "requires_approval": false,
    "risk": "LOW",
    "reason": "This operation only reads employee information."
}}

Later current tool:

send_a_email

Correct result:

{{
    "requires_approval": true,
    "risk": "HIGH",
    "reason": "This operation sends employee information to an external email address."
}}

--------------------------------------------------
ANOTHER EXAMPLE
--------------------------------------------------

User request:

"Delete employee 1"

Current tool:

delete_employee_by_id

Correct result:

{{
    "requires_approval": true,
    "risk": "HIGH",
    "reason": "This operation permanently deletes an employee record."
}}

--------------------------------------------------

The CURRENT TOOL CALL is the most important factor.

Do not predict or approve/block future tool calls.

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{{
    "requires_approval": true,
    "risk": "HIGH",
    "reason": "Short explanation"
}}

OR:

{{
    "requires_approval": false,
    "risk": "LOW",
    "reason": "Short explanation"
}}
"""

    response = await llm.ainvoke(prompt)

    content = response.content

    # ---------------------------------------------
    # Normalize response
    # ---------------------------------------------

    if isinstance(content, list):

        text = ""

        for item in content:

            if isinstance(item, dict):

                if item.get("type") == "text":

                    text += item.get(
                        "text",
                        ""
                    )

            else:

                text += str(item)

        content = text

    content = str(content).strip()

    # ---------------------------------------------
    # Remove accidental markdown
    # ---------------------------------------------

    if content.startswith("```"):

        content = content.replace(
            "```json",
            ""
        )

        content = content.replace(
            "```",
            ""
        )

        content = content.strip()

    # ---------------------------------------------
    # Parse JSON
    # ---------------------------------------------

    try:

        result = json.loads(content)

    except json.JSONDecodeError:

        # -----------------------------------------
        # FAIL SAFE
        # -----------------------------------------

        return {
            "requires_approval": True,
            "risk": "HIGH",
            "reason": (
                "The safety evaluator could not "
                "reliably determine the risk."
            ),
        }

    # ---------------------------------------------
    # Normalize risk
    # ---------------------------------------------

    risk = str(
        result.get(
            "risk",
            "HIGH"
        )
    ).upper()

    if risk not in {
        "LOW",
        "MEDIUM",
        "HIGH",
    }:

        risk = "HIGH"

    # ---------------------------------------------
    # Validate approval
    # ---------------------------------------------

    requires_approval = bool(
        result.get(
            "requires_approval",
            True
        )
    )

    # ---------------------------------------------
    # Safety consistency
    # ---------------------------------------------

    # HIGH risk must always require approval.

    if risk == "HIGH":

        requires_approval = True

    # ---------------------------------------------
    # Return normalized result
    # ---------------------------------------------

    return {
        "requires_approval": requires_approval,

        "risk": risk,

        "reason": result.get(
            "reason",
            "Safety evaluation requires approval."
        ),
    }