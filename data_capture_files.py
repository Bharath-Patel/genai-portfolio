import json, base64

with open("capture.jsonl") as f:
    for i, line in enumerate(f):
        rec = json.loads(line)
        inp = rec["captureData"]["endpointInput"]
        data = inp["data"]
        if inp["encoding"] == "BASE64":
            data = base64.b64decode(data).decode()
        print(i, inp["encoding"], "|", data[:100])

