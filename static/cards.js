// カードゲーム用JavaScript

let cardHistory = [];
let cardsFlipped = 0;
let isFlipping = false;  // フリップ中フラグ
const totalCards = 53; // 52 + ジョーカー

const cardContainerEl = document.getElementById('cardContainer');
const cardTextEl = document.getElementById('cardText');
const countTextEl = document.getElementById('countText');
const cardHistoryListEl = document.getElementById('cardHistoryList');
const resetCardBtn = document.getElementById('resetCardBtn');

// カード表示エリアをクリック
cardContainerEl.addEventListener('click', flipCard);

async function flipCard() {
    if (isFlipping) return;  // フリップ中は処理しない
    
    isFlipping = true;
    
    try {
        // サーバーにリクエスト
        const response = await fetch('/api/flip_card', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        const card = result.card;
        
        // フリップアニメーション
        const cardEl = cardContainerEl.querySelector('.card');
        cardEl.style.animation = 'none';
        setTimeout(() => {
            cardEl.style.animation = 'flip 0.6s ease';
        }, 10);
        
        // カード表示を更新
        if (card.suit === 'JOKER') {
            cardEl.innerHTML = `<div class="card-info">
                <div style="font-size: 3rem;">🃏</div>
                <div class="card-rank">JOKER</div>
            </div>`;
            cardEl.style.background = 'linear-gradient(135deg, #9b59b6, #8e44ad)';
        } else {
            const suitColor = (card.suit === '♥' || card.suit === '♦') ? '#e74c3c' : '#2c3e50';
            cardEl.innerHTML = `<div class="card-info">
                <div class="card-suit" style="color: ${suitColor}">${card.suit}</div>
                <div class="card-rank" style="color: ${suitColor}">${card.rank}</div>
            </div>`;
            cardEl.style.background = 'white';
        }
        
        cardEl.classList.add('front');
        
        // テキスト表示
        cardTextEl.textContent = card.suit === 'JOKER' ? 'JOKER 🃏' : `${card.rank}${card.suit}`;
        
        // 累計を更新
        cardsFlipped++;
        countTextEl.textContent = `${cardsFlipped}/${totalCards}`;
        
        // 履歴に追加
        cardHistory.push(card);
        updateCardHistory();
        
        // 音声を再生
        playAudio(result.audio);
        
        // 1秒後にカード表示をリセット（ラグ改善）
        setTimeout(() => {
            resetCardDisplay();
            isFlipping = false;
        }, 1000);
        
    } catch (error) {
        console.error('エラー:', error);
        alert('エラーが発生しました');
        isFlipping = false;
    }
}

// カード表示をリセット
function resetCardDisplay() {
    const cardEl = cardContainerEl.querySelector('.card');
    cardEl.classList.remove('front');
    cardEl.classList.add('back');
    cardEl.innerHTML = '<div class="card-pattern">🎴</div>';
    cardEl.style.background = 'linear-gradient(135deg, #3498db, #2980b9)';
}

// カード履歴を更新
function updateCardHistory() {
    cardHistoryListEl.innerHTML = '';
    
    if (cardHistory.length === 0) {
        cardHistoryListEl.innerHTML = '<p class="empty-message">まだカードをめくっていません</p>';
        return;
    }
    
    cardHistory.forEach((card, idx) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        if (card.suit === 'JOKER') {
            historyItem.textContent = 'JOKER 🃏';
            historyItem.style.color = '#9b59b6';
        } else {
            const suitColor = (card.suit === '♥' || card.suit === '♦') ? '#e74c3c' : '#2c3e50';
            historyItem.textContent = `${card.rank}${card.suit}`;
            historyItem.style.color = suitColor;
        }
        
        cardHistoryListEl.appendChild(historyItem);
    });
}

// リセット
resetCardBtn.addEventListener('click', () => {
    cardHistory = [];
    cardsFlipped = 0;
    cardTextEl.textContent = '-';
    countTextEl.textContent = '0/53';
    resetCardDisplay();
    updateCardHistory();
});

// 音声を再生
function playAudio(audioData) {
    const audio = new Audio(audioData);
    audio.play().catch(err => console.error('音声再生エラー:', err));
}

// CSS アニメーション追加
const style = document.createElement('style');
style.textContent = `
    @keyframes flip {
        0% { transform: rotateY(0deg); }
        50% { transform: rotateY(90deg); }
        100% { transform: rotateY(0deg); }
    }
`;
document.head.appendChild(style);

// 初期表示
resetCardDisplay();
