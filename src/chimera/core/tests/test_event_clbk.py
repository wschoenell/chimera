import time

from chimera.core.proxy import Proxy

p = Proxy("127.0.0.1:6379/FakeDome/fake")
print(p.ping(), p.get_az())


def callback(topic, *args, **kwargs):
    print("callback", topic, args, kwargs)


p.sync_begin += callback


fits = None

while True:
    print(p.client.transport.pubsub_thread.is_alive())
    if fits is None:
        t0 = time.time()
        from astropy.io import fits

        print("import time", time.time() - t0)
    time.sleep(0.1)
