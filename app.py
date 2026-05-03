from src import create_app
from src.extensions import db

app = create_app()

# Create all DB tables on first run (needed on Render / fresh deployments)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
