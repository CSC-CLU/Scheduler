import datetime
import re
import interactions
from sys import argv

import timezone

bot = interactions.Client(token=argv[1])
@bot.command(name="update_events", description="populate the discord with this week's hours")
async def update_events(ctx: interactions.CommandContext):
    await ctx.send("Events updated!")


# gets a list of scheduled events for easy iterating
async def get_scheduled_events(ctx: interactions.CommandContext) -> list[interactions.ScheduledEvents]:
    return list(map(
        lambda event: interactions.ScheduledEvents(**event),
        await ctx.client.get_scheduled_events(ctx.guild_id, False)
    ))

@bot.command(name="clear_events", description="clear all events created by this bot")
async def clear_events(ctx: interactions.CommandContext):
    guild = await ctx.get_guild()
    res = ""
    for event in await get_scheduled_events(ctx):
        # fixme this deletes all events unconditionally.
        if event.creator_id == ctx.application_id:
            await guild.delete_scheduled_event(event.id)
            if res:
                res += "\n"
            res += f"deleted {event.name} for {event.scheduled_start_time}"
    if not res:
        res = "No events deleted."
    await ctx.send(res)

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
    time_format_m = re.compile("(?P<hour>1[0-2]|[1-9])(:(?P<min>[0-5]\\d)|)(?P<m>[a|p]m)")

    def time(time):
        match = time_format_m.fullmatch(time)
        if match:
            groups: dict = match.groupdict()
            hour = int(groups['hour'])
            if groups['m'] == 'pm':
                hour += 12
            minutes = groups.get('min')
            return datetime.datetime(date.year, date.month, date.day,
                                     hour,
                                     int(minutes) if minutes is not None else 0,
                                     tzinfo=timezone.Pacific)
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
