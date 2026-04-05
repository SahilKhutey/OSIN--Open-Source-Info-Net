// OSIN Terminal Dashboard
// Real-time intelligence signal ingestion and visualization

class OSINTerminal {
    constructor() {
        this.signals = [];
        this.trends = [];
        this.sourceCount = {
            'Twitter': 0,
            'Reddit': 0,
            'YouTube': 0,
            'News': 0,
            'Instagram': 0,
            'LinkedIn': 0
        };
        this.threatLevel = 'GREEN';
        this.startTime = Date.now();
        this.signalCount = 0;
        this.ingestionRate = 0;
        
        this.initTerminal();
    }

    initTerminal() {
        this.updateLiveTime();
        this.loadMockData();
        this.startSignalStream();
        setInterval(() => this.updateLiveTime(), 1000);
        setInterval(() => this.updateIngestionRate(), 1000);
    }

    loadMockData() {
        const mockSignals = [
            { 
                id: 1, 
                source: 'Twitter', 
                content: 'Market volatility detected in Asian trading sessions', 
                timestamp: new Date(Date.now() - 30000),
                credibility: 0.88,
                threatLevel: 'GREEN'
            },
            { 
                id: 2, 
                source: 'News', 
                content: 'Central banks signal policy adjustments ahead', 
                timestamp: new Date(Date.now() - 60000),
                credibility: 0.92,
                threatLevel: 'GREEN'
            },
            { 
                id: 3, 
                source: 'Reddit', 
                content: 'Technology sector trending: AI adoption acceleration', 
                timestamp: new Date(Date.now() - 90000),
                credibility: 0.75,
                threatLevel: 'YELLOW'
            },
            { 
                id: 4, 
                source: 'YouTube', 
                content: 'Geopolitical analysis: Regional tensions overview', 
                timestamp: new Date(Date.now() - 120000),
                credibility: 0.80,
                threatLevel: 'GREEN'
            }
        ];

        this.trends = [
            { keyword: '#QuantumComputing', score: 9.2, platforms: ['Twitter', 'Reddit'] },
            { keyword: '#ClimateAction', score: 8.5, platforms: ['News', 'Instagram'] },
            { keyword: '#TechInnovation', score: 8.1, platforms: ['YouTube', 'LinkedIn'] },
            { keyword: '#GlobalTrade', score: 7.8, platforms: ['News', 'Twitter'] },
            { keyword: '#DataPrivacy', score: 7.4, platforms: ['Reddit', 'LinkedIn'] }
        ];

        this.signals = mockSignals;
        this.signalCount = mockSignals.length;
        this.renderSignals();
        this.updateTrends();
        this.updateSourceMetrics();
        this.updateThreatLevel();
    }

    startSignalStream() {
        setInterval(() => {
            const sources = ['Twitter', 'Reddit', 'YouTube', 'News', 'Instagram', 'LinkedIn'];
            const contents = [
                'Market sentiment shift detected in real-time feeds',
                'Breaking: International policy announcement incoming',
                'Trending topic surge across multiple platforms',
                'Emerging pattern in social media discussions',
                'Data anomaly detected in signal correlation',
                'Cross-platform signal validation in progress',
                'Intelligence gap identified - requires analysis',
                'High-confidence signal extracted and confirmed'
            ];
            const threatLevels = ['GREEN', 'GREEN', 'GREEN', 'YELLOW', 'YELLOW'];

            const newSignal = {
                id: this.signals.length + 1,
                source: sources[Math.floor(Math.random() * sources.length)],
                content: contents[Math.floor(Math.random() * contents.length)],
                timestamp: new Date(),
                credibility: (Math.random() * 0.35 + 0.65).toFixed(2),
                threatLevel: threatLevels[Math.floor(Math.random() * threatLevels.length)]
            };

            this.signals.unshift(newSignal);
            if (this.signals.length > 20) this.signals.pop();
            this.signalCount++;
            this.ingestionRate++;

            this.sourceCount[newSignal.source]++;
            this.renderSignals();
            this.updateSourceMetrics();
            this.updateThreatLevel();

        }, 3000 + Math.random() * 2000);
    }

    renderSignals() {
        const feedContainer = document.getElementById('signal-feed');
        const signalCountEl = document.getElementById('signal-count');

        signalCountEl.textContent = this.signalCount;

        feedContainer.innerHTML = this.signals.map(sig => `
            <div class="signal-item" onclick="terminal.showSignalDetails(${sig.id})">
                <span class="signal-source">[${sig.source.toUpperCase()}]</span>
                <span class="signal-content">${sig.content}</span>
                <div style="display: flex; justify-content: space-between; margin-top: 3px;">
                    <span class="signal-time">${this.formatTime(sig.timestamp)}</span>
                    <span style="color: var(--terminal-amber);">Cred: ${(sig.credibility * 100).toFixed(0)}%</span>
                </div>
            </div>
        `).join('');

        if (this.signals.length === 0) {
            feedContainer.innerHTML = '<div class="terminal-line">> AWAITING SIGNAL STREAM...</div>';
        }
    }

