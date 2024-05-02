from elasticsearch import Elasticsearch

es = Elasticsearch(hosts=["http://localhost:39200"], basic_auth=('elastic', 'pg1Qwv&HBE+Ey+e?'))

index_name = "business"

business_mapping = {
    "mappings": {
        "dynamic_templates": [
            {
                "no_accent_index": {
                    "match": "no_accent",
                    "mapping": {
                        "type": "text",
                        "index": True
                    }
                }
            },
            {
                "other_fields": {
                    "match": "*",
                    "mapping": {
                        "type": "keyword",
                        "index": False
                    }
                }
            }
        ],
        "properties": {
            "category": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "text"},
                }
            },
            "repr_label": {
                "type": "object"
            }
        }
    }
}


address_mapping = {
    "mappings": {
        "dynamic_templates": [
            {
                "no_accent_index": {
                    "match": "no_accent",
                    "mapping": {
                        "type": "text",
                        "index": True
                    }
                }
            },
            {
                "other_fields": {
                    "match": "*",
                    "mapping": {
                        "type": "keyword",
                        "index": False
                    }
                }
            }
        ],
        "properties": {
            "repr_label": {
                "type": "object"
            }
        }
    }
}

if not es.indices.exists(index='address'):
    es.indices.create(index='address', body=address_mapping)

if not es.indices.exists(index='business'):
    es.indices.create(index='business', body=business_mapping)

# es.indices.delete(index='address')
# es.indices.delete(index='business')

indices = es.indices.get_mapping(index="*")
print(indices)