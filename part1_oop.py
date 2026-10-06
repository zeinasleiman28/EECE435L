"""
Lab 2 - Part 1: OOP Implementation
School Management System

Classes: Person, Student, Instructor, Course (+ SchoolData to manage them).
Shows: classes/objects, inheritance, polymorphism (introduce()),
encapsulation (validated properties, _email), abstraction (Entity ABC),
data validation and JSON serialization (save/load).
"""
import json
import os
import re
from abc import ABC, abstractmethod

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,20}$")
MAX_TEXT_LENGTH = 100


class ValidationError(ValueError):
    """Raised when an object receives invalid data."""


# ---------------------------------------------------------------- validation
def validate_text(value, field, max_length=MAX_TEXT_LENGTH):
    value = str(value).strip()
    if not value:
        raise ValidationError(f"{field} cannot be empty.")
    if len(value) > max_length:
        raise ValidationError(f"{field} must be at most {max_length} characters.")
    return value


def validate_id(value, field="ID"):
    value = str(value).strip()
    if not ID_PATTERN.match(value):
        raise ValidationError(
            f"{field} must be 1-20 characters: letters, digits, '-' or '_' (no spaces).")
    return value


def validate_age(age):
    try:
        age = int(str(age).strip())
    except (TypeError, ValueError):
        raise ValidationError("Age must be a whole number.") from None
    if age < 0:
        raise ValidationError("Age cannot be negative.")
    if age > 150:
        raise ValidationError("Age must be at most 150.")
    return age


def validate_email(email):
    email = str(email).strip()
    if not EMAIL_PATTERN.match(email):
        raise ValidationError(f"Invalid email address: '{email}'.")
    return email


# ------------------------------------------------------------------- classes
class Entity(ABC):
    """Abstract base for everything stored in the school (abstraction)."""

    @property
    @abstractmethod
    def key(self):
        """Unique identifier of the entity."""

    @abstractmethod
    def to_dict(self):
        """Return a JSON-serializable dict."""


class Person(Entity):
    def __init__(self, name, age, email):
        self.name = name      # each assignment goes through a validating setter
        self.age = age
        self.email = email

    # Encapsulation: attributes are stored privately and validated on write.
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = validate_text(value, "Name")

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        self._age = validate_age(value)

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = validate_email(value)

    @property
    def key(self):
        return self.email

    def introduce(self):
        return f"Hello, my name is {self.name} and I am {self.age} years old."

    def to_dict(self):
        return {"name": self.name, "age": self.age, "email": self.email}

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})"


class Student(Person):
    def __init__(self, name, age, email, student_id):
        super().__init__(name, age, email)
        self.student_id = validate_id(student_id, "Student ID")
        self.registered_courses = []

    @property
    def key(self):
        return self.student_id

    def register_course(self, course):
        """Register in a course; keeps Course.enrolled_students in sync."""
        if course in self.registered_courses:
            raise ValidationError(f"{self.name} is already registered in {course.course_id}.")
        self.registered_courses.append(course)
        course.enrolled_students.append(self)

    def drop_course(self, course):
        if course not in self.registered_courses:
            raise ValidationError(f"{self.name} is not registered in {course.course_id}.")
        self.registered_courses.remove(course)
        course.enrolled_students.remove(self)

    def introduce(self):  # polymorphism: overrides Person.introduce
        courses = ", ".join(c.course_id for c in self.registered_courses) or "no courses"
        return f"{super().introduce()} I am student {self.student_id}, taking {courses}."

    def to_dict(self):
        data = super().to_dict()
        data["student_id"] = self.student_id
        data["registered_courses"] = [c.course_id for c in self.registered_courses]
        return data


