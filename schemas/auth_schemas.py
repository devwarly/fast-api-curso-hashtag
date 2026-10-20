from pydantic import BaseModel
from typing import Optional, List

class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: Optional[bool]
    admin: Optional[bool]

    class Config:
        from_atributes = True



class EntrarSchema(BaseModel):
    email: str
    senha: str
    class Config():
        from_atributes = True
