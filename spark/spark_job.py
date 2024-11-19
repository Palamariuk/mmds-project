from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, BooleanType, IntegerType
import pickle
import mmh3
from bitarray import bitarray

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("KafkaBloomFilterStreaming") \
    .master("local[*]") \
    .config("spark.kafka.consumer.cache.enabled", "false") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Kafka configuration
KAFKA_TOPIC = "test"
KAFKA_BROKER = "kafka:9092"

# Define schema for incoming JSON data
schema = StructType([
    StructField("id", StringType(), True),
    StructField("title", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("user", StringType(), True),
    StructField("bot", BooleanType(), True),
    StructField("minor", BooleanType(), True),
    StructField("change", IntegerType(), True),
    StructField("comment", StringType(), True),
])

# Load Bloom Filter state
with open("/app/bloom_state.pkl", "rb") as file:
    deserialized_data = pickle.load(file)

serialized_data = pickle.dumps(deserialized_data)
broadcast_bloom_filter = spark.sparkContext.broadcast(serialized_data)

def check_bloom_filter(item):
    bit_array, hash_count, size = pickle.loads(broadcast_bloom_filter.value)
    for i in range(hash_count):
        index = mmh3.hash(str(item), i) % size
        if bit_array[index] == 0:
            return False
    return True


# Register UDF for Bloom Filter
bloom_udf = F.udf(check_bloom_filter, BooleanType())

# Read streaming data from Kafka
stream_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("kafka.consumer.poll.ms", "60000") \
    .option("kafka.session.timeout.ms", "60000") \
    .load()

# Parse JSON from the Kafka stream
parsed_df = stream_df.select(F.col("value").cast("string").alias("json_data")) \
    .withColumn("data", F.from_json(F.col("json_data"), schema)) \
    .select("data.*") \
    .withColumn("is_bot_bloom", bloom_udf(F.col("user")))

# Calculate metrics
metrics_df = parsed_df.withColumn(
    "tp", F.when((F.col("bot") == 1) & (F.col("is_bot_bloom") == 1), 1).otherwise(0)
).withColumn(
    "tn", F.when((F.col("bot") == 0) & (F.col("is_bot_bloom") == 0), 1).otherwise(0)
).withColumn(
    "fp", F.when((F.col("bot") == 0) & (F.col("is_bot_bloom") == 1), 1).otherwise(0)
).withColumn(
    "fn", F.when((F.col("bot") == 1) & (F.col("is_bot_bloom") == 0), 1).otherwise(0)
)

# Aggregate metrics
agg_metrics = metrics_df.groupBy().agg(
    F.sum("tp").alias("tp"),
    F.sum("tn").alias("tn"),
    F.sum("fp").alias("fp"),
    F.sum("fn").alias("fn")
)

# Calculate precision, recall, and F1-score
final_metrics = agg_metrics.selectExpr(
    "(tp + tn) / (tp + tn + fp + fn) AS accuracy",
    "tp / (tp + fp) AS precision",
    "tp / (tp + fn) AS recall",
    "2 * (tp / (tp + fp) * tp / (tp + fn)) / (tp / (tp + fp) + tp / (tp + fn)) AS f1",
    "tp", "tn", "fp", "fn"
)

# Write metrics to console
query = final_metrics.writeStream \
    .outputMode("complete") \
    .trigger(processingTime="10 second") \
    .format("console") \
    .start()

query.awaitTermination()
