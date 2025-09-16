import requests
import yaml
from cerberus import Validator
import json
from typing import Any
import os

BASE_AGRO_URI = "https://api.arpa.veneto.it/REST/v1/meteo_60gg_tabella"
AGROMETEO_URI = "https://api.arpa.veneto.it/REST/v1/meteo_60gg_tabella?codseqst={}"
ANAGRAFICA_STAZIONI = "https://api.arpa.veneto.it/REST/v1/meteo_60gg?coordcd=18&rnd=0.9293509776556528"

class ListAgrometeo:
    def __init__(self, list_data):
        self.list_data = []
        self.uri = list_data['meta']['first']
        for item in list_data['data']:
            self.list_data.append(AgrometeoData(item))

    def get_item(self, index: int):
        return self.list_data[index]

class AgrometeoData:
    def __init__(self, data: Any):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_path = os.path.join(script_dir, "arpav_structure.yml")

        # Load YAML files
        with open(default_path, 'r') as file:
            default_data = yaml.safe_load(file)

        data_elements = default_data['arpav_meteoagro_structure']["data"]
        self.data = dict(map(lambda key: (key, None), data_elements))

        for item in data_elements:
            self.data[item] = data[item]

def main():
    schema_filename = "arpav_structure.yml"
    # --- Legge lo schema dal file YAML ---
    with open(schema_filename, "r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)



    # --- Ottieni la risposta API ---
    for i in range (300000000,300000005):
        new_uri = AGROMETEO_URI.format(i)
        print(new_uri)
        #response = requests.get(AGROMETEO_URI)

'''    data = response.json()
    #print(data)
    print(type(data["data"]))
    print(data["data"][0])
    agrometeo = ListAgrometeo(data)


    # --- Salva comunque la risposta su file ---
    with open("response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        print("Risposta salvata su response.json")'''


if __name__ == "__main__":
    main()


