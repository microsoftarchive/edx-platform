import signal

from django.core.management.base import BaseCommand, CommandError
import zerorpc

import enrollment.api

class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **options):
        # s = zerorpc.Server(ScoresAPI())

        s = zerorpc.Server(enrollment.api)

        s.bind("tcp://127.0.0.1:4242")
        print "starting enrollment zserver"
#        gevent.signal(signal.SIGTERM, s.stop)
#        gevent.spawn(s.run).join()

        s.run()
