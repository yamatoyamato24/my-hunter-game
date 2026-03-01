import pygame
import asyncio
import math

# --- 天気を取得する関数 ---
def get_real_weather():
    # デフォルトは晴れ
    result = "Snow"
    try:
        import requests
        # ここにご自身のキーを入れてください
        api_key = "0a33b88275e1a3a4034a80ab8909f3cf" 
        city = "Kobe"
        # タイムアウトを極短（0.5秒）にして、ネットが遅くてもゲームを優先する
        response = requests.get(f"http://api.openweathermap.org{city}&appid={api_key}", timeout=0.5)
        if response.status_code == 200:
            result = response.json()["weather"][0]["main"] # [0]が必要な場合があります
    except:
        pass # 失敗したらClearのまま
    return result

# --- 画像読み込み関数（縦横比を維持） ---
def load_game_image(path, target_width):
    try:
        img = pygame.image.load(path).convert_alpha()
        org_width, org_height = img.get_size()
        aspect_ratio = org_height / org_width
        target_height = int(target_width * aspect_ratio)
        return pygame.transform.scale(img, (target_width, target_height))
    except:
        surf = pygame.Surface((target_width, target_width))
        surf.fill((200, 200, 200))
        return surf

class Player:
    def __init__(self):
        self.image = load_game_image("assets/run_away.png", 60)
        self.rect = self.image.get_rect(center=(400, 300))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 10
        self.hp = 3
        self.invincible_timer = 0 

    def update(self, move_vec=(0, 0)):
        # キーボード操作
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:    self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:  self.rect.y += self.speed
        if keys[pygame.K_LEFT]:  self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]: self.rect.x += self.speed

        # タッチ操作（引数で移動ベクトルを受け取る）
        self.rect.x += move_vec[0] * self.speed
        self.rect.y += move_vec[1] * self.speed

        # 画面の下端(1500)まで動けるように修正
        self.rect.clamp_ip(pygame.Rect(0, 0, 800, 1500))

        if self.invincible_timer > 0: 
            self.invincible_timer -= 1

        

        self.rect.clamp_ip(pygame.Rect(0, 0, 800, 1500))

    def draw(self, screen):
        # 無敵時間中（ダメージを受けた後）の演出
        if self.invincible_timer > 0:
            # 10フレームごとに点滅（チカチカさせる）
            if self.invincible_timer % 10 < 5: 
                # 1. 画像のコピーを作る（元の画像を変えないため）
                temp_image = self.image.copy()
                
                # 2. 赤色で塗りつぶして合成する
                # (255, 100, 100) は少し明るい赤。真っ赤なら (255, 0, 0)
                temp_image.fill((255, 150, 150), special_flags=pygame.BLEND_RGBA_MULT)
                
                # 3. 赤くなった画像を表示
                screen.blit(temp_image, self.rect)
        else:
            # 通常時はそのまま表示
            screen.blit(self.image, self.rect)

class Enemy:
    def __init__(self):
        self.image = load_game_image("assets/enemy.png", 300)
        self.rect = self.image.get_rect(topleft=(20, 20))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 5

    def update(self, player_rect):
        if self.rect.x < player_rect.x: self.rect.x += self.speed
        if self.rect.x > player_rect.x: self.rect.x -= self.speed
        if self.rect.y < player_rect.y: self.rect.y += self.speed
        if self.rect.y > player_rect.y: self.rect.y -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Background:
    def __init__(self):
        # 最初に真っ新なキャンバスを作る（サイズを800x1500に強制固定）
        self.image = pygame.Surface((800, 1500))
        
        # 天気を取得して色を決める
        # 起動時に天気を取得
        self.weather = get_real_weather()
        
        # 天気色の設定
        colors = {
            "Clear": (135, 206, 235),  # 晴れ
            "Clouds": (169, 169, 169), # くもり
            "Rain": (70, 70, 90),      # 雨
            "Snow": (240, 248, 255),   # 雪
            "Drizzle": (70, 70, 90)    # 霧雨（雨と同じにする）
        }
        self.base_color = colors.get(self.weather, (34, 139, 34))

        try:
            raw_img = pygame.image.load("assets/background.png").convert()
            # ここでサイズを強制的に 800x1500 にリサイズ
            self.image = pygame.transform.scale(raw_img, (800, 1500))
            
            # 画像の上に天気の色の「薄い膜」を乗せる（サイズ崩れ防止）
            overlay = pygame.Surface((800, 1500), pygame.SRCALPHA)
            overlay.fill((*self.base_color, 80)) # 80は透明度。薄く色を付ける
            self.image.blit(overlay, (0, 0))
        except:
            # 画像がない場合は単色で塗りつぶし
            self.image.fill(self.base_color)
            
        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # 描画位置も (0, 0) に固定
        screen.blit(self.image, (0, 0))

