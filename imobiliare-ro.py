import requests
from bs4 import BeautifulSoup
import time
import pandas
import datetime
import json
from datetime import datetime

class ExtractorImobiliareRo:

    def __init__(self, cartier, nr_camere):
        self.iduri = []
        self.linkuri = []
        self.detalii = []
        self.zone = []
        self.nume_vanzatori = []
        self.tipuri_vanzatori = []
        self.dictionar_root = dict()
        self.back_up_dict = dict()
        self.cartier = cartier
        self.nr_camere = nr_camere
        self.home_url = f'https://www.imobiliare.ro/vanzare-apartamente/bucuresti/{self.cartier}?nrcamere={self.nr_camere}'

    def getpagenumbers(self):

        home_link = requests.get(self.home_url)
        page_soup = BeautifulSoup(home_link.text, 'html.parser')
        self.ultima_pagina = int(page_soup.find_all('a', {'class': 'butonpaginare'})[-2]['data-pagina'])
        home_link.close()

    def extract_data(self):
        for i in range(self.ultima_pagina):
            # -- The while loop will try to connect to the page, and in case it throws back an error,
            # --- it will wait 5 seconds and then try again
            connected = False
            while not connected:
                try:
                    link = requests.get(f'{self.home_url}&pagina={i}')
                    soup = BeautifulSoup(link.text, 'html.parser')
                    link.close()
                    connected = True
                except:
                    print(f'Am avut o problema cu conectarea la pagina {i}\nMai incerc conectarea peste 5 sec')
                    time.sleep(5)
                    connected = False
                    continue
            anunturi = soup.find_all('div', {'class': 'box-anunt', 'data-camere': '3'})
            # --- Storing
            for x in range(len(anunturi)):
                    # --- ID anunt - unique id of every listing
                id_anunt = anunturi[x]['id']
                if id_anunt not in self.iduri:
                    self.iduri.append(id_anunt)
                else:
                    continue
                # --- link -> link to the linsting
                link_anunt = anunturi[x].find('a', {'class': 'mobile-container-url'})['href']
                self.linkuri.append(link_anunt)
                # --- detalii -> the details (number of rooms, square feet, price, distance to the subway, etc)
                detalii_anunt = [j.text for j in anunturi[x].find_all('span')]
                self.detalii.append(detalii_anunt)
                # --- Zona -> neighbourhood name
                zona = anunturi[x]['data-zona']
                self.zone.append(zona)
                # --- Seller name
                try:
                    nume_vanzator = anunturi[x]['data-ssellername']
                    self.nume_vanzatori.append(nume_vanzator)
                except:
                    self.nume_vanzatori.append(None)
                # --- Seller type
                try:
                    tip_vanzator = anunturi[x]['data-ssellertype']
                    self.tipuri_vanzatori.append(tip_vanzator)
                except:
                    self.tipuri_vanzatori.append(None)

    def store_data(self):
        for i in range(len(self.iduri)):
            self.dictionar_root.update({self.iduri[i]: {'Link': self.linkuri[i], 'Detalii': self.detalii[i],
                                                        'Zona': self.zone[i], 'Vanzator': self.nume_vanzatori[i],
                                                        'Tip vanzator': self.tipuri_vanzatori[i]}
                                   })
        with open(f'{datetime.date(datetime.now())}.json', 'w') as fp:
            json.dump(self.dictionar_root, fp)


Tot = ExtractorImobiliareRo('', 3)
Tot.getpagenumbers()
Tot.extract_data()
Tot.store_data()