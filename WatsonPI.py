#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import os
import json
from google.appengine.ext.webapp import template
from google.appengine.ext import vendor
# Add any libraries install in the "lib" folder.
vendor.add(os.path.join(os.path.dirname(os.path.realpath(__file__)),'lib'))

# third party libraries
from urllib3 import PoolManager
from urllib3.contrib.appengine import AppEngineManager, is_appengine_sandbox

if is_appengine_sandbox():
    # AppEngineManager uses AppEngine's URLFetch API behind the scenes
    http = AppEngineManager()
else:
    # PoolManager uses a socket-level API behind the scenes
    http = PoolManager()

import requests_toolbelt.adapters.appengine
from watson_developer_cloud import PersonalityInsightsV3
from watson_developer_cloud import WatsonApiException

requests_toolbelt.adapters.appengine.monkeypatch()

PAGES = {
    'home':'/',
    'results':'/results',
}

class MainPage(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'template')
        form_values = {'url':PAGES['results']}
        template_values = {
            'content':template.render(os.path.join(path,'form.html'),form_values),
            'title':'Watson PI',
        }
        html = template.render(os.path.join(path,'base.html'), template_values)
        return webapp2.Response(html)

class ResultsPage(webapp2.RequestHandler):
    def get(self):
        personality_insights = PersonalityInsightsV3(
                version='2017-10-13',
                username= os.environ.get("WATSON_USERNAME"),
                password= os.environ.get("WATSON_PASSWORD"),
                url='https://gateway.watsonplatform.net/personality-insights/api'
            )
        try:
            self.profile = personality_insights.profile(
                    content = self.request.get('text').encode('utf-8'),
                    content_type='text/plain',
                    accept='application/json',
                    content_language='ja',
                    consumption_preferences=True,
                    raw_scores=True
                ).get_result()
        except WatsonApiException as ex:
            print "Method failed with status code " + str(ex.code) + ": " + ex.message

        path = os.path.join(os.path.dirname(__file__), 'template')
        form_values = {
            'url':PAGES['results'],
            'word_count':self.profile['word_count'],
            'openness'              :{'label':u"開放性",'value': 0},
            'conscientiousness'     :{'label':u"誠実性",'value': 0},
            'extraversion'          :{'label':u"外交性",'value': 0},
            'agreeableness'         :{'label':u"協調性",'value': 0},
            'neuroticism'          :{'label':u"情緒不安定性",'value': 0},
            'adventurousness'       :{'label':u"冒険的",'value': 0},
            'artistic_interests'   :{'label':u"芸術的",'value': 0},
            'emotionality'          :{'label':u"情緒的",'value': 0},
            'imagination'           :{'label':u"想像的",'value': 0},
            'intellect'             :{'label':u"知的",'value': 0},
            'liberalism'            :{'label':u"保守的",'value': 0},
            'achievement_striving'   :{'label':u"達成努力",'value': 0},
            'cautiousness'          :{'label':u"注意深さ",'value': 0},
            'dutifulness'           :{'label':u"忠実性",'value': 0},
            'orderliness'           :{'label':u"規律性",'value': 0},
            'self_discipline'       :{'label':u"自制性",'value': 0},
            'self_efficacy'         :{'label':u"自己効力感",'value': 0},
            'activity_level'          :{'label':u"活性レベル",'value': 0},
            'assertiveness'         :{'label':u"積極性",'value': 0},
            'cheerfulness'          :{'label':u"快活性",'value': 0},
            'excitement_seeking'    :{'label':u"興奮性",'value': 0},
            'friendliness'          :{'label':u"好意性",'value': 0},
            'gregariousness'        :{'label':u"社交性",'value': 0},
            'altruism'              :{'label':u"利他主義",'value': 0},
            'cooperation'           :{'label':u"連携性",'value': 0},
            'modesty'               :{'label':u"謙虚性",'value': 0},
            'morality'              :{'label':u"倫理性",'value': 0},
            'sympathy'              :{'label':u"共感性",'value': 0},
            'trust'                 :{'label':u"他者信頼性",'value': 0},
            'anger'                 :{'label':u"怒り",'value': 0},
            'anxiety'               :{'label':u"不安",'value': 0},
            'depression'            :{'label':u"鬱",'value': 0},
            'immoderation'          :{'label':u"過敏性",'value': 0},
            'self_consciousness'    :{'label':u"自意識過剰性",'value': 0},
            'vulnerability'         :{'label':u"脆弱性",'value': 0},
            'liberty'               :{'label':u"自由",'value': 0},
            'ideal'                 :{'label':u"理想",'value': 0},
            'love'                  :{'label':u"愛情",'value': 0},
            'practicality'          :{'label':u"実用的",'value': 0},
            'self_expression'       :{'label':u"自己表現",'value': 0},
            'stability'             :{'label':u"安定",'value': 0},
            'structure'             :{'label':u"組織",'value': 0},
            'challenge'             :{'label':u"挑戦",'value': 0},
            'closeness'             :{'label':u"接近",'value': 0},
            'curiosity'             :{'label':u"好奇心",'value': 0},
            'excitement'            :{'label':u"興奮",'value': 0},
            'harmony'               :{'label':u"調和",'value': 0},
            'conservation'          :{'label':u"現状維持",'value': 0},
            'hedonism'              :{'label':u"快楽",'value': 0},
            'openness_to_change'    :{'label':u"変化しやすさ",'value': 0},
            'self_enhancement'      :{'label':u"自己増強",'value': 0},
            'self_transcendence'    :{'label':u"自己超越",'value': 0},
        }

        for bigf in self.profile['personality']:
            if bigf['trait_id'] == u'big5_openness':
                form_values['openness']['value'] = bigf['percentile'] * 100
                for opn in bigf['children']:
                    if opn['trait_id'] == u'facet_adventurousness':form_values['adventurousness']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_artistic_interests':form_values['artistic_interests']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_emotionality':form_values['emotionality']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_imagination':form_values['imagination']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_intellect':form_values['intellect']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_liberalism':form_values['liberalism']['value'] = opn['percentile'] * 100
            if bigf['trait_id'] == u'big5_conscientiousness':
                form_values['conscientiousness']['value'] = bigf['percentile'] * 100
                for cns in bigf['children']:
                    if cns['trait_id'] == u'facet_achievement_striving':form_values['achievement_striving']['value'] = cns['percentile'] * 100
                    if cns['trait_id'] == u'facet_cautiousness':form_values['cautiousness']['value'] = cns['percentile'] * 100
                    if cns['trait_id'] == u'facet_dutifulness':form_values['dutifulness']['value'] = cns['percentile'] * 100
                    if cns['trait_id'] == u'facet_orderliness':form_values['orderliness']['value'] = cns['percentile'] * 100
                    if cns['trait_id'] == u'facet_self_discipline':form_values['self_discipline']['value'] = cns['percentile'] * 100
                    if cns['trait_id'] == u'facet_self_efficacy':form_values['self_efficacy']['value'] = cns['percentile'] * 100
            if bigf['trait_id'] == u'big5_extraversion':
                form_values['extraversion']['value'] = bigf['percentile'] * 100
                for opn in bigf['children']:
                    if opn['trait_id'] == u'facet_activity_level':form_values['activity_level']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_assertiveness':form_values['assertiveness']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_cheerfulness':form_values['cheerfulness']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_excitement_seeking':form_values['excitement_seeking']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_friendliness':form_values['friendliness']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_gregariousness':form_values['gregariousness']['value'] = opn['percentile'] * 100
            if bigf['trait_id'] == u'big5_agreeableness':
                form_values['agreeableness']['value'] = bigf['percentile'] * 100
                for opn in bigf['children']:
                    if opn['trait_id'] == u'facet_altruism':form_values['altruism']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_cooperation':form_values['cooperation']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_modesty':form_values['modesty']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_morality':form_values['morality']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_sympathy':form_values['sympathy']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_trust':form_values['trust']['value'] = opn['percentile'] * 100
            if bigf['trait_id'] == u'big5_neuroticism':
                form_values['neuroticism']['value'] = bigf['percentile'] * 100
                for opn in bigf['children']:
                    if opn['trait_id'] == u'facet_anger':form_values['anger']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_anxiety':form_values['anxiety']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_depression':form_values['depression']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_immoderation':form_values['immoderation']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_self_consciousness':form_values['self_consciousness']['value'] = opn['percentile'] * 100
                    if opn['trait_id'] == u'facet_vulnerability':form_values['vulnerability']['value'] = opn['percentile'] * 100
        for need in self.profile['needs']:
            if need['trait_id'] == u'need_challenge': form_values['challenge']['value'] = need['percentile'] * 100
            if need['trait_id'] == u'need_closeness': form_values['closeness']['value'] = need['percentile'] * 100
            if need['trait_id'] == u'need_curiosity': form_values['curiosity']['value'] = need['percentile'] * 100
            if need['trait_id'] == u'need_excitement': form_values['excitement']['value'] = need['percentile'] * 100
            if need['trait_id'] == u'need_harmony': form_values['harmony']['value'] = need['percentile'] * 100
            if need['trait_id'] == u'need_ideal': form_values['ideal']['value'] = need['percentile'] * 100
            if need['trait_id'] == u'need_liberty': form_values['liberty']['value'] = need['percentile'] * 100
            if need['trait_id'] == u'need_love': form_values['love']['value'] = need['percentile'] * 100
            if need['trait_id'] == u'need_practicality': form_values['practicality']['value'] = need['percentile'] * 100
            if need['trait_id'] == u'need_self_expression': form_values['self_expression']['value'] = need['percentile'] * 100
            if need['trait_id'] == u'need_stability': form_values['stability']['value'] = need['percentile'] * 100
            if need['trait_id'] == u'need_structure': form_values['structure']['value'] = need['percentile'] * 100
        for value in self.profile['values']:
            if value['trait_id'] == u'value_conservation': form_values['conservation']['value'] = need['percentile'] * 100
            if value['trait_id'] == u'value_openness_to_change': form_values['openness_to_change']['value'] = need['percentile'] * 100
            if value['trait_id'] == u'value_hedonism': form_values['hedonism']['value'] = need['percentile'] * 100
            if value['trait_id'] == u'value_self_enhancement': form_values['self_enhancement']['value'] = need['percentile'] * 100
            if value['trait_id'] == u'value_self_transcendence': form_values['self_transcendence']['value'] = need['percentile'] * 100
        template_values = {
            'content':template.render(os.path.join(path,'results.html'),form_values),
            'title':'Watson PI result',
        }
        html = template.render(os.path.join(path,'base.html'), template_values)
        return webapp2.Response(html)


app = webapp2.WSGIApplication([
    (PAGES['home'], MainPage),
    (PAGES['results'], ResultsPage),
], debug=False)
