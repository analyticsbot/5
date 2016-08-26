from apscheduler.schedulers.blocking import BlockingScheduler

## scheduler that runs every 24 hours and likes/RTs tweets
sched = BlockingScheduler()
@sched.scheduled_job('interval', seconds = 1)
def timed_job():
    print 'cron job'
    runTheProgram()

def runTheProgram():
    print 'rp'

sched.start()
