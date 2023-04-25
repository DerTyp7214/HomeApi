# HomeApi

## Main: /

The config should be persistent, so you only need to set it once.
To use see devices from other apis, you need to set the config for them too.

### /lights

normalized response with all lights

array of [lights](#lightsid)

### /lights/:id

normalized response for one light

```json
{
  "id": "string", // required
  "name": "string", // required
  "on": "boolean", // required
  "brightness": "float: 0-1",
  "color": {
    "hue": "float: 0-360",
    "saturation": "float: 0-100"
  },
  "reachable": "boolean", // required
  "type": "string", // required
  "model": "string",
  "manufacturer": "string",
  "uniqueid": "string", // required
  "swversion": "string",
  "productid": "string"
}
```

### /lights/:id/state {PUT}

accepts the json body

```json
{
  "on": "boolean",
  "brightness": "float: 0-1",
  "color": {
    "hue": "float: 0-360",
    "saturation": "float: 0-100"
  }
}
```

returns 200 if successfull, otherwise the error json

### /plugs

normalized response with all plugs

array of [plugs](#plugsid)

### /plugs/:id

normalized response for one plug

```json
{
  "id": "string", // required
  "name": "string", // required
  "on": "boolean", // required
  "reachable": "boolean", // required
  "type": "string", // required
  "model": "string",
  "manufacturer": "string",
  "uniqueid": "string", // required
  "swversion": "string",
  "productid": "string"
}
```

### /plugs/:id/state {PUT}

accepts the json body

```json
{
  "on": "boolean"
}
```

returns 200 if successfull, otherwise the error json

---

## Hue: /hue

- Set the ip of the hue bridge using the config endpoint
- Init the api using the init endpoint
- Use the api as normal

### /hue/config {POST}

Set the config (needed for host the first time starting the api)

body: `{"host":"ip"}`

### /hue/init {GET}

Sets up a new user

error if the button is not pressed: `Link button not pressed`

if the button is pressed: `{"username": "<username>"}`

### /hue/lights {GET}

same response as original hue api

### /hue/lights/:id {GET}

same response as original hue api

### /hue/lights/:id/state {PUT}

accepts the same body as the original hue api

returns 200 if successfull, otherwise the error json

### /hue/plugs {GET}

same response as original hue api (only the plugs)

### /hue/plugs/:id {GET}

same response as original hue api (only the plugs)

### /hue/plugs/:id/state {PUT}

accepts the same body as the original hue api

returns 200 if successfull, otherwise the error json
