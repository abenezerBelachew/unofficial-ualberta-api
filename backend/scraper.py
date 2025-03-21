import requests
import json
import re
from bs4 import BeautifulSoup as bs
from time import sleep, time


ROOT_URL = "https://apps.ualberta.ca"
MAIN_URL = "https://apps.ualberta.ca/catalogue"
DELAY_TIME = 4


def write_to_file(name_of_file, data):
    """
    Writes scraped data a json file.
    """
    with open(f'data/{name_of_file}.json', 'w') as file:
        json.dump(data, file, indent=4)


def get_faculties():
    """
    Returns the faculties offered at the university in the following format:
    {AR :  ['Faculty of Arts', 'https://apps.ualberta.ca/catalogue/faculty/ar'], 
    AU :  ['Augustana Faculty', 'https://apps.ualberta.ca/catalogue/faculty/au']}
    """
    try:
        catalog_page = requests.get(MAIN_URL, headers={'User-Agent': 'Mozilla/5.0'}).text
        course_soup = bs(catalog_page, 'html.parser')

        faculty_container = course_soup.select_one('body > div.content > div.container > div.row > div.col.col-md-6.col-lg-5.offset-lg-2 > ul')
        if not faculty_container:
            print("Error: Faculty container not found!")
            return {}

        faculty_data = dict()

        for faculty in faculty_container.find_all('li'):
            sleep(DELAY_TIME)

            faculty_title, faculty_link = [str(faculty.find('a').text), faculty.find('a').get('href')]
            faculty_code, faculty_name = faculty_title.split(' - ')
            faculty_link = ROOT_URL + faculty_link
            
            faculty_data[faculty_code] = {
                "faculty_name": faculty_name,
                "faculty_link": faculty_link
            }

        write_to_file('faculties', faculty_data)
        return faculty_data

    except Exception as e:
        print(f"Error in get_faculties(): {str(e)}")
        return {}


def get_subjects(faculty_data):
    """
    Gets the subjects available from the different faculties.
    Key   :  Value
    WKEXP :  {'name': 'Work Experience', 
               'link': 'https://apps.ualberta.ca/catalogue/course/wkexp', 
               'faculties': ['AH', 'AR', 'BC', 'EN', 'SC']}
    """
    # ---------------------------------------------------------------------
    # Data about subjects
    # E.g. {'code', 'name', 'link', 'faculty'}
    subject_data = dict()

    for faculty_code, faculty_value in faculty_data.items():
        sleep(DELAY_TIME)
        faculty_link = faculty_value["faculty_link"]
        
        try:
            # Get faculty page
            faculty_page = requests.get(faculty_link, headers={'User-Agent': 'Mozilla/5.0'}).text
            subject_soup = bs(faculty_page, 'html.parser')

            subject_container = subject_soup.select_one('div.content > div.container > ul')
            if not subject_container:
                print(f"Warning: No subjects found for faculty {faculty_code}")
                continue

            # Get subjects
            for subject in subject_container.find_all('li'):
                subject_link = subject.find('a')
                if not subject_link:
                    continue

                subject_title = subject_link.text.strip()
                subject_url = ROOT_URL + subject_link.get('href')

                if ' - ' in subject_title:
                    subject_code, subject_name = subject_title.split(' - ', 1)
                else:
                    print(f"Warning: Unexpected subject format: {subject_title}")
                    continue

                # Create subject entry if it doesn't exist yet
                if subject_code not in subject_data:
                    subject_data[subject_code] = {
                        "name": subject_name,
                        "link": subject_url,
                        "faculties": []
                    }

                if faculty_code not in subject_data[subject_code]["faculties"]:
                    subject_data[subject_code]["faculties"].append(faculty_code)

        except Exception as e:
            print(f"Error processing faculty {faculty_code}: {str(e)}")
            continue

    write_to_file('subjects', subject_data)

    return subject_data


