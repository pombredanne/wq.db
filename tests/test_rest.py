from rest_framework.test import APITestCase
from rest_framework import status
import json
from tests.rest_app.models import (
    RootModel, OneToOneModel, ForeignKeyModel, ExtraModel, UserManagedModel,
    Parent, ItemType, GeometryModel, SlugModel, DateModel, ChoiceModel,
)
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured


class RestTestCase(APITestCase):
    def setUp(self):
        instance = RootModel.objects.create(
            slug='instance',
            description="Test",
        )
        for cls in OneToOneModel, ForeignKeyModel, ExtraModel:
            cls.objects.create(
                root=instance,
            )
        self.user = User.objects.create(username="testuser")
        UserManagedModel.objects.create(id=1, user=self.user)
        parent = Parent.objects.create(name="Test", pk=1)
        parent.children.create(name="Test 1")
        parent.children.create(name="Test 2")
        parent2 = Parent.objects.create(name="Test 2", pk=2)
        parent2.children.create(name="Test 1")
        itype = ItemType.objects.create(name="Test", pk=1)
        itype.item_set.create(name="Test 1")
        itype.item_set.create(name="Test 2")
        SlugModel.objects.create(
            code="test",
            name="Test",
        )
        DateModel.objects.create(
            pk=1,
            name="Test",
            date="2015-01-01 12:00Z",
        )
        ChoiceModel.objects.create(
            pk=1,
            name="Test",
            choice="two",
        )

    def get_config(self, result, page_name):
        self.assertIn('pages', result)
        self.assertIn(page_name, result['pages'])
        return result['pages'][page_name]

    def get_field(self, page_config, field_name):
        self.assertIn('form', page_config)
        for field in page_config['form']:
            if field['name'] == field_name:
                return field
        self.fail("Could not find %s" % field_name)

    # Test existence and content of config.json
    def test_rest_config_json(self):
        response = self.client.get('/config.json')
        result = json.loads(response.content.decode('utf-8'))
        self.assertIn("pages", result)

        # Extra config
        self.assertIn("debug", result)

    def test_rest_index_json(self):
        from wq.db.rest import router
        result = router.get_index(self.user)
        self.assertIn("pages", result)
        self.assertIn("list", result["pages"][0])
        self.assertNotIn("list", result["pages"][-1])

    def test_rest_config_json_fields(self):
        response = self.client.get('/config.json')
        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual([
            {
                'name': 'name',
                'label': 'Name',
                'type': 'string',
                'wq:length': 10,
                'bind': {'required': True},
            },
            {
                'name': 'date',
                'label': 'Date',
                'type': 'dateTime',
                'bind': {'required': True},
            },
            {
                'name': 'empty_date',
                'label': 'Empty Date',
                'type': 'dateTime',
            },
        ], self.get_config(result, 'datemodel')['form'])

    def test_rest_config_json_choices(self):
        response = self.client.get('/config.json')
        result = json.loads(response.content.decode('utf-8'))
        conf = self.get_config(result, 'choicemodel')
        self.assertEqual([
            {
                'name': 'name',
                'label': 'Name',
                'hint': 'Enter Name',
                'type': 'string',
                'wq:length': 10,
                'bind': {'required': True},
            },
            {
                'name': 'choice',
                'label': 'Choice',
                'hint': 'Pick One',
                'type': 'select1',
                'bind': {'required': True},
                'choices': [{
                    'name': 'one',
                    'label': 'Choice One',
                }, {
                    'name': 'two',
                    'label': 'Choice Two',
                }, {
                    'name': 'three',
                    'label': 'Choice Three',
                }]
            }
        ], conf['form'])

    def test_rest_config_json_rels(self):
        response = self.client.get('/config.json')
        result = json.loads(response.content.decode('utf-8'))

        pconf = self.get_config(result, 'parent')
        self.assertEqual({
            'name': 'children',
            'label': 'Children',
            'type': 'repeat',
            'bind': {'required': True},
            'children': [{
                'name': 'name',
                'label': 'Name',
                'type': 'string',
                'wq:length': 10,
                'bind': {'required': True},
            }]
        }, self.get_field(pconf, 'children'))

        cconf = self.get_config(result, 'child')
        self.assertEqual({
            'name': 'parent',
            'label': 'Parent',
            'type': 'string',
            'wq:ForeignKey': 'parent',
            'bind': {'required': True},
        }, self.get_field(cconf, 'parent'))

    # Test url="" use case
    def test_rest_list_at_root(self):
        response = self.client.get("/.json")
        self.assertTrue(status.is_success(response.status_code), response.data)
        self.assertTrue(len(response.data['list']) == 1)

    def test_rest_detail_at_root(self):
        response = self.client.get('/instance.json')
        self.assertTrue(status.is_success(response.status_code), response.data)
        self.assertTrue(response.data['description'] == "Test")

    # Test nested models with foreign keys
    def test_rest_detail_nested_foreignkeys(self):
        response = self.client.get('/instance.json')

        # Include explicitly declared serializers for related fields
        self.assertIn("onetoonemodel", response.data)
        self.assertEqual(
            response.data["onetoonemodel"]["label"],
            "onetoonemodel for instance"
        )
        self.assertIn("extramodels", response.data)
        self.assertEqual(
            response.data["extramodels"][0]["label"],
            "extramodel for instance"
        )

        # Related fields without explicit serializers will not be included
        self.assertNotIn("extramodel_set", response.data)
        self.assertNotIn("foreignkeymodel_set", response.data)
        self.assertNotIn("foreignkeymodels", response.data)

    def test_rest_filter_by_parent(self):
        response = self.client.get('/parents/1/children.json')
        self.assertIn("list", response.data)
        self.assertEqual(len(response.data['list']), 2)

        response = self.client.get('/itemtypes/1/items.json')
        self.assertIn("list", response.data)
        self.assertEqual(len(response.data['list']), 2)

    def test_rest_target_to_children(self):
        response = self.client.get('/children-by-parents.json')
        self.assertIn("list", response.data)
        self.assertEqual(len(response.data['list']), 2)
        self.assertIn("target", response.data)
        self.assertEqual(response.data['target'], 'children')

    def test_rest_detail_user_serializer(self):
        response = self.client.get('/usermanagedmodels/1.json')
        self.assertIn('user', response.data)
        self.assertIn('label', response.data['user'])
        self.assertNotIn('password', response.data['user'])

    def test_rest_multi(self):
        lists = ['usermanagedmodels', 'items', 'children']
        response = self.client.get(
            "/multi.json?lists=" + ",".join(lists)
        )
        for listurl in lists:
            self.assertIn(listurl, response.data)
            self.assertIn("list", response.data[listurl])
            self.assertGreater(len(response.data[listurl]["list"]), 0)

    def test_rest_custom_lookup(self):
        response = self.client.get('/slugmodels/test.json')
        self.assertTrue(status.is_success(response.status_code), response.data)
        self.assertEqual(response.data['id'], 'test')

    def test_rest_default_per_page(self):
        response = self.client.get('/parents.json')
        self.assertTrue(status.is_success(response.status_code), response.data)
        self.assertEqual(response.data['per_page'], 50)

    def test_rest_custom_per_page(self):
        response = self.client.get('/children.json')
        self.assertTrue(status.is_success(response.status_code), response.data)
        self.assertEqual(response.data['per_page'], 100)

    def test_rest_limit(self):
        response = self.client.get('/children.json?limit=10')
        self.assertTrue(status.is_success(response.status_code), response.data)
        self.assertEqual(response.data['per_page'], 10)

    def test_rest_date_label(self):
        response = self.client.get("/datemodels/1.json")
        self.assertTrue(status.is_success(response.status_code), response.data)
        self.assertIn('date_label', response.data)
        self.assertEqual(response.data['date_label'], "2015-01-01 06:00 AM")

    def test_rest_choice_label(self):
        response = self.client.get("/choicemodels/1.json")
        self.assertTrue(status.is_success(response.status_code), response.data)
        self.assertIn('choice_label', response.data)
        self.assertEqual(response.data['choice_label'], "Choice Two")


