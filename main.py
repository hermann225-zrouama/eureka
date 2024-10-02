import os
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import split, col

if __name__ == "__main__":
    # Création de la configuration Spark
    conf = SparkConf() \
        .set("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,org.projectnessie.spark.extensions.NessieSparkSessionExtensions") \
        .set("spark.sql.catalog.standardized.io-impl", "org.apache.iceberg.aws.s3.S3FileIO") \
        .set("spark.sql.catalog.standardized.warehouse", "s3a://standardized/") \
        .set("spark.sql.catalog.standardized.s3.endpoint", "http://minio.minio.svc.cluster.default:9000") \
        .set("spark.sql.catalog.standardized.catalog-impl", "org.apache.iceberg.nessie.NessieCatalog") \
        .set("spark.sql.catalog.standardized.uri", "http://nessie.default.svc.cluster.default:19120/api/v1/") \
        .set("spark.sql.catalog.standardized.authentication.type", "NONE") \
        .set("spark.sql.catalog.standardized.ref", "main") \
        .set("spark.sql.catalog.standardized", "org.apache.iceberg.spark.SparkCatalog") \
        .set("fs.s3a.access.key", "minioadmin") \
        .set("fs.s3a.secret.key", "minio@demo!") \
        .set("fs.s3a.endpoint", "http://minio.minio.svc.cluster.default:9000") \
        .set("fs.s3a.connection.ssl.enabled", "false") \
        .set("fs.s3a.path.style.access", "true") \
        .set("fs.s3a.attempts.maximum", "1") \
        .set("fs.s3a.connection.establish.timeout", "5000") \
        .set("fs.s3a.connection.timeout", "10000")

    # Création de la session Spark
    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    # Réduire le niveau de log
    spark.sparkContext.setLogLevel("ERROR")

    # Lecture des données brutes depuis S3
    raw = spark.read.text("s3a://raw/people.txt")
    
    # Division des colonnes par espaces
    split_by_whitespace = split(col("value"), " ")

    # Transformation pour structurer les données
    structured = raw.withColumn("first_name", split_by_whitespace.getItem(0)) \
                    .withColumn("last_name", split_by_whitespace.getItem(1)) \
                    .withColumn("age", split_by_whitespace.getItem(2).cast('int')) \
                    .drop("value")

    # Nettoyage des données
    create_name_filter_condition = lambda column_name: col(column_name).rlike("^[a-zA-Z]*$")
    age_filter_condition = col("age").between(1, 150)

    cleaned = structured.filter(create_name_filter_condition("first_name") & create_name_filter_condition("last_name") & age_filter_condition)

    # Persistance des données dans un tableau Iceberg
    cleaned.writeTo("standardized.people").create()

    # Arrêt de la session Spark
    spark.stop()