class Instructor(Person):
    def __init__(self, name, age, email, instructor_id):
        super().__init__(name, age, email)
        self.instructor_id = validate_id(instructor_id, "Instructor ID")
        self.assigned_courses = []

    @property
    def key(self):
        return self.instructor_id

    def assign_course(self, course):
        """Assign a course; a course has one instructor, so the old one loses it."""
        if course.instructor is self:
            raise ValidationError(f"{self.name} already teaches {course.course_id}.")
        if course.instructor is not None:
            course.instructor.assigned_courses.remove(course)
        course.instructor = self
        self.assigned_courses.append(course)

    def unassign_course(self, course):
        if course.instructor is not self:
            raise ValidationError(f"{self.name} does not teach {course.course_id}.")
        self.assigned_courses.remove(course)
        course.instructor = None

    def introduce(self):  # polymorphism
        courses = ", ".join(c.course_id for c in self.assigned_courses) or "no courses yet"
        return f"{super().introduce()} I am instructor {self.instructor_id}, teaching {courses}."

    def to_dict(self):
        data = super().to_dict()
        data["instructor_id"] = self.instructor_id
        data["assigned_courses"] = [c.course_id for c in self.assigned_courses]
        return data


class Course(Entity):
    def __init__(self, course_id, course_name, instructor=None):
        self.course_id = validate_id(course_id, "Course ID")
        self.course_name = course_name
        self.instructor = None
        self.enrolled_students = []
        if instructor is not None:
            instructor.assign_course(self)

    @property
    def course_name(self):
        return self._course_name

    @course_name.setter
    def course_name(self, value):
        self._course_name = validate_text(value, "Course name")

    @property
    def key(self):
        return self.course_id

    def add_student(self, student):
        student.register_course(self)

    def remove_student(self, student):
        student.drop_course(self)

    def to_dict(self):
        return {
            "course_id": self.course_id,
            "course_name": self.course_name,
            "instructor_id": self.instructor.instructor_id if self.instructor else None,
        }

    def __str__(self):
        return f"{self.course_id} - {self.course_name}"

    def __repr__(self):
        return f"Course({self.course_id!r})"


