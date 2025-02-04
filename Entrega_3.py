#Import librerias
import pandas as pd
from sqlalchemy import create_engine

#Datos de conexión
database_host = 'db.relational-data.org'
username = 'guest'
password = 'relational'
database_name = 'employee'
port = 3306

#Conexión a la base de datos con SQLAlchemy
engine = create_engine(f"mysql+pymysql://{username}:{password}@{database_host}:{port}/{database_name}")

#Consulta para obtener salarios máximo, mínimo y promedio por género y cargo
query = '''
SELECT 
    e.gender,
    t.title AS cargo,
    MAX(s.salary) AS salario_maximo,
    MIN(s.salary) AS salario_minimo,
    AVG(s.salary) AS salario_promedio
FROM employees AS e
JOIN salaries AS s ON e.emp_no = s.emp_no
JOIN titles AS t ON e.emp_no = t.emp_no
GROUP BY e.gender, t.title
'''

#Ejecución de la consulta y carga de los resultados en un DataFrame
try:
    df_salarios = pd.read_sql(query, engine)
    df_salarios[["salario_maximo", "salario_minimo", "salario_promedio"]] = df_salarios[["salario_maximo", "salario_minimo", "salario_promedio"]].round(2)
    print("\nDatos de salarios por género y cargo:")
    print(df_salarios)

    #Diferencias de salario según género
    genero_diff = df_salarios.groupby("gender")[["salario_maximo", "salario_minimo", "salario_promedio"]].mean().round(2)
    print("\nDiferencias de salario según el género:")
    print(genero_diff)

except Exception as e:
    print("Ocurrió un error al ejecutar la consulta:", e)

#Cierre de conexión después de cargar los datos
engine.dispose()

#Conclusiones
#Los hombres alcanzan salarios máximos ligeramente superiores a las mujeres, mientras que las mujeres
#tienen salarios mínimos más altos. El salario promedio es favorable para los hombres, que superan a las
#mujeres en 1,666 euros en promedio. En algunos puestos de trabajo como "Manager" los hombres tienen
#salarios más altos que las mujeres, mientras que en otros como "Engineer" las diferencias son mínimas.
#Los salarios promedio más altos se encuentran en el cargo de "Manager", donde los hombres tienen un 
#salario promedio de 72,810.95, frente a las mujeres con 62,037.22.

#La diferencia salarial entre hombres y mujeres en esta muestra no es extremadamente amplia. Aún así,
#existe una tendencia donde los hombres tienen, en promedio, salarios más altos. Esta disparidad 
#se observa tanto en el salario máximo como en el promedio.