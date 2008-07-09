from twisted.trial import unittest

import labrad
from labrad import types as T

TEST_STR = "this is a test, this is only a test"

class ClientTests(unittest.TestCase):
    def setUp(self):
        self.cxn = labrad.connect(host='localhost')

    def tearDown(self):
        self.cxn.disconnect()

    def _get_manager(self):
        self.assert_(hasattr(self.cxn, 'manager'))
        return self.cxn.manager

    def _get_tester(self):
        self.assert_(hasattr(self.cxn, 'python_test_server'))
        return self.cxn.python_test_server

    def testConnection(self):
        servers = self.cxn.servers
        self.assert_(len(servers.keys()) > 0)
        self.assert_('manager' in servers)
        self.assert_('python_test_server' in servers)

        self._get_manager()
        self._get_tester()
        
        self._get_manager()
        self._get_tester()

    def testServer(self):
        pts = self._get_tester()

        # make sure we can access the setting by both allowed methods
        self.assert_(hasattr(pts, 'echo'))
        self.assert_('echo' in pts.settings)

        # single setting, named explicitly
        resp = pts.echo(TEST_STR)
        self.assertEquals(resp, TEST_STR)

        resp = pts.echo(T.Value(15.0, 's'))
        self.assertEquals(float(resp), 15.0)
        self.assertEquals(resp.unit.name, 's')

        # single setting with the name looked up
        resp = pts.settings['echo']([1,2,3,4])
        self.assertEquals(len(resp), 4)

        # single setting with delayed response
        resp = pts.echo(TEST_STR, wait=False)
        resp = resp.wait()
        self.assertEquals(resp, TEST_STR)

    def testCompoundPacket(self):
        pts = self._get_tester()

        self.assert_(hasattr(pts, 'packet'))

        # make a simple packet and check the various methods of getting
        # data out of it
        pkt = pts.packet()
        resp = pkt.echo(1).echo(2).settings['echo'](3).send()
        self.assert_(hasattr(resp, 'echo'))
        self.assertEquals(len(resp.echo), 3)
        self.assert_('echo' in resp.settings)
        self.assertEquals(len(resp.settings['echo']), 3)
        self.assertEquals(len(resp['echo']), 3)
        
        # test using keys to refer to parts of a packet
        pkt2 = pts.packet()
        resp = pkt2.echo(1L, key='one')\
                   .echo_delay(T.Value(2, 's'))\
                   .delayed_echo('blah', key='two')\
                   .send()
        self.assert_(hasattr(resp, 'one'))
        self.assert_('one' in resp.settings)
        self.assertEquals(resp['one'], 1)
        self.assert_(not hasattr(resp, 'echo_word'))
        self.assertEquals(resp.two, 'blah')

        # test packet mutation by key
        pkt2['two'] = TEST_STR
        resp = pkt2.send()
        self.assertEquals(resp.two, TEST_STR)
        

    def testExceptions(self):
        pts = self._get_tester()

        self.assertRaises(Exception, pts.exc_in_handler)
        self.assertRaises(Exception, pts.exc_in_subfunction)
        self.assertRaises(Exception, pts.exc_in_deferred)
        self.assertRaises(Exception, pts.exc_in_errback)
        self.assertRaises(Exception, pts.exc_in_inlinecallback)