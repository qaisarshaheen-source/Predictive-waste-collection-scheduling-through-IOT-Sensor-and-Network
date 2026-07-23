# Predictive Waste Collection Scheduling Through IoT Sensor and Network Optimization

**Smart Waste Bin (SWB) — Project Documentation**

## 1. Project Overview

This project presents a Smart Waste Bin (SWB), an IoT-enabled waste management system that combines AI-based visual waste classification, automated mechanical segregation, real-time fill-level sensing, and predictive network optimization. The system classifies waste into plastic, paper/wrapper, and glass, directs each item to the appropriate compartment, monitors bin capacity, and notifies waste-management authorities when collection is required.

![Smart Bin Fill Level](images/smart%20bin%20fill%20level.jpeg)

## 2. Problem Statement

Traditional waste collection often relies on manual segregation and fixed collection routes. This causes mixed recyclable waste, overflowing bins, unnecessary collection trips, fuel consumption, and inefficient use of municipal resources. The SWB addresses these problems by combining automated segregation with real-time monitoring and demand-driven collection.

## 3. Objectives

- Automate identification and segregation of plastic, paper/wrapper, and glass waste.
- Use servo motors to actuate the correct compartment or lid.
- Monitor compartment fill levels in real time using HC-SR04 ultrasonic sensors.
- Send alerts containing bin status, waste type, and location information.
- Use predictive modeling to reduce network congestion and improve telemetry delivery.
- Support demand-based waste collection and reduce unnecessary collection journeys.

## 4. System Architecture

The architecture follows a modular **Sense → Think → Act** model:

- **Perception Layer:** camera/ESP32-CAM or Pi Camera and ultrasonic sensors collect visual and fill-level data.
- **Cognitive Layer:** cloud AI/API or CNN-based processing classifies waste; predictive ML analyzes telemetry and congestion risk.
- **Execution Layer:** Arduino/microcontroller controls servo motors, sensing, alerts, and communication.
- **Communication Layer:** GSM/GPRS and GPS provide remote status reporting and location-aware alerts.
- **Power Layer:** regulated 5V control/actuation supply with LM2596 regulation and battery backup for selected components.

![Modular Sense-Think-Act Architecture](images/Modular%20sense%20think%20act%20architecture.jpeg)

## 5. System Workflow

1. User deposits waste.
2. Camera captures an image of the waste item.
3. AI service classifies the item as plastic, paper/wrapper, or glass.
4. Microcontroller receives the classification result.
5. The corresponding servo motor opens or actuates the correct compartment.
6. HC-SR04 sensors continuously estimate fill levels.
7. When a compartment reaches the configured full threshold, an alert is generated.
8. GSM/GPS communication transmits the bin ID, waste type/status, and location.
9. Predictive network scheduling staggers transmissions to reduce congestion and improve collection planning.

![System Workflow](images/System%20workflow.jpeg)

## 6. Hardware and Software Components

- Arduino Uno / microcontroller
- Camera module or USB webcam
- Three servo motors for plastic, paper, and glass compartments
- Three HC-SR04 ultrasonic sensors
- SIM800L/SIM808 GSM/GPRS communication module
- GPS module such as NEO-6M/7M
- LM2596 step-down switching regulator
- Pushbutton, status LED, buzzer, wiring, and power supply
- Cloud AI/API or CNN-based image classification
- Machine-learning models: Random Forest, XGBoost, Decision Tree, and Logistic Regression

![Component to MCU System Mapping](images/component%20to%20MCU%20system%20mapping.jpeg)

## 7. AI and Predictive Network Model

A 500-row telemetry dataset was used to evaluate supervised learning algorithms for congestion prediction. Random Forest was selected as the preferred model, achieving the highest reported accuracy (96.8%) and recall (0.97). The predictive network strategy uses bin capacity and telemetry information to stagger transmissions rather than allowing simultaneous alert bursts.

![Training and Validation Graph](images/Training%20and%20validation%20graph.jpeg)

## 8. Key Results

- **Random Forest:** 96.8% accuracy, 0.96 precision, 0.97 recall, 0.96 F1-score.
- Average network latency decreased from 155 ms to 52 ms.
- Packet delivery ratio increased from 91.5% to 99.6%.
- Reported congestion events decreased from 14/day to 1/day.
- Validation loss reached 0.065 at the end of the evaluated curve.
- The prototype supports demand-driven collection and can reduce overflow and unnecessary collection trips.

![Performance Gains Graph](images/Performance%20gains%20graph.jpeg)

## 9. Applications

- Smart cities and municipal waste management
- Schools, universities, and offices
- Hospitals, shopping malls, railway stations, and airports
- Industrial and corporate campuses
- Public parks and residential areas

## 10. Constraints and Deployment Considerations

- Estimated total power draw: approximately 12–15 W idle and 22–30 W peak.
- Reported total prototype cost: approximately PKR 60,000–67,000, excluding variable ongoing API usage.
- Operating temperature: 0°C–50°C.
- IP65-style enclosure is recommended for dust/humidity protection.
- Reported prototype dimensions are approximately 70 cm × 50 cm × 100 cm, with an estimated weight of 15–20 kg.
- Cloud-based image classification introduces network dependency and reported response times of approximately 4–7 seconds.
- Regular cleaning of sensors/camera and electrical inspection are required.

## 11. Future Work

- Integrate renewable power, particularly solar energy, for outdoor autonomous deployment.
- Move more AI inference to edge devices to reduce latency and dependence on internet connectivity.
- Improve scalability for city-wide deployment and larger fleets of smart bins.
- Strengthen model robustness across lighting, weather, camera angles, and occlusion conditions.
- Integrate GIS-based route optimization and municipal dashboards for automated collection planning.

## 12. Abbreviations

| Abbreviation | Full Form |
|---|---|
| AI | Artificial Intelligence |
| API | Application Programming Interface |
| CNN | Convolutional Neural Network |
| ESP32 | Espressif 32-bit Microcontroller |
| GIS | Geographic Information System |
| GSM | Global System for Mobile Communications |
| GPS | Global Positioning System |
| HC-SR04 | Ultrasonic Distance Sensor Module |
| IoT | Internet of Things |
| MCU | Microcontroller Unit |
| PWM | Pulse Width Modulation |
| SMS | Short Message Service |
| VCC | Voltage at the Common Collector |
| GND | Ground |

## 13. Source Document

Prepared from the thesis/document titled *"Predictive Waste Collection Scheduling Through IoT Sensor and Network Optimization."*
