EC2_CREATE_POST_REQUEST_MODEL = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": 'EC2 create',
    "type": "object",
    "required": ["instanceName"],
    "properties": {
        "instanceName": {
            "type": "string"
        },
        "instanceType": {
            "type": "string"
        },
        "keyPairName": {
            "type": "string"
        },
        "imageId": {
            "type": "string"
        }
    }
}
EC2_START_POST_REQUEST_MODEL = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": 'EC2 start',
    "type": "object",
    "required": ["instanceId"],
    "properties": {
        "instanceId": {
            "type": "string"
        }
    }
}
EC2_STOP_POST_REQUEST_MODEL = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": 'EC2 start',
    "type": "object",
    "required": ["instanceId"],
    "properties": {
        "instanceId": {
            "type": "string"
        }
    }
}
EC2_DELETE_DELETE_REQUEST_MODEL = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": 'EC2 start',
    "type": "object",
    "required": ["instanceId"],
    "properties": {
        "instanceId": {
            "type": "string"
        }
    }
}
