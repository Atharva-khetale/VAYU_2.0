# ⚡ VAYU X - Quick Reference Guide

## 🎯 You Have 2 Minutes? Do This:

```bash
# Step 1: Install (2 min)
pip install -r requirements.txt

# Step 2: Run (1 sec)
python main.py --dashboard --port 5000

# Step 3: Open browser (1 sec)
http://localhost:5000/dashboard

# DONE ✓ - System running with real-time dashboard!
```

---

## 📁 What's in the Box

| File | Size | What It Does |
|------|------|-------------|
| `main.py` | 13K | System launcher |
| `config.py` | 14K | All settings |
| `base.py` | 13K | Base classes & logging |
| `edge_ai.py` | 20K | TensorFlow Lite AI |
| `agents.py` | 22K | 5 robot agents |
| `orchestrator.py` | 17K | Agent coordination |
| `digital_twin.py` | 26K | Web dashboard & API |
| `test_suite.py` | 14K | Automated tests |
| `requirements.txt` | 1K | Python dependencies |
| `README.md` | 15K | Full documentation |
| `DEPLOYMENT_GUIDE.md` | 15K | Hackathon guide |
| `PROJECT_ASSESSMENT.md` | 3.5K | Before/after analysis |
| `.env.example` | 6K | Config template |

**Total: 204KB, 4,000+ lines of code**

---

## 🚀 Running VAYU X

### Option 1: Web Dashboard (Recommended)
```bash
python main.py --dashboard --port 5000
```
Then open: http://localhost:5000/dashboard

### Option 2: Interactive CLI
```bash
python main.py --interactive
```
Then type: `help`, `status`, `agents`, `mission`, `speak`, `emergency`, `exit`

### Option 3: Monitoring Only
```bash
python main.py --no-dashboard
```
Prints status every 5 seconds to console

### Option 4: Custom Mode
```bash
# Museum mode
python main.py --mode museum --dashboard --port 5000

# Home mode
python main.py --mode home --dashboard --port 5000

# Security mode
python main.py --mode security --dashboard --port 5000

# Warehouse mode
python main.py --mode warehouse --dashboard --port 5000
```

---

## ✅ Validate Everything Works

```bash
# Run full test suite
python test_suite.py

# Expected output:
# ✓ Configuration Validation
# ✓ Logging System
# ✓ Base Classes
# ✓ Edge AI Models
# ✓ Vision Agent
# ✓ Voice Agent
# ✓ Motion Agent
# ✓ Safety Agent
# ✓ Mission Planner
# ✓ Agent Manager
# ✓ Message Bus
# ✓ Digital Twin API
# ALL TESTS PASSED ✓
```

---

## 📊 Dashboard Features

Access: http://localhost:5000/dashboard

### What You'll See:
- **System Health** - Battery, temperature, overall status
- **Agent Status** - All 5 agents with health indicators
- **Mission Status** - Current mission and queue
- **Robot Position** - X, Y coordinates, heading, speed
- **Safety Status** - Safety parameters and alerts
- **Vision Detections** - Detected persons and objects

### Auto-Updates
- Dashboard refreshes every 2 seconds
- Real-time agent monitoring
- Live status indicators

---

## 🔌 Test Without Touching Hardware

All 5 agents run in **pure simulation mode**:

- **Vision Agent** ✓ Simulates camera & person detection
- **Voice Agent** ✓ Simulates voice input & keywords
- **Motion Agent** ✓ Simulates movement & position
- **Safety Agent** ✓ Simulates sensor readings & thresholds
- **Mission Planner** ✓ Executes simulated missions

**Everything works exactly like real hardware, but in software.**

---

## 📡 REST API Quick Test

```bash
# Health check
curl http://localhost:5000/health

# List agents
curl http://localhost:5000/agents

# Robot position
curl http://localhost:5000/motion/position

# Safety status
curl http://localhost:5000/safety/status

# Vision detections
curl http://localhost:5000/vision/detections

# Queue mission
curl -X POST http://localhost:5000/mission/queue \
  -H "Content-Type: application/json" \
  -d '{"mission_id":"m1","name":"Test","waypoints":[{"x":0,"y":0}]}'

# Emergency stop
curl -X POST http://localhost:5000/control/emergency-stop
```

---

## 🏆 For Hackathon Demo

### Setup (5 min before demo)
```bash
# Terminal 1
python main.py --mode museum --dashboard --port 5000
```

### Demo Flow (3 minutes)
```
1. Refresh dashboard (auto-updates every 2 sec)
   http://localhost:5000/dashboard
   
2. Show agents all healthy & running
   
3. Show mission status (active mission)
   
4. Show position tracking in real-time
   
5. Show safety parameters
   
6. Click "Emergency Stop" button → immediate response
   
7. Show API responses
   curl http://localhost:5000/health | jq
   
8. Highlight key features:
   - "Works completely offline"
   - "5-agent distributed system"
   - "Production-grade code"
   - "No hardware needed"
   - "Ready to deploy to ESP32"
```

