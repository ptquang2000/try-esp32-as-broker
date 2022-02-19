from time import sleep
import unittest
from unittest import TestCase
from unittest.mock import Mock, call
from paho.mqtt import client as mqtt_client


broker = 'broker'
client_id = f'subscriber1'


class TestSubscriber1(TestCase):

    def on_log(client, userdata, level, buf):
        print('log:', buf)
        TestSubscriber1._on_log(buf)


    def on_subsribe(client, userdata, mid, granted_qos):
        print('mid:', mid, 'qos:', granted_qos)
        TestSubscriber1._on_subscribe(mid, granted_qos)


    def on_message(client, userdata, message):
        print('receive message:', str(message.payload.decode('utf8')), ', topic:', message.topic, ', retain:', message.retain)
        TestSubscriber1._on_message(str(message.payload.decode('utf8')), message.topic, message.retain)

    @classmethod
    def setUpClass(self):
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
        
        TestSubscriber1._on_log = Mock()
        TestSubscriber1._on_subscribe = Mock()
        TestSubscriber1._on_message = Mock()

        client.on_log = TestSubscriber1.on_log
        client.on_message = TestSubscriber1.on_message
        client.on_subscribe = TestSubscriber1.on_subsribe

        client.connect(broker, 1883)
        client.loop_start()
        client.subscribe('house/room',0)
        sleep(8)
        client.loop_stop()

    
    def test_on_log(self):
        TestSubscriber1._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c1, k60) client_id=b'subscriber1'"),
            call('Received CONNACK (0, 0)'),
            call("Sending SUBSCRIBE (d0, m1) [(b'house/room', 0)]"),
            call("Received SUBACK"),
            call("Received PUBLISH (d0, q0, r0, m0), 'house/room', ...  (2 bytes)"),
            call("Received PUBLISH (d0, q0, r0, m0), 'house/room', ...  (3 bytes)"),
        ],any_order=True)


    def test_on_subscribe(self):
        TestSubscriber1._on_subscribe.assert_has_calls([
            call(1, (0,)),
        ], any_order=False)
        self.assertEqual(self._on_subscribe.call_count, 1)

    
    def test_on_message(self):
        TestSubscriber1._on_message.assert_has_calls([
            call('on', 'house/room', 0),
            call('off', 'house/room', 0),
        ], any_order=False)


if __name__ == '__main__':
    unittest.main()
