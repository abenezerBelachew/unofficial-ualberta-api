import json
from fastapi import FastAPI, HTTPException
from typing import Optional


app = FastAPI(
    title="Unofficial University of Alberta API",
    description="API for course, faculty, subject and class schedules.",
    version="2020.2021", # The Year it was scraped
)

def open_and_return(file_name):
    """
    Open the file and return what's in it.
    """
    with open(file_name, "r") as file:
        data = json.load(file)
        return data


@app.get("/", tags=["Endpoints"])
def endpoints():
    """
    All the available endpoints
    """
    return [{"endpoints": {
                "/docs",
                "/faculties",
                "/faculties/{faculty_code}",
                "/subjects",
                "/subjects/{subject_code}",
                "/courses/",
                "/courses/{course_code}"
            }}]


# *******************************************
# Faculty-related enpoints
# *******************************************
@app.get("/faculties", tags=["Faculties"])
def get_faculties():
    """
    The different faculties at the University.
    """
    faculty_file = "data/faculties.json"
    faculties = open_and_return(faculty_file)
    return [faculties]

@app.get("/faculties/{faculty_code}", tags=["Faculties"])
def get_faculty(faculty_code: str):
    """
    Get details about one faculty.
    """
    faculty_file = "data/faculties.json"
    faculties = open_and_return(faculty_file)
    faculty_code = faculty_code.upper()
    if faculty_code not in faculties:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return faculties[faculty_code]

# *******************************************
# Subject-related enpoints
# *******************************************
@app.get("/subjects", tags=["Subjects"])
def get_subjects():
    """
    The different subjects at the university.
    """
    subject_file = "data/subjects.json"
    subjects = open_and_return(subject_file)
    return [subjects]


@app.get("/subjects/{subject_code}", tags=["Subjects"])
def get_subject(subject_code: str):
    """
    Get details about one subject.
    """
    subject_file = "data/subjects.json"
    subjects = open_and_return(subject_file)
    
    if subject_code not in subjects:
            raise HTTPException(status_code=404, detail="Subject not found")
    return subjects[subject_code]


# *******************************************
# Course-related enpoints
# *******************************************
@app.get("/courses", tags=["Courses"])
def get_courses():
    """
    Courses offered in 2020/2021 at the University of Alberta.
    """
    course_file = "data/courses.json"
    courses = open_and_return(course_file)
    try:
        return [courses]
    except:
        return {"Error": "Not Found"}


@app.get("/courses/{course_code}", tags=["Courses"])
def get_course(course_code: str):
    """
    Get details about one course.
    """
    course_file = "data/courses.json"
    courses = open_and_return(course_file)
    course_code = course_code.upper()

    if course_code not in courses:
            raise HTTPException(status_code=404, detail="Course not found. Make sure there is no space (e.g. CMPUT401 and not CMPUT 401)")
    return courses[course_code]


# *******************************************
# ClassSchedule-related enpoints
# *******************************************

@app.get("/class_schedules/", tags=["ClassSchedules"])
def get_class_schedules():
    """
    Get all course data for an academic year
    """
    class_schedules_file = "data/class_schedules.json"
    class_schedules = open_and_return(class_schedules_file)
    try:
        return class_schedules
    except:
        return {"Error": "Not Found"}
    

@app.get("/class_schedules/{course_code}", tags=["ClassSchedules"])
def get_class_schedule(course_code: str):
    """
    Get class schedule for a specific course.
    """
    class_schedules_file = "data/class_schedules.json"
    class_schedules = open_and_return(class_schedules_file)
    course_code = course_code.upper()
    if course_code not in class_schedules:
        raise HTTPException(status_code=404, detail="Course not found")
    return class_schedules[course_code]


@app.get("/class_schedules/{course_code}/{term_code}", tags=["ClassSchedules"])
def get_class_schedule_for_term(term_code: str, course_code: str):
    """
    Get class schedule for a specific course in a specific term.
    """
    class_schedules_file = "data/class_schedules.json"
    class_schedules = open_and_return(class_schedules_file)
    course_code = course_code.upper()

    if course_code not in class_schedules:
            raise HTTPException(status_code=404, detail="Course not found")
    if term_code not in class_schedules[course_code]:
            raise HTTPException(status_code=404, detail=f"{term_code} not found in {course_code}.")
    return class_schedules[course_code][term_code]


@app.get("/class_schedules/lectures/{course_code}/{term_code}", tags=["ClassSchedules"])
def get_lectures_for_course(course_code: str, term_code: str):
    """
    Get class data for lectures for a specific course in a specific term.
    """
    class_schedules_file = "data/class_schedules.json"
    class_schedules = open_and_return(class_schedules_file)
    course_code = course_code.upper()
    # term_code = term_code.upper()

    if course_code not in class_schedules:
        raise HTTPException(status_code=404, detail="Course not found")
    if term_code not in class_schedules[course_code]:
        raise HTTPException(status_code=404, detail=f"{course_code} not offered in {term_code}.")

    try:
        return class_schedules[course_code][term_code]["Lectures"]
    except:
        return {"detail": "No lectures for this course."}


@app.get("/class_schedules/labs/{course_code}/{term_code}", tags=["ClassSchedules"])
def get_labs_for_course(course_code: str, term_code: str):
    """
    Get class data for labs for a specific course in a specific term.
    """
    class_schedules_file = "data/class_schedules.json"
    class_schedules = open_and_return(class_schedules_file)
    course_code = course_code.upper()
    # term_code = term_code.upper()

    if course_code not in class_schedules:
        raise HTTPException(status_code=404, detail="Course not found")
    if term_code not in class_schedules[course_code]:
        raise HTTPException(status_code=404, detail=f"{course_code} not found in {term_code}.")
    try:
        return class_schedules[course_code][term_code]["Labs"]
    except:
        return {"detail": "No labs for this course."}

@app.get("/class_schedules/seminars/{course_code}/{term_code}", tags=["ClassSchedules"])
def get_seminars_for_course(course_code: str, term_code: str):
    """
    Get class data for seminars for a specific course in a specific term.
    """
    class_schedules_file = "data/class_schedules.json"
    class_schedules = open_and_return(class_schedules_file)
    course_code = course_code.upper()
    # term_code = term_code.upper()

    if course_code not in class_schedules:
        raise HTTPException(status_code=404, detail="Course not found")
    if term_code not in class_schedules[course_code]:
        raise HTTPException(status_code=404, detail=f"{course_code} not offered in {term_code}.")

    try:
        return class_schedules[course_code][term_code]["Seminars"]
    except:
        return {"detail": "No Seminars for this course."}
