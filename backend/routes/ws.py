import asyncio
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from database.session import SessionLocal
from services.auth_service import AuthService
from websocket.manager import manager

router = APIRouter(tags=["WebSocket"])


def _authenticate_token(token: str) -> bool:
    try:
        token_data = AuthService.decode_token(token)
        db = SessionLocal()
        try:
            user = AuthService.get_user_by_username(db, token_data.username)  # type: ignore[arg-type]
            return user is not None
        finally:
            db.close()
    except Exception:
        return False


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
):
    """Real-time alert stream. Connect with: ws://host/ws?token=<jwt>"""
    if not _authenticate_token(token):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket)
    try:
        await websocket.send_json({"event": "connected", "message": "SkyAssist alert stream active"})
        while True:
            try:
                # Wait for any incoming client text with a 20-second timeout
                await asyncio.wait_for(websocket.receive_text(), timeout=20.0)
            except asyncio.TimeoutError:
                # Send periodic ping message to keep the WebSocket connection alive
                # and prevent Vite proxy or browser idle timeouts.
                await websocket.send_json({"event": "ping"})
    except Exception:
        pass
    finally:
        manager.disconnect(websocket)
