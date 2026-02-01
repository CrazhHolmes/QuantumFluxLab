/**
 * Quantum-Flux Lab Console - Main Application
 * Quantum-Flux Lab Control Interface
 * 
 * Features:
 * - Real-time sensor monitoring
 * - System control interface
 * - Data visualization
 * - Command console
 * - Safety monitoring
 */

// ============================================================================
// Configuration
// ============================================================================
const CONFIG = {
    updateInterval: 100,      // ms between sensor updates
    graphHistory: 200,        // Number of data points to keep
    safetyThresholds: {
        temp: { warning: 40, critical: 50 },
        ozone: { warning: 0.05, critical: 0.08 },
        current: { warning: 0.8, critical: 1.2 },
        spl: { warning: 100, critical: 120 },
        uv: { warning: 0.5, critical: 1.0 }
    }
};

// ============================================================================
// State Management
// ============================================================================
const state = {
    connected: false,
    systemState: 'STANDBY',
    sensors: {
        temperature1: 22.5,
        temperature2: 23.1,
        ozone: 0.02,
        uv: 0.1,
        current: 0.15,
        voltage: 11.8,
        spl: 45
    },
    controls: {
        hvEnabled: false,
        audioEnabled: false,
        hvFrequency: 400,
        hvAmplitude: 128,
        audioFrequency: 20,
        audioAmplitude: 100
    },
    history: {
        temp: [],
        current: [],
        spl: [],
        ozone: [],
        uv: []
    },
    uptime: 0,
    logs: {
        discovery: '',
        safety: '',
        timetravel: '',
        commands: 'Command log initialized...\n'
    }
};

// ============================================================================
// DOM Elements
// ============================================================================
const elements = {};

function initElements() {
    // Navigation
    elements.navTabs = document.querySelectorAll('.nav-tab');
    elements.views = document.querySelectorAll('.view');
    
    // Connection
    elements.connectionStatus = document.getElementById('connectionStatus');
    
    // Metrics
    elements.metrics = {
        temp: document.getElementById('metricTemp'),
        ozone: document.getElementById('metricOzone'),
        current: document.getElementById('metricCurrent'),
        spl: document.getElementById('metricSPL'),
        voltage: document.getElementById('metricVoltage'),
        uv: document.getElementById('metricUV')
    };
    
    // State
    elements.systemState = document.getElementById('systemState');
    elements.trapNode = document.getElementById('trapNode');
    
    // Indicators
    elements.indicators = {
        hv: document.getElementById('indHV'),
        audio: document.getElementById('indAudio'),
        relay: document.getElementById('indRelay'),
        estop: document.getElementById('indEStop')
    };
    
    // Controls
    elements.sliders = {
        hvFreq: document.getElementById('hvFreq'),
        hvAmp: document.getElementById('hvAmp'),
        audioFreq: document.getElementById('audioFreq'),
        audioAmp: document.getElementById('audioAmp')
    };
    
    elements.sliderValues = {
        hvFreq: document.getElementById('hvFreqVal'),
        hvAmp: document.getElementById('hvAmpVal'),
        audioFreq: document.getElementById('audioFreqVal'),
        audioAmp: document.getElementById('audioAmpVal')
    };
    
    elements.buttons = {
        hv: document.getElementById('btnHV'),
        audio: document.getElementById('btnAudio'),
        start: document.getElementById('btnStart'),
        stop: document.getElementById('btnStop'),
        reset: document.getElementById('btnReset'),
        emergency: document.getElementById('emergencyStop')
    };
    
    // Terminal
    elements.terminalOutput = document.getElementById('terminalOutput');
    elements.terminalInput = document.getElementById('terminalInput');
    
    // Graph
    elements.graph = document.getElementById('realtimeGraph');
    elements.graphButtons = document.querySelectorAll('.graph-btn');
    
    // Logs
    elements.logButtons = document.querySelectorAll('.log-btn');
    elements.logDisplay = document.getElementById('logDisplay');
    
    // Footer
    elements.uptime = document.getElementById('uptime');
    elements.safetyStatus = document.getElementById('safetyStatus');
    
    // Modal
    elements.alertModal = document.getElementById('alertModal');
    elements.alertHeader = document.getElementById('alertHeader');
    elements.alertBody = document.getElementById('alertBody');
    elements.alertAck = document.getElementById('alertAck');
}

