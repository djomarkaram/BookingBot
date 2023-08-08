# Description
Bot that books a swimming session at our local recreation center.

# Purpose
I created this bot during the Covid lockdowns to tackle the challenge of securing a swimming session at our local recreation center. My motivation was to overcome the morning rush and ensure a spot for swimming by automating the reservation process through the bot.

# How It Works
The bot uses the `selenium` library in Python and the Chrome drivers. I used the Task Scheduler application in Windows and the `Wakeup.bat` script to wake up my PC from sleep every morning at 6:00am, then at 6:05am Task Scheduler runs the `StartBot.bat` script to start the bot in order to book the sessions for me. When i wake up, i would look at my PC and check the results which were printed on a command prompt window.

# Important Note
The script provided has a demo URL and demo username and password which means that the bot will not work for you. The source code provided is solely for learning purposes only and to show how to scrape websites using the selenium library.
