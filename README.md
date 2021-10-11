# Unofficial University of Alberta API

### This is just a fun personal project I made to test FastAPI. It's not affiliated with the University of Alberta.

<p>
Inspired by UWaterloo's API (https://openapi.data.uwaterloo.ca/api-docs/index.html), I made a somewhat similar API for U of Alberta. I couldn't get as many endpoints as  UWaterloo's because I don't have access to UAlberta's databases so I've scraped what was available online. 
</p>
<p>
I've tried to balance the over-fetching and under-fetching of data by allowing user to query based on different variables in their endpoints. To keep it simple, I have used JSON. Getting what you need from the scraped data should be as simple as calling keys from a dictionary.
</p>
<p>
There were over 10k pages to scrap so if you're going to run scraper.py it's going to take a while if DELAY_TIME is not changed. I suggest not to change it to avoid hitting U of A's servers too much.
</p>

## Data
- 20 Faculties
- 315 Subjects
- 10114 Courses

## Screenshots
![App Screenshot](https://www.abenezerbelachew.com/images/projects/ualbertaapi.gif)

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


### Get lab class schedule for a course in a specific term 

```http
  GET /class_schedules/seminars/{course_code}/{term_code}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| - | - | Gets the seminar section of a specific course in a specific term|
| `course_code`      | `string` | The Course Code (E.g. CMPUT204 for Algorithms I) |
| `term_code`      | `string` | The Term Code (E.g. Fall2021 for Fall 2021) |






## License
[MIT](https://choosealicense.com/licenses/mit/)
