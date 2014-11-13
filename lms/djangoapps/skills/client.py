import json
import os.path
from random import random
from collections import namedtuple

import loremipsum
import requests

from student.models import anonymous_id_for_user


Skill = namedtuple('skill', 'id description')

SkillValue = namedtuple('skill_value', 'description value')


class BaseClient(object):
    def __init__(self, course):
        self.course = course

    def get_skills(self):
        raise NotImplementedError()

    def get_skill_probability(self, user, skill):
        raise NotImplementedError()

    def get_skill_values(self, user):
        results = []
        for skill in self.get_skills():
            p = self.get_skill_probability(user, skill)
            value = self.map_probablitity(p)
            result = SkillValue(description=skill.description, value=value)
            results.append(result)

        return results

    def map_probablitity(self, p):
        if p < 0.1:
            value = 'Unknown'
        elif p < 0.3:
            value = 'Low'
        elif p < 0.8:
            value = 'Medium'
        else:
            value = 'High'
        return value

class DummyClient(BaseClient):
    def get_skills(self):
        skills = []
        for i in range(10):
            description = ' '.join(loremipsum.get_sentences(3))
            skill = Skill(id=i, description=description)
            skills.append(skill)
        return skills

    def get_skill_probability(self, user, skill):
        return random()


class OLIClient(BaseClient):
    def get_endpoint_url(self, enpoint):
        return os.path.join(self.course.oli_analytics_service_url, enpoint)

    def get_skill_values(self, user):
        skills = self.get_skills()

        user_id = anonymous_id_for_user(user, None)
        endpoint = 'student/{}'.format(user_id)
        values = {r['skill_id']:r['p_learned']  for r in self.request(endpoint)}

        results = []
        for skill in skills:
            value = self.map_probablitity(values.get(skill.id, 0))
            result = SkillValue(description=skill.description, value=value)
            results.append(result)

        return results

    def get_skills(self):
        data = self.request('skills')

        results = []
        for entry in data:
            skill = Skill(id=entry['skill_id'], description=entry['skill_desc'])
            results.append(skill)
        return results

    def request(self, endpoint):
        headers = {
            'Authorization': self.course.oli_analytics_service_secret
        }
        url = self.get_endpoint_url(endpoint)
        response = requests.get(
            url,
            headers=headers,
            timeout = self.course.oli_analytics_service_timeout
        )

        payload = json.loads(json.loads(response.text[5:]).get('payload','[]'))
        return payload


def get_skills_and_values(course, user):
    client = OLIClient(course)
    results = client.get_skill_values(user)
    return results
