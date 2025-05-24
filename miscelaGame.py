import time
import random
import cv2
from handdetect import HandGestureTracker
import serial

image_paths = [
    "/Users/erdalyalcin/Desktop/image1.png",
    "/Users/erdalyalcin/Desktop/image2.png",
    "/Users/erdalyalcin/Desktop/image2.png",
    "/Users/erdalyalcin/Desktop/image2.png",
    "/Users/erdalyalcin/Desktop/image10.png",
    "/Users/erdalyalcin/Desktop/image3.png",
    "/Users/erdalyalcin/Desktop/image11.png",
    "/Users/erdalyalcin/Desktop/image11.png",
    "/Users/erdalyalcin/Desktop/image11.png",
    "/Users/erdalyalcin/Desktop/image4.png",
]

image_index = 0
flag = 0

current_max_hands = None

class Player:
    def __init__(self, id, is_computer=False):
        self.id = id
        self.is_computer = is_computer
        self.gesture = None  # "Avuç İçi" veya "Elin Tersi"
    def __repr__(self):
        return f"Computer" if self.is_computer else f"Player {self.id}"

    @staticmethod
    def get_computer_gesture():
        return True if random.randint(0, 1) % 2 == 0 else False
    
    @staticmethod
    def find_minority_gesture(players):
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
    
        print(f"True sayısı: {true_count}")
        print(f"False sayısı: {false_count}")

        if true_count == false_count:
            return None  

        return True if true_count < false_count else False  #True:palm

    @staticmethod
    def create_players(count):
        players = [Player(i + 1) for i in range(count)]
        computer = Player(id="Computer", is_computer=True)
        players.append(computer)
        return players

    @staticmethod
    def eliminate_minority(players,flag):
        minority = Player.find_minority_gesture(players)  # True (palm) or False (behind)

        if minority is None:
            print("⏸ Eşitlik var, kimse elenmiyor bu tur.")
            flag = 1
            return players

    # Elenenleri belirle: gesture True/False olabilir veya {'palm': True/False}
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

        print(f"❌ Elenenler: {eliminated}")
        print(f"✅ Kalanlar: {remaining}")
        return remaining



