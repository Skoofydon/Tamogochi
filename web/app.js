// Инициализация Telegram Web App
const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();
tg.setHeaderColor('#1a1a2e');
tg.setBackgroundColor('#1a1a2e');

// Состояние игры
class TamagochiGame {
    constructor() {
        this.stats = {
            energy: 100,
            food: 100,
            mood: 80,
            study: 0
        };
        
        this.coins = 100;
        this.level = 1;
        this.experience = 0;
        this.studentName = 'Студент';
        this.status = '😊';
        this.isSleeping = false;
        this.sleepTimer = null;
        this.foodItems = ['🍎', '🍕', '🥪'];
        this.booksCount = 2;
        
        this.events = [];
        this.maxEvents = 8;
        
        this.STAT_DECAY_RATE = 0.5;
        this.MAX_STAT = 100;
        this.EAT_COST = 5;
        this.EAT_GAIN = 30;
        this.SLEEP_GAIN = 50;
        this.STUDY_GAIN = 15;
        this.WORK_COINS = 20;
        this.STEAL_SUCCESS_RATE = 0.4;
        this.PARTY_MOOD_GAIN = 40;
        
        this.init();
    }
    
    init() {
        if (tg.initDataUnsafe?.user?.first_name) {
            this.studentName = tg.initDataUnsafe.user.first_name;
        }
        
        this.loadGame();
        this.updateUI();
        this.startDecay();
        this.bindEvents();
        
        this.addEvent('🎓 Добро пожаловать в общагу!');
    }
    
