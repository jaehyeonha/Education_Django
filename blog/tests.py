from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_ha = User.objects.create_user(username='ha', password = 'pass4321')

        self.category_movie = Category.objects.create(name='movie',slug='movie')

        self.post_001 = Post.objects.create(
            title='첫번째 포스트입니다.',
            content='category가 없을 수도 있죠',
            author=self.user_ha
        )

        self.post_002 = Post.objects.create(
            title='두번째 포스트입니다.',
            content='Hello World. We are the world.',
            category=self.category_movie,
            author=self.user_ha
        )

    
    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(
            f'{self.category_movie.name} ({self.category_movie.post_set.count()})',
            categories_card.text
        )
        self.assertIn(f'미분류 (1)', categories_card.text)

    def navbar_test(self,soup):
        navbar = soup.nav
        self.assertIn('Blog',navbar.text)
        self.assertIn('About me',navbar.text) 
        
        logo_btn = navbar.find('a', text='Get It')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def test_post_list(self):

        self.assertEqual(Post.objects.count(),2)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card=main_area.find('div',id='post-1')
        self.assertIn('미분류', post_001_card.text)
        self.assertIn(self.post_001.title, post_001_card.text)

        post_002_card=main_area.find('div',id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)

        self.assertIn(self.user_ha.username.upper(),main_area.text)


        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(),0)
        response = self.client.get('/blog/')
        soup=BeautifulSoup(response.content,'html.parser')
        main_area = soup.find('div',id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):
    
        self.assertEqual(self.post_002.get_absolute_url(), '/blog/2/')

        response = self.client.get(self.post_002.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.post_002.title, soup.title.text)

        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_002.title, post_area.text)
        self.assertIn(self.category_movie.name, post_area.text)

        self.assertIn(self.user_ha.username.upper(),post_area.text)

        self.assertIn(self.post_002.content, post_area.text)


    def test_category_page(self):
        response = self.client.get(self.category_movie.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_movie.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_movie.name, main_area.text)
        self.assertIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_001.title, main_area.text)
        
        