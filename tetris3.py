import pyxel
import random

# 画面やブロックなどの定数定義
SCREEN_WIDTH = 160  # 画面幅を増やしてホールド表示スペースを確保
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
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Pyxel Tetris - Hold機能付き")
        self.reset()
        # ゲームのメインループを開始
        pyxel.run(self.update, self.draw)

    def reset(self):
        # 空のフィールドを作成（0は何もない、1はブロック）
        self.field = [[0]*FIELD_WIDTH for _ in range(FIELD_HEIGHT)]
        self.shape_bag = []  # 形のバッグを初期化
        self.next_block = None  # 次のブロックを初期化
        self.hold_block = None  # ホールドブロックを初期化
        self.can_hold = True  # ホールドが使用可能かどうかのフラグ
        self.lines_cleared = 0  # 消したライン数
        # テトリミノの使用回数を初期化（T, O, S, Z, I, J, L の順）
        self.tetrimino_count = [0, 0, 0, 0, 0, 0, 0]
        self.new_block()  # 最初のブロックを出現

    def new_block(self):
        # 形のバッグが空の場合、全ての形をシャッフルして追加
        if not self.shape_bag:
            self.shape_bag = SHAPES[:]
            random.shuffle(self.shape_bag)
        # 次のブロックを設定
        if self.next_block is None:
            self.next_block = self.shape_bag.pop()
        # 現在のブロックを次のブロックに設定し、新しい次のブロックを取得
        self.block, self.color = self.next_block
        self.next_block = self.shape_bag.pop() if self.shape_bag else None
        self.x = FIELD_WIDTH // 2 - len(self.block[0]) // 2
        self.y = 0
        self.can_hold = True  # 新しいブロックが出現したらホールドが再び使用可能
        
        # テトリミノの使用回数をカウント
        tetrimino_index = self.get_tetrimino_index(self.block)
        if tetrimino_index is not None:
            self.tetrimino_count[tetrimino_index] += 1

    def get_tetrimino_index(self, block):
        # ブロックの形からテトリミノのインデックスを取得
        for i, (shape, _) in enumerate(SHAPES):
            if block == shape:
                return i
        return None

    def hold_current_block(self):
        # ホールド機能：現在のブロックをホールドし、ホールドされていたブロックを出現させる
        if not self.can_hold:
            return  # ホールドが使用できない場合は何もしない
        
        current_block = (self.block, self.color)
        
        if self.hold_block is None:
            # ホールドが空の場合、現在のブロックをホールドして新しいブロックを出現
            self.hold_block = current_block
            self.new_block()
        else:
            # ホールドにブロックがある場合、現在のブロックとホールドブロックを交換
            self.block, self.color = self.hold_block
            self.hold_block = current_block
            self.x = FIELD_WIDTH // 2 - len(self.block[0]) // 2
            self.y = 0
        
        self.can_hold = False  # ホールドを使用したので、次のブロックまで使用不可

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
        initial_lines = len(self.field)
        self.field = [row for row in self.field if any(cell == 0 for cell in row)]
        lines_removed = initial_lines - len(self.field)
        self.lines_cleared += lines_removed  # 消したライン数を追加
        
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

        # キー入力処理（左右移動・回転・高速落下・ホールド）
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
        if pyxel.btnp(pyxel.KEY_UP):  # 上キーでホールド
            self.hold_current_block()
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if pyxel.btnp(pyxel.KEY_R):
            self.reset()

    def draw(self):
        # 画面の描画
        pyxel.cls(7)  # 背景を青にクリア
        
        # フィールドの右側に境界線を描画
        pyxel.line(FIELD_WIDTH * BLOCK_SIZE, 0, FIELD_WIDTH * BLOCK_SIZE, FIELD_HEIGHT * BLOCK_SIZE, 0)
        
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

        # 次のブロックを描画
        pyxel.text(FIELD_WIDTH * BLOCK_SIZE + 4, 8, "NEXT", 0)
        if self.next_block:
            for cy, row in enumerate(self.next_block[0]):
                for cx, cell in enumerate(row):
                    if cell:
                        px = (FIELD_WIDTH + cx + 2) * BLOCK_SIZE
                        py = (cy + 2) * BLOCK_SIZE
                        pyxel.rect(px, py, BLOCK_SIZE, BLOCK_SIZE, self.next_block[1])

        # ホールドブロックを描画
        pyxel.text(FIELD_WIDTH * BLOCK_SIZE + 4, 48, "HOLD", 0)
        if self.hold_block:
            # ホールドが使用できない場合は薄い色で表示
            hold_color = self.hold_block[1] if self.can_hold else 5
            for cy, row in enumerate(self.hold_block[0]):
                for cx, cell in enumerate(row):
                    if cell:
                        px = (FIELD_WIDTH + cx + 2) * BLOCK_SIZE
                        py = (cy + 7) * BLOCK_SIZE
                        pyxel.rect(px, py, BLOCK_SIZE, BLOCK_SIZE, hold_color)

        # 右側にスコア表示をまとめて配置
        right_x = FIELD_WIDTH * BLOCK_SIZE + 4
        
        # 操作方法とスコアを下部にまとめて表示
        pyxel.text(right_x, 72, f"LINES: {self.lines_cleared}", 0)
        
        # 合計使用数を表示
        total_count = sum(self.tetrimino_count)
        pyxel.text(right_x, 80, f"TOTAL: {total_count}", 0)
        
        # 操作方法を表示
        pyxel.text(right_x, 88, "UP:HOLD", 0)
        pyxel.text(right_x, 96, "R:RESET", 0)
        pyxel.text(right_x, 104, "Q:QUIT", 0)

# ゲーム開始！
Tetris()
