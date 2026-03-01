from pydantic import BaseModel, ConfigDict
class A(BaseModel):
    model_config = ConfigDict(extra="allow")
a = A(**{"c": {"d": 1}})
print(type(a.c))
