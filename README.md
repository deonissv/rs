# Recommender system to recommend track for group of users

## SETUP

> Generate .pkl objects first

```
cd microservice
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8080
```

OR

```
cd microservice
docker build . -t recommender
docker run -p 8080:8080 recommender
```

## USAGE

#### ABTest endpoint

```
  curl -X 'POST' \
    'http://localhost:8080/predict/abtest' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '[
    346,123,876
  ]'
```

#### Models endpoint

```
  curl -X 'POST' \
    'http://localhost:8080/predict/top_all_model' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '[
    645, 345, 1234
  ]'
```


#### Update endpoint

```
  curl -X 'POST' \
    'http://localhost:8080/update' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '[
    {
      "session_id": 0,
      "duration": 0,
      "user_id": 0,
      "track_id": "HasdZcx",
      "like": 1,
      "skip": 3,
      "play": 5
    },
    {
      "session_id": 0,
      "duration": 0,
      "user_id": 0,
      "track_id": "ZXCoknsdf",
      "like": 4,
      "skip": 3,
      "play": 20
    }
  ]'
```