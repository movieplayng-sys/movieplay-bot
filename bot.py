import telebot
import requests
import time

# PASTE YOUR NEW BOT TOKEN HERE
bot = telebot.TeleBot("8205298863:AAEYqp-Fc5JCG-AroDQlRKfRzfn_iuIV5Eo")

# PASTE YOUR OMDB API KEY HERE
OMDB_API_KEY = "ebdad049"

@bot.message_handler(commands=['start', 'help', 'menu'])
def send_welcome(message):
    welcome_text = """
🎬 *MoviePlay.ngBot* 🎬

Send me any movie name and I'll fetch:
• Movie poster
• IMDb rating  
• Plot summary
• Cast & director

Example: `Avatar` or `Inception`
"""
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def get_movie_info(message):
    movie_name = message.text.strip()
    
    # Send typing indicator
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Call OMDB API
        url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if data.get("Response") == "True":
            # Extract movie details
            title = data.get("Title", "N/A")
            year = data.get("Year", "N/A")
            imdb = data.get("imdbRating", "N/A")
            genre = data.get("Genre", "N/A")
            director = data.get("Director", "N/A")
            actors = data.get("Actors", "N/A")
            plot = data.get("Plot", "N/A")
            poster = data.get("Poster", "")
            
            # Create message
            movie_text = f"""
🎬 *{title}* ({year})

⭐ *IMDb:* {imdb}/10
🎭 *Genre:* {genre}
🎬 *Director:* {director}
👥 *Cast:* {actors}

📝 *Plot:* {plot[:300]}...
"""
            
            # Send poster if available
            if poster and poster != "N/A":
                try:
                    bot.send_photo(message.chat.id, poster, caption=movie_text, parse_mode="Markdown")
                except:
                    bot.send_message(message.chat.id, movie_text, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, movie_text, parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Movie '{movie_name}' not found. Try another name!")
            
    except Exception as e:
        bot.reply_to(message, "❌ Error fetching movie data. Please try again.")
        print(f"Error details: {e}")

print("✅ BOT STARTED SUCCESSFULLY! Waiting for messages...")
print("Press Ctrl+C to stop")

# Keep the bot running
if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Connection error: {e}")
            time.sleep(3)