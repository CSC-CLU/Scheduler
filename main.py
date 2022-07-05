import interactions
import sys
bot = interactions.Client(token=sys.argv[1])


@bot.command(name="update_events", description="populate the discord with this week's hours")
async def update_events(ctx: interactions.CommandContext):
    await ctx.send("Events updated!")


@bot.command(name="clear_events", description="clear all events created by this bot")
async def clear_events(ctx: interactions.CommandContext):
    await ctx.send("Events cleared!")


day_of_week = interactions.Option(
    name="day", description="day being held",
    type=interactions.OptionType.STRING,
    required=True,
    choices=[
        interactions.Choice(name=day, value=day)
        for day in ("Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday"
                    )
    ])


@bot.command(name="add",
             description="Add hours",
             options=[
                 interactions.Option(name="user",
                                     description="person holding the hours",
                                     type=interactions.OptionType.USER,
                                     required=True,
                                     ),
                 day_of_week,
                 interactions.Option(name="start_time",
                                     description="time at which the hours start",
                                     type=interactions.OptionType.STRING,
                                     required=True,
                                     ),
                 interactions.Option(name="end_time",
                                     description="time at which the hours end",
                                     type=interactions.OptionType.STRING,
                                     required=True,
                                     ),
             ])
async def add(ctx: interactions.CommandContext,
              user: interactions.User, day, start_time, end_time):
    await ctx.send(f"Added hours for {user.mention} on {day} from {start_time} to {end_time}!")


bot.start()
