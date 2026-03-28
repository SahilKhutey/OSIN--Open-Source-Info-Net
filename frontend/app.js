// OSIN Dashboard Logic

const mockSignals = [
    { 
        id: 1, type: 'social', source: 'X / Twitter', content: 'Significant increase in trade volume detected in Southeast Asian markets.', time: '2m ago', 
        credibility: 0.85, 
        threat_level: 'YELLOW', combat_score: 0.78,
        breakdown: { credibility: 0.9, occurrence: 0.8, reach: 0.7, proof_type: 0.8, coverage: 0.9, variance: 0.8, source_diversity: 0.85 }
    },
    { 
        id: 2, type: 'news', source: 'Reuters', content: 'Global central banks indicate potential pivot in interest rate strategies.', time: '5m ago', 
        credibility: 0.95,
        threat_level: 'GREEN', combat_score: 0.92,
        breakdown: { credibility: 1.0, occurrence: 0.9, reach: 0.9, proof_type: 1.0, coverage: 0.95, variance: 0.9, source_diversity: 0.92 }
    }
];

const mockTrends = [
    { keyword: '#QuantumLeap', score: 9.4, platforms: ['X', 'Reddit'] },
    { keyword: 'MarketPivot', score: 8.2, platforms: ['NewsAPI', 'X'] },
    { keyword: 'OSIN_v1', score: 7.9, platforms: ['GDELT', 'YouTube'] }
];

function initDashboard() {
    renderSignals(mockSignals);
    renderTrends(mockTrends);
    renderHeatmap();
    setupModal();
    startLiveSimulation();
}

function renderHeatmap() {
    const grid = document.querySelector('.heatmap-grid');
    grid.innerHTML = Array(200).fill(0).map(() => `
        <div class="heat-cell ${Math.random() > 0.95 ? 'hot' : ''}"></div>
    `).join('');
}

function renderSignals(signals) {
    const container = document.getElementById('signals-container');
    container.innerHTML = signals.map(sig => `
        <div class="signal-item" onclick="showBreakdown(${sig.id})">
            <div class="signal-header">
                <span class="signal-tag tag-${sig.type}">${sig.type}</span>
                <span class="source-name">${sig.source}</span>
                <span class="combat-badge" style="color: ${sig.combat_score > 0.8 ? '#10b981' : '#94a3b8'}">Combat: ${(sig.combat_score * 100).toFixed(0)}</span>
            </div>
            <div class="signal-content">${sig.content}</div>
            <div class="signal-footer">
                <span class="signal-time">${sig.time}</span>
                <span class="signal-cred">Credibility: ${(sig.credibility * 100).toFixed(0)}%</span>
                <span class="threat-badge threat-${sig.threat_level}" style="font-size: 0.7rem; margin-left: auto; font-weight: bold;">${sig.threat_level}</span>
            </div>
        </div>
    `).join('');
    
    updateThreatLevel(signals[0]?.threat_level || 'GREEN');
}

function updateThreatLevel(level) {
    const indicator = document.getElementById('current-threat');
    const desc = document.getElementById('threat-desc');
    
    if (!indicator) return;
    
    indicator.textContent = level;
    indicator.className = `threat-indicator threat-${level}`;
    
    const descriptions = {
        'GREEN': 'Routine monitoring',
        'YELLOW': 'Elevated interest', 
        'ORANGE': 'Potential threat',
        'RED': 'Active situation',
        'BLACK': 'Critical emergency'
    };
    desc.textContent = descriptions[level] || 'Initializing...';
}

function renderTrends(trends) {
    const list = document.getElementById('trends-list');
    list.innerHTML = trends.map(tr => `
        <li class="trend-item">
            <div>
                <div class="trend-keyword">${tr.keyword}</div>
                <div style="font-size: 0.7rem; color: #94a3b8;">${tr.platforms.join(' • ')}</div>
            </div>
            <span class="trend-score">${tr.score}</span>
        </li>
    `).join('');
}

function setupModal() {
    const modal = document.getElementById('credibility-modal');
    const closeBtn = document.querySelector('.close-btn');
    closeBtn.onclick = () => modal.style.display = "none";
    window.onclick = (event) => {
        if (event.target == modal) modal.style.display = "none";
    }
}

