from dotenv import load_dotenv
load_dotenv()

from functools import wraps
from flask import Flask, jsonify, Response, request, render_template
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
from cache import MemoryCache

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Initialize cache
cache = MemoryCache()

# Sample data for demonstration
sample_data = {
    'sales': pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=100, freq='D'),
        'product': ['Product A', 'Product B', 'Product C'] * 34 + ['Product A', 'Product B'],
        'sales': [100 + i * 2 + (i % 10) * 5 for i in range(100)],
        'region': ['North', 'South', 'East', 'West'] * 25
    }),
    'customers': pd.DataFrame({
        'customer_id': range(1, 51),
        'name': [f'Customer {i}' for i in range(1, 51)],
        'age': [25 + (i % 40) for i in range(50)],
        'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'] * 10,
        'total_spent': [1000 + i * 50 for i in range(50)]
    })
}

def requires_cache(fields):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            id = request.args.get('id')
            
            if id is None:
                return jsonify({"type": "error", "error": "No id provided"})
            
            for field in fields:
                if cache.get(id=id, field=field) is None:
                    return jsonify({"type": "error", "error": f"No {field} found"})
            
            field_values = {field: cache.get(id=id, field=field) for field in fields}
            field_values['id'] = id
            
            return f(*args, **field_values, **kwargs)
        return decorated
    return decorator

def generate_sql_from_question(question):
    """Simple rule-based SQL generation for demo purposes"""
    question_lower = question.lower()
    
    if 'sales' in question_lower:
        if 'total' in question_lower or 'sum' in question_lower:
            return "SELECT SUM(sales) as total_sales FROM sales"
        elif 'product' in question_lower:
            return "SELECT product, SUM(sales) as total_sales FROM sales GROUP BY product"
        elif 'region' in question_lower:
            return "SELECT region, SUM(sales) as total_sales FROM sales GROUP BY region"
        elif 'date' in question_lower or 'time' in question_lower:
            return "SELECT date, SUM(sales) as daily_sales FROM sales GROUP BY date ORDER BY date"
        else:
            return "SELECT * FROM sales LIMIT 10"
    
    elif 'customer' in question_lower:
        if 'age' in question_lower:
            return "SELECT age, COUNT(*) as count FROM customers GROUP BY age ORDER BY age"
        elif 'city' in question_lower:
            return "SELECT city, COUNT(*) as customer_count FROM customers GROUP BY city"
        elif 'spent' in question_lower or 'spending' in question_lower:
            return "SELECT name, total_spent FROM customers ORDER BY total_spent DESC LIMIT 10"
        else:
            return "SELECT * FROM customers LIMIT 10"
    
    else:
        return "SELECT 'Please ask about sales or customers' as message"

def execute_sql(sql):
    """Execute SQL-like queries on our sample data"""
    try:
        # Simple query parser for demo
        if 'FROM sales' in sql:
            df = sample_data['sales'].copy()
        elif 'FROM customers' in sql:
            df = sample_data['customers'].copy()
        else:
            return pd.DataFrame({'message': ['Query not supported in demo']})
        
        # Handle basic aggregations
        if 'SUM(sales)' in sql and 'GROUP BY product' in sql:
            return df.groupby('product')['sales'].sum().reset_index()
        elif 'SUM(sales)' in sql and 'GROUP BY region' in sql:
            return df.groupby('region')['sales'].sum().reset_index()
        elif 'SUM(sales)' in sql and 'GROUP BY date' in sql:
            return df.groupby('date')['sales'].sum().reset_index()
        elif 'SUM(sales)' in sql:
            return pd.DataFrame({'total_sales': [df['sales'].sum()]})
        elif 'COUNT(*)' in sql and 'GROUP BY age' in sql:
            return df.groupby('age').size().reset_index(name='count')
        elif 'COUNT(*)' in sql and 'GROUP BY city' in sql:
            return df.groupby('city').size().reset_index(name='customer_count')
        elif 'ORDER BY total_spent DESC' in sql:
            return df.nlargest(10, 'total_spent')[['name', 'total_spent']]
        elif 'LIMIT 10' in sql:
            return df.head(10)
        else:
            return df.head(10)
            
    except Exception as e:
        return pd.DataFrame({'error': [str(e)]})

