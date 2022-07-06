import datetime
import pytz
import re
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
    type=interactions.OptionType.INTEGER,
    required=True,
    choices=[
        interactions.Choice(name=day, value=index)
        for (index, day) in
        enumerate(("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"))
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
    today = datetime.date.today()
    days_from_today = ((day + 7) - today.weekday()) % 7
    # calculate new date
    date = datetime.date.fromordinal(today.toordinal() + days_from_today)
    # calculate proper start time
    regex = re.compile("(?P<hour>\\d{1,2}):(?P<min>\\d{2})(?P<m>[a|p]m)?", re.IGNORECASE)

    def time(time):
        match = regex.fullmatch(time)
        if match:
            groups: dict = match.groupdict()
            hour = int(groups['hour'])
            if groups['m'] == 'pm':
                hour += 12
            return datetime.datetime(date.year, date.month, date.day, hour, int(groups['min']),
                                     tzinfo=pytz.timezone('America/Los_Angeles'))
        return None

    start_time = time(start_time)
    end_time = time(end_time)
    if start_time is not None and end_time is not None:
        await ctx.get_guild()
        await ctx.guild.create_scheduled_event(
            "DA Hours", interactions.EntityType.EXTERNAL,
            start_time.isoformat(), end_time.isoformat(),
            interactions.EventMetadata(location='D13'),
            description=f"{user.mention} will be holding DA hours.",
        )
        await ctx.send(f"Added hours for {user.mention} at {start_time.isoformat()} to {end_time.isoformat()}")
    else:
        await ctx.send("Invalid time entry")


bot.start()
