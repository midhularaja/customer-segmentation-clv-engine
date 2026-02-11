# Customer-Segmentation-CLV
The project cleans and analyzes e-commerce sales data using python and sql ,and presents the insights through a dashboard that updates automatically on a weekly basis

⚠️ Huge dataset not included in repo due to size constraints.

## Setup Database with Data

1. Download the raw CSV file from shared location: [CSV dataset download](https://www.kaggle.com/datasets/vijayuv/onlineretail?resource=download)

2. Place the CSV in path:  
   ` C:\Customer_Segmentation_CLV_Engine_Project\raw_dataset\OnlineRetail.csv`
   
## Project Workflow
1. Raw csv dataset downloaded from koggle
2. Data stored in sql database and cleaned 
3. Python used for RFM customer segmentation and market basket analysis
4. Cleaned & Segmented data loaded into power BI
5. Dashboard created with KPI cards ,iteractive visuals and filters
6. Python automation script refreshes the dashboard weekly

## Tools
1. sql
2. python
3. powerbi

## Python Environment Setup
A virtual environment (`venv`)was created to manage dependencies and ensure reproducibility
### steps to setup
**create a virtual environment**:
```bash
  python -m venv venv
  ```
**Activate the virtual environment**:
on windows
```bash
venv\Scripts\activate
```
**Install required packages**:
```bash
pip install -r requirements.txt
```
## Dashboard
![alt text](image.png)