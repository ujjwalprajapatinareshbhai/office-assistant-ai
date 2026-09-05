from app.graph import graph
from langchain_core.messages import HumanMessage

response = graph.invoke(
    {
        "messages": [
            HumanMessage(
                content="Hello"
            )
        ]
    }
)

print(response["messages"][-1].content)

# import inspect
# from app.agent import llm

# from pydantic import BaseModel
# from app.agent import llm


# class Person(BaseModel):
#     name: str
#     city: str


# structured_llm = llm.with_structured_output(
#     Person,
#     include_raw=True
# )

# result = structured_llm.invoke(
#     "My name is Ujjwal and I live in Pune."
# )

# print(result)