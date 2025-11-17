import time
import requests
import os


base_url = 'https://openspeech.bytedance.com/api/v1/vc/ata'
appid = "3384563591"
access_token = "UpTwYTHp5ULW0WAOTYazIQ_0q9E1n4Et"
file = "wavfiles/dushunv2_3.MP3"
audio_text = "百年孤独里有这样一句话，他说人群聚集的地方"

def log_time(func):
    def wrapper(*args, **kw):
        begin_time = time.time()
        func(*args, **kw)
        print('total cost time = {time}'.format(time=time.time() - begin_time))
    return wrapper


@log_time
def main():
    response = requests.post(
        '{base_url}/submit'.format(base_url=base_url),
        params=dict(
            appid=appid,
            caption_type='speech',
        ),
        files={
            'audio-text': audio_text,
            'data': (os.path.basename(file), open(file, 'rb'), 'audio/wav'),
        },
        headers={
            'Authorization': 'Bearer; {}'.format(access_token)
        }
    )
    print('submit response = {}'.format(response.text))
    assert (response.status_code == 200)
    assert (response.json()['message'] == 'Success')

    job_id = response.json()['id']
    response = requests.get(
        '{base_url}/query'.format(base_url=base_url),
        params=dict(
            appid=appid,
            id=job_id,
        ),
        headers={
            'Authorization': 'Bearer; {}'.format(access_token)
        }
    )
    print('query response = {}'.format(response.json()))
    assert (response.status_code == 200)


if __name__ == '__main__':
    main()