// ============================================================================
// Navigation
// ============================================================================
function initNavigation() {
    elements.navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const viewName = tab.dataset.view;
            switchView(viewName);
            
            elements.navTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
        });
    });
}

function switchView(viewName) {
    elements.views.forEach(view => view.classList.remove('active'));
    document.getElementById(viewName + 'View').classList.add('active');
}

// ============================================================================
// Sensor Simulation
// ============================================================================
function simulateSensors() {
    // Base values with small random fluctuations
    state.sensors.temperature1 = simulateValue(
        state.sensors.temperature1, 
        state.controls.hvEnabled ? 35 : 22, 
        0.5, 20, 60
    );
    state.sensors.temperature2 = simulateValue(
        state.sensors.temperature2, 
        state.controls.hvEnabled ? 38 : 23, 
        0.5, 20, 60
    );
    state.sensors.ozone = simulateValue(
        state.sensors.ozone, 
        state.controls.hvEnabled ? 0.06 : 0.02, 
        0.005, 0, 0.15
    );
    state.sensors.current = simulateValue(
        state.sensors.current, 
        state.controls.hvEnabled ? 0.5 : 0.15, 
        0.05, 0, 2
    );
    state.sensors.spl = simulateValue(
        state.sensors.spl, 
        state.controls.audioEnabled ? 105 : 45, 
        2, 30, 150
    );
    state.sensors.uv = simulateValue(
        state.sensors.uv, 
        state.controls.hvEnabled ? 0.4 : 0.1, 
        0.02, 0, 2
    );
    state.sensors.voltage = simulateValue(
        state.sensors.voltage, 
        12.0, 
        0.1, 10, 14
    );
}

function simulateValue(current, target, noise, min, max) {
    const drift = (target - current) * 0.1;
    const random = (Math.random() - 0.5) * noise;
    const newValue = current + drift + random;
    return Math.max(min, Math.min(max, newValue));
}

// ============================================================================
// Update UI
// ============================================================================
function updateMetrics() {
    updateMetricCard('temp', state.sensors.temperature1, '°C', 60);
    updateMetricCard('ozone', state.sensors.ozone, ' ppm', 0.1);
    updateMetricCard('current', state.sensors.current, ' A', 2);
    updateMetricCard('spl', state.sensors.spl, ' dB', 140);
    updateMetricCard('voltage', state.sensors.voltage, ' V', 15);
    updateMetricCard('uv', state.sensors.uv, ' mW', 2);
}

function updateMetricCard(key, value, unit, max) {
    const card = elements.metrics[key];
    if (!card) return;
    
    const valueEl = card.querySelector('.metric-value');
    const fillEl = card.querySelector('.metric-fill');
    
    valueEl.textContent = value.toFixed(key === 'ozone' ? 3 : key === 'current' ? 2 : 1) + unit;
    
    const percent = Math.min(100, (value / max) * 100);
    fillEl.style.width = percent + '%';
    
    // Check thresholds
    const thresholds = CONFIG.safetyThresholds[key];
    card.classList.remove('warning', 'critical');
    
    if (thresholds) {
        if (value >= thresholds.critical) {
            card.classList.add('critical');
        } else if (value >= thresholds.warning) {
            card.classList.add('warning');
        }
    }
}

function updateSystemState() {
    const badge = elements.systemState;
    badge.className = 'state-badge';
    
    // Determine state based on controls and safety
    if (state.controls.hvEnabled && state.controls.audioEnabled) {
        // Check for critical conditions
        if (state.sensors.temperature1 > 50 || state.sensors.ozone > 0.08) {
            state.systemState = 'CRITICAL';
            badge.classList.add('critical');
        } else if (state.sensors.temperature1 > 40 || state.sensors.ozone > 0.05) {
            state.systemState = 'WARNING';
            badge.classList.add('warning');
        } else {
            state.systemState = 'RUNNING';
            badge.classList.add('running');
        }
    } else if (state.controls.hvEnabled || state.controls.audioEnabled) {
        state.systemState = 'PARTIAL';
    } else {
        state.systemState = 'STANDBY';
    }
    
    badge.textContent = state.systemState;
    
    // Update trap visualization
    if (state.systemState === 'RUNNING') {
        elements.trapNode.classList.add('active');
    } else {
        elements.trapNode.classList.remove('active');
    }
}