    updateTrends() {
        const trendsContainer = document.getElementById('trends-container');
        trendsContainer.innerHTML = this.trends.map(tr => `
            <div class="trend-item">
                <span class="trend-keyword">${tr.keyword}</span>
                <span class="trend-score">${tr.score.toFixed(1)}</span>
            </div>
        `).join('');
    }

    updateSourceMetrics() {
        Object.keys(this.sourceCount).forEach(source => {
            const el = document.getElementById(source.toLowerCase() + '-count');
            if (el) el.textContent = this.sourceCount[source];
        });
    }

    updateThreatLevel() {
        const threatsCount = this.signals.filter(s => s.threatLevel === 'RED').length;
        const yellowCount = this.signals.filter(s => s.threatLevel === 'YELLOW').length;

        if (threatsCount > 0) {
            this.threatLevel = 'RED';
        } else if (yellowCount > 1) {
            this.threatLevel = 'YELLOW';
        } else {
            this.threatLevel = 'GREEN';
        }

        const threatBar = document.getElementById('threat-level-bar');
        const threatValue = document.getElementById('threat-value');
        const threatStatus = document.getElementById('threat-status');

        const threatLevels = { 'GREEN': 25, 'YELLOW': 60, 'RED': 100 };
        threatBar.style.width = threatLevels[this.threatLevel] + '%';
        threatBar.className = 'threat-level ' + this.threatLevel.toLowerCase();

        threatValue.textContent = this.threatLevel;
        threatValue.className = 'value threat-val ' + this.threatLevel.toLowerCase();

        const statusMap = {
            'GREEN': 'Routine monitoring in progress',
            'YELLOW': 'Elevated signal activity detected',
            'RED': 'Critical threat detected - escalation required'
        };
        threatStatus.textContent = statusMap[this.threatLevel];
    }

    showSignalDetails(signalId) {
        const signal = this.signals.find(s => s.id === signalId);
        if (!signal) return;

        const modalBody = document.getElementById('modal-body');
        const breakdown = {
            credibility: parseFloat(signal.credibility),
            frequency: (Math.random() * 0.3 + 0.7).toFixed(2),
            reach: (Math.random() * 0.3 + 0.6).toFixed(2),
            sourceQuality: (Math.random() * 0.3 + 0.75).toFixed(2),
            timelinessScore: (Math.random() * 0.3 + 0.8).toFixed(2)
        };

        modalBody.innerHTML = `
            <div class="detail-row">
                <span class="label">SOURCE:</span>
                <span class="value">${signal.source}</span>
            </div>
            <div class="detail-row">
                <span class="label">TIMESTAMP:</span>
                <span class="value">${signal.timestamp.toLocaleString()}</span>
            </div>
            <div class="detail-row">
                <span class="label">THREAT LEVEL:</span>
                <span class="value">${signal.threatLevel}</span>
            </div>
            <div style="margin: 10px 0; border-top: 1px dashed rgba(0, 255, 65, 0.3); padding-top: 10px;">
                <span style="color: var(--terminal-green); font-weight: bold;">CREDIBILITY BREAKDOWN:</span>
            </div>
            ${Object.entries(breakdown).map(([key, value]) => `
                <div class="detail-row">
                    <span class="label">${key.replace(/([A-Z])/g, ' $1').toUpperCase()}:</span>
                    <span class="value">${(value * 100).toFixed(0)}%</span>
                </div>
            `).join('')}
        `;

        const modal = document.getElementById('signal-modal');
        modal.classList.add('active');
    }

    updateLiveTime() {
        const timeEl = document.querySelector('.timestamp');
        if (timeEl) {
            const now = new Date();
            timeEl.textContent = now.toLocaleString();
        }
    }

    updateIngestionRate() {
        const rateEl = document.getElementById('ingestion-rate');
        if (rateEl) {
            rateEl.textContent = this.ingestionRate;
            this.ingestionRate = 0;
        }

        const uptimeEl = document.getElementById('uptime');
        if (uptimeEl) {
            const elapsed = Date.now() - this.startTime;
            const hours = Math.floor(elapsed / 3600000);
            const minutes = Math.floor((elapsed % 3600000) / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            uptimeEl.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }
    }

    formatTime(date) {
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);

        if (minutes > 0) return `${minutes}m ago`;
        return `${seconds}s ago`;
    }
}

// Initialize terminal
let terminal;
document.addEventListener('DOMContentLoaded', () => {
    terminal = new OSINTerminal();
});

// Modal handling
function closeModal() {
    const modal = document.getElementById('signal-modal');
    modal.classList.remove('active');
}

window.onclick = (event) => {
    const modal = document.getElementById('signal-modal');
    if (event.target === modal) {
        modal.classList.remove('active');
    }
};

