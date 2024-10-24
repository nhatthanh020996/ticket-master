curl --location --request PUT 'http://localhost:39200/locations' \
--header 'Authorization: Basic ZWxhc3RpYzpwZzFRd3YmSEJFK0V5K2U/' \
--header 'Content-Type: application/json' \
--data '{
    "mappings": {
        "dynamic_templates": [
            {
                "location_template": {
                    "match": "location",
                    "mapping": {
                        "type": "text",
                        "index": true
                    }
                }
            },
            {
                "autocompletion_template": {
                    "match": "autocompletion",
                    "mapping": {
                        "type": "search_as_you_type"
                    }
                }
            },
            {
                "other_fields_template": {
                    "match": "*",
                    "mapping": {
                        "type": "keyword",
                        "index": false
                    }
                }
            }
        ],
        "properties": {
            "sli": {
                "type": "object"
            },
            "coordinate": {
                "type": "geo_point"
            }
        }
    }
}'