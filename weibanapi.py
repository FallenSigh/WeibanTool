import datetime
import json
import random
import requests


def get_timestamp():
    return str(round(datetime.datetime.now().timestamp(), 3))

class WeibanAPI:
    tenantCode = ''
    x_token = ' '
    userId = ' '
    userProjectId = ' '
    headers = None

    def __init__(self, token, user_id, user_project_id, tenant_code):
        self.x_token = token
        self.tenantCode = tenant_code
        self.userId = user_id
        self.userProjectId = user_project_id
        self.headers = {
            'X-Token': self.x_token,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203'
        }
        res = self._showProgress()
        if len(res) == 0:
            raise Exception('failed to get course info')

    def showProgress(self):
        res = self._showProgress()
        j = json.loads(res)
        return j["data"]["requiredNum"], j["data"]["requiredFinishedNum"]

    def _showProgress(self):
        url = 'https://weiban.mycourse.cn/pharos/project/showProgress.do?timestamp=' + get_timestamp()
        data = {
            'tenantCode': self.tenantCode,
            'userId': self.userId,
            'userProjectId': self.userProjectId
        }
        return self.process_url(url, data)

    def _process_url(self, url, param, method):
        if method == 'POST':
            re = requests.post(url=url, data=param, headers=self.headers)
        elif method == 'GET':
            url += '?'
            for key, item in param.items():
                url = url + ('' if url.endswith('?') else '&') + str(key) + '=' + str(item)
            re = requests.get(url=url, headers=self.headers)
        else:
            raise ValueError('WRONG METHOD')
        return re.text

    def process_url(self, url, param, method='POST'):
        return self._process_url(url, param, method)

    def _listCategory(self):
        url = 'https://weiban.mycourse.cn/pharos/usercourse/listCategory.do?timestamp=' + get_timestamp()
        data = {
            'tenantCode': self.tenantCode,
            'userId': self.userId,
            'userProjectId': self.userProjectId,
            'chooseType': 3
        }
        return self.process_url(url, data)

    def listCategory(self):
        ret = self._listCategory()
        try:
            j = json.loads(ret)
            return j["data"]
        except json.decoder.JSONDecodeError as e:
            print(e.msg)

    def _listCourse(self, category_code):
        url = 'https://weiban.mycourse.cn/pharos/usercourse/listCourse.do?timestamp=' + get_timestamp()
        data = {
            'tenantCode': self.tenantCode,
            'userId': self.userId,
            'userProjectId': self.userProjectId,
            'chooseType': 3,
            'categoryCode': category_code
        }
        return self.process_url(url, data)

    def listCourse(self, category_code):
        ret = self._listCourse(category_code)
        try:
            j = json.loads(ret)
            return j["data"]
        except json.decoder.JSONDecodeError as e:
            print(e.msg)

    def _getCourseUrl(self, resource_id):
        url = 'https://weiban.mycourse.cn/pharos/usercourse/getCourseUrl.do?timestamp=' + get_timestamp()
        data = {
            'tenantCode': self.tenantCode,
            'userId': self.userId,
            'userProjectId': self.userProjectId,
            'courseId': resource_id
        }
        return self.process_url(url, data)

    def getMethodToken(self, resource_id):
        url = 'https://weiban.mycourse.cn/pharos/usercourse/getCaptcha.do'
        params = {
            'userCourseId': resource_id,
            'userProjectId': self.userProjectId,
            'userId': self.userId,
            'tenantCode': self.tenantCode
        }
        res = requests.get(url, headers=self.headers, params=params).text.encode().decode('unicode_escape')
        question_id = json.loads(res)['captcha']['questionId']

        url = "https://weiban.mycourse.cn/pharos/usercourse/checkCaptcha.do"
        params = {
            "userCourseId": resource_id,
            "userProjectId": self.userProjectId,
            "userId": self.userId,
            "tenantCode": self.tenantCode,
            "questionId": question_id
        }
        data = {
            "coordinateXYs": "[{\"x\":199,\"y\":448},{\"x\":241,\"y\":466},{\"x\":144,\"y\":429}]"
        }

        res = requests.post(url, headers=self.headers, params=params, data=data).text
        return json.loads(res)['data']['methodToken']


    def getCourseUrl(self, resource_id):
        ret = self._getCourseUrl(resource_id).encode().decode('unicode_escape')
        try:
            j = json.loads(ret)
            return j["data"]
        except json.decoder.JSONDecodeError as e:
            print(e.msg)

    def study(self, resource_id):
        res = self._study(resource_id)
        try:
            j = json.loads(res)
            return j["code"]
        except json.decoder.JSONDecodeError as e:
            print(e.msg)

    def finish(self, resource_id, user_course_id):
        courseUrl = self.getCourseUrl(resource_id)
        token = self.getMethodToken(user_course_id)
        url = 'https://weiban.mycourse.cn/pharos/usercourse/v2/{}.do'
        t = get_timestamp().replace('.', '')
        params = {
            'callback': 'jQuery341' + str(random.random()).replace('.', '') + '_' + t,
            'userCourseId': user_course_id,
            'tenantCode': self.tenantCode,
            '_': int(t) + 1
        }

        res = requests.get(url.format(token), params=params, headers=self.headers).text
        if '"code":"-1"' in res:
            res = requests.get(url.format(user_course_id), params=params, headers=self.headers).text
        return res


    def _study(self, resource_id):
        url = 'https://weiban.mycourse.cn/pharos/usercourse/study.do?timestamp=' + get_timestamp()
        data = {
            'tenantCode': self.tenantCode,
            'userId': self.userId,
            'userProjectId': self.userProjectId,
            'courseId': resource_id
        }
        return self.process_url(url, data)
