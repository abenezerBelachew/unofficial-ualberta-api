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


## API Reference

#### Get all items

```http
  GET /api/items
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Your API key |

#### Get item

```http
  GET /api/items/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id of item to fetch |


## License
[MIT](https://choosealicense.com/licenses/mit/)
