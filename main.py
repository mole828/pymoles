from bson import ObjectId
from gridfs import GridOut
import loguru
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from starlette.staticfiles import StaticFiles

from src.config import app, mongo


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


from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from enum import IntEnum,Enum
class emmm(IntEnum):
    Mole = 0
    MistEO = 1
@app.get("/test/{data}")
async def testFunction(data: emmm):
    return f"{str(data)} is {data}"


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
