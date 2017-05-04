# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re
import copy


import mistune

from .utils.emoji import emojis

_linebreak = re.compile(r'^ *\n(?!\s*$)')
_text = re.compile(
    r'^[\s\S]+?(?=[\\<!\[_*`:@~]|https?://| *\n|$)'
)


class InlineGrammar(mistune.InlineGrammar):

    # todo: match unicode emojis
    emoji = re.compile(
        r'^:(?P<emoji>[A-Za-z0-9_\-\+]+?):'
    )

    mention = re.compile(
        r'^@(?P<username>[\w.@+-]+)',
        flags=re.UNICODE
    )

    # Override
    def hard_wrap(self):
        # Adds ":" and "@" as an invalid text character, so we can match emojis and mentions.
        self.linebreak = _linebreak
        self.text = _text


class InlineLexer(mistune.InlineLexer):

    default_rules = copy.copy(mistune.InlineLexer.default_rules)
    default_rules.insert(2, 'emoji')
    default_rules.insert(2, 'mention')

    def __init__(self, renderer, rules=None, **kwargs):
        rules = InlineGrammar()
        rules.hard_wrap()

        super(InlineLexer, self).__init__(renderer, rules, **kwargs)

        self.mentions = {}
        self._mention_count = 0

    def output_emoji(self, m):
        emoji = m.group('emoji')

        if emoji not in emojis:
            return m.group(0)

        name_raw = emoji
        name_class = emoji.replace('_', '-').replace('+', 'plus')
        return self.renderer.emoji(name_class=name_class, name_raw=name_raw)
    
    # remove def output_mention
    # def output_mention(self, m):
   