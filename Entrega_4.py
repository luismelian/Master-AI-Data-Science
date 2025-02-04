#Importación de librerias
import ftplib
import xml.etree.ElementTree as ET
import pandas as pd
from prettytable import PrettyTable

#Conexión al servidor FTP
ftp = ftplib.FTP()
try:
    ftp.connect('f31-preview.runhosting.com', 21)
    ftp.login(user='4009006_DATOS', passwd='Rafa9999')
    print("Conexión FTP exitosa")
except Exception as e:
    print(f"Error en la conexión FTP: {e}")
    #Cierre de la conexión FTP
    ftp.quit()

#Descarga del archivo OptaF24.xml
ftp.retrbinary("RETR OptaF24.xml", open("OptaF24.xml", 'wb').write)

#Parseo del archivo XML
filename = "OptaF24.xml"
tree = ET.parse(filename)
root = tree.getroot()
print("Archivo XML parseado correctamente.")

#Creación de listas vacías para almacenar los datos
teams, halves, minutes, seconds = [], [], [], []
x_origins, y_origins, x_destinations, y_destinations = [], [], [], []
outcomes = []

#Iteración sobre los eventos en el archivo XML
for game in root.findall('Game'):
    for event in game.findall('Event'):
        #Filtrado de los eventos de pases
        if event.attrib.get('type_id') == "1":
            teams.append(event.attrib.get('team_id'))
            halves.append(int(event.attrib.get('period_id')))
            minutes.append(int(event.attrib.get('min')))
            seconds.append(int(event.attrib.get('sec')))
            x_origins.append(float(event.attrib.get('x')))
            y_origins.append(float(event.attrib.get('y')))
            outcomes.append(int(event.attrib.get('outcome')))

            #Búsqueda de coordenadas de destino
            x_dest, y_dest = None, None
            for qualifier in event.findall('Q'):
                if qualifier.attrib.get('qualifier_id') == "140":
                    x_dest = float(qualifier.attrib.get('value'))
                elif qualifier.attrib.get('qualifier_id') == "141":
                    y_dest = float(qualifier.attrib.get('value'))
            x_destinations.append(x_dest)
            y_destinations.append(y_dest)

#DataFrame de eventos
df = pd.DataFrame({
    'team_id': teams,
    'half': halves,
    'minute': minutes,
    'second': seconds,
    'x_origin': x_origins,
    'y_origin': y_origins,
    'x_destination': x_destinations,
    'y_destination': y_destinations,
    'outcome': outcomes
})

#DataFrame para el mapeo de team_id & team
team_mapping = pd.DataFrame({
    'team_id': ["43", "30"],
    'team': ["Manchester City", "Bolton Wanderers"]
})

#Join para añadir los nombres de los equipos
df = df.merge(team_mapping, on='team_id', how='left')

#Visualización del DataFrame con PrettyTable
print("DataFrame:")
table = PrettyTable()
table.field_names = ['team', 'half', 'minute', 'second', 'x_origin', 'y_origin', 'x_destination', 'y_destination', 'outcome']

#Adición de primeras 5 filas del DataFrame
for _, row in df[['team', 'half', 'minute', 'second', 'x_origin', 'y_origin', 'x_destination', 'y_destination', 'outcome']].head().iterrows():
    table.add_row(row)

#Impresión del DataFrame
print(table)

#Filtro de pases largos > 20 metros en coordenada x
df['x_distance'] = df['x_destination'] - df['x_origin']
long_passes = df[df['x_distance'] > 20]

#Conteo de los pases largos por equipo
team_long_passes = long_passes['team'].value_counts()
print(f"El equipo con más pases superiores a 20 metros de avance en coordenada x es: {team_long_passes.idxmax()}, con {team_long_passes.max()} pases largos.")
