import streamlit as st
import pandas as pd
import numpy as np
import json
import uuid
from streamlit_calendar import calendar
from datetime import datetime, timedelta
from datetime import time
import itertools
st.set_page_config(layout="wide")

class Trajet:
    id_obj = itertools.count()
    def __init__(self,id, name, jour, heure_depart, duree, bus,etape):
        self.id = id
        self.name = name
        self.jour = jour
        self.heure_depart = heure_depart
        self.duree = duree
        self.bus = bus
        self.heure_arrivee = self.calculer_heure_arrivee()
        self.etape= etape
    
    def calculer_heure_arrivee(self):
        heure_depart_int, minute_depart_int = map(int, self.heure_depart.split(":"))
        duree_heures = self.duree // 60
        duree_minutes = self.duree % 60

        # Calculer l'heure d'arrivée
        heure_arrivee_int = heure_depart_int + duree_heures
        minute_arrivee_int = minute_depart_int + duree_minutes

        # Si les minutes d'arrivée dépassent 60, ajuster l'heure d'arrivée
        if minute_arrivee_int >= 60:
            heure_arrivee_int += 1
            minute_arrivee_int -= 60

        # Formater l'heure d'arrivée sous forme de chaîne
        heure_arrivee_str = f"{heure_arrivee_int:02d}:{minute_arrivee_int:02d}"
        return heure_arrivee_str
   
def editing(trajet, df):
    trajet.etape = df.to_dict(orient='records')
    
    df['heure'] = pd.to_datetime(df['heure'])
    heure_min = df['heure'].dt.time.min()
    heure_max = df['heure'].dt.time.max()
    duree_minutes = (heure_max.hour * 60 + heure_max.minute) - (heure_min.hour * 60 + heure_min.minute)

    trajet.heure_depart = heure_min
    trajet.heure_arrivee= heure_max
    trajet.duree = duree_minutes

def delete_trajet(id):
    for index, trajet in enumerate(st.session_state.trajets):
        if trajet.id == id:
            index_trajet_a_supprimer = index
            del st.session_state.trajets[index_trajet_a_supprimer]



st.title('Planning Bus')
with open("testdata.json", "r") as f:
    trajets_predefinis = json.load(f)
noms_uniques = set()

# Itération sur la liste de trajets pré-définis pour extraire les noms uniques
for trajet in trajets_predefinis:
    if "name" in trajet:
        noms_uniques.add(trajet["name"])

# Convertir l'ensemble en une liste pour l'afficher dans Streamlit
liste_noms_uniques = list(noms_uniques)
# Initialiser la variable persistante pour stocker les trajets
if 'trajets' not in st.session_state:
    st.session_state.trajets = []

# Interface utilisateur

bus_colors = {
    "RENAULT": "#ff5733",  # Rouge
    "NAVETTE ZEBRA": "#33ff57",  # Vert
    "NAVETTE IVECO": "#3366ff",  # Bleu
    "BUS ARVY": "#ffff33",  # Jaune
    "BUS VAUBAN": "#ff33ff" ,  # Magenta
    "BUS PRO": "#9900cc"
}
# Saisie de la date du trajet
date_trajet = st.date_input("Sélectionnez la date du trajet", datetime.today())

# Saisie de la description du trajet
description_trajet = st.selectbox("Liste Trajets",liste_noms_uniques)
newtrajet = [trajet for trajet in trajets_predefinis if trajet["name"] == description_trajet]
# Bouton pour enregistrer le trajet
if st.button("Enregistrer uniquement le trajet sélectionné"):
    random_id = uuid.uuid4()
    random_id_str = str(random_id)
    st.session_state.trajets.append(Trajet(random_id_str,description_trajet,date_trajet, newtrajet[0]["heure_depart"], newtrajet[0]["duree"], newtrajet[0]["bus"],newtrajet[0]["etapes"] ))
    st.success("Trajet enregistré avec succès!")

if st.button("Ajourter l'ensemble des trajets prédéfinis pour le jour sélectionné"):
    for trajet in trajets_predefinis:
        random_id = uuid.uuid4()
        random_id_str = str(random_id)
        st.session_state.trajets.append(Trajet(random_id_str,trajet["name"],date_trajet, trajet["heure_depart"], trajet["duree"], trajet["bus"],trajet["etapes"] ))
        st.success("Tous les trajets ont été enregistré avec succès!")

