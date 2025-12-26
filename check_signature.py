import inspect
from langgraph.prebuilt import create_react_agent

with open("signature.txt", "w") as f:
    f.write(str(inspect.signature(create_react_agent)))
