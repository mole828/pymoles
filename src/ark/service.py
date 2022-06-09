import loguru
from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorCursor

from src.ark.ArkNightsApi import basic
from src.config import mongo
from src.ark.ArkNightsTask import start_task, findNew




router = APIRouter()


@router.get('/list.doc')
async def docs():
    return [doc async for doc in mongo.client.moles.doctor.find({}, {'_id': 0, 'token': 0}).sort('uid', 1)]


@router.get('/list', include_in_schema=False)
async def passList():
    return [gacha async for gacha in mongo.client.moles.gacha.find({}, {'_id': 0}).sort('ts', -1)]


nicks = {}
async def nick(gacha: dict):
    uid = gacha['uid']
    if uid in nicks.keys():
        gacha['nickName'] = nicks[uid]
    else:
        doc = (await mongo.client.moles.doctor.find({'uid': uid}).to_list(1))[0]
        nicks[uid] = doc['nickName']
        gacha['nickName'] = nicks[uid]
    return gacha


pageSize = 10
@router.get('/gacha')
async def gachas(
        uid: str = None,
        page: int = 0
):
    query = {}
    if uid:
        if uid != 'null':
            query['uid'] = uid

    return {
        'code': 0,
        'data': {
            'list': [
            await nick(gacha) async for gacha in mongo.client.moles.gacha.find(query, {'_id': 0}).sort([('ts', -1)]).skip(page * pageSize).limit(pageSize)],
            'pagination': {
                "current": page,
                "total": await mongo.client.moles.gacha.count_documents(query),
                'pageSize': pageSize,
            },
            'statistic': {
            },
        },
        'msg': '',
    }


@router.post('/register')
async def register(token: str):
    try:
        import json
        d = json.loads(token)
        token = d['data']['token']
    except BaseException:
        pass
    res = basic(token)
    new = res['data']
    new['token'] = token
    loguru.logger.info(('register:', token, '=>', res))
    if res['status'] == 0:
        # mongo.client.moles.doctor.insert_one(res['data'])
        doc: dict = await mongo.client.moles.doctor.find_one({'uid': res['data']['uid']}, {'_id': 0})

        if doc is None:
            await mongo.client.moles.doctor.insert_one(new)
            findNew(new)
            loguru.logger.info({'insert': await mongo.client.moles.doctor.find_one({'token': token})})
        elif 'token' not in doc.keys():
            new = res['data']
            new['token'] = token
            await mongo.client.moles.doctor.delete_one({'uid': res['data']['uid']})
            await mongo.client.moles.doctor.insert_one(new)
            loguru.logger.info({'insert': await mongo.client.moles.doctor.find_one({'token': token})})
        elif doc['token'] != token:
            mongo.client.moles.doctor.update_one({
                'token': doc['token']
            }, {
                '$set': {'token': token}
            })
            findNew(new)
            loguru.logger.info({'update': await mongo.client.moles.doctor.find_one({'token': token})})
    return {'msg': res['msg']}

from src.ark.ArkNightsTask import beat
@router.get('/update_map', include_in_schema=False)
async def update_map():
    return beat

from src.ark.ArkNightsTask import statistic
@router.get('/statistic')
async def _(uid: str = ''):
    if uid in statistic:
        statistic[uid]['uid'] = uid
        if uid == '':
            statistic[uid]['nick'] = uid
        else:
            await nick(statistic[uid])
        return statistic[uid]
    return None


@router.get('/doc.invalid')
async def _():
    resp = beat['docsResp']
    return [key for key in resp.keys() if resp[key]['basic']['status'] != 0]


router.add_event_handler('startup', start_task)


