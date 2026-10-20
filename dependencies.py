from models import db, Usuario
from fastapi import Depends, HTTPException
from sqlalchemy.orm import sessionmaker, Session
from main import SECRET_KEY, ALGORITHM, oauth2_schema
from jose import jwt, JWTError

def pegar_session():
    try:

        Session = sessionmaker(bind=db)
        session = Session()
        yield session # Retorna a sessão do usuário depois vai fechar a sessão
    finally:
        session.close()

        # Indepndente do que acontecer ele vai fechar a sessão do banco de dados

def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_session)):
    try:
        info_usuario = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = int(info_usuario.get("sub"))
    except JWTError as e:
        # Imprime o erro exato no terminal do uvicorn para sabermos o motivo
        print(f"Erro ao decodificar token: {e}")
        raise HTTPException(status_code=401, detail="Acesso Negado, verifique a validade do token")

    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Inválido")
    return usuario