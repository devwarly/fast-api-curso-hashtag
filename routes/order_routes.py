from fastapi import APIRouter, Depends, HTTPException
from schemas.order_schemas import PedidoSchema, ItemPedidoSchema, ResponsePedido

from sqlalchemy.orm import Session
from dependencies import pegar_session, verificar_token
from models import Pedido, Usuario, ItemPedido

from typing import List

order_router = APIRouter(prefix="/pedidos", tags=["order"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def pedidos():

    """
    Essa é a rota padrão dos predidos do nosso sistema. Todas as rotas dos predidos precisam de autenticação.
    """
    return {"message": "Você acessou a rota de pedidos"}


@order_router.post("/criar_pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_session)):

    novo_pedido = Pedido(usuario=pedido_schema.id_usuario)

    session.add(novo_pedido)
    session.commit()
    return {"message": f"Pedido criado com sucesso. ID do pedido: {novo_pedido.id}"}

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_session), usuario: Usuario = Depends(verificar_token)):

    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")

    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização")

    pedido.status = "CANCELADO"
    session.commit()
    return {
        "message": "Pedido cancelado com sucesso",
        "numero": f"{pedido.id}",
        "pedido": pedido
    }


@order_router.get("/listar")
async def listar_pedidos(session: Session = Depends(pegar_session), usuario: Usuario = Depends(verificar_token)):

    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização")

    else:
        pedidos = session.query(Pedido).all()

        return {
            "pedidos": pedidos
        }


@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_session), usuario: Usuario = Depends(verificar_token)):

    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")

    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização")

    pedido.status = "FINALIZADO"
    session.commit()
    return {
        "message": "Pedido finalizado com sucesso",
        "numero": f"{pedido.id}",
        "pedido": pedido
    }


@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int, item_pedido_schema: ItemPedidoSchema, session: Session = Depends(pegar_session), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não existe")

    elif not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização")

    item_pedido = ItemPedido(item_pedido_schema.quantidade, item_pedido_schema.sabor, item_pedido_schema.tamanho, item_pedido_schema.preco_unitario, id_pedido)

    
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()

    return {
        "message": "Item criado com sucesso",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco
    }

@order_router.get("/pedido/{id.pedido}")
async def visualizar_pedido(id_pedido: int, session: Session = Depends(pegar_session), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()

    if not pedido:
            raise HTTPException(status_code=400, detail="Pedido não existe")
    
    elif not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização")

    return {
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
    }


@order_router.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido: int, session: Session = Depends(pegar_session), usuario: Usuario = Depends(verificar_token)):
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id==id_item_pedido).first()
    pedido = session.query(Pedido).filter(Pedido.id==item_pedido.pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item no Pedido não existe")

    elif not usuario.admin and usuario.id != item_pedido.pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização")

   
    
    session.delete(item_pedido)
    pedido.calcular_preco()
    session.commit()

    return {
        "message": "Item removido com sucesso",
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido,

    }


@order_router.get("/listar/pedidos-usuario", response_model=List[ResponsePedido])
async def listar_pedidos(session: Session = Depends(pegar_session), usuario: Usuario = Depends(verificar_token)):

    pedidos = session.query(Pedido).filter(Pedido.usuario==usuario.id).all()

    return pedidos


