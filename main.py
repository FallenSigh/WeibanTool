import time
import json

import weibanapi

x_token = ''
user_id = ''
user_project_id = ''
tenant_code = ''


# 1.  showProgess 获取课程进度
# 2.  listCategory 获取课程分类 传入userprojectid
# 3.  listCourse 获取课程 传入categorycode
# 4.  study 传入courseid(上一步获取的resourceid)
# 5.  getCourseUrl 获取methodToken
# 6.  checkFinish(验证码用的，直接跳过)
# 7.  getNear(获取最近学习，没啥用，直接跳过)
# 8.  调用methodToken完成学习 参数callback(341+16位随机数+时间戳) _(时间戳)

def wait(text: str, ti: int):
    while ti:
        print(text % ti, end='')
        time.sleep(1)
        print('\r', end='')
        ti = ti - 1
    print('                                                                   \r', end='')


def main():
    try:
        w = weibanapi.WeibanAPI(x_token, user_id, user_project_id, tenant_code)

    except Exception:
        print('请检查初始化参数是否正确!')
        exit(-1)

    courseInfo = []

    required, finished = w.showProgress()
    print('共{}， 已完成{}'.format(required, finished))

    # 获取课程分类
    categorys = w.listCategory()
    for c in categorys:
        print("{}[{}/{}]".format(c["categoryName"], c["finishedNum"], c["totalNum"]))
        # 如果该类课程学习数 < 总数 加入到courseInfo列表中
        if c["totalNum"] > c["finishedNum"]:
            courses = w.listCourse(c["categoryCode"])
            for course in courses:
                if course["finished"] == 2:  # 根据观察 1是学了 2是没学
                    courseInfo.append(course)

    for c in courseInfo:
        userCourseId = c["userCourseId"]
        resourceName = c["resourceName"]
        categoryName = c["categoryName"]
        resourceId = c["resourceId"]
        print('开始学习{}-{}'.format(categoryName, resourceName))
        code = w.study(resourceId)
        if code != '0':
            print('开始学习失败')
            exit(-1)
        cUrl = w.getCourseUrl(resourceId)
        token = weibanapi.parseMethodToken(cUrl)
        # 学太快好像有可能学不上
        wait('等待中.......%2d', 15)
        tmp = w.methodToken(token, userCourseId)
        res = tmp[tmp.find('({') + 1:len(tmp) - 1]
        j = json.loads(res)
        if j["msg"] != "ok":
            print('调用methodToken失败!')
            exit(-1)
        wait('通过 %2d s后继续', 3)


if __name__ == '__main__':
    print('免责声明： \n此程序仅供学习使用，由于个人操作引发的一系列后果与作者无关')
    main()
