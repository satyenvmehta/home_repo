from pyspark.sql import SparkSession

from pyspark.sql.functions import broadcast

from pyspark.sql import SparkSession
from pyspark.sql.functions import broadcast

spark = SparkSession.builder.getOrCreate()

trades_df = spark.read.parquet("trades.parquet")
acct_ref_df = spark.read.parquet("account_reference.parquet")

enriched_df = trades_df.join(
    broadcast(acct_ref_df),
    on="account_id",
    how="left"
)

enriched_df.show()