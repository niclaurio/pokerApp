import os

import mongoengine as me

class MongoModel:
    _connection = None
    _db = os.environ['db_mongo']
    _host = os.environ['host_mongo']
    _port = os.environ['port_mongo']


    @classmethod
    def get_connection(cls):
        if not cls._connection:
            cls._connection = me.connect(db=cls._db, host=cls._host, port=cls._port)


