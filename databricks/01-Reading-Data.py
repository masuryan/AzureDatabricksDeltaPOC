# Databricks notebook source
# MAGIC %md-sandbox
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # Reading Data & Writing Files - Parquet and CSV
# MAGIC 
# MAGIC **In this lesson you:**
# MAGIC - Read data in from CSV format
# MAGIC - Write data out in Parquet format

# COMMAND ----------

# MAGIC %run ./Includes/Classroom-Setup

# COMMAND ----------

# MAGIC %md
# MAGIC ##![Spark Logo Tiny](https://files.training.databricks.com/images/wiki-book/general/logo_spark_tiny.png) <b>Databricks File System</b>
# MAGIC <b>Databricks File System (DBFS)</b> is a layer over Azure's blob store.
# MAGIC * Files in DBFS persist to the blob store, so data is not lost even after clusters are terminated.
# MAGIC 
# MAGIC #### Databricks Utilities - dbutils
# MAGIC * Access the DBFS through the Databricks Utilities class (and other file IO routines).
# MAGIC * An instance of DBUtils is already declared as `dbutils`.
# MAGIC * For in-notebook documentation on DBUtils execute the command `dbutils.help()`.
# MAGIC * See also <a href="https://docs.databricks.com/user-guide/dbutils.html" target="_blank">Databricks Utilities - dbutils</a>

# COMMAND ----------

dbutils.help()

# COMMAND ----------

# MAGIC %md
# MAGIC ##![Spark Logo Tiny](https://files.training.databricks.com/images/105/logo_spark_tiny.png) Reading from CSV

# COMMAND ----------

# MAGIC %md
# MAGIC ### The Data Source
# MAGIC * For this exercise, use a file called **products.csv**.
# MAGIC * The data represents new products to add to the online store.
# MAGIC * Use **&percnt;fs head ...** to view the first few lines of the file.

# COMMAND ----------

# MAGIC %fs ls /mnt/training/

# COMMAND ----------

# MAGIC %fs head /mnt/training-msft/initech/Product.csv

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 1: Read The CSV File
# MAGIC Start by indicating the type and location of the file to read.
# MAGIC The default delimiter for `spark.read.csv( )` is a comma(`,`).  It is possible to change the delimiter parameter with an option.

# COMMAND ----------

# A reference to our csv file
csvFile = "dbfs:/mnt/training-msft/initech/Product.csv"
tempDF = (spark.read           # The DataFrameReader
#  .option("delimiter", "\t")  # This is how we could pass in a Tab or other delimiter.
   .csv(csvFile)               # Creates a DataFrame from CSV after reading in the file
)

# COMMAND ----------

# MAGIC %md
# MAGIC This is guaranteed to <u>trigger one job</u>.
# MAGIC 
# MAGIC A *Job* is triggered anytime we are "physically" __required to touch the data__.
# MAGIC 
# MAGIC In some cases, __one action may create multiple jobs__ (multiple reasons to touch the data).
# MAGIC 
# MAGIC In this case, the reader has to __"peek" at the first line__ of the file to determine how many columns of data it has.

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC Execute the command `printSchema()`to see the structure of the `DataFrame`.
# MAGIC 
# MAGIC The name of each column is printed to the console, with its data type, and whether it may contain null values.
# MAGIC 
# MAGIC ** *Note:* ** *Other `DataFrame` functions are covered in following lessons.*

# COMMAND ----------

tempDF.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC From the schema notice:
# MAGIC * There are eight columns in the DataFrame.
# MAGIC * The column names **_c0**, **_c1**, and **_c2**... (automatically generated names)
# MAGIC * All columns are **strings**
# MAGIC * All columns are **nullable**
# MAGIC 
# MAGIC Use `display(..)` to take another look at the data and confirm that the first row contains the column headers and not column data.

# COMMAND ----------

display(tempDF)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 2: Use the File Header
# MAGIC Next, add an option that indicates the data contains a header, and to use the header to determine column names.

# COMMAND ----------

