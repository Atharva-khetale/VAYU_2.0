"""
VAYU X - Digital Twin Backend
Flask REST API for real-time monitoring and control
Production-grade web service for dashboard
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import json
import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from orchestrator import VAYUOrchestrator
from base import get_logger, get_telemetry, get_metric_stats
from config import ROBOT, DEPLOYMENT_MODE, ENVIRONMENT

# ============================================================================
# FLASK APPLICATION SETUP
# ============================================================================

app = Flask(__name__)
CORS(app)

# Global orchestrator instance
orchestrator: Optional[VAYUOrchestrator] = None

# Logging configuration for Flask
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logger = get_logger("DigitalTwin")

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_system():
    """Initialize VAYU X system on startup"""
    global orchestrator
    try:
        orchestrator = VAYUOrchestrator()
        if orchestrator.initialize():
            logger.info("✓ VAYU X system initialized")
            return True
        else:
            logger.error("✗ System initialization failed")
            return False
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        return False

# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """
    System health check endpoint
    Returns system status, agent health, and operational metrics
    """
    try:
        if not orchestrator:
            return jsonify({"error": "System not initialized"}), 503
        
        status = orchestrator.get_status()
        
        return jsonify({
            "status": "healthy" if status["context"]["is_healthy"] else "degraded",
            "robot_id": status["robot_id"],
            "timestamp": time.time(),
            "deployment_mode": status["deployment_mode"],
            "agent_count": status["agent_count"],
            "agents_healthy": sum(1 for a in status["agents"].values() if a["is_healthy"]),
            "context": status["context"]
        }), 200
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def get_system_status():
    """Get detailed system status"""
    try:
        if not orchestrator:
            return jsonify({"error": "System not initialized"}), 503
        
        status = orchestrator.get_status()
        
        return jsonify({
            "robot_id": status["robot_id"],
            "deployment_mode": status["deployment_mode"],
            "timestamp": time.time(),
            "context": status["context"],
            "agents": status["agents"],
            "edge_ai": status["edge_ai"]
        }), 200
    
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/agents', methods=['GET'])
def get_agents():
    """Get list of all agents and their status"""
    try:
        if not orchestrator:
            return jsonify({"error": "System not initialized"}), 503
        
        agents = orchestrator.agent_manager.get_all_agents()
        
        agent_list = [
            {
                "agent_id": agent.agent_id,
                "agent_type": agent.agent_type,
                "status": agent.get_status()
            }
            for agent in agents.values()
        ]
        
        return jsonify({
            "agents": agent_list,
            "total_agents": len(agent_list),
            "timestamp": time.time()
        }), 200
    
    except Exception as e:
        logger.error(f"Agents error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/agent/<agent_id>', methods=['GET'])
def get_agent(agent_id: str):
    """Get specific agent status and metrics"""
    try:
        if not orchestrator:
            return jsonify({"error": "System not initialized"}), 503
        
        agent = orchestrator.agent_manager.get_agent(agent_id)
        if not agent:
            return jsonify({"error": f"Agent not found: {agent_id}"}), 404
        
        return jsonify({
            "agent_id": agent.agent_id,
            "agent_type": agent.agent_type,
            "status": agent.get_status(),
            "timestamp": time.time()
        }), 200
    
    except Exception as e:
        logger.error(f"Agent error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/telemetry', methods=['GET'])
def get_telemetry_data():
    """Get system telemetry events"""
    try:
        since = request.args.get('since', type=float)
        events = get_telemetry(since)
        
        return jsonify({
            "events": [e.to_dict() for e in events],
            "count": len(events),
            "timestamp": time.time()
        }), 200
    
    except Exception as e:
        logger.error(f"Telemetry error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/metrics/<agent_id>/<metric_name>', methods=['GET'])
def get_metrics(agent_id: str, metric_name: str):
    """Get performance metrics for an agent"""
    try:
        stats = get_metric_stats(agent_id, metric_name)
        
        if not stats:
            return jsonify({"error": f"No metrics found"}), 404
        
        return jsonify({
            "agent_id": agent_id,
            "metric_name": metric_name,
            "statistics": stats,
            "timestamp": time.time()
        }), 200
    
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mission/queue', methods=['GET'])
def get_mission_queue():
    """Get current mission queue and status"""
    try:
        if not orchestrator:
            return jsonify({"error": "System not initialized"}), 503
        
        mission_agent = orchestrator.agent_manager.get_agent("mission_001")
        if not mission_agent:
            return jsonify({"error": "Mission planner not found"}), 404
        
        mission_status = mission_agent.get_mission_status()
        
        return jsonify({
            "current_mission": mission_status.get("current_mission"),
            "waypoint_index": mission_status.get("waypoint_index"),
            "queued_missions": mission_status.get("queued_missions"),
            "completed_missions": mission_status.get("completed_missions"),
            "timestamp": time.time()
        }), 200
    
    except Exception as e:
        logger.error(f"Mission queue error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mission/queue', methods=['POST'])
def queue_mission():
    """Queue a new mission"""
    try:
        if not orchestrator:
            return jsonify({"error": "System not initialized"}), 503
        
        data = request.get_json()
        mission_agent = orchestrator.agent_manager.get_agent("mission_001")
        
        if not mission_agent:
            return jsonify({"error": "Mission planner not found"}), 404
        
        # Create and queue mission
        from agents import Mission
        mission = Mission(
            mission_id=data.get("mission_id", f"mission_{int(time.time())}"),
            name=data.get("name", "Unnamed Mission"),
            description=data.get("description", ""),
            waypoints=data.get("waypoints", []),
            deployment_mode=data.get("deployment_mode", DEPLOYMENT_MODE)
        )
        
        mission_agent.queue_mission(mission)
        
        return jsonify({
            "status": "mission_queued",
            "mission_id": mission.mission_id,
            "timestamp": time.time()
        }), 201
    
    except Exception as e:
        logger.error(f"Queue mission error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/vision/detections', methods=['GET'])
def get_vision_detections():
    """Get latest vision detections"""
    try:
        if not orchestrator:
            return jsonify({"error": "System not initialized"}), 503
        
        vision_agent = orchestrator.agent_manager.get_agent("vision_001")
        if not vision_agent:
            return jsonify({"error": "Vision agent not found"}), 404
        
        detections = vision_agent.get_detections()
        
        return jsonify({
            "detections": detections,
            "count": len(detections),
            "timestamp": time.time()
        }), 200
    
    except Exception as e:
        logger.error(f"Vision detections error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/motion/position', methods=['GET'])
def get_motion_position():
    """Get robot current position and movement"""
    try:
        if not orchestrator:
            return jsonify({"error": "System not initialized"}), 503
        
        motion_agent = orchestrator.agent_manager.get_agent("motion_001")
        if not motion_agent:
            return jsonify({"error": "Motion agent not found"}), 404
        
        position = motion_agent.get_position()
        
        return jsonify({
            "position": position,
            "timestamp": time.time()
        }), 200
    
    except Exception as e:
        logger.error(f"Motion position error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/safety/status', methods=['GET'])
def get_safety_status():
    """Get safety status"""
    try:
        if not orchestrator:
            return jsonify({"error": "System not initialized"}), 503
        
        safety_agent = orchestrator.agent_manager.get_agent("safety_001")
        if not safety_agent:
            return jsonify({"error": "Safety agent not found"}), 404
        
        safety_status = safety_agent.get_safety_status()
        
        return jsonify({
            "safety": safety_status,
            "is_safe": safety_status["is_safe"],
            "timestamp": time.time()
        }), 200
    
    except Exception as e:
        logger.error(f"Safety status error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# CONTROL ENDPOINTS
# ============================================================================

@app.route('/control/emergency-stop', methods=['POST'])
def emergency_stop():
    """Trigger emergency stop"""
    try:
        if not orchestrator:
            return jsonify({"error": "System not initialized"}), 503
        
        safety_agent = orchestrator.agent_manager.get_agent("safety_001")
        if safety_agent:
            safety_agent.emergency_stop_active = True
        
        motion_agent = orchestrator.agent_manager.get_agent("motion_001")
        if motion_agent:
            from agents import MotionCommand
            cmd = MotionCommand(action="stop", speed=0, duration=0)
            motion_agent.queue_command(cmd)
        
        logger.warning("EMERGENCY STOP triggered")
        
        return jsonify({
            "status": "emergency_stop_activated",
            "timestamp": time.time()
        }), 200
    
    except Exception as e:
        logger.error(f"Emergency stop error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/control/voice', methods=['POST'])
def voice_control():
    """Send voice command"""
    try:
        data = request.get_json()
        text = data.get("text", "")
        
        if not text:
            return jsonify({"error": "Text required"}), 400
        
        voice_agent = orchestrator.agent_manager.get_agent("voice_001")
        if voice_agent:
            voice_agent.speak(text)
        
        return jsonify({
            "status": "voice_command_sent",
            "text": text,
            "timestamp": time.time()
        }), 200
    
    except Exception as e:
        logger.error(f"Voice control error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# WEB DASHBOARD
# ============================================================================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VAYU X Digital Twin Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .header h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .header .info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .info-card {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        .card {
            background: rgba(255,255,255,0.95);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 18px;
        }
        .status {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
            margin: 8px 0;
        }
        .status-label {
            font-weight: bold;
            color: #333;
        }
        .status-value {
            color: #667eea;
            font-weight: bold;
        }
        .status.healthy .status-value { color: #27ae60; }
        .status.warning .status-value { color: #f39c12; }
        .status.error .status-value { color: #e74c3c; }
        .button {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
            transition: background 0.3s;
        }
        .button:hover { background: #764ba2; }
        .button.danger {
            background: #e74c3c;
        }
        .button.danger:hover {
            background: #c0392b;
        }
        .agents-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .agent-badge {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .agent-badge.healthy { border-left-color: #27ae60; }
        .agent-badge.warning { border-left-color: #f39c12; }
        .agent-badge.error { border-left-color: #e74c3c; }
        .chart-container {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
        }
        .loading {
            text-align: center;
            color: #667eea;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 VAYU X - Digital Twin Dashboard</h1>
            <div class="info">
                <div class="info-card">
                    <strong>Robot ID:</strong> <span id="robot-id">Loading...</span>
                </div>
                <div class="info-card">
                    <strong>Status:</strong> <span id="system-status">Loading...</span>
                </div>
                <div class="info-card">
                    <strong>Deployment Mode:</strong> <span id="deployment-mode">Loading...</span>
                </div>
                <div class="info-card">
                    <strong>Agents:</strong> <span id="agent-count">Loading...</span>
                </div>
            </div>
        </div>

        <div class="grid">
            <!-- System Health -->
            <div class="card">
                <h2>🏥 System Health</h2>
                <div id="health-status" class="loading">Loading...</div>
                <button class="button danger" onclick="emergencyStop()">🛑 Emergency Stop</button>
            </div>

            <!-- Agents Status -->
            <div class="card">
                <h2>👥 Agents Status</h2>
                <div id="agents-status" class="agents-list loading">Loading...</div>
            </div>

            <!-- Mission Status -->
            <div class="card">
                <h2>🎯 Mission Status</h2>
                <div id="mission-status" class="loading">Loading...</div>
            </div>

            <!-- Robot Position -->
            <div class="card">
                <h2>📍 Robot Position</h2>
                <div id="position-status" class="loading">Loading...</div>
            </div>

            <!-- Safety Status -->
            <div class="card">
                <h2>⚠️ Safety Status</h2>
                <div id="safety-status" class="loading">Loading...</div>
            </div>

            <!-- Vision -->
            <div class="card">
                <h2>👁️ Vision Detections</h2>
                <div id="vision-status" class="loading">Loading...</div>
            </div>
        </div>
    </div>

    <script>
        async function updateDashboard() {
            try {
                // Fetch health
                const healthRes = await fetch('/health');
                const health = await healthRes.json();
                
                document.getElementById('robot-id').textContent = health.robot_id;
                document.getElementById('system-status').textContent = health.status.toUpperCase();
                document.getElementById('deployment-mode').textContent = health.deployment_mode.toUpperCase();
                document.getElementById('agent-count').textContent = health.agents_healthy + '/' + health.agent_count;

                // Update health card
                let healthHtml = '<div class="status ' + health.status + '"><span class="status-label">Overall:</span><span class="status-value">' + health.status.toUpperCase() + '</span></div>';
                healthHtml += '<div class="status"><span class="status-label">Battery:</span><span class="status-value">' + health.context.battery_percentage + '%</span></div>';
                healthHtml += '<div class="status"><span class="status-label">Temperature:</span><span class="status-value">' + health.context.temperature_celsius.toFixed(1) + '°C</span></div>';
                document.getElementById('health-status').innerHTML = healthHtml;

                // Fetch and update agents
                const agentsRes = await fetch('/agents');
                const agents = await agentsRes.json();
                
                let agentsHtml = '';
                for (const agent of agents.agents) {
                    const statusClass = agent.status.is_healthy ? 'healthy' : (agent.status.error_count > 5 ? 'error' : 'warning');
                    agentsHtml += '<div class="agent-badge ' + statusClass + '">';
                    agentsHtml += '<span><strong>' + agent.agent_id + '</strong> (' + agent.agent_type + ')</span>';
                    agentsHtml += '<span>' + (agent.status.is_healthy ? '✓' : '✗') + '</span>';
                    agentsHtml += '</div>';
                }
                document.getElementById('agents-status').innerHTML = agentsHtml;

                // Fetch mission status
                const missionRes = await fetch('/mission/queue');
                const mission = await missionRes.json();
                let missionHtml = '<div class="status"><span class="status-label">Current:</span><span class="status-value">' + (mission.current_mission || 'None') + '</span></div>';
                missionHtml += '<div class="status"><span class="status-label">Queued:</span><span class="status-value">' + mission.queued_missions + '</span></div>';
                missionHtml += '<div class="status"><span class="status-label">Completed:</span><span class="status-value">' + mission.completed_missions + '</span></div>';
                document.getElementById('mission-status').innerHTML = missionHtml;

                // Fetch position
                const posRes = await fetch('/motion/position');
                const pos = await posRes.json();
                let posHtml = '<div class="status"><span class="status-label">X:</span><span class="status-value">' + pos.position.x.toFixed(2) + ' m</span></div>';
                posHtml += '<div class="status"><span class="status-label">Y:</span><span class="status-value">' + pos.position.y.toFixed(2) + ' m</span></div>';
                posHtml += '<div class="status"><span class="status-label">Heading:</span><span class="status-value">' + pos.position.heading.toFixed(1) + '°</span></div>';
                posHtml += '<div class="status"><span class="status-label">Speed:</span><span class="status-value">' + pos.position.speed.toFixed(2) + ' m/s</span></div>';
                document.getElementById('position-status').innerHTML = posHtml;

                // Fetch safety
                const safetyRes = await fetch('/safety/status');
                const safety = await safetyRes.json();
                let safetyHtml = '<div class="status ' + (safety.is_safe ? 'healthy' : 'error') + '"><span class="status-label">Safe:</span><span class="status-value">' + (safety.is_safe ? 'YES' : 'NO') + '</span></div>';
                safetyHtml += '<div class="status"><span class="status-label">Battery:</span><span class="status-value">' + safety.safety.battery_voltage.toFixed(2) + 'V</span></div>';
                safetyHtml += '<div class="status"><span class="status-label">Temperature:</span><span class="status-value">' + safety.safety.temperature_celsius.toFixed(1) + '°C</span></div>';
                document.getElementById('safety-status').innerHTML = safetyHtml;

                // Fetch vision
                const visionRes = await fetch('/vision/detections');
                const vision = await visionRes.json();
                let visionHtml = '<div class="status"><span class="status-label">Detections:</span><span class="status-value">' + vision.count + '</span></div>';
                if (vision.detections.length > 0) {
                    visionHtml += '<div class="chart-container">';
                    for (const det of vision.detections.slice(0, 3)) {
                        visionHtml += '<div style="padding: 5px;"><strong>' + det.class_name + '</strong> - ' + (det.confidence * 100).toFixed(1) + '%</div>';
                    }
                    visionHtml += '</div>';
                }
                document.getElementById('vision-status').innerHTML = visionHtml;

            } catch (error) {
                console.error('Error:', error);
            }
        }

        function emergencyStop() {
            if (confirm('Trigger EMERGENCY STOP? This will immediately halt all robot movement.')) {
                fetch('/control/emergency-stop', { method: 'POST' })
                    .then(r => r.json())
                    .then(data => {
                        alert('Emergency stop activated!');
                        updateDashboard();
                    });
            }
        }

        // Update every 2 seconds
        updateDashboard();
        setInterval(updateDashboard, 2000);
    </script>
</body>
</html>
"""

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Serve web dashboard"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/', methods=['GET'])
def root():
    """Redirect to dashboard"""
    return render_template_string(DASHBOARD_HTML)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting VAYU X Digital Twin Backend...")
    
    # Initialize system
    if initialize_system():
        logger.info("Starting Flask application on http://localhost:5000")
        logger.info("Dashboard available at http://localhost:5000/dashboard")
        
        # Run Flask app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=(ENVIRONMENT == "development"),
            use_reloader=False  # Prevent double initialization
        )
    else:
        logger.error("Failed to initialize VAYU X system")
