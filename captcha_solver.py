import requests
from time import sleep


def solve(captcha_api_key, site_key, url, data_s):
    session = requests.Session()

    res = session.post(f"http://2captcha.com/in.php"
                       f"?key={captcha_api_key}"
                       f"&method=userrecaptcha"
                       f"&googlekey={site_key}"
                       f"&data-s={data_s}"
                       f"&pageurl={url}")

    print(f'2Captcha result: {res.text}')
    if res.text == 'ERROR_ZERO_BALANCE':
        return 'ERROR_ZERO_BALANCE'
    
    try:
        captcha_id = res.text.split('|')[1]
    except:
        return "ERROR"

    recaptcha_answer = session.get(
        "http://2captcha.com/res.php?key={}&action=get&id={}".format(captcha_api_key, captcha_id)).text

    print("Solving ref captcha...")
    while 'CAPCHA_NOT_READY' in recaptcha_answer:
        sleep(1)
        recaptcha_answer = session.get(
            "http://2captcha.com/res.php?key={}&action=get&id={}".format(captcha_api_key, captcha_id)).text
        #print(f'\tStep: {recaptcha_answer}')
        if recaptcha_answer == 'ERROR_CAPTCHA_UNSOLVABLE':
            return 'ERROR_CAPTCHA_UNSOLVABLE'

    recaptcha_answer = recaptcha_answer.split('|')[1]
    return recaptcha_answer

