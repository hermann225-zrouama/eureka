# Base Image 
FROM apache/spark-py:3.3.1
 
# Switch to root user temporairement pour créer l'utilisateur et groupe spark 
USER root 
RUN groupadd -r spark && \ 
    useradd -r -g spark spark && \ 
    # Assurez-vous que les répertoires Spark appartiennent à l'utilisateur spark 
    chown -R spark:spark /opt/spark
    
RUN apt-get update && apt-get install -y wget

# Téléchargement des JAR dans le répertoire /opt/spark/jars
RUN wget https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.3_2.12/1.6.0/iceberg-spark-runtime-3.3_2.12-1.6.0.jar -P /opt/spark/jars && \
    wget https://repo1.maven.org/maven2/org/projectnessie/nessie-integrations/nessie-spark-extensions-3.3_2.12/0.79.0/nessie-spark-extensions-3.3_2.12-0.79.0.jar -P /opt/spark/jars && \
    wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.2/hadoop-aws-3.3.2.jar -P /opt/spark/jars && \
    wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.1026/aws-java-sdk-bundle-1.11.1026.jar -P /opt/spark/jars

# Switch back to spark user 
USER spark

# Verify the spark user 
RUN id spark 

# Define work directory 
WORKDIR /opt/spark/work-dir
 
# Copy necessary files 
COPY ./main.py . 

