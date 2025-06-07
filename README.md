# Robotics and Design

Project of the XIII edition of the Robotics and Design Course, A.Y. 2024-2025.

## Module Outdoor Actuation 2 
- **Yalçın Erdal**, School Of Industrial And Information Engineering.
- **Martini Marcello**, School Of Design.
## Project Overview
This repository documents contains the work developed by the **Actuation 2** group as part of the **Outdoor Module** for **BB2** — the robotic mascot designed to interact with students in the open area of Bovisa campus. While BB2 engages users through various activities, our team was responsible for designing and building a robotic arm that plays **Miscela**, a multi-action game designed to provide real-time, engaging interactions.

The gameplay is triggered by signals received through the **Communication Module**, which manages inter-module coordination and initializes the game session. The game operates in real time, allowing dynamic interaction between the user and the robot.

Our system communicates with the Communication Module via a **Raspberry Pi**, which also handles audio output to guide the player through the game phases. The robotic behavior is thus both reactive and expressive, thanks to synchronized actuation and sound cues.

The entire game logic is distributed across two main Python scripts:

- One script manages the overall game architecture, including logic flow and hardware coordination.
- The second script handles the camera thread, performing continuous hand detection and gesture analysis.
  
This modular setup allows for efficient execution of both visual recognition and motor responses, enabling the robot to participate in the game in an intelligent and responsive manner.

## Informatics
### System Requirements 

The hand recognition functionality of this project is powered by **MediaPipe**, a library developed by Google for extracting hand landmarks from live video. Please ensure that your **Python** version is **3.11** or **earlier**, as newer versions may lead to compatibility issues with **MediaPipe**.

If you're setting up the environment manually, you'll need to install the following Python packages:

<pre> pip install opencv-python
 pip install cvzone
 pip install mediapipe
 pip install numpy
 pip install pyserial </pre>

For those using the **Raspberry Pi** setup provided with the project, all necessary libraries are already installed within a virtual environment. You can activate this environment by running:

<pre> source venv/bin/activate</pre>

You can then run any python script inside the virtual environment:

<pre> python OA2.py </pre>

### Delivered Files

- [actuationContols](https://github.com/yalcinerdal/roboticsDesignGame/tree/main/actuationControls) : This folder contains the Arduino code and schema responsible for controlling the robotic arm through dedicated a servo and stepper motor. It receives serial commands to move the hand (palm, back, side) and rotate the arm forward or backward. Microstepping settings allow precise motor control. Commands trigger smooth, timed movements for accurate positioning.

- [HandDetection.py](https://github.com/yalcinerdal/roboticsDesignGame/blob/main/HandDetection.py) : This file contains the main function play_rock_paper_scissors() that runs the Rock-Paper-Scissors interaction between the user and the robotic arm.

	The implementation includes:

	🖐️ **HandController**

	Supports tracking of up to 8 hands concurrently.

	- `detect_finger_states()` : Estimates the open/closed state of fingers using landmark positions.

	- `is_hand_up()`: Determines whether the hand is raised above the wrist level.

	- `detect_hand_orientation()` : Estimates palm orientation based on thumb-pinky spatial relationship.

	- `analyze_hands()` : Processes input frames and returns right-hand count, palm states, and annotated image.

	📸 **CameraHandler**

	Manages real-time frame capture from the raspberry camera in a thread-safe manner. Supports live preview in a background thread.

	- `turn_on_camera()`: Starts the camera and thread.
  
	- `_update()`: Captures and updates frames continuously.
   
	- `read_frame()`: Returns the latest captured frame (thread-safe).
   
	- `show_frame()`: Displays the frame for the testing part for programmer.
   
	- `close_camera()`: Releases and closes the camera. 

	👀 **HandGestureTracker (Threaded)**

	HandGestureTracker connects HandController and CameraHandler to perform real-time hand tracking. It runs analysis in a background thread to keep the UI responsive. It provides thread-safe access to detection results, hand orientations, and processed frames. It also supports pausing, resuming, and adjusting the maximum hand count dynamically.

- [OA2.py](https://github.com/yalcinerdal/roboticsDesignGame/blob/main/OA2.py) :

	This file implements a multiplayer hand-gesture-based elimination game integrating computer vision and physical interaction. It uses HandGestureTracker file for gesture recognition, and serial communication to interface with an Arduino-controlled physical actuation system. Key elements include:

	- `Player class` : Represents human or computer players; handles gesture assignment and minority detection.

	- `play_multiplayer_game()` : Orchestrates the game loop—detects hand gestures, determines the minority gesture (palm or back of hand), and eliminates players accordingly.

	- `Arduino integration` : Communicates audio and mechanical feedback based on game state ( `selectAudioInput` , `arduino.write()` ).


