import cv2
import mediapipe as mp
import random
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, 
                      max_num_hands=1,
                      min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Finger tip landmark IDs
finger_tips = [4, 8, 12, 16, 20]

def count_fingers(hand_landmarks):
    fingers = []
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers.append(1)
    else:
        fingers.append(0)
    for tip in finger_tips[1:]:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip-2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return sum(fingers)

def get_computer_choice():
    return random.choice(['rock', 'paper', 'scissors'])

def determine_gesture(finger_count):
    if finger_count == 0:
        return 'rock'
    elif finger_count == 5:
        return 'paper'
    elif finger_count == 2:
        return 'scissors'
    else:
        return None

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
                    2, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.imshow('Rock-Paper-Scissors', frame)
        cv2.waitKey(1000)  # Wait for 1 second

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

            finger_count = count_fingers(hand_landmarks)
            player_gesture = determine_gesture(finger_count)

            if player_gesture:
                # Get computer's choice
                computer_choice = get_computer_choice()
                result = get_winner(player_gesture, computer_choice)

                # Display both choices and result
                cv2.putText(image, f"Your gesture: {player_gesture}", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                cv2.putText(image, f"Computer gesture: {computer_choice}", (10, 130),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                cv2.putText(image, f"Result: {result}", (10, 170),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

                cv2.imshow('Rock-Paper-Scissors', image)
                cv2.waitKey(2000)  # Show for 2 seconds

                if result == 'player':
                    player_score += 1
                elif result == 'computer':
                    computer_score += 1

                current_round += 1
                break

    cv2.imshow('Rock-Paper-Scissors', image)
    if cv2.waitKey(5) & 0xFF == 27:  # ESC to exit
        break

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
