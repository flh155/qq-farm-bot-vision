import os
import sys
import configparser
import time
from utils.farm_bot_cv import FarmBotCV
from utils.window_session import WindowSession
from utils.screen_capture import ScreenCapture
from utils.window_control import WindowControl

# 检查游戏窗口是否存在
window_session = WindowSession("QQ经典农场")
hwnd = window_session.get_hwnd()
if not hwnd:
    print("错误: 未找到【QQ经典农场】窗口，请先打开游戏")
    sys.exit(1)

print(f"找到游戏窗口，HWND: {hwnd}")

# 获取并打印窗口位置
window_pos = window_session.get_window_position()
print(f"窗口位置(屏幕坐标): {window_pos}")
window_rect = window_session.get_window_rect()
print(f"窗口RECT: {window_rect}")

# 加载配置文件
config = configparser.ConfigParser()
config.read(r"config.ini", encoding="utf-8")

# 创建实例
bot = FarmBotCV(config=config)
print("="*50)

def field_test(i):
    game_frame = bot.screen_capture.get_window_frame()
    dog_house_center = bot.get_dog_house_position(game_frame)
    if dog_house_center is None:
        time.sleep(1)
        return False
    dog_house_x, dog_house_y = dog_house_center[0], dog_house_center[1]
    print(f"【狗屋】坐标为：{dog_house_x, dog_house_y}")

    FIRST_FIELD_OFFSET_X = 22
    FIRST_FIELD_OFFSET_Y = 75
    field_offset_map = {
        0: (0, 0),          1: (38, 20),        2: (76, 40),        3: (114, 60),
        4: (-38, 20),       5: (0, 40),         6: (38, 60),        7: (76, 80),
        8: (-76, 40),       9: (-38, 60),       10: (0, 80),        11: (38, 100),
        12: (-114, 60),     13: (-76, 80),      14: (-38, 100),     15: (0, 120),
        16: (-152, 80),     17: (-114, 100),    18: (-76, 120),     19: (-38, 140),
        20: (-190, 100),    21: (-152, 120),    22: (-114, 140),    23: (-76, 160),
    }
    x, y = field_offset_map[i]
    x = dog_house_center[0] + FIRST_FIELD_OFFSET_X + x
    y = dog_house_center[1] + FIRST_FIELD_OFFSET_Y + y

    screen_coord = bot.convert_to_screen_coordinate((x,y))
    print(f"field: {i}  局部坐标{(x, y)} -> 屏幕坐标 {screen_coord}")
    bot.click_at_position(screen_coord)
    # print("点击完成")

# 测试地块点击是否有偏差
while 1:
    for i in range(24):
        field_test(i)
        time.sleep(1)
    print("="*50)
