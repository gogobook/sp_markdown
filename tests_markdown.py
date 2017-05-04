# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.test.utils import override_settings
from django.utils import translation
from django.utils import timezone

import utils
from sp_markdown import Markdown, quotify
from django.conf import settings
import base

now_fixed = timezone.now()


class UtilsMarkdownTests(TestCase):
  
    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user(username="nitely")
        # self.user2 = utils.create_user(username="esteban")
        # self.user3 = utils.create_user(username="áéíóú")

    def test_markdown_escape(self):
        """
        Should escape html
        """
        comment = "<span>foo</span>"
        comment_md = Markdown().render(comment)
        self.assertEqual(comment_md, '<p>&lt;span&gt;foo&lt;/span&gt;</p>')

    def test_markdown_html(self):
        """
        Should escape html
        """
        # todo: fixed on mistune 0.7.2 ?
        # markdown is not parsed within html tags, there is a way to parse it
        # but it's broken since it gets escaped afterwards.
        comment = (
            "<div>\n"
            "<em>*foo*</em>\n"
            "<em>*bar*</em>\n"
            "*foobar*\n"
            "@nitely\n"
            "*<em>foobar</em>*\n"
            "</div>\n"
            "<em>*foo*</em>\n"
         #  "<em>@nitely</em>\n"  # Why this gets parsed properly is beyond me
            "*<em>foobar</em>*\n"
        )
        comment_md = Markdown().render(comment)
        self.assertEqual(comment_md, (
            '<p>&lt;div&gt;\n'
            '&lt;em&gt;*foo*&lt;/em&gt;\n'
            '&lt;em&gt;*bar*&lt;/em&gt;\n'
            '*foobar*\n'
            '@nitely\n'
            '*&lt;em&gt;foobar&lt;/em&gt;*\n'
            '&lt;/div&gt;<br>\n'
            '&lt;em&gt;*foo*&lt;/em&gt;<br>\n'
            # '&lt;em&gt;<a class="comment-mention" rel="nofollow" href="%s">@nitely</a>&lt;/em&gt;<br>\n'
            '<em>&lt;em&gt;foobar&lt;/em&gt;</em></p>'
        ) )

    # def test_markdown_mentions(self):
    #     """
    #     markdown mentions
    #     """
    #     comment = "@nitely, @esteban,@áéíóú, @fakeone"
    #     comment_md = Markdown().render(comment)
    #     self.assertEqual(comment_md, '<p><a class="comment-mention" rel="nofollow" href="%s">@nitely</a>, '
    #                                  '<a class="comment-mention" rel="nofollow" href="%s">@esteban</a>,'
    #                                  '<a class="comment-mention" rel="nofollow" href="%s">@áéíóú</a>, '
    #                                  '@fakeone</p>' %
    #                                  (self.user.st.get_absolute_url(),
    #                                   self.user2.st.get_absolute_url(),
    #                                   self.user3.st.get_absolute_url()))

    # @override_settings(ST_MENTIONS_PER_COMMENT=2)
    # def test_markdown_mentions_limit(self):
    #     """
    #     markdown mentions limit
    #     """
    #     comment = "@a, @b, @nitely"
    #     comment_md = Markdown().render(comment)
    #     self.assertEqual(comment_md, "<p>@a, @b, @nitely</p>")

    # def test_markdown_mentions_dict(self):
    #     """
    #     markdown mentions dict
    #     """
    #     comment = "@nitely, @esteban"
    #     md = Markdown()
    #     md.render(comment)
    #     # mentions get dynamically added on MentionifyExtension
    #     self.assertDictEqual(md.get_mentions(), {'nitely': self.user,
    #                                              'esteban': self.user2})

    def test_markdown_emoji(self):
        """
        markdown emojify
        """
        comment = ":airplane:, :8ball: :+1: :bademoji: foo:"
        comment_md = Markdown().render(comment)
        self.assertEqual(comment_md, '<p><i class="tw tw-airplane" title=":airplane:"></i>, '
                                     '<i class="tw tw-8ball" title=":8ball:"></i> '
                                     '<i class="tw tw-plus1" title=":+1:"></i> '
                                     ':bademoji: foo:</p>')

    @override_settings(LANGUAGE_CODE='en')
    def test_markdown_quote(self):
        """
        markdown quote
        """
        comment = "text\nnew line"
        quote = quotify(comment, self.user)
        self.assertListEqual(quote.splitlines(), ("> @%s said:\n> text\n> new line\n\n" % self.user.username).splitlines())

    @override_settings(LANGUAGE_CODE='en')
    def test_markdown_quote_header_language(self):
        """
        markdown quote
        "@user said:" should keep the default language (settings.LANGUAGE_CODE)
        """
        comment = ""
        quote = quotify(comment, self.user)

        with translation.override('es'):
            self.assertListEqual(quote.splitlines(), ("> @%s said:\n> \n\n" % self.user.username).splitlines())

    @override_settings(LANGUAGE_CODE='en')
    def test_markdown_quote_no_polls(self):
        """
        should remove poll markdown
        """
        comment = "foo\n" \
                  "[poll param=value]\n" \
                  "1. [/fake_closing_tag]\n" \
                  "2. opt 2\n" \
                  "[/poll]\n" \
                  "bar\n" \
                  "[poll param=value]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "[/poll]"
        quote = quotify(comment, self.user)
        self.assertListEqual(quote.splitlines(), ("> @%s said:\n> foo\n> \n> bar\n\n" % self.user.username).splitlines())

    def test_markdown_image(self):
        """
        markdown image
        """
        comment = (
            "http://foo.bar/image.png\n"
            "http://www.foo.bar.fb/path/image.png\n"
            "https://foo.bar/image.png\n"
            "bad http://foo.bar/image.png\n"
            "http://foo.bar/image.png bad\nhttp://bad.png\n"
            "http://foo.bar/.png\n"
            "![im](http://foo.bar/not_imagified.png)\n"
            "foo.bar/bad.png\n\n"
            "http://foo.bar/<escaped>.png"
        )
        comment_md = Markdown().render(comment)
        self.assertListEqual(
            comment_md.splitlines(),
            [
                '<p><img src="http://foo.bar/image.png" alt="image" title="image"></p>',
                '<p><img src="http://www.foo.bar.fb/path/image.png" alt="image" title="image"></p>',
                '<p><img src="https://foo.bar/image.png" alt="image" title="image"></p>',

                # auto-link
                '<p>bad <a rel="nofollow" href="http://foo.bar/image.png">http://foo.bar/image.png</a><br>',
                '<a rel="nofollow" href="http://foo.bar/image.png">http://foo.bar/image.png</a> bad<br>',
                '<a rel="nofollow" href="http://bad.png">http://bad.png</a><br>',
                '<a rel="nofollow" href="http://foo.bar/.png">http://foo.bar/.png</a><br>',
                '<img src="http://foo.bar/not_imagified.png" alt="im"><br>',
                'foo.bar/bad.png</p>',

                '<p><img src="http://foo.bar/&lt;escaped&gt;.png" alt="&lt;escaped&gt;" title="&lt;escaped&gt;"></p>'
            ]
        )

    def test_markdown_youtube(self):
        """
        markdown youtube
        """
        comment = (
            "https://www.youtube.com/watch?v=Z0UISCEe52Y\n"
            "https://www.youtube.com/watch?v=Z0UISCEe52Y&t=1m13s\n"
            "https://www.youtube.com/watch?v=O1QQajfobPw&t=1h1m38s\n"
            "https://www.youtube.com/watch?v=O1QQajfobPw&t=105m\n"
            "https://www.youtube.com/watch?v=O1QQajfobPw&feature=youtu.be&t=3698\n"
            "http://youtu.be/afyK1HSFfgw\n"
            "http://youtu.be/O1QQajfobPw?t=1h1m38s\n"
            "https://www.youtube.com/embed/vsF0K3Ou1v0\n"
            "https://www.youtube.com/watch?v=<bad>\n"
            "https://www.noyoutube.com/watch?v=Z0UISCEe52Y\n"
            "badbad https://www.youtube.com/watch?v=Z0UISCEe52Y\n\n"
            "https://www.youtube.com/watch?v=Z0UISCEe52Y badbad\n"
        )
        comment_md = Markdown().render(comment)
        self.assertListEqual(
            comment_md.splitlines(),
            [
                '<span class="video"><iframe src="https://www.youtube.com/embed/Z0UISCEe52Y?html5=1" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://www.youtube.com/embed/Z0UISCEe52Y?html5=1&start=73" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://www.youtube.com/embed/O1QQajfobPw?html5=1&start=3698" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://www.youtube.com/embed/O1QQajfobPw?html5=1&start=6300" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://www.youtube.com/embed/O1QQajfobPw?html5=1&start=3698" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://www.youtube.com/embed/afyK1HSFfgw?html5=1"'
                ' allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://www.youtube.com/embed/O1QQajfobPw?html5=1&start=3698" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://www.youtube.com/embed/vsF0K3Ou1v0?html5=1"'
                ' allowfullscreen></iframe></span>',
                '<p><a rel="nofollow" href="https://www.youtube.com/watch?v=&lt;bad&gt;">'
                'https://www.youtube.com/watch?v=&lt;bad&gt;</a></p>',
                '<p><a rel="nofollow" href="https://www.noyoutube.com/watch?v=Z0UISCEe52Y">'
                'https://www.noyoutube.com/watch?v=Z0UISCEe52Y</a></p>',
                '<p>badbad <a rel="nofollow" href="https://www.youtube.com/watch?v=Z0UISCEe52Y">'
                'https://www.youtube.com/watch?v=Z0UISCEe52Y</a></p>',
                '<p><a rel="nofollow" href="https://www.youtube.com/watch?v=Z0UISCEe52Y">'
                'https://www.youtube.com/watch?v=Z0UISCEe52Y</a> badbad</p>'
            ]
        )

    def test_markdown_vimeo(self):
        """
        markdown vimeo
        """
        comment = (
            "https://vimeo.com/11111111\n"
            "https://www.vimeo.com/11111111\n"
            "https://player.vimeo.com/video/11111111\n"
            "https://vimeo.com/channels/11111111\n"
            "https://vimeo.com/groups/name/videos/11111111\n"
            "https://vimeo.com/album/2222222/video/11111111\n"
            "https://vimeo.com/11111111?param=value\n"
            "https://novimeo.com/11111111\n"
            "bad https://novimeo.com/11111111\n\n"
            "https://novimeo.com/11111111 bad"
        )
        comment_md = Markdown().render(comment)
        self.assertListEqual(
            comment_md.splitlines(),
            [
                '<span class="video"><iframe src="https://player.vimeo.com/video/11111111" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://player.vimeo.com/video/11111111" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://player.vimeo.com/video/11111111" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://player.vimeo.com/video/11111111" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://player.vimeo.com/video/11111111" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://player.vimeo.com/video/11111111" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://player.vimeo.com/video/11111111" '
                'allowfullscreen></iframe></span>',

                '<p><a rel="nofollow" href="https://novimeo.com/11111111">https://novimeo.com/11111111</a></p>',
                '<p>bad <a rel="nofollow" href="https://novimeo.com/11111111">https://novimeo.com/11111111</a></p>',
                '<p><a rel="nofollow" href="https://novimeo.com/11111111">https://novimeo.com/11111111</a> bad</p>'
            ]
        )

    def test_markdown_gfycat(self):
        """
        markdown vimeo
        """
        comment = (
            "https://gfycat.com/PointedVengefulHyracotherium\n"
            "https://www.gfycat.com/PointedVengefulHyracotherium\n"
            "http://gfycat.com/PointedVengefulHyracotherium\n"
            "http://www.gfycat.com/PointedVengefulHyracotherium\n"
            "bad https://gfycat.com/PointedVengefulHyracotherium\n"
            "https://gfycat.com/PointedVengefulHyracotherium bad"
        )
        comment_md = Markdown().render(comment)
        self.assertListEqual(
            comment_md.splitlines(),
            [
                '<span class="video"><iframe src="https://gfycat.com/ifr/PointedVengefulHyracotherium" '
                'frameborder="0" scrolling="no" allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://gfycat.com/ifr/PointedVengefulHyracotherium" '
                'frameborder="0" scrolling="no" allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://gfycat.com/ifr/PointedVengefulHyracotherium" '
                'frameborder="0" scrolling="no" allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://gfycat.com/ifr/PointedVengefulHyracotherium" '
                'frameborder="0" scrolling="no" allowfullscreen></iframe></span>',

                '<p>bad <a rel="nofollow" href="https://gfycat.com/PointedVengefulHyracotherium">'
                'https://gfycat.com/PointedVengefulHyracotherium</a><br>',
                '<a rel="nofollow" href="https://gfycat.com/PointedVengefulHyracotherium">'
                'https://gfycat.com/PointedVengefulHyracotherium</a> bad</p>'
            ]
        )

    def test_markdown_video(self):
        """
        markdown video
        """
        comment = (
            "http://foo.bar/video.mp4\n"
            "http://foo.bar/<escaped>.mp4"
        )
        comment_md = Markdown().render(comment)
        self.assertListEqual(
            comment_md.splitlines(),
            [
                '<video controls><source src="http://foo.bar/video.mp4">'
                '<a rel="nofollow" href="http://foo.bar/video.mp4">http://foo.bar/video.mp4</a></video>',
                '<video controls><source src="http://foo.bar/&lt;escaped&gt;.mp4">'
                '<a rel="nofollow" href="http://foo.bar/&lt;escaped&gt;.mp4">'
                'http://foo.bar/&lt;escaped&gt;.mp4</a></video>'
            ]
        )

    def test_markdown_audio(self):
        """
        markdown audio
        """
        comment = (
            "http://foo.bar/audio.mp3\n"
            "http://foo.bar/<escaped>.mp3"
        )
        comment_md = Markdown().render(comment)
        self.assertListEqual(
            comment_md.splitlines(),
            [
                '<audio controls><source src="http://foo.bar/audio.mp3"><a '
                'rel="nofollow" href="http://foo.bar/audio.mp3">http://foo.bar/audio.mp3</a></audio>',
                '<audio controls><source src="http://foo.bar/&lt;escaped&gt;.mp3"><a '
                'rel="nofollow" href="http://foo.bar/&lt;escaped&gt;.mp3">'
                'http://foo.bar/&lt;escaped&gt;.mp3</a></audio>'
            ]
        )

    def test_autolink(self):
        """
        Should parse the link as <a> tag
        """
        comment = "http://foo.com\n" \
                  "http://foo.com?foo=1&bar=2\n" \
                  "http://foo.com/<bad>"
        comment_md = Markdown().render(comment)
        self.assertEqual(
            comment_md.splitlines(),
            [
                '<p><a rel="nofollow" href="http://foo.com">http://foo.com</a></p>',
                '<p><a rel="nofollow" href="http://foo.com?foo=1&amp;bar=2">http://foo.com?foo=1&amp;bar=2</a></p>',
                '<p><a rel="nofollow" href="http://foo.com/&lt;bad&gt;">http://foo.com/&lt;bad&gt;</a></p>'
            ])

    def test_autolink_without_no_follow(self):
        """
        Should parse the link as <a> tag without no-follow
        """
        comment = "http://foo.com"
        comment_md = Markdown(no_follow=False).render(comment)
        self.assertEqual(comment_md, '<p><a href="http://foo.com">http://foo.com</a></p>')

    def test_link(self):
        """
        Should parse the link as <a> tag
        """
        comment = "[link](http://foo.com)"
        comment_md = Markdown().render(comment)
        self.assertEqual(comment_md, '<p><a rel="nofollow" href="http://foo.com">link</a></p>')

    def test_link_without_no_follow(self):
        """
        Should parse the link as <a> tag without no-follow
        """
        comment = "[link](http://foo.com)"
        comment_md = Markdown(no_follow=False).render(comment)
        self.assertEqual(comment_md, '<p><a href="http://foo.com">link</a></p>')

    def test_link_title(self):
        """
        Should parse the link as <a> tag
        """
        comment = "[link](http://foo.com \"bar\")"
        comment_md = Markdown().render(comment)
        self.assertEqual(comment_md, '<p><a rel="nofollow" href="http://foo.com" title="bar">link</a></p>')

    def test_link_title_without_no_follow(self):
        """
        Should parse the link as <a> tag without no-follow
        """
        comment = "[link](http://foo.com \"bar\")"
        comment_md = Markdown(no_follow=False).render(comment)
        self.assertEqual(comment_md, '<p><a href="http://foo.com" title="bar">link</a></p>')

    def test_link_safety(self):
        """
        Should sanitize the links to avoid XSS attacks
        """
        attack_vectors = (
            # "standard" javascript pseudo protocol
            ('javascript:alert`1`', ''),
            # bypass attempt
            ('jAvAsCrIpT:alert`1`', ''),
            # javascript pseudo protocol with entities
            ('javascript&colon;alert`1`', ''),
            # javascript pseudo protocol with prefix (dangerous in Chrome)
            ('\x1Ajavascript:alert`1`', ''),
            # data-URI (dangerous in Firefox)
            ('data:text/html,<script>alert`1`</script>', ''),
            # vbscript-URI (dangerous in Internet Explorer)
            ('vbscript:msgbox', ''),
            # breaking out of the attribute
            ('"<>', ''),
        )

        for vector, expected in attack_vectors:
            # Image
            self.assertEqual(
                Markdown().render('![atk](%s)' % vector),
                '<p><img src="%s" alt="atk"></p>' % expected)
            # Link
            self.assertEqual(
                Markdown().render('[atk](%s)' % vector),
                '<p><a rel="nofollow" href="%s">atk</a></p>' % expected)
