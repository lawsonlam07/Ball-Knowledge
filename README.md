# 🎾 Ball Knowledge
_Restoring the Visual Narrative of Sport_

This is our entry for IC Hack 26, entering in the Sports and Tech for Good (IMChange) categories.

Ball Knowledge is an AI-powered accessibility framework developed for ICHack 26. Our mission is to provide individual games with the same tactical depth and emotional immersion as professional matches, using a single video feed to generate a rich, spatial audio-description.

## 💻 Interface
The interface for our web app is sleek and intuitive. Using a minimalist approach, we have boiled the page down to its bare essentials as to not overwhelm the user.

<img width="717" height="591" alt="image" src="https://github.com/user-attachments/assets/e49f06bb-3ca9-4f9f-a282-1a1ce501cace" />

1. We provide a multimodal method of input: both a direct upload or a YouTube video link can be analysed.
2. The method of input is simple and intuitive.
3. A final layer of customisation allows the user to tailor the commentator's style to better suit their needs.

## 🎗️ Charity: Access Sport
While developing Ball Knowledge, we aligned our goals with Access Sport, a charity dedicated to providing disabled and disadvantaged young people with access to the life-changing benefits of sport.

Our framework supports their "Inclusive Club Network" through three primary pillars:

Digital Equity for Local Clubs Access Sport works in the UK’s most deprived areas where high-tech broadcast equipment is non-existent. Ball Knowledge brings "Grand Slam" level technology to local park courts. This can bring professional audio commentary to a local club match or youth tournament, allowing amateur athletes to feel like pros and local clubs to build more inclusive communities.

Sensory-Friendly Spectatorship For neurodivergent fans, standard high-velocity commentary can cause sensory overload. Our platform offers a "Calm Mode" that replaces chaotic hype with a structured, descriptive narrative tailored to the user's sensory needs—aligning with Access Sport’s mission to create inclusive, welcoming environments for all.

Scaling Volunteer Impact Grassroots clubs rely on volunteers who are often stretched thin. By automating descriptive commentary and match analysis, we empower these clubs to provide an accessible experience for parents and fans without needing extra human resources.

## 🌍 The Mission: Equity in Every Match
For many, following a fast-paced sport like tennis is an exercise in exclusion. Whether due to visual impairment, neurodivergence, or simply a lack of resources in local parks, standard broadcasts fail to provide an inclusive narrative. Current solutions often ignore:

Spatial Context: Where is the player positioned? Is a local youth player holding their ground or being forced wide?

Sensory Needs: Standard commentary is often a chaotic "sensory minefield" of overlapping noise that can overwhelm neurodivergent fans.

Grassroots Representation: Professional-grade analysis is usually a luxury of the elite, leaving local club matches and youth tournaments invisible.

Ball Knowledge solves this by democratizing sports technology. We use AI to "see" the court, translating raw spatial data into a narrative that restores the viewer's mental model of the game—regardless of their sensory needs or the zip code of the court.

## ❤️ Social Impact & Charity Alignment
We built Ball Knowledge to ensure that no fan or athlete is left on the sidelines. By removing the need for a sighted companion or a professional broadcast team, we provide a scalable solution for inclusive sport at every level.

Our project is rooted in three core values:

**Independent Spectatorship**: We provide the tools for blind and partially sighted fans to follow the "spatial story" of a match autonomously. By translating raw data into descriptive audio, we restore the dignity of an independent viewing experience.

**Democratizing the Grassroots**: High-quality commentary is currently a luxury reserved for the elite. We bring this "Grand Slam" experience to local park courts and youth tournaments, ensuring that disadvantaged communities have access to the same technology as professional academies.

**Sensory Autonomy**: We recognize that "one size fits all" commentary doesn't work for neurodivergent fans. By allowing users to choose between high-energy personas or "Calm Mode," we respect individual sensory needs and prevent cognitive overload.

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