window.showBreakdown = function(id) {
    const sig = [...mockSignals].find(s => s.id === id);
    if (!sig) return;
    
    const container = document.getElementById('breakdown-container');
    const modal = document.getElementById('credibility-modal');
    
    container.innerHTML = Object.entries(sig.breakdown).map(([key, val]) => `
        <div class="breakdown-row">
            <div style="text-transform: capitalize;">${key.replace('_', ' ')}</div>
            <div style="width: 200px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                    <span>${(val * 100).toFixed(0)}%</span>
                </div>
                <div class="progress-bar"><div class="progress" style="width: ${val * 100}%"></div></div>
            </div>
        </div>
    `).join('');
    
    modal.style.display = "block";
}

function startLiveSimulation() {
    setInterval(() => {
        const types = ['GREEN', 'YELLOW', 'ORANGE', 'RED'];
        const randomLevel = types[Math.floor(Math.random() * types.length)];
        
        const newSig = {
            id: Date.now(),
            type: Math.random() > 0.5 ? 'social' : 'news',
            source: 'OSIN Node ' + Math.floor(Math.random() * 10),
            content: randomLevel === 'RED' ? 'CRITICAL SIGNAL: Potential threat detected in global communications.' : 'Real-time alert: Intelligence signal extracted for monitoring.',
            time: 'Just now',
            credibility: (Math.random() * 0.4 + 0.6).toFixed(2),
            threat_level: randomLevel,
            combat_score: (Math.random() * 0.3 + 0.6).toFixed(2),
            breakdown: { credibility: 0.7, occurrence: 0.8, reach: 0.6, proof_type: 0.7, coverage: 0.8, variance: 0.7, source_diversity: 0.75 }
        };
        
        mockSignals.unshift(newSig);
        renderSignals(mockSignals.slice(0, 10));
        renderHeatmap(); // Update heatmap dots
    }, 15000);
}

function initDashboard() {
    renderSignals(mockSignals);
    renderTrends(mockTrends);
    renderHeatmap();
    renderPredictions();
    setupModal();
    startLiveSimulation();
    startCounterIntelMonitor();
}

function renderPredictions() {
    const list = document.getElementById('prediction-list');
    const predictions = [
        { zone: "Region Alpha-9", confidence: 88, risk: "High Escalation" },
        { zone: "Sector Gamma-12", confidence: 76, risk: "Social Unrest" }
    ];
    
    list.innerHTML = predictions.map(p => `
        <li class="prediction-item">
            <div>${p.zone} [${p.confidence}%]</div>
            <span>Type: ${p.risk}</span>
        </li>
    `).join('');
}

window.triggerGhost = function() {
    const protocol = document.getElementById('opsec-protocol');
    protocol.textContent = "Protocol: GHOST (Tor Active)";
    protocol.style.color = "#00ff41";
    alert("OSIN Layer: Protocol GHOST Initialized. Routing through Tor-over-VPN.");
}

window.triggerPhantom = function() {
    if (confirm("CRITICAL: Initiate Protocol PHANTOM? This will wipe all ephemeral node data.")) {
        document.body.style.filter = "grayscale(1) contrast(2)";
        alert("PROTOCOL PHANTOM: Data purge complete. Node self-destructing...");
        window.location.reload();
    }
}

function startCounterIntelMonitor() {
    setInterval(() => {
        const status = document.getElementById('hostile-monitoring');
        const random = Math.random();
        
        // Hostile monitoring telemetry
        if (random > 0.95) {
            status.textContent = "SUSPICIOUS";
            status.style.color = "#ef4444";
        } else {
            status.textContent = "Normal";
            status.style.color = "#00ff41";
        }

        // Multi-domain HUD telemetry
        document.getElementById('sat-status').textContent = random > 0.2 ? 'ACQUIRED' : 'SCANNING';
        document.getElementById('sigint-status').textContent = random > 0.5 ? 'BEARING FOUND' : 'INTERCEPTING';
        document.getElementById('lingua-status').textContent = 'TRANSLATING';
        
    }, 10000);
}

document.addEventListener('DOMContentLoaded', initDashboard);

