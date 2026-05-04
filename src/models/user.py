from src.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hash = db.Column(db.String(255), nullable=False)
    admin = db.Column(db.Integer, default=0)
    img = db.Column(db.String(255), default='default_user.jpg')

    @property
    def enrollments(self):
        from src.models.course import users_courses
        return db.session.query(users_courses).filter_by(user_id=self.id).count()

    def set_password(self, password):
        self.hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
