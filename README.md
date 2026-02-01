# 🎾 Ball Knowledge
_Restoring the Visual Narrative of Sport_

This is our entry for IC Hack 26, entering in the Sports and Tech for Good (IMChange) categories.

Ball Knowledge is an AI-powered accessibility framework developed for ICHack 26. Our mission is to provide visually impaired individuals with the same tactical depth and emotional immersion as sighted fans, using a single video feed to generate a rich, spatial audio-description.

## 💻 Interface
The interface for our web app is sleek and intuitive. Using a minimalist approach, we have boiled the page down to its bare essentials as to not overwhelm the user.

<img width="717" height="591" alt="image" src="https://github.com/user-attachments/assets/e49f06bb-3ca9-4f9f-a282-1a1ce501cace" />

1. We provide a multimodal method of input: both a direct upload or a YouTube video link can be analysed.
2. The method of input is simple and intuitive.
3. A final layer of customisation allows the user to tailor the commentator's style to better suit their needs.

## 🌍 The Mission: Why This Matters
For the 2.2 billion people globally living with vision impairment, following a fast-paced sport like tennis is an exercise in frustration. Current solutions - like standard radio commentary - often fail to describe:

Positioning: Where is the player relative to the baseline?

Tactics: Are they charging the net or being forced wide?

Physics: How close was that ball to the line?

Ball Knowledge solves this by using AI to "see" the court and translate spatial data into a narrative that restores the viewer's mental model of the game.

## ❤️ Social Impact & Charity Alignment
We built this project with the aim of providing blind fans with a data-rich experience in mind. It has the advantage of that doesn't rely on a human being available to describe it.

Our ptoject relates to the core values of Inclusion, Dignity, and Equity:

Independent Spectatorship: We provide the tools for blind fans to enjoy a match independently, without needing a sighted companion to explain the action.

Empowering Grassroots Sport: High-quality audio description is currently a luxury reserved for the Grand Slams. We make it accessible for local club tournaments, youth games, and school matches - ensuring no community is left behind.

Autonomy through Choice: By allowing users to customize the "Persona" of the commentator, we respect the diverse ways people engage with sport, from data-driven analysis to hype-filled narration.

## 🛠️ Algorithms
A simplified rundown of the processes at work is as follows:
1. The user inputs a video to the server.
2. YOLO is used to track entities of interest based on their absolute position in pixels on the screen.
   - In particular, we track the players, ball and boundary box.
4. Planar homography is used to transform this into a top-down view in order to gauge the position of the ball relative to the playing field.
5. Next, collections of frames are analysed in order to mark them with an event.
   - The Physics of the Game: Detecting bounces, net-crosses, and shots.
   - Player Intent: Recognizing when a player is "out of position" or "attacking the net".
7. This is then used to create a JSON file that we pass to Claude, which generates a running commentary.
8. ElevenLabs is then used to synthesise audio, which we can overlay on the original video.
9. This is then passed back to the website so the user can watch at their own enjoyment.

## 🚀 The Future: Beyond the Court
While we are launching with Tennis, the framework is designed to scale across the sporting world:

Adaptive & Parasports: Tailoring the logic to track wheelchair tennis or blind football (5-a-side), providing bespoke commentary for adaptive athletes.

Coaching & Feedback: Allowing athletes, like our team members in Taekwondo, to receive automated tactical feedback to improve their performance and reach their competitive potential.
