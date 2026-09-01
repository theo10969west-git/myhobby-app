from flask import Flask, render_template, jsonify, request
import random
import numpy as np
from scipy.io import wavfile
import os
import tempfile
import base64
import io

app = Flask(__name__, template_folder='', static_folder='static')

# 既存のサイコロ音生成関数
def generate_dice_sound():
    """リアルなサイコロのカラカラ音を生成"""
    sample_rate = 44100
    duration = 0.8
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    sound = np.zeros_like(t)
    frequencies = [950, 1100, 850, 1050, 900, 1150]
    
    for i, freq in enumerate(frequencies):
        start_time = i * 0.13
        end_time = start_time + 0.15
        mask = (t >= start_time) & (t < end_time)
        
        fade_in = np.linspace(0, 1, int(sample_rate * 0.02))
        fade_out = np.linspace(1, 0, int(sample_rate * 0.03))
        envelope = np.ones(np.sum(mask))
        
        if len(envelope) > len(fade_in):
            envelope[:len(fade_in)] = fade_in
        if len(envelope) > len(fade_out):
            envelope[-len(fade_out):] = fade_out
        
        component = np.sin(2 * np.pi * freq * t[mask]) * envelope * 0.15
        sound[mask] += component
    
    noise = np.random.normal(0, 0.03, len(t))
    sound += noise * (1 - t / duration)
    
    sound = np.clip(sound, -1, 1)
    sound_int16 = np.int16(sound * 32767)
    
    return sound_int16, sample_rate

def generate_card_flip_sound():
    """リアルなカードめくり音を生成"""
    sample_rate = 44100
    duration = 0.35
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    sound = np.zeros_like(t)
    
    noise1_mask = t < 0.15
    noise1 = np.random.normal(0, 0.15, np.sum(noise1_mask))
    freq_sweep = 200 + t[noise1_mask] * 300
    noise1 *= np.sin(2 * np.pi * freq_sweep * 0.01)
    fade_out1 = np.linspace(1, 0, np.sum(noise1_mask))
    sound[noise1_mask] = noise1 * fade_out1 * 0.3
    
    noise2_mask = (t >= 0.1) & (t < 0.25)
    noise2 = np.random.normal(0, 0.1, np.sum(noise2_mask))
    freq_sweep2 = 800 + t[noise2_mask] * 400
    noise2 *= np.sin(2 * np.pi * freq_sweep2 * 0.01)
    fade_envelope = np.linspace(1, 0.3, np.sum(noise2_mask))
    sound[noise2_mask] += noise2 * fade_envelope * 0.25
    
    high_freq_mask = t >= 0.2
    high_freq = 1200
    high_sound = np.sin(2 * np.pi * high_freq * t[high_freq_mask]) * 0.15
    fade_out3 = np.linspace(1, 0, np.sum(high_freq_mask))
    sound[high_freq_mask] += high_sound * fade_out3 * 0.4
    
    for _ in range(3):
        click_pos = np.random.randint(0, len(t) - 1000)
        click_duration = np.random.randint(100, 500)
        sound[click_pos:click_pos + click_duration] += np.random.normal(0, 0.05, click_duration)
    
    sound = np.clip(sound, -1, 1)
    sound_int16 = np.int16(sound * 32767)
    
    return sound_int16, sample_rate

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dice')
def dice():
    return render_template('dice.html')

@app.route('/cards')
def cards():
    return render_template('cards.html')

@app.route('/api/roll_dice', methods=['POST'])
def roll_dice():
    data = request.json
    num_dice = data.get('num_dice', 1)
    
    # サイコロを振る
    results = [random.randint(1, 6) for _ in range(num_dice)]
    total = sum(results)
    
    # 音声生成
    sound_data, sample_rate = generate_dice_sound()
    
    # WAV データをバイナリに変換してBase64エンコード
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        wav_file = tmp.name
    
    wavfile.write(wav_file, sample_rate, sound_data)
    
    with open(wav_file, 'rb') as f:
        wav_data = f.read()
    
    os.unlink(wav_file)
    
    audio_base64 = base64.b64encode(wav_data).decode('utf-8')
    
    return jsonify({
        'results': results,
        'total': total,
        'audio': f'data:audio/wav;base64,{audio_base64}'
    })

@app.route('/api/flip_card', methods=['POST'])
def flip_card():
    # デッキ（52枚 + ジョーカー）を初期化
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    deck = []
    for suit in suits:
        for rank in ranks:
            deck.append({'rank': rank, 'suit': suit})
    deck.append({'rank': 'J', 'suit': 'JOKER'})
    
    random.shuffle(deck)
    card = deck[0]
    
    # 音声生成
    sound_data, sample_rate = generate_card_flip_sound()
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        wav_file = tmp.name
    
    wavfile.write(wav_file, sample_rate, sound_data)
    
    with open(wav_file, 'rb') as f:
        wav_data = f.read()
    
    os.unlink(wav_file)
    
    audio_base64 = base64.b64encode(wav_data).decode('utf-8')
    
    return jsonify({
        'card': card,
        'audio': f'data:audio/wav;base64,{audio_base64}'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
