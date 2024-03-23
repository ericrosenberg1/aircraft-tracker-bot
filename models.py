# Define your data models here, such as Flight, Message, etc.
class Flight:
    def __init__(self, id, takeoff_time, landing_time, status):
        self.id = id
        self.takeoff_time = takeoff_time
        self.landing_time = landing_time
        self.status = status