class RestRouterTestCase(APITestCase):
    def test_rest_model_conflict(self):
        from wq.db import rest
        from tests.conflict_app.models import Item

        # Register model with same name as existing model
        with self.assertRaises(ImproperlyConfigured) as e:
            rest.router.register_model(Item)
        self.assertEqual(
            e.exception.args[0],
            "Could not register <class 'tests.conflict_app.models.Item'>: "
            "the name 'item' was already registered for "
            "<class 'tests.rest_app.models.Item'>"
        )

        # Register model with different name, but same URL as existing model
        with self.assertRaises(ImproperlyConfigured) as e:
            rest.router.register_model(Item, name="conflictitem")
        self.assertEqual(
            e.exception.args[0],
            "Could not register <class 'tests.conflict_app.models.Item'>: "
            "the url 'items' was already registered for "
            "<class 'tests.rest_app.models.Item'>"
        )

        # Register model with different name and URL
        rest.router.register_model(
            Item, name="conflictitem", url="conflictitems"
        )
        self.assertIn("conflictitem", rest.router.get_config()['pages'])


class RestPostTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", is_superuser=True)
        self.client.force_authenticate(self.user)

    def test_rest_geometry_post_geojson(self):
        """
        Posting GeoJSON to a model with a geometry field should work.
        """
        form = {
            'name': "Geometry Test 1",
            'geometry': json.dumps({
                "type": "Point",
                "coordinates": [-90, 44]
            })
        }

        # Test for expected response
        response = self.client.post('/geometrymodels.json', form)
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED, response.data
        )

        # Double-check ORM model & geometry attribute
        obj = GeometryModel.objects.get(id=response.data['id'])
        geom = obj.geometry
        self.assertEqual(geom.srid, 4326)
        self.assertEqual(geom.x, -90)
        self.assertEqual(geom.y, 44)

    def test_rest_geometry_post_wkt(self):
        """
        Posting WKT to a model with a geometry field should work.
        """
        form = {
            'name': "Geometry Test 2",
            'geometry': "POINT(%s %s)" % (-97, 50)
        }

        # Test for expected response
        response = self.client.post('/geometrymodels.json', form)
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED, response.data
        )

        # Double-check ORM model & geometry attribute
        obj = GeometryModel.objects.get(id=response.data['id'])
        geom = obj.geometry
        self.assertEqual(geom.srid, 4326)
        self.assertEqual(geom.x, -97)
        self.assertEqual(geom.y, 50)

    def test_rest_date_label_post(self):
        """
        Posting to a model with a date should return a label and an ISO date
        """
        form = {
            'name': "Test Date",
            'date': '2015-06-01 12:00:00Z',
        }
        response = self.client.post("/datemodels.json", form)
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED, response.data
        )
        self.assertIn('date_label', response.data)
        self.assertEqual(response.data['date_label'], "2015-06-01 07:00 AM")
        self.assertIn('date', response.data)
        self.assertEqual(response.data['date'], "2015-06-01T12:00:00Z")

    def test_rest_empty_date_post(self):
        """
        Allow posting an empty date if the field allows nulls
        """
        form = {
            'name': "Test Date",
            'date': '2015-06-01 12:00:00Z',
            'empty_date': '',
        }
        response = self.client.post("/datemodels.json", form)
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED, response.data
        )
