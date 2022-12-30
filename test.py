from pack_save_it.auth import NeedCaptcha,login
from pack_save_it.mycqu import access_mycqu
from requests import Session
session=Session()
try:
    password='theonlylove145'
    account='30043798'
    login(session,account,password)
    print(login(session,account,password).status_code)
except NeedCaptcha as e:
    with open('captcha.jpg','wb') as file:
        file.write(e.image)
    print('请输入验证码并回车:',end=' ')
    e.after_captcha(input())
access_mycqu(session,add_to_head=0)