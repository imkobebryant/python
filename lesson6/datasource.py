import requests
def get_sitename()->list[str]:
    url='https://data.moenv.gov.tw/api/v2/aqx_p_432?api_key=e8dd42e6-9b8b-43f8-991e-b3dee723a52d&limit=1000&sort=ImportDate%20desc&format=JSON'
    try:
        respone=requests.get(url)
        respone.raise_for_status()
        data=respone.json()
        type(respone)
    except Exception as e:
        print(e)
    else:
        sitenames=set()
        for items in (data['records']):
            sitenames.add(items['sitename'])

    # len(sitenames)
    sitenames=list(sitenames)
    return sitenames

# a=get_sitename()
# print(a)


def get_selected_data(sitename:str)->list[str]:
    url='https://data.moenv.gov.tw/api/v2/aqx_p_432?api_key=e8dd42e6-9b8b-43f8-991e-b3dee723a52d&limit=1000&sort=ImportDate%20desc&format=JSON'
    try:
        respone=requests.get(url)
        respone.raise_for_status()
        data=respone.json()
        type(respone)
    except Exception as e:
        print(e)
    else:
        outerlist=[sitename]
        for items in (data['records']):
            if items['sitename']==sitename:
                innerlist=[items['publishtime'],items['county'],items['aqi'],items['pm2.5'],items ['status'],items['latitude'],items['longitude']]
                outerlist.append(innerlist)
            
    return outerlist