(spark.read                    # The DataFrameReader
   .option("header", True)     # Use first line of all files as header
   .csv(csvFile)               # Creates a DataFrame from CSV after reading in the file
   .printSchema()
)

# COMMAND ----------

# MAGIC %md
# MAGIC Notice spark uses the header row to create the column names in the DataFrame.  However, all the column datatypes are still strings.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 3: Infer the Schema
# MAGIC 
# MAGIC Lastly, add an option that infers each column's data type (the schema).

# COMMAND ----------

(spark.read                        # The DataFrameReader
   .option("header", True)         # Use first line of all files as header
   .option("inferSchema", True)    # Automatically infer data types
   .csv(csvFile)                   # Creates a DataFrame from CSV after reading in the file
   .printSchema()
)

# COMMAND ----------

# MAGIC %md
# MAGIC Note that inferring the schema caused Spark to run a second job.  This is because Spark must read all of the data in the file in order to determine the data types. This is not so bad for a small file like the one we are working with here, but this can be significant when reading in large files.  We can avoid both jobs by providing the schema explicitly.

# COMMAND ----------

# MAGIC %md
# MAGIC ##![Spark Logo Tiny](https://files.training.databricks.com/images/105/logo_spark_tiny.png) Providing a schema when reading from a CSV
# MAGIC 
# MAGIC This time read the same file but define the schema first, to avoid the execution of any extra jobs.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 1: Declare the schema.
# MAGIC 
# MAGIC This is a list of field names and data types.

# COMMAND ----------

# Required for StructField, StringType, IntegerType, etc.
from pyspark.sql.types import *

csvSchema = StructType([
  StructField("product_id", LongType()),
  StructField("category", StringType()),
  StructField("brand", StringType()),
  StructField("model", StringType()),
  StructField("price", DoubleType()),
  StructField("processor", StringType()),
  StructField("size", StringType()),
  StructField("display", StringType())
 ])

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 2: Read the data (and print the schema).
# MAGIC 
# MAGIC Specify the schema, or rather the `StructType`, with the `schema(..)` command:
# MAGIC 
# MAGIC ** *NOTE:* ** *We still need to specify the option header as true.  We have already given the correct column names in our schema definition, but we need to let Spark know that the first row in the file should not be read in as actual data.*

# COMMAND ----------

productDF = (spark.read                   # The DataFrameReader
  .option('header', 'true')   # Ignore line #1 - it's a header
  .schema(csvSchema)          # Use the specified schema
  .csv(csvFile)               # Creates a DataFrame from CSV after reading in the file
)

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC With the DataFrame created, create a temporary view and then view the data via SQL:

# COMMAND ----------

# create a view called products
productDF.createOrReplaceTempView("products")

# COMMAND ----------

# MAGIC %md
# MAGIC Next, take a peek at the data with a simple SQL SELECT statement:

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM products

# COMMAND ----------

# MAGIC %md
# MAGIC ##![Spark Logo Tiny](https://files.training.databricks.com/images/105/logo_spark_tiny.png) Writing to Parquet
# MAGIC 
# MAGIC Parquet is a columnar format that is supported by many data processing systems. Spark SQL provides support for both reading and writing Parquet files that automatically preserves the schema of the original data. When writing Parquet files, all columns are automatically converted to be nullable for compatibility reasons.
# MAGIC 
# MAGIC More discussion on <a href="http://parquet.apache.org/documentation/latest/" target="_blank">Parquet</a>
# MAGIC 
# MAGIC Documentation on <a href="https://spark.apache.org/docs/latest/api/python/pyspark.sql.html?highlight=dataframe%20reader#pyspark.sql.DataFrameReader" target="_blank">DataFrameReader</a>

# COMMAND ----------

outputFile = userhome + "/initech/Products.parquet"
productDF.write.mode("overwrite").parquet(outputFile)    

# COMMAND ----------

# MAGIC %md
# MAGIC View the parquet files in the file system.

# COMMAND ----------

# MAGIC %fs ls /mnt/training-msft/initech/Products.parquet/

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2018 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>
