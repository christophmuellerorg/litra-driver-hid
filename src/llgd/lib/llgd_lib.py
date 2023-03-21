"""
This module defines a library for accessing the functionality of the
Logitech Litra Glow and Logitech Litra Beam
"""
import logging
import math
import hid
from llgd.config.llgd_config import LlgdConfig

VENDOR_ID = 0x046d
LITRA_PRODUCTS = [{'name': 'Glow',
                   'id': 0xc900,
                   'usage': 0x202,
                   'buffer_length': 64},

                  {'name': 'Beam',
                   'id': 0xc901,
                   'usage': 0x202,
                   'buffer_length': 32},
                  ]

LIGHT_OFF = 0x00
LIGHT_ON = 0x01
TIMEOUT_MS = 3000
MIN_BRIGHTNESS = 0x14
MAX_BRIGHTNESS = 0xfa


buffer_length_mapping={}
config = LlgdConfig()
devices = {}

def find_devices():
    """ Search for Litra Devices
    """
    logging.info("Searching for litra devices...")
    for product in LITRA_PRODUCTS:
        product_devices = hid.enumerate(vendor_id=VENDOR_ID, product_id=product['id'])
        for product_device in product_devices:
            if "usage" in product_device and product_device["usage"] == product['usage']:
                serial = product_device["serial_number"]
                logging.info("Found Device: {} with serial {}".format(product_device["product_string"], serial))
                buffer_length_mapping[serial] = product['buffer_length']
                devices[serial] = product_device

def count():
    """ Returns a count of all devices
    """
    return len(devices)

def setup(index):
    """Sets up the device

    Raises:
        ValueError: When the device cannot be found

    Returns:
        [device, reattach]: where device is a Device object and reattach
        is a bool indicating whether the kernel driver should be reattached
    """
    if index > len(devices):
        raise ValueError('Device not found')
    
    dev_path = devices[list(devices.keys())[index]]["path"]
    dev = hid.device()
    dev.open_path(dev_path)
    
    logging.debug(dev_path)

    return dev

def teardown(dev):
    """Tears down the device
    """
    dev.close()


def light_on():
    """Turns on the light
    """
    for index in range(0, count()):
        dev = setup(index)
        dev.write([0x11, 0xff, 0x04, 0x1c, LIGHT_ON, 0x00, 0x00, 0x00, 0x00, 0x00,
                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        #dev.read(buffer_length_mapping[dev])
        logging.info("Light On")
        teardown(dev)


def light_off():
    """Turns off the light
    """
    for index in range(0, count()):
        dev = setup(index)
        dev.write([0x11, 0xff, 0x04, 0x1c, LIGHT_OFF, 0x00, 0x00, 0x00, 0x00, 0x00,
                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        #dev.read(usage_mapping[dev], buffer_length_mapping[dev])
        logging.info("Light Off")
        teardown(dev)


def set_brightness(level):
    """Sets the brightness level

    Args:
        level (int): The brigtness level from 1-100. Converted between the min and
        max brightness levels supported by the device.
    """
    for index in range(0, count()):
        dev = setup(index)
        adjusted_level = math.floor(
            MIN_BRIGHTNESS + ((level/100) * (MAX_BRIGHTNESS - MIN_BRIGHTNESS)))
        dev.write( [0x11, 0xff, 0x04, 0x4c, 0x00, adjusted_level, 0x00, 0x00, 0x00, 0x00,
                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        #dev.read(usage_mapping[dev], buffer_length_mapping[dev])
        config.update_current_state(brightness=level)
        logging.info("Brightness set to %d", level)
        teardown(dev)


def set_temperature(temp):
    """Sets the color temerpature

    Args:
        temp (int): A color temperature of between 2700 and 6500
    """
    for index in range(0, count()):
        dev = setup(index)
        byte_array = temp.to_bytes(2, 'big')
        dev.write([0x11, 0xff, 0x04, 0x9c, byte_array[0], byte_array[1], 0x00, 0x00,
                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        #dev.read(usage_mapping[dev], buffer_length_mapping[dev])
        config.update_current_state(temp=temp)
        logging.info("Temperature set to %d", temp)
        teardown(dev)

find_devices()