def generate_plotly_figure(question, sql, df):
    """Generate appropriate visualization based on data"""
    try:
        if df.empty or 'error' in df.columns:
            return None
        
        # Determine chart type based on data structure
        if len(df.columns) == 2 and df.dtypes.iloc[1] in ['int64', 'float64']:
            # Bar chart for categorical data
            fig = px.bar(df, x=df.columns[0], y=df.columns[1], 
                        title=f"Analysis: {question}")
        elif 'date' in df.columns:
            # Line chart for time series
            fig = px.line(df, x='date', y=df.columns[1], 
                         title=f"Time Series: {question}")
        elif len(df.columns) > 2:
            # Scatter plot for multi-dimensional data
            fig = px.scatter(df, x=df.columns[0], y=df.columns[1], 
                           title=f"Scatter Plot: {question}")
        else:
            # Default bar chart
            fig = px.bar(df, x=df.columns[0], y=df.columns[1] if len(df.columns) > 1 else df.columns[0],
                        title=f"Data Visualization: {question}")
        
        fig.update_layout(
            template="plotly_white",
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        return fig
    except Exception as e:
        print(f"Error generating plot: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v0/generate_questions', methods=['GET'])
def generate_questions():
    sample_questions = [
        "What are the total sales by product?",
        "Show me sales by region",
        "What are the daily sales trends?",
        "Who are the top spending customers?",
        "Show customer distribution by city",
        "What is the age distribution of customers?"
    ]
    
    return jsonify({
        "type": "question_list",
        "questions": sample_questions,
        "header": "Here are some questions you can ask:"
    })

@app.route('/api/v0/generate_sql', methods=['GET'])
def generate_sql():
    question = request.args.get('question')
    
    if question is None:
        return jsonify({"type": "error", "error": "No question provided"})
    
    id = cache.generate_id(question=question)
    sql = generate_sql_from_question(question)
    
    cache.set(id=id, field='question', value=question)
    cache.set(id=id, field='sql', value=sql)
    
    return jsonify({
        "type": "sql",
        "id": id,
        "text": sql,
    })

@app.route('/api/v0/run_sql', methods=['GET'])
@requires_cache(['sql'])
def run_sql(id: str, sql: str):
    try:
        df = execute_sql(sql)
        cache.set(id=id, field='df', value=df)
        
        return jsonify({
            "type": "df",
            "id": id,
            "df": df.head(10).to_json(orient='records'),
        })
    except Exception as e:
        return jsonify({"type": "error", "error": str(e)})

@app.route('/api/v0/download_csv', methods=['GET'])
@requires_cache(['df'])
def download_csv(id: str, df):
    csv = df.to_csv(index=False)
    
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=query_results_{id}.csv"}
    )

@app.route('/api/v0/generate_plotly_figure', methods=['GET'])
@requires_cache(['df', 'question', 'sql'])
def generate_plotly_figure_endpoint(id: str, df, question, sql):
    try:
        fig = generate_plotly_figure(question, sql, df)
        
        if fig is None:
            return jsonify({"type": "error", "error": "Could not generate visualization"})
        
        fig_json = fig.to_json()
        cache.set(id=id, field='fig_json', value=fig_json)
        
        return jsonify({
            "type": "plotly_figure",
            "id": id,
            "fig": fig_json,
        })
    except Exception as e:
        return jsonify({"type": "error", "error": str(e)})

@app.route('/api/v0/get_question_history', methods=['GET'])
def get_question_history():
    return jsonify({
        "type": "question_history", 
        "questions": cache.get_all(field_list=['question'])
    })

@app.route('/api/v0/load_question', methods=['GET'])
@requires_cache(['question', 'sql', 'df'])
def load_question(id: str, question, sql, df):
    try:
        fig_json = cache.get(id=id, field='fig_json')
        
        return jsonify({
            "type": "question_cache",
            "id": id,
            "question": question,
            "sql": sql,
            "df": df.head(10).to_json(orient='records'),
            "fig": fig_json,
        })
    except Exception as e:
        return jsonify({"type": "error", "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)