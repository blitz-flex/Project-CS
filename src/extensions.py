from flask_sqlalchemy import SQLAlchemy

# Initialize Flask-SQLAlchemy
db = SQLAlchemy()

# Models will be imported later in the app factory to avoid circular imports
