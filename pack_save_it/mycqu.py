import re
from typing import Dict
from requests import Session
from .auth import access_sso_service
__all__=('access_mycqu',)

urls={
    'MYCQU_TOKEN_INDEX_URL':"https://my.cqu.edu.cn/enroll/token_index",
    'MYCQU_TOKEN_URL':'https://my.cqu.edu.cn/authserver/oauth/token',
    'MYCQU_AUTHORIZE_URL': f'https://my.cqu.edu.cn/authserver/oauth/authorize?client_id=enroll-prod&response_type=code&scope=all&state=&redirect_url={"https://my.cqu.edu.cn/authserver/oauth/token"}',#格式化字符串，不能直接相加?
    'MYCQU_SERVICE_URL':"https://my.cqu.edu.cn/authserver/authentication/cas"
}
CODE_RE=re.compile(r"\?code=([^&]+)&")#正则表达式嗯抄了
def _get_oauth_token(session:Session):
    resp=session.get(urls['MYCQU_AUTHORIZE_URL'],allow_redirects=False,)
    search_match=CODE_RE.search(resp.headers['Location'])
    if search_match is None:
        raise ValueError('failed to get the code whem accessing mycqu')
    assert search_match
    token_data={
        'client_id':'enroll-prod',
        'client_secret':'app-a-1234',
        'code':search_match[1],
        'redirect_url':urls['MYCQU_TOKEN_INDEX_URL'],
        'grant_type':'authorization_code'
    }
    access_token=session.post(urls['MYCQU_TOKEN_URL'],data=token_data)
    return access_token.json()['access_token']
def access_mycqu(session:Session,add_to_head:bool)->Dict[str,str]:#漏写add_to_head
    if 'Authorization' in session.headers:
        del session.headers['Authorization']
    access_sso_service(session,urls['MYCQU_SERVICE_URL'])
    token=_get_oauth_token(session)
    if add_to_head:
        session.headers['Authorization']=token
    return {'Authorization':token}