function updateIndicators() {
    // HV indicator
    elements.indicators.hv.classList.toggle('active', state.controls.hvEnabled);
    
    // Audio indicator
    elements.indicators.audio.classList.toggle('active', state.controls.audioEnabled);
    
    // Relay indicator (active in normal operation)
    const relayActive = state.systemState !== 'EMERGENCY_STOP' && state.systemState !== 'CRITICAL';
    elements.indicators.relay.classList.toggle('active', relayActive);
    
    // E-stop indicator (normally off, red when pressed)
    elements.indicators.estop.classList.toggle('danger', state.systemState === 'EMERGENCY_STOP');
}

function updateHistory() {
    // Add current values to history
    state.history.temp.push(state.sensors.temperature1);
    state.history.current.push(state.sensors.current);
    state.history.spl.push(state.sensors.spl);
    state.history.ozone.push(state.sensors.ozone);
    state.history.uv.push(state.sensors.uv);
    
    // Trim to max length
    Object.keys(state.history).forEach(key => {
        if (state.history[key].length > CONFIG.graphHistory) {
            state.history[key].shift();
        }
    });
}

function updateSafetyStatus() {
    let status = 'OK';
    let className = 'safety-ok';
    
    if (state.systemState === 'CRITICAL' || state.systemState === 'EMERGENCY_STOP') {
        status = 'CRITICAL';
        className = 'safety-critical';
    } else if (state.systemState === 'WARNING') {
        status = 'WARNING';
        className = 'safety-warning';
    }
    
    elements.safetyStatus.textContent = status === 'OK' ? '✓ OK' : '⚠ ' + status;
    elements.safetyStatus.className = className;
}

// ============================================================================
// Graph Rendering
// ============================================================================
let currentGraphMetric = 'temp';

function initGraph() {
    elements.graphButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            currentGraphMetric = btn.dataset.metric;
            elements.graphButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
}

