# Proceso ETL con PySpark

Este proyecto realiza un proceso ETL (Extracción, Transformación y Carga) sobre datos de viajes en la ciudad de Nueva York utilizando PySpark. El script principal es [`etl.py`](etl.py).

## Objetivo

El objetivo del script [`etl.py`](etl.py) es procesar un archivo CSV de viajes, limpiar y transformar los datos relevantes, y guardar el resultado en formato Parquet para su posterior análisis.

## Descripción de cada paso

### 1. Extracción

Se inicia una sesión de Spark y se lee el archivo CSV ubicado en `data/NYC.csv` con los encabezados y el esquema inferido automáticamente.

```python
spkSession = SparkSession.builder.appName('Project_spark').getOrCreate()
df = spkSession.read.csv("data/NYC.csv", header=True, inferSchema=True)
```

### 2. Transformación

- **Limpieza de columna `id`:**  
  Se elimina el prefijo "id" y se convierte la columna a tipo entero.

- **Conteo por proveedor:**  
  Se agrupan los datos por `vendor_id` y se muestra el conteo de registros por proveedor.

- **Mapeo de nombres de proveedores:**  
  Se crea una nueva columna `vendor_name` que asigna el nombre del proveedor según el `vendor_id`.

- **Conversión de duración de viaje:**  
  Se transforma la columna `trip_duration` de segundos a minutos, redondeando a dos decimales, y se elimina la columna original.

```python
df = df.withColumn("id", regexp_replace("id", "^id", ""))
df = df.withColumn("id", df["id"].cast("int"))
df.groupBy("vendor_id").count().show()
mapa_proveedores = {1: "Creative Mobile Technologies", 2: "VeriFone Inc."}
mapping_expr = create_map([lit(x) for x in chain(*mapa_proveedores.items())])
df = df.withColumn("vendor_name", mapping_expr[df["vendor_id"]])
df = df.withColumn("trip_duration(min)", (col("trip_duration") / 60))
df = df.withColumn("trip_duration(min)", round(col("trip_duration(min)"), 2))
df = df.drop("trip_duration")
```

### 3. Carga

El DataFrame transformado se guarda en formato Parquet en la carpeta `output/etl_result.parquet`.

```python
df.write.mode("overwrite").parquet("output/etl_result.parquet")
```

## Estructura del proyecto

- [`etl.py`](etl.py): Script principal del proceso ETL.
- `input/`: Carpeta para archivos de entrada.
- `output/`: Carpeta para archivos de salida.

...existing code...

## Comportamiento del Dockerfile

El Dockerfile incluido construye una imagen que prepara un entorno PySpark y descarga el dataset desde Kaggle durante el build. Resumen de pasos que ejecuta:

1. Base y usuario
   - Usa la imagen base `apache/spark-py:v3.3.1`.
   - Cambia a usuario `root` y establece `/app` como WORKDIR.

2. Instalación del sistema y dependencias Python
   - `apt-get update` e instala `unzip`.
   - Copia `requirements.txt` e instala dependencias con `pip`.

3. Credenciales de Kaggle y descarga del dataset
   - Copia `kaggle.json` a `/root/.kaggle/kaggle.json` y le aplica `chmod 600`.
   - Instala y usa la CLI de Kaggle para descargar `yasserh/nyc-taxi-trip-duration`.
   - Descomprime el ZIP en `/app/data`.

4. Código y ejecución
   - Copia el contenido de `src/` a `/app/src`.
   - ENTRYPOINT ejecuta `python3 src/etl.py`.

### Comandos para construir y ejecutar

Desde la raíz del proyecto (Windows PowerShell):

- Construir la imagen:
```bash
docker build -t etl-pyspark:latest -f DockerFile .
```

