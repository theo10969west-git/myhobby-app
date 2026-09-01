import tkinter as tk
from tkinter import font
from PIL import Image, ImageDraw, ImageTk
import random
import time
import threading
import math
import numpy as np
from scipy.io import wavfile
import os
import tempfile
import platform
import subprocess

class DiceGame:
    def __init__(self, root):
        self.root = root
        self.root.title("サイコロゲーム")
        self.root.geometry("600x800")
        self.root.configure(bg="#2c3e50")
        
        self.results = []
        self.is_rolling = False
        self.num_dice = 1  # サイコロの個数
        self.dice_values = [1]  # 各サイコロの結果
        self.dice_images = []  # サイコロ画像のキャッシュ
        
        # タイトル
        title_font = font.Font(family="Arial", size=24, weight="bold")
        title_label = tk.Label(root, text="🎲 サイコロゲーム 🎲", 
                               font=title_font, bg="#2c3e50", fg="#ecf0f1")
        title_label.pack(pady=15)
        
        # サイコロ個数制御フレーム
        control_frame = tk.Frame(root, bg="#2c3e50")
        control_frame.pack(pady=10)
        
        button_font = font.Font(family="Arial", size=14, weight="bold")
        
        # 「-」ボタン
        minus_button = tk.Button(control_frame, text="◀ -", command=self.decrease_dice,
                                font=button_font, bg="#e74c3c", fg="white",
                                padx=15, pady=8, cursor="hand2")
        minus_button.pack(side=tk.LEFT, padx=10)
        
        # サイコロ数表示
        self.dice_count_label = tk.Label(control_frame, text="サイコロ: 1個",
                                        font=font.Font(family="Arial", size=14, weight="bold"),
                                        bg="#2c3e50", fg="#f39c12", width=15)
        self.dice_count_label.pack(side=tk.LEFT, padx=10)
        
        # 「+」ボタン
        plus_button = tk.Button(control_frame, text="+ ▶", command=self.increase_dice,
                               font=button_font, bg="#27ae60", fg="white",
                               padx=15, pady=8, cursor="hand2")
        plus_button.pack(side=tk.LEFT, padx=10)
        
        # サイコロ表示 Frame
        self.canvas_frame = tk.Frame(root, bg="#34495e", width=550, height=200)
        self.canvas_frame.pack(pady=15, padx=20, fill=tk.BOTH, expand=True)
        
        self.canvas_label = tk.Label(self.canvas_frame, bg="#34495e")
        self.canvas_label.pack(fill=tk.BOTH, expand=True)
        self.canvas_frame.bind("<Button-1>", self.roll_dice)
        self.canvas_label.bind("<Button-1>", self.roll_dice)
        
        # 現在の結果表示
        result_font = font.Font(family="Arial", size=16, weight="bold")
        self.result_label = tk.Label(root, text="クリックしてサイコロを振る！",
                                     font=result_font, bg="#2c3e50", fg="#e74c3c")
        self.result_label.pack(pady=8)
        
        # 合計値表示
        total_font = font.Font(family="Arial", size=18, weight="bold")
        self.total_label = tk.Label(root, text="合計: 0",
                                    font=total_font, bg="#2c3e50", fg="#27ae60")
        self.total_label.pack(pady=8)
        
        # リセットボタン
        button_font2 = font.Font(family="Arial", size=11)
        self.reset_button = tk.Button(root, text="リセット", command=self.reset_game,
                                      font=button_font2, bg="#e74c3c", fg="white",
                                      padx=20, pady=10, cursor="hand2")
        self.reset_button.pack(pady=8)
        
        # 履歴表示
        history_font = font.Font(family="Arial", size=10)
        history_label = tk.Label(root, text="振った結果の履歴:",
                                font=history_font, bg="#2c3e50", fg="#ecf0f1")
        history_label.pack(anchor="w", padx=30, pady=(5, 0))
        
        self.history_label = tk.Label(root, text="",
                                     font=("Arial", 10), bg="#2c3e50", fg="#bdc3c7",
                                     justify=tk.LEFT, wraplength=500)
        self.history_label.pack(anchor="w", padx=30, pady=(0, 5), fill=tk.BOTH, expand=True)
        
        # 初期描画
        self.draw_dices(self.dice_values)
    
    def create_3d_dice_image(self, value, size=80, angle_x=20, angle_y=15):
        """立体的な3D風のサイコロ画像を作成"""
        img = Image.new('RGB', (size, size), color='white')
        draw = ImageDraw.Draw(img)
        
        # サイコロの面の色
        face_colors = {
            'front': '#f39c12',      # 前面（オレンジ）
            'top': '#f9d56e',        # 上面（明るいオレンジ）
            'right': '#d68910'       # 右面（濃いオレンジ）
        }
        
        # サイコロの各面を描画（アイソメトリック図法）
        offset = size // 8
        
        # 左上面（上）
        points_top = [
            (offset, offset),
            (size - offset, offset),
            (size - offset // 2, offset // 2),
            (offset // 2, offset // 2)
        ]
        draw.polygon(points_top, fill=face_colors['top'], outline='#333333', width=2)
        
        # 左下面（前）
        points_front = [
            (offset, offset),
            (offset, size - offset),
            (size - offset, size - offset),
            (size - offset, offset)
        ]
        draw.polygon(points_front, fill=face_colors['front'], outline='#333333', width=2)
        
        # 右側面（右）
        points_right = [
            (size - offset, offset),
            (size - offset // 2, offset // 2),
            (size - offset // 2, size - offset // 2),
            (size - offset, size - offset)
        ]
        draw.polygon(points_right, fill=face_colors['right'], outline='#333333', width=2)
        
        # ドット（目）を描画
        dot_positions = {
            1: [(size // 2, size // 2)],
            2: [(size // 4, size // 4), (3 * size // 4, 3 * size // 4)],
            3: [(size // 4, size // 4), (size // 2, size // 2), (3 * size // 4, 3 * size // 4)],
            4: [(size // 4, size // 4), (3 * size // 4, size // 4), 
                (size // 4, 3 * size // 4), (3 * size // 4, 3 * size // 4)],
            5: [(size // 4, size // 4), (3 * size // 4, size // 4), 
                (size // 2, size // 2), (size // 4, 3 * size // 4), (3 * size // 4, 3 * size // 4)],
            6: [(size // 4, size // 4), (3 * size // 4, size // 4),
                (size // 4, size // 2), (3 * size // 4, size // 2),
                (size // 4, 3 * size // 4), (3 * size // 4, 3 * size // 4)]
        }
        
        dot_radius = max(2, size // 16)
        for x, y in dot_positions[value]:
            draw.ellipse([x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
                        fill='#000000', outline='#000000')
        
        return ImageTk.PhotoImage(img)
    
    def draw_dices(self, dice_values):
        """複数の3D風サイコロを表示"""
        # 表示用の複合画像を作成
        num_dice = len(dice_values)
        available_width = 550  # フレームの利用可能幅
        spacing = 15  # サイコロ間の間隔
        padding = 30  # 両側のパディング
        
        # サイコロのサイズを動的に計算
        # (available_width - padding - spacing*(num_dice-1)) / num_dice
        dice_size = max(40, (available_width - padding - spacing * (num_dice - 1)) // num_dice)
        
        # 総幅を再計算
        total_width = num_dice * dice_size + (num_dice - 1) * spacing + padding
        height = dice_size + 30
        
        # 背景画像を作成
        bg_img = Image.new('RGB', (total_width, height), color='#34495e')
        
        for idx, value in enumerate(dice_values):
            x_pos = padding // 2 + idx * (dice_size + spacing)
            y_pos = (height - dice_size) // 2

            # 各サイコロの画像を作成
            dice_img = Image.new('RGB', (dice_size, dice_size), color='white')
            dice_draw = ImageDraw.Draw(dice_img)
            
            # サイコロの面を描画（アイソメトリック図法）
            offset = dice_size // 8
            
            # 上面
            points_top = [
                (offset, offset),
                (dice_size - offset, offset),
                (dice_size - offset // 2, offset // 2),
                (offset // 2, offset // 2)
            ]
            dice_draw.polygon(points_top, fill='#f9d56e', outline='#333333', width=2)
            
            # 前面
            points_front = [
                (offset, offset),
                (offset, dice_size - offset),
                (dice_size - offset, dice_size - offset),
                (dice_size - offset, offset)
            ]
            dice_draw.polygon(points_front, fill='#f39c12', outline='#333333', width=2)
            
            # 右側面
            points_right = [
                (dice_size - offset, offset),
                (dice_size - offset // 2, offset // 2),
                (dice_size - offset // 2, dice_size - offset // 2),
                (dice_size - offset, dice_size - offset)
            ]
            dice_draw.polygon(points_right, fill='#d68910', outline='#333333', width=2)
            
            # ドット（目）を描画
            dot_positions = {
                1: [(dice_size // 2, dice_size // 2)],
                2: [(dice_size // 4, dice_size // 4), (3 * dice_size // 4, 3 * dice_size // 4)],
                3: [(dice_size // 4, dice_size // 4), (dice_size // 2, dice_size // 2), 
                    (3 * dice_size // 4, 3 * dice_size // 4)],
                4: [(dice_size // 4, dice_size // 4), (3 * dice_size // 4, dice_size // 4), 
                    (dice_size // 4, 3 * dice_size // 4), (3 * dice_size // 4, 3 * dice_size // 4)],
                5: [(dice_size // 4, dice_size // 4), (3 * dice_size // 4, dice_size // 4), 
                    (dice_size // 2, dice_size // 2), (dice_size // 4, 3 * dice_size // 4), 
                    (3 * dice_size // 4, 3 * dice_size // 4)],
                6: [(dice_size // 4, dice_size // 4), (3 * dice_size // 4, dice_size // 4),
                    (dice_size // 4, dice_size // 2), (3 * dice_size // 4, dice_size // 2),
                    (dice_size // 4, 3 * dice_size // 4), (3 * dice_size // 4, 3 * dice_size // 4)]
            }
            
            dot_radius = max(3, dice_size // 14)
            for x, y in dot_positions[value]:
                dice_draw.ellipse([x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
                                 fill='#000000', outline='#000000')
            
            # 背景画像に貼り付け
            bg_img.paste(dice_img, (x_pos, y_pos))
        
        # Tkinter で表示
        photo = ImageTk.PhotoImage(bg_img)
        self.canvas_label.config(image=photo)
        self.canvas_label.image = photo  # 参照を保持
    
    def increase_dice(self):
        """サイコロの個数を増やす"""
        if self.num_dice < 10 and not self.is_rolling:
            self.num_dice += 1
            self.dice_values.append(1)
            self.dice_count_label.config(text=f"サイコロ: {self.num_dice}個")
            self.draw_dices(self.dice_values)
    
    def decrease_dice(self):
        """サイコロの個数を減らす"""
        if self.num_dice > 1 and not self.is_rolling:
            self.num_dice -= 1
            self.dice_values.pop()
            self.dice_count_label.config(text=f"サイコロ: {self.num_dice}個")
            self.draw_dices(self.dice_values)
    
    def generate_dice_sound(self):
        """リアルなサイコロのカラカラ音を生成"""
        sample_rate = 44100
        duration = 0.8  # 秒
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # 複数のパルスとノイズの組み合わせ
        sound = np.zeros_like(t)
        
        # メイン周波数の複数成分
        frequencies = [950, 1100, 850, 1050, 900, 1150]
        
        for i, freq in enumerate(frequencies):
            # それぞれの周波数成分を生成
            start_time = i * 0.13
            end_time = start_time + 0.15
            mask = (t >= start_time) & (t < end_time)
            
            # フェードエンベロープ
            fade_in = np.linspace(0, 1, int(sample_rate * 0.02))
            fade_out = np.linspace(1, 0, int(sample_rate * 0.03))
            envelope = np.ones(np.sum(mask))
            
            if len(envelope) > len(fade_in):
                envelope[:len(fade_in)] = fade_in
            if len(envelope) > len(fade_out):
                envelope[-len(fade_out):] = fade_out
            
            # 各周波数成分を生成
            component = np.sin(2 * np.pi * freq * t[mask]) * envelope * 0.15
            sound[mask] += component
        
        # ランダムノイズの追加（リアルな質感）
        noise = np.random.normal(0, 0.03, len(t))
        sound += noise * (1 - t / duration)  # ノイズをフェードアウト
        
        # 正規化
        sound = np.clip(sound, -1, 1)
        
        # 16-bit PCMに変換
        sound_int16 = np.int16(sound * 32767)
        
        return sound_int16, sample_rate
    
    def play_dice_sound(self):
        """サイコロを振る音を再生（別スレッドで実行）"""
        def sound_thread():
            try:
                # サウンド生成
                sound_data, sample_rate = self.generate_dice_sound()
                
                # 一時ファイルに保存
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                    wav_file = tmp.name
                
                wavfile.write(wav_file, sample_rate, sound_data)
                
                # Windows での再生
                if platform.system() == 'Windows':
                    os.startfile(wav_file, 'play')
                else:
                    # Linux/Mac での再生
                    subprocess.run(['aplay', wav_file], check=False)
                
                # 再生完了を待つ
                time.sleep(1)
                
                # 一時ファイル削除
                try:
                    os.unlink(wav_file)
                except:
                    pass
            except Exception as e:
                print(f"音声再生エラー: {e}")
        
        thread = threading.Thread(target=sound_thread, daemon=True)
        thread.start()
    
    def roll_dice(self, event):
        if self.is_rolling:
            return
        
        self.is_rolling = True
        self.result_label.config(text="振っています...", fg="#f39c12")
        
        # サイコロを振る音を再生
        self.play_dice_sound()
        
        # アニメーション効果
        for _ in range(25):
            random_dice = [random.randint(1, 6) for _ in range(self.num_dice)]
            self.draw_dices(random_dice)
            self.root.update()
            time.sleep(0.04)
        
        # 最終結果
        self.dice_values = [random.randint(1, 6) for _ in range(self.num_dice)]
        self.draw_dices(self.dice_values)
        self.results.append(self.dice_values.copy())
        
        # 結果表示
        total = sum(self.dice_values)
        dice_str = " + ".join(str(d) for d in self.dice_values)
        self.result_label.config(text=f"出た目: {dice_str} = {total}", fg="#e74c3c")
        
        # 合計値表示（全試行の合計）
        all_total = sum(sum(r) for r in self.results)
        self.total_label.config(text=f"合計: {all_total}")
        
        # 履歴更新
        self.update_history()
        
        self.is_rolling = False
    
    def update_history(self):
        history_text = " | ".join(
            "(" + " + ".join(str(d) for d in r) + ")" 
            for r in self.results
        )
        if len(self.results) > 0:
            self.history_label.config(text=history_text)
    
    def reset_game(self):
        self.results = []
        self.dice_values = [1] * self.num_dice
        self.draw_dices(self.dice_values)
        self.result_label.config(text="クリックしてサイコロを振る！", fg="#e74c3c")
        self.total_label.config(text="合計: 0")
        self.history_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    game = DiceGame(root)
    root.mainloop()