function drawGraph() {
    const canvas = elements.graph;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Get data
    const data = state.history[currentGraphMetric];
    if (data.length < 2) return;
    
    // Calculate scales
    const min = Math.min(...data) * 0.9;
    const max = Math.max(...data) * 1.1;
    const range = max - min || 1;
    
    // Draw grid
    ctx.strokeStyle = '#30363d';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i < 5; i++) {
        const y = (height / 4) * i;
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
    }
    ctx.stroke();
    
    // Draw data line
    ctx.strokeStyle = getGraphColor(currentGraphMetric);
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    data.forEach((value, i) => {
        const x = (i / (CONFIG.graphHistory - 1)) * width;
        const y = height - ((value - min) / range) * height;
        
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.stroke();
    
    // Draw fill
    ctx.fillStyle = getGraphColor(currentGraphMetric) + '20';
    ctx.lineTo(width, height);
    ctx.lineTo(0, height);
    ctx.closePath();
    ctx.fill();
    
    // Draw current value
    ctx.fillStyle = '#f0f6fc';
    ctx.font = '12px JetBrains Mono';
    const current = data[data.length - 1];
    ctx.fillText(currentMetricLabel(currentGraphMetric, current), 10, 20);
}

function getGraphColor(metric) {
    const colors = {
        temp: '#d29922',
        current: '#58a6ff',
        spl: '#a371f7',
        ozone: '#3fb950',
        uv: '#f85149'
    };
    return colors[metric] || '#58a6ff';
}

function currentMetricLabel(metric, value) {
    const labels = {
        temp: value.toFixed(1) + '°C',
        current: value.toFixed(2) + 'A',
        spl: value.toFixed(0) + 'dB'
    };
    return labels[metric] || value.toFixed(2);
}

// ============================================================================
// Controls
// ============================================================================
function initControls() {
    // Sliders
    Object.keys(elements.sliders).forEach(key => {
        const slider = elements.sliders[key];
        const valueDisplay = elements.sliderValues[key];
        
        slider.addEventListener('input', () => {
            valueDisplay.textContent = slider.value;
            updateControlState(key, parseInt(slider.value));
        });
    });
    
    // Toggle buttons
    elements.buttons.hv.addEventListener('click', () => {
        state.controls.hvEnabled = !state.controls.hvEnabled;
        elements.buttons.hv.classList.toggle('active', state.controls.hvEnabled);
        logCommand(`HV ${state.controls.hvEnabled ? 'enabled' : 'disabled'}`);
    });
    
    elements.buttons.audio.addEventListener('click', () => {
        state.controls.audioEnabled = !state.controls.audioEnabled;
        elements.buttons.audio.classList.toggle('active', state.controls.audioEnabled);
        logCommand(`Audio ${state.controls.audioEnabled ? 'enabled' : 'disabled'}`);
    });
    
    // System buttons
    elements.buttons.start.addEventListener('click', () => {
        state.controls.hvEnabled = true;
        state.controls.audioEnabled = true;
        elements.buttons.hv.classList.add('active');
        elements.buttons.audio.classList.add('active');
        state.systemState = 'RUNNING';
        logCommand('System started');
        addTerminalLine('System starting...', 'success');
    });
    
    elements.buttons.stop.addEventListener('click', () => {
        state.controls.hvEnabled = false;
        state.controls.audioEnabled = false;
        elements.buttons.hv.classList.remove('active');
        elements.buttons.audio.classList.remove('active');
        state.systemState = 'STANDBY';
        logCommand('System stopped');
        addTerminalLine('System stopped', 'warning');
    });
    
    elements.buttons.reset.addEventListener('click', () => {
        resetSystem();
        logCommand('System reset');
    });
    
    // Emergency stop
    elements.buttons.emergency.addEventListener('click', () => {
        emergencyStop();
    });
}

function updateControlState(key, value) {
    const mapping = {
        hvFreq: 'hvFrequency',
        hvAmp: 'hvAmplitude',
        audioFreq: 'audioFrequency',
        audioAmp: 'audioAmplitude'
    };
    
    if (mapping[key]) {
        state.controls[mapping[key]] = value;
    }
}

function resetSystem() {
    state.controls.hvEnabled = false;
    state.controls.audioEnabled = false;
    elements.buttons.hv.classList.remove('active');
    elements.buttons.audio.classList.remove('active');
    state.systemState = 'STANDBY';
    addTerminalLine('System reset complete', 'success');
}

function emergencyStop() {
    state.controls.hvEnabled = false;
    state.controls.audioEnabled = false;
    elements.buttons.hv.classList.remove('active');
    elements.buttons.audio.classList.remove('active');
    state.systemState = 'EMERGENCY_STOP';
    
    showAlert('EMERGENCY STOP', 'All systems have been shut down. Click Acknowledge to reset.');
    addTerminalLine('!!! EMERGENCY STOP TRIGGERED !!!', 'error');
    logCommand('EMERGENCY STOP');
}

// ============================================================================
// Terminal
// ============================================================================
const COMMANDS = {
    help: {
        description: 'Show available commands',
        execute: () => {
            addTerminalLine('Available commands:', 'system');
            Object.keys(COMMANDS).forEach(cmd => {
                addTerminalLine(`  ${cmd.padEnd(12)} - ${COMMANDS[cmd].description}`, 'response');
            });
        }
    },
    status: {
        description: 'Show system status',
        execute: () => {
            addTerminalLine('System Status:', 'system');
            addTerminalLine(`  State: ${state.systemState}`, 'response');
            addTerminalLine(`  HV: ${state.controls.hvEnabled ? 'ON' : 'OFF'} (${state.controls.hvFrequency}Hz)`, 'response');
            addTerminalLine(`  Audio: ${state.controls.audioEnabled ? 'ON' : 'OFF'} (${state.controls.audioFrequency}Hz)`, 'response');
            addTerminalLine(`  Temperature: ${state.sensors.temperature1.toFixed(1)}°C`, 'response');
            addTerminalLine(`  Current: ${state.sensors.current.toFixed(2)}A`, 'response');
        }
    },
    start: {
        description: 'Start the system',
        execute: () => {
            elements.buttons.start.click();
        }
    },
    stop: {
        description: 'Stop the system',
        execute: () => {
            elements.buttons.stop.click();
        }
    },
    reset: {
        description: 'Reset the system',
        execute: () => {
            elements.buttons.reset.click();
        }
    },
    hv: {
        description: 'Toggle HV (high voltage)',
        execute: () => {
            elements.buttons.hv.click();
        }
    },
    audio: {
        description: 'Toggle audio system',
        execute: () => {
            elements.buttons.audio.click();
        }
    },
    clear: {
        description: 'Clear terminal',
        execute: () => {
            elements.terminalOutput.innerHTML = '';
        }
    },
    sensors: {
        description: 'Show sensor readings',
        execute: () => {
            addTerminalLine('Sensor Readings:', 'system');
            addTerminalLine(`  Temperature 1: ${state.sensors.temperature1.toFixed(1)}°C`, 'response');
            addTerminalLine(`  Temperature 2: ${state.sensors.temperature2.toFixed(1)}°C`, 'response');
            addTerminalLine(`  Ozone: ${state.sensors.ozone.toFixed(3)} ppm`, 'response');
            addTerminalLine(`  UV: ${state.sensors.uv.toFixed(2)} mW/cm²`, 'response');
            addTerminalLine(`  Current: ${state.sensors.current.toFixed(3)} A`, 'response');
            addTerminalLine(`  Voltage: ${state.sensors.voltage.toFixed(1)} V`, 'response');
            addTerminalLine(`  SPL: ${state.sensors.spl.toFixed(1)} dB`, 'response');
        }
    },
    about: {
        description: 'Show system information',
        execute: () => {
            addTerminalLine('RPAT Research Console v1.0', 'system');
            addTerminalLine('Resonant Plasma Acoustic Trap', 'response');
            addTerminalLine('Budget: $72.65 / $75.00', 'response');
            addTerminalLine('Open Source - MIT License', 'response');
        }
    }
};

function initTerminal() {
    elements.terminalInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const cmd = elements.terminalInput.value.trim();
            if (cmd) {
                addTerminalLine(`QFL> ${cmd}`, 'command');
                executeCommand(cmd);
                elements.terminalInput.value = '';
            }
        }
    });
}

