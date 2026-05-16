from ast import Break
import cv2
import keyboard
import time
import pyautogui
import logging
import configparser
import random
from utils.cv_match import cvMatch
from utils.screen_capture import ScreenCapture
from utils.window_control import WindowControl
from utils.window_session import WindowSession


class FarmBotCV:
    def __init__(self, check_interval = 3, debug_mode = False, config: configparser.ConfigParser = None):
        self.debug_mode = debug_mode
        self.logger = logging.getLogger(__name__)
        if debug_mode == True:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        if config is None:
            assert False, f"配置文件缺失，请检查是否传入配置文件"
        
        # 获取全局配置
        self.config = config
        self.enable_process_self = config.getboolean('bot', 'enable_process_self')
        self.enable_process_friend = config.getboolean('bot', 'enable_process_friend')
        self.friend_colddown_time = config.getint('bot', 'friend_colddown_time')
        self.enable_silence_click = config.getboolean('bot', 'enable_silence_click')
        self.enable_hide_window = config.getboolean('bot', 'enable_hide_window', fallback=False)

        if self.enable_hide_window and not self.enable_silence_click:
            self.enable_silence_click = True

        # 获取自己农场的功能配置
        self.enable_harvest = config.getboolean('self', 'enable_harvest')
        self.enable_remove_bug = config.getboolean('self', 'enable_remove_bug')
        self.enable_remove_grass = config.getboolean('self', 'enable_remove_grass')
        self.enable_watering = config.getboolean('self', 'enable_watering')
        self.enable_daily_free = config.getboolean('self', 'enable_daily_free')
        self.enable_plant_seed = config.getboolean('self', 'enable_plant_seed')
        self.plant_seed_check_interval = config.getint('self', 'plant_seed_check_interval')

        # 获取好友农场任务的功能配置
        self.enable_steal = config.getboolean('friend', 'enable_steal')
        self.enable_help_remove_bugs = config.getboolean('friend', 'enable_help_remove_bugs')
        self.enable_help_remove_grass = config.getboolean('friend', 'enable_help_remove_grass')
        self.enable_help_watering = config.getboolean('friend', 'enable_help_watering')

        # 获取各项阈值参数
        self.help_remove_bugs_frame_threshold = config.getfloat('threshold', 'help_remove_bugs_frame')
        self.help_remove_grass_frame_threshold = config.getfloat('threshold', 'help_remove_grass_frame')
        self.help_watering_frame_threshold = config.getfloat('threshold', 'help_watering_frame')
        self.can_steal_frame_threshold = config.getfloat('threshold', 'can_steal_frame')
        self.close_x_frame_threshold = config.getfloat('threshold', 'close_x_frame')
        self.go_home_frame_threshold = config.getfloat('threshold', 'go_home_frame')
        self.steal_all_frame_threshold = config.getfloat('threshold', 'steal_all_frame')
        self.friend_icon_frame_threshold = config.getfloat('threshold', 'friend_icon_frame')
        self.welcome_back_frame_threshold = config.getfloat('threshold', 'welcome_back_frame')
        self.harvest_all_frame_threshold = config.getfloat('threshold', 'harvest_all_frame')
        self.harvest_one_frame_threshold = config.getfloat('threshold', 'harvest_one_frame')
        self.get_new_seed_frame_threshold = config.getfloat('threshold', 'get_new_seed_frame')
        self.level_up_frame_threshold = config.getfloat('threshold', 'level_up_frame')
        self.watering_all_frame_threshold = config.getfloat('threshold', 'watering_all_frame')
        self.remove_all_grass_frame_threshold = config.getfloat('threshold', 'remove_all_grass_frame')
        self.remove_all_bugs_frame_threshold = config.getfloat('threshold', 'remove_all_bugs_frame')
        self.reconnect_frame_threshold = config.getfloat('threshold', 'reconnect_frame')
        self.can_steal_small_frame_threshold = config.getfloat('threshold', 'can_steal_small_frame')
        self.can_watering_small_frame_threshold = config.getfloat('threshold', 'can_watering_small_frame')
        self.can_remove_bugs_small_frame_threshold = config.getfloat('threshold', 'can_remove_bugs_small_frame')
        self.close_x_small_frame_threshold = config.getfloat('threshold', 'close_x_small_frame')
        self.shop_red_frame_threshold = config.getfloat('threshold', 'shop_red_frame')
        self.daily_free_frame_threshold = config.getfloat('threshold', 'daily_free_frame')
        self.return_farm_frame_threshold = config.getfloat('threshold', 'return_farm_frame')
        self.dog_house_frame_threshold = config.getfloat('threshold', 'dog_house_frame')
        self.remove_seed_frame_threshold = config.getfloat('threshold', 'remove_seed_frame')



        self.check_interval = check_interval
        self.running = True
        self.pause_status = False
        self.now_scene = "home"     # 判断当前所在的场景
        self.window_session = WindowSession("QQ经典农场")
        self.screen_capture = ScreenCapture("QQ经典农场", self.window_session)
        if self.enable_silence_click or self.enable_hide_window:
            self.window_control = WindowControl("QQ经典农场", self.window_session)
        else:
            self.window_control = None
        self.cv_match = cvMatch()
        self.is_friend_has_task = True
        self.start_friend_check_colddown_time = 0
        self.game_frame_w = None
        self.game_frame_h = None
        self.is_today_check_daily_free = False
        self.last_check_plant_time = 0

        
        # 加载匹配图片资源
        self.welcome_back_frame = cv2.imread(r"assert\datasets\icons\welcome_back.jpg")
        self.harvest_all_frame = cv2.imread(r"assert\datasets\icons\harvest_all.jpg")
        self.harvest_one_frame = cv2.imread(r"assert\datasets\icons\harvest_one.jpg")
        self.get_new_seed_frame = cv2.imread(r"assert\datasets\icons\get_new_seed.jpg")
        self.level_up_frame = cv2.imread(r"assert\datasets\icons\level_up.jpg")
        self.watering_all_frame = cv2.imread(r"assert\datasets\icons\watering_all.jpg")
        self.remove_all_grass_frame = cv2.imread(r"assert\datasets\icons\remove_all_grass.jpg")
        self.remove_all_bugs_frame = cv2.imread(r"assert\datasets\icons\remove_all_bugs.jpg")
        self.reconnect_frame = cv2.imread(r"assert\datasets\icons\reconnect.jpg")
        self.friend_icon_frame = cv2.imread(r"assert\datasets\icons\friend_red.jpg")
        self.can_steal_frame = cv2.imread(r"assert\datasets\icons\can_steal.jpg")
        self.steal_all_frame = cv2.imread(r"assert\datasets\icons\steal_all.jpg")
        self.go_home_frame = cv2.imread(r"assert\datasets\icons\go_home.jpg")
        self.close_x_frame = cv2.imread(r"assert\datasets\icons\close_x.jpg")
        self.help_remove_bugs = cv2.imread(r"assert\datasets\icons\help_remove_bugs.jpg")
        self.help_remove_grass = cv2.imread(r"assert\datasets\icons\help_remove_grass.jpg")
        self.help_watering = cv2.imread(r"assert\datasets\icons\help_watering.jpg")
        self.can_steal_small_frame = cv2.imread(r"assert\datasets\icons\can_steal_small.jpg")
        self.can_watering_small_frame = cv2.imread(r"assert\datasets\icons\can_watering_small.jpg")
        self.can_remove_bugs_small_frame = cv2.imread(r"assert\datasets\icons\can_remove_bugs.jpg")
        self.close_x_small_frame = cv2.imread(r"assert\datasets\icons\close_x_small.jpg")
        self.shop_red_frame = cv2.imread(r"assert\datasets\icons\shop_red.jpg")
        self.daily_free_frame = cv2.imread(r"assert\datasets\icons\daily_free.jpg")
        self.return_farm_frame = cv2.imread(r"assert\datasets\icons\return_farm.jpg")
        self.dog_house_frame = cv2.imread(r"assert\datasets\icons\dog_house.jpg")
        self.remove_seed_frame = cv2.imread(r"assert\datasets\icons\remove_seed.jpg")

        self.logger.info("机器人初始化完成")
        if self.enable_silence_click:
            self.logger.warning("注意：【后台静默点击】功能已被配置启用")
        if not self.enable_process_friend:
            self.logger.warning("注意：【处理好友农场】功能已被配置禁用")
        if not self.enable_process_self:
            self.logger.warning("注意：【处理自家农场】功能已被配置禁用")
        if not self.enable_steal:
            self.logger.warning("注意：【偷菜】功能已被配置禁用")
        if not self.enable_help_remove_grass:
            self.logger.warning("注意：【帮助好友除草】功能已被配置禁用")
        if not self.enable_help_watering:
            self.logger.warning("注意：【帮助好友浇水】功能已被配置禁用")
        if not self.enable_remove_bug:
            self.logger.warning("注意：【帮助好友除虫】功能已被配置禁用")
        if not self.enable_daily_free:
            self.logger.warning("注意：【自动领取每日免费礼包】功能已被配置禁用")
        if not self.enable_plant_seed:
            self.logger.warning("注意：【自动种植】功能已被配置禁用")
        if self.enable_hide_window:
            self.logger.warning("注意：【隐藏窗口】功能已被配置启用")
        self.logger.info(f"【机器人操作间隔】已配置为 {self.check_interval} 秒")
        self.logger.info(f"【好友巡检间隔】已配置为 {self.friend_colddown_time} 秒")
        self.logger.info(f"【自动种植检查间隔】已配置为 {self.plant_seed_check_interval} 秒")

        self.apply_window_visibility()

        
    def start(self):
        # 注册退出热键
        keyboard.add_hotkey('ctrl+c', self.stop)
        keyboard.add_hotkey('p', self.pause)

        while self.running:
            # 主循环逻辑
            if not self.pause_status:
                self.logger.info("======================机器人正在执行一轮操作======================")
                self.run_cycle()
                self.logger.info(f"======================本轮操作执行完毕======================\r\n")
            if self.debug_mode == True:
                self.logger.debug(f"********Debug模式已开启，按[ctrl+s]键后进入下一轮操作********")
                keyboard.wait('ctrl+s')
            else:
                time.sleep(self.check_interval)
            
    def pause(self):
        if self.pause_status == False:
            self.logger.info("接收到暂停信号，机器人暂时停止处理")
            self.pause_status = True
        else:
            self.logger.info("接收到恢复信号，机器人继续处理")
            self.pause_status = False

    def stop(self):
        self.logger.info("接收到停止信号，机器人已停止退出")
        self.running = False
        self.apply_window_visibility(False)
        exit()

    def apply_window_visibility(self, hidden=None):
        """根据当前配置隐藏或显示目标窗口。"""
        if hidden is None:
            hidden = self.enable_hide_window

        if self.window_control is None:
            return False

        if hidden:
            return self.window_control.hide_window()
        return self.window_control.show_window()
    

    def run_cycle(self):
        # 循环处理事件
        self.logger.debug(f"now sence:{self.now_scene}")
        if self.screen_capture.check_window_exist():
            self.logger.debug("正在获取游戏画面")
            game_frame = self.screen_capture.get_window_frame()     # 获取游戏画面
            if game_frame is None:
                self.logger.error(f"游戏画面截取失败，请检查游戏是否开启并确保窗口在前台")
                return
            self.logger.debug("游戏画面获取成功,开始处理")
            # 对游戏窗口大小进行检测（当前版本下若窗口被调的太小会导致匹配不到甚至报错）
            # TODO 优化获取游戏画面的方式
            game_frame_shape = game_frame.shape
            self.logger.debug(f"游戏当前窗口尺寸：{game_frame_shape}")
            game_frame_w, game_frame_h = game_frame_shape[1], game_frame_shape[0]
            if game_frame_w < 400 or game_frame_h < 800:
                self.logger.error(f"游戏窗口尺寸过小，请调整窗口大小,当前窗口尺寸：{game_frame_w}x{game_frame_h}，至少需满足: 400x800")
                return
            self.game_frame_w = game_frame_w
            self.game_frame_h = game_frame_h

            # 验证是否真正回到了自己的农场
            # 检查是否存在好友农场特有的元素（如回家按钮），如果存在但场景被标记为home，则修正场景
            if self.now_scene == "home":
                # 检查是否仍然在好友农场（存在回家按钮）
                if self.check_go_home_icon(game_frame):
                    self.logger.warning("检测到仍在好友农场，已再次点击返回自己农场按钮")
                    self.now_scene = "home"
                # 检查是否在商店等界面
                if self.check_close_x_icon(game_frame):
                    self.logger.warning("检测到在商店等界面，已再次点击返回自己农场按钮")
                    self.now_scene = "home"
                if self.check_return_farm(game_frame):
                    self.logger.warning("检测到在商店等界面，已再次点击返回自己农场按钮")
                    self.now_scene = "home"
            
            # 优先处理自家农场事件
            if self.now_scene == "home":
                if self.enable_process_self:
                    self.logger.info(f"正在检查自家农场是否有可执行的任务")
                    if self.process_self_farm(game_frame):
                        self.is_self_has_task = True
                        return
                    else:
                        self.logger.info("家里已无可执行的任务，下一轮巡查将尝试查看其它好友家可执行的任务")
                        self.now_scene = "friend"
                        
                else:
                    self.logger.warning("机器人已被配置为【不处理自家农场】")
                    self.now_scene = "friend"
            else:       # 自家地里没事干的时候尝试去偷菜
                if self.enable_process_friend:
                    if self.is_friend_has_task == False and time.time() - self.start_friend_check_colddown_time < self.friend_colddown_time:
                        self.logger.info(f"上次检查好友农场无任务后, 冷却时间还未达到{self.friend_colddown_time}秒,当前已过去{int(time.time() - self.start_friend_check_colddown_time)}秒,本轮巡检暂不操作")
                        # 验证是否真正回到了自己的农场
                        if not self.check_go_home_icon(game_frame):
                            self.now_scene = "home"
                        return
                    self.logger.info(f"正在检查好友农场是否有可执行的任务")
                    if self.process_friend_farm(game_frame):
                        self.is_friend_has_task = True
                        return
                    else:
                        self.logger.info("好友农场已无可执行的任务，下一轮巡查将回家查看是否有可执行的任务")
                        # 只有当确实没有回家按钮时，才设置为home
                        if not self.check_go_home_icon(game_frame):
                            self.now_scene = "home"
                            self.is_friend_has_task = False
                            self.start_friend_check_colddown_time = time.time()   # 记录开始冷却时间
                        else:
                            self.logger.warning("仍在好友农场，等待下次尝试返回")
                        return 
                        
                else:
                    self.logger.warning("机器人已被配置为【不处理好友农场】")
                    # 验证是否真正回到了自己的农场
                    if not self.check_go_home_icon(game_frame):
                        self.now_scene = "home"
                    else:
                        self.logger.warning("仍在好友农场，尝试返回")
                        self.check_go_home_icon(game_frame)
                        self.now_scene = "home"
                        return 

        else:
            self.logger.warning("未找到游戏窗口，请检查游戏是否开启并确保窗口在前台")



    def process_self_farm(self, game_frame):
        '''
        处理自家农场事件
        '''
        # 检测重连按钮
        if self.check_reconnect(game_frame):
            return True
        # 检测欢迎回来界面
        if self.check_welcome_back(game_frame):
            return True
        # 检测其它如更新通知等弹窗
        if self.check_close_x_icon(game_frame):
            return True
        if self.enable_harvest:
            # 检测一键收获按钮
            if self.check_harvest_all(game_frame):
                return True
            # 检测单个收获按钮
            if self.check_harvest_one(game_frame):
                return True
        else:
            self.logger.warning("机器人已被配置为【不执行收获】")
        # 检测获得新种子页面
        if self.check_get_new_seed(game_frame):
            return True
        # 检测升级提示窗口
        if self.check_level_up(game_frame):
            return True
        if self.enable_watering:
            # 检测一键浇水按钮
            if self.check_watering_all(game_frame):
                return True
        else:
            self.logger.warning("机器人已被配置为【不执行浇水】")
        # 检测一键除草按钮
        if self.enable_remove_grass:
            # 检测一键除草按钮
            if self.check_remove_all_grass(game_frame):
                return True
        else:
            self.logger.warning("机器人已被配置为【不执行除草】")
        if self.enable_remove_bug:
            # 检测一键除虫按钮
            if self.check_remove_all_bugs(game_frame):
                return True
        else:
            self.logger.warning("机器人已被配置为【不执行除虫】")
        
        # 自动种植功能
        if self.enable_plant_seed == True:
            if time.time() - self.last_check_plant_time > self.plant_seed_check_interval:
                for field_idx in range(24):
                    if self.running == False:
                        exit()
                    self.logger.info("正在检查是否有空地可以种植")
                    game_frame = self.screen_capture.get_window_frame()     # 获取游戏画面
                    if game_frame is None:
                        self.logger.error(f"游戏画面截取失败，请检查游戏是否开启并确保窗口在前台")
                        continue
                    if not self.plant_seed_v1(game_frame, field_idx):
                        break
                self.last_check_plant_time = time.time()
                self.logger.debug("尝试点击空白位置")
                time.sleep(1)
                dog_house_center = self.get_dog_house_position(game_frame)
                if dog_house_center:
                    target_x = dog_house_center[0]
                    target_y = dog_house_center[1] - 80  # 点击狗屋上方80像素的空白位置
                    self.click_at_position(self.convert_to_screen_coordinate((target_x, target_y)))
                else:
                    self.click_at_position(self.convert_to_screen_coordinate((200, 270)))
            else:
                self.logger.info(f"距离上次检查可播种地块时间间隔未达到{self.plant_seed_check_interval}秒，本轮巡检暂不检查，当前间隔时间为：{int(time.time() - self.last_check_plant_time)}秒")
        
        time.sleep(0.5)
        
        # 检测每日礼包是否已领取
        if self.enable_daily_free == True:
            if self.now_scene == "home":
                current_hour = time.localtime().tm_hour
                current_min = time.localtime().tm_min
                current_sec = time.localtime().tm_sec
                if self.is_today_check_daily_free == False:
                    self.logger.info("正在尝试领取【每日免费礼包】")
                    self.check_daily_free()
                    self.is_today_check_daily_free = True
                    return True
                else:
                    if current_hour == 0 and current_min == 0 and current_sec in [0,1,2,3]:     # 到了每日0点
                        self.is_today_check_daily_free = False
                        self.logger.info("已过每日0点，今日免费礼包已刷新")
                    else:
                        self.logger.info("今日免费礼包已领取")    
                    return False   
        else:
            self.logger.info("机器人已被配置为【不检查领取每日免费礼包】")
            return False
        

    def process_friend_farm(self, game_frame):
        '''
        处理好友农场事件
        '''
        if self.now_scene == "friend":    # 在自家农场界面检测好友图标上面是否有弹窗显示可偷
            if self.enable_steal == True:
                if self.check_can_steal_small(game_frame):
                    self.now_scene = "friend_farm"
                    return True
            else:
                self.logger.info("当前配置不偷取好友作物")
            if self.enable_help_watering == True:
                if self.check_can_watering_small(game_frame):
                    self.now_scene = "friend_farm"
                    return True
            else:
                self.logger.info("当前配置不帮助好友浇水")
            if self.enable_help_remove_bugs == True and self.enable_help_remove_grass == True:
                if self.check_can_remove_bugs_small(game_frame):
                    self.now_scene = "friend_farm"
                    return True
            else:
                self.logger.info("当前配置不帮助好友除虫/除草")
            if self.check_close_x_small(game_frame):    # 好友来农场的弹窗需要关掉
                self.now_scene = "home"
                return True
            # 如果没有弹窗则点开好友列表再次确认
            if self.check_friend_icon(game_frame):
                self.now_scene = "friend_list"
                return True

        # 在好友列表的操作
        elif self.now_scene == "friend_list":
            # 检测可以偷的图标
            if self.enable_steal == True:
                if self.check_steal_icon(game_frame):
                    self.now_scene = "friend_farm"  # 在好友农场界面
                    return True 
            else:
                self.logger.info("当前配置不偷取好友作物")
            # 检测可以帮忙除草的图标
            if self.enable_help_remove_grass == True:
                if self.check_help_remove_grass(game_frame):
                    self.now_scene = "friend_farm"  # 在好友农场界面
                    return True
            else:
                self.logger.info("当前配置不帮助好友除草")
            # 检测可以帮忙浇水的图标
            if self.enable_help_watering == True:
                if self.check_help_watering(game_frame):
                    self.now_scene = "friend_farm"  # 在好友农场界面
                    return True
            else:
                self.logger.info("当前配置不帮助好友浇水")
            # 检测可以帮忙除虫的图标
            if self.enable_help_remove_bugs == True:
                if self.check_help_remove_bugs(game_frame):
                    self.now_scene = "friend_farm"  # 在好友农场界面
                    return True
            else:
                self.logger.info("当前配置不帮助好友除虫")
            # 没有好友任务，点击X返回
            if self.check_close_x_icon(game_frame):
                return False
            # 可能只是在好友界面，先返回True
            else:
                return True
        
        
        # 在好友农场中的操作
        elif self.now_scene == "friend_farm":
            if self.enable_steal == True:
                #检测一键偷取按钮
                if self.check_steal_all_icon(game_frame):
                    return True
            else:
                self.logger.info("当前配置不偷取好友作物")
            # 检测单个收获按钮（四方格地无法一键偷取）
            if self.enable_steal == True:
                if self.check_harvest_one(game_frame):
                    return True
            else:
                self.logger.info("当前配置不执行收获")
            # 检测是否能帮忙浇水
            if self.enable_help_watering == True:
                if self.check_watering_all(game_frame):
                    return True
            else:
                self.logger.info("当前配置不帮助好友浇水")
            # 检测是否能帮忙除草
            if self.enable_help_remove_grass == True:
                if self.check_remove_all_grass(game_frame):
                    return True
            else:
                self.logger.info("当前配置不帮助好友除草")
            # 检测是否能帮忙除虫
            if self.enable_help_remove_bugs == True:
                if self.check_remove_all_bugs(game_frame):
                    return True
            else:
                self.logger.info("当前配置不帮助好友除虫")
            # 以上都没有则回家
            if self.check_go_home_icon(game_frame):
                # 点击回家按钮后，不立即设置为home，等待下次循环验证是否真正返回
                # 增加延迟，确保页面有时间响应
                time.sleep(1.5)
                return True
        else:
            self.logger.error("scene error")
            return False


    def convert_to_screen_coordinate(self, local_coord):
        '''
        将截图内的局部坐标转换为屏幕绝对坐标
        
        Args:
            local_coord: 局部坐标 (x, y)
        
        Returns:
            tuple: 屏幕绝对坐标 (screen_x, screen_y)
        '''
        window_pos = self.screen_capture.get_window_position()
        if window_pos is None:
            raise RuntimeError("无法获取窗口位置")
        
        screen_x = window_pos[0] + local_coord[0]
        screen_y = window_pos[1] + local_coord[1]
        
        return (screen_x, screen_y)
    
    def click_at_position(self, screen_coord, duration=0.1):
        '''
        在指定屏幕坐标位置执行鼠标点击
        新增随机值机制,在目标坐标点基础上随机向四周偏移少量像素
        避免经常点击同一坐标触发检测
        
        Args:
            screen_coord: 屏幕绝对坐标 (x, y)
            duration: 鼠标按下持续时间，默认 0.1 秒
        '''
        # 加入随机值机制,在目标坐标点基础上随机向四周偏移不超过3像素
        random_x_px = random.randint(-3, 3)
        random_y_px = random.randint(-3, 3)
        target_x = int(screen_coord[0] + random_x_px)
        target_y = int(screen_coord[1] + random_y_px)
        if self.enable_silence_click == True:
            # 使用后台窗口控制进行点击
            success = self.window_control.click(target_x, target_y, duration)
            if success:
                self.logger.debug(f"原坐标：{screen_coord}, 随机偏移：{random_x_px}, {random_y_px}, 最终点击坐标：{target_x}, {target_y}")
            else:
                self.logger.error(f"后台点击失败，原坐标：{screen_coord}, 随机偏移：{random_x_px}, {random_y_px}, 最终点击坐标：{target_x}, {target_y}")

        else:
            pyautogui.click(target_x, target_y, duration=duration)
            self.logger.debug(f"原坐标：{screen_coord}, 随机偏移：{random_x_px}, {random_y_px}, 最终点击坐标：{target_x}, {target_y}")

    def check_help_remove_bugs(self, game_frame):
        '''
        检查是否可以帮忙除虫
        Returns:
            bool: 是否可以帮忙除虫
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.help_remove_bugs, threshold=0.6)
        if match_result is not None:        # 可以帮忙除虫
            self.logger.debug(f"检测到【可帮忙除虫】图标，准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将点击位置偏移到【拜访】区域
            center_x = match_result['center'][0]
            center_y = match_result['center'][1]
            pias_x = center_x + 181
            pias_y = center_y - 10
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate((pias_x,pias_y))
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【可帮忙除虫】图标, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False

    def check_help_remove_grass(self, game_frame):
        '''
        检查是否可以帮忙除草
        Returns:
            bool: 是否可以帮忙除草
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.help_remove_grass, threshold=self.help_remove_grass_frame_threshold)
        if match_result is not None:        # 可以帮忙除草
            self.logger.debug(f"检测到【可帮忙除草】图标，准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将点击位置偏移到【拜访】区域
            center_x = match_result['center'][0]
            center_y = match_result['center'][1]
            pias_x = center_x + 181
            pias_y = center_y - 10
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate((pias_x,pias_y))
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【可帮忙除草】图标, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False

    def check_help_watering(self, game_frame):
        '''
        检查是否可以帮忙浇水
        Returns:
            bool: 是否可以帮忙浇水
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.help_watering, threshold=self.help_watering_frame_threshold)
        if match_result is not None:        # 可以帮忙浇水
            self.logger.debug(f"检测到【可帮忙浇水】图标，准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将点击位置偏移到【拜访】区域
            center_x = match_result['center'][0]
            center_y = match_result['center'][1]
            pias_x = center_x + 181
            pias_y = center_y - 10
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate((pias_x,pias_y))
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【可帮忙浇水】图标, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False

    def check_close_x_icon(self, game_frame):
        '''
        检查是否点击了关闭按钮
        Returns:
            bool: 是否点击了关闭按钮
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.close_x_frame, threshold=self.close_x_frame_threshold)
        if match_result is not None:        # 点击了关闭按钮
            self.logger.debug(f"检测到【关闭】按钮，准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【关闭】按钮, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False



    def check_go_home_icon(self, game_frame):
        '''
        检查是否有一键回家的图标
        Returns:
            bool: 是否有一键回家的图标
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.go_home_frame, threshold=self.go_home_frame_threshold)
        if match_result is not None:        # 有一键回家图标
            self.logger.debug(f"检测到【一键回家】图标，准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【一键回家】图标, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False


    def check_steal_all_icon(self, game_frame):
        '''
        检查是否有一键偷取的图标
        Returns:
            bool: 是否有一键偷取的图标
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.steal_all_frame, threshold=self.steal_all_frame_threshold)
        if match_result is not None:        # 有一键偷取图标
            self.logger.info(f"检测到【一键偷取】图标，准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【一键偷取】图标, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False


    def check_steal_icon(self, game_frame):
        '''
        检查是否有可以偷菜的图标
        Returns:
            bool: 是否点击了偷菜图标
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.can_steal_frame, threshold=self.can_steal_frame_threshold)
        if match_result is not None:        # 点击了偷菜图标
            self.logger.debug(f"检测到【可以偷的图标】，准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将点击位置偏移到【拜访】区域
            center_x = match_result['center'][0]
            center_y = match_result['center'][1]
            pias_x = center_x + 181
            pias_y = center_y - 10
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate((pias_x, pias_y))
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【可以偷的图标】, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False

    def check_friend_icon(self, game_frame):
        '''
        检查是否点击了好友图标
        Returns:
            bool: 是否点击了好友图标
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.friend_icon_frame, threshold=self.friend_icon_frame_threshold)
        if match_result is not None:        # 点击了好友图标
            self.logger.debug(f"检测到【好友图标】，准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【好友图标】, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False


    def check_welcome_back(self, game_frame):
        '''
        检查是否弹欢迎回来的窗口
        
        Returns:
            bool: 是否检测到并处理了欢迎弹窗
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.welcome_back_frame, threshold=self.welcome_back_frame_threshold)
        if match_result is not None:        # 有欢迎回来界面
            self.logger.info(f"检测到【欢迎回来】界面，准备点击 X 按钮, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            center_x = match_result['center'][0]
            center_y = match_result['center'][1]
            # 因截图是上方一条，因此右上角X位置要加上偏移
            pias_x = center_x + 185     # 往右偏大概185pxs
            pias_y = center_y - 16      # 往上偏大概16px
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate((pias_x, pias_y))
            # 点击屏幕坐标
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【欢迎回来】界面, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False

    def check_harvest_all(self, game_frame):
        '''
        检查是否有一键收获的按钮
        Returns:
            bool: 是否有一键收获的按钮
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.harvest_all_frame, threshold=self.harvest_all_frame_threshold)
        if match_result is not None:        # 有一键收获按钮
            self.logger.info(f"检测到【一键收获】按钮,准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])   # 直接点击中间即可
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【一键收获】按钮, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False

    def check_harvest_one(self, game_frame):
        '''
        检查是否有单个收获按钮
        部分四方格无法一键收获,需要使用单个收获按钮
        Returns:
            bool: 检查是否有单个收获按钮
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.harvest_one_frame, threshold=self.harvest_one_frame_threshold)
        if match_result is not None:        # 有单个收获按钮
            self.logger.info(f"检测到【单个收获】按钮,准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])   # 直接点击中间即可
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【单个收获】按钮, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False

    def check_get_new_seed(self, game_frame):
        '''
        检查是否有获取新种子的提示窗口，有就点击一下关闭
        Returns:
            bool: 是否有获取新种子的按钮
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.get_new_seed_frame, threshold=self.get_new_seed_frame_threshold)
        if match_result is not None:        # 有获取新种子的按钮
            self.logger.info(f"检测到【获得新种子】的提示窗口,准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            self.now_scene = "home"     # 只有在自家地里才会弹出这个窗口
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])   # 直接点击中间即可
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【获得新种子】的提示窗口, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False
        
    def check_level_up(self, game_frame):
        '''
        检查是否升级提示窗口
        Returns:
            bool: 是否有升级提示窗口
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.level_up_frame, threshold=self.level_up_frame_threshold)
        if match_result is not None:        # 有升级提示窗口
            self.logger.info(f"检测到【升级提示】窗口,准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])   # 直接点击中间即可
            # 点击位置要往下偏移一些
            screen_center = (screen_center[0], screen_center[1] + 500)
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【升级提示】窗口, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False

    def check_watering_all(self, game_frame):
        '''
        检查是否有一键浇水按钮
        Returns:
            bool: 是否有一键浇水按钮
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.watering_all_frame, threshold=self.watering_all_frame_threshold)
        if match_result is not None:        # 有一键浇水按钮
            self.logger.info(f"检测到【一键浇水】按钮,准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])   # 直接点击中间即可
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【一键浇水】按钮, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False
        
    def check_remove_all_grass(self, game_frame):
        '''
        检查是否有一键除草按钮
        Returns:
            bool: 是否有一键除草按钮
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.remove_all_grass_frame, threshold=self.remove_all_grass_frame_threshold)
        if match_result is not None:        # 有一键除草按钮
            self.logger.info(f"检测到【一键除草】按钮,准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])   # 直接点击中间即可
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【一键除草】按钮, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False
    
    def check_remove_all_bugs(self, game_frame):
        '''
        检查是否有一键除虫按钮
        Returns:
            bool: 是否有一键除虫按钮
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.remove_all_bugs_frame, threshold=self.remove_all_bugs_frame_threshold)
        if match_result is not None:        # 有一键除虫按钮
            self.logger.info(f"检测到【一键除虫】按钮,准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])   # 直接点击中间即可
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【一键除虫】按钮, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False

    def check_reconnect(self, game_frame):
        '''
        检查是否有重新登录按钮
        Returns:
            bool: 是否有重新登录按钮
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.reconnect_frame, threshold=self.reconnect_frame_threshold)
        if match_result is not None:        # 有重新登录按钮
            self.logger.info(f"检测到【重新登录】按钮,准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])   # 直接点击中间即可
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【重新登录】按钮, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False
    
    def check_can_steal_small(self, game_frame):
        '''
        检查好友按钮上方是否有可偷的标志
        Returns:
            bool: 是否有可偷的标志
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.can_steal_small_frame, threshold=self.can_steal_small_frame_threshold)
        if match_result is not None:        # 有可偷的标志
            self.logger.info(f"检测到【好友可偷】的标志,准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])   # 直接点击中间即可
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【好友可偷】的标志, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False
    
    def check_can_watering_small(self, game_frame):
        '''
        检查好友按钮上方是否有可浇水的标志
        Returns:
            bool: 是否有可浇水的标志
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.can_watering_small_frame, threshold=self.can_watering_small_frame_threshold)
        if match_result is not None:        # 有可浇水的标志
            self.logger.info(f"检测到【好友可浇水】的标志,准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])   # 直接点击中间即可
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【好友可浇水】的标志, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False
    
    def check_can_remove_bugs_small(self, game_frame):
        '''
        检查好友按钮上方是否有可除虫的标志
        Returns:
            bool: 是否有可除虫的标志
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.can_remove_bugs_small_frame, threshold=self.can_remove_bugs_small_frame_threshold)
        if match_result is not None:        # 有可除虫的标志
            self.logger.info(f"检测到【好友可除虫】的标志,准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])   # 直接点击中间即可
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【好友可除虫】的标志, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False

    def check_close_x_small(self, game_frame):
        '''
        检查好友按钮上方是否有可关闭的标志
        Returns:
            bool: 是否有可关闭的标志
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.close_x_small_frame, threshold=self.close_x_small_frame_threshold)
        if match_result is not None:        # 有可关闭的标志
            self.logger.info(f"检测到【好友可关闭】的标志,准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])   # 直接点击中间即可
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【好友可关闭】的标志, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False

    def check_return_farm(self, game_frame):
        '''
        检查是否有返回农场按钮
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.return_farm_frame, threshold=self.return_farm_frame_threshold)
        if match_result is not None:        # 有返回农场按钮
            self.logger.info(f"检测到【返回农场】按钮,准备点击, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            # 将局部坐标转换为屏幕坐标
            screen_center = self.convert_to_screen_coordinate(match_result['center'])   # 直接点击中间即可
            self.click_at_position(screen_center)
            return True
        else:
            self.logger.debug(f"未检测到【返回农场】按钮, 最高置信度：{max_val:.4f} (阈值：{threshold})")
            return False
    
    def check_daily_free(self):
        '''
        检查并尝试领取每日免费礼包
        '''
        # 直接通过游戏画面尺寸相对坐标点击商店查看(453x854->411x193)
        shop_x_pos = self.game_frame_w * 0.907
        shop_y_pos = self.game_frame_h * 0.225
        # 将局部坐标转换为屏幕坐标
        screen_center = self.convert_to_screen_coordinate((shop_x_pos,shop_y_pos))
        self.click_at_position(screen_center)
        time.sleep(1)   # 等待商店页面加载
        # 进入商店页面后点击免费化肥按钮(453x854->128x401)
        free_button_x_pos = self.game_frame_w * 0.282
        free_button_y_pos = self.game_frame_h * 0.469
        screen_center = self.convert_to_screen_coordinate((free_button_x_pos,free_button_y_pos))
        self.click_at_position(screen_center)
        # 点击空白处尝试关闭弹窗(453x854->225x61)
        blank_x_pos = self.game_frame_w * 0.49
        blank_y_pos = self.game_frame_h * 0.07
        screen_center = self.convert_to_screen_coordinate((blank_x_pos,blank_y_pos))
        self.click_at_position(screen_center)
        time.sleep(1)   # 等待空白处点击
        # 点击返回农场按钮(453x854->49x142)
        return_button_x_pos = self.game_frame_w * 0.089
        return_button_y_pos = self.game_frame_h * 0.165
        screen_center = self.convert_to_screen_coordinate((return_button_x_pos,return_button_y_pos))
        self.click_at_position(screen_center)
        time.sleep(1)   # 等待返回农场按钮点击
        return True


    def get_dog_house_position(self, game_frame):
        '''
        获取狗屋的坐标位置，返回 (x, y) 或 None
        '''
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.dog_house_frame, threshold=self.dog_house_frame_threshold)
        if match_result is not None:
            self.logger.debug(f"检测到【狗屋】, 坐标：{match_result['center']}, 置信度：{max_val:.4f} (阈值：{threshold})")
            return match_result['center']
        self.logger.warning(f"未检测到【狗屋】, 最高置信度：{max_val:.4f} (阈值：{threshold})")
        return None

    def plant_seed_v1(self, game_frame, now_field_idx):
        '''
        检查空地并尝试种植种子V1版本
        '''
        # 先定位到狗屋，以狗屋坐标作为基准点，使用相对坐标定位到各块地
        dog_house_center = self.get_dog_house_position(game_frame)
        if dog_house_center is None:
            self.logger.warning(f"未检测到【狗屋】，无法定位空地并种植种子")
            return False

        dog_house_x, dog_house_y = dog_house_center[0], dog_house_center[1]
        self.logger.debug(f"【狗屋】坐标为：{dog_house_x, dog_house_y}")
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

        first_field_pos_x = dog_house_x + FIRST_FIELD_OFFSET_X
        first_field_pos_y = dog_house_y + FIRST_FIELD_OFFSET_Y
        field_offset_x, field_offset_y = field_offset_map[now_field_idx]
        now_field_pos_x = first_field_pos_x + field_offset_x
        now_field_pos_y = first_field_pos_y + field_offset_y
        # 转换为屏幕坐标
        screen_center = self.convert_to_screen_coordinate((now_field_pos_x, now_field_pos_y))
        self.click_at_position(screen_center)
        time.sleep(1)

        # 更新游戏画面
        game_frame = self.screen_capture.get_window_frame()     # 获取游戏画面
        if game_frame is None:
            self.logger.error(f"游戏画面截取失败，请检查游戏是否开启并确保窗口在前台")
            return True

        # 检查是否为未扩建的地
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.close_x_frame, threshold=self.close_x_frame_threshold)
        if match_result is not None:
            self.logger.info(f"检测到第{now_field_idx+1}块地为【未扩建】的地，后续土地不再巡检")
            x_close_center = match_result['center']
            screen_center = self.convert_to_screen_coordinate(x_close_center)
            self.click_at_position(screen_center)
            return False
        else:
            self.logger.debug(f"未检测关闭按钮")

        # 检查是否可以种植种子
        time.sleep(0.2)
        # 略微增加延迟，防止第1-4块地的铲除图标还没有从屏幕外回正时就开始检查导致识别不到
        match_result, max_val, threshold = self.cv_match.match_template(game_frame, self.remove_seed_frame, threshold=self.remove_seed_frame_threshold)
        if match_result is not None:
            self.logger.info(f"第{now_field_idx+1}块地为【已种植】的土地")
            return True
        else:
            self.logger.info(f"第{now_field_idx+1}块地为【未种植】的土地,准备播种")
            # 更新游戏画面，重新获取土地的坐标,防止点击屏幕左侧边缘的土地后，直接点击原来的土地坐标下方位置，导致点到不兼容的4格占地的作物种子
            game_frame = self.screen_capture.get_window_frame()
            dog_house_center = self.get_dog_house_position(game_frame)
            if dog_house_center is None:
                self.logger.warning(f"未检测到【狗屋】，无法定位空地并种植种子")
                return False
            dog_house_x, dog_house_y = dog_house_center[0], dog_house_center[1]
            self.logger.debug(f"【狗屋】坐标为：{dog_house_x, dog_house_y}")
            first_field_pos_x = dog_house_x + FIRST_FIELD_OFFSET_X
            first_field_pos_y = dog_house_y + FIRST_FIELD_OFFSET_Y
            field_offset_x, field_offset_y = field_offset_map[now_field_idx]
            now_field_pos_x = first_field_pos_x + field_offset_x
            now_field_pos_y = first_field_pos_y + field_offset_y
            # 随机向右偏移5-50像素，防止点击到不兼容的4格作物的种子
            seed_x_pos = now_field_pos_x + random.randint(5, 50)
            seed_y_pos = now_field_pos_y + 70
            screen_center = self.convert_to_screen_coordinate((seed_x_pos,seed_y_pos))
            self.click_at_position(screen_center)
            self.logger.info(f"已尝试播种")
            return True
