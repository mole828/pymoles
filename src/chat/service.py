import time

from fastapi import APIRouter
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket,WebSocketDisconnect

app = APIRouter()

history = [{
    'sender': 'server',
    'msg': f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) }',
}]
@app.get('/history')
async def _():
    return history


import loguru
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            await websocket.send_text(data)
        except WebSocketDisconnect:
            loguru.logger.info('disconnect')
        except RuntimeError as e:
            loguru.logger.error(e)

