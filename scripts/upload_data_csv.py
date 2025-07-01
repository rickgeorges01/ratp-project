from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp
import os
import glob

def create_spark_session():
    """Crée une session Spark configurée pour MinIO"""
    spark = SparkSession.builder \
        .appName("CSV-to-MinIO-Parquet") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    print("✅ Session Spark créée avec configuration MinIO")
    return spark

def upload_csv_with_spark(local_data_folder="../data"):
    """Upload CSV vers MinIO en format Parquet avec Spark"""
    
    spark = create_spark_session()
    
    try:
        if not os.path.exists(local_data_folder):
            print(f"❌ Dossier {local_data_folder} inexistant")
            return []
        
        # Recherche des fichiers CSV
        csv_files = glob.glob(os.path.join(local_data_folder, "*.csv"))
        uploaded_files = []
        
        print(f"📂 Trouvé {len(csv_files)} fichiers CSV")
        
        for csv_file in csv_files:
            try:
                file_name = os.path.basename(csv_file).replace('.csv', '')
                print(f"📤 Traitement: {file_name}.csv")
                
                # Lecture du CSV avec Spark
                df = spark.read.option("header", "true") \
                    .option("inferSchema", "true") \
                    .csv(csv_file)
                
                # Ajout du timestamp de traitement
                df_with_timestamp = df.withColumn("processed_at", current_timestamp())
                
                # Sauvegarde en Parquet vers MinIO
                minio_path = f"s3a://ratp-raw/data/{file_name}/"
                
                df_with_timestamp.write.mode("overwrite").parquet(minio_path)
                
                print(f"✅ {file_name}: {df.count()} lignes → {minio_path}")
                uploaded_files.append(minio_path)
                
            except Exception as e:
                print(f"❌ Erreur {csv_file}: {e}")
        
        print(f"\n✅ Upload terminé: {len(uploaded_files)} fichiers")
        return uploaded_files
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return []
    
    finally:
        spark.stop()
        print("🔒 Session Spark fermée")

if __name__ == "__main__":
    print("🚀 Upload CSV → MinIO Parquet avec Spark")
    print("=" * 50)
    
    # Upload des CSV
    uploaded = upload_csv_with_spark("../data")
    
    print(f"\n📦 Fichiers uploadés:")
    for path in uploaded:
        print(f"   - {path}")
