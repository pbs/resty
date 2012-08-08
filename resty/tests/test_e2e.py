import os
import unittest2 as unittest
from resty import Client, LazyJsonDocument, Service, Collection, Resource


def disk_loader(uri):
    fixture_dir = os.path.join(os.path.dirname(__file__), 'mocks')
    fixture_path = os.path.join(fixture_dir, uri)
    mime_type = 'application/json'
    content = open(fixture_path).read()
    return (mime_type, content)


client = Client(disk_loader)
client.register_document_parser('application/json', LazyJsonDocument)
client.register_document('application/vnd.test-service+json', Service)
client.register_document(
    'application/vnd.test-collection+json', Collection
)
client.register_document('application/vnd.test-resource+json', Resource)


class TestClient(unittest.TestCase):

    def _get_target(self):
        return client

    def test_available_cars(self):
        c = self._get_target()
        home = c.load('entrypoint.json')
        car_collection = home.service('cars')
        self.assertEqual(len(car_collection.items()), 3)

    def test_car_model(self):
        c = self._get_target()
        home = c.load('entrypoint.json')
        car_collection = home.service('cars')
        c = car_collection.items()[0]
        self.assertEqual(c.content.model, "Opel")

    def test_applications_by_customer1(self):
        c = self._get_target()
        home = c.load('entrypoint.json')
        customer_collection = home.service('customers')
        c3_resource = customer_collection.items()[0]
        related_app = c3_resource.related('children', 'Application')
        self.assertEqual(len(related_app.items()), 2)
