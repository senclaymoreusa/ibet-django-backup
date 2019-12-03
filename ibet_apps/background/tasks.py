from background_task import background

@background(schedule=10)
def demo_task():
    print ('THIS IS ONLY A TEST')
