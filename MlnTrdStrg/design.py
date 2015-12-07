class Feeder(object):
    import sched
    import time
    s = sched.scheduler(time.time, time.sleep)

    def __init__(self,source_feeder,vehicle_list,frequency):
        self.source_feeder = source_feeder
        self.vehicle_list = vehicle_list


    def run(self, frequency):
        def schedule(sc):
            print self.source_feeder,self.vehicle_list, 'called--'
            sc.enter(tm, 1, fetch_sequencial, (sc,))

        s.enter(frequency, 1, schedule, (s,))
        s.run()


class RedisFeeder(object):
    def __init__(self, *args, **kwargs):
        return super(RedisFeeder, self).__init__(*args, **kwargs)

    def run(self,**kwargs):
        pass


class MoneyControlTerminalFeeder(object):
    def __init__(self, *args, **kwargs):
        return super(MoneyControlTerminalFeeder, self).__init__(*args, **kwargs)

    def run(self,**kwargs):
        pass

class NSEFeeder(object):
    def __init__(self, *args, **kwargs):
        return super(NSEFeeder, self).__init__(*args, **kwargs)

    def run(self,**kwargs):
        pass

class YahooFinanceFeeder(object):
    def __init__(self, *args, **kwargs):
        return super(YahooFinanceFeeder, self).__init__(*args, **kwargs)

    def run(self,**kwargs):
        pass


class DataParser(object):
    def __init__(self, *args, **kwargs):
        return super(DataParser, self).__init__(*args, **kwargs)

class Vehicle(object):
    def __init__(self, *args, **kwargs):
        return super(Vehicle, self).__init__(*args, **kwargs)

    def set_last(self,symbol,**kwargs):
        return 0

    def get_last(self,symbol,**kwargs):
        vals = {}
        return vals
    

    @staticmethod
    def make_car_sound():
        print 'VRooooommmm!'

    @classmethod
    def is_motorcycle(cls):
        return cls.wheels == 2



class Store():
    def __init__(self):
        pass

class AFP():
    def __init__(self):
        pass
