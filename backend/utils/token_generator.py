from passlib.hash import hex_md5

def generate_token(username: str, password: str, url_parameters: str) -> str:
    '''
    Генерирует токен запроса VIN17 API на основе данной формулы:
    https://www.17vin.com/doc.html -> Раздел 1003.
    '''
    return hex_md5.hash(hex_md5.hash(username) + hex_md5.hash(password) + url_parameters)