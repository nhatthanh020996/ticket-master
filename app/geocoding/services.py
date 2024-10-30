import uuid
import abc
from typing import Annotated

from fastapi import Depends

from ..generics import async_es, settings
import elasticsearch


class IGeocodingThirdParty(abc.ABC):
    @abc.abstractmethod
    async def search_by_coordinate(self, lat: float, lon: float) -> dict:
        raise NotImplementedError()


class IGeocodingService(abc.ABC):
    @abc.abstractmethod
    async def search_by_coordinate(self, lat: float, lon: float) -> dict:
        raise NotImplementedError()
    
    @abc.abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> dict:
        raise NotImplementedError()
    
    async def insert(self, data: dict):
        raise NotImplementedError()

    @abc.abstractmethod
    async def retrieve_from_third_party(self, lat: float, lon: float) -> dict:
        raise NotImplementedError()
    
    @abc.abstractmethod
    async def auto_complete(self, query: str, limit: int) -> dict:
        raise NotImplementedError()
    

class PostgisGecodingService(IGeocodingService):
    def __init__(self, third_party_svc: IGeocodingThirdParty) -> None:
        self.third_party_svc = third_party_svc

    async def search_by_coordinate(self, lat: float, lon: float) -> dict:
        pass

    async def get_by_id(self, id: uuid.UUID) -> dict:
        pass

    async def insert(self, id: uuid.UUID, data: dict) -> uuid.UUID:
        pass

    async def retrieve_from_third_party(self, lat: float, lon: float) -> dict:
        pass

    async def auto_complete(self, query: str, limit: int = 10) -> dict:
        pass


class ElasticGeocodingService(IGeocodingService):
    def __init__(self, third_party_svc: IGeocodingThirdParty) -> None:
        self.third_party_svc = third_party_svc

    async def search_by_coordinate(self, lat: float, lon: float) -> dict:
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
        if len(result['hits']['hits']) > 0:
            return [{'id': hit['_id'], **hit['_source']} for hit in result['hits']['hits']]
        return await self.retrieve_from_third_party(lat, lon)

    async def get_by_id(self, id: uuid.UUID) -> dict:
        try:
            result = await async_es.get(index='locations', id=str(id))
        except elasticsearch.NotFoundError as e:
            raise e
        return {'id': result['_id'], **result['_source']}
    
    async def insert(self, id: uuid.UUID, data: dict) -> uuid.UUID:
        await async_es.create(index='locations', id=str(id), document=data)

    async def retrieve_from_third_party(self, lat: float, lon: float) -> dict:
        data = await self.third_party_svc.search_by_coordinate(lat, lon)
        id = uuid.uuid4() 
        await self.insert(id, data)
        return self.get_by_id(id)
    
    async def auto_complete(self, query: str, limit: int = 10) -> dict:
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
        return [{'id': hit['_id'], **hit['_source']} for hit in result['hits']['hits']]
    

class GoogleAPIIGeocodingThirdParty(IGeocodingThirdParty):
    async def search_by_coordinate(self, lat: float, lon: float) -> dict:
        raise NotImplementedError()


class NominatimGeocodingThirdParty(IGeocodingThirdParty):
    async def search_by_coordinate(self, lat: float, lon: float) -> dict:
        raise NotImplementedError()


def geocoding_service_factory() -> IGeocodingService:
    if settings.GEOCODING_THIRD_PARTY == 'google':
        geocoding_thirdparty_svc = GoogleAPIIGeocodingThirdParty()
    elif settings.GEOCODING_THIRD_PARTY == 'nominatim':
        geocoding_thirdparty_svc = NominatimGeocodingThirdParty()
    else:
        geocoding_thirdparty_svc = NominatimGeocodingThirdParty()

    if settings.GEOCODING_ENGINE == 'postgis':
        return PostgisGecodingService(geocoding_thirdparty_svc)
    elif settings.GEOCODING_ENGINE == 'elastic':
        return ElasticGeocodingService(geocoding_thirdparty_svc)
    else:
        return ElasticGeocodingService(geocoding_thirdparty_svc)


GeocodingService = Annotated[IGeocodingService, Depends(geocoding_service_factory)]