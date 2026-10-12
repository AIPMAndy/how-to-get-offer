import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build import build, md_to_html

class Links(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.scripts=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='a' and 'href' in d:self.links.append(d['href'])
        if tag=='script' and 'src' in d:self.scripts.append(d['src'])

class Integrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.count=build()
        cls.tasks=json.loads((ROOT/'data/tasks.json').read_text('utf-8'))
        cls.html=(ROOT/'index.html').read_text('utf-8')

    def test_100_actionable_tasks(self):
        self.assertEqual(self.count,100)
        self.assertEqual(len({x['id'] for x in self.tasks}),100)
        self.assertEqual({x['stage'] for x in self.tasks},{'定位','简历','渠道','面试','Offer','入职'})
        for x in self.tasks:
            for k in ('title','do','done','stuck'):
                self.assertGreaterEqual(len(x[k]),4 if k=='title' else 6,(x['id'],k))

    def test_no_broken_local_site_links(self):
        files=[ROOT/'index.html']+list(ROOT.glob('guides/*.html'))+list(ROOT.glob('playbooks/*.html'))+list(ROOT.glob('templates/*.html'))+list(ROOT.glob('examples/*.html'))
        self.assertGreaterEqual(len(files),25)
        for path in files:
            parser=Links();parser.feed(path.read_text('utf-8'))
            for link in parser.links:
                if link.startswith(('https://','http://','#','mailto:')):continue
                dest=link.split('#')[0]
                self.assertTrue((path.parent/dest).is_file(),(path,link))
            self.assertFalse(parser.scripts,(path,parser.scripts))

    def test_static_single_file_and_escaping(self):
        self.assertIn('const TASKS =',self.html)
        self.assertIn('社招拿 Offer',self.html)
        self.assertIn('id="salaryResults"',self.html)
        self.assertIn('id="taskList"',self.html)
        self.assertIn('id="jobRows"',self.html)
        self.assertNotIn('<script src=',self.html)
        self.assertNotIn('fetch(', (ROOT/'assets/app.js').read_text('utf-8').replace('never calls fetch',''))
        self.assertNotIn('innerHTML',(ROOT/'assets/app.js').read_text('utf-8'))

    def test_every_markdown_has_reader(self):
        for kind in ['guides','playbooks','templates','examples']:
            for md in (ROOT/kind).glob('*.md'):
                self.assertTrue(md.with_suffix('.html').exists(),md)

    def test_critical_docs_and_guardrails(self):
        for item in ['guides/07-positioning-lab.md', 'guides/08-resume-workshop.md',
                     'guides/10-interview-answer-bank.md', 'playbooks/09-background-check.md',
                     'playbooks/11-offer-withdrawn.md', 'audit/ADVERSARIAL_REVIEW.md']:
            text=(ROOT/item).read_text('utf-8')
            self.assertGreater(len(text),800,(item,len(text)))
        self.assertIn('100 ACTIONS', self.html)
        self.assertNotIn('56项', self.html)
        self.assertIn('个人信息保护法', (ROOT/'SOURCES.md').read_text('utf-8'))

    def test_bad_url_blocked_by_renderer(self):
        self.assertNotIn('href="javascript:',md_to_html('[bad](javascript:alert(1))'))

    def test_readme_links_markdown_sources(self):
        readme=(ROOT/'README.md').read_text('utf-8')
        self.assertIn('AI 酋长 Andy',readme)
        self.assertIn('免费',readme)
        self.assertIn('微信',readme)
        self.assertIn('https://job.mohrss.gov.cn/',readme)
        self.assertIn('不承诺录用、涨薪或内推结果',readme)

if __name__=='__main__':unittest.main()
