# file: miscelaMultiplayerGame.py

import time
import random
import cv2
from HandDetection import HandGestureTracker
import serial

def selectAudioInput(com,choice): #communication arduino will send here.
    if 1 <= choice <= 17:
        command = f"OA2 {choice}"
        print(command)
        com.write(command.encode())

def delay(seconds):
    print(f"? {seconds} waiting.")
    time.sleep(seconds)
    print("Waiting has just finished.")

class Player:
    def __init__(self, id, is_computer=False):
        self.id = id
        self.is_computer = is_computer
        self.gesture = None  # "Palm" or "Back"
    def __repr__(self):
        return f"Computer" if self.is_computer else f"Player {self.id}"

    @staticmethod
    def get_computer_gesture():
        return True if random.randint(0, 1) % 2 == 0 else False
    
    @staticmethod
    def find_minority_gesture(players,com):
        gestures = []
        for p in players:
            if isinstance(p.gesture, dict) and 'palm' in p.gesture:
                gestures.append(p.gesture['palm'])
            elif isinstance(p.gesture, bool):
                gestures.append(p.gesture)

            if len(gestures) >= len(players):
                break

        print(f"Palm values: {gestures}")

        true_count = 0
        false_count = 0

        for item in gestures:
            if item is True:
                true_count += 1
            elif item is False:
                false_count += 1
    
        print(f"True count: {true_count}")
        print(f"False count: {false_count}")

        if true_count == false_count:
            return None
        elif (true_count == 0 and false_count >= 2) or (true_count >= 2 and false_count == 0):
            return None
        
        if true_count < false_count:
            selectAudioInput(com,12)
            delay(15) 
            return True
        else:
            selectAudioInput(com,9)
            delay(13) 
            return False

    @staticmethod
    def create_players(count):
        players = [Player(i + 1) for i in range(count)]
        computer = Player(id="Computer", is_computer=True)
        players.append(computer)
        return players

    @staticmethod
    def eliminate_minority(players,com): #communication arduino will send here.
        minority = Player.find_minority_gesture(players,com)  # True (palm) or False (behind).Communication arduino will send here.

        if minority is None:
            print("⏸ Equal gestures. Noone will lose.")
            com.write(b'TIE\n') 
            flag = 1
            return players
        elif minority is False:
            selectAudioInput(com,11)
            delay(16)
        elif minority is True:
            selectAudioInput(com,10)
            delay(17)

        eliminated = []
        remaining = []

        for p in players:
            gesture_val = None
            if isinstance(p.gesture, dict) and 'palm' in p.gesture:
                gesture_val = p.gesture['palm']
            elif isinstance(p.gesture, bool):
                gesture_val = p.gesture

            if gesture_val == minority:
                eliminated.append(p)
            else:
                remaining.append(p)

        print(f"❌ Eliminated: {eliminated}")
        print(f"✅ Remaining: {remaining}")
        return remaining

