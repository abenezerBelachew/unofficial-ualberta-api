import random
import requests
import json
import re
from bs4 import BeautifulSoup as bs
from time import sleep, time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT_URL = "https://apps.ualberta.ca"
MAIN_URL = "https://apps.ualberta.ca/catalogue"
DELAY_TIME = 4

MIN_DELAY = 1 
MAX_DELAY = 3
MAX_RETRIES = 3 # Maximum number of retries for failed requests

WORKERS = 10    # I set the number of parallel threads for each scraper function to 10, increasing beyond 10 had little impact

SESSION = requests.Session()
SESSION.headers.update({'User-Agent': 'Mozilla/5.0'})

def random_delay():
    sleep(random.uniform(MIN_DELAY, MAX_DELAY)) 

def make_request(url):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            random_delay()
            response = SESSION.get(url) # Use the shared session
            response.raise_for_status()
            return response.text
            
        except requests.exceptions.HTTPError as e:
            if hasattr(e.response, 'status_code') and e.response.status_code == 429:
                retry_after = int(e.response.headers.get('Retry-After', 5))
                print(f"Rate limited. Retrying after {retry_after} seconds...")
                sleep(retry_after)
                retries += 1
            else:
                print(f"HTTP error: {e}")
                break
                
        except Exception as e:
            print(f"Error making request: {e}")
            break
            
    return None

def write_to_file(name_of_file, data):
    """
    Writes scraped data a json file.
    """
    with open(f'data/{name_of_file}.json', 'w') as file:
        json.dump(data, file, indent=4)

def get_faculties():
    """
    Gets each faculty with the following format:
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
            print(f"Found faculty: {faculty_title}")   # Debugging print statement
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
    Gets the subjects from each faculty with parallel threads with the following format:
    "AUACC": {
        "name": "Augustana Faculty - Accounting",
        "link": "https://apps.ualberta.ca/catalogue/course/auacc",
        "faculties": [
            "AU"
        ]
    }
    """
    subject_data = {}
    
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {
            executor.submit(process_faculty_for_subjects, faculty_code, faculty_info): faculty_code
            for faculty_code, faculty_info in faculty_data.items()
        }
        
        for future in as_completed(futures):
            faculty_subjects = future.result()
            for subject_code, subject_name, subject_url in faculty_subjects:
                if subject_code not in subject_data:
                    subject_data[subject_code] = {
                        "name": subject_name,
                        "link": subject_url,
                        "faculties": []
                    }
                # Make sure each faculty is only added once
                faculty_code = futures[future]
                if faculty_code not in subject_data[subject_code]["faculties"]:
                    subject_data[subject_code]["faculties"].append(faculty_code)

    write_to_file('subjects', subject_data)
    return subject_data

def process_faculty_for_subjects(faculty_code, faculty_info):
    """Processes a single faculty to extract its subjects"""
    start_time = time()
    faculty_link = faculty_info["faculty_link"]
    faculty_subjects = []
    
    try:
        html = make_request(faculty_link)
        if not html:
            return faculty_subjects
            
        subject_soup = bs(html, 'html.parser')
        subject_container = subject_soup.select_one('div.content > div.container > ul')
        
        if not subject_container:
            print(f"Warning: No subjects found for faculty {faculty_code}")
            return faculty_subjects

        for subject in subject_container.find_all('li'):
            subject_link = subject.find('a')
            if not subject_link:
                continue
            
            subject_title = subject_link.text.strip()
            subject_url = ROOT_URL + subject_link.get('href')
            
            if ' - ' in subject_title:
                subject_code, subject_name = subject_title.split(' - ', 1)
                faculty_subjects.append((subject_code, subject_name, subject_url))
    
    except Exception as e:
        print(f"Error processing faculty {faculty_code}: {str(e)}")
    
    duration = time() - start_time
    print(f"Scraped faculty {faculty_code} in {duration:.2f}s")
    return faculty_subjects

