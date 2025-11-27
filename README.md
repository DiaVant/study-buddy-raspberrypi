# rPPG and Pomodoro Study Buddy powered by Raspberry Pi
A study companion that combines remote heart rate monitoring with an adaptive Pomodoro timer to promote healthier and more effective studying. Using rPPG technology through the Pi camera, the system passively tracks the user’s pulse, delivering intelligent break reminders. Calm mode delivers guided box breathing through blue visual cues and a handheld motor pulsing at 60 BPM. This multi-sensory feedback helps users regulate breathing, lower heart rate, and transition out of high-stress states. Pomodoro focus mode is completely customizable and features study sound tracks.

<p align="center">
  <img src="SS/piSetup.JPEG" alt="Pi-setup" width=600/>
</p>

## [rPPG Technology Monitoring](https://noldus.com/blog/what-is-rppg): Remoately tracks cardiac activity through Pi Camera to assess stress and exertion levels.
- Remote Photoplethysmography (rPPG) measures heart rate using a multi-wavelength RGB camera by detecting subtle changes in skin color caused by each pulse. 
- Uses OpenCV and Pi Camera
- Adapts and customizees [HeartPi model](https://github.com/ganeshkumartk/heartpi) by Ganesh Kumar T K
<p align="center">
  <img src="SS/rPPG_diagram.png?raw=true" alt="Pi-camera" width="400" height="900"/>
</p>
<h5 align="center"> 
  <a href="https://github.com/ganeshkumartk/heartpi">HeartPi</a> Algorithm Breakdown: rPPG Implementation via Blind Source seperation (PCA & FastICA) </h5>

### Intelligent Break Reminders
- Constnatly monitors heartrate, checking every 30 seconds for age-adjusted elevated readings
- Warning LEDs notifies user to take a break

### Calm Mode
- Mini handheld motor pulsing at 60bpm
- Blue lights guide users through the box breathing technique
- Activated any time by the press of a button, all timers are paused

### Focus Mode
- Completely customizable pomodoro clock (study time, break time, cycles)
- Featuring 3 Original Soundtracks by Ted Dixon-kraegel (cycle tracks by the press of a button)
  - Chilling in the Rain (calm 
  - Joyful Trills
  - Pirate Thunder

<br>

## Usage
1. Follow [these instructions](https://github.com/ganeshkumartk/heartpi/tree/master?tab=readme-ov-file#usage) to setup HeartPi
2. Replace 'Heartrate.py' with the modified version from this repository
3. Download the remainder of this respository onto your raspberry pi
