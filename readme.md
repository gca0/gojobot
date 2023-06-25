## Gojo Bot
This is a twitter bot written in Python. Based on a modified tutorial by CS Dojo.

### Functions:
- Searches for five recent tweets that include **'#GojoSatoru'** or **'#gojosatoru'**, and replies to each 
   tweet with a randomly chosen quote from <code>reply_quotes.txt.</code> This is set to execute daily at 12:00:00 PM.
- Tweets a randomly chosen quote from <code>tweet_quotes.txt.</code> Once a quote has been tweeted, it is deleted
   from the file and added to <code>quote_archive.txt.</code> This set to execute weekly.
- With every mention that includes the word 'dance' (not case sensitive), the bot will reply 
   with a GIF of Gojo dancing.
