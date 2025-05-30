# Unofficial University of Alberta API

### This project provides an unofficial API for accessing the University of Alberta faculty, subject, course, and class schedules from its official course catalogue through web scraping. Originally built by [@abenezerBelachew](https://github.com/abenezerBelachew), this fork allows the scraper to function with the updated HTML layout of the course catalogue website, and significantly updates the project by upgrading dependencies to current versions, optimizing scraping with parallel threads, and replacing outdated data with a new, reformatted dataset.

## What's New in This Fork

- ✅ Updated all Python dependencies to latest secure/compatible versions.
- ⚡ Significantly improved scraping speed via multithreading (parallel requests).
- 🧹 Cleaned and reformatted data collection.
- 📦 Replaced outdated scraped data with newly refreshed data for faculties, subjects, and courses.
- 🛠 Fixed scraper to work with the current version of the University of ALberta course catalogue HTML layout.

## Data
- 20 Faculties
- 327 Subjects
- 10014 Courses

## Screenshots
![App Screenshot](https://www.abenezerbelachew.com/static/images/projects/ualbertaapi.gif)

## Installation 

Install locally

```bash 
  git clone https://github.com/abenezerBelachew/unofficial-ualberta-api.git
  cd unofficial-ualberta-api
  pipenv install -r requirements.txt
  pipenv shell

  python3 scraper.py # Not necessary if you want to use the already scraped data in the data folder.
  uvicorn main:app --reload or python main.py
```
Go to http://127.0.0.1:8000 [or whichever port Uvicorn says it is running on].

# API Reference

## Faculties
### Get Faculties

```http
  GET /faculties
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `No Parameters` | `-` | Returns all faculties with necessary data |

### Get specific faculty

```http
  GET /faculties/{faculty_code}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `faculty_code`      | `string` | The Faculty Code (E.g. RM for Faculty of Rehabilitation Medicine) |

<!-- ----------------------------------------------------------- -->

## Subjects
### Get Subjects

```http
  GET /subjects
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `No Parameters` | `-` | Returns all subjects with necessary data |

### Get specific faculty

```http
  GET /subjects/{subject_code}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `subject_code`      | `string` | The Subject Code (E.g. BIOEN for Bioresource Engineering) |

<!-- ----------------------------------------------------------- -->

## Courses
### Get Courses

```http
  GET /courses
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `No Parameters` | `-` | Returns all courses with necessary data |

### Get specific faculty

```http
  GET /courses/{course_code}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `course_code`      | `string` | The Course Code (E.g. CHEM102 for Introductory University Chemistry II) |

<!-- ----------------------------------------------------------- -->

## Class Schedules
### Get all class schedules

```http
  GET /class_schedules
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `No Parameters` | `-` | Returns all class schedules with necessary data |

### Get specific class schedule for a course

```http
  GET /class_schedules/{course_code}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `course_code`      | `string` | The Course Code (E.g. MATH322 for Graph Theory) |

### Get specific class schedule for a course in a specific term

```http
  GET /class_schedules/{course_code}/{term_code}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `course_code`      | `string` | The Course Code (E.g. MATH322 for Graph Theory) |
| `term_code`      | `string` | The Term Code (E.g. Fall2021 for Fall 2021) |

### Get lecture class schedule for a course in a specific term 

```http
  GET /class_schedules/lectures/{course_code}/{term_code}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| - | - | Gets the lecture section of a specific course in a specific term|
| `course_code`      | `string` | The Course Code (E.g. MATH322 for Graph Theory) |
| `term_code`      | `string` | The Term Code (E.g. Fall2021 for Fall 2021) |

### Get lab class schedule for a course in a specific term 

```http
  GET /class_schedules/labs/{course_code}/{term_code}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| - | - | Gets the lab section of a specific course in a specific term|
| `course_code`      | `string` | The Course Code (E.g. CMPUT404 for Web Applications and Architecture) |
| `term_code`      | `string` | The Term Code (E.g. Fall2021 for Fall 2021) |

### Get seminar class schedule for a course in a specific term 

```http
  GET /class_schedules/seminars/{course_code}/{term_code}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| - | - | Gets the seminar section of a specific course in a specific term|
| `course_code`      | `string` | The Course Code (E.g. CMPUT204 for Algorithms I) |
| `term_code`      | `string` | The Term Code (E.g. Fall2021 for Fall 2021) |

## Acknowledgments

- Original project by [@abenezerBelachew](https://github.com/abenezerBelachew)
- Fork updated and maintained by [@mahughes23](https://github.com/mahughes23)

## License
[MIT](https://choosealicense.com/licenses/mit/)
