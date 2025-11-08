# FinCo Installation Guide

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- git (optional, for cloning the repository)

## Installation Steps

### 1. Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd finco

# Or download and extract the ZIP file, then navigate to the directory
cd finco
```

### 2. Create a Virtual Environment (Recommended)

Creating a virtual environment isolates your project dependencies from your system Python installation.

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the beginning of your terminal prompt, indicating the virtual environment is active.

### 3. Install Dependencies

With your virtual environment activated, install all required packages:

```bash
pip install -r requirements.txt
```

This will install:
- **streamlit** - Web application framework
- **pandas** - Data manipulation and analysis
- **SQLAlchemy** - Database ORM
- **matplotlib** - Data visualization
- **plotly** - Interactive charts
- **pdfplumber** - PDF text extraction
- **python-dotenv** - Environment variable management
- **bcrypt** - Password hashing
- **pytest** - Testing framework
- And additional utilities

### 4. Set Up Environment Variables

Create your `.env` file from the example:

```bash
# On macOS/Linux
cp .env.example .env

# On Windows
copy .env.example .env
```

Edit `.env` and update the values:

```env
DATABASE_URL=sqlite:///finance.db
SECRET_KEY=your_secret_here  # Change this to a random string
DEBUG=True
```

**Important:** Never commit your `.env` file to version control!

### 5. Initialize the Database

Run the database initialization script to create all tables:

```bash
python init_database.py
```

When prompted, choose whether to create sample data:
- Type `y` or `yes` to create sample data for testing
- Type `n` or `no` to start with an empty database

### 6. Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`

If it doesn't open automatically, navigate to the URL shown in your terminal.

## Verify Installation

To verify all packages are installed correctly:

```bash
pip list
```

You should see all the packages from `requirements.txt` listed.

## Troubleshooting

### Issue: `ModuleNotFoundError`

**Solution:** Make sure your virtual environment is activated and all dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: Database errors on startup

**Solution:** Reinitialize the database:
```bash
rm finance.db  # Delete the existing database
python init_database.py  # Create a fresh database
```

### Issue: Port 8501 already in use

**Solution:** Either stop the other Streamlit process or use a different port:
```bash
streamlit run app.py --server.port 8502
```

### Issue: Permission errors on macOS/Linux

**Solution:** Use Python 3 explicitly:
```bash
python3 -m venv venv
python3 -m pip install -r requirements.txt
```

## Running Tests

To run the test suite:

```bash
pytest
```

To run tests with coverage report:

```bash
pytest --cov=. --cov-report=html
```

## Updating Dependencies

To update all packages to their latest compatible versions:

```bash
pip install --upgrade -r requirements.txt
```

## Deactivating the Virtual Environment

When you're done working on the project:

```bash
deactivate
```

## Uninstallation

To completely remove the project:

1. Deactivate the virtual environment: `deactivate`
2. Delete the project directory: `rm -rf finco`
3. The virtual environment and all dependencies will be removed with the directory

## Next Steps

After successful installation:

1. Read the [README.md](README.md) for project overview
2. Check [DATABASE_GUIDE.md](DATABASE_GUIDE.md) for database operations
3. Explore the sample data (if you created it during initialization)
4. Start building your financial tracking system!

## Getting Help

If you encounter issues:

1. Check this installation guide
2. Review error messages carefully
3. Ensure all prerequisites are met
4. Check that environment variables are set correctly
5. Verify Python version: `python --version` (should be 3.10+)

## Package Versions

The project uses the following major package versions:

- Python: 3.10+
- Streamlit: 1.32.0
- Pandas: 2.1.4
- SQLAlchemy: 2.0.23
- Matplotlib: 3.8.2
- Plotly: 5.18.0
- bcrypt: 4.1.2
- pytest: 7.4.4

For a complete list, see [requirements.txt](requirements.txt)
