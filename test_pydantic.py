from pydantic import BaseModel, ConfigDict
class A(BaseModel):
    model_config = ConfigDict(extra="allow")

a = A(**{"b": 2})
print(getattr(a, "b", None))
print(a.model_extra)
