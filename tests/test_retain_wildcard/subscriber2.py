from time import sleep
import unittest
from unittest import TestCase
from unittest.mock import Mock, call
from paho.mqtt import client as mqtt_client


broker = 'broker'
client_id = f'subscriber2'


class TestSubscriber2(TestCase):

    def on_log(client, userdata, level, buf):
        print('log:', buf)
        TestSubscriber2._on_log(buf)


    def on_subsribe(client, userdata, mid, granted_qos):
        print('mid:', mid, 'qos:', granted_qos)
        TestSubscriber2._on_subscribe(mid, granted_qos)


    def on_message(client, userdata, message):
        print('receive message:', str(message.payload.decode('utf8')), ', topic:', message.topic, ', retain:', message.retain)
        TestSubscriber2._on_message(str(message.payload.decode('utf8')), message.topic, message.retain)

    @classmethod
    def setUpClass(self):
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
        
        TestSubscriber2._on_log = Mock()
        TestSubscriber2._on_subscribe = Mock()
        TestSubscriber2._on_message = Mock()

        client.on_log = TestSubscriber2.on_log
        client.on_message = TestSubscriber2.on_message
        client.on_subscribe = TestSubscriber2.on_subsribe

        client.connect(broker, 1883)
        client.loop_start()
        
        sleep(4)
        client.subscribe('house/+/main-light',0)
        sleep(6)
        client.loop_stop()

    
    def test_on_log(self):
        TestSubscriber2._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c1, k60) client_id=b'subscriber2'"),
            call('Received CONNACK (0, 0)'),
            call("Sending SUBSCRIBE (d0, m1) [(b'house/+/main-light', 0)]"),
            call("Received SUBACK"),
            call("Received PUBLISH (d0, q0, r1, m0), 'house/garage/main-light', ...  (6 bytes)"),
            call("Received PUBLISH (d0, q0, r1, m0), 'house/room/main-light', ...  (9 bytes)"),
        ],any_order=True)


    def test_on_subscribe(self):
        TestSubscriber2._on_subscribe.assert_has_calls([
            call(1, (0,)),
        ], any_order=False)
        self.assertEqual(self._on_subscribe.call_count, 1)

    
    def test_on_message(self):
        TestSubscriber2._on_message.assert_has_calls([
            call('garage', 'house/garage/main-light', 1),
            call('room-main', 'house/room/main-light', 1),
        ], any_order=True)
        self.assertEqual(self._on_message.call_count, 2)


if __name__ == '__main__':
    unittest.main()