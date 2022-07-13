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


@bot.command(name="get_hours",
             description="get the events corresponding to a given user's DA hours",
             options=[
                 interactions.Option(name="user",
                                     description="Departmental Assistance holding the hours",
                                     type=interactions.OptionType.USER,
                                     required=True)
             ])
async def get_hours(ctx: interactions.CommandContext, user: interactions.User):
    await ctx.get_guild()
    # event description starts with the DA user
    matches = filter(lambda event: event.description.startswith(user.mention), (await get_scheduled_events(ctx))[::-1])
    res = str.join('\n', map(lambda e: 'https://discord.gg/whW3SsZUqG?event=' + str(e.id), matches))
    await ctx.send(res if res else f"No events found for {user.mention}")
def __relative_date(day: int):
    today = datetime.date.today()
    days_from_today = ((day + 7) - today.weekday()) % 7
    # calculate new date
    return today + datetime.timedelta(days=days_from_today)


time_format_m = re.compile("(?P<hour>1[0-2]|[1-9])(:(?P<min>[0-5]\\d)|)(?P<m>[a|p]m)")

def __time12(time_str):
    match = time_format_m.fullmatch(time_str)
    if match:
        groups: dict = match.groupdict()
        hour = int(groups['hour'])
        if groups['m'] == 'pm':
            hour += 12
            hour %= 24
        minutes = groups.get('min')
        return datetime.time(hour, int(minutes) if minutes is not None else 0, tzinfo=timezone.Pacific)
    return None


def __datetime(date: datetime.date, time: datetime.time) -> datetime.datetime:
    return datetime.datetime(date.year,date.month,date.day,time.hour,time.minute,time.second,time.microsecond,time.tzinfo)


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
    # todo move to own method logic
    date = __relative_date(day)
    # calculate proper start time
    start_time = __datetime(date, __time12(start_time))
    end_time = __datetime(date, __time12(end_time))

    if start_time.replace(tzinfo=None) < datetime.datetime.now():
        # todo determine if we want to simply specify a duration instead of an end time.
        start_time += datetime.timedelta(weeks=1)
        end_time += datetime.timedelta(weeks=1)

    if start_time is not None and end_time is not None:
        await ctx.get_guild()
        await ctx.guild.create_scheduled_event(
            "DA Hours", interactions.EntityType.EXTERNAL,
            start_time.isoformat(), end_time.isoformat(),
            interactions.EventMetadata(location='D13'),
            description=f"{user.mention} will be holding DA hours.",
        )
        msg = f"Added hours for {user.mention} on " \
              + start_time.strftime("%a %m/%d from %I:%M%p") \
              + " to " + end_time.strftime("%I:%M%p")
        await ctx.send(msg)
    else:
        await ctx.send("Invalid time entry")


bot.start()