def get_courses(subject_data):
    """
    Gets the courses from each subject with parallel threads with the following format:
    "CMPUT301": {
        "course_name": "Introduction to Software Engineering",
        "course_link": "https://apps.ualberta.ca/catalogue/course/cmput/301",
        "course_description": "Object-oriented design and analysis, with interactive applications as the primary example. Topics include: software process; revision control; Unified Modeling Language (UML); requirements; software architecture, design patterns, frameworks, design guidelines; unit testing; refactoring; software tools.",
        "course_units": "3",
        "course_fee_index": "6",
        "course_schedule": "EITHER",
        "course_hrs_for_lecture": "3",
        "course_hrs_for_seminar": "0",
        "course_hrs_for_labtime": "3",
        "course_prerequisites": "Prerequisite: CMPUT 201 or 275. This course may not be taken for credit if credit has been obtained in MIS 419 or BTM 419.",
        "subject_code": "CMPUT"
    }
    """
    course_data = {}
    
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {
            executor.submit(process_subjects_for_courses, subject_code, subject_info): subject_code
            for subject_code, subject_info in subject_data.items()
        }
        
        for future in as_completed(futures):
            subject_courses = future.result()
            for course in subject_courses:
                course_code = course['course_code']
                course_data[course_code] = {
                    'course_name': course['course_name'],
                    'course_link': course['course_link'],
                    'course_description': course['course_description'],
                    'course_units': course['course_units'],
                    'course_fee_index': course['course_fee_index'],
                    'course_schedule': course['course_schedule'],
                    'course_hrs_for_lecture': course['course_hrs_for_lecture'],
                    'course_hrs_for_seminar': course['course_hrs_for_seminar'],
                    'course_hrs_for_labtime': course['course_hrs_for_labtime'],
                    'course_prerequisites': course['course_prerequisites'],
                    'subject_code': course['subject_code']
                }

    write_to_file('courses', course_data)
    return course_data

def process_subjects_for_courses(subject_code, subject_info):
    """Processes a single subject to extract its courses"""
    start_time = time()
    subject_url = subject_info["link"]
    subject_courses = []
    
    try:
        html = make_request(subject_url)
        if not html:
            return subject_courses
            
        course_soup = bs(html, 'html.parser')
        course_containers = course_soup.select('div.container > div.mb-3.pb-3.border-bottom')
        
        if not course_containers:
            print(f"Warning: No courses found for subject {subject_code}")
            return subject_courses

        for course in course_containers:
            course_units = None
            course_weight = None
            course_fee_index = None
            course_schedule = None
            course_hrs_for_lecture = None
            course_hrs_for_seminar = None
            course_hrs_for_labtime = None
            course_prerequisites = None
            
            course_link_tag = course.find('a', href=True)
            if not course_link_tag:
                continue
            
            course_title = course_link_tag.text.strip()
            if ' - ' not in course_title:
                continue
                
            course_code, course_name = course_title.split(' - ', 1)
            course_link = ROOT_URL + course_link_tag['href']
            
            weight_tag = course.find('b')
            description_tag = course.find('p')
            
            course_description = description_tag.text.strip() if description_tag else "No description available."
            
            if weight_tag:
                weight_text = weight_tag.text.strip()
                if 'units' in weight_text:
                    course_units = weight_text.split('units')[0].strip()
                
                # Extract fee index (e.g., "6" from "fi 6")
                if 'fi' in weight_text:
                    try:
                        course_fee_index = weight_text.split('fi')[1].split(')')[0].strip()
                    except:
                        pass
                
                # Extract schedule components
                if '(' in weight_text:
                    try:
                        schedule_part = weight_text.split('(')[-1].strip(')')
                        if ',' in schedule_part:
                            course_schedule = schedule_part.split(',')[0].strip()
                            hours_part = schedule_part.split(',')[1].strip()
                            if '-' in hours_part:
                                hours = hours_part.split('-')
                                course_hrs_for_lecture = hours[0].strip(' )')
                                course_hrs_for_seminar = hours[1]
                                course_hrs_for_labtime = hours[2].strip(')')
                    except:
                        pass
            
            # Extract prerequisites if they exist while still keeping the "Prerequisite" text
            # Every saved prereq field should look like:
            # Prerequisite: CMPUT 101
            # Prerequisites: CMPUT 101, CMPUT 201
            if description_tag:
                course_description = description_tag.text.strip()
                if 'Prerequisite:' in course_description:
                    parts = course_description.split('Prerequisite:', 1)
                    course_description = parts[0].strip()
                    course_prerequisites = 'Prerequisite: ' + parts[1].strip()
                elif 'Prerequisites:' in course_description:
                    parts = course_description.split('Prerequisites:', 1)
                    course_description = parts[0].strip()
                    course_prerequisites = 'Prerequisites: ' + parts[1].strip()
                elif 'Prerequisite' in course_description:
                    # In the case of no colon but with a space
                    parts = course_description.split('Prerequisite', 1)
                    course_description = parts[0].strip()
                    course_prerequisites = 'Prerequisite: ' + parts[1].strip()  # Adjusted to fit format
                elif 'Prerequisites' in course_description:
                    # In the case of no colon but with a space
                    parts = course_description.split('Prerequisites', 1)
                    course_description = parts[0].strip()
                    course_prerequisites = 'Prerequisites: ' + parts[1].strip()  # Adjusted to fit format
            
            # Remove the space in the course code (CMPUT 101 -> CMPUT101)
            formatted_course_code = course_code.replace(" ", "")
            
            subject_courses.append({
                'course_code': formatted_course_code,
                'course_name': course_name,
                'course_link': course_link,
                'course_description': course_description,
                'course_units': course_units,
                'course_weight': course_weight,
                'course_fee_index': course_fee_index,
                'course_schedule': course_schedule,
                'course_hrs_for_lecture': course_hrs_for_lecture,
                'course_hrs_for_seminar': course_hrs_for_seminar,
                'course_hrs_for_labtime': course_hrs_for_labtime,
                'course_prerequisites': course_prerequisites,
                'subject_code': subject_code
            })
            
    except Exception as e:
        print(f"Error processing subject {subject_code}: {str(e)}")
        import traceback
        traceback.print_exc()
    
    duration = time() - start_time
    print(f"Scraped subject {subject_code} in {duration:.2f}s")
    return subject_courses