if __name__ == "__main__":
    '''cam = CameraHandler()
    if not cam.turn_on_camera():
        print("Kamera açılamadı.")
        exit(1)'''
    try:
        # Arduino'ya bağlanmaya çalış
        arduino = serial.Serial('/dev/ttyACM2', 9600)
        time.sleep(2)  # Arduino'nun reset sonrası açılması için bekle

        print(f"[INFO] Arduino bağlantısı başarılı:")

    except serial.SerialException as e:
        print(f"[HATA] Arduino bağlanamadı (): {e}")
        print("[BİLGİ] Program bağlantı olmadan devam ediyor.")

        #arduino.write(b'START\n') #Arm and hand will be home position 
        #time.sleep(0.05)
    #finally:
        #arduino.write()
        #arduino.write(b'START\n') #Arm and hand will be home position 
        #time.sleep(0.05)

    tracker = HandGestureTracker()
    tracker.start_processing()

    players = []
    round_num = 0
    current_max_hands = None

    try:
        while True:
            '''status, frame = cam.read_frame()
            if not status or frame is None:
                continue'''

            #tracker.update_frame(frame)

            if image_index >= len(image_paths):
                print("📂 Tüm resimler bitti. Oyun sonlandırılıyor.")
                break

            print(image_index)
            print(len(image_paths))
            frame = cv2.imread(image_paths[image_index])
            if frame is None:
                print(f"{image_paths[image_index]} okunamadı.")
                break

            tracker.update_frame(frame)

            processed_img = tracker.get_processed_image()
            
            if processed_img is not None:
                cv2.imshow("Hand Detection", processed_img)
                cv2.waitKey(500)  # resmi yarım saniye göster

            '''key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):  # ESC veya q ile çık
                break'''

            # Oyun mantığı burada başlıyor
            if round_num == 0:
                print("👉 Lütfen sağ elinizi 3 saniye kaldırın...")

                start_time = time.time()  
                print("El algılama yapılıyor...")
                while time.time() - start_time < 2.5:
                    time.sleep(0.1) 

                result = tracker.get_result()
                time.sleep(0.1)

                if result is None:
                    print("El algılanamadı. Tekrar deneyin.")
                    continue

                count, orientations = result
                current_max_hand_number = count
                print("first round sayı: ",current_max_hand_number)
                

                if current_max_hand_number < 2:
                    print("Yeterli el bulunamadı.")
                    continue

                players = Player.create_players(count)
                print("🎮 Oyun Başladı. Playerlar:", players)
                round_num += 1
                image_index += 1

            else:
                print(f"🕹 Tur {round_num} başladı! Lütfen elinizi gösterin...")
                time.sleep(3)
                computer_gesture = Player.get_computer_gesture()

                '''if not temp:
                    arduino.write(b"EVEN\n")
                    time.sleep(0.05)
                else:
                    arduino.write(b"EVEN\n")
                    time.sleep(0.05)'''

                # Tekrar frame al
                if image_index >= len(image_paths):
                    print("📂 Tüm resimler bitti. Oyun sonlandırılıyor.")
                    break

                frame = cv2.imread(image_paths[image_index])
                if frame is None:
                    print("⚠️ Görsel okunamadı.")
                    continue
                
                print(players)
                print("BIR ONCEKİ ROUND: ",current_max_hand_number)

                result = tracker.get_result()
                if result is None:
                    print("El verisi alınamadı.")
                    continue

                count, orientations = result
                print("SUAN EL GÖSTERİLEN SAYI ",count)
                if count < 1:
                    print("Yeterli el algılanamadı.")
                    continue

                human_players = len(players) - 1 if players and players[-1].is_computer else len(players)

                if count > human_players:
                    print("❌ Başlangıçtaki el sayısı Player sayısından fazla")
                    image_index += 1
                    continue
                    # El sayısı insan sayısından azsa, Player listesini kes
                elif count < human_players:
                    print("👥 Mevcut Player sayısı:", len(players))
                    current_max_hand_number = count

                    if players and players[-1].is_computer:
                        # Bilgisayarı ayır
                        computer = players.pop()
                        print("🧠 Bilgisayar çıkarıldı:", computer)

                        # Gerekli sayıda insan Playeryu sil
                        players = players[:count]

                        # Bilgisayarı tekrar ekle
                        players.append(computer)
                        print("♻️ Bilgisayar tekrar eklendi:", players)
                    else:
                    # Bilgisayar yoksa sadece insanları sayıya göre kırp
                        players = players[:count]
                        print("✅ Yeni Player listesi:", players)
                
                print("Yeni ply", players)
                print("ori1:",orientations)
                print("ori3:",orientations)
                print(type(orientations))
                
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
                print("playyyers", players)
                players = Player.eliminate_minority(players, flag)

                print(players)
                print(round_num)
                active_players = [p for p in players if not p.is_computer]
                print("Akttif Player sayısı:", players)
                #tracker.set_current_hand_count(len(active_players))
                print(active_players)
                #current_max_hands = len(active_players)

                if (len(active_players) == 1 and any(p.is_computer for p in players)) or len(players) == 1:
                    print("🎉 Oyun bitti! Kalan Playerlar:", players)
                    print(active_players)
                    break
                elif len(active_players) == 2 and not any(p.is_computer for p in players):
                    print("2 Player kaldı ve bilgisayar zaten elendi.")
                    players = Player.create_players(2)
                    current_max_hand_number = 2
                    print(players)
                    print(active_players)

                round_num += 1
                if flag == 0:
                    image_index += 1
                else: 
                    flag = 0

    finally:
        tracker.stop_processing()
        #tracker.cam.close_camera()
        cv2.destroyAllWindows()
        #arduino.close()
        print("🛑 Uygulama sonlandırıldı.")

