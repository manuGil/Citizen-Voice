# APIs

The Citizen Voice system provides two REST Application Programming Interfaces. 

## Voice API

The Voice API provides functionality to create suveys and retrieve questions. This the API used by the **Citizen Mapping** application.
Depending on how are you running the Djago API App, the root URL of this API is either `http://localhost/voice/v3/` or `http://localhost:8000/voice/v3/`. The following API endpoins are available.

```json
{
    "answers":"http://localhost/voice/v3/answers/",
    "questions":"http://localhost/voice/v3/questions/",
    "surveys":"http://localhost/voice/v3/surveys/",
    "responses":"http://localhost/voice/v3/responses/",
    "users":"http://localhost/voice/v3/users/",
    "locations":"http://localhost/voice/v3/locations/",
    "polygonfeatures":"http://localhost/voice/v3/polygonfeatures/",
    "linefeatures":"http://localhost/voice/v3/linefeatures/",
    "map-views":"http://localhost/voice/v3/map-views/",
    "pointfeatures":"http://localhost/voice/v3/pointfeatures/",
    "topics":"http://localhost/civilian/v1/topics/"
}
```


## CIVILIAN API

The CIVILIAN API provides functionatlity to retrieve answers related to geospatial questions. Those are questions that include map-views. This is the API used by the **Community Dashboard**.
Depending on how are you running the Djago API App, the root URL of this API is either `http://localhost/civilian/v1/` or `http://localhost:8000/civilian/v1/`. The following API endpoins are available.


```json
{
    "answers":"http://localhost/civilian/v1/answers/",
    "topics":"http://localhost/civilian/v1/topics/"
}
```

```{tip}
Visit our [API Documentation Page](https://citizenvoice.tudelft.nl/voice/v3/schema/redoc/) for a complete description of the endpoints and their capabilities.
```
