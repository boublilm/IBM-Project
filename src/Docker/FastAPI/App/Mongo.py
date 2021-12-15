from pymongo import MongoClient


class MongoHandler:
    def __init__(self, host, port, db_name):
        self.host = host
        self.port = port
        self.client = MongoClient(self.host, port=self.port)
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def get_all_collections(self):
        return self.db.list_collection_names()

    def get_all_documents(self, collection_name):
        return self.db[collection_name].find()

    def get_document(self, collection_name, document_id, filter="_id"):
        return self.db[collection_name].find_one({filter: document_id})

    def insert_document(self, collection_name, document):
        return self.db[collection_name].insert_one(document)

    def update_document(self, collection_name, document_id, document):
        return self.db[collection_name].update_one({"_id": document_id}, {"$set": document})

    def delete_document(self, collection_name, document_id):
        return self.db[collection_name].delete_one({"_id": document_id})

    def delete_collection(self, collection_name):
        return self.db.drop_collection(collection_name)

    def close(self):
        self.client.close()

    def insert_many_documents(self, collection_name, documents):
        return self.db[collection_name].insert_many(documents)


