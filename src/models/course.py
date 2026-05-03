from src.extensions import db

# Association table for users and courses (Enrollments)
users_courses = db.Table('users_courses',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True)
)

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), default='default_course.jpg')

    def __repr__(self):
        return f'<Course {self.name}>'

class Promo(db.Model):
    __tablename__ = 'promo'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Promo {self.name}>'
