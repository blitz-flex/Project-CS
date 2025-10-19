class Course:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        """Get all courses"""
        return self.db.execute("SELECT * FROM courses")

    def get_by_id(self, course_id):
        """Get course by ID"""
        return self.db.execute("SELECT * FROM courses WHERE id = ?", course_id)

    def get_latest(self, limit=3):
        """Get latest courses"""
        return self.db.execute("SELECT * FROM courses ORDER BY id DESC LIMIT ?", limit)

    def search(self, query):
        """Search courses by name"""
        return self.db.execute("SELECT * FROM courses WHERE name LIKE ?", f"%{query}%")

    def create(self, name, price, description, image):
        """Create new course"""
        self.db.execute("INSERT INTO courses (name, price, description, image) VALUES (?, ?, ?, ?)",
                        name, price, description, image)

    def update(self, course_id, name, price, description, image):
        """Update course"""
        self.db.execute("UPDATE courses SET name = ?, price = ?, description = ?, image = ? WHERE id = ?",
                        name, price, description, image, course_id)

    def delete(self, course_id):
        """Delete course and all enrollments"""
        self.db.execute("DELETE FROM users_courses WHERE course_id = ?", course_id)
        self.db.execute("DELETE FROM courses WHERE id = ?", course_id)

    def get_user_courses(self, user_id):
        """Get all courses enrolled by user"""
        return self.db.execute(
            "SELECT * FROM users_courses, courses WHERE courses.id = users_courses.course_id AND user_id = ?",
            user_id)

    def is_user_enrolled(self, user_id, course_id):
        """Check if user is enrolled in course"""
        result = self.db.execute(
            "SELECT * FROM users_courses WHERE course_id = ? AND user_id = ?",
            course_id, user_id)
        return len(result) > 0

    def enroll_user(self, user_id, course_id):
        """Enroll user in course"""
        if not self.is_user_enrolled(user_id, course_id):
            self.db.execute("INSERT INTO users_courses (user_id, course_id) VALUES (?, ?)",
                            user_id, course_id)

    def count(self):
        """Count all courses"""
        return self.db.execute("SELECT COUNT(*) as count FROM courses")[0]["count"]

    def count_enrollments(self):
        """Count all course enrollments"""
        return self.db.execute("SELECT COUNT(*) as count FROM users_courses")[0]["count"]

    def get_popular(self, limit=5):
        """Get popular courses by enrollment count"""
        return self.db.execute(
            "SELECT c.name, COUNT(uc.user_id) as enrollments FROM courses c "
            "LEFT JOIN users_courses uc ON c.id = uc.course_id "
            "GROUP BY c.id ORDER BY enrollments DESC LIMIT ?", limit)

    def get_cart_courses(self, course_ids):
        """Get courses by list of IDs (for cart)"""
        if not course_ids:
            return []
        return self.db.execute("SELECT * FROM courses WHERE id IN (?)", course_ids)

    def get_cart_total(self, course_ids):
        """Get total price of courses in cart"""
        if not course_ids:
            return 0
        result = self.db.execute("SELECT SUM(price) FROM courses WHERE id IN (?)", course_ids)
        return result[0]["SUM(price)"] if result[0]["SUM(price)"] else 0

    def get_cart_count(self, course_ids):
        """Get count of courses in cart"""
        if not course_ids:
            return 0
        result = self.db.execute("SELECT COUNT(*) FROM courses WHERE id IN (?)", course_ids)
        return result[0]["COUNT(*)"]


class Promo:
    def __init__(self, db):
        self.db = db

    def get_by_name(self, promo_name):
        """Get promo code by name"""
        return self.db.execute("SELECT * FROM promo WHERE name = ?", promo_name)

    def get_by_ids(self, promo_ids):
        """Get promo codes by list of IDs"""
        if not promo_ids:
            return []
        return self.db.execute("SELECT * FROM promo WHERE id IN (?)", promo_ids)

    def get_total_value(self, promo_ids):
        """Get total discount value from promo codes"""
        if not promo_ids:
            return 0
        result = self.db.execute("SELECT SUM(value) FROM promo WHERE id IN (?)", promo_ids)
        return result[0]["SUM(value)"] if result[0]["SUM(value)"] else 0
