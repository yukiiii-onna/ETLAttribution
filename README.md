# **Attribution Pipeline Orchestration - Final Report**

## **1. Introduction**  
This project implements an **Attribution Pipeline Orchestration** as part of a **Data Engineering technical challenge**. The goal is to design a robust data pipeline that:
- **Queries marketing session and conversion data from a database** (SQLite).  
- **Processes customer journeys** by linking user sessions to conversion events.  
- **Sends processed data to the IHC Attribution API** for attribution modeling.  
- **Stores the computed IHC attribution scores** back in the database.  
- **Generates a channel performance report and exports it as a CSV file**.  
- **Automates the pipeline using Apache Airflow** for orchestration.  

This pipeline enables businesses to **analyze advertising effectiveness** and optimize marketing spend.

---

## **2. Pipeline Overview**  
The pipeline follows a **modular design** where each step is independent, ensuring flexibility and maintainability.

### **📌 Key Steps**  
1️⃣ **Data Extraction & Preparation**  
   - Reads data from **SQLite (`challenge.db`)**.  
   - Executes SQL scripts to **set up necessary tables**.  

2️⃣ **Customer Journey Construction**  
   - Extracts all **user sessions that occurred before each conversion**.  
   - Filters out **impressions-only** interactions.  

3️⃣ **API Communication & Attribution Calculation**  
   - **Limits API POST requests to 199 records per batch** (IHC API restriction).  
   - **Implements a loop to send multiple batches sequentially** until all data is processed.  
   - Uses **trained conversion type ID (`CONV_TYPE_ID`)** obtained from **IHC parameter training**.  
   - Stores the **attribution values (IHC scores)** returned by the API.  

4️⃣ **Channel Reporting & CSV Export**  
   - Aggregates attribution data to compute **marketing channel effectiveness**.  
   - Computes **Cost Per Order (CPO)** and **Return on Ad Spend (ROAS)**.  
   - Exports the results as a **CSV file** in `/reports/`.  

5️⃣ **Orchestration with Apache Airflow**  
   - Uses **Apache Airflow on Astro** for automation and scheduling.  
   - Allows **dynamic time-range filtering** via **Airflow Variables**.  

---

## **3. Deployment with Astro (Instead of Local Airflow)**  
I initially attempted to run **Airflow locally** but faced **critical issues mounting the SQLite database inside the container**:  
- **File permission issues** prevented the Airflow DAG from accessing `challenge.db`.  
- **Database persistence problems** required additional debugging, consuming too much time.  
- **Airflow's local setup required extensive manual fixes** for volume mounting and file access.  

To **avoid these issues and save debugging time**, I deployed **Airflow using Astronomer Astro**, which provided:  
- **Pre-configured environment**: Avoids local Docker and volume mount complexities.  
- **Better resource management**: Runs **Airflow on Kubernetes**, ensuring smooth DAG execution.  
- **Built-in observability**: Logs, DAG versioning, and monitoring tools for debugging.  

This decision allowed me to **focus on building the pipeline rather than fixing infrastructure issues**.

---

## **4. Project Folder Structure**  
The **project follows a structured layout** that separates concerns across different components.

### **📂 Project Structure**  
```
ETLATTRIBUTION
│
├── dags
│   ├── attribution_dag.py            # Main DAG defining the pipeline
│
├── include
│   ├── challenge.db                   # SQLite database
│   ├── create_tables.sql               # SQL script for table setup
│   ├── data_generator.py               # Generates synthetic data
│   │
│   ├── utils                           # Utility functions
│   │   ├── api_utils.py               # Handles API communication with IHC
│   │   ├── config.py                   # Stores sensitive credentials (e.g., API keys)
│   │   ├── db_utils.py                 # Manages database queries and connections
│   │   ├── file_utils.py               # Handles CSV export and file storage
│   │   ├── time_utils.py               # Manages time-range filtering for data processing
│   │   ├── transformation_utils.py     # Processes customer journeys and calculates metrics
│   │
│   ├── reports                         # Stores exported CSV reports
│       ├── channel_reporting.csv       # Final report with marketing channel performance
```

---

## **5. API Request Batching**  
The IHC API enforces a **limit of 199 customer journeys per POST request**. To handle this, the pipeline:
1. **Splits the data into batches of ≤199 records**.  
2. **Sends each batch sequentially in a loop** until all customer journeys are processed.  
3. **Logs successful requests and tracks partial failures**.  
4. **Retries failed batches separately** to ensure data completeness.  

### **Example Implementation**  
```python
chunk_size = 199  # IHC API limit
chunks = [customer_journeys[i:i + chunk_size] for i in range(0, len(customer_journeys), chunk_size)]

for i, chunk in enumerate(chunks):
    response = requests.post(API_URL, json={"customer_journeys": chunk}, headers={"x-api-key": API_KEY})
    if response.status_code == 200:
        log.info(f"✅ Batch {i+1} processed successfully!")
    else:
        log.error(f"❌ Batch {i+1} failed: {response.text}")
```

---

## **6. Future Improvements**  
### **🔹 Move from SQLite to AWS Redshift**  
- SQLite is **limited in scalability**.  
- **AWS Redshift** would allow:
  - Faster querying on large datasets.  
  - Parallel processing for performance improvements.  
  - Better integration with AWS analytics tools.  

### **🔹 Store Reports in AWS S3 Instead of Local Storage**  
- Instead of keeping reports **locally**, integrate with **AWS S3**.  
- Use **Airflow S3 Operators** to automatically upload reports.  
- Benefits:
  - **Scalability**: Handles large files efficiently.  
  - **Availability**: Data is accessible across distributed teams.  

### **🔹 Automate Tableau Report Generation**  
- Set up a **separate reporting pipeline** to:
  - Refresh **daily marketing dashboards**.  
  - Extract structured data from **database views**.  
  - Push updated data to **Tableau Server**.  

---

## **7. Conclusion**  
This pipeline **automates customer attribution modeling**, **enhances marketing insights**, and **ensures scalable data processing**.  

🚀 Future upgrades (AWS Redshift, S3, Tableau automation) would further enhance its capabilities.


