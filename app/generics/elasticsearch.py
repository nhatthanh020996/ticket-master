from .settings import settings

from elasticsearch import AsyncElasticsearch


async_es = AsyncElasticsearch(hosts=[f"http://{settings.ES_HOST}:{settings.ES_PORT}"], basic_auth=(settings.ES_USERNAME, settings.ES_PASSWORD))