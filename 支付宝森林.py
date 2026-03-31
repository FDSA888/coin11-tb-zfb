import time
import uiautomator2 as u2
import cv2

# import ant_forest_task

from utils import (
    get_current_app,
    select_device
)

# =========================
# 全局状态
# =========================
unclick_btn = []
have_clicked = {}
in_other_app = False
start_time = time.time()
first_visit = True
img_task_btn = "img/forest_reward.png"


# =========================
# 页面 / 状态判断
# =========================
def check_in_forest():
    package, _ = get_current_app(d)
    return (
            package == "com.eg.android.AlipayGphone"
            and (
                    d(text="个人版").exists
                    or d(text="背包").exists
                    or d(text="领奖励").exists
            )
    )


def check_in_forest_task():
    package, _ = get_current_app(d)
    return (
            package == "com.eg.android.AlipayGphone"
            and (
                    d(text="奖励").exists
                    or d(text="去兑换").exists
            )
    )


# =========================
# 页面跳转相关
# =========================

# 寻找蚂蚁森林入口
def find_forest_btn():
    forest_btn = d(
        resourceId="com.alipay.android.phone.openplatform:id/home_app_view"
    ).child(text="蚂蚁森林")

    if forest_btn.exists:
        forest_btn.click()
        time.sleep(5)
    else:
        d(description="搜索框").click()
        d(resourceId="com.alipay.mobile.antui:id/search_input_box").send_keys("蚂蚁森林")
        time.sleep(3)
        d(descriptionContains="蚂蚁森林").click()
        time.sleep(5)


# 返回蚂蚁森林
def back_to_forest():
    package, _ = get_current_app(d)
    if package == "com.eg.android.AlipayGphone":
        d.press("back")
    else:
        d.app_start("com.eg.android.AlipayGphone")
    time.sleep(3)


# =========================
# 任务相关
# =========================

# 进入任务列表
def image_search_btn(template_path, threshold=0.8):
    """
    识别图片并在手机上点击
    :param template_path: 目标图片的路径 (如 'target.png')
    :param threshold: 匹配阈值，0-1之间，越接近1越要求精准匹配
    :return: 布尔值，是否点击成功
    """

    # 获取手机屏幕截图并转换为 OpenCV 格式
    screenshot_raw = d.screenshot(format="opencv")
    screen_gray = cv2.cvtColor(screenshot_raw, cv2.COLOR_BGR2GRAY)

    # 读取目标图片（模板）并转为灰度图
    template = cv2.imread(template_path, 0)
    if template is None:
        print(f"错误：无法加载图片文件 {template_path}")
        return False

    w, h = template.shape[::-1]

    # 进行模板匹配
    res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # 判断匹配度是否达标
    if max_val >= threshold:
        # 计算目标中心坐标
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2

        # print(f"匹配成功！相似度: {max_val:.2f}，坐标: ({center_x}, {center_y})")

        # 执行点击
        d.click(center_x, center_y)
        return True
    else:
        # print(f"匹配失败，最高相似度仅为: {max_val:.2f}")
        return False


def go_look_task():
    if not check_in_forest_task():
        return "不在任务页面"

    dialog = d(className="android.app.Dialog")
    btn = dialog.child(textMatches="去看看", clickable=True)
    if btn.exists:
        btn.click()
        d.sleep(4)
        d.press("back")


def click_reward_btn():
    if not check_in_forest_task():
        return "不在任务页面"

    dialog = d(className="android.app.Dialog")
    btn = dialog.child(text="立即领取", clickable=True)
    if btn.exists:
        btn.click()
        d.sleep(3)


# 检查任务是否已完成（领取按钮是否存在）
def check_task_completed(task_name):
    try:
        dialog = d(className="android.app.Dialog")
        reward_btn = dialog.child(text="立即领取", clickable=True)

        if reward_btn.exists:
            print(f"任务「{task_name}」可领取奖励")
            return True
        else:
            print(f"任务「{task_name}」未完成或已领取")
            return False
    except:
        return False


# =========================
# 初始化相关
# =========================
def init_device():
    global d
    device = select_device()
    d = u2.connect(device)
    print(f"已连接设备：{device}")

    d.shell("adb kill-server && adb start-server")
    time.sleep(5)


def check_in_zfb_forest_task():
    global first_visit

    if first_visit:
        first_visit = False

        # 启动支付宝
        d.app_start("com.eg.android.AlipayGphone", stop=True, use_monkey=True)
        time.sleep(6)

        # 进入蚂蚁森林
        find_forest_btn()
        time.sleep(3)

        # 确保在蚂蚁森林页面
        if not check_in_forest():
            print("未进入蚂蚁森林页面")
            return

        # 进入任务页面
        image_search_btn(img_task_btn, 0.7)
        time.sleep(3)


# =========================
# 主执行入口
# =========================
def main():
    # 判断是否在支付宝森林任务页面
    check_in_zfb_forest_task()


# =========================
# 程序入口
# =========================
if __name__ == "__main__":
    init_device()

    try:
        main()
    finally:
        end_time = time.time()
        print(f"运行结束，用时 {int(end_time - start_time)} 秒")
