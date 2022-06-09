import json

import loguru
import requests


def basic(token: str):
    data = json.dumps({
        "appId": 1,
        "channelMasterId": 1,
        "channelToken": {
            "token": token
        }
    })
    with requests.post('https://as.hypergryph.com/u8/user/info/v1/basic', data=data) as response:
        return json.loads(response.text)


paths = ["gacha", "diamond", "recent"]
def recent(token: str, page: int):
    with requests.post("https://as.hypergryph.com/u8/pay/v1/recent", json.dumps({
        "appId": 1,
        "channelMasterId": 1,
        "channelToken": {
            "token": token,
        }
    })) as response:
        res_json = json.loads(response.text)
        try:
            return res_json['data']
        except KeyError:
            loguru.logger.info((token, page, res_json))
            return []


def inquiry(token: str, page: int, path: str = "gacha"):
    if path == "recent":
        return recent(token=token, page=page)
    params = {
        'token': token,
        'page': page
    }
    try:
        with requests.get(f'https://ak.hypergryph.com/user/api/inquiry/{path}', params=params) as response:
            res_json = json.loads(response.text)
            return res_json['data']['list']
    except KeyError:
        loguru.logger.info((token, page, response.text))
    except requests.exceptions.ChunkedEncodingError:
        loguru.logger.info((token, page, response.text))
    except json.decoder.JSONDecodeError:
        loguru.logger.info((token, page, response.text))
    return []

def inquiry2iter(token: str, path: str = "gacha"):
    for page in range(1, 11):
        gs = inquiry(token=token, page=page, path=path)
        for g in gs:
            try:
                if 'payTime' in g.keys():
                    g['ts'] = g['payTime']
            except AttributeError as e:
                loguru.logger.info({
                    'function:': f'inquiry2iter(token: str = {token}, path: str = {path}):',
                    'e': e,
                    'g': g,
                    'type(g)': type(g),
                })
                return
            yield g
        if len(gs) != 10:
            break

if __name__ == '__main__':
    t = "KQQVv1/4i94WWvSYRIeMs"
    print(basic(t))
    #
    # for g in inquiry2iter(t):
    #     print(g)
    # print(diamond("qe/AxGCo1//WCzsOKZ18bD8C", 1))
    # for d in inquiry2iter(t, "recent"):
    #     print(d)

