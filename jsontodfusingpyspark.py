# -*- coding: utf-8 -*-
"""JSONtoDFusingSpark.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kchrHW_UEeB5-9DjbRFsq22YLpIYxxHy
"""

!pip install pyspark

from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

# Read JSON file into dataframe
df = spark.read.json("/content/hotel1.json")
df.show()

df.printSchema()

from pyspark.sql.functions import explode, col

df1 = df.select("hotel.*")

"""***if list [] then explode, if struct {} then col.****"""

rates = df1.select(explode("rates"))
recommendations = df1.select(explode("recommendations"))
rooms = df1.select(explode("rooms"))
standardizedRooms = df1.select(explode("standardizedRooms"))

rates_df = rates.select("col.*")
recommendations_df = recommendations.select("col.*")
rooms_df = rooms.select("col.*")
standardizedRooms_df = standardizedRooms.select("col.*")

recommendations_df = recommendations_df.select(col("groupId"),col("id").alias("recommendations_id"),explode("rates").alias("recom_rates_id"))

rates_df = rates_df.withColumnRenamed("id","rates_id")

occupancies_df = rates_df.select(col("rates_id").alias("occ_rates_id"),explode("occupancies"))
occupancies_df = occupancies_df.select("occ_rates_id","col.*")

rates_occupancies_df = rates_df.join(occupancies_df, rates_df.rates_id == occupancies_df.occ_rates_id, "leftouter")

rates_occupancies_df = rates_occupancies_df.drop("occ_rates_id","occupancies")

rates_occupancies_rooms_df = rates_occupancies_df.join(rooms_df, rates_occupancies_df.roomId == rooms_df.id, "leftouter")

rates_occupancies_rooms_df = rates_occupancies_rooms_df.drop("id")

rates_occ_rooms_recom_df = rates_occupancies_rooms_df.join(recommendations_df, rates_occupancies_rooms_df.rates_id == recommendations_df.recom_rates_id, "leftouter")

rates_occ_rooms_recom_df = rates_occ_rooms_recom_df.drop("recom_rates_id")

fin_df = rates_occ_rooms_recom_df.select("rates_id",explode("facilities")).select("rates_id",col("col.*"))
fin_df = fin_df.withColumnRenamed("name", "facilities").withColumnRenamed("rates_id","fac_rates_id")
fin_df = rates_occ_rooms_recom_df.join(fin_df, rates_occ_rooms_recom_df.rates_id == fin_df.fac_rates_id, "leftouter")
fin_df = fin_df.drop("fac_rates_id","facilities")

fin_df1 = fin_df.select("rates_id",explode("beds")).select("rates_id",col("col.*"))
fin_df1 = fin_df.withColumnRenamed("rates_id","beds_rates_id").withColumnRenamed("count","bed_count").withColumnRenamed("type","bed_type")
fin_df1 = fin_df.join(fin_df1, fin_df.rates_id == fin_df1.beds_rates_id, "leftouter")
fin_df1 = fin_df1.drop("beds_rates_id","beds")

fin_df2 = fin_df1.select("rates_id",explode("taxes")).select("rates_id",col("col.*"))
#fin_df2 = fin_df1.withColumnRenamed("rates_id","taxes_rates_id")#.withColumnRenamed("count","bed_count").withColumnRenamed("type","bed_type")
#fin_df2 = fin_df1.join(fin_df1, fin_df.rates_id == fin_df1.beds_rates_id, "leftouter")
#fin_df2 = fin_df2.drop("beds_rates_id","beds")

columns = ["facilities","beds", "taxes", "policies", "otherrateComponents", "otherProviderRates", "offers", "dailyRates"]
for i in columns:
  fin_df = rates_occ_rooms_recom_df.select("rates_id",explode(i)).select("rates_id",col("col.*"))
  fin_df = fin_df.withColumnRenamed(fin_df.columns[1], i)
  fin_df1 = rates_occ_rooms_recom_df.join(fin_df, rates_occ_rooms_recom_df.rates_id == fin_df.rates_id, "leftouter")

"""**Array Rows:** *facilities, beds, taxes, policies, otherrateComponents, otherProviderRates, offers, dailyRates*

**Struct Rows:** *boardBasis, commission*
"""
