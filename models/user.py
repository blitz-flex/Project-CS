from werkzeug.security import check_password_hash, generate_password_hash


class User:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, user_id):
        """Get user by ID"""
        return self.db.execute("SELECT * FROM users WHERE id = ?", user_id)

    def get_by_username(self, username):
        """Get user by username"""
        return self.db.execute("SELECT * FROM users WHERE username = ?", username)

    def create(self, username, password):
        """Create new user"""
        hash_password = generate_password_hash(password)
        self.db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                        username, hash_password)
        return self.get_by_username(username)

    def update_password(self, user_id, new_password):
        """Update user password"""
        hash_password = generate_password_hash(new_password)
        self.db.execute("UPDATE users SET hash = ? WHERE id = ?",
                        hash_password, user_id)

    def update_image(self, user_id, image_path):
        """Update user profile image"""
        self.db.execute("UPDATE users SET img = ? WHERE id = ?", image_path, user_id)

    def delete(self, user_id):
        """Delete user and their enrollments"""
        self.db.execute("DELETE FROM users_courses WHERE user_id = ?", user_id)
        self.db.execute("DELETE FROM users WHERE id = ?", user_id)

    def verify_password(self, user_id, password):
        """Verify user password"""
        user = self.get_by_id(user_id)
        if len(user) == 1:
            return check_password_hash(user[0]["hash"], password)
        return False

    def get_all(self):
        """Get all users"""
        return self.db.execute("SELECT id, username, admin FROM users ORDER BY id DESC")

    def get_all_non_admin(self):
        """Get all non-admin users"""
        return self.db.execute("SELECT id, username, admin FROM users WHERE admin = 0 ORDER BY id DESC")

    def count_non_admin(self):
        """Count non-admin users"""
        return self.db.execute("SELECT COUNT(*) as count FROM users WHERE admin = 0")[0]["count"]

    def get_recent(self, limit=5):
        """Get recent non-admin users"""
        return self.db.execute("SELECT username FROM users WHERE admin = 0 ORDER BY id DESC LIMIT ?", limit)

    def is_admin(self, user_id):
        """Check if user is admin"""
        user = self.get_by_id(user_id)
        if len(user) == 1:
            return user[0]["admin"] == 1
        return False

    def has_enrolled_courses(self, user_id):
        """Check if the user is enrolled in any courses"""
        courses = self.db.execute("SELECT course_id FROM users_courses WHERE user_id = ?", user_id)
        return len(courses) > 0
