import schedule
import os, sys, time
import RESTFUL

#Need to modify schedule based on daylight savings.
#tm_isdst

schedule.every().day.at("07:05").do(RESTFUL.getAllEvents_two)
schedule.every().day.at("07:06").do(RESTFUL.getAllEvents)
schedule.every().day.at("09:00").do(RESTFUL.full_meta_report)
schedule.every().day.at("22:00").do(RESTFUL.updatePastNames)
schedule.every().day.at("22:05").do(RESTFUL.updatePastTeams)
schedule.every().day.at("07:15").do(RESTFUL.get_unknown_players)
schedule.every().monday.at("07:04").do(RESTFUL.getTeamWarCardChoices)
schedule.every().monday.at("07:10").do(RESTFUL.full_team_report)


#Database Backups
#schedule.every().day.at("02:15").do(RESTFUL.dailyBackupDatabase)
#schedule.every().monday.at("02:30").do(RESTFUL.weeklyBackupDatabase)

schedule.every().hour.do(RESTFUL.processChallengeMetaReport)

#Need to fix this one since decks/cards are spread across multiple things now...
#schedule.every().day.at("22:10").do(RESTFUL.doCleanup)

# Need new function.
# Unschedule all if they exist. Schedule all new ones based on the time an event ends today - if one exists. Otherwise use the end time of the most recent event.
# Then when the time for the first schedule comes, poll events every 10 minutes until there's new events.

print("Tasks Are Scheduled")
while True:
	schedule.run_pending()
	if os.path.exists("KILL"):
		print("Clean Exit.")
		sys.exit(0)
	time.sleep(1)