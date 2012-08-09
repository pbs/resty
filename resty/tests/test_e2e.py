import os
import unittest2 as unittest
from resty import (
    Client, LazyJsonDocument, Service, Collection, Resource, JsonDocument
)


def disk_loader(uri):
    fixture_dir = os.path.join(os.path.dirname(__file__), 'mocks')
    fixture_path = os.path.join(fixture_dir, uri)
    mime_type = 'application/json'
    content = open(fixture_path).read()
    return (mime_type, content)


class TestClient(unittest.TestCase):

    def _get_target(self):
        client = Client(disk_loader)
        client.register_document_parser('application/json', LazyJsonDocument)
        client.register_document('application/vnd.test-service+json', Service)
        client.register_document(
            'application/vnd.test-collection+json', Collection
        )
        client.register_document(
            'application/vnd.test-resource+json', Resource
        )
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

    def test_status_applications_by_customer1(self):
        c = self._get_target()
        home = c.load('entrypoint.json')
        customer_collection = home.service('customers')
        c1_resource = customer_collection.items()[0]
        related_app = c1_resource.related('children', 'Application')
        api_app_status = [r.content.status for r in related_app.items()]
        self.assertEqual(api_app_status, ['pending', 'approved'])

    def test_application5_history(self):
        c = self._get_target()
        app5_resource = c.load('applications/app5.json')
        customer_name = app5_resource.related('applied_by').content.name
        car_model = app5_resource.related('parent').content.model
        self.assertEqual([customer_name, car_model], ['Donald Bob', 'Opel'])

    def test_car2_rentals(self):
        c = self._get_target()
        car2_resource = c.load('cars/car2.json')
        car2_applications = car2_resource.related('children')
        api_applied_by = []
        for c in car2_applications.items():
            api_applied_by.append(c.related('applied_by').content.name)
        self.assertEqual(api_applied_by, ['John Smith', 'Donald Bob'])


class TestDumbClient(TestClient):

    def _get_target(self):
        dumb_client = Client(disk_loader)
        dumb_client.register_document_parser('application/json', JsonDocument)
        dumb_client.register_document(
            'application/vnd.test-service+json', Service
        )
        dumb_client.register_document(
            'application/vnd.test-collection+json', Collection
        )
        dumb_client.register_document(
            'application/vnd.test-resource+json', Resource
        )
        return dumb_client
