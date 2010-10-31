#coding: utf-8
import xml.etree.ElementTree as ET

def gen_xml(root, kwargs):
    root_elem = ET.Element(root)
    for key, value in kwargs:
        ET.SubElement(root_elem, key).text = unicode(value)
    return ET.tostring(root_elem, 'utf8')


def error(error_code, error_description, error_parameters='', critical=True):
    return gen_xml('failure', (
       ('error-code', error_code),
       ('error-description', error_description),
       ('error-parameters', error_parameters),
       ('critical', str(critical).lower())
    ))


def status_change_success(order_id, merchant_order_id):
    return gen_xml('success', (
       ('order-id', order_id),
       ('merchant-order-id', merchant_order_id),
    ))

