import cv2
import time
import random
from fer import FER
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pymongo import MongoClient
from datetime import datetime, timezone, timedelta

# ✅ ADD THIS (for tree update)
import webview

# ===================== TIME (IST) =====================
IST = timezone(timedelta(hours=5, minutes=30))

# ===================== MONGODB ATLAS =====================
uri = " "

client = MongoClient(uri)
db = client["emohealDB"]
camera_collection = db["camera_emotions"]

print("✅ MongoDB Atlas Connected")

# ===================== SPOTIFY =====================
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=" ",
        client_secret=" ",
        redirect_uri="http://127.0.0.1:8888/callback",
        scope="user-modify-playback-state user-read-playback-state"
    )
)
print("✅ Spotify Premium Auth Successful")

# ===================== EMOTION → BOLLYWOOD =====================
EMOTION_QUERY = {
    "happy": "Hindi Bollywood happy songs",
    "sad": "Hindi Bollywood sad songs",
    "angry": "Hindi Bollywood calm songs",
    "fear": "Hindi Bollywood meditation songs",
    "surprise": "Hindi Bollywood party songs",
    "neutral": "Hindi Bollywood relaxing songs",
    "disgust": "Hindi Bollywood soothing songs"
}

# ===================== PLAY SONG =====================
def play_song(emotion):
    query = EMOTION_QUERY.get(emotion, "Hindi Bollywood songs")

    res = sp.search(q=query, type="track", limit=25, market="IN")
    tracks = res["tracks"]["items"]
    if not tracks:
        return ""

    track = random.choice(tracks)

    devices = sp.devices()["devices"]
    if not devices:
        print("⚠️ Open Spotify (mobile/desktop)")
        return ""

    device_id = devices[0]["id"]
    sp.transfer_playback(device_id=device_id, force_play=True)
    sp.start_playback(device_id=device_id, uris=[track["uri"]])

    song = f"{track['name']} - {track['artists'][0]['name']}"
    print("🎵 Playing:", song)
    return song

def pause_song():
    try:
        sp.pause_playback()
        print("⏸ Song Paused")
    except:
        pass

def resume_song():
    try:
        sp.start_playback()
        print("▶️ Song Resumed")
    except:
        print("⚠️ No song to resume")

# ===================== CAMERA =====================
detector = FER(mtcnn=False)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

current_emotion = "No Face Detected"
current_song = ""
selected_face_index = -1
last_faces = []
allow_detection = True

DETECT_EVERY = 10
frame_count = 0

mouse_x, mouse_y = 0, 0

# ===== Mouse Click =====
def mouse_click(event, x, y, flags, param):
    global allow_detection, mouse_x, mouse_y

    mouse_x, mouse_y = x, y

    if event == cv2.EVENT_LBUTTONDOWN:

        if 20 < x < 160 and 100 < y < 150:
            allow_detection = True
            print("🔄 Detect Again Clicked")

        elif 180 < x < 320 and 100 < y < 150:
            print("❌ Quit Clicked")
            cap.release()
            cv2.destroyAllWindows()
            exit()

        elif 340 < x < 460 and 100 < y < 150:
            resume_song()

        elif 480 < x < 620 and 100 < y < 150:
            pause_song()

print("🎥 EmoHeal Running")

# ===================== MAIN LOOP =====================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_count += 1
    faces = []

    if allow_detection and frame_count % DETECT_EVERY == 0:
        faces = detector.detect_emotions(frame)
        last_faces = faces

        if not faces:
            pause_song()
            current_emotion = "No Face Detected"
            current_song = ""
            selected_face_index = -1

        else:
            selected_face_index = max(
                range(len(faces)),
                key=lambda i: max(faces[i]["emotions"].values())
            )

            emotions = faces[selected_face_index]["emotions"]
            current_emotion = max(emotions, key=emotions.get)

            
            try:
                webview.windows[0].evaluate_js(
                    f"updateTreeFromVoice('{current_emotion}')"
                )
            except:
                pass

            current_song = play_song(current_emotion)

            record = {
                "emotion": current_emotion,
                "song": current_song,
                "source": "camera",
                "timestamp": datetime.now(IST)
            }

            camera_collection.insert_one(record)
            print("✅ Stored in MongoDB Atlas:", record)

            allow_detection = False

    # ===== DRAW FACES =====
    draw_faces = last_faces if not allow_detection else faces

    for i, face in enumerate(draw_faces):
        x, y, w, h = face["box"]
        color = (0, 255, 0) if i == selected_face_index else (150, 150, 150)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    # ===== UI =====
    cv2.rectangle(frame, (0, 0), (640, 90), (0, 0, 0), -1)

    cv2.putText(frame, f"Emotion: {current_emotion}", (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.putText(frame, f"Song: {current_song}", (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

    # ===== BUTTONS =====
    cv2.rectangle(frame, (20, 100), (160, 150), (0, 180, 0), -1)
    cv2.putText(frame, "Detect Again", (25, 135),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 2)

    cv2.rectangle(frame, (180, 100), (320, 150), (0, 0, 180), -1)
    cv2.putText(frame, "Quit", (225, 135),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 2)

    cv2.rectangle(frame, (340, 100), (460, 150), (0, 200, 200), -1)
    cv2.putText(frame, "Play", (375, 135),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,0,0), 2)

    cv2.rectangle(frame, (480, 100), (620, 150), (180, 0, 0), -1)
    cv2.putText(frame, "Stop", (515, 135),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 2)

    cv2.namedWindow("EmoHeal - Emotion Based Player", cv2.WINDOW_NORMAL)
    cv2.imshow("EmoHeal - Emotion Based Player", frame)
    cv2.moveWindow("EmoHeal - Emotion Based Player", 600, 450)
    cv2.setMouseCallback("EmoHeal - Emotion Based Player", mouse_click)

    key = cv2.waitKey(1) & 0xFF
    if key == 13:
        allow_detection = True
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