class Controller:
    def get_move_vector(self):
        m_pos = pygame.mouse.get_pos()
        m_pressed = pygame.mouse.get_pressed()[0]
        if not m_pressed: return (0, 0)

        dx = m_pos[0] - self.cx
        dy = m_pos[1] - self.cy
        dist = math.sqrt(dx**2 + dy**2)

        # パッドの範囲内なら、正規化（1か-1など）した方向を返す
        if 10 < dist < self.pad_radius:
            return (dx/dist, dy/dist) # 斜め移動もスムーズになります
        return (0, 0)

    def __init__(self):
        # 画面の下の方（y=1200あたり）に配置
        self.cx, self.cy = 400, 1200 
        self.pad_radius = 220 
        self.font = pygame.font.SysFont(None, 70)

    def draw(self, screen):
        # 1500の画面全体を覆うSurface
        pad_surf = pygame.Surface((800, 1500), pygame.SRCALPHA)
        m_pos = pygame.mouse.get_pos()
        m_pressed = pygame.mouse.get_pressed()[0] # 左クリック/タッチ

        # 1. 土台の丸（暗いグレー）
        pygame.draw.circle(pad_surf, (40, 40, 40, 150), (self.cx, self.cy), self.pad_radius)

        # 2. 扇状の「光」の描画
        if m_pressed:
            dx = m_pos[0] - self.cx
            dy = m_pos[1] - self.cy
            dist_sq = dx**2 + dy**2
            
            # 半径の範囲内なら、触っている角度を計算
            if 10**2 < dist_sq < self.pad_radius**2:
                import math
                # 角度（ラジアン）を取得 (-π to π)
                angle = math.atan2(dy, dx)
                
                # 触っている方向を扇状に光らせる (黄色)
                # 45度(π/4)ずつの範囲で描画
                start_angle = (math.floor((angle + math.pi/8) / (math.pi/4)) * (math.pi/4)) - math.pi/8
                points = [
                    (self.cx, self.cy),
                    (self.cx + math.cos(start_angle) * self.pad_radius, self.cy + math.sin(start_angle) * self.pad_radius),
                    (self.cx + math.cos(start_angle + math.pi/4) * self.pad_radius, self.cy + math.sin(start_angle + math.pi/4) * self.pad_radius)
                ]
                pygame.draw.polygon(pad_surf, (255, 255, 0, 150), points)

        # 3. 扇状の「白い枠線」を描く
        import math
        for i in range(8):
            angle = i * (math.pi / 4) + math.pi/8
            # 中心から外側へ引く境界線
            end_x = self.cx + math.cos(angle) * self.pad_radius
            end_y = self.cy + math.sin(angle) * self.pad_radius
            pygame.draw.line(pad_surf, (255, 255, 255, 100), (self.cx, self.cy), (end_x, end_y), 2)

        # 4. 外枠のリング
        pygame.draw.circle(pad_surf, (255, 255, 255, 200), (self.cx, self.cy), self.pad_radius, 5)
        # 中心に小さな円（飾り）
        pygame.draw.circle(pad_surf, (255, 255, 255, 200), (self.cx, self.cy), 10)

        # 5. 矢印のガイド表示
        arrows = [("▲", 0, -150), ("▼", 0, 150), ("◀", -150, 0), ("▶", 150, 0)]
        for arrow, ox, oy in arrows:
            txt = self.font.render(arrow, True, (255, 255, 255, 180))
            pad_surf.blit(txt, txt.get_rect(center=(self.cx + ox, self.cy + oy)))

        screen.blit(pad_surf, (0, 0))

    def get_input(self):
        mouse_pos = pygame.mouse.get_pos()
        # [0]を付けて左クリック/タップのみ判定
        mouse_pressed = pygame.mouse.get_pressed()[0]
        res = {"up": False, "down": False, "left": False, "right": False}
        
        if mouse_pressed:
            # 配列のインデックス指定で計算（エラー防止）
            dx = mouse_pos[0] - self.cx
            dy = mouse_pos[1] - self.cy
            dist_sq = dx**2 + dy**2

            # 遊び（中心の無反応地帯）を作って誤操作防止
            # パッドの円内に指があるか判定
            if 10**2 < dist_sq < self.pad_radius**2:
                # 角度（度数法）に変換
                import math
                deg = math.degrees(math.atan2(dy, dx))
                
                # --- 45度ずつの範囲で8方向を判定 ---
                
                # 右 ( -22.5 〜 22.5 )
                if -22.5 < deg <= 22.5:
                    res["right"] = True
                # 右下 ( 22.5 〜 67.5 )
                elif 22.5 < deg <= 67.5:
                    res["right"] = True
                    res["down"] = True
                # 下 ( 67.5 〜 112.5 )
                elif 67.5 < deg <= 112.5:
                    res["down"] = True
                # 左下 ( 112.5 〜 157.5 )
                elif 112.5 < deg <= 157.5:
                    res["left"] = True
                    res["down"] = True
                # 左 ( 157.5以上 または -157.5以下 )
                elif deg > 157.5 or deg <= -157.5:
                    res["left"] = True
                # 左上 ( -157.5 〜 -112.5 )
                elif -157.5 < deg <= -112.5:
                    res["left"] = True
                    res["up"] = True
                # 上 ( -112.5 〜 -67.5 )
                elif -112.5 < deg <= -67.5:
                    res["up"] = True
                # 右上 ( -67.5 〜 -22.5 )
                elif -67.5 < deg <= -22.5:
                    res["right"] = True
                    res["up"] = True

        return res

