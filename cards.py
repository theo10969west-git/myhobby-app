import tkinter as tk
from tkinter import font
import random
import threading
import time
import numpy as np
from scipy.io import wavfile
import os
import tempfile
import platform
import subprocess

class CardGame:
    def __init__(self, root):
        self.root = root
        self.root.title("トランプめくりゲーム")
        self.root.geometry("600x700")
        self.root.configure(bg="#1a5c3a")
        
        # スーツと数字の定義
        self.suits = ['♠', '♥', '♦', '♣']
        self.suit_names = {'♠': 'スペード', '♥': 'ハート', '♦': 'ダイヤ', '♣': 'クラブ', 'J': 'ジョーカー'}
        self.suit_colors = {'♠': '#000000', '♥': '#ff0000', '♦': '#ff0000', '♣': '#000000', 'J': '#ff00ff'}
        self.ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        
        # デッキの初期化
        self.deck = [(suit, rank) for suit in self.suits for rank in self.ranks]
        self.deck.append(('J', 'Joker'))  # ジョーカーを1枚追加
        random.shuffle(self.deck)
        self.flipped = []
        self.current_card = None
        
        # タイトル
        title_font = font.Font(family="Arial", size=24, weight="bold")
        title_label = tk.Label(root, text="🎴 トランプめくりゲーム 🎴", 
                               font=title_font, bg="#1a5c3a", fg="#ffffff")
        title_label.pack(pady=20)
        
        # カード表示 Canvas
        self.canvas = tk.Canvas(root, width=300, height=400, bg="#ffffff", 
                                highlightthickness=3, highlightbackground="#ffd700",
                                cursor="hand2")
        self.canvas.pack(pady=20)
        self.canvas.bind("<Button-1>", self.flip_card_event)
        
        # 情報表示
        info_font = font.Font(family="Arial", size=12, weight="bold")
        self.info_label = tk.Label(root, text=f"残り: {len(self.deck)}枚",
                                   font=info_font, bg="#1a5c3a", fg="#ffd700")
        self.info_label.pack(pady=10)
        
        # カード情報表示
        card_font = font.Font(family="Arial", size=14)
        self.card_info_label = tk.Label(root, text="クリックしてカードをめくる",
                                       font=card_font, bg="#1a5c3a", fg="#ffffff")
        self.card_info_label.pack(pady=10)
        
        # リセットボタン
        button_font = font.Font(family="Arial", size=12)
        reset_button = tk.Button(root, text="リセット", command=self.reset_game,
                                font=button_font, bg="#ffd700", fg="#000000",
                                padx=20, pady=10, cursor="hand2")
        reset_button.pack(pady=10)
        
        # 初期描画
        self.draw_card_back()
    
    def draw_card_back(self):
        """カードの裏を描画"""
        self.canvas.delete("all")
        
        # 外枠
        self.canvas.create_rectangle(10, 10, 290, 390, fill="#0052cc", outline="#ffffff", width=3)
        
        # 内枠
        self.canvas.create_rectangle(25, 25, 275, 375, fill="#0066ff", outline="#ffffff", width=2)
        
        # 背景パターン
        for i in range(0, 300, 30):
            for j in range(0, 400, 30):
                self.canvas.create_rectangle(i, j, i + 20, j + 20, fill="#0052cc", outline="#0066ff")
        
        # テキスト
        self.canvas.create_text(150, 190, text="🎴", font=("Arial", 80), fill="#ffd700")
    
    def draw_card_front(self, suit, rank):
        """カードの表を描画"""
        self.canvas.delete("all")
        
        color = self.suit_colors[suit]
        
        # ジョーカーの場合
        if suit == 'J' and rank == 'Joker':
            # カード背景
            self.canvas.create_rectangle(10, 10, 290, 390, fill="#ffffff", outline=color, width=3)
            # 中央にジョーカー表示
            self.canvas.create_text(150, 190, text="🃏", font=("Arial", 150), fill=color)
            self.canvas.create_text(150, 300, text="JOKER", font=("Arial", 28, "bold"), fill=color)
        else:
            # 通常のカード
            # カード背景
            self.canvas.create_rectangle(10, 10, 290, 390, fill="#ffffff", outline=color, width=3)
            
            # 左上のランクとスーツ
            self.canvas.create_text(30, 30, text=rank, font=("Arial", 24, "bold"), 
                                   fill=color, anchor="nw")
            self.canvas.create_text(30, 55, text=suit, font=("Arial", 20), 
                                   fill=color, anchor="nw")
            
            # 右下のランクとスーツ（反転）
            self.canvas.create_text(270, 370, text=rank, font=("Arial", 24, "bold"), 
                                   fill=color, anchor="se")
            self.canvas.create_text(270, 345, text=suit, font=("Arial", 20), 
                                   fill=color, anchor="se")
            
            # 中央のスーツを大きく表示
            self.canvas.create_text(150, 200, text=suit, font=("Arial", 100), fill=color)
    
    
    def generate_card_flip_sound(self):
        """リアルなカードめくり音を生成"""
        sample_rate = 44100
        duration = 0.35  # 秒
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        sound = np.zeros_like(t)
        
        # 最初のシャッ音（低周波ノイズ）
        noise1_mask = t < 0.15
        noise1 = np.random.normal(0, 0.15, np.sum(noise1_mask))
        # ローパスフィルタの代わりに単純に低周波成分を強調
        freq_sweep = 200 + t[noise1_mask] * 300
        noise1 *= np.sin(2 * np.pi * freq_sweep * 0.01)
        
        # フェードエンベロープ
        fade_out1 = np.linspace(1, 0, np.sum(noise1_mask))
        sound[noise1_mask] = noise1 * fade_out1 * 0.3
        
        # 次のシャッ音（中周波）
        noise2_mask = (t >= 0.1) & (t < 0.25)
        noise2 = np.random.normal(0, 0.1, np.sum(noise2_mask))
        freq_sweep2 = 800 + t[noise2_mask] * 400
        noise2 *= np.sin(2 * np.pi * freq_sweep2 * 0.01)
        
        fade_envelope = np.linspace(1, 0.3, np.sum(noise2_mask))
        sound[noise2_mask] += noise2 * fade_envelope * 0.25
        
        # 最後のキツ音（高周波成分）
        high_freq_mask = t >= 0.2
        high_freq = 1200
        high_sound = np.sin(2 * np.pi * high_freq * t[high_freq_mask]) * 0.15
        
        fade_out3 = np.linspace(1, 0, np.sum(high_freq_mask))
        sound[high_freq_mask] += high_sound * fade_out3 * 0.4
        
        # ランダムなクリック音（より現実的な質感）
        for _ in range(3):
            click_pos = np.random.randint(0, len(t) - 1000)
            click_duration = np.random.randint(100, 500)
            sound[click_pos:click_pos + click_duration] += np.random.normal(0, 0.05, click_duration)
        
        # 正規化とクリッピング
        sound = np.clip(sound, -1, 1)
        
        # 16-bit PCMに変換
        sound_int16 = np.int16(sound * 32767)
        
        return sound_int16, sample_rate
    
    def play_card_flip_sound(self):
        """カードをめくる音を再生"""
        def sound_thread():
            try:
                # サウンド生成
                sound_data, sample_rate = self.generate_card_flip_sound()
                
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
                time.sleep(0.5)
                
                # 一時ファイル削除
                try:
                    os.unlink(wav_file)
                except:
                    pass
            except Exception as e:
                print(f"音声再生エラー: {e}")
        
        thread = threading.Thread(target=sound_thread, daemon=True)
        thread.start()
    
    def flip_card_event(self, event):
        """カードをめくるイベント"""
        if not self.deck:
            self.card_info_label.config(text="ゲーム終了！すべてのカードをめくりました", fg="#ffff00")
            return
        
        # カードをめくる音を再生
        self.play_card_flip_sound()
        
        # デッキからカードを取得
        self.current_card = self.deck.pop()
        suit, rank = self.current_card
        self.flipped.append(self.current_card)
        
        # カードを表示
        self.draw_card_front(suit, rank)
        
        # 情報を更新
        if suit == 'J' and rank == 'Joker':
            self.card_info_label.config(text="🃏 JOKER", fg="#ff00ff")
        else:
            suit_name = self.suit_names[suit]
            self.card_info_label.config(text=f"🎴 {rank} {suit_name}", fg="#ffffff")
        self.info_label.config(text=f"残り: {len(self.deck)}枚 | めくった: {len(self.flipped)}枚")
    
    def reset_game(self):
        """ゲームをリセット"""
        self.deck = [(suit, rank) for suit in self.suits for rank in self.ranks]
        self.deck.append(('J', 'Joker'))  # ジョーカーを1枚追加
        random.shuffle(self.deck)
        self.flipped = []
        self.current_card = None
        
        self.draw_card_back()
        self.card_info_label.config(text="クリックしてカードをめくる", fg="#ffffff")
        self.info_label.config(text=f"残り: {len(self.deck)}枚")

if __name__ == "__main__":
    root = tk.Tk()
    game = CardGame(root)
    root.mainloop()
