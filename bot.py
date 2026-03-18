import telebot
import requests
import os
import sqlite3
from datetime import datetime

# Configuration
BOT_TOKEN = "8205298863:AAHV8vQ97r8IeqSs-c1I9AJ9Ow1yOvY3FUI"
OMDB_API_KEY = "1cfbcaa"
TMDB_API_KEY = "371623048ad20eec2617321a47197469"

bot = telebot.TeleBot(BOT_TOKEN)

# Database setup
conn = sqlite3.connect('movies.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        year INTEGER,
        country TEXT,
        type TEXT,
        genre TEXT,
        imdb_rating REAL,
        poster TEXT,
        video_file_id TEXT,
        download_url TEXT
    )
''')
conn.commit()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
🎬 *MoviePlay.ngBot - Complete Movie System* 🎬

*Search Commands:*
• `/search [name]` - Search by movie name
• `/trending` - See trending movies this week
• `/advanced` - Advanced search (country, year, type)

*Features:*
✅ Movie details, ratings, posters
✅ Where to watch (streaming links)
✅ Trending movies
✅ Auto ads to support the bot

Try: `/search Avatar` or `/trending`
    """
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['trending'])
def trending_movies(message):
    """Get trending movies using TMDb API"""
    try:
        url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={TMDB_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        trending_text = "🔥 *Trending Movies This Week*\n\n"
        for i, movie in enumerate(data.get('results', [])[:5], 1):
            title = movie.get('title', 'Unknown')
            release = movie.get('release_date', 'N/A')[:4]
            trending_text += f"{i}. *{title}* ({release})\n"
        
        trending_text += "\nUse /search [title] to find where to watch"
        bot.send_message(message.chat.id, trending_text, parse_mode="Markdown")
        
        # Show auto ad
        show_auto_ad(message.chat.id)
        
    except Exception as e:
        bot.reply_to(message, f"Error getting trending: {str(e)}")

@bot.message_handler(commands=['search'])
def search_movie(message):
    """Search by movie name and return streaming options"""
    try:
        movie_name = message.text.replace('/search', '').strip()
        if not movie_name:
            bot.reply_to(message, "Please provide a movie name: `/search Avatar`", parse_mode="Markdown")
            return

        # Search OMDB for basic movie details (poster, rating, plot)
        omdb_url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
        omdb_response = requests.get(omdb_url)
        movie_data = omdb_response.json()

        if movie_data.get("Response") != "True":
            bot.reply_to(message, f"❌ Movie '{movie_name}' not found")
            return

        # Build the response message
        title = movie_data.get('Title', 'N/A')
        year = movie_data.get('Year', 'N/A')
        imdb = movie_data.get('imdbRating', 'N/A')
        genre = movie_data.get('Genre', 'N/A')
        plot = movie_data.get('Plot', 'N/A')
        poster = movie_data.get('Poster', '')
        
        caption = f"""
🎬 *{title}* ({year})

⭐ *IMDb:* {imdb}/10
🎭 *Genre:* {genre}

📝 *Plot:* {plot[:300]}...

🔍 Use /trending for popular movies
        """
        
        # Send result with poster
        if poster and poster != "N/A":
            bot.send_photo(message.chat.id, poster, caption=caption, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, caption, parse_mode="Markdown")
        
        # Show auto ad after result
        show_auto_ad(message.chat.id)
        
    except Exception as e:
        bot.reply_to(message, f"Error searching: {str(e)}")

@bot.message_handler(commands=['advanced'])
def advanced_search(message):
    """Advanced search with filters"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = telebot.types.InlineKeyboardButton("🎭 By Genre", callback_data="search_genre")
    btn2 = telebot.types.InlineKeyboardButton("🌍 By Country", callback_data="search_country")
    btn3 = telebot.types.InlineKeyboardButton("📅 By Year", callback_data="search_year")
    btn4 = telebot.types.InlineKeyboardButton("🎬 By Type", callback_data="search_type")
    
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(message.chat.id, "🔍 *Advanced Search Options*", 
                     parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    """Handle button callbacks"""
    if call.data == "search_genre":
        bot.send_message(call.message.chat.id, "Enter genre (e.g., Action, Comedy, Drama):")
        bot.register_next_step_handler(call.message, process_genre_search)
    
    elif call.data == "search_country":
        bot.send_message(call.message.chat.id, "Enter country (e.g., USA, Korea, UK):")
        bot.register_next_step_handler(call.message, process_country_search)
    
    elif call.data == "search_year":
        bot.send_message(call.message.chat.id, "Enter year (e.g., 2026):")
        bot.register_next_step_handler(call.message, process_year_search)
    
    elif call.data == "search_type":
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("🎬 Movie", callback_data="type_movie"),
            telebot.types.InlineKeyboardButton("📺 Series", callback_data="type_series")
        )
        bot.send_message(call.message.chat.id, "Select type:", reply_markup=markup)
    
    elif call.data == "show_ad":
        show_rewarded_ad(call.message.chat.id)

def process_genre_search(message):
    """Handle genre search"""
    genre = message.text.strip()
    # For now, show a message - implement with TMDb later
    bot.send_message(message.chat.id, f"Searching for {genre} movies... (Coming soon)")
    show_auto_ad(message.chat.id)

def process_country_search(message):
    """Handle country search"""
    country = message.text.strip()
    bot.send_message(message.chat.id, f"Searching for movies from {country}... (Coming soon)")
    show_auto_ad(message.chat.id)

def process_year_search(message):
    """Handle year search"""
    try:
        year = int(message.text.strip())
        bot.send_message(message.chat.id, f"Searching for movies from {year}... (Coming soon)")
        show_auto_ad(message.chat.id)
    except:
        bot.send_message(message.chat.id, "Please enter a valid year (e.g., 2026)")

def send_movie_card(chat_id, movie_data):
    """Send single movie with info"""
    title = movie_data.get('Title', 'N/A')
    year = movie_data.get('Year', 'N/A')
    imdb = movie_data.get('imdbRating', 'N/A')
    genre = movie_data.get('Genre', 'N/A')
    poster = movie_data.get('Poster', '')
    
    caption = f"""
🎬 *{title}* ({year})

⭐ *IMDb:* {imdb}/10
🎭 *Genre:* {genre}
    """
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("⭐ Support Us (Watch Ad)", callback_data="show_ad"))
    
    if poster and poster != "N/A":
        try:
            bot.send_photo(chat_id, poster, caption=caption, 
                          parse_mode="Markdown", reply_markup=markup)
        except:
            bot.send_message(chat_id, caption, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(chat_id, caption, parse_mode="Markdown", reply_markup=markup)
    
    # Auto-show ad after movie display
    show_auto_ad(chat_id)

def show_auto_ad(chat_id):
    """Show automatic interstitial ad"""
    try:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(
            "🎯 Support Us (Watch Ad)", 
            callback_data="show_ad"
        ))
        bot.send_message(chat_id, "Enjoying free movies? Support us!", reply_markup=markup)
    except:
        pass

def show_rewarded_ad(chat_id):
    """Show rewarded ad with callback"""
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        "✅ I Watched the Ad", 
        callback_data="ad_watched"
    ))
    
    msg = bot.send_message(
        chat_id, 
        "🎥 *Watch a short ad to unlock premium features:*\n\n"
        "• HD Streaming\n"
        "• Direct Downloads\n"
        "• Exclusive Content",
        parse_mode="Markdown",
        reply_markup=markup
    )
    
    # Auto-delete after 30 seconds
    import threading
    threading.Timer(30.0, lambda: bot.delete_message(chat_id, msg.message_id)).start()

@bot.callback_query_handler(func=lambda call: call.data == "ad_watched")
def handle_ad_watched(call):
    """Give reward after ad"""
    bot.answer_callback_query(call.id, "✅ Reward unlocked! Enjoy premium features.")
    bot.send_message(call.message.chat.id, "🎉 *Thanks!* Premium features unlocked!", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    """Catch-all handler - try movie search"""
    movie_name = message.text.strip()
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if data.get("Response") == "True":
        send_movie_card(message.chat.id, data)
    else:
        bot.reply_to(message, f"Try /search {movie_name} or /trending for popular movies")

print("🎬 COMPLETE MOVIE BOT STARTED!")
print("Features: Search, Trending, Auto Ads, TMDb Integration")
bot.infinity_polling()