# Coffee Bot

A Raspberry Pi Zero W project to remotely "press" the physical buttons on a coffee maker using solenoids and a motor driver.

### None of this has actually been tested yet, so I wouldn't try to use it, I don't really know what I'm doing.

## Hardware
- **Controller:** Raspberry Pi Zero W
- **Driver:** Waveshare Motor Driver HAT
- **Actuators:** 2x Mini Push-Pull Solenoids (DS-0420S)
- **Power:** 9V 2A DC Power Supply (PWM throttled via software)

## Pinout Mapping
The Waveshare Motor Driver HAT uses the following GPIO (BCM):

| Component | Function | GPIO Pin |
| :--- | :--- | :--- |
| **Solenoid A (Power)** | PWM (Speed) | 21 |
| **Solenoid A (Power)** | IN2 (Direction) | 20 |
| **Solenoid B (Brew)** | PWM (Speed) | 16 |
| **Solenoid B (Brew)** | IN2 (Direction) | 19 |

## Getting Started
1. **Clone the repo to your Pi:**  
   ```
   git clone https://github.com/NinjaGeoff/coffee_bot.git
   cd coffee_bot
   ```

2. **Install dependencies:**  
   `pip install flask`

3. **Run the Web UI:**  
   `python3 coffee_web.py`  

4. **Access the controls at**  
    `http://<your-pi-ip>:5000`  

## Safety Note
The solenoids are rated for 3V-5V. The software uses a PWM Duty Cycle of 33% to step down the 9V power supply to a safe level (~3V).