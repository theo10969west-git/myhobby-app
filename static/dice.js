// サイコロゲーム用JavaScript

let numDice = 1;
let results = [];
let isRolling = false;

const diceCountEl = document.getElementById('diceCount');
const diceContainerEl = document.getElementById('diceContainer');
const resultTextEl = document.getElementById('resultText');
const totalTextEl = document.getElementById('totalText');
const historyListEl = document.getElementById('historyList');
const decreaseBtn = document.getElementById('decreaseBtn');
const increaseBtn = document.getElementById('increaseBtn');
const rollBtn = document.getElementById('rollBtn');
const resetBtn = document.getElementById('resetBtn');

// サイコロを減らす
decreaseBtn.addEventListener('click', () => {
    if (numDice > 1 && !isRolling) {
        numDice--;
        updateDiceDisplay();
    }
});

// サイコロを増やす
increaseBtn.addEventListener('click', () => {
    if (numDice < 16 && !isRolling) {
        numDice++;
        updateDiceDisplay();
    }
});

// サイコロ表示を更新
function updateDiceDisplay() {
    diceCountEl.textContent = numDice;
    diceContainerEl.innerHTML = '';
    
    for (let i = 0; i < numDice; i++) {
        const diceEl = document.createElement('div');
        diceEl.className = 'dice';
        diceEl.dataset.value = '1';
        diceEl.textContent = '1';
        diceContainerEl.appendChild(diceEl);
    }
}

// サイコロを振る
rollBtn.addEventListener('click', rollDice);

async function rollDice() {
    if (isRolling) return;
    
    isRolling = true;
    rollBtn.disabled = true;
    
    try {
        // サーバーにリクエスト
        const response = await fetch('/api/roll_dice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ num_dice: numDice })
        });
        
        const data = await response.json();
        
        // アニメーション中にランダムな値を表示
        const diceElements = document.querySelectorAll('.dice');
        const animationDuration = 600;
        const frameTime = 50;
        const frames = animationDuration / frameTime;
        
        let frame = 0;
        const animationInterval = setInterval(() => {
            diceElements.forEach((el, idx) => {
                const randomValue = Math.floor(Math.random() * 6) + 1;
                el.textContent = randomValue;
                el.style.animation = 'none';
                setTimeout(() => {
                    el.style.animation = 'bounce 0.3s ease';
                }, 10);
            });
            
            frame++;
            if (frame >= frames) {
                clearInterval(animationInterval);
                
                // 最終結果を表示
                diceElements.forEach((el, idx) => {
                    el.textContent = data.results[idx];
                    el.style.animation = 'bounce 0.5s ease';
                });
                
                // 結果テキストを更新
                const resultStr = data.results.join(' + ');
                resultTextEl.textContent = `${resultStr} = ${data.total}`;
                totalTextEl.textContent = data.total;
                
                // 履歴に追加
                results.push(data.results.slice());
                updateHistory();
                
                // 音声を再生
                playAudio(data.audio);
            }
        }, frameTime);
        
    } catch (error) {
        console.error('エラー:', error);
        alert('エラーが発生しました');
    } finally {
        isRolling = false;
        rollBtn.disabled = false;
    }
}

// 履歴を更新
function updateHistory() {
    historyListEl.innerHTML = '';
    
    if (results.length === 0) {
        historyListEl.innerHTML = '<p class="empty-message">まだ履歴がありません</p>';
        return;
    }
    
    results.forEach((result, idx) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        const sum = result.reduce((a, b) => a + b, 0);
        historyItem.textContent = `${idx + 1}. (${result.join(' + ')}) = ${sum}`;
        historyListEl.appendChild(historyItem);
    });
}

// リセット
resetBtn.addEventListener('click', () => {
    results = [];
    resultTextEl.textContent = '-';
    totalTextEl.textContent = '-';
    updateDiceDisplay();
    updateHistory();
});

// 音声を再生
function playAudio(audioData) {
    const audio = new Audio(audioData);
    audio.play().catch(err => console.error('音声再生エラー:', err));
}

// 初期表示
updateDiceDisplay();
