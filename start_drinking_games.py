import tkinter as tk
from tkinter import font
import sys
import subprocess
import os

class StartScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("飲みゲーム")
        self.root.geometry("700x600")
        self.root.minsize(500, 400)  # 最小サイズを設定
        self.root.configure(bg="#0a0e27")
        self.root.resizable(True, True)  # ウィンドウサイズを変更可能に
        
        # グラデーション背景を作成
        self.create_background()
        
        # ウィンドウサイズ変更時に背景を再描画
        self.root.bind("<Configure>", self.on_window_resize)
    
    def create_background(self):
        """背景を作成"""
        # 既存のキャンバスを削除
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()
        
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # 最小サイズの場合
        if width < 100:
            width = 700
        if height < 100:
            height = 600
        
        self.bg_canvas = tk.Canvas(self.root, bg="#0a0e27", highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, width=width, height=height)
        
        # グラデーション効果
        for i in range(height):
            color_value = 10 + int(20 * (i / height))
            color = f"#{color_value:02x}{min(255, color_value + 50):02x}{min(255, color_value + 100):02x}"
            self.bg_canvas.create_line(0, i, width, i, fill=color)
        
        # ウィンドウメインフレーム（背景の上に配置）
        self.main_frame = tk.Frame(self.root, bg="#0a0e27")
        self.main_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # タイトル
        title_font = font.Font(family="Arial", size=48, weight="bold")
        title_label = tk.Label(self.main_frame, text="🎉 飲みゲーム 🎉", 
                              font=title_font, bg="#0a0e27", fg="#00ff88")
        title_label.pack(pady=40)
        
        # サブタイトル
        subtitle_font = font.Font(family="Arial", size=16)
        subtitle_label = tk.Label(self.main_frame, text="楽しいゲームを選んでください", 
                                 font=subtitle_font, bg="#0a0e27", fg="#00ccff")
        subtitle_label.pack(pady=(0, 60))
        
        # ゲーム選択ボタンフレーム
        button_frame = tk.Frame(self.main_frame, bg="#0a0e27")
        button_frame.pack(pady=20)
        
        # サイコロゲームボタン
        self.create_game_button(button_frame, 
                               "🎲 サイコロゲーム 🎲",
                               "複数のサイコロを振って合計を競う！",
                               self.launch_dice,
                               0)
        
        # カードゲームボタン
        self.create_game_button(button_frame, 
                               "🃏 トランプゲーム 🃏",
                               "トランプをめくってドキドキ！",
                               self.launch_cards,
                               1)
        
        # 終了ボタン
        exit_font = font.Font(family="Arial", size=12)
        exit_button = tk.Button(self.main_frame, text="終了", command=self.exit_app,
                               font=exit_font, bg="#ff3366", fg="#ffffff",
                               padx=30, pady=10, cursor="hand2",
                               activebackground="#ff5588", relief=tk.RAISED, bd=3)
        exit_button.pack(pady=40)
    
    def on_window_resize(self, event):
        """ウィンドウサイズ変更時に背景を再描画"""
        width = event.width
        height = event.height
        
        # グラデーション効果を再描画
        self.bg_canvas.delete("all")
        for i in range(height):
            color_value = 10 + int(20 * (i / height))
            color = f"#{color_value:02x}{min(255, color_value + 50):02x}{min(255, color_value + 100):02x}"
            self.bg_canvas.create_line(0, i, width, i, fill=color)
    
    def create_game_button(self, parent, title, description, command, row):
        """ゲーム選択ボタンを作成"""
        # ボタンフレーム
        btn_frame = tk.Frame(parent, bg="#1a2a4a", relief=tk.RAISED, bd=2)
        btn_frame.grid(row=row, column=0, padx=20, pady=15, sticky="ew", ipady=15)
        parent.grid_columnconfigure(0, weight=1)
        
        # ボタン本体
        button = tk.Button(btn_frame, text=title, command=command,
                          font=font.Font(family="Arial", size=18, weight="bold"),
                          bg="#00cc99", fg="#000000",
                          padx=30, pady=15, cursor="hand2",
                          activebackground="#00ff99", relief=tk.RAISED, bd=3)
        button.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # 説明テキスト
        desc_label = tk.Label(btn_frame, text=description,
                             font=font.Font(family="Arial", size=11),
                             bg="#1a2a4a", fg="#00ffff")
        desc_label.pack(padx=10, pady=(0, 5))
    
    def launch_dice(self):
        """サイコロゲームを起動"""
        self.root.destroy()
        subprocess.run([sys.executable, "dice.py"])
        self.root = tk.Tk()
        self.__init__(self.root)
        self.root.mainloop()
    
    def launch_cards(self):
        """カードゲームを起動"""
        self.root.destroy()
        subprocess.run([sys.executable, "cards.py"])
        self.root = tk.Tk()
        self.__init__(self.root)
        self.root.mainloop()
    
    def exit_app(self):
        """アプリを終了"""
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = StartScreen(root)
    root.mainloop()
