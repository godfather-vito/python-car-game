import pyxel
import random

class CarGame:
    def __init__(self):
        pyxel.init(400, 400, title="Car Game to SFC")
        pyxel.load("arrowL.pyxres")
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.circles = []
        self.circle_id = 0

        self.lane_x = [random.randint(50, 125), random.randint(125, 200), random.randint(200, 275), random.randint(275, 350)]
        self.line_x = [50, 125, 200, 275, 350]

        self.car_x = 120
        self.car_y = 300
        self.car_speed = 50 
        self.time = 0
        self.score = 0
        self.obstacles = [(random.choice(self.lane_x), random.randint(-80, 0)) for _ in range(3)]
        self.slow_cars = [(random.choice(self.lane_x), random.randint(-80, 0)) for _ in range(2)]
        self.slow_cars2 = (random.choice(self.lane_x), random.randint(-80, 0))

        self.patocar = (random.choice(self.lane_x), random.randint(-80, 0))
        self.game_over = False
        self.game_clear = False
        self.distance = 0



        self.bullets = []
        self.delete = False

        self.yellow_line_index = -1
        self.yellow_line_timer = 0

    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.reset_game()
            return

        self.time += 1
        self.yellow_line_timer += 1

        # Car control
        if pyxel.btn(pyxel.KEY_LEFT):
            self.car_x = max(self.car_x - 2, 0)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.car_x = min(self.car_x + 2, pyxel.width - 16)
        if pyxel.btn(pyxel.KEY_UP):
            self.car_speed = min(self.car_speed + 1, 180)  # 最大180km/h
        if pyxel.btn(pyxel.KEY_DOWN):
            self.car_speed = max(self.car_speed - 1, 50)

        # Shooting bullets
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.bullets.append({'x': self.car_x + 7, 'y': self.car_y - 5})

        # Move bullets
        for bullet in self.bullets:
            bullet['y'] -= 5

        self.bullets = [bullet for bullet in self.bullets if bullet['y'] > 0]

        # Obstacle and slow car movement
        obstacle_speed = 3 + self.car_speed / 50
        for i, (x, y) in enumerate(self.obstacles):
            self.obstacles[i] = (x, y + obstacle_speed)
            if y > pyxel.height:
                self.obstacles[i] = (random.choice(self.lane_x), random.randint(-80, 0))

        slow_car_speed = random.randint(1, 3) + self.car_speed / 100
        for i, (x, y) in enumerate(self.slow_cars):
            self.slow_cars[i] = (x, y + slow_car_speed)
            if y > pyxel.height:
                self.slow_cars[i] = (random.choice(self.lane_x), random.randint(-80, 0))

        slow_car_speed2 = random.randint(1, 3) + self.car_speed / 100
        self.slow_cars2 = (self.slow_cars2[0], self.slow_cars2[1] + slow_car_speed2)
        if self.slow_cars2[1] > pyxel.height:
            self.slow_cars2 = (random.choice(self.lane_x), random.randint(-80, 0))

        patocar_speed = 0.5 + self.car_speed / 100
        self.patocar = (self.patocar[0], self.patocar[1] + patocar_speed)
        if self.patocar[1] > pyxel.height:
            self.patocar = (random.choice(self.lane_x), random.randint(-80, 0))
            if self.delete:
                self.delete = False

        for circle in self.circles:
            circle['y'] += circle['speed']
            if circle['y'] > pyxel.height + circle['radius']:
                # 画面下端を超えた円を削除
                self.circles.remove(circle)
        # 一定の確率で新しい円を追加
        # 辞書の作成
        radius = random.randint(5, 10)
        speed = 10
        r = [random.randint(0, 40), random.randint(360, 400)]
        self.circles.append({
            'id': self.circle_id,
            'x': random.choice(r),
            'y': -radius,
            'radius': radius,
            'speed': speed
        })
        self.circle_id += 1
        # 距離カウント＆道案内（車線）
        self.distance += self.car_speed * 1000 // 108  # 車が１リフレッシュレートで進む距離（m）

        if self.distance > 1199998: #and not self.flag_1199998:

            self.game_clear = True

        # 黄色線の位置変更
        if self.yellow_line_timer >= 15 * 30:
            self.yellow_line_index = random.randint(0, 4)
            self.yellow_line_timer = 0

        # 当たり判定
        for x, y in self.slow_cars:
            if abs(self.car_x - x) < 16 and abs(self.car_y - y) < 16:
                self.game_over = True
        if abs(self.car_x - self.slow_cars2[0]) < 16 and abs(self.car_y - self.slow_cars2[1]) < 16:
            self.game_over = True

        if abs(self.car_x - self.patocar[0]) < 16 and abs(self.car_y - self.patocar[1]) < 16:
            if not self.delete:
                self.game_over = True
        for x, y in self.obstacles:
            if abs(self.car_x - x) < 16 and abs(self.car_y - y) < 16:
                self.game_over = True

        # 弾丸の当たり判定       
        for bullet in self.bullets:
            if abs(self.patocar[0] - bullet['x']) < 16 and abs(self.patocar[1] - bullet['y']) < 16:
                self.delete = True

        # 画面外
        if not 50 < self.car_x < 350:
            self.game_over = True

        # スピード違反
        if self.patocar[1] > self.car_y and self.car_speed > 100:
            if not self.delete:
                self.game_over = True

        # 黄色線を跨いでいるかの判定
        if self.yellow_line_index != -1:
            yellow_line_x = self.line_x[self.yellow_line_index]
            if yellow_line_x - 5 < self.car_x < yellow_line_x + 5:
                self.game_over = True

        # Time over condition
        if self.time > 30 * 30:
            self.game_over = True

    def draw(self):
        pyxel.cls(13)

        pyxel.rect(47, 0, 306, 400, 13)

        # 白線と黄色線の描画
        for i in range(5):
            line_color = 7
            if i == self.yellow_line_index:
                line_color = 10
            pyxel.line(self.line_x[i], 0, self.line_x[i], 400, line_color)
            pyxel.line(self.line_x[i] - 1, 0, self.line_x[i] - 1, 400, line_color)
            pyxel.line(self.line_x[i] + 1, 0, self.line_x[i] + 1, 400, line_color)

        # 自分の車
        pyxel.blt(self.car_x - 13, self.car_y, 0, 62, 0, 28, 45, 0)

        for x, y in self.obstacles:
            pyxel.blt(x, y,0,13, 98, 20, 18, 0)

        for x, y in self.slow_cars:
            pyxel.blt(x, y,0,143,0,26,48,0)

        pyxel.blt(self.slow_cars2[0], self.slow_cars2[1],0,143,0,26,48,0)
        
        pyxel.blt(self.patocar[0], self.patocar[1] - 12, 0,95,0,26,48,0)
        
        if not self.delete:
            pyxel.blt(self.patocar[0] + 5, self.patocar[1] + 12, 0,105, 84, 15,5,0)

        # 弾の描画
        for bullet in self.bullets:
            pyxel.circ(bullet['x'], bullet['y'], 2, 9)

        # 景色の描画
        for circle in self.circles:
            pyxel.rect(circle['x'] - 2, circle['y'] - 15, 12, 10, 4)  # 木の幹
            pyxel.circ(circle['x'], circle['y'], circle['radius'], 11)  # 木の緑の部分
        
        # 情報表示
        pyxel.rect(0, 0, 400, 50, 0)
        pyxel.text(5, 5, f"{self.car_speed}km/h", 7)
        pyxel.text(5, 15, f"Time: {30 - self.time // 30}s", 7)
        pyxel.text(5, 25, f"left: {36-(self.distance*3//100000)}km", 7)
        if ((self.time//30) % 15) > 11:
            pyxel.blt(100, 15,0, 0, 56, 127,16, 0)

        if self.game_over:
            pyxel.text(180, 120, "GAME OVER", pyxel.frame_count % 16)
            pyxel.text(180, 140, "Press 'R' to Restart", 7)

        if self.game_clear:
            pyxel.rect(0, 0, 400, 400, 7)
            pyxel.text(150, 120, "9:25 GAME CLEAR!!!", pyxel.frame_count % 16)

if __name__ == "__main__":
    CarGame()