def get_class_schedules(course_data):
    """
    Gets the class schedules from each course with parallel threads with the following format:
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
            
        } 
    } 
    """     
    class_schedules = {}
    
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {
            executor.submit(process_courses_for_class_schedules, course_code, values['course_link']): course_code
            for course_code, values in course_data.items()
        }
        
        for future in as_completed(futures):
            course_code = futures[future]
            try:
                result = future.result()
                if result:  # Ignore unsuccessful scrapes
                    class_schedules[course_code] = result
            except Exception as e:
                print(f"Error processing {course_code}: {str(e)}")
                class_schedules[course_code] = "error"
    
    write_to_file('class_schedules', class_schedules)
    return class_schedules

def process_courses_for_class_schedules(course_code, course_url):
    """Processes a single course's schedule data"""
    start_time = time()
    try:
        course_page = make_request(course_url)
        if not course_page:
            return None
            
        course_soup = bs(course_page, 'html.parser')
        
        # Check if not offered
        warning = course_soup.find('div', class_='alert alert-warning')
        if warning and "no scheduled offerings" in warning.text.lower():
            duration = time() - start_time
            print(f"Scraped {course_code} (not offered) in {duration:.2f}s")
            return "not offered"
        
        course_data = {}
        term_sections = course_soup.select('div.container > div.mb-5')
        
        if not term_sections:
            print(f"Warning: No term sections found for {course_code}")
            return None

        for term in term_sections:
            term_name = term.find('h2').text.strip()
            term_key = term_name.replace(" Term ", "")
            course_data[term_key] = {}

            for heading in term.find_all('h3'):
                class_type = heading.text.strip().capitalize()
                course_data[term_key][class_type] = []
                table = heading.find_next('table')
                
                if not table:
                    continue

                for row in table.select('tbody > tr'):
                    class_info = {}
                    
                    # Section and Code
                    section_cell = row.find('td', {'data-card-title': 'Section'})
                    if section_cell:
                        section_text = section_cell.text.strip()
                        class_info["section"] = section_text.split('(')[0].strip()
                        class_info["code"] = section_text.split('(')[1].strip(')')

                    # Capacity
                    capacity_cell = row.find('td', {'data-card-title': 'Capacity'})
                    if capacity_cell:
                        class_info["capacity"] = capacity_cell.text.strip()

                    # Class Times
                    times_cell = row.find('td', {'data-card-title': 'Class times'})
                    if times_cell:
                        day_time_pairs = []
                        current_days = None
                        
                        for time_part in times_cell.select('.col'):
                            if time_part.find('span', class_='fa-calendar'):
                                date_text = time_part.text.strip()
                                days_match = re.search(r"\(([A-Za-z]+)\)", date_text)
                                if days_match:
                                    current_days = days_match.group(1)
                            
                            elif time_part.find('span', class_='fa-clock') and current_days:
                                time_text = time_part.text.strip()
                                times = re.findall(r"\d{2}:\d{2}", time_text)
                                if len(times) == 2:
                                    day_time_pairs.append({
                                        "days": current_days,
                                        "start_time": times[0],
                                        "end_time": times[1]
                                    })
                                current_days = None

                        if day_time_pairs:
                            class_info["day_time_pairs"] = day_time_pairs

                    course_data[term_key][class_type].append(class_info)

        duration = time() - start_time
        print(f"Scraped {course_code} in {duration:.2f}s")
        return course_data

    except Exception as e:
        print(f"Error in {course_code}: {str(e)}")
        raise

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
    '''
    Uncomment any of the blocks below to update a specific json data file (faculties, subjects, courses, class_schedules)
    '''

    # print("Scraping Faculties...")
    # faculty_data = get_faculties()

    # faculty_data = load_from_file('faculties')
    # if not faculty_data:
    #     return
    # print("Scraping Subjects...")
    # subject_data = get_subjects(faculty_data)

    # subject_data = load_from_file('subjects')
    # if not subject_data:
    #     return
    # print("Scraping Courses...")
    # course_data = get_courses(subject_data)

    # course_data = load_from_file('courses')
    # if not course_data:
    #     return
    # print("Scraping Class Schedules...")
    # class_schedules = get_class_schedules(course_data)

if __name__ == "__main__":
    main()