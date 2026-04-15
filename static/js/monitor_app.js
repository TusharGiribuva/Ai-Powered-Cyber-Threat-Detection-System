let pollInterval = null;
let isRunning = false;
let currentMode = "Ordinary User View";

const DOM = {
    btnToggle: document.getElementById('btnToggle'),
    statusPulse: document.getElementById('statusPulse'),
    viewModeGroup: document.getElementsByName('viewMode'),
    
    // Views
    viewOrdinary: document.getElementById('viewOrdinary'),
    viewTechnician: document.getElementById('viewTechnician'),

    // Ordinary UI
    ordinaryAlert: document.getElementById('ordinaryAlert'),
    ordTotalPkts: document.getElementById('ordTotalPkts'),
    ordBlocked: document.getElementById('ordBlocked'),
    ordCertainty: document.getElementById('ordCertainty'),
    ordHackersCard: document.getElementById('ordHackersCard'),
    ordFirewallState: document.getElementById('ordFirewallState'),
    btnResetFirewallOrd: document.getElementById('btnResetFirewallOrd'),
    ordTimeline: document.getElementById('ordTimeline'),

    // Technician UI
    techTotalPkts: document.getElementById('techTotalPkts'),
    techThreatLevel: document.getElementById('techThreatLevel'),
    techActiveThreats: document.getElementById('techActiveThreats'),
    techActiveThreatsCard: document.getElementById('techActiveThreatsCard'),
    techCertainty: document.getElementById('techCertainty'),
    techFirewallCode: document.getElementById('techFirewallCode'),
    btnResetFirewallTech: document.getElementById('btnResetFirewallTech'),
    techTableBody: document.getElementById('techTableBody'),
    techTableEmpty: document.getElementById('techTableEmpty')
};

function formatNumber(num) {
    return num.toLocaleString('en-US');
}

// Chart layout constants
const darkLayout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: '#94a3b8' },
    margin: { l: 40, r: 20, t: 30, b: 40 }
};

async function fetchState() {
    try {
        const res = await authFetch('/api/monitor/state');
        const data = await res.json();
        updateUI(data);
    } catch(e) {
        console.error('Error fetching state', e);
    }
}

async function fetchTick() {
    try {
        const res = await authFetch('/api/monitor/tick', { method: 'POST' });
        const data = await res.json();
        updateUI(data);
    } catch(e) {
        console.error('Error fetching tick', e);
    }
}

async function toggleMonitor() {
    isRunning = !isRunning;
    try {
        await authFetch('/api/monitor/toggle', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({is_running: isRunning})
        });
        updateToggleBtn();
        if (isRunning) {
            startPolling();
        } else {
            stopPolling();
        }
    } catch (e) {
        console.error(e);
        isRunning = !isRunning; // Revert
    }
}

async function clearFirewall() {
    try {
        await authFetch('/api/monitor/clear-firewall', { method: 'POST' });
        fetchState();
    } catch (e) {
        console.error(e);
    }
}

async function setViewMode(mode) {
    currentMode = mode;
    DOM.viewOrdinary.style.display = mode === 'Ordinary User View' ? 'block' : 'none';
    DOM.viewTechnician.style.display = mode === 'Technician View' ? 'block' : 'none';
    
    // Only resize charts if visible
    if(mode === 'Technician View') {
        window.dispatchEvent(new Event('resize'));
    }
}

function updateToggleBtn() {
    if (isRunning) {
        DOM.btnToggle.innerText = "⏸️ Pause Monitoring";
        DOM.statusPulse.classList.remove('paused');
    } else {
        DOM.btnToggle.innerText = "▶️ Start Monitoring";
        DOM.statusPulse.classList.add('paused');
    }
}

function startPolling() {
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(fetchTick, 1500);
}

function stopPolling() {
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = null;
}

