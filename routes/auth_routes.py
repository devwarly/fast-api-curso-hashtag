from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from schemas.auth_schemas import UsuarioSchema, EntrarSchema
from sqlalchemy.orm import Session
from dependencies import pegar_session, verificar_token
from jose import jwt, JWTError
from main import brcypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm


auth_router = APIRouter(prefix="/auth", tags=["auth"])


def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):

    '''
    id_usuario
    data_expiracao
    '''

    data_expiracao = datetime.now(timezone.utc) + duracao_token

    dicionario_informacoes = {"sub": str(id_usuario), "exp": data_expiracao}

    token = jwt.encode(dicionario_informacoes, SECRET_KEY, ALGORITHM)


    return token


    

@auth_router.get("/")
async def home():

    """
    Essa é a rota padrão de autenticação. É necessários estar logado para realizar ações no sistema.
    """

    return {"message" : "Login realizado com sucesso!", "token": "kjgiod44093jkjsdkljf92332..."}

@auth_router.post("/criar_usuario")
async def criar_conta(usuario_schema: UsuarioSchema,  session: Session = Depends(pegar_session)):
  

    usuario = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first()

    if usuario:
        raise HTTPException(status_code=400, detail="Email de usuário já cadastrado!")
    else:
       
        senha_criptografada = brcypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(
            nome=usuario_schema.nome, 
            email=usuario_schema.email, 
            senha=senha_criptografada,
            ativo=usuario_schema.ativo if usuario_schema.ativo is not None else True,
            admin=usuario_schema.admin if usuario_schema.admin is not None else False
        )
        session.add(novo_usuario)
        session.commit()
        session.refresh(novo_usuario)

        return {"message" : f"Usuário cadastrado com sucesso {usuario_schema.email}"}
    

def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()

    if not usuario:
        return False

    elif not brcypt_context.verify(senha, usuario.senha):
        return False

    return usuario

@auth_router.post("/entrar")
async def entrar_conta(entrar_schema: EntrarSchema, session : Session = Depends(pegar_session)):
    usuario = autenticar_usuario(entrar_schema.email, entrar_schema.senha, session)
    
    if not usuario:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    else:
        token_acesso = criar_token(usuario.id)
        token_atualizar = criar_token(usuario.id,  duracao_token=timedelta(days=15))

        return {
            "access-token": token_acesso,
            "refresh_token": token_atualizar,
            "token-type": "Bearer"
        }


@auth_router.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session : Session = Depends(pegar_session)):
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)
    
    if not usuario:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    else:
        token_acesso = criar_token(usuario.id)

        return {
            "access_token": token_acesso,
            "token_type": "Bearer"
        }




@auth_router.get("/atualizar")
async def usar_token_atualizacao(usuario: Usuario = Depends(verificar_token)):

    
    token_acesso = criar_token(usuario.id)

    return {
        "access_token": token_acesso,
        "token_type": "Bearer"
    }
