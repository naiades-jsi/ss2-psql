import json

alert_template = {
    "@context": [
        "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
    ],
    "dateIssued": {
        "type": "Property",
        "value": {
            "@type": "DateTime",
            "@value": "2022-09-09T05:49:44.7036Z"
        }
    },
    "description": {
        "type": "Property",
        "value": "Title: New data for model."
    },
    "ksiSignature": {
        "type": "Property",
        "value": "fail"
    },
    "type": "Alert",
    "updatedAttributes": {
        "type": "Property",
        "value": "dateIssued,description,ksiSignature,updatedAttributes"
    }
}

alert_template_old = {
    "alertSource":{
        "type": "Text",
        # Value will be added (State analysis tool)
    },
    "category": {
        "type": "Text",
        "value": "anomaly"
    },
    "dateIssued": {
        "type": "DateTime",
        # eg. "value": "2017-01-02T09:25:55.00Z"
    },
    "description": {
        "type": "Text",
        "value": "Final leakage position detected" # title + Content
    },
    "location": {
        "type": "geo:json",
        "value": {
            "type": "Point",
            "coordinates": [ # to be inserted
            ]
        }
    },
    "subCategory": {
        "type": "Text",
        "value": "longTerm"
    },
    "type": "Alert",
    # Attributes that get updated
    "updatedAttributes": {
        "type": "Text",
        "value": "dateIssued,description,ksiSignature"
    }
}
