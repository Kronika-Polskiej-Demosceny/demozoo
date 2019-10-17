from __future__ import absolute_import, unicode_literals

from io import BytesIO
import os

from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from mock import patch
import PIL.Image

from demoscene.models import Nick
from parties.models import Party
from platforms.models import Platform
from productions.models import Production, ProductionLink, ProductionType


def get_test_image():
    f = BytesIO()
    image = PIL.Image.new('RGBA', (200, 200), 'white')
    image.save(f, 'PNG')
    return ImageFile(f, name='test.png')


class TestIndex(TestCase):
    fixtures = ['tests/gasman.json']

    def test_get(self):
        demo = ProductionType.objects.get(name='Demo').id
        zx = Platform.objects.get(name='ZX Spectrum').id
        response = self.client.get('/productions/?platform=%d&production_type=%d' % (zx, demo))
        self.assertEqual(response.status_code, 200)

    def test_get_by_title(self):
        response = self.client.get('/productions/?order=title')
        self.assertEqual(response.status_code, 200)

    def test_get_by_date_asc(self):
        response = self.client.get('/productions/?dir=asc')
        self.assertEqual(response.status_code, 200)


class TestTagIndex(TestCase):
    fixtures = ['tests/gasman.json']

    def test_get(self):
        pondlife = Production.objects.get(title="Pondlife")
        pondlife.tags.add('48k')
        response = self.client.get('/productions/tagged/48k/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/productions/tagged/something-random/')
        self.assertEqual(response.status_code, 200)


class TestShowProduction(TestCase):
    fixtures = ['tests/gasman.json']

    def test_get(self):
        pondlife = Production.objects.get(title="Pondlife")
        response = self.client.get('/productions/%d/' % pondlife.id)
        self.assertEqual(response.status_code, 200)

    def test_get_pack(self):
        pondlife = Production.objects.get(title="Pondlife")
        pondlife.types.add(ProductionType.objects.get(name='Pack'))
        response = self.client.get('/productions/%d/' % pondlife.id)
        self.assertEqual(response.status_code, 200)

    def test_redirect_non_prod(self):
        cybrev = Production.objects.get(title="Cybernoid's Revenge")
        response = self.client.get('/productions/%d/' % cybrev.id)
        self.assertRedirects(response, '/music/%d/' % cybrev.id)


class TestShowHistory(TestCase):
    fixtures = ['tests/gasman.json']

    def test_get(self):
        pondlife = Production.objects.get(title="Pondlife")
        response = self.client.get('/productions/%d/history/' % pondlife.id)
        self.assertEqual(response.status_code, 200)

    def test_redirect_non_prod(self):
        cybrev = Production.objects.get(title="Cybernoid's Revenge")
        response = self.client.get('/productions/%d/history/' % cybrev.id)
        self.assertRedirects(response, '/music/%d/history/' % cybrev.id)


