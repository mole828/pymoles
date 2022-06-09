import time
import loguru
import pymongo
import requests
from pymongo.collection import Collection



client = pymongo.MongoClient("mongodb://localhost:27017/")['moles']
from src.ark.ArkNightsApi import basic, paths, inquiry2iter


def getSame(collection: Collection, uid: str, ts: int):
    return collection.find_one({
        'uid': uid,
        'ts': ts,
    })


statistic = {
    '': {
        'sum': 0,
        'rar': {
            2: 0, 3: 0, 4: 0, 5: 0,
        },
        2: 0, 3: 0, 4: 0, 5: 0,
    }
}

def count(gacha: dict):
    uid: str = gacha['uid']
    if uid not in statistic.keys():
        statistic[uid] = {
            'sum': 0,
            'rar': {
                2: 0, 3: 0, 4: 0, 5: 0,
            },
            2: 0, 3: 0, 4: 0, 5: 0,
        }
    for char in gacha['chars']:
        for d in [statistic[''], statistic[uid]]:
            d[char['rarity']] += 1  # delete before test
            d['rar'][char['rarity']] += 1
            d['sum'] += 1

    return True


def findNew(doc: dict, path: str = 'gacha'):
    collection: Collection = client[path]
    for d in inquiry2iter(token=doc['token'], path=path):
        dib = getSame(collection, doc['uid'], d['ts'])
        if dib is None:
            d['uid'] = doc['uid']
            collection.insert_one(d)
            if path == 'gacha':
                count(d)
            # loguru.logger.info({
            #     'insert': d,
            #     'doc': doc
            # })
        else:
            return d

beat = {
    'roundStart': {},
    'beat': {},
    'docsResp': {},
}

def findNewLoop():
    loguru.logger.info(('client.list_collection_names()', client.list_collection_names()))
    for g in client.gacha.find({}): count(g)
    dt: int = 5
    time.sleep(dt)
    while True:
        beat['roundStart'] = {
            'timestamp': int(time.time()),
            'strftime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        }
        try:
            for doc in client['doctor'].find():
                beat['beat'] = {
                    'timestamp': int(time.time()),
                    'strftime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                }
                try:
                    bas = basic(token=doc['token'])
                    beat['docsResp'][doc['nickName']] = {
                        'time': int(time.time()),
                        'basic': bas,
                    }
                    if bas['status'] == 3:
                        continue
                    for path in paths:
                        dib = findNew(doc, path)
                        beat['docsResp'][doc['nickName']][path] = dib
                        time.sleep(dt)
                    # loguru.logger.info(doc)
                except ConnectionError as e:
                    beat['error'] = e.__str__()
                    loguru.logger.error(e)
                except requests.exceptions.ConnectionError as e:
                    loguru.logger.error(e)
                except requests.exceptions.ReadTimeout as e:
                    loguru.logger.error(e)
        except pymongo.errors.CursorNotFound as e:
            loguru.logger.error(e)
        dt = min(dt*2, 30)


def start_task():
    import _thread
    _thread.start_new_thread(findNewLoop, ())


# ... import start_task, map

if __name__ == '__main__':
    print(__name__)
    t = "KQQVv1/4i94WWvSYRIeMsZC/"
    # for d in moles['draw'].find():
    #     moles['gacha'].insert_one(d)
    doc = basic(t)['data']
    doc['token'] = t
    print(doc)
    findNew(doc)
