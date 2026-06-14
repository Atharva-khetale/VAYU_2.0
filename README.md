# 🤖 VAYU 2.0 — Edge-Native Multi-Agent Autonomous Robotic Guide

<div align="center">

### *Vision Assisted Yaan for Utility*

**An intelligent robotic guide designed for museums, zoos, theme parks, campuses, and public spaces using Edge AI, Multi-Agent Systems, and Real-Time Human Interaction.**

---

🏆 **Evolution of the Award-Winning Original VAYU**

📄 Best Research Paper Award at an International Conference

</div>

---

# 🌟 Overview

VAYU 2.0 is an **Edge-Native Multi-Agent Autonomous Assistance Platform** that acts as an intelligent robotic guide capable of:

* Leading visitors autonomously
* Explaining exhibits and attractions
* Answering questions naturally
* Detecting obstacles and surroundings
* Interacting through voice and vision
* Operating with minimal cloud dependency

Unlike conventional robots that depend heavily on cloud services, **VAYU 2.0 performs sensing, reasoning, and decision-making directly on the device using Edge AI**, enabling low latency, improved privacy, and offline capabilities.

---

# 🏆 About the Original VAYU

The original **VAYU (Vision Assisted Yaan for Utility)** was developed as an intelligent robotic guide for museums and tourist attractions.

### Achievements

✅ Successfully tested prototype

✅ Real-time voice interaction

✅ Exhibit information assistant

✅ Face and object recognition

✅ Best Research Paper Award at an International Conference

---

# 🚀 What's New in VAYU 2.0

VAYU 2.0 is not a simple upgrade.

It is a complete redesign with:

### 🧠 Edge AI Architecture

* AI inference on-device
* Reduced cloud dependency
* Real-time local decision making
* Offline capabilities

### 🤖 Multi-Agent System

Independent agents collaborate for:

* Vision
* Voice
* Motion
* Safety
* Mission Planning

### 🎥 Dedicated Vision Processor

Separate:

* ESP32-S3 → Main Controller
* ESP32-CAM → Vision Controller

This allows:

* Parallel processing
* Better frame rates
* Reduced controller load

### 🔋 Improved Power Architecture

* Battery monitoring
* Buck/Boost regulation
* Dedicated 5V rail
* Dedicated 3.3V rail
* Efficient power distribution

### 📊 Digital Twin & Dashboard

Optional cloud integration:

* Mobile App
* Web Dashboard
* Real-time telemetry
* Remote monitoring

---

# 🎯 Problem Statement

Visitors in museums, zoos, and public attractions often face:

* Difficulty finding exhibits
* Limited interactive guidance
* Language barriers
* Static information boards
* Lack of engaging experiences

VAYU 2.0 aims to provide:

* Autonomous navigation
* Interactive voice assistance
* Personalized information
* Multilingual interaction
* Immersive visitor experiences

---

# ✨ Features

## 🎙 Voice Interaction

* Speech-to-Text
* Text-to-Speech
* Real-time Q&A
* Natural conversations

---

## 🎥 Computer Vision

* Object Detection
* Person Detection
* Face Recognition *(optional)*
* Exhibit Recognition

---

## 🗺 Autonomous Navigation

* Dynamic path following
* Obstacle avoidance
* Guided tours
* Autonomous movement

---

## 🌐 Connectivity

* Wi-Fi
* ESP-NOW
* UART Communication
* Optional MQTT

---

## 🧒 Interactive Experience

* Fun facts
* Jokes
* Stories
* Trivia
* Educational quizzes

---

## 🌍 Multilingual Support

Supports multiple languages for:

* Narration
* Q&A
* Instructions
* Visitor assistance

---

# 🧠 System Architecture

VAYU 2.0 follows an **Edge-Native Multi-Agent Architecture**.

### Agents

### Vision Agent

Responsible for:

* Camera streaming
* Object detection
* Visitor recognition
* Visual understanding

