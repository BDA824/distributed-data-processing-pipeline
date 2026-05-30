import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql.functions import regexp_replace
from pyspark.sql.functions import create_map, lit
from itertools import chain
from pyspark.sql.functions import col
from pyspark.sql.functions import round

print("\n Iniciando proceso ETL con PySpark... \n")
spkSession = SparkSession.builder. \
    appName('Project_spark'). \
    getOrCreate()

print("\n En este momento estamos en la etapa de extracción... \n")
df = spkSession.read.csv("data/NYC.csv", header=True, inferSchema=True)

print("\n En este momento estamos en la etapa de transformación... \n")
df = df.withColumn("id", regexp_replace("id", "^id", ""))
df = df.withColumn("id", df["id"].cast("int"))

df.groupBy("vendor_id").count().show()
mapa_proveedores = {1: "Creative Mobile Technologies", 2: "VeriFone Inc."}
mapping_expr = create_map([lit(x) for x in chain(*mapa_proveedores.items())])
df = df.withColumn("vendor_name", mapping_expr[df["vendor_id"]])

df = df.withColumn("trip_duration(min)", (col("trip_duration") / 60))
df = df.withColumn("trip_duration(min)", round(col("trip_duration(min)"), 2))
df = df.drop("trip_duration")

print("\n En este momento estamos en la etapa de carga... \n")
df.write.mode("overwrite").parquet("output/etl_result.parquet")