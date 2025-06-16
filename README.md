# Flask Database Chat Application

A modern Flask web application that provides a chat interface for querying databases using natural language.

## Features

- 🗣️ Natural language to SQL conversion
- 📊 Automatic data visualization with Plotly
- 📋 Interactive data tables
- 📥 CSV export functionality
- 📚 Query history
- 🎨 Modern, responsive UI with Tailwind CSS
- ⚡ Real-time chat interface

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser:**
   Navigate to `http://localhost:5000`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main chat interface |
| `/api/v0/generate_questions` | GET | Get sample questions |
| `/api/v0/generate_sql` | GET | Convert question to SQL |
| `/api/v0/run_sql` | GET | Execute SQL query |
| `/api/v0/generate_plotly_figure` | GET | Generate visualization |
| `/api/v0/download_csv` | GET | Download results as CSV |
| `/api/v0/get_question_history` | GET | Get query history |

## Sample Questions

Try asking questions like:
- "What are the total sales by product?"
- "Show me sales by region"
- "Who are the top spending customers?"
- "What is the age distribution of customers?"

## Architecture

- **Backend**: Flask with RESTful API
- **Frontend**: Vanilla JavaScript with Tailwind CSS
- **Visualization**: Plotly.js
- **Data**: Pandas DataFrames
- **Caching**: In-memory cache system

## Customization

### Adding New Data Sources

1. Update the `sample_data` dictionary in `app.py`
2. Modify the `generate_sql_from_question()` function
3. Update the `execute_sql()` function to handle new queries

### Styling

The application uses Tailwind CSS for styling. You can customize the appearance by modifying the CSS classes in the HTML template.

## Production Deployment

For production deployment:

1. Set `FLASK_ENV=production` in your environment
2. Use a production WSGI server like Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
3. Consider using a reverse proxy like Nginx
4. Implement proper database connections instead of sample data

## License

MIT License - feel free to use this code for your own projects!