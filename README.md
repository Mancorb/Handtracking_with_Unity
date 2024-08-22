# Hand Tracking and Gesture Recognition Program

## Overview

This program is designed to track the user's hands using a depth camera, allowing the control of a graphical interface in Unity. It is capable of recognizing simple gestures such as pinching or making a fist, as well as detecting which fingers are flexed, enabling the recognition of more complex hand gestures.

## Features

- **Hand Tracking:** Utilizes a depth camera to accurately track the user's hands in real-time.
- **Gesture Recognition:**
  - **Simple Gestures:** Recognizes basic hand gestures like pinching, making a fist, and open hand.
  - **Finger Flexion Detection:** Identifies which fingers are flexed to recognize more detailed gestures.
- **Unity Integration:** Seamlessly integrates with Unity to control graphical elements and interfaces using hand gestures.

## Prerequisites

- **Hardware:**
  - A depth camera (e.g., Intel RealSense, Azure Kinect, or similar).
  
- **Software:**
  - Unity 2020.3 or later.
  - Depth camera SDK (e.g., RealSense SDK, Azure Kinect SDK, etc.).
  - .NET Framework 4.7.1 or later.

- **Libraries and Dependencies:**
  - Unity XR Interaction Toolkit
  - OpenCV for Unity (optional for advanced image processing)
  - Your depth camera's SDK
