import base64
import json
import uuid
import requests
import os, sys

def huoshan_normal_gen(text, file_to_save):
    text_content = ""
    if os.path.exists(text):
        with open(text, "r") as f:
            text_content = f.read()
    else:
        text_content = text.strip()

    # 填写平台申请的appid, access_token以及cluster
    appid = "2723200895"
    access_token= "xPartAAzIhh4Y6_zc2MpwHA3WaYayoDS"
    cluster = "volcano_tts"

    #voice_type = "BV503_streaming"
    voice_type = "BV504_streaming"
    host = "openspeech.bytedance.com"
    api_url = f"https://{host}/api/v1/tts"

    header = {"Authorization": f"Bearer;{access_token}"}

    request_json = {
        "app": {
            "appid": appid,
            "token": access_token,
            "cluster": cluster
        },
        "user": {
            "uid": "388808087185088"
        },
        "audio": {
            "voice_type": voice_type,
            "encoding": "wav",
            "speed_ratio": 1.0,
            "volume_ratio": 1.0,
            "pitch_ratio": 1.0,
        },
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": text_content,
            "text_type": "plain",
            "operation": "query",
            "with_frontend": 1,
            "frontend_type": "unitTson"

        }
    }
    try:
        if os.path.exists(file_to_save):
            os.remove(file_to_save)
        resp = requests.post(api_url, json.dumps(request_json), headers=header)
        #print(f"resp body: \n{resp.json()}")
        if "data" in resp.json():
            data = resp.json()["data"]
            file_to_save = open(file_to_save, "wb")
            file_to_save.write(base64.b64decode(data))
    except Exception as e:
        e.with_traceback()

if __name__ == "__main__":
    text = sys.argv[1]
    target_file = sys.argv[2]
    huoshan_normal_gen(text, target_file)