# ------------------------------------------------------------ data management
class SchoolData:
    """Holds all records and handles search, editing and save/load."""

    def __init__(self):
        self.students = {}
        self.instructors = {}
        self.courses = {}

    # --- create
    def add_student(self, student):
        self._check_new(self.students, student.student_id, "Student")
        self.students[student.student_id] = student

    def add_instructor(self, instructor):
        self._check_new(self.instructors, instructor.instructor_id, "Instructor")
        self.instructors[instructor.instructor_id] = instructor

    def add_course(self, course):
        self._check_new(self.courses, course.course_id, "Course")
        self.courses[course.course_id] = course

    @staticmethod
    def _check_new(table, key, label):
        if key in table:
            raise ValidationError(f"{label} with ID '{key}' already exists.")

    # --- update (validate everything first so a bad field changes nothing)
    def update_student(self, student_id, name, age, email):
        return self._update_person(self.students[student_id], name, age, email)

    def update_instructor(self, instructor_id, name, age, email):
        return self._update_person(self.instructors[instructor_id], name, age, email)

    @staticmethod
    def _update_person(person, name, age, email):
        name, age, email = validate_text(name, "Name"), validate_age(age), validate_email(email)
        person.name, person.age, person.email = name, age, email
        return person

    def update_course(self, course_id, course_name, instructor_id=None):
        course = self.courses[course_id]
        course.course_name = course_name
        new_instructor = self.instructors[instructor_id] if instructor_id else None
        if new_instructor is not course.instructor:
            if new_instructor is None:
                course.instructor.unassign_course(course)
            else:
                new_instructor.assign_course(course)
        return course

    # --- delete (also removes references from related objects)
    def remove_student(self, student_id):
        student = self.students.pop(student_id)
        for course in list(student.registered_courses):
            student.drop_course(course)
        return student

    def remove_instructor(self, instructor_id):
        instructor = self.instructors.pop(instructor_id)
        for course in list(instructor.assigned_courses):
            instructor.unassign_course(course)
        return instructor

    def remove_course(self, course_id):
        course = self.courses.pop(course_id)
        for student in list(course.enrolled_students):
            student.drop_course(course)
        if course.instructor:
            course.instructor.unassign_course(course)
        return course

    # --- search by name, ID or course (ID or name)
    def search(self, query=""):
        q = query.strip().lower()

        def hit(*values):
            return not q or any(q in str(v).lower() for v in values)

        def course_terms(courses):
            return [t for c in courses for t in (c.course_id, c.course_name)]

        return {
            "students": [s for s in self.students.values()
                         if hit(s.name, s.student_id, *course_terms(s.registered_courses))],
            "instructors": [i for i in self.instructors.values()
                            if hit(i.name, i.instructor_id, *course_terms(i.assigned_courses))],
            "courses": [c for c in self.courses.values()
                        if hit(c.course_id, c.course_name,
                               c.instructor.name if c.instructor else "")],
        }

    # --- serialization
    def to_dict(self):
        return {
            "instructors": [i.to_dict() for i in self.instructors.values()],
            "courses": [c.to_dict() for c in self.courses.values()],
            "students": [s.to_dict() for s in self.students.values()],
        }

    @classmethod
    def from_dict(cls, data):
        school = cls()
        try:
            for d in data.get("instructors", []):
                school.add_instructor(Instructor(d["name"], d["age"], d["email"], d["instructor_id"]))
            for d in data.get("courses", []):
                course = Course(d["course_id"], d["course_name"])
                school.add_course(course)
                if d.get("instructor_id"):
                    school.instructors[d["instructor_id"]].assign_course(course)
            for d in data.get("students", []):
                student = Student(d["name"], d["age"], d["email"], d["student_id"])
                school.add_student(student)
                for course_id in d.get("registered_courses", []):
                    student.register_course(school.courses[course_id])
        except (KeyError, TypeError, AttributeError) as e:
            raise ValidationError(f"Data file is malformed (problem with {e}).") from None
        return school

    def save(self, path):
        tmp = f"{path}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        os.replace(tmp, path)  # never leave a half-written file behind

    @classmethod
    def load(cls, path):
        with open(path, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Not a valid JSON file: {e}") from None
        return cls.from_dict(data)


def build_sample_school():
    school = SchoolData()
    smith = Instructor("Dr. Rana Smith", 45, "rsmith@aub.edu.lb", "I001")
    haddad = Instructor("Dr. Karim Haddad", 38, "khaddad@aub.edu.lb", "I002")
    for i in (smith, haddad):
        school.add_instructor(i)

    eece230 = Course("EECE230", "Introduction to Programming", smith)
    eece330 = Course("EECE330", "Data Structures", haddad)
    eece435 = Course("EECE435", "Software Tools Lab")
    for c in (eece230, eece330, eece435):
        school.add_course(c)

    students = [
        Student("Lina Khoury", 19, "lina.khoury@mail.aub.edu", "S001"),
        Student("Omar Saad", 20, "omar.saad@mail.aub.edu", "S002"),
        Student("Maya Nassar", 21, "maya.nassar@mail.aub.edu", "S003"),
    ]
    for s in students:
        school.add_student(s)
    students[0].register_course(eece230)
    students[0].register_course(eece435)
    eece330.add_student(students[1])
    students[2].register_course(eece435)
    return school


if __name__ == "__main__":
    school = build_sample_school()

    print("== Polymorphism: same introduce() call, different behaviour ==")
    people = list(school.instructors.values()) + list(school.students.values())
    for person in people:
        print(" -", person.introduce())

    print("\n== Validation ==")
    for args in [("Bad Email", 20, "not-an-email", "S9"),
                 ("Negative Age", -3, "x@y.com", "S9"),
                 ("", 20, "x@y.com", "S9"),
                 ("Bad Id", 20, "x@y.com", "S 9")]:
        try:
            Student(*args)
        except ValidationError as e:
            print(" - rejected:", e)

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "school_data.json")
    school.save(path)
    loaded = SchoolData.load(path)
    print(f"\n== Serialization ==\n - saved and reloaded {path}")
    print(f" - {len(loaded.students)} students, {len(loaded.instructors)} instructors, "
          f"{len(loaded.courses)} courses")
    print(" - EECE435 enrolled:", [s.name for s in loaded.courses["EECE435"].enrolled_students])
    print(" - search('data'):", {k: [o.key for o in v] for k, v in loaded.search("data").items()})
