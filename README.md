# OsuBot
A basic Discord bot for displaying recent and overall osu! scores. The aim of this bot is to provide a way for casual osu! players to share their accomplishments with each other. Commands and other features will be added upon request, and as I see fit. Basic documentation for this bot can be found below, and detailed documentation will be added to the [wiki page](https://github.com/azn-abel/OsuBot/wiki) once it is ready. Hope you enjoy!

Add this bot to your Discord server: [Click here](https://discord.com/api/oauth2/authorize?client_id=843169608852570184&permissions=534723816512&scope=bot)

## Basic Commands
Quick note: for any username in any command, if the username contains spaces, "it will need quotation marks around it".
- [osu!info](#osuinfo)
- [osu!recent and osu!top](#osurecent-and-osutop)
- [osu!plot](#osuplot)
- [osu!bar](#osubar)

### osu!info
Using ```osu!info [username] [mode]``` will return and display the cumulative stats of the specified user in an optionally specified mode. If the mode is not specified, it displays the user's stats for osu! standard.

<img src="https://user-images.githubusercontent.com/66392457/233444032-23e9937b-4d18-4fee-9836-4196f69c11d9.png" width=500 />

[Return to table of contents](#basic-commands)

### osu!recent and osu!top
Using ```osu!recent [username] [mode]``` displays the specified user's most recent play in an optionally specified mode. If the mode is not specified, it displays the user's most recent play for osu! standard. This is useful for sharing accomplishments to members of a Discord server as they happen in real time.

<img src="https://user-images.githubusercontent.com/66392457/233444719-47bb0196-989f-4e3c-a8a2-1240354ec172.png" width=500 />

[Return to table of contents](#basic-commands)

Using ```osu!top [username] [mode]``` similarly displays a specified user's top play.

<img src="https://user-images.githubusercontent.com/66392457/233444195-a1eb1580-571c-44cb-bc45-98dfa5acad89.png" width=500 />

[Return to table of contents](#basic-commands)

Adding a ```-d``` clause to the above will provide a more detailed response that covers the users top 5 most recent scores or highest pp plays.

<img src="https://user-images.githubusercontent.com/66392457/233444835-5c692c86-31cd-46ba-8256-b51bff4cb0b8.png" width=500 />

[Return to table of contents](#basic-commands)

### osu!plot
Using ```osu!plot [username] [mode]``` will display basic statistics on the user's top 100 plays in an optionally specified mode, as well as a histogram showing their distribution. If the mode is not specified, it displays the user's stats for osu! standard.

<img src="https://user-images.githubusercontent.com/66392457/233445745-372ddbba-10e6-40be-a184-0bc9b08a51a8.png" width=500 />

[Return to table of contents](#basic-commands)

### osu!bar
Using ```osu!bar [mode] [number]``` displays the following embed, containing a list of countries that top osu! players are from, as well as a bar chart showing their distribution. The command can take optionally specified arguments mode and number, which default to osu! standard and 100 users, respectively. With higher numbers, the resulting bar chart may be hard to read due to how many countries are shown. If this is the case, you can click on the image to expand it.

<img src="https://user-images.githubusercontent.com/66392457/233773205-ab4c3d26-3f85-4ea2-ae4f-8e755a4f3e76.png" width=500 />

[Return to table of contents](#basic-commands)




