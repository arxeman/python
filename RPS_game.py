import cv2
import mediapipe as mp
import random
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

def determine_gesture(hand_landmarks):
    # Thumb: compare x-coordinates (for right hand; flip for left)
    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]
    thumb_up = thumb_tip.x < thumb_ip.x

    # Fingers: compare y-coordinates (tip above pip means up)
    index_up = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
    middle_up = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
    ring_up = hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y
    pinky_up = hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y

    # Rock: all fingers closed
    if not any([thumb_up, index_up, middle_up, ring_up, pinky_up]):
        return 'rock'
    # Paper: all fingers open (thumb can be up or down)
    if all([index_up, middle_up, ring_up, pinky_up]):
        return 'paper'
    # Scissors: only index and middle up, ring and pinky down
    if index_up and middle_up and not ring_up and not pinky_up:
        return 'scissors'
    return None

def get_computer_choice():
    return random.choice(['rock', 'paper', 'scissors'])

def get_winner(player_choice, computer_choice):
    if player_choice == computer_choice:
        return 'tie'
    elif (player_choice == 'rock' and computer_choice == 'scissors') or \
         (player_choice == 'paper' and computer_choice == 'rock') or \
         (player_choice == 'scissors' and computer_choice == 'paper'):
        return 'player'
    else:
        return 'computer'

def show_countdown(cap, seconds=2):
    for i in range(seconds, 0, -1):
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        cv2.putText(frame, f"Get ready: {i}", (150, 200), cv2.FONT_HERSHEY_SIMPLEX,
                    2, (0, 0, 255), 4, cv2.LINE_AA)
        cv2.imshow('Rock-Paper-Scissors', frame)
        cv2.waitKey(1000)

# Game setup
rounds = int(input("Enter number of rounds: "))
current_round = 1
player_score = 0
computer_score = 0

cap = cv2.VideoCapture(0)
game_active = True

while cap.isOpened() and game_active and current_round <= rounds:
    # --- Show the countdown before each round ---
    show_countdown(cap, 2)

    # Capture hand gestures for 2 seconds
    gesture_counts = {'rock': 0, 'paper': 0, 'scissors': 0}
    start_time = time.time()
    capture_duration = 2  # seconds

    while time.time() - start_time < capture_duration:
        success, image = cap.read()
        if not success:
            continue

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        # Display round and score
        cv2.putText(image, f"Round: {current_round}/{rounds}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(image, f"Player: {player_score}  Computer: {computer_score}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                player_gesture = determine_gesture(hand_landmarks)
                if player_gesture:
                    gesture_counts[player_gesture] += 1

        cv2.imshow('Rock-Paper-Scissors', image)
        if cv2.waitKey(5) & 0xFF == 27:  # ESC to exit
            game_active = False
            break

    if not game_active:
        break

    # Choose the gesture with the highest count
    if any(gesture_counts.values()):
        player_gesture = max(gesture_counts, key=gesture_counts.get)

        # Get computer's choice
        computer_choice = get_computer_choice()
        result = get_winner(player_gesture, computer_choice)

        # Display result
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)

        cv2.putText(frame, f"Your gesture: {player_gesture}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        cv2.putText(frame, f"Computer gesture: {computer_choice}", (10, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(frame, f"Result: {result}", (10, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 128, 0), 2)

        cv2.imshow('Rock-Paper-Scissors', frame)
        cv2.waitKey(2000)

        if result == 'player':
            player_score += 1
        elif result == 'computer':
            computer_score += 1

        current_round += 1

cap.release()
cv2.destroyAllWindows()

# Final result
print("\nFinal Scores:")
print(f"Player: {player_score}")
print(f"Computer: {computer_score}")
if player_score > computer_score:
    print("You win the game!")
elif computer_score > player_score:
    print("Computer wins the game!")
else:
    print("It's a tie!")