---

### Voice Agent

Responsible for:

* Speech recognition
* Voice commands
* Text-to-speech
* Conversations

---

### Motion Agent

Responsible for:

* Motor control
* Navigation
* Path planning
* Servo movement

---

### Safety Agent

Responsible for:

* Battery monitoring
* Sensor health
* Obstacle awareness
* Emergency stop

---

### Mission Planner

Responsible for:

* Task scheduling
* Agent coordination
* Decision making
* Tour management

---

# 📐 Architecture Diagram

> Insert Architecture Diagram here

```
docs/vayu2_architecture.png
```

---

# ⚡ Electrical Schematic

> Insert Electrical Schematic here

```
docs/vayu2_schematic.png
```

---

# 🔧 Hardware Stack

| Component            | Purpose            |
| -------------------- | ------------------ |
| ESP32-S3             | Main Controller    |
| ESP32-CAM            | Vision Processing  |
| OV2640 Camera        | Visual Input       |
| MPU6050              | IMU Sensor         |
| INA219               | Battery Monitoring |
| INMP441              | I2S Microphone     |
| MAX98357A            | Audio Amplifier    |
| TB6612FNG            | Motor Driver       |
| SG90/MG90S           | Pan-Tilt Servos    |
| Li-ion Battery       | Power Source       |
| TP4056               | Battery Charging   |
| Buck/Boost Converter | Power Regulation   |

---

# 💻 Software Stack

### Languages

* Python
* C++
* Arduino Framework

### AI & Computer Vision

* OpenCV
* TensorFlow Lite
* Edge AI Models

### Communication

* Wi-Fi
* UART
* ESP-NOW
* MQTT *(Optional)*

### Web Technologies

* Flask
* REST API
* HTML/CSS/JavaScript

---

# 📁 Repository Structure

```bash
VAYU_2.0/

├── docs/
│   ├── architecture/
│   │   └── vayu2_architecture.png
│   │
│   └── hardware/
│       └── vayu2_schematic.png
│

├── firmware/
│   ├── esp32_s3/
│   └── esp32_cam/
│

├── software/
│   ├── agents/
│   ├── edge_ai/
│   ├── dashboard/
│   └── api/
│

├── models/
│

├── assets/
│

├── README.md

└── LICENSE
```

---

# 🔌 Hardware Connections

### Main Controller

**ESP32-S3**

Controls:

* Sensors
* Audio
* Motors
* Servos
* Communication

---

### Vision Controller

**ESP32-CAM**

Handles:

* Camera streaming
* Object detection
* Visual inference

Communicates with:

* UART
* ESP-NOW

---

# 🧪 Current Prototype Status

### Completed

✅ Architecture Design

✅ Electrical Schematic

✅ Power Management Design

✅ Multi-Agent Architecture

✅ Edge AI Framework

✅ Audio System

✅ Motion System

✅ Sensor Integration

---

# 🌍 Applications

VAYU 2.0 can be deployed in:

* Museums
* Zoos
* Theme Parks
* Science Centers
* Airports
* Railway Stations
* Universities
* Smart Campuses
* Hospitals
* Corporate Buildings

---

# 🔮 Future Scope

Future enhancements include:

* Custom PCB Design
* ROS2 Integration
* SLAM-based Navigation
* Large Language Model Integration
* Gesture Recognition
* Autonomous Charging Dock
* Swarm Robot Coordination
* Cloud-based Fleet Management

---

# 🏅 Achievements

🏆 Best Research Paper Award (Original VAYU)

🚀 Selected for FAR AWAY 2026

🤖 Edge-Native Multi-Agent Robotic Platform

---

<div align="center">

### "Not just a robot.

### An intelligent companion that guides, explains, learns, and evolves."

**VAYU 2.0 — Vision Assisted Yaan for Utility**

🚀 Edge AI • Multi-Agent • Autonomous Systems

</div>