function updateUI(data) {
    // 1. Sync state correctly based on backend dicts
    if (data.is_running !== isRunning) {
        isRunning = data.is_running;
        updateToggleBtn();
        if (isRunning) startPolling();
        else stopPolling();
    }
    
    if (data.metrics === undefined) return; // safety

    const m = data.metrics;
    const blocks = data.blocklist || [];
    
    // Update Ordinary View
    DOM.ordTotalPkts.innerText = formatNumber(m.total_packets || 0);
    DOM.ordBlocked.innerText = `${m.blocklist_count || 0} Unique`;
    DOM.ordCertainty.innerText = `${(m.avg_confidence * 100).toFixed(1)}%`;
    
    if (m.active_threats === 0) {
        DOM.ordinaryAlert.innerHTML = `
            <div class="alert-box alert-safe">
                <h2><span style="font-size: 2rem;">🟢</span> Your Network is Safe and Secure</h2>
                <p style="color: #cbd5e1; font-size: 1.1rem; margin-top: 10px;">The AI is actively monitoring all web traffic. No hackers detected recently.</p>
            </div>
        `;
    } else {
        DOM.ordinaryAlert.innerHTML = `
            <div class="alert-box alert-danger">
                <h2><span style="font-size: 2rem;">🔴</span> Alert! We blocked ${m.active_threats} hacking attempt${m.active_threats>1?'s':''}</h2>
                <p style="color: #ffb7b7; font-size: 1.1rem; margin-top: 10px;">The AI detected abnormal behavior and has isolated the threats instantly.</p>
            </div>
        `;
    }
    
    if (m.active_threats > 0) {
        DOM.ordHackersCard.classList.add('danger-border');
        DOM.ordBlocked.classList.replace('safe-text', 'critical-text');
    } else {
        DOM.ordHackersCard.classList.remove('danger-border');
        DOM.ordBlocked.classList.replace('critical-text', 'safe-text');
    }
    
    if (m.blocklist_count > 0) {
        DOM.ordFirewallState.innerHTML = `<p style="color: #f59e0b; font-weight: 500;">⚠️ <strong>Action Taken:</strong> The AI has automatically blocked <strong>${m.blocklist_count}</strong> malicious IP Addresses from accessing the network.</p>`;
        DOM.btnResetFirewallOrd.style.display = 'inline-block';
    } else {
        DOM.ordFirewallState.innerHTML = `<p style="color: #10b981;">The firewall is standing by. All connected computers are trusted.</p>`;
        DOM.btnResetFirewallOrd.style.display = 'none';
    }
    
    // Render Timeline
    const evts = data.recent_events || [];
    DOM.ordTimeline.innerHTML = evts.map(e => {
        if (e.is_anomaly === 0) {
            return `<div class="timeline-item"><span class="time">${e.time}</span> - Normal connection from computer <code>...${e.src_ip.slice(-6)}</code> was permitted.</div>`;
        } else {
            let term = e.label;
            if (term === "DDoS") term = "Website Overload Attack (Trying to crash the site)";
            else if (term === "Brute Force") term = "Password Guessing Attack";
            else if (term === "Port Scan") term = "Network Probing (Looking for vulnerabilities)";
            else if (term === "SQL Injection") term = "Database Hacking Attempt";
            
            return `<div class="timeline-item danger"><strong style="color: #ef4444">${e.time} ⚠️ Threat Prevented:</strong> Someone tried a <b>${term}</b>. The AI permanently blocked their IP Address with ${(e.confidence*100).toFixed(1)}% certainty.</div>`;
        }
    }).join("");
    
    
    // Update Technician View
    DOM.techTotalPkts.innerText = formatNumber(m.total_packets || 0);
    DOM.techThreatLevel.innerText = `${(m.threat_ratio || 0).toFixed(1)}%`;
    DOM.techActiveThreats.innerText = m.active_threats || 0;
    DOM.techCertainty.innerText = `${(m.avg_confidence * 100).toFixed(1)}%`;
    
    if (m.threat_ratio > 10) DOM.techThreatLevel.className = "critical-text";
    else if (m.threat_ratio > 5) DOM.techThreatLevel.className = "warning-text";
    else DOM.techThreatLevel.className = "safe-text";
    
    if (m.active_threats > 0) {
        DOM.techActiveThreatsCard.classList.add('danger-border');
        DOM.techActiveThreats.className = "critical-text";
    } else {
        DOM.techActiveThreatsCard.classList.remove('danger-border');
        DOM.techActiveThreats.className = "safe-text";
    }
    
    if (m.blocklist_count > 0) {
        DOM.techFirewallCode.innerHTML = blocks.map(ip => `iptables -A INPUT -s ${ip} -j DROP`).join('\n');
    } else {
        DOM.techFirewallCode.innerHTML = '<span style="color:#10b981;">No active layer 3 blocking rules.</span>';
    }
    
    // Technician Alerts Table
    const alerts = data.recent_alerts || [];
    if (alerts.length > 0) {
        DOM.techTableBody.innerHTML = alerts.map(a => 
            `<tr><td>${a.timestamp_str}</td><td>${a.src_ip}</td><td>${a.label}</td><td>${(a.confidence*100).toFixed(1)}%</td></tr>`
        ).join('');
        DOM.techTableBody.style.display = 'table-row-group';
        DOM.techTableEmpty.style.display = 'none';
    } else {
        DOM.techTableBody.style.display = 'none';
        DOM.techTableEmpty.style.display = 'block';
    }
    
    updateCharts(data);
}

