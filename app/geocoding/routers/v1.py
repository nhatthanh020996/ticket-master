import uuid

from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse

import elasticsearch

from ...generics import async_es

geocoding_v1 = APIRouter(prefix='/geocoding')


@geocoding_v1.get('/search', status_code=status.HTTP_200_OK)
async def search(query: str, limit: int):
    search_query = {
        "query": {
            "multi_match": {
                "query": query,
                "type": "bool_prefix",
                "fields": [
                    "autocompletion",
                    "autocompletion._2gram",
                    "autocompletion._3gram"
                ]
            }
        },
        "_source": ['id', 'location'],
        "size": limit
    }
    result = await async_es.search(index='locations', body=search_query)
    resp_body = [{'id': hit['_id'], **hit['_source']} for hit in result['hits']['hits']]
    return JSONResponse(content=resp_body) 


@geocoding_v1.get('/reverse', status_code=status.HTTP_200_OK)
async def to_latlon(lat: float, lon: float):
    search_query = {
        "query": {
            "bool": {
                "filter": {
                    "geo_distance": {
                        "distance": "10m",
                        "coordinate": {
                            "lat": lat,
                            "lon": lon
                        }
                    }
                }
            }
        },
        "size": 1
    }
    result = await async_es.search(index='locations', body=search_query)
    resp_body = [{'id': hit['_id'], **hit['_source']} for hit in result['hits']['hits']]
    return JSONResponse(content=resp_body)


@geocoding_v1.get('/{location_id}', status_code=status.HTTP_200_OK)
async def get_by_id(location_id: uuid.UUID):
    try:
        result = await async_es.get(index='locations', id=str(location_id))
    except elasticsearch.NotFoundError:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return JSONResponse(content={'id': result['_id'], **result['_source']})