function executeCommand(cmd) {
    const parts = cmd.toLowerCase().split(' ');
    const command = parts[0];
    
    if (COMMANDS[command]) {
        COMMANDS[command].execute();
        logCommand(cmd);
    } else {
        addTerminalLine(`Unknown command: ${command}. Type 'help' for available commands.`, 'error');
    }
}

function addTerminalLine(text, type = 'response') {
    const line = document.createElement('div');
    line.className = `terminal-line ${type}`;
    line.textContent = text;
    elements.terminalOutput.appendChild(line);
    elements.terminalOutput.scrollTop = elements.terminalOutput.scrollHeight;
}

// ============================================================================
// Logs
// ============================================================================
function initLogs() {
    elements.logButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const logType = btn.dataset.log;
            elements.logButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadLog(logType);
        });
    });
    
    // Load initial log
    loadLog('discovery');
}

function loadLog(type) {
    // In a real implementation, this would fetch from the server
    // For now, we'll display placeholder content
    const logs = {
        discovery: `Loading Discovery Log...

[2026-01-31 17:46:12] INITIAL SEARCH COMPLETED
- Source: NASA Tech Reports, arXiv, MDPI Sensors
- Key Finding: Corona discharge at low pressure (20-100 kPa) shows CEV 
  decreases quasi-linearly with pressure (Riba et al., 2021)

[2026-01-31 17:47:33] PIEZO-HV BREAKTHROUGH
- Source: NASA HDBK-4007 (Spacecraft HV Paschen & Corona)
- Discovery: Multiple piezo sparkers in phased array can generate 
  sustained corona without arc breakdown

[2026-01-31 17:50:18] SYNTHESIS - THE RESONANT PLASMA ACOUSTIC TRAP (RPAT)
NOVEL DISCOVERY CLAIM:
The combination of piezo-driven resonant HV, corona plasma sheet,
electrostatic pressure field, and infrasound standing wave creates
a STABLE, TUNABLE levitation node.

See full log: logs/Log_discovery.log`,
        
        safety: `Loading Safety Log...

[2026-01-31 17:46:30] HIGH VOLTAGE SAFETY ANALYSIS
Operating Voltage: 10-30 kV DC
Paschen's Law Calculations:
- Breakdown voltage in air: ~3 kV/mm
- Operating gap: 30mm
- Safety margin: 3:1

[2026-01-31 17:48:15] CORONA/PLASMA SAFETY
Ozone Generation Rate: ~0.1-0.3 ppm
OSHA 8-hr limit: 0.1 ppm
SHUTDOWN TRIGGER: >0.08 ppm

[2026-01-31 17:55:00] FAIL-SAFE CIRCUIT DESIGN
Triple Redundant Safety:
1. Hardware Relay (Watchdog + E-Stop)
2. Software MOSFET (Controller-mediated)
3. Passive Fuse (Overcurrent)

See full log: logs/Log_safety.log`,
        
        timetravel: `Loading Time-Travel Physics Log...

[2026-01-31 17:46:00] WARP DRIVES & CLOSED TIMELIKE CURVES
Source: arXiv:2309.10072 (Barak Shoshany, 2023)
Key Finding: Two warp drives can create closed timelike geodesics
Status: Theoretical - requires exotic matter

[2026-01-31 17:49:00] MACROSCOPIC DELAYED-CHOICE QUANTUM ERASER
Source: arXiv:2205.14353 (Ham, 2022)
Setup: Noninterfering Mach-Zehnder with polarizing beam splitters
Result: Post-determination of photon nature in macroscopic regime

[2026-01-31 17:55:00] MOST FEASIBLE GARAGE EXPERIMENT
Delayed-Choice Optical Delay Line ($50-75 budget)
Demonstrates the PRINCIPLE of temporal nonlocality.

See full log: logs/Log_time_travel.log`,
        
        commands: state.logs.commands
    };
    
    elements.logDisplay.textContent = logs[type] || 'Log not found';
}