# Afficher les trajets enregistrés


calendar_events = []

# Traitement de chaque trajet
for trajet in st.session_state.trajets:
    # Convertir l'heure de départ en objet datetime
    test = f"{trajet.jour}T{trajet.heure_depart}:00"
    heure_depart_dt = datetime.fromisoformat(test)
    
    # Calculer l'heure d'arrivée en ajoutant la durée au départ
    heure_arrivee_dt = heure_depart_dt + timedelta(minutes=trajet.duree)

    # Créer un objet JSON représentant l'événement pour ce trajet
    event = {
        "id": trajet.id,
        "title": trajet.name,
        "start": heure_depart_dt.isoformat(),  # Convertir en format ISO 8601
        "end": heure_arrivee_dt.isoformat(),  # Convertir en format ISO 8601
        # Autres informations facultatives de l'événement
        "ressourceId": trajet.bus,
       "backgroundColor":bus_colors.get(trajet.bus)
    }
    
    # Ajouter cet événement à la liste des événements
    calendar_events.append(event)

calendar_options = {
    "editable": "true",
    "selectable": "true",
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridDay,dayGridWeek,dayGridMonth",
    },
    "slotMinTime": "00:00:00",
    "slotMaxTime": "23:59:00",
    "initialView": "dayGridWeek",
    "resourceGroupField": "building",
    "resources": [
        {"id": "Bus 1", "building": "Building A", "title": "Building A"},
        {"id": "b", "building": "Building A", "title": "Building B"},
        {"id": "Bus 2", "building": "Building B", "title": "Building C"},
        {"id": "d", "building": "Building B", "title": "Building D"},
        {"id": "e", "building": "Building C", "title": "Building E"},
        {"id": "f", "building": "Building C", "title": "Building F"},
    ],
}

custom_css="""
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
"""
col1, col2 = st.columns(spec = [0.7,0.3])

with col1:
    st.markdown("# Calendrier")
    calendar = calendar(events=calendar_events, options=calendar_options, custom_css=custom_css)
df = pd.DataFrame(calendar)
with col2:
    if 'eventClick' in df.columns:
        date_str = df["eventClick"]["event"]["start"]
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z").date()
        name_trajet = df["eventClick"]["event"]["title"]
        date_time_obj_start = datetime.fromisoformat(df["eventClick"]["event"]["start"])
        # Extraire l'heure de l'objet datetime
        heure_start = date_time_obj_start.strftime("%H:%M")
        date_time_obj_end = datetime.fromisoformat(df["eventClick"]["event"]["end"])
        # Extraire l'heure de l'objet datetime
        heure_end = date_time_obj_end.strftime("%H:%M")
        selected_id = df["eventClick"]["event"]["id"]
        
        trajet_recherche = None
        for trajet in st.session_state.trajets:
            if trajet.id == selected_id:
                trajet_recherche = trajet
                break
        st.write("## Détails du trajet")
        st.dataframe([vars(trajet_recherche)])
        etapes_df = pd.DataFrame(trajet_recherche.etape)
        etapes_df["heure"] = pd.to_datetime(etapes_df["heure"])
        if "reading" not in st.session_state:
            st.session_state.reading = True
        col_button1, col_button2 = st.columns(2)
        with col_button1:
            if st.button("Modifier"):
                st.session_state.reading = False
        with col_button2:
            if st.button("Supprimer"):
                delete_trajet(selected_id)
                st.experimental_rerun()
        st.write(st.session_state.reading)
        if st.session_state.reading:
            st.dataframe(etapes_df,column_config={
                    "heure": st.column_config.TimeColumn(
                        "heure",
                        min_value=time(0, 0),
                        max_value=time(23, 59),
                        format="hh:mm",
                        step=5,
                    ),})
        else:
            new_data = st.data_editor(etapes_df,column_config={
                    "heure": st.column_config.TimeColumn(
                        "heure",
                        min_value=time(0, 0),
                        max_value=time(23, 59),
                        format="hh:mm",
                        step=5,
                    ),},num_rows= "dynamic")
            if st.button("Enregistrer les modifications"):
                st.session_state.reading = True
                editing(trajet_recherche,new_data)
                st.experimental_rerun()
                ##implémenter la modification des données

          
