# app/infrastructure/db_connector.py

from pymongo import MongoClient


MONGO_URI = "mongodb+srv://Rocio:23456bcd@dbecomarket.agkm8ny.mongodb.net/" 

class MongoDBConnector:
    _client = None
    
    @classmethod
    def get_client(cls):
        """Retorna una instancia única del cliente MongoDB (Singleton)."""
        if cls._client is None:
            print("[INFRA] Conectando a MongoDB Atlas...")
            cls._client = MongoClient(MONGO_URI)
        return cls._client

    @classmethod
    def get_collection(cls, collection_name: str):
        """Retorna la colección específica dentro de la base de datos 'ecomarket'."""
        client = cls.get_client()
        db = client.get_database('ecomarket')
        return db.get_collection(collection_name)