class TestCreateProduction(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_get(self):
        response = self.client.get('/productions/new/')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post('/productions/new/', {
            'title': 'Ultraviolet',
            'byline_search': 'Gasman',
            'byline_author_match_0_id': Nick.objects.get(name='Gasman').id,
            'byline_author_match_0_name': 'Gasman',
            'release_date': 'march 2017',
            'type': ProductionType.objects.get(name='Demo').id,
            'platform': Platform.objects.get(name='ZX Spectrum').id,
            'links-TOTAL_FORMS': 0,
            'links-INITIAL_FORMS': 0,
            'links-MIN_NUM_FORMS': 0,
            'links-MAX_NUM_FORMS': 1000,
        })
        self.assertRedirects(response, '/productions/%d/' % Production.objects.get(title='Ultraviolet').id)


class TestEditCoreDetails(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_locked(self):
        mooncheese = Production.objects.get(title='Mooncheese')
        response = self.client.get('/productions/%d/edit_core_details/' % mooncheese.id)
        self.assertEqual(response.status_code, 403)

    def test_get_production(self):
        pondlife = Production.objects.get(title='Pondlife')
        response = self.client.get('/productions/%d/edit_core_details/' % pondlife.id)
        self.assertEqual(response.status_code, 200)

    def test_get_music(self):
        cybrev = Production.objects.get(title="Cybernoid's Revenge")
        response = self.client.get('/productions/%d/edit_core_details/' % cybrev.id)
        self.assertEqual(response.status_code, 200)

    def test_get_graphics(self):
        skyrider = Production.objects.get(title="Skyrider")
        response = self.client.get('/productions/%d/edit_core_details/' % skyrider.id)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        pondlife = Production.objects.get(title='Pondlife')
        response = self.client.post('/productions/%d/edit_core_details/' % pondlife.id, {
            'title': 'P0ndlife',
            'byline_search': 'Hooy-Program',
            'byline_author_match_0_id': Nick.objects.get(name='Hooy-Program').id,
            'byline_author_match_0_name': 'Hooy-Program',
            'release_date': '18 March 2001',
            'types': ProductionType.objects.get(name='Demo').id,
            'platforms': Platform.objects.get(name='ZX Spectrum').id,
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-0-party_search': 'Forever 2e3',
            'form-0-party_party_id': Party.objects.get(name='Forever 2e3').id,
        })
        self.assertRedirects(response, '/productions/%d/' % pondlife.id)
        self.assertTrue(Production.objects.filter(title='P0ndlife').exists())
        self.assertEqual(pondlife.invitation_parties.count(), 1)

    def test_post_unset_invitation(self):
        pondlife = Production.objects.get(title='Pondlife')
        forever2e3 = Party.objects.get(name='Forever 2e3')
        pondlife.invitation_parties.add(forever2e3)
        response = self.client.post('/productions/%d/edit_core_details/' % pondlife.id, {
            'title': 'P0ndlife',
            'byline_search': 'Hooy-Program',
            'byline_author_match_0_id': Nick.objects.get(name='Hooy-Program').id,
            'byline_author_match_0_name': 'Hooy-Program',
            'release_date': '18 March 2001',
            'types': ProductionType.objects.get(name='Demo').id,
            'platforms': Platform.objects.get(name='ZX Spectrum').id,
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 1,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-0-party_search': 'Forever 2e3',
            'form-0-party_party_id': forever2e3.id,
            'form-0-DELETE': 'form-0-DELETE'
        })
        self.assertRedirects(response, '/productions/%d/' % pondlife.id)
        self.assertTrue(Production.objects.filter(title='P0ndlife').exists())
        self.assertEqual(pondlife.invitation_parties.count(), 0)


class TestEditNotes(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        User.objects.create_superuser(username='testsuperuser', email='testsuperuser@example.com', password='12345')
        self.client.login(username='testsuperuser', password='12345')
        self.pondlife = Production.objects.get(title='Pondlife')

    def test_non_superuser(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        response = self.client.get('/productions/%d/edit_notes/' % self.pondlife.id)
        self.assertRedirects(response, '/productions/%d/' % self.pondlife.id)

    def test_get(self):
        response = self.client.get('/productions/%d/edit_notes/' % self.pondlife.id)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post('/productions/%d/edit_notes/' % self.pondlife.id, {
            'notes': "I am one thousand years old",
        })
        self.assertRedirects(response, '/productions/%d/' % self.pondlife.id)
        self.assertEqual(Production.objects.get(id=self.pondlife.id).notes, "I am one thousand years old")


class TestAddBlurb(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        User.objects.create_superuser(username='testsuperuser', email='testsuperuser@example.com', password='12345')
        self.client.login(username='testsuperuser', password='12345')
        self.pondlife = Production.objects.get(title='Pondlife')

    def test_non_superuser(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        response = self.client.get('/productions/%d/add_blurb/' % self.pondlife.id)
        self.assertRedirects(response, '/productions/%d/' % self.pondlife.id)

    def test_get(self):
        response = self.client.get('/productions/%d/add_blurb/' % self.pondlife.id)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post('/productions/%d/add_blurb/' % self.pondlife.id, {
            'body': "Hooy-Program's love letter to the humble duck",
        })
        self.assertRedirects(response, '/productions/%d/' % self.pondlife.id)
        self.assertEqual(self.pondlife.blurbs.count(), 1)


class TestEditBlurb(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        User.objects.create_superuser(username='testsuperuser', email='testsuperuser@example.com', password='12345')
        self.client.login(username='testsuperuser', password='12345')
        self.pondlife = Production.objects.get(title='Pondlife')
        self.blurb = self.pondlife.blurbs.create(body="Hooy-Program's love letter to the humble duck")

    def test_non_superuser(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        response = self.client.get('/productions/%d/edit_blurb/%d/' % (self.pondlife.id, self.blurb.id))
        self.assertRedirects(response, '/productions/%d/' % self.pondlife.id)

    def test_get(self):
        response = self.client.get('/productions/%d/edit_blurb/%d/' % (self.pondlife.id, self.blurb.id))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post('/productions/%d/edit_blurb/%d/' % (self.pondlife.id, self.blurb.id), {
            'body': "Hooy-Program's love letter to the humble mallard",
        })
        self.assertRedirects(response, '/productions/%d/' % self.pondlife.id)
        self.assertEqual(self.pondlife.blurbs.get().body, "Hooy-Program's love letter to the humble mallard")


class TestDeleteBlurb(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        User.objects.create_superuser(username='testsuperuser', email='testsuperuser@example.com', password='12345')
        self.client.login(username='testsuperuser', password='12345')
        self.pondlife = Production.objects.get(title='Pondlife')
        self.blurb = self.pondlife.blurbs.create(body="Hooy-Program's love letter to the humble duck")

    def test_non_superuser(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        response = self.client.get('/productions/%d/delete_blurb/%d/' % (self.pondlife.id, self.blurb.id))
        self.assertRedirects(response, '/productions/%d/' % self.pondlife.id)

    def test_get(self):
        response = self.client.get('/productions/%d/delete_blurb/%d/' % (self.pondlife.id, self.blurb.id))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post('/productions/%d/delete_blurb/%d/' % (self.pondlife.id, self.blurb.id), {
            'yes': 'yes'
        })
        self.assertRedirects(response, '/productions/%d/' % self.pondlife.id)
        self.assertEqual(self.pondlife.blurbs.count(), 0)


class TestEditExternalLinks(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.pondlife = Production.objects.get(title='Pondlife')

    def test_locked(self):
        mooncheese = Production.objects.get(title='Mooncheese')
        response = self.client.get('/productions/%d/edit_external_links/' % mooncheese.id)
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        response = self.client.get('/productions/%d/edit_external_links/' % self.pondlife.id)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post('/productions/%d/edit_external_links/' % self.pondlife.id, {
            'links-TOTAL_FORMS': 1,
            'links-INITIAL_FORMS': 0,
            'links-MIN_NUM_FORMS': 0,
            'links-MAX_NUM_FORMS': 1000,
            'links-0-url': 'https://www.pouet.net/prod.php?which=2611',
            'links-0-production': self.pondlife.id,
        })
        self.assertRedirects(response, '/productions/%d/' % self.pondlife.id)
        self.assertEqual(
            ProductionLink.objects.filter(production=self.pondlife, link_class='PouetProduction').count(),
            1
        )


class TestEdiDownloadLinks(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.pondlife = Production.objects.get(title='Pondlife')

    def test_locked(self):
        mooncheese = Production.objects.get(title='Mooncheese')
        response = self.client.get('/productions/%d/edit_download_links/' % mooncheese.id)
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        response = self.client.get('/productions/%d/edit_download_links/' % self.pondlife.id)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post('/productions/%d/edit_download_links/' % self.pondlife.id, {
            'links-TOTAL_FORMS': 1,
            'links-INITIAL_FORMS': 0,
            'links-MIN_NUM_FORMS': 0,
            'links-MAX_NUM_FORMS': 1000,
            'links-0-url': 'https://files.scene.org/get/parties/2001/forever01/spectrum/f2speccy.zip',
            'links-0-production': self.pondlife.id,
        })
        self.assertRedirects(response, '/productions/%d/' % self.pondlife.id)
        self.assertEqual(
            ProductionLink.objects.filter(production=self.pondlife, link_class='SceneOrgFile').count(),
            1
        )


class TestShowScreenshots(TestCase):
    fixtures = ['tests/gasman.json']

    def test_get(self):
        pondlife = Production.objects.get(title="Pondlife")
        response = self.client.get('/productions/%d/screenshots/' % pondlife.id)
        self.assertEqual(response.status_code, 200)

    def test_redirect_music(self):
        cybrev = Production.objects.get(title="Cybernoid's Revenge")
        response = self.client.get('/productions/%d/screenshots/' % cybrev.id)
        self.assertRedirects(response, '/productions/%d/artwork/' % cybrev.id)


class TestShowArtwork(TestCase):
    fixtures = ['tests/gasman.json']

    def test_get(self):
        cybrev = Production.objects.get(title="Cybernoid's Revenge")
        response = self.client.get('/productions/%d/artwork/' % cybrev.id)
        self.assertEqual(response.status_code, 200)

    def test_redirect_music(self):
        pondlife = Production.objects.get(title="Pondlife")
        response = self.client.get('/productions/%d/artwork/' % pondlife.id)
        self.assertRedirects(response, '/productions/%d/screenshots/' % pondlife.id)


class TestEditScreenshots(TestCase):
    fixtures = ['tests/gasman.json']

    def test_non_superuser(self):
        User.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.client.login(username='testuser', password='12345')
        pondlife = Production.objects.get(title="Pondlife")
        response = self.client.get('/productions/%d/screenshots/edit/' % pondlife.id)
        self.assertRedirects(response, '/productions/%d/' % pondlife.id)

    def test_get(self):
        User.objects.create_superuser(username='testsuperuser', email='testsuperuser@example.com', password='12345')
        self.client.login(username='testsuperuser', password='12345')
        pondlife = Production.objects.get(title="Pondlife")
        response = self.client.get('/productions/%d/screenshots/edit/' % pondlife.id)
        self.assertEqual(response.status_code, 200)

    def test_redirect_music(self):
        User.objects.create_superuser(username='testsuperuser', email='testsuperuser@example.com', password='12345')
        self.client.login(username='testsuperuser', password='12345')
        cybrev = Production.objects.get(title="Cybernoid's Revenge")
        response = self.client.get('/productions/%d/screenshots/edit/' % cybrev.id)
        self.assertRedirects(response, '/productions/%d/artwork/edit/' % cybrev.id)


class TestEditArtwork(TestCase):
    fixtures = ['tests/gasman.json']

    def test_non_superuser(self):
        User.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.client.login(username='testuser', password='12345')
        cybrev = Production.objects.get(title="Cybernoid's Revenge")
        response = self.client.get('/productions/%d/artwork/edit/' % cybrev.id)
        self.assertRedirects(response, '/music/%d/' % cybrev.id)

    def test_get(self):
        User.objects.create_superuser(username='testsuperuser', email='testsuperuser@example.com', password='12345')
        self.client.login(username='testsuperuser', password='12345')
        cybrev = Production.objects.get(title="Cybernoid's Revenge")
        response = self.client.get('/productions/%d/artwork/edit/' % cybrev.id)
        self.assertEqual(response.status_code, 200)

    def test_redirect_nonmusic(self):
        User.objects.create_superuser(username='testsuperuser', email='testsuperuser@example.com', password='12345')
        self.client.login(username='testsuperuser', password='12345')
        pondlife = Production.objects.get(title="Pondlife")
        response = self.client.get('/productions/%d/artwork/edit/' % pondlife.id)
        self.assertRedirects(response, '/productions/%d/screenshots/edit/' % pondlife.id)


class TestAddScreenshot(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_locked(self):
        mooncheese = Production.objects.get(title='Mooncheese')
        response = self.client.get('/productions/%d/add_screenshot/' % mooncheese.id)
        self.assertEqual(response.status_code, 403)

    def test_get_production(self):
        pondlife = Production.objects.get(title='Pondlife')
        response = self.client.get('/productions/%d/add_screenshot/' % pondlife.id)
        self.assertEqual(response.status_code, 200)

    def test_redirect_production(self):
        pondlife = Production.objects.get(title='Pondlife')
        response = self.client.get('/productions/%d/add_artwork/' % pondlife.id)
        self.assertRedirects(response, '/productions/%d/add_screenshot/' % pondlife.id)

    def test_get_music(self):
        cybrev = Production.objects.get(title="Cybernoid's Revenge")
        response = self.client.get('/productions/%d/add_artwork/' % cybrev.id)
        self.assertEqual(response.status_code, 200)

    def test_redirect_music(self):
        cybrev = Production.objects.get(title="Cybernoid's Revenge")
        response = self.client.get('/productions/%d/add_screenshot/' % cybrev.id)
        self.assertRedirects(response, '/productions/%d/add_artwork/' % cybrev.id)

    @patch('screenshots.tasks.create_screenshot_versions_from_local_file')
    def test_post_production_single(self, create_screenshot_versions_from_local_file):
        pondlife = Production.objects.get(title='Pondlife')
        response = self.client.post('/productions/%d/add_screenshot/' % pondlife.id, {
            'screenshot': SimpleUploadedFile('test.png', get_test_image().file.getvalue()),
        })
        self.assertRedirects(response, '/productions/%d/' % pondlife.id)
        self.assertEqual(pondlife.screenshots.count(), 1)
        self.assertEqual(create_screenshot_versions_from_local_file.delay.call_count, 1)
        screenshot_id, filename = create_screenshot_versions_from_local_file.delay.call_args.args
        self.assertEqual(screenshot_id, pondlife.screenshots.get().id)
        os.remove(filename)

    @patch('screenshots.tasks.create_screenshot_versions_from_local_file')
    def test_post_production_multiple(self, create_screenshot_versions_from_local_file):
        pondlife = Production.objects.get(title='Pondlife')
        response = self.client.post('/productions/%d/add_screenshot/' % pondlife.id, {
            'screenshot': [
                SimpleUploadedFile('test1.png', get_test_image().file.getvalue()),
                SimpleUploadedFile('test2.png', get_test_image().file.getvalue()),
            ],
        })
        self.assertRedirects(response, '/productions/%d/' % pondlife.id)
        self.assertEqual(pondlife.screenshots.count(), 2)
        self.assertEqual(create_screenshot_versions_from_local_file.delay.call_count, 2)
        for call in create_screenshot_versions_from_local_file.delay.call_args_list:
            _, filename = call.args
            os.remove(filename)

    @patch('screenshots.tasks.create_screenshot_versions_from_local_file')
    def test_post_music_single(self, create_screenshot_versions_from_local_file):
        cybrev = Production.objects.get(title="Cybernoid's Revenge")
        response = self.client.post('/productions/%d/add_artwork/' % cybrev.id, {
            'screenshot': SimpleUploadedFile('test.png', get_test_image().file.getvalue()),
        })
        self.assertRedirects(response, '/music/%d/' % cybrev.id)
        self.assertEqual(cybrev.screenshots.count(), 1)
        self.assertEqual(create_screenshot_versions_from_local_file.delay.call_count, 1)
        screenshot_id, filename = create_screenshot_versions_from_local_file.delay.call_args.args
        self.assertEqual(screenshot_id, cybrev.screenshots.get().id)
        os.remove(filename)

    @patch('screenshots.tasks.create_screenshot_versions_from_local_file')
    def test_post_music_multiple(self, create_screenshot_versions_from_local_file):
        cybrev = Production.objects.get(title="Cybernoid's Revenge")
        response = self.client.post('/productions/%d/add_artwork/' % cybrev.id, {
            'screenshot': [
                SimpleUploadedFile('test1.png', get_test_image().file.getvalue()),
                SimpleUploadedFile('test2.png', get_test_image().file.getvalue()),
            ],
        })
        self.assertRedirects(response, '/music/%d/' % cybrev.id)
        self.assertEqual(cybrev.screenshots.count(), 2)
        self.assertEqual(create_screenshot_versions_from_local_file.delay.call_count, 2)
        for call in create_screenshot_versions_from_local_file.delay.call_args_list:
            _, filename = call.args
            os.remove(filename)


class TestDeleteScreenshot(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        User.objects.create_superuser(username='testsuperuser', email='testsuperuser@example.com', password='12345')
        self.client.login(username='testsuperuser', password='12345')
        self.pondlife = Production.objects.get(title='Pondlife')
        self.pondlife_screenshot = self.pondlife.screenshots.create()
        self.cybrev = Production.objects.get(title="Cybernoid's Revenge")
        self.cybrev_artwork = self.cybrev.screenshots.create()

    def test_non_superuser(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        response = self.client.get('/productions/%d/delete_screenshot/%d/' % (self.pondlife.id, self.pondlife_screenshot.id))
        self.assertRedirects(response, '/productions/%d/' % self.pondlife.id)

    def test_get_production(self):
        response = self.client.get('/productions/%d/delete_screenshot/%d/' % (self.pondlife.id, self.pondlife_screenshot.id))
        self.assertEqual(response.status_code, 200)

    def test_redirect_production(self):
        response = self.client.get('/productions/%d/delete_artwork/%d/' % (self.pondlife.id, self.pondlife_screenshot.id))
        self.assertRedirects(response, '/productions/%d/delete_screenshot/%d/' % (self.pondlife.id, self.pondlife_screenshot.id))

    def test_get_music(self):
        response = self.client.get('/productions/%d/delete_artwork/%d/' % (self.cybrev.id, self.cybrev_artwork.id))
        self.assertEqual(response.status_code, 200)

    def test_redirect_music(self):
        response = self.client.get('/productions/%d/delete_screenshot/%d/' % (self.cybrev.id, self.cybrev_artwork.id))
        self.assertRedirects(response, '/productions/%d/delete_artwork/%d/' % (self.cybrev.id, self.cybrev_artwork.id))

    def test_post_production(self):
        response = self.client.post('/productions/%d/delete_screenshot/%d/' % (self.pondlife.id, self.pondlife_screenshot.id), {
            'yes': 'yes'
        })
        self.assertRedirects(response, '/productions/%d/screenshots/edit/' % self.pondlife.id)
        self.assertEqual(self.pondlife.screenshots.count(), 0)

    def test_post_music(self):
        response = self.client.post('/productions/%d/delete_artwork/%d/' % (self.cybrev.id, self.cybrev_artwork.id), {
            'yes': 'yes'
        })
        self.assertRedirects(response, '/productions/%d/artwork/edit/' % self.cybrev.id)
        self.assertEqual(self.cybrev.screenshots.count(), 0)


class TestAddCredit(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_locked(self):
        mooncheese = Production.objects.get(title='Mooncheese')
        response = self.client.get('/productions/%d/add_credit/' % mooncheese.id)
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        pondlife = Production.objects.get(title='Pondlife')
        response = self.client.get('/productions/%d/add_credit/' % pondlife.id)
        self.assertEqual(response.status_code, 200)

    def test_get_ajax(self):
        pondlife = Production.objects.get(title='Pondlife')
        response = self.client.get(
            '/productions/%d/add_credit/' % pondlife.id, HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        pondlife = Production.objects.get(title='Pondlife')
        yerz = Nick.objects.get(name='Yerzmyey')

        response = self.client.post('/productions/%d/add_credit/' % pondlife.id, {
            'nick_search': 'yerzmyey',
            'nick_match_id': yerz.id,
            'nick_match_name': 'yerzmyey',
            'credit-TOTAL_FORMS': 1,
            'credit-INITIAL_FORMS': 0,
            'credit-MIN_NUM_FORMS': 0,
            'credit-MAX_NUM_FORMS': 1000,
            'credit-0-id': '',
            'credit-0-category': 'Music',
            'credit-0-role': 'Part 2',
        })
        self.assertRedirects(response, '/productions/%d/?editing=credits#credits_panel' % pondlife.id)
        self.assertEqual(1, pondlife.credits.filter(nick=yerz).count())


class TestEditCredit(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.pondlife = Production.objects.get(title='Pondlife')
        self.gasman = Nick.objects.get(name='Gasman')
        self.pondlife_credit = self.pondlife.credits.get(nick=self.gasman)

    def test_locked(self):
        mooncheese = Production.objects.get(title='Mooncheese')
        mooncheese_credit = mooncheese.credits.create(nick=Nick.objects.get(name='Shingebis'), category='Code')
        response = self.client.get('/productions/%d/edit_credit/%d/' % (mooncheese.id, mooncheese_credit.id))
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        response = self.client.get(
            '/productions/%d/edit_credit/%d/' % (self.pondlife.id, self.pondlife_credit.id)
        )
        self.assertEqual(response.status_code, 200)

    def test_get_ajax(self):
        response = self.client.get(
            '/productions/%d/edit_credit/%d/' % (self.pondlife.id, self.pondlife_credit.id),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        pondlife = Production.objects.get(title='Pondlife')

        response = self.client.post(
            '/productions/%d/edit_credit/%d/' % (self.pondlife.id, self.pondlife_credit.id),
            {
                'nick_search': 'gasman',
                'nick_match_id': self.gasman.id,
                'nick_match_name': 'gasman',
                'credit-TOTAL_FORMS': 2,
                'credit-INITIAL_FORMS': 1,
                'credit-MIN_NUM_FORMS': 0,
                'credit-MAX_NUM_FORMS': 1000,
                'credit-0-id': self.pondlife_credit.id,
                'credit-0-category': 'Code',
                'credit-0-role': '',
                'credit-0-DELETE': 'credit-0-DELETE',
                'credit-1-id': '',
                'credit-1-category': 'Music',
                'credit-1-role': 'Part 1',
            }
        )
        self.assertRedirects(response, '/productions/%d/?editing=credits#credits_panel' % self.pondlife.id)
        self.assertEqual('Music', pondlife.credits.get(nick=self.gasman).category)


class TestDeleteCredit(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.pondlife = Production.objects.get(title='Pondlife')
        self.gasman = Nick.objects.get(name='Gasman')
        self.pondlife_credit = self.pondlife.credits.get(nick=self.gasman)

    def test_locked(self):
        mooncheese = Production.objects.get(title='Mooncheese')
        mooncheese_credit = mooncheese.credits.create(nick=Nick.objects.get(name='Shingebis'), category='Code')
        response = self.client.get('/productions/%d/delete_credit/%d/' % (mooncheese.id, mooncheese_credit.id))
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        response = self.client.get(
            '/productions/%d/delete_credit/%d/' % (self.pondlife.id, self.pondlife_credit.id)
        )
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post('/productions/%d/delete_credit/%d/' % (self.pondlife.id, self.pondlife_credit.id), {
            'yes': 'yes'
        })
        self.assertRedirects(response, '/productions/%d/?editing=credits#credits_panel' % self.pondlife.id)
        self.assertEqual(self.pondlife.credits.count(), 0)


class TestEditSoundtracks(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.pondlife = Production.objects.get(title='Pondlife')

    def test_locked(self):
        mooncheese = Production.objects.get(title='Mooncheese')
        response = self.client.get('/productions/%d/edit_soundtracks/' % mooncheese.id)
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        response = self.client.get('/productions/%d/edit_soundtracks/' % self.pondlife.id)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        soundtrack_link = self.pondlife.soundtrack_links.get()
        response = self.client.post('/productions/%d/edit_soundtracks/' % self.pondlife.id, {
            'form-TOTAL_FORMS': 3,
            'form-INITIAL_FORMS': 1,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-0-ORDER': 1,
            'form-0-id': soundtrack_link.id,
            'form-0-soundtrack_id': soundtrack_link.soundtrack_id,
            'form-0-DELETE': 'form-0-DELETE',
            'form-1-ORDER': 2,
            'form-1-id': '',
            'form-1-soundtrack_id': '',
            'form-1-soundtrack_title': 'Fantasia',
            'form-1-soundtrack_byline_search': '',
            'form-2-ORDER': 3,
            'form-2-id': '',
            'form-2-soundtrack_id': '',
            'form-2-soundtrack_title': '',
            'form-2-soundtrack_byline_search': '',
            'form-2-DELETE': 'form-2-DELETE',
        })
        self.assertRedirects(response, '/productions/%d/' % self.pondlife.id)
        self.assertEqual(self.pondlife.soundtrack_links.count(), 1)
        self.assertEqual(self.pondlife.soundtrack_links.first().soundtrack.title, 'Fantasia')


class TestEditPackContents(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.pondlife = Production.objects.get(title='Pondlife')
        self.pondlife.types.add(ProductionType.objects.get(name='Pack'))
        self.madrielle = self.pondlife.pack_members.create(member=Production.objects.get(title='Madrielle'), position=1)

        self.mooncheese = Production.objects.get(title='Mooncheese')
        self.mooncheese.types.add(ProductionType.objects.get(name='Pack'))

    def test_locked(self):
        mooncheese = Production.objects.get(title='Mooncheese')
        response = self.client.get('/productions/%d/edit_pack_contents/' % mooncheese.id)
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        response = self.client.get('/productions/%d/edit_pack_contents/' % self.pondlife.id)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post('/productions/%d/edit_pack_contents/' % self.pondlife.id, {
            'form-TOTAL_FORMS': 3,
            'form-INITIAL_FORMS': 1,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-0-ORDER': 1,
            'form-0-id': self.madrielle.id,
            'form-0-member_id': self.madrielle.member_id,
            'form-0-DELETE': 'form-0-DELETE',
            'form-1-ORDER': 2,
            'form-1-id': '',
            'form-1-member_id': '',
            'form-1-member_title': 'Froob',
            'form-1-member_byline_search': '',
            'form-2-ORDER': 3,
            'form-2-id': '',
            'form-2-member_id': '',
            'form-2-member_title': '',
            'form-2-member_byline_search': '',
            'form-2-DELETE': 'form-2-DELETE',
        })
        self.assertRedirects(response, '/productions/%d/' % self.pondlife.id)
        self.assertEqual(self.pondlife.pack_members.count(), 1)
        self.assertEqual(self.pondlife.pack_members.first().member.title, 'Froob')