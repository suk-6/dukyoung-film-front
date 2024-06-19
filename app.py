import tkinter as tk
from PIL import Image, ImageTk
import cv2
import base64
import requests
import os
from dotenv import load_dotenv
import json
from io import BytesIO
import platform
from playsound import playsound

load_dotenv()

PROCESSING_URL = os.getenv("PROCESSING_URL")


class app:
    def __init__(self):
        self.defaultTimer = 8
        self.window = tk.Tk()
        self.window.title("Dukyoung Film")

        self.positionRight = self.window.winfo_screenwidth() / 2
        self.positionDown = self.window.winfo_screenheight() / 2

        # Full Screen
        self.window.attributes("-fullscreen", True)
        self.window.geometry("1920x1080")
        self.fullScreenState = True
        self.window.bind("f", self.toggleFullScreen)
        self.window.bind("<Escape>", self.quitFullScreen)

        self.window.configure(bg="white")

        # Start Page
        self.frameView = tk.Frame(self.window, bg="white")
        self.frameView.place(
            x=self.positionRight, y=self.positionDown, anchor=tk.CENTER
        )

        mainImage = Image.open("./static/main.png")
        mainImage = mainImage.resize((1920, 1080), Image.LANCZOS)
        mainImage = ImageTk.PhotoImage(mainImage)

        self.startPage = tk.Label(
            self.frameView,
            image=mainImage,
        )
        self.startPage.pack(pady=100)

        self.window.bind("<Button-1>", self.selectFrame)

        # Exit
        self.window.bind("q", lambda e: self.window.destroy())
        self.window.mainloop()

    def blank(self, event):
        pass

    def selectFrame(self, event):
        self.startPage.destroy()
        self.window.bind("<Button-1>", self.blank)
        self.framePage = tk.Frame(self.window, bg="white")
        self.framePage.pack(expand=True)

        # Load frames
        self.frameCount = len([s for s in os.listdir("./frames") if s.endswith(".png")])
        self.frames = []

        for i in range(self.frameCount):
            original = Image.open(f"./frames/frame{i}.png")
            # crop = original.crop((50, 100, 1150, 3500))
            # resized = crop.resize((int(1150 / 4.7), int(3500 / 4.7)), Image.LANCZOS)
            resized = original.resize((int(1000 / 2), int(1480 / 2)), Image.LANCZOS)
            image = ImageTk.PhotoImage(resized)

            self.frames.append(image)

        for i in range(self.frameCount):
            frameLabel = tk.Label(self.framePage, image=self.frames[i])
            frameLabel.bind(
                "<Button-1>", lambda event, frame=i: self.startCamera(event, frame)
            )
            frameLabel.grid(row=1, column=i, padx=15)

        self.frameLabels = [frameLabel]

        self.window.update()

    def readyCamera(self):
        self.readyPage = tk.Frame(self.window, bg="white")
        self.readyPage.pack(expand=True)

        self.readyPageTitle = tk.Label(
            self.readyPage,
            text="준비 중...",
            font=("Arial", 100),
            fg="black",
            bg="white",
        )
        self.readyPageTitle.pack(pady=100)

        self.window.update()

    def startCamera(self, event, frame):
        self.framePage.destroy()
        self.frame = frame

        self.readyCamera()

        self.cameraPage = tk.Frame(self.window, bg="white")
        self.cameraPage.pack(expand=True)

        self.camera = cv2.VideoCapture(1)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        self.cameraLabel = tk.Label(self.cameraPage)
        self.cameraLabel.pack()

        self.images = ["", "", "", ""]

        self.window.after(10, self.updateCamera)
        self.readyPage.destroy()

        self.timer = self.defaultTimer
        self.index = 0

        self.timerLabel = tk.Label(
            self.cameraPage,
            text=f"{self.index + 1}번째 사진! {self.timer}!",
            font=("Arial", 60),
            fg="black",
            bg="white",
        )
        self.timerLabel.pack()

        self.window.after(1000, self.updateTimer)

    def updateTimer(self):
        self.timer -= 1
        self.timerLabel.configure(text=f"{self.index + 1}번째 사진! {self.timer}!")

        if self.timer == 0:
            playsound("./static/shutter.mp3")
        if self.timer > 0:
            self.window.after(1000, self.updateTimer)
        else:
            self.takePhoto()
            if self.index < 3:
                self.timerLabel.configure(text=f"찰칵!")

                self.timer = self.defaultTimer
                self.index += 1
                self.window.after(2000, self.updateTimer)
            else:
                self.camera.release()
                self.cameraPage.destroy()
                self.processImages()

    def takePhoto(self):
        _, image = self.camera.read()
        image = cv2.flip(image, 1)
        image = self.centerCrop(image)

        cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.imencode(".png", image)
        self.images[self.index] = base64.b64encode(image[1]).decode("utf-8")

    def centerCrop(self, image):
        height, width = image.shape[:2]
        targetHeight, targetWidth = 500 * 2, 430 * 2

        top = (height - targetHeight) // 2
        left = (width - targetWidth) // 2

        cropped = image[top : top + targetHeight, left : left + targetWidth]

        return cropped

    def updateCamera(self):
        try:
            _, frame = self.camera.read()
            frame = cv2.flip(frame, 1)
            frame = self.centerCrop(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(frame)

            self.cameraLabel.configure(image=frame)
            self.cameraLabel.image = frame
        except:
            return

        self.window.after(10, self.updateCamera)

    def processImages(self):
        self.processPage = tk.Frame(self.window, bg="white")
        self.processPage.pack(expand=True)

        self.processPageTitle = tk.Label(
            self.processPage,
            text="처리 중...",
            font=("Arial", 100),
            fg="black",
            bg="white",
        )
        self.processPageTitle.pack(pady=100)

        self.window.update()

        # Process images
        try:
            self.req = requests.post(
                PROCESSING_URL,
                json={"images": self.images, "frame": self.frame},
                verify=False,
            )
            self.req = json.loads(self.req.text)
        except Exception as e:
            print(f"Processing failed!\n{e}")
            self.processPageTitle.configure(text="처리 실패!")
            return

        self.processPageTitle.configure(text="처리 완료!")
        self.window.after(2000, self.showImage)

    def showImage(self):
        self.processPage.destroy()

        self.resultPage = tk.Frame(self.window, bg="white")
        self.resultPage.pack(expand=True)

        print(f"ID: {self.req['id']}, TIME: {self.req['time']}")

        self.image = Image.open(BytesIO(base64.b64decode(self.req["image"])))

        self.resultImage = self.image.resize(
            (int(1200 / 2), int(3552 / 4)), Image.LANCZOS
        )
        self.resultImage = ImageTk.PhotoImage(self.resultImage)
        self.resultLabel = tk.Label(self.resultPage, image=self.resultImage)
        self.resultLabel.pack(pady=100)

        self.window.update()
        if platform.system() == "Windows":
            self.printer()

        self.window.after(10000, self.restart)

    def printer(self):
        if os.path.exists("print") == False:
            os.mkdir("print")

        self.image.save(os.path.join("print", f"{self.req['id']}.png"))

        from printer import printer

        printer(os.path.join("print", f"{self.req['id']}.png"))

    def restart(self):
        self.window.destroy()
        app()

    def toggleFullScreen(self, event):
        self.fullScreenState = not self.fullScreenState
        self.window.attributes("-fullscreen", self.fullScreenState)

    def quitFullScreen(self, event):
        self.fullScreenState = False
        self.window.attributes("-fullscreen", self.fullScreenState)


if __name__ == "__main__":
    print("Dukyoung Film Starting...")
    print(PROCESSING_URL)
    app = app()
