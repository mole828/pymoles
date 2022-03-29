from bson import ObjectId
from gridfs import GridOut
import loguru
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from starlette.staticfiles import StaticFiles

from src.config import app, mongo


@app.get('/mfs/list')
async def listFile():
    arr = await mongo.client.moles.fs.files.find().to_list(1000000)
    for a in arr:
        a['_id'] = a['_id'].__str__()
    return arr


@app.get('/var/get/{key}')
async def varGet(key: str):
    v = await mongo.client.moles.var.find_one({'key': key})
    return {key: v['value'] if v is not None else None}


@app.post('/var/set')
async def varSet(key: str, value: str):
    await mongo.client.moles.var.update_one({'key': key}, {
        '$set': {'value': value}
    })
    return {'msg': 'OK'}

import docker
@app.get('/paper/restart')
async def dockerList():
    client = docker.APIClient(base_url='www.moles.top:52375')
    client.stop('paper')
    client.start('paper')
    client.close()
    return {'msg': 'ok'}


from src.ark.service import router as ark
app.include_router(ark, prefix="/ark")

from src.chat.service import app as chat
app.include_router(chat, prefix='/chat')

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app=app,
        host="0.0.0.0",
        port=7998,
        # root_path="/api",
        proxy_headers=True,
        forwarded_allow_ips='*',
    )
