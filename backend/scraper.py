import requests
import json
import re
from bs4 import BeautifulSoup as bs
from time import sleep, time
from concurrent.futures import ThreadPoolExecutor, as_completed


ROOT_URL = "https://apps.ualberta.ca"
MAIN_URL = "https://apps.ualberta.ca/catalogue"
DELAY_TIME = 4

# ==================================================
import random

MIN_DELAY = 1 
MAX_DELAY = 3
MAX_RETRIES = 3 # Maximum number of retries for failed requests

def random_delay():
    sleep(random.uniform(MIN_DELAY, MAX_DELAY))

def make_request(url):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            random_delay()  # Add a random delay before each request
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            return response.text
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:  # Too Many Requests
                retry_after = int(response.headers.get('Retry-After', 5))   # Default to 5 seconds if header is missing
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
# ============================================================


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

        try:
            subject_page = requests.get(subject_url, headers={'User-Agent': 'Mozilla/5.0'}).text
            course_soup = bs(subject_page, 'html.parser')

            course_containers = course_soup.select('div.container > div.mb-3.pb-3.border-bottom')
            if not course_containers:
                print(f"Warning: No courses found for subject {subject_code}")
                continue

            # Get course details
            for course in course_containers:
                course_link_tag = course.find('a', href=True)
                if not course_link_tag:
                    continue

                course_title = course_link_tag.text.strip()
                if ' - ' not in course_title:
                    print(f"Warning: Unexpected course title format: {course_title}")
                    continue

                course_code, course_name = course_title.split(' - ', 1)
                course_link = ROOT_URL + course_link_tag['href']

                # Get course weight and description
                weight_tag = course.find('b')
                description_tag = course.find('p')

                course_weight = weight_tag.text.strip() if weight_tag else None
                course_description = description_tag.text.strip() if description_tag else "No description available."

                # Get extra details (if possible)
                try:
                    # Ex: "3 units (fi 6)(EITHER, 3-0-3)"
                    weight_parts = weight_tag.text.split()
                    course_units = weight_parts[0] if weight_parts else None
                    course_fee_index = weight_parts[2].strip('()') if len(weight_parts) > 2 else None
                    course_schedule = weight_parts[3].strip('()') if len(weight_parts) > 3 else None
                except Exception as e:
                    print(f"Error parsing course weight for {course_code}: {str(e)}")
                    course_units = course_fee_index = course_schedule = None

                course_data[course_code] = {
                    'course_name': course_name,
                    'course_link': course_link,
                    'course_description': course_description,
                    'course_weight': course_weight,
                    'course_units': course_units,
                    'course_fee_index': course_fee_index,
                    'course_schedule': course_schedule,
                    'subject_code': subject_code
                }

        except Exception as e:
            print(f"Error processing subject {subject_code}: {str(e)}")
            continue

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
    class_schedules = {}
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(process_course, course_code, values['course_link']): course_code
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

def process_course(course_code, course_url):
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
    # print("Scraping Faculties...")
    # faculty_data = get_faculties()

    # print("Scraping Subjects...")
    # subject_data = get_subjects(faculty_data)

    # print("Scraping Courses...")
    # course_data = get_courses(subject_data)

    course_data = load_from_file('courses')
    if not course_data:
        return

    print("Scraping Class Schedules...")
    class_schedules = get_class_schedules(course_data)
    print("Done. Check the data folder for scraped data.")


if __name__ == "__main__":
    main()