async def play_game(screen):
    # ★開始直後に一瞬だけ休ませる（ブラウザの読み込み待ち）
    await asyncio.sleep(0.1) 

    # --- フォント読み込み（ここで1回だけ行う） ---
    try:
        font_path = "assets/NotoSansJP-Regular.ttf"
        font_msg = pygame.font.Font(font_path, 80)   
        font_ui = pygame.font.Font(font_path, 40)    
        font_count = pygame.font.Font(font_path, 150) 
    except:
        font_msg = pygame.font.SysFont(None, 80)
        font_ui = pygame.font.SysFont(None, 40)
        font_count = pygame.font.SysFont(None, 150)

    # --- ゲーム用BGMの再生 ---
    try:
        pygame.mixer.music.load("assets/game_bgm.ogg")
        pygame.mixer.music.play(-1)
    except:
        pass

    # クラスの初期化
    bg = Background()
    player = Player()
    enemy = Enemy()
    controller = Controller()
    
    clock = pygame.time.Clock()
    score = 0
    speed_up_timer = 0 
    last_speed_check = 0 
    
    # 【修正ポイント】ここにあった SysFont(None, ...) の再定義を削除しました
    # これで上の日本語フォントがそのまま使われます
    
    start_ticks = pygame.time.get_ticks()

    while True:
        countdown = 3 - (pygame.time.get_ticks() - start_ticks) // 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT", 0
        
        # 入力を受け取る
        ctrl = controller.get_input()

        if countdown <= 0:
            # 十字キー/タップ操作の反映
            if ctrl["up"]:    player.rect.y -= player.speed
            if ctrl["down"]:  player.rect.y += player.speed
            if ctrl["left"]:  player.rect.x -= player.speed
            if ctrl["right"]: player.rect.x += player.speed
            
            player.update()
            enemy.update(player.rect)
            
            score += 1 / 60
            current_sec = int(score)

            # ★【追加】25秒でゲームクリア判定
            if current_sec >= 25:
                pygame.mixer.music.stop() # 音楽を止める
                await asyncio.sleep(0.5)  # クリアの余韻
                return "CLEAR", current_sec # "CLEAR" という状態を返す

            # スピードアップ処理
            if current_sec > 0 and current_sec % 10 == 0 and current_sec != last_speed_check:
                speed_up_timer = 90      
                last_speed_check = current_sec 

            # スコアに合わせて敵の速度を更新
            enemy.speed = 5 + (current_sec // 10)

        # 当たり判定
        offset_x = enemy.rect.x - player.rect.x
        offset_y = enemy.rect.y - player.rect.y
        if player.mask.overlap(enemy.mask, (offset_x, offset_y)) and player.invincible_timer <= 0:
            player.hp -= 1
            player.invincible_timer = 60
            if player.hp <= 0:
                pygame.mixer.music.stop()
                await asyncio.sleep(0.5)
                return "GAMEOVER", int(score)

        # --- 描画処理 ---
        bg.draw(screen)
        player.draw(screen)
        enemy.draw(screen)
        controller.draw(screen)

        # スピードアップ演出
        if speed_up_timer > 0:
            msg_surf = pygame.Surface((800, 100), pygame.SRCALPHA)
            msg_surf.fill((50, 50, 50, 180)) 
            screen.blit(msg_surf, (0, 450))
            
            # 日本語フォントで描画
            txt = font_msg.render("スピードアップ！！", True, (255, 255, 0)) 
            screen.blit(txt, txt.get_rect(center=(400, 500)))
            speed_up_timer -= 1 

        # UI表示
        txt_ui = font_ui.render(f"体力:{player.hp}  スコア:{int(score)}秒", True, (255,255,255))
        screen.blit(txt_ui, (20,20))

        # カウントダウン演出
        if countdown > 0:
            overlay = pygame.Surface((800, 1500), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            count_surf = font_count.render(str(countdown), True, (255, 215, 0))
            screen.blit(count_surf, count_surf.get_rect(center=(400, 500)))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