def get_courses(subject_data):
    """
    Gets the courses in the different subjects of the different faculties.
    """
    course_data = dict()

    for subject_code, values in subject_data.items():
        sleep(DELAY_TIME)
        subject_url = subject_data[subject_code]["link"]
        subject_page = requests.get(subject_url).text 
        course_soup = bs(subject_page, 'html.parser')
        courses = course_soup.findAll('div', {'class': 'card-body'})

        for course in courses:
            course_code, course_name = course.find('h4', {'class': 'flex-grow-1'}).text.strip().split('\n')[0].split(' - ', 1)
            course_link = ROOT_URL + course.find('a').get('href')
            course_weight = course.find('b').text[2:][:2].strip()

            # Code is a bit ugly here because there is a bit of an inconsistecy 
            # due to the nature of some courses not having some of the data
            try:
                course_fee_index = course.find('b').text[2:].split('fi')[1].split(')')[0].strip()
            except:
                course_fee_index = None
            try:
                course_schedule = courses[0].find('b').text[2:].split('fi')[1].split('(')[1].split(',')[0]
            except:
                course_schedule = None        
            try:            
                course_description = course.find('p').text.split('Prerequisite')[0]
            except:
                course_description = "There is no available course description."
            try:
                course_hrs_for_lecture = course.find('b').text[2:].split('fi')[1].split('(')[1].split(',')[1].split('-')[0].strip(' )')
            except:
                course_hrs_for_lecture = None
            try:
                course_hrs_for_seminar = course.find('b').text[2:].split('fi')[1].split('(')[1].split(',')[1].split('-')[1]
            except:
                course_hrs_for_seminar = None
            try:    
                course_hrs_for_labtime = course.find('b').text[2:].split('fi')[1].split('(')[1].split(',')[1].split('-')[2].strip(')')
            except:
                course_hrs_for_labtime = None
            try:
                course_prerequisites = course.find('p').text.split('Prerequisite')[1]
            except:
                course_prerequisites = None

            # If it is a 100 level class: Junior. Else, Senior.
            if course_code.split(' ')[1].startswith('1'):
                course_type = 'Junior'
            else:
                course_type = 'Senior'
            
            # Get rid of the spaces between courses: CMPUT 404 to CMPUT404
            course_code = course_code.replace(" ", "")

            course_data[course_code] = {
                'course_name': course_name,
                'course_link': course_link,
                'course_description': course_description,
                'course_weight': course_weight,
                'course_fee_index': course_fee_index,
                'course_schedule': course_schedule,
                'course_hrs_for_lecture': course_hrs_for_lecture,
                'course_hrs_for_seminar': course_hrs_for_seminar,
                'course_hrs_for_labtime': course_hrs_for_labtime,
                'course_prerequisites': course_prerequisites
            }

    write_to_file('courses', course_data)
    return course_data