function logCommand(cmd) {
    const timestamp = new Date().toISOString();
    state.logs.commands += `[${timestamp}] ${cmd}\n`;
}

// ============================================================================
// Modal
// ============================================================================
function initModal() {
    elements.alertAck.addEventListener('click', () => {
        elements.alertModal.classList.remove('active');
        if (state.systemState === 'EMERGENCY_STOP') {
            resetSystem();
        }
    });
}

function showAlert(title, message) {
    elements.alertHeader.textContent = title;
    elements.alertBody.textContent = message;
    elements.alertModal.classList.add('active');
}

// ============================================================================
// Uptime
// ============================================================================
function updateUptime() {
    state.uptime++;
    const hours = Math.floor(state.uptime / 3600).toString().padStart(2, '0');
    const minutes = Math.floor((state.uptime % 3600) / 60).toString().padStart(2, '0');
    const seconds = (state.uptime % 60).toString().padStart(2, '0');
    elements.uptime.textContent = `Uptime: ${hours}:${minutes}:${seconds}`;
}

// ============================================================================
// Main Loop
// ============================================================================
function update() {
    simulateSensors();
    updateMetrics();
    updateSystemState();
    updateIndicators();
    updateHistory();
    updateSafetyStatus();
    drawGraph();
}

// ============================================================================
// Initialization
// ============================================================================
function init() {
    initElements();
    initNavigation();
    initControls();
    initTerminal();
    initGraph();
    initLogs();
    initModal();
    
    // Start update loops
    setInterval(update, CONFIG.updateInterval);
    setInterval(updateUptime, 1000);
    
    // Initial update
    update();
    
    // Simulate connection
    setTimeout(() => {
        state.connected = true;
        elements.connectionStatus.querySelector('.status-dot').classList.remove('offline');
        elements.connectionStatus.querySelector('.status-text').textContent = 'Connected';
        addTerminalLine('Connected to Arduino controller', 'success');
    }, 1500);
    
    console.log('RPAT Research Console initialized');
}

// Start the app when DOM is ready
document.addEventListener('DOMContentLoaded', init);
