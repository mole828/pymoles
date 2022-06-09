from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket


class molesMongo:
    client: AsyncIOMotorClient
    bucket: AsyncIOMotorGridFSBucket

    def connect(self):
        self.client = AsyncIOMotorClient('127.0.0.1', 27017)
        self.bucket = AsyncIOMotorGridFSBucket(self.client.moles)


    def __init__(self, app) -> None:
        app.add_event_handler('startup', self.connect)



