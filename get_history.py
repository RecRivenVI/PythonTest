import re
import time
import json
import requests

from tqdm import tqdm
from pathlib import Path
from datetime import datetime

# Properties kept in a message
KEEP = [
    'user_id',
    'raw_message',
    'message',
    'time',
    'message_id',
]
URL = 'http://192.168.0.192:3000/get_group_msg_history'
GROUP_ID = 576353195
SLEEP_SEC = 0
ATTEMPT_TIMES = 20
MAX_MESSAGES_PER_FILE = 100


def save(messages):
    assert len(messages) > 0
    timestamp = int(datetime.now().timestamp())
    with open(f'data_{timestamp}.json', 'w') as f:
        json.dump(messages, f, ensure_ascii=False)


def detect_last_id():
    now_fp = None
    now_timestamp = 0
    for fp in Path('.').iterdir():
        if not fp.is_file():
            continue
        f = re.search(r'data_(\d+)\.json', fp.name)
        if f is None:
            continue
        ts = int(f.group(1))
        if ts > now_timestamp:
            now_timestamp, now_fp = ts, fp
    
    if now_fp is None:
        print('No cache found. Get newest messages.')
        return None

    with now_fp.open('r') as f:
        msg = json.load(f)[-1]
        print(f'Detected last message(first 20 chars): {msg["raw_message"][:20]}')
        return msg['message_id']



def main():
    message_id = detect_last_id()
    queue = []
    for _ in tqdm(range(ATTEMPT_TIMES)):
        time.sleep(SLEEP_SEC)
        data = requests.post(URL, data=json.dumps({
            'group_id': GROUP_ID,
            'message_seq': message_id,
        })).json()
        if data['status'] != 'ok':
            print('Failed to get message.')
            print(data)
            continue

        msgs = [
            # filter
            {k: v for k, v in msg.items() if k in KEEP}
            for msg in data['data']['messages']
        ]
        if len(msgs) == 0:
            print('Got no messages')
            continue

        message_id = msgs[0]['message_id']
        queue.extend(reversed(msgs))

        if len(queue) >= MAX_MESSAGES_PER_FILE:
            save(queue[:MAX_MESSAGES_PER_FILE])
            queue = queue[MAX_MESSAGES_PER_FILE:]

    if queue: save(queue)


if __name__ == '__main__':
    main()