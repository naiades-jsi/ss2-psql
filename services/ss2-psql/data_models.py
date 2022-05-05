import json

alert_template = {
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