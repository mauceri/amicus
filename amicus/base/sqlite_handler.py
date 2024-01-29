import sqlite3
import json
from typing import Dict

from amicus.base.common import Speech


class SQLiteHandler:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.creation_speeches()
        # self.creation_contexte()

    def creation_speeches(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS speeches (
                                 speech_id INTEGER PRIMARY KEY,
                                 conversation TEXT,
                                 speaker TEXT,
                                 date TEXT,
                                 speech TEXT)''')

    def suppression_historique(self):
        with self.conn:
            self.conn.execute('DROP TABLE IF EXISTS speeches')
            self.creation_historique()

    def creation_contexte(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS contexte (
                                 source TEXT PRIMARY KEY,
                                 contexte TEXT)''')

    def effacement_contexte(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DROP TABLE IF EXISTS contexte')

    def ajout_speech(self, speech: Speech ):
        with self.conn:
            self.conn.execute('INSERT INTO speeches (conversation,speaker,date,speech) VALUES (?, ?, ?, ?)',
                              (speech.conversationId, speech.speaker, speech.date, speech.content ) )

    def ajout_speeches(self, speech1: Speech, speech2: Speech ):
        self.ajout_speech(speech1)
        self.ajout_speech(speech2)



    def remove_speech(self, speech_id:int)->int:
        with self.conn:
            ret = self.conn.execute('DELETE FROM speeches WHERE speech_id = ?',
                              (speech_id))
            return ret
        
    def remove_transaction(self, conversation:str):
        with self.conn:
            ret = self.conn.execute('DELETE FROM speeches WHERE conversation = ?',
                              (conversation ))
            return ret

    
    def remove_all_transactions(self)->int:
        with self.conn:
            ret = self.conn.execute('DELETE FROM speeches')
            return ret


    def modification_contexte(self, source:str, contexte:object)->int:
        with self.conn:
            contexte_json = json.dumps(contexte)
            ret = self.conn.execute('INSERT OR REPLACE INTO contexte (source, contexte) VALUES (?, ?)',
                              (source, contexte_json))
            self.conn.commit()
            return ret
            
    def historique(self, conversation:str, n:int)->Dict[int,str]:
        with self.conn:
            cursor = self.conn.execute('''SELECT * FROM speeches WHERE conversation = ? ORDER BY speech_id  DESC LIMIT ?''',
                                       (conversation, n,))
            transactions = cursor.fetchall()
            
            # Convertir les transactions en une liste de dictionnaires pour une meilleure lisibilité
            colonnes = [description[0] for description in cursor.description]
            transactions_liste = []
            for transaction in transactions:
                transactions_liste.append(dict(zip(colonnes, transaction)))
            
            return transactions_liste[::-1]

    def __del__(self):
        self.conn.close()