function updateCharts(data) {
    const timeGrps = data.time_grouped || [];
    if (timeGrps.length > 0) {
        const trace = {
            x: timeGrps.map(g => g.time),
            y: timeGrps.map(g => g.src_bytes),
            fill: 'tozeroy',
            type: 'scatter',
            mode: 'lines',
            line: { color: '#818cf8', width: 2 },
            fillcolor: 'rgba(129, 140, 248, 0.2)',
            name: 'Bandwidth'
        };
        // Add markers for anomalies
        const anomalies = timeGrps.filter(g => g.is_anomaly === 1);
        const traceAnom = {
            x: anomalies.map(g => g.time),
            y: anomalies.map(g => g.src_bytes),
            mode: 'markers',
            marker: { color: '#ef4444', size: 10, symbol: 'star', line: {width:1, color:'white'} },
            name: 'Threat detected'
        };
        
        Plotly.react('areaChart', [trace, traceAnom], {
            ...darkLayout,
            showlegend: false,
            xaxis: { showgrid: false },
            yaxis: { showgrid: true, gridcolor: 'rgba(255,255,255,0.05)' }
        });
    }
    
    const threats = data.threat_dist || [];
    if (threats.length > 0) {
        const pieTrace = {
            values: threats.map(t => t.count),
            labels: threats.map(t => t.label),
            type: 'pie',
            hole: 0.7,
            marker: { colors: ['#ef4444', '#f59e0b', '#8b5cf6', '#ec4899', '#10b981'] },
            textinfo: 'none'
        };
        Plotly.react('pieChart', [pieTrace], {
            ...darkLayout, showlegend: false,
            annotations: [{ text: `<b>${data.metrics.anomalies_detected}</b><br>Threats`, font: {size: 14, color: '#fff'}, showarrow: false }]
        });
    }
    
    const ports = data.port_dist || [];
    if (ports.length > 0) {
        const topPorts = ports.slice(0, 5);
        const barTrace = {
            x: topPorts.map(p => p.port),
            y: topPorts.map(p => p.count),
            type: 'bar',
            marker: { color: '#6366f1' }
        };
        Plotly.react('barChart', [barTrace], {
            ...darkLayout,
            xaxis: { showgrid: false, title: "Targeted Ports" },
            yaxis: { showgrid: true, gridcolor: 'rgba(255,255,255,0.05)', title: "Attacks" }
        });
    }
}

// Event Listeners
DOM.btnToggle.addEventListener('click', toggleMonitor);
DOM.btnResetFirewallOrd.addEventListener('click', clearFirewall);
DOM.btnResetFirewallTech.addEventListener('click', clearFirewall);

DOM.viewModeGroup.forEach(radio => {
    radio.addEventListener('change', (e) => {
        setViewMode(e.target.value);
    });
});

// Setup
fetchState();
