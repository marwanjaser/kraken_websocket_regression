schema_spread = {
    "type": "array",
    "minItems": 4,
    "maxItems": 4,
    "items": [
        {
            "type": "integer"
        },
        {
            "type": "array",
            "maxItems": 5,
            "items": [
                {
                    "type": "string"
                },
                {
                    "type": "string"
                },
                {
                    "type": "string"
                },
                {
                    "type": "string"
                },
                {
                    "type": "string"
                },
            ],

        },
        {
            "type": "string"
        },
        {
            "type": "string"
        }
    ]
}

schema_ticker = {
  "type": "array",
    "minItems": 4,
    "maxItems": 4,
    "items": [
    {
      "type": "integer"
    },
    {
      "type": "object",
      "properties": {
        "a": {
          "type": "array",
          "minItems": 3,
          "maxItems": 3,
          "items": [
            {
              "type": "string"
            },
            {
              "type": "integer"
            },
            {
              "type": "string"
            }
          ]
        },
        "b": {
          "type": "array",
          "minItems": 3,
          "maxItems": 3,
          "items": [
            {
              "type": "string"
            },
            {
              "type": "integer"
            },
            {
              "type": "string"
            }
          ]
        },
        "c": {
          "type": "array",
          "minItems": 2,
          "maxItems": 2,
          "items": [
            {
              "type": "string"
            },
            {
              "type": "string"
            }
          ]
        },
        "h": {
          "type": "array",
          "minItems": 2,
          "maxItems": 2,
          "items": [
            {
              "type": "string"
            },
            {
              "type": "string"
            }
          ]
        },
        "l": {
          "type": "array",
          "minItems": 2,
          "maxItems": 2,
          "items": [
            {
              "type": "string"
            },
            {
              "type": "string"
            }
          ]
        },
        "o": {
          "type": "array",
          "minItems": 2,
          "maxItems": 2,
          "items": [
            {
              "type": "string"
            },
            {
              "type": "string"
            }
          ]
        },
        "p": {
          "type": "array",
          "minItems": 2,
          "maxItems": 2,
          "items": [
            {
              "type": "string"
            },
            {
              "type": "string"
            }
          ]
        },
        "t": {
          "type": "array",
          "minItems": 2,
          "maxItems": 2,
          "items": [
            {
              "type": "integer"
            },
            {
              "type": "integer"
            }
          ]
        },
        "v": {
          "type": "array",
          "minItems": 2,
          "maxItems": 2,
          "items": [
            {
              "type": "string"
            },
            {
              "type": "string"
            }
          ]
        }
      },
      "required": [
        "a",
        "b",
        "c",
        "h",
        "l",
        "o",
        "p",
        "t",
        "v"
      ]
    },
    {
      "type": "string"
    },
    {
      "type": "string"
    }
  ]
}

schema_ohlc = {
  "type": "array",
  "minItems": 4,
  "maxItems": 4,
  "items": [
    {
      "type": "integer"
    },
    {
      "type": "array",
      "minItems": 9,
      "maxItems": 9,
      "items": [
        {
          "type": "string"
        },
        {
          "type": "string"
        },
        {
          "type": "string"
        },
        {
          "type": "string"
        },
        {
          "type": "string"
        },
        {
          "type": "string"
        },
        {
          "type": "string"
        },
        {
          "type": "string"
        },
        {
          "type": "integer"
        }
      ]
    },
    {
      "type": "string"
    },
    {
      "type": "string"
    }
  ]
}

schema_trade = {
        "type": "array",
        "minItems": 4,
        "maxItems": 4,
        "items": [
            {
                "type": "integer"
            },
            {
                "type": "array",
                "items": [
                    {
                        "type": "array",
                        "minItems": 6,
                        "maxItems": 6,
                        "items": [
                            {
                                "type": "string"
                            },
                            {
                                "type": "string"
                            },
                            {
                                "type": "string"
                            },
                            {
                                "type": "string"
                            },
                            {
                                "type": "string"
                            },
                            {
                                "type": "string"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "string"
            },
            {
                "type": "string"
            }
        ]
    }

schema_book = {
  "type": "array",
  "minItems": 4,
  "maxItems": 4,
  "items": [
    {
      "type": "integer"
    },
    {
      "type": "object",
      "properties": {
        "as": {
          "type": "array",
          "items": [
            {
              "type": "array",
              "minItems": 3,
              "maxItems": 3,
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            },
            {
              "type": "array",
                "minItems": 3,
                "maxItems": 3,
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            },
            {
              "type": "array",
              "minItems": 3,
              "maxItems": 3,
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          ]
        },
        "bs": {
          "type": "array",
          "items": [
            {
              "type": "array",
              "minItems": 3,
              "maxItems": 3,
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            },
            {
              "type": "array",
              "minItems": 3,
              "maxItems": 3,
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            },
            {
              "type": "array",
              "minItems": 3,
              "maxItems": 3,
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          ]
        }
      },
      "required": [
        "as",
        "bs"
      ]
    },
    {
      "type": "string"
    },
    {
      "type": "string"
    }
  ]
}

schema_subscription_status = {
  "type": "object",
  "properties": {
    "channelID": {
      "type": "integer"
    },
    "channelName": {
      "type": "string"
    },
    "event": {
      "type": "string"
    },
    "pair": {
      "type": "string"
    },
    "status": {
      "type": "string"
    },
    "subscription": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string"
        }
      },
      "required": [
        "name"
      ]
    }
  },
  "required": [
    "channelID",
    "channelName",
    "event",
    "pair",
    "status",
    "subscription"
  ]
}