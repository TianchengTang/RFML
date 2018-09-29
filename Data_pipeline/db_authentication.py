import pymongo


def authentication(server_ip, server_port=27017, username='developer', password='Dev1234', db_name='Target_sanity'):
    """
        create client connection, including authentication.

        server_ip: str
            IP of the server

        server_port: int
            TCP port

        username: str
            username

        password: str
            password

        db_name: str
            database name

        return:
            client object, database object if authentication successful.
            None, None otherwise
    """
    try:
        client = pymongo.MongoClient(server_ip,
                              username=username,
                              password=password,
                              authSource=db_name,
                              authMechanism='SCRAM-SHA-1')
        return client, client[db_name]
    except:
        print('Authentication failure')
        return None, None

# client, db = authentication('10.63.100.195')
