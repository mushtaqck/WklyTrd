import threading  


class DataJobs(object):
    """description of class"""
    def __init__(self,object_lst=None,**kwargs):
        self.objs = object_lst
        self.worker = None

    def run(self,frequency,func=None,**kwargs):

        def runfunc(o,func):
            if type(func) == list:
                for f in func:
                    if type(f) == tuple:
                        funcname,param = f
                        callfunc = getattr(o,funcname)
                        callfunc(param)
                    else:
                        callfunc = getattr(o,f)
                        callfunc()
            else:
                callfunc = getattr(o,func)
                callfunc()

        def schedule():
            if self.objs and func :
                if type(self.objs) == list:
                    for o in self.objs:
                        runfunc(o,func)
                else:
                    runfunc(self.objs,func)

            if 'run_this' in kwargs:
                callfunc,param = kwargs['run_this']
                callfunc(param)

            self.worker = threading.Timer(frequency,schedule)
            self.worker.start()

        schedule()

    def stop(self):
        if self.worker:
            self.worker.cancel()
        else:
            print 'worker not initialized'




