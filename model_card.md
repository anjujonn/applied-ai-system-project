# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

SingYourSong 1.0

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

The recommender is designed for people that want to get top 5 recommendations of songs that most match their vibe. I guess it's for everyone, since theres a song for everyone in there. The assumptions it makes is that they like atleast 1 song within the dataset we have. I think this is more of an exploration and not a real users thing--you'd need a much more robust model. 

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

So, to start, the recommender gives each song a score based on how well it matches what you said you like. It checks four things: whether the song's genre matches your favorite, whether the mood matches, how close the song's energy level is to yours, and how acoustic or electronic the song sounds compared to what you said you liked. Genre and mood are simple yes or no checks. Energy and acousticness are more gradual where the closer a song is to your target, the more points it earns, so a song that's slightly off still gets partial credit. All those points are added up, the songs with the highest totals get recommended to you first!

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

I have 20 songs with lofi, pop, ambient, classical, country, darkwave, edm, folk, hip-hop, indie pop, jazz, metal, r&b, reggae, rock, synthwave, world. I added quite a bit of data and didn't remove much. There's probably some tastes missing--I tried to have a song for each category but I'm sure I've missed some. 

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

I think it does really well with looking at everything objectively and trying to derive the mathematical portion of it. It definitely does pretty good with recommendations given its simplicity. I thought it was really interesting that it gives pretty good results for rock and faster-paced music. I though it'd be harder to identify since they can have very similar beats, but no!

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  


So one issue I noticed is that even though I take a few metrics into account for recommendation, valence and danceability are ignored in scoring. They certainly add to the metrics and can help with more accurate scoring. Basically this created hidden bias because valence is about songs with same energy and daceability is about how danceable and energetic the song is. Two very important qualities to help figure out a recommendation.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

I went ahead and just from what I know about the genre of each music piece assessed. Overall, mathematically it seems to be working, but there's mixed input on the recommendations I'd say. I tested 5 profiles and there were the outcomes: Chill Lofi has most accurate I feel like, then pop, then rock, then rnb, and lastly edm. To be honest I wasn't expecting Pop and Rock to have any good recommendations because when beats increase I feel like it gets harder. But it did pretty good!

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

Major idea is to make the model more complex, then add more data.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

This was a fun experience `:)` I got to understand how models are built. I've always only worked with them never really made one. I didn't really expect building a model to be this simple. I'm sure it's a lot more complex with very hard-core datasets and what-not. But the steps are probably similar I guess. I thought it would always be a very gruesome process. I guess I see how simple music recommendation apps can be, but truly kudos to Spotify, Youtube Music, etc for their system--it is not simple I'm sure. AI was a huge help in smoothing this process. Helped me a lot with the math, logic, and code. The only time I needed to double check is when checking outputs. Otherwise--pretty great! Still, I always try to check whatever edits it made and understand because AI isn't perfect. It did great for the most part though! If I had to extend this project, I'd for sure use a much larger dataset and better data analysis for better models and find better patterns for my model to recommend better. 
