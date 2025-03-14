import requests
import csv
import os
import json
from datetime import datetime
from sqlalchemy import create_engine, text
import feedparser
import urllib
import urllib.parse
import pandas as pd

# made by lucas.esmeraldino 20/01/2025
datenow = datetime.now().strftime("%Y-%m-%d %H:%M")

class WebInfo:
    def __init__(self, host, dbname, table, dbuser, dbpassword):
        self.url = "https://filestore.fortinet.com/fortiguard/rss/ir.xml"
        self.title = []
        self.description = []
        self.font = []
        self.publishdate = []
        self.host = host
        self.dbname = dbname
        self.table = table
        self.dbuser = dbuser
        self.dbpassword = dbpassword
    
    def get(self):
        response = requests.request("GET", self.url)
        return response.text

    def parse(self):
        # URL ou conteúdo do XML
        rss_url = "https://fortiguard.fortinet.com/rss/ir.xml"

        # Parseando o XML
        feed = feedparser.parse(rss_url)

        # Iterando pelos itens do feed
        for entry in feed.entries:
            self.title.append(entry.title)
            self.font.append(entry.link)
            self.description.append(entry.description)
            self.publishdate.append(entry.published)

    def dbCommit(self):
        # Criação do dicionário de registros únicos
        unique_records_dict = {title: (title, description, font, publishdate) 
                            for title, description, font, publishdate
                            in zip(self.title, self.description, self.font, self.publishdate)}
        records = list(unique_records_dict.values())

        # String de conexão com o banco de dados
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.host};DATABASE={self.dbname};UID={self.dbuser};PWD={self.dbpassword}"
        conn_url = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(conn_str)}"

        try:
            # Criação da engine de conexão
            engine = create_engine(conn_url)

            with engine.connect() as connection:
                if records:
                    # Ajustando a consulta MERGE com placeholders para cada registro individualmente
                    df = pd.DataFrame(list(unique_records_dict.values()), columns=["title", "description", "font", "publishdate"])
                    df.to_sql("GrafanaFortinetNews", connection, if_exists="append", index=False, method="multi")

                print(f"[{datenow}] [WEB-NOTICE] Save to DB OK")

        except Exception as e:
            print(f"[{datenow}] [WEB-NOTICE] Erro to save on DB: {e}")

    def main(self):
        WebInfo.parse(self)
        WebInfo.dbCommit(self)