    bindEvents() {
        document.querySelectorAll('[data-action]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = btn.dataset.action;
                if (action === 'save') {
                    this.sendDataToBot();
                } else {
                    this.handleAction(action);
                }
            });
        });
        
        document.querySelectorAll('.menu-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.menu-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.showTab(btn.dataset.tab);
            });
        });
        
        document.getElementById('modalClose').addEventListener('click', () => {
            document.getElementById('modal').classList.remove('show');
        });
        
        document.getElementById('modalBtn').addEventListener('click', () => {
            document.getElementById('modal').classList.remove('show');
        });
    }
    
    handleAction(action) {
        if (this.isSleeping && action !== 'sleep') {
            this.showModal('😴 Спишь', 'Ты сейчас спишь. Нажми "Поспать" чтобы проснуться.');
            return;
        }
        
        switch(action) {
            case 'eat': this.eat(); break;
            case 'sleep': this.sleep(); break;
            case 'study': this.study(); break;
            case 'work': this.work(); break;
            case 'steal': this.steal(); break;
            case 'party': this.party(); break;
        }
        
        this.updateUI();
        this.saveGame();
    }
    
    eat() {
        if (this.coins < this.EAT_COST) {
            this.showModal('💰 Нет денег', 'Иди подработай!');
            return;
        }
        
        if (this.stats.food >= this.MAX_STAT) {
            this.addEvent('🍔 Ты уже сыт!');
            return;
        }
        
        this.coins -= this.EAT_COST;
        this.stats.food = Math.min(this.MAX_STAT, this.stats.food + this.EAT_GAIN);
        this.stats.mood = Math.min(this.MAX_STAT, this.stats.mood + 5);
        
        this.updateFoodItems();
        this.addEvent(`🍽️ Вкусно поел. +${this.EAT_GAIN} сытости`);
        this.updateStatus();
    }
    
    sleep() {
        if (this.isSleeping) {
            this.isSleeping = false;
            clearTimeout(this.sleepTimer);
            document.getElementById('sleepZ').classList.remove('active');
            
            this.stats.energy = Math.min(this.MAX_STAT, this.stats.energy + this.SLEEP_GAIN);
            this.stats.mood = Math.min(this.MAX_STAT, this.stats.mood + 10);
            
            this.addEvent(`😊 Проснулся бодрым! +${this.SLEEP_GAIN} энергии`);
            this.updateStatus();
            
            document.querySelector('[data-action="sleep"] .btn-text').textContent = 'Поспать';
            document.querySelector('[data-action="sleep"] .btn-time').textContent = '3ч';
        } else {
            if (this.stats.energy >= this.MAX_STAT) {
                this.addEvent('⚡ Не хочется спать');
                return;
            }
            
            this.isSleeping = true;
            document.getElementById('sleepZ').classList.add('active');
            
            this.addEvent('😴 Ушёл спать...');
            this.updateStatus();
            
            document.querySelector('[data-action="sleep"] .btn-text').textContent = 'Проснуться';
            document.querySelector('[data-action="sleep"] .btn-time').textContent = '';
            
            this.sleepTimer = setTimeout(() => {
                if (this.isSleeping) this.sleep();
            }, 3000);
        }
    }
    
    study() {
        if (this.stats.energy < 10) {
            this.showModal('😫 Нет сил', 'Слишком устал, поспи сначала');
            return;
        }
        
        if (this.stats.food < 10) {
            this.showModal('🤤 Голоден', 'Надо поесть перед учёбой');
            return;
        }
        
        this.stats.energy = Math.max(0, this.stats.energy - 10);
        this.stats.food = Math.max(0, this.stats.food - 10);
        this.stats.study = Math.min(this.MAX_STAT, this.stats.study + this.STUDY_GAIN);
        this.stats.mood = Math.max(0, this.stats.mood - 5);
        
        this.experience += 10;
        this.checkLevelUp();
        
        this.booksCount = Math.min(5, this.booksCount + 1);
        this.updateBooks();
        
        this.addEvent(`📚 Позанимался. +${this.STUDY_GAIN} к учёбе, +10 XP`);
        this.updateStatus();
    }
    
    work() {
        if (this.stats.energy < 20) {
            this.showModal('😫 Устал', 'Нет сил работать');
            return;
        }
        
        this.stats.energy = Math.max(0, this.stats.energy - 20);
        this.stats.food = Math.max(0, this.stats.food - 5);
        this.stats.mood = Math.max(0, this.stats.mood - 10);
        
        const earned = this.WORK_COINS + Math.floor(Math.random() * 15);
        this.coins += earned;
        
        this.addEvent(`💼 Подработал курьером. +${earned}🪙`);
        this.updateStatus();
    }
    
    steal() {
        if (this.stats.energy < 15) {
            this.showModal('😴 Нет сил', 'Слишком устал для такого');
            return;
        }
        
        this.stats.energy = Math.max(0, this.stats.energy - 15);
        
        const success = Math.random() < this.STEAL_SUCCESS_RATE;
        
        if (success) {
            const foodFound = ['🍗', '🥟', '🍜', '🥖', '🧀'];
            const item = foodFound[Math.floor(Math.random() * foodFound.length)];
            this.foodItems.push(item);
            
            this.stats.food = Math.min(this.MAX_STAT, this.stats.food + 25);
            this.stats.mood = Math.min(this.MAX_STAT, this.stats.mood + 15);
            
            this.updateFoodItems();
            this.addEvent(`🥷 Стырил ${item} из общего холодильника! +25 сытости`);
        } else {
            this.stats.mood = Math.max(0, this.stats.mood - 20);
            this.addEvent(`😡 Спалился! Сосед заметил и обматерил. -20 настроения`);
            
            document.querySelector('.room').classList.add('shake');
            setTimeout(() => document.querySelector('.room').classList.remove('shake'), 300);
        }
        
        this.updateStatus();
    }
    
    party() {
        if (this.stats.energy < 30) {
            this.showModal('😴 Устал', 'Какая вписка без сил?');
            return;
        }
        
        if (this.coins < 30) {
            this.showModal('💰 Денег нет', 'Надо скинуться на пиццу');
            return;
        }
        
        this.stats.energy = Math.max(0, this.stats.energy - 30);
        this.coins -= 30;
        this.stats.mood = Math.min(this.MAX_STAT, this.stats.mood + this.PARTY_MOOD_GAIN);
        this.stats.study = Math.max(0, this.stats.study - 20);
        
        this.experience += 20;
        this.checkLevelUp();
        
        this.addEvent(`🎉 Отличная вписка! +${this.PARTY_MOOD_GAIN} настроения, -20 учёбы, +20 XP`);
        this.updateStatus();
    }
    
    sendDataToBot() {
        const data = {
            coins: this.coins,
            level: this.level,
            stats: this.stats,
            experience: this.experience
        };
        
        if (tg.isVersionAtLeast('6.1')) {
            tg.sendData(JSON.stringify(data));
            this.addEvent('💾 Прогресс отправлен в бота!');
            this.showModal('✅ Успех', 'Данные отправлены боту. Можешь закрывать приложение.');
        } else {
            this.showModal('❌ Ошибка', 'Твоя версия Telegram не поддерживает отправку данных.');
        }
        
        this.updateUI();
    }
    
    startDecay() {
        setInterval(() => {
            if (this.isSleeping) {
                this.stats.food = Math.max(0, this.stats.food - this.STAT_DECAY_RATE * 0.3);
            } else {
                this.stats.energy = Math.max(0, this.stats.energy - this.STAT_DECAY_RATE);
                this.stats.food = Math.max(0, this.stats.food - this.STAT_DECAY_RATE * 1.5);
                this.stats.mood = Math.max(0, this.stats.mood - this.STAT_DECAY_RATE * 0.8);
            }
            
            this.checkCritical();
            this.updateUI();
            this.saveGame();
        }, 5000);
    }
    
    checkCritical() {
        if (this.stats.energy <= 0) {
            this.addEvent('⚠️ Ты потерял сознание от усталости!');
            this.stats.energy = 20;
            this.stats.mood = Math.max(0, this.stats.mood - 30);
        }
        
        if (this.stats.food <= 0) {
            this.addEvent('⚠️ Голодный обморок!');
            this.stats.food = 20;
            this.stats.energy = Math.max(0, this.stats.energy - 30);
        }
        
        if (this.stats.mood <= 0) {
            this.addEvent('😢 Депрессия... Поспал и стало чуть легче');
            this.stats.mood = 30;
        }
        
        this.updateStatus();
    }
    
    checkLevelUp() {
        const nextLevel = Math.floor(this.experience / 100) + 1;
        if (nextLevel > this.level) {
            this.level = nextLevel;
            this.coins += 50;
            this.addEvent(`🎓 Поздравляем! Ты перешёл на ${this.level} курс! +50🪙`);
            this.showModal('🎉 УРОВЕНЬ ПОВЫШЕН', `Теперь ты на ${this.level} курсе! Получено 50 монет.`);
        }
    }
    
    updateStatus() {
        const minStat = Math.min(this.stats.energy, this.stats.food, this.stats.mood);
        
        if (this.isSleeping) {
            this.status = '😴';
        } else if (minStat < 20) {
            this.status = '😫';
        } else if (minStat < 40) {
            this.status = '😟';
        } else if (minStat < 60) {
            this.status = '😐';
        } else if (minStat < 80) {
            this.status = '🙂';
        } else {
            this.status = '😊';
        }
        
        document.getElementById('statusBubble').textContent = this.status;
        
        const avatars = ['🧑‍🎓', '👨‍🎓', '🧔‍♂️', '👨‍🏫', '🧙‍♂️'];
        const avatarIndex = Math.min(this.level - 1, avatars.length - 1);
        document.getElementById('avatar').textContent = avatars[avatarIndex];
    }
    
    updateUI() {
        document.getElementById('studentName').textContent = this.studentName;
        document.getElementById('studentLevel').textContent = `${this.level} курс`;
        document.getElementById('coinBalance').textContent = this.coins;
        
        document.getElementById('energyBar').style.width = `${this.stats.energy}%`;
        document.getElementById('foodBar').style.width = `${this.stats.food}%`;
        document.getElementById('moodBar').style.width = `${this.stats.mood}%`;
        document.getElementById('studyBar').style.width = `${this.stats.study}%`;
        
        document.getElementById('energyValue').textContent = `${Math.round(this.stats.energy)}%`;
        document.getElementById('foodValue').textContent = `${Math.round(this.stats.food)}%`;
        document.getElementById('moodValue').textContent = `${Math.round(this.stats.mood)}%`;
        document.getElementById('studyValue').textContent = `${Math.round(this.stats.study)}%`;
        
        const hour = new Date().getHours();
        const timeIcons = { night: '🌙', morning: '🌅', day: '☀️', evening: '🌆' };
        let timeIcon = timeIcons.day;
        if (hour < 6) timeIcon = timeIcons.night;
        else if (hour < 12) timeIcon = timeIcons.morning;
        else if (hour < 18) timeIcon = timeIcons.day;
        else timeIcon = timeIcons.evening;
        document.getElementById('timeOfDay').textContent = timeIcon;
    }
    
    updateFoodItems() {
        document.getElementById('foodItems').textContent = this.foodItems.slice(-3).join('');
    }
    
    updateBooks() {
        const bookEmojis = ['📚', '📖', '📕', '📗', '📘', '📙'];
        const books = [];
        for (let i = 0; i < Math.min(this.booksCount, 5); i++) {
            books.push(bookEmojis[i % bookEmojis.length]);
        }
        document.getElementById('books').textContent = books.join('');
    }
    
    addEvent(text) {
        this.events.unshift({ text, time: new Date().toLocaleTimeString().slice(0,5) });
        if (this.events.length > this.maxEvents) this.events.pop();
        
        const log = document.getElementById('eventLog');
        log.innerHTML = this.events.map(e => 
            `<div class="log-entry">[${e.time}] ${e.text}</div>`
        ).join('');
    }
    
    showModal(title, body) {
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalBody').textContent = body;
        document.getElementById('modal').classList.add('show');
    }
    
    showTab(tab) {
        if (tab !== 'room') {
            this.showModal(`📋 ${tab}`, 'Этот раздел в разработке. Скоро здесь будет магазин, рейтинг и соседи!');
            document.querySelector('.menu-btn[data-tab="room"]').classList.add('active');
        }
    }
    
    saveGame() {
        const saveData = {
            stats: this.stats,
            coins: this.coins,
            level: this.level,
            experience: this.experience,
            foodItems: this.foodItems,
            booksCount: this.booksCount
        };
        localStorage.setItem('tamagochiSave', JSON.stringify(saveData));
    }
    
    loadGame() {
        const saved = localStorage.getItem('tamagochiSave');
        if (saved) {
            try {
                const data = JSON.parse(saved);
                this.stats = data.stats;
                this.coins = data.coins;
                this.level = data.level;
                this.experience = data.experience;
                this.foodItems = data.foodItems || ['🍎', '🍕', '🥪'];
                this.booksCount = data.booksCount || 2;
                this.updateFoodItems();
                this.updateBooks();
                this.updateStatus();
            } catch(e) {
                console.error('Ошибка загрузки:', e);
            }
        }
    }
}

// Запуск игры
const game = new TamagochiGame();