def get_class_schedules(course_data):
    """
    Get the class schedules for a specific course in the different terms.
    Format Eg.:
    "CMPUT 404": {
        "Spring Term 2021": {
            "Lectures": {
                "Lecture A1": {
                    "Code": Int,
                    "Remote": Boolean,
                    "Capacity": Int,
                    "Days": "String",
                    "Start Date": Date,
                    "End Date": Date,
                    "Start Time": DateTime,
                    "End Time": DateTime,
                    "Room Number": String
                },
                "Lecture A2": {
                    ...
                }
            "Labs": {
                "Lab H01": {
                    "Code": Int,
                    "Capacity": Int,
                    "Days": "String",
                    "Start Date": Date,
                    "End Date": Date,
                    "Start Time": DateTime,
                    "End Time": DateTime,
                    "Room Number": String
                },
                "Lab H02": {
                    ...
                }
            },
            "Seminars": {
                "Seminar J1": {
                    "Code": Int,
                    "Capacity": Int,
                    "Days": "String",
                    "Start Date": Date,
                    "End Date": Date,
                    "Start Time": DateTime,
                    "End Time": DateTime,
                    "Room Number": String
                },
                "Seminar J2": {
                    ...
                }
            }

            }
            
        },

        "Winter Term 2022": {
            ...
        }   
    } 
    """
    class_schedules = dict()

    for course_code, values in course_data.items():
        sleep(DELAY_TIME)
        course_url = course_data[course_code]["course_link"]
        course_page = requests.get(course_url).text 
        course_soup = bs(course_page, 'html.parser')
        terms = course_soup.findAll('div', {'class': 'card mt-4 dv-card-flat'})
        print("------------------------------------------------------------------")
        print(f"Currently at {course_url}. ")
        print("------------------------------------------------------------------")
        class_schedules[course_code] = {}

        for term in terms:
            term_code = term.find('div', {'class': 'card-header m-0 px-3 pt-3 pb-2 bg-white d-flex'}).text.strip("\n") # Winter Term 2021, Fall Term 2021, Spring Term 2021, Summer Term 2021
            term_code = term_code.replace(" Term ", "")      # Condensed Name: "Fall Term 2021" --> "Fall2021"

            class_schedules[course_code][term_code] = {}

            class_types = term.findAll(lambda tag: tag.name == 'div' and tag.get('class') == ['col-12'])    # List that has the type of formats the course offers (lectures, labs, seminars)
            
            for class_type in class_types:
                class_type_name = class_type.find('h3', {'class': 'mt-2 d-none d-md-block'}).text      # Lecture, Seminar or Lab
                class_schedules[course_code][term_code][class_type_name] = []
                
                
                offered_classes = class_type.findAll('div', {'class': 'col-lg-4 col-12 pb-3'})

                for classes in offered_classes:
                    class_info = {}

                    class_code_and_name = classes.find('strong', {'class': 'mb-0 mt-4'}).text.strip('\n')
                    class_code = re.search(r"\(([A-Za-z0-9_]+)\)", class_code_and_name).group(1)    # Gets the value inside the paranthesis
                    class_name = class_code_and_name.replace(f'({class_code})', '').strip(' ').strip('\n').strip(' ')

                    ems = classes.findAll('em')
                    try:
                        capacity = ems[0].text.strip("Capacity: ")
                    except:
                        capacity = 'NA'
                    try:
                        date_time_room_data = ems[1].text.strip("\n")
                    except:
                        date_time_room_Data = 'NA'
                    try:
                        start_date, end_date = re.findall(r"(\d+-\d+-\d+)", date_time_room_data)
                    except:
                        start_date, end_date = ['NA', 'NA']
                    try:
                        start_time, end_time = re.findall(r"(\d+:\d+)", date_time_room_data)
                    except:
                        start_time, end_time = ['NA', 'NA']
                    try:
                        room = re.search(r"\((.*?)\)", date_time_room_data).group(1)
                    except:
                        room = 'NA'
                    if len(ems) == 3:   # If Primary Instructor field is provided
                        try:
                            primary_instructor = ems[2].find('a').text
                            primary_instructor_link = ems[2].find('a').get('href')
                        except:
                            primary_instructor = 'NA'
                            primary_instructor_link = 'NA'
                    else:
                        primary_instructor = 'TBD'
                        primary_instructor_link = 'TBD'
                    
                    try:
                        pattern = "\n(.*?)\d+"
                        days = re.search(pattern, date_time_room_data).group(1)
                        days = list(days.strip(" "))
                    except:
                        days = 'NA'


                    class_info["class_code"] = class_code
                    class_info["class_name"] = class_name 
                    class_info["capacity"] = capacity
                    class_info["days"] = days
                    class_info["start_date"] = start_date
                    class_info["end_date"] = end_date
                    class_info["start_time"] = start_time
                    class_info["end_time"] = end_time
                    class_info["room"] = room
                    class_info["primary_instructor"] = primary_instructor
                    class_info["primary_instructor_link"] = primary_instructor_link

                    class_schedules[course_code][term_code][class_type_name].append(class_info)

    write_to_file('class_schedules_5', class_schedules)

def load_from_file(filename):
    """
    Loads data from a JSON file.
    """
    try:
        with open(f'data/{filename}.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {filename}.json not found. Please run the faculty scraper first.")
        return None
    except json.JSONDecodeError:
        print(f"Error: {filename}.json is not valid JSON.")
        return None

def main():
    # print("Scraping Faculties...")
    # faculty_data = get_faculties()

    faculty_data = load_from_file('faculties')
    if not faculty_data:
        return

    print("Scraping Subjects...")
    subject_data = get_subjects(faculty_data)

    # print("Scraping Courses...")
    # course_data = get_courses(subject_data)

    # print("Scraping Class Schedules...")
    # class_schedules = get_class_schedules(course_data)
    # print("Done. Check the data folder for scraped data.")

    # print(end_time - start_time)


if __name__ == "__main__":
    main()