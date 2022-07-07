This Twitter bot has three functions: 
1. Searches for five recent tweets that include '#GojoSatoru' or '#gojosatoru', and replies to each 
   tweet with a randomly chosen quote from 'reply_quotes.txt.' This is set to execute daily at 2:00:00PM.
2. Tweets a randomly chosen quote from 'tweet_quotes.txt'. Once a quote has been tweeted, it is deleted
   from the file and added to 'quote_archive.txt.' This set to execute weekly.
3. With every mention (@gojo_senseii) that includes the word 'dance' (not case sensitive), the bot will reply 
   with a GIF of Gojo dancing.

Based on a modified tutorial by CS Dojo.