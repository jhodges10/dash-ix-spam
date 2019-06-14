from requests import get

def check_insight_block_count():
    try:
        response = get('https://insight.dash.org/insight-api/status')
        data = response.json()
        return data['info']['blocks']
    except:
        return 0

if __name__ == "__main__":
    print(check_insight_block_count())