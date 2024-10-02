# FROM openlake/spark-py:3.3.2

# USER root

# WORKDIR /app

# RUN pip3 install pyspark==3.3.2

# COPY ./main.py .

# ------------------------------------------
# Base Image 
FROM apache/spark-py:3.3.1
 
# Switch to root user temporarily to create the spark user and group 
USER root 
RUN groupadd -r spark && \ 
    useradd -r -g spark spark && \ 
    # Ensure that the Spark directories are owned by the spark user 
    chown -R spark:spark /opt/spark 
  
# Switch to the spark user 
USER spark 
 
# Verify the spark user 
RUN id spark 

WORKDIR /opt/spark/work-dir
 
# Copy necessary files 
COPY ./main.py . 
 