def play_multiplayer_game(com, arduino):
    
    #Testing for the game check with images.
    '''image_paths = [
    "/home/pi/image1.png",
    "/home/pi/image2.png",
    "/home/pi/image3.png",
    "/home/pi/image4.png",
    "/home/pi/image5.png",
    "/home/pi/image6.png",
    "/home/pi/image7.png",
    "/home/pi/image11.png",
    "/home/pi/image11.png",
    "/home/pi/image4.png",
    ]'''

    print("Game starts.")
    #image_index = 0
    secondJoke = 0
    controlMec = True
    controlMec2 = True
    
    arduino.write(b'handShowsSide\n')

    tracker = HandGestureTracker()
    tracker.start_processing()

    players = []
    round_num = 0
    counter = 0


    while True:
        
            processed_img = tracker.get_processed_image()
            
            if processed_img is not None:
                cv2.imshow("Hand Detection", processed_img)
                cv2.waitKey(500)   

            if round_num == 0:
                delay(3) #a little break
                arduino.write(b'startPosition\n')
                delay(0.05)
                print("Hold up your hands Players, if you wanna play.")
                selectAudioInput(com,2)
                delay(9) #until beep
                print("3 seconds start")
                delay(3) 

                result = tracker.get_result()
                time.sleep(0.1)
                print(result)
                delay(3) #a breath for robot

                if result is None and counter < 1:
                    print("El algılanamadı. Tekrar deneyin.")
                    selectAudioInput(com,3)
                    counter += 1
                    delay(3) #lets try once more
                    arduino.write(b'sleepPosition\n')
                    delay(3) #lets try once more
                    continue
                elif result is None and counter == 1:
                    print("Game over")
                    break 
                else:
                    counter = 0

                count, orientations = result
                current_max_hand_number = count
                print("first round sayı: ",current_max_hand_number)

                if count < 2:
                    print("Hands could not detected.")
                    selectAudioInput(com,16)
                    delay(14) #get some friends and 3 second break
                    controlMec = False
                    continue

                players = Player.create_players(count)
                print("🎮 Players:", players)
                round_num += 1
                image_index += 1
                arduino.write(b'sleepPosition\n')
                delay(0.05)
                
                selectAudioInput(com,4)
                delay(10) #joking about machines and robots and a 3second delay

            else:
                arduino.write(b'startPosition\n')
                controlMec2 = True
                print(f"🕹 Round {round_num} show ur hands players. ")
                delay(3)
                selectAudioInput(com,6)
                delay(10) #show your hand back or front
                delay(1.5)
                computer_gesture = Player.get_computer_gesture()
                if computer_gesture:
                    arduino.write(b'handShowsPalm\n')
                else:
                    arduino.write(b'handShowsBack\n')
                delay(0.5)
                delay(1)

                print(players)

                result = tracker.get_result()
                
                if result is None and counter < 1:
                    print("Hands could not detected.")
                    selectAudioInput(com,3)
                    counter += 1
                    delay(2)
                    arduino.write(b'sleepPosition\n')
                    delay(6) #lets try once more
                    continue
                elif result is None and counter == 1:
                    print("Game over")
                    break 
                else:
                    counter = 0
                
                count, orientations = result
                print("Detected hand count: ",count)
                
                if count < 1 and counter < 1:
                    print("Hands could not detected.")
                    selectAudioInput(com,3)
                    counter += 1
                    delay(2)
                    arduino.write(b'sleepPosition\n')
                    delay(6) #lets try once more
                    continue
                elif count < 1 and counter == 1:
                   print("Game over")
                   break 
                else:
                    counter = 0
                    
                arduino.write(b'sleepPosition\n')
                controlMec2 = False
                delay(0.05)

                human_players = len(players) - 1 if players and players[-1].is_computer else len(players)
                #current hand number constraints
                if count > human_players:
                    if counter < 1:
                        print("❌ Detected hands more than player numbers.")
                        selectAudioInput(com,15)
                        image_index += 1
                        delay(11)
                        continue
                    else:
                        print("Game over")
                        break 
                    # El sayısı insan sayısından azsa, Player listesini kes
                elif count < human_players:
                    print("👥 Players:", len(players))
                    current_max_hand_number = count

                    if players and players[-1].is_computer:
                        # Seperate the computer
                        computer = players.pop()
                        print("🧠 Computer deleted:", computer)

                        players = players[:count]

                        # Add computer again.
                        players.append(computer)
                        print("♻️ Computer added:", players)
                    else:
                    #If computer is already lose the game
                        players = players[:count]
                        print("✅ New Players list:", players)
                
                print("New players", players)
                print("orientations::",orientations)
                
                if secondJoke == 0:
                    secondJoke +=1
                    selectAudioInput(com,7)
                    delay(10)
                elif secondJoke == 1:
                    secondJoke +=1
                    selectAudioInput(com,5)
                    delay(11)
                elif secondJoke == 2:
                    secondJoke +=1
                    selectAudioInput(com,8)
                    delay(25)
                
                for i, player in enumerate(players):
                    if not player.is_computer:
                        try:
                            player.gesture = orientations[i]
                            print(f"{player}: {player.gesture}")
                        except IndexError:
                            player.gesture = None
                    else:
                        player.gesture = computer_gesture
                        print(f"{player}: {player.gesture}")
                        
                players = [p for p in players if p.gesture is not None]
                print("Players", players)
                players = Player.eliminate_minority(players,com) #Send Communications arduino
                print(players)
                active_players = [p for p in players if not p.is_computer]
                print("Active players:", players)
                print(active_players)

                if (len(active_players) == 1 and any(p.is_computer for p in players)) or len(players) == 1:
                    print("🎉 Game is over now. Players:", players)
                    print(active_players)
                    selectAudioInput(com,14)
                    delay(15)
                    controlMec = False
                    break
                elif len(active_players) == 2 and not any(p.is_computer for p in players):
                    print("2 Players are left ve computer is already lost.")
                    selectAudioInput(com,13)
                    delay(11)
                    players = Player.create_players(2)
                    current_max_hand_number = 2
                    print(players)
                    print(active_players)

                round_num += 1

    
    tracker.stop_processing()
    tracker.cam.close_camera()
    cv2.destroyAllWindows()

    if controlMec:
        selectAudioInput(com,17)
        delay(17)

    if controlMec2:
        arduino.write(b'sleepPosition\n')
        delay(0.05)
    arduino.close()
    print("🛑 App is ended.")
    
'''if __name__ == "__main__":
    play_multiplayer_game(com, arduino)'''
 
