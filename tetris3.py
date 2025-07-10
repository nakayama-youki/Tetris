import pyxel
import random

# 画面やブロックなどの定数定義
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 120
BLOCK_SIZE = 8  # ブロックサイズ（ピクセル）
FIELD_WIDTH = 10  # フィールド幅（ブロック数）
FIELD_HEIGHT = 15  # フィールド高さ（ブロック数）

# テトリスの形（7種類）と色
SHAPES = [
    ([[1, 1, 1],
      [0, 1, 0]], 9),  # T字型
    ([[1, 1],
      [1, 1]], 10),     # 四角型
    ([[1, 1, 0],
      [0, 1, 1]], 11),  # S字型
    ([[0, 1, 1],
      [1, 1, 0]], 12),  # Z字型
    ([[1, 1, 1, 1]], 13),  # I字型
    ([[1, 0, 0],
      [1, 1, 1]], 14),  # J字型
    ([[0, 0, 1],
      [1, 1, 1]], 15)   # L字型
]

class Tetris:
    def __init__(self):
        # Pyxelの初期化
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Pyxel Tetris")
        self.reset()
        # ゲームのメインループを開始
        pyxel.run(self.update, self.draw)

    def reset(self):
        # 空のフィールドを作成（0は何もない、1はブロック）
        self.field = [[0]*FIELD_WIDTH for _ in range(FIELD_HEIGHT)]
        self.shape_bag = []  # 形のバッグを初期化
        self.new_block()  # 最初のブロックを出現

    def new_block(self):
        # 形のバッグが空の場合、全ての形をシャッフルして追加
        if not self.shape_bag:
            self.shape_bag = SHAPES[:]
            random.shuffle(self.shape_bag)
        # バッグから1つ取り出して現在のブロックに設定
        self.block, self.color = self.shape_bag.pop()
        self.x = FIELD_WIDTH // 2 - len(self.block[0]) // 2
        self.y = 0

    def check_collision(self, dx, dy, shape=None):
        # 衝突チェック（左右・下方向・回転時など）
        shape = shape or self.block
        for cy, row in enumerate(shape):
            for cx, cell in enumerate(row):
                if cell:
                    nx, ny = self.x + cx + dx, self.y + cy + dy
                    if (nx < 0 or nx >= FIELD_WIDTH or ny >= FIELD_HEIGHT or 
                        (ny >= 0 and self.field[ny][nx])):
                        return True
        return False

    def fix_block(self):
        # ブロックをフィールドに固定
        for cy, row in enumerate(self.block):
            for cx, cell in enumerate(row):
                if cell and self.y + cy >= 0:
                    self.field[self.y + cy][self.x + cx] = self.color
        self.clear_lines()  # 揃ったラインを消す
        self.new_block()    # 次のブロックを出現

    def clear_lines(self):
        # ラインが揃っているかチェックし、削除
        self.field = [row for row in self.field if any(cell == 0 for cell in row)]
        # 削除したぶん上に空行を追加
        while len(self.field) < FIELD_HEIGHT:
            self.field.insert(0, [0]*FIELD_WIDTH)

    def rotate(self):
        # ブロックを回転させる（行列の転置＋反転）
        rotated = [list(reversed(col)) for col in zip(*self.block)]
        if not self.check_collision(0, 0, rotated):
            self.block = rotated

    def reverse_rotate(self):
        # ブロックを逆回転させる（回転の動きを3回繰り返す）
        for _ in range(3):
            reversed_rotated = [list(col) for col in zip(*reversed(self.block))]
            if not self.check_collision(0, 0, reversed_rotated):
                self.block = reversed_rotated

    def hard_drop(self):
        # ブロックを一気に下まで落とす
        while not self.check_collision(0, 1):
            self.y += 1
        self.fix_block()

    def update(self):
        # フレームごとに落下処理（30フレームごと）
        if pyxel.frame_count % 30 == 0:
            if not self.check_collision(0, 1):
                self.y += 1
            else:
                self.fix_block()

        # キー入力処理（左右移動・回転・高速落下）
        if pyxel.btnp(pyxel.KEY_A):
            if not self.check_collision(-1, 0):
                self.x -= 1
        if pyxel.btnp(pyxel.KEY_D):
            if not self.check_collision(1, 0):
                self.x += 1
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.reverse_rotate()
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.rotate()
        if pyxel.btnp(pyxel.KEY_S):
            if not self.check_collision(0, 1):
                self.y += 1
        if pyxel.btnp(pyxel.KEY_W):
            self.hard_drop()
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    def draw(self):
        # 画面の描画
        pyxel.cls(0)  # 背景を黒にクリア
        # 固定されたフィールドのブロックを描画
        for y, row in enumerate(self.field):
            for x, cell in enumerate(row):
                if cell:
                    pyxel.rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, cell)

        # 現在の操作ブロックを描画
        for cy, row in enumerate(self.block):
            for cx, cell in enumerate(row):
                if cell:
                    px = (self.x + cx) * BLOCK_SIZE
                    py = (self.y + cy) * BLOCK_SIZE
                    pyxel.rect(px, py, BLOCK_SIZE, BLOCK_SIZE, self.color)

# ゲーム開始！
Tetris()