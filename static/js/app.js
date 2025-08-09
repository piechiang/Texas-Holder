/**
 * Texas Hold'em Calculator Web App JavaScript
 * 德州扑克计算器网页应用JavaScript代码
 */

class TexasHoldemApp {
    constructor() {
        this.apiUrl = '/api';
        this.isCalculating = false;
        this.presets = {};
        
        this.initializeElements();
        this.bindEvents();
        this.loadPresets();
        this.initializePlayerActions();
        this.ensureInitialState(); // 确保初始状态正确
    }

    initializeElements() {
        // Input elements
        this.holeCard1 = document.getElementById('hole-card-1');
        this.holeCard2 = document.getElementById('hole-card-2');
        this.flopCards = [
            document.getElementById('flop-1'),
            document.getElementById('flop-2'),
            document.getElementById('flop-3')
        ];
        this.turnCard = document.getElementById('turn');
        this.riverCard = document.getElementById('river');
        
        // Settings
        this.numOpponents = document.getElementById('num-opponents');
        this.potSize = document.getElementById('pot-size');
        this.betToCall = document.getElementById('bet-to-call');
        this.simulations = document.getElementById('simulations');
        this.playerPosition = document.getElementById('player-position');
        
        // Player Actions
        this.actionsContainer = document.getElementById('actions-container');
        this.actionPlayer = document.getElementById('action-player');
        this.actionType = document.getElementById('action-type');
        this.actionAmount = document.getElementById('action-amount');
        this.addActionBtn = document.getElementById('add-action-btn');
        this.clearActionsBtn = document.getElementById('clear-actions-btn');
        
        // Check if elements exist before proceeding
        if (!this.actionsContainer || !this.actionPlayer || !this.actionType) {
            console.warn('Player action elements not found, skipping action initialization');
            return;
        }
        
        // Player actions data
        this.playerActions = [];
        this.players = [];
        
        // Buttons
        this.calculateBtn = document.getElementById('calculate-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.presetsBtn = document.getElementById('presets-btn');
        this.helpBtn = document.getElementById('help-btn');
        
        // Results
        this.loading = document.getElementById('loading');
        this.results = document.getElementById('results');
        this.error = document.getElementById('error');
        
        // Modals
        this.presetsModal = document.getElementById('presets-modal');
        this.helpModal = document.getElementById('help-modal');
        
        // Get all card input elements
        this.cardInputs = [
            this.holeCard1, this.holeCard2,
            ...this.flopCards, this.turnCard, this.riverCard
        ];
    }

    bindEvents() {
        // Button events
        this.calculateBtn.addEventListener('click', () => this.calculateProbabilities());
        this.clearBtn.addEventListener('click', () => this.clearAll());
        this.presetsBtn.addEventListener('click', () => this.showPresets());
        this.helpBtn.addEventListener('click', () => this.showHelp());
        
        // Card input validation
        this.cardInputs.forEach(input => {
            input.addEventListener('input', (e) => this.validateCardInput(e.target));
            input.addEventListener('blur', (e) => this.validateCardInput(e.target));
        });
        
        // Modal events
        document.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', () => this.closeModals());
        });
        
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModals();
                }
            });
        });
        
        // Enter key to calculate
        document.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.isCalculating) {
                this.calculateProbabilities();
            }
        });
        
        // ESC key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModals();
            }
        });

        // Player action events (only if elements exist)
        if (this.addActionBtn) {
            this.addActionBtn.addEventListener('click', () => this.addPlayerAction());
        }
        if (this.clearActionsBtn) {
            this.clearActionsBtn.addEventListener('click', () => this.clearPlayerActions());
        }
        if (this.actionType) {
            this.actionType.addEventListener('change', () => this.updateActionAmountVisibility());
        }
        if (this.numOpponents) {
            this.numOpponents.addEventListener('change', () => this.updatePlayerList());
        }
        if (this.playerPosition) {
            this.playerPosition.addEventListener('change', () => this.updatePlayerList());
        }
    }

    validateCardInput(input) {
        const value = input.value.trim().toUpperCase();
        
        if (!value) {
            input.classList.remove('valid', 'invalid');
            return;
        }

        // Basic validation pattern
        const cardPattern = /^(10|[2-9JQKA])[HDCS]$/i;
        
        if (cardPattern.test(value)) {
            // Check for duplicates
            const allValues = this.getAllCardValues();
            const duplicates = allValues.filter(v => v && v.toUpperCase() === value).length;
            
            if (duplicates > 1) {
                input.classList.remove('valid');
                input.classList.add('invalid');
            } else {
                input.classList.remove('invalid');
                input.classList.add('valid');
            }
        } else {
            input.classList.remove('valid');
            input.classList.add('invalid');
        }
    }

    getAllCardValues() {
        return this.cardInputs.map(input => input.value.trim()).filter(v => v);
    }

    async calculateProbabilities() {
        if (this.isCalculating) return;

        // Validate inputs
        const holeCards = [this.holeCard1.value.trim(), this.holeCard2.value.trim()];
        
        if (!holeCards[0] || !holeCards[1]) {
            this.showError('Please enter both hole cards / 请输入两张底牌');
            return;
        }

        // Check for invalid cards
        const invalidCards = this.cardInputs.filter(input => 
            input.value.trim() && input.classList.contains('invalid')
        );
        
        if (invalidCards.length > 0) {
            this.showError('Please fix invalid card formats / 请修正无效的牌面格式');
            return;
        }

        // Collect community cards
        const communityCards = [
            ...this.flopCards.map(input => input.value.trim()),
            this.turnCard.value.trim(),
            this.riverCard.value.trim()
        ].filter(card => card);

        // Prepare request data
        const requestData = {
            hole_cards: holeCards,
            community_cards: communityCards,
            num_opponents: parseInt(this.numOpponents.value),
            pot_size: parseFloat(this.potSize.value),
            bet_to_call: parseFloat(this.betToCall.value),
            num_simulations: parseInt(this.simulations.value),
            player_position: this.playerPosition.value,
            player_actions: this.playerActions
        };

        this.isCalculating = true;
        this.showLoading();

        try {
            const response = await fetch(`${this.apiUrl}/calculate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (data.success) {
                this.displayResults(data);
            } else {
                this.showError(data.error || 'Calculation failed / 计算失败');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Network error. Please try again. / 网络错误，请重试。');
        } finally {
            this.isCalculating = false;
            this.hideLoading();
        }
    }

    displayResults(data) {
        // Hide error
        this.error.classList.add('hidden');

        // Display probability bars
        this.updateProbabilityBar('win', data.probabilities.win_probability);
        this.updateProbabilityBar('tie', data.probabilities.tie_probability);
        this.updateProbabilityBar('lose', data.probabilities.lose_probability);

        // Update simulation count
        document.getElementById('simulations-count').textContent = data.probabilities.simulations.toLocaleString();
        document.getElementById('simulations-count-cn').textContent = data.probabilities.simulations.toLocaleString();

        // Display hand strength
        document.getElementById('hand-description').textContent = data.hand_strength.description || '-';
        document.getElementById('hand-rank').textContent = data.hand_strength.hand_rank || '-';
        
        const strengthScoreDiv = document.getElementById('strength-score-div');
        const strengthScore = document.getElementById('strength-score');
        
        if (data.hand_strength.strength_score !== undefined) {
            strengthScore.textContent = data.hand_strength.strength_score.toFixed(2);
            strengthScoreDiv.style.display = 'block';
        } else {
            strengthScoreDiv.style.display = 'none';
        }

        // Display betting recommendation
        const actionElement = document.getElementById('recommended-action');
        actionElement.textContent = data.betting_advice.recommended_action;
        actionElement.className = `action-badge ${data.betting_advice.recommended_action}`;

        const confidenceElement = document.getElementById('confidence');
        confidenceElement.textContent = data.betting_advice.confidence;
        confidenceElement.className = `confidence-badge ${data.betting_advice.confidence}`;

        document.getElementById('expected-value').textContent = data.betting_advice.expected_value.toFixed(2);
        document.getElementById('pot-odds-display').textContent = (data.betting_advice.pot_odds * 100).toFixed(1) + '%';
        document.getElementById('reasoning-text').textContent = data.betting_advice.reasoning;

        // Show results
        this.results.classList.remove('hidden');
        this.results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    updateProbabilityBar(type, probability) {
        const percentage = (probability * 100).toFixed(1);
        const bar = document.getElementById(`${type}-bar`);
        const label = document.getElementById(`${type}-percentage`);
        
        // Animate the bar
        setTimeout(() => {
            bar.style.width = `${percentage}%`;
        }, 100);
        
        label.textContent = `${percentage}%`;
    }

    showLoading() {
        this.loading.classList.remove('hidden');
        this.results.classList.add('hidden');
        this.calculateBtn.disabled = true;
        this.calculateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calculating... / 计算中...';
    }

    hideLoading() {
        this.loading.classList.add('hidden');
        this.calculateBtn.disabled = false;
        this.calculateBtn.innerHTML = '<i class="fas fa-calculator"></i> Calculate / 计算';
    }

    showError(message) {
        document.getElementById('error-text').textContent = message;
        this.error.classList.remove('hidden');
        this.results.classList.add('hidden');
        this.error.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    clearAll() {
        // Clear all inputs
        this.cardInputs.forEach(input => {
            input.value = '';
            input.classList.remove('valid', 'invalid');
        });

        // Reset settings to defaults
        this.numOpponents.value = '1';
        this.potSize.value = '100';
        this.betToCall.value = '10';
        this.simulations.value = '5000';
        this.playerPosition.value = 'BB';
        
        // Clear player actions
        this.clearPlayerActions();

        // Hide results and errors
        this.results.classList.add('hidden');
        this.error.classList.add('hidden');

        // Focus on first hole card
        this.holeCard1.focus();
    }

    async loadPresets() {
        try {
            const response = await fetch(`${this.apiUrl}/presets`);
            this.presets = await response.json();
        } catch (error) {
            console.error('Error loading presets:', error);
        }
    }

    showPresets() {
        const presetsList = document.getElementById('presets-list');
        presetsList.innerHTML = '';

        Object.entries(this.presets).forEach(([, preset]) => {
            const presetElement = document.createElement('div');
            presetElement.className = 'preset-item';
            presetElement.innerHTML = `
                <div class="preset-name">${preset.name}</div>
                <div class="preset-description">${preset.description}</div>
                <div class="preset-cards">
                    Hole: ${preset.hole_cards.join(' ')} 
                    ${preset.community_cards.length ? `| Community: ${preset.community_cards.join(' ')}` : ''}
                </div>
            `;
            
            presetElement.addEventListener('click', () => {
                this.loadPreset(preset);
                this.closeModals();
            });
            
            presetsList.appendChild(presetElement);
        });

        this.presetsModal.classList.remove('hidden');
        this.presetsModal.style.display = 'flex'; // 确保显示
    }

    loadPreset(preset) {
        // Clear all first
        this.clearAll();

        // Set hole cards
        if (preset.hole_cards.length >= 2) {
            this.holeCard1.value = preset.hole_cards[0];
            this.holeCard2.value = preset.hole_cards[1];
        }

        // Set community cards
        const communityInputs = [...this.flopCards, this.turnCard, this.riverCard];
        preset.community_cards.forEach((card, index) => {
            if (index < communityInputs.length) {
                communityInputs[index].value = card;
            }
        });

        // Validate all cards
        this.cardInputs.forEach(input => {
            if (input.value.trim()) {
                this.validateCardInput(input);
            }
        });

        // Auto-calculate
        setTimeout(() => {
            this.calculateProbabilities();
        }, 500);
    }

    showHelp() {
        this.helpModal.classList.remove('hidden');
        this.helpModal.style.display = 'flex'; // 确保显示
    }

    closeModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.add('hidden');
            modal.style.display = 'none'; // 强制隐藏
        });
        
        // 确保页面可以滚动
        document.body.style.overflow = 'auto';
        
        // 特别处理帮助模态框
        const helpModal = document.getElementById('help-modal');
        if (helpModal) {
            helpModal.classList.add('hidden');
            helpModal.style.display = 'none';
        }
        
        // 特别处理预设模态框
        const presetsModal = document.getElementById('presets-modal');
        if (presetsModal) {
            presetsModal.classList.add('hidden');
            presetsModal.style.display = 'none';
        }
    }

    initializePlayerActions() {
        if (!this.actionsContainer || !this.actionPlayer || !this.actionType) {
            return; // Skip initialization if elements don't exist
        }
        this.updatePlayerList();
        this.updateActionAmountVisibility();
        this.renderPlayerActions(); // 初始化渲染动作列表
    }

    updatePlayerList() {
        const numOpponents = parseInt(this.numOpponents.value);
        this.actionPlayer.innerHTML = '<option value="">Select Player / 选择玩家</option>';
        
        // Add yourself
        const option = document.createElement('option');
        option.value = 'You';
        option.textContent = `You (${this.playerPosition.value}) / 您 (${this.playerPosition.value})`;
        this.actionPlayer.appendChild(option);
        
        // Add opponents
        for (let i = 1; i <= numOpponents; i++) {
            const option = document.createElement('option');
            option.value = `Player${i}`;
            option.textContent = `Player ${i} / 玩家${i}`;
            this.actionPlayer.appendChild(option);
        }
    }

    updateActionAmountVisibility() {
        const actionType = this.actionType.value;
        const amountNeeded = ['raise', 'call'].includes(actionType);
        this.actionAmount.style.display = amountNeeded ? 'block' : 'none';
        
        if (actionType === 'raise') {
            this.actionAmount.placeholder = 'Raise amount / 加注金额';
        } else if (actionType === 'call') {
            this.actionAmount.placeholder = 'Call amount / 跟注金额';
        }
    }

    addPlayerAction() {
        const player = this.actionPlayer.value;
        const actionType = this.actionType.value;
        const amount = this.actionAmount.value ? parseFloat(this.actionAmount.value) : null;
        
        if (!player) {
            alert('Please select a player / 请选择一个玩家');
            return;
        }
        
        if (['raise', 'call'].includes(actionType) && (!amount || amount <= 0)) {
            alert('Please enter a valid amount / 请输入有效金额');
            return;
        }
        
        const action = {
            player: player,
            action: actionType,
            amount: amount,
            timestamp: Date.now()
        };
        
        this.playerActions.push(action);
        this.renderPlayerActions();
        
        // Reset form
        this.actionPlayer.value = '';
        this.actionType.value = 'fold';
        this.actionAmount.value = '';
        this.updateActionAmountVisibility();
    }

    clearPlayerActions() {
        this.playerActions = [];
        this.renderPlayerActions();
    }

    renderPlayerActions() {
        this.actionsContainer.innerHTML = '';
        
        if (this.playerActions.length === 0) {
            this.actionsContainer.innerHTML = '<div class="no-actions">No actions recorded / 暂无动作记录</div>';
            return;
        }
        
        this.playerActions.forEach((action, index) => {
            const actionElement = document.createElement('div');
            actionElement.className = 'action-record';
            
            let actionText = this.getActionText(action);
            
            actionElement.innerHTML = `
                <span class="action-player">${action.player}</span>
                <span class="action-text">${actionText}</span>
                <button class="remove-action-btn" onclick="window.texasHoldemApp.removeAction(${index})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            this.actionsContainer.appendChild(actionElement);
        });
    }

    getActionText(action) {
        const actionTexts = {
            'fold': 'Fold / 弃牌',
            'check': 'Check / 过牌',
            'call': 'Call / 跟注',
            'raise': 'Raise / 加注',
            'all-in': 'All-in / 全下'
        };
        
        let text = actionTexts[action.action] || action.action;
        
        if (action.amount) {
            text += ` (${action.amount})`;
        }
        
        return text;
    }

    removeAction(index) {
        this.playerActions.splice(index, 1);
        this.renderPlayerActions();
    }

    ensureInitialState() {
        // 确保加载提示隐藏
        if (this.loading) {
            this.loading.classList.add('hidden');
        }
        
        // 确保结果和错误信息隐藏
        if (this.results) {
            this.results.classList.add('hidden');
        }
        
        if (this.error) {
            this.error.classList.add('hidden');
        }
        
        // 确保模态框关闭
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.add('hidden');
        });
        
        // 重新绑定模态框关闭事件，确保它们能正常工作
        setTimeout(() => {
            this.rebindModalEvents();
        }, 100);
    }

    rebindModalEvents() {
        // 重新绑定关闭按钮事件
        document.querySelectorAll('.close-modal').forEach(btn => {
            btn.onclick = () => {
                this.closeModals();
            };
        });
        
        // 重新绑定模态框背景点击事件
        document.querySelectorAll('.modal').forEach(modal => {
            modal.onclick = (e) => {
                if (e.target === modal) {
                    this.closeModals();
                }
            };
        });
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.texasHoldemApp = new TexasHoldemApp();
});

// Add some utility functions for card validation
window.cardUtils = {
    isValidRank: (rank) => {
        return /^(10|[2-9JQKA])$/i.test(rank);
    },
    
    isValidSuit: (suit) => {
        return /^[HDCS]$/i.test(suit);
    },
    
    parseCard: (cardStr) => {
        const str = cardStr.trim().toUpperCase();
        if (str.startsWith('10')) {
            return { rank: '10', suit: str.slice(2) };
        } else {
            return { rank: str.slice(0, 1), suit: str.slice(1) };
        }
    },
    
    formatCard: (cardStr) => {
        const card = window.cardUtils.parseCard(cardStr);
        return card.rank + card.suit.toLowerCase();
    }
};