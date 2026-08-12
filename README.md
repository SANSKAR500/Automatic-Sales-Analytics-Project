# Automatic Sales Analytics Project

Upload any sales CSV/Excel file → it gets auto-cleaned → you get KPIs,
charts, and a written report. Works as a Streamlit dashboard or a
Jupyter notebook.

## Files in this folder

| File | Purpose |
|---|---|
| `data_cleaner.py` | Loads a file, guesses which columns mean what, cleans it |
| `analyzer.py` | Computes KPIs, trends, top products/regions, writes the report |
| `app.py` | The Streamlit dashboard (the app you interact with in a browser) |
| `sales_analysis_notebook.ipynb` | Jupyter notebook for manual/step-by-step exploration |
| `sample_sales_data.csv` | Fake sample data to test everything immediately |
| `requirements.txt` | List of Python libraries needed |
| `reports/` | Where saved text reports land |

## Setup (do this once)

1. Install Python 3.10+ if you don't have it: https://www.python.org/downloads/
2. Open a terminal **inside this folder** (`sales_analytics`).
3. (Recommended) Create a virtual environment:
   ```
   python -m venv venv
   ```
   Activate it:
   - Mac/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
4. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```

## Option A: Run the interactive dashboard (recommended)

```
streamlit run app.py
```

This opens a browser tab automatically (usually at `http://localhost:8501`).
Upload `sample_sales_data.csv` first to see it working, then try your
own files.

## Option B: Run the Jupyter notebook

```
jupyter notebook
```

Then open `sales_analysis_notebook.ipynb` in the browser tab that opens,
and run each cell in order with Shift+Enter.

## Using your own sales files

Your file just needs *some* of these kinds of columns — names don't
have to match exactly, the tool guesses:
- A date column (e.g. "Order Date", "Date")
- A revenue/sales amount column (e.g. "Sales", "Revenue", "Amount")
- Optionally: Product, Region, Customer, Category, Quantity columns

If the auto-detection guesses wrong, the dashboard has a "Detected
columns" panel where you can manually correct it.

## Troubleshooting

- **"streamlit: command not found"** → make sure you activated your
  virtual environment and ran `pip install -r requirements.txt`.
- **Dates not parsing correctly** → open the "Detected columns" panel
  in the dashboard and confirm the right column is picked as "date".
- **Currency symbols causing errors** → already handled automatically;
  `$`, `,`, and other symbols are stripped from number columns.
