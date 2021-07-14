import requests, time, pywifi
from pywifi import const
from os import popen


def login(student_number: int, password: int):
    """登陆校园网"""
    url = r'http://10.10.43.3/drcom/login'
    # 用户信息参数
    users_params = dict(
        DDDDD=student_number,  # 学号
        upass=password,  # 密码
    )
    # 固定参数
    fixed_params = {'0MKKey': 123456, 'R1': 0, 'R3': 0, 'R6': 0, 'para': 00, 'v6ip': ''}
    # 时间参数
    t = time.time()
    t = int(round(t * 1000))  # 获取毫秒级时间戳
    interval = 5000  # 页面加载完毕到点击确认按钮的时间间隔，单位ms
    time1_params = {'callback': 'dr%d' % (t + interval)}
    time2_params = {'_': t, }  # 测试表明只有当callback位于参数第一个，用户名紧随其后，_位于末尾时请求才有效
    params = {**time1_params, **users_params, **fixed_params, **time2_params}
    print(params)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0',
    }
    response = requests.get(url, headers=headers, params=params, timeout=1)
    print(response.text)
    if 'Error' in response.text:
        raise Exception('参数错误，登陆失败')
    elif '"result":1' in response.text:
        return True
    else:
        # 各种各样的原因
        raise Exception('请检查网络配置及确认账号及密码是否正确！')


def get_wifi_name():
    """获取当前连接的WiFi名，如果没有连接WiFi则返回False"""
    res = popen('netsh WLAN show interfaces')
    res = res.read().replace(' ', '').split('\n')
    for text in res:
        if 'SSID' in text:
            return text.split(':')[-1]
    return False


def wifi_connect(wifiname: str = 'local.wlan.bjtu'):
    """连接指定WiFi"""
    wifi = pywifi.PyWiFi()
    ifaces = wifi.interfaces()[0]
    wifi_now = get_wifi_name()
    if wifi_now and wifi_now != wifiname:
        # 当前连接的WiFi与想连接的WiFi不一致
        print('断开与%s的连接' % wifi_now)
        ifaces.disconnect()  # 断开所有wifi连接
        time.sleep(1)
    elif wifi_now == wifiname:
        return True

    if ifaces.status() == const.IFACE_DISCONNECTED:
        profile = pywifi.Profile()  # 创建WiFi连接文件
        profile.ssid = wifiname  # WiFi的ssid，即wifi的名称
        tep_profile = ifaces.add_network_profile(profile)  # 设定新的连接文件
        ifaces.connect(tep_profile)  # 连接WiFi
        time.sleep(1.5)
        if ifaces.status() == const.IFACE_CONNECTED:
            return True
        else:
            return False


def config() -> dict or bool:
    import configparser, os
    path = 'config.ini'

    class Config:
        def __init__(self):
            self.cf = configparser.ConfigParser()
            self.cf.read(path)

        def get_connect(self, param):
            value = self.cf.get("CONNECT", param)
            return value

        def set_connect(self, param, value):
            self.cf.set("CONNECT", param, value)

    cp = Config()

    if not os.path.exists(path):
        print('首次使用请输入个人信息~')
        student_number = input('请输入学号：')
        password = input('请输入密码：')
        with open(path, 'w') as fp:
            cp.cf.add_section('CONNECT')
            cp.set_connect('student_number', student_number)
            cp.set_connect('password', password)
            cp.cf.write(fp)
        return dict(student_number=student_number,
                    password=password,
                    )
    else:
        # 如果文件存在，读取配置文件
        try:
            student_number = int(cp.get_connect('student_number'))
            password = int(cp.get_connect('password'))
            return dict(student_number=student_number,
                        password=password,
                        )
        except:
            os.remove(path)
            return config()


def run(wifiname: str):
    while 1:
        print('正在尝试连接%s...' % wifiname)
        status = wifi_connect(wifiname)
        if status == True:
            # 成功连接WiFi
            print('成功连接%s' % wifiname)
            break
        else:
            time.sleep(1)  # 1s后重连
    while 1:
        print('正在尝试连接校园网...')
        data = config()
        try:
            status = login(data['student_number'], data['password'])
        except Exception as err:
            status = str(err)
        if status == True:
            print('已经连上校园网！')
            return True
        else:
            if 'timed out' in status:
                print('连接超时，即将重试')
            else:
                print(status)
            time.sleep(1)  # 1s后重连
    return False


if not run('web.wlan.bjtu'):
    run('local.wlan.bjtu')