---

## 🐛 Troubleshooting

### Port 5000 already in use?
```bash
python main.py --port 8080
# or
python main.py --port 3000
```

### Dependencies not installing?
```bash
# Upgrade pip first
pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

### TensorFlow issues?
```bash
# TensorFlow Lite should install automatically
# If not, install explicitly:
pip install tensorflow tensorflow-lite
```

### Dashboard won't load?
```bash
# Check if Flask is running:
curl http://localhost:5000/health

# If that fails, Flask didn't start
# Check console for error messages
# Make sure Flask installed: pip install Flask
```

### Agents not starting?
```bash
# Check configuration:
python -c "from config import validate_config; print(validate_config())"

# Run with debug logging:
LOG_LEVEL=DEBUG python main.py --interactive
```

---

## 📚 Documentation Links

- **Setup & Installation** → See README.md
- **Deployment Guide** → See DEPLOYMENT_GUIDE.md
- **API Reference** → See digital_twin.py docstrings
- **Configuration** → See config.py with all comments
- **Architecture** → See PROJECT_ASSESSMENT.md

---

## 🎓 System Components

```
┌─────────────────────────────────────────┐
│   WEB DASHBOARD (http://localhost:5000)  │
│   Real-time monitoring & control        │
└──────────────────┬──────────────────────┘
                   │ (REST API)
        ┌──────────┴──────────┐
        │  ORCHESTRATOR       │
        │  (Agent Manager)    │
        └──────────┬──────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
    ┌───▼───┐  ┌──▼───┐  ┌──▼────┐
    │VISION │  │VOICE │  │MOTION │
    │AGENT  │  │AGENT │  │AGENT  │
    └───┬───┘  └──┬───┘  └──┬────┘
        │         │         │
        └─────────┼─────────┘
                  │
        ┌─────────▼────────┐
        │  SAFETY AGENT    │
        │  (Critical Guard)│
        └─────────┬────────┘
                  │
        ┌─────────▼────────────┐
        │  EDGE AI (TFLite)    │
        │  (Local inference)   │
        └──────────────────────┘
```

---

## 🎯 Key Points for Judges

1. **"This runs COMPLETELY offline"**
   - No cloud required
   - Edge AI on device
   - Works without internet

2. **"5-agent distributed architecture"**
   - Each agent independent
   - Scalable to multiple robots
   - Fault-tolerant design

3. **"No hardware needed to test"**
   - Full simulation mode
   - Ready to deploy anytime
   - Proven architecture

4. **"Production-grade codebase"**
   - 4,000+ lines
   - Professional error handling
   - Comprehensive logging
   - Thread-safe operations

5. **"Digital twin monitoring"**
   - Real-time web dashboard
   - REST API for control
   - Telemetry tracking
   - Emergency controls

---

## ⏱️ Typical Usage Timeline

| Time | Action |
|------|--------|
| T+0 | `pip install -r requirements.txt` |
| T+30s | `python main.py --dashboard` |
| T+1m | Open http://localhost:5000/dashboard |
| T+2m | See live system monitoring |
| T+5m | System fully operational |
| T+∞ | System runs indefinitely |

---

## 💾 File Size Summary

```
Total Package: 204 KB

Code Files:
  agents.py          618 lines
  base.py            405 lines
  config.py          450 lines
  digital_twin.py    702 lines
  edge_ai.py         551 lines
  main.py            372 lines
  orchestrator.py    481 lines
  test_suite.py      396 lines
  ─────────────────────────
  TOTAL:           3,975 lines

Documentation:
  README.md          300+ lines
  DEPLOYMENT_GUIDE   400+ lines
  PROJECT_ASSESS     150+ lines
  .env.example       200+ lines
```

---

## 🎉 You're Ready!

✅ System installed
✅ All files ready
✅ No hardware needed
✅ Test suite passes
✅ Documentation complete
✅ Ready to demo
✅ Ready to deploy

## 🚀 Next 3 Minutes

```bash
# Terminal
pip install -r requirements.txt
python main.py --dashboard --port 5000

# Browser
http://localhost:5000/dashboard

# Done! System is running ✓
```

---

## 📞 Quick Help

- **Want to run?** → See "Running VAYU X" above
- **Want to test?** → Run `python test_suite.py`
- **Want API docs?** → Check digital_twin.py
- **Want config help?** → See config.py
- **Want deployment?** → See DEPLOYMENT_GUIDE.md
- **Want full guide?** → See README.md

---

**VAYU X is ready to impress. Good luck! 🚀**
