"""Synthetic document fixtures test retrieval; they are NEVER policy authority."""
from pathlib import Path
import hashlib
import tempfile
import unittest
from unittest.mock import patch
from policy_engine import PolicyIndex, write_index, answer, classify, split_pages
from scripts.index_policies import fetch, refresh

# Deliberately fictional identifiers/text, confined to tests.
MEAL='Test-only meal subsistence passage. Duty meal expenses require circumstances to be checked. A lunch receipt alone is insufficient in this fictional fixture. '
MILES='Test-only motor mileage allowance passage. Authorised official duty travel using a private vehicle requires the relevant authorisation and evidence in this fictional fixture. '

class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)/'index.sqlite3'
        self.addCleanup(self.temp.cleanup)
        docs=[{'source_id':'JSP 752','document_id':'test-only','title':'SYNTHETIC TEST DOCUMENT — NOT POLICY','url':'https://assets.publishing.service.gov.uk/test-only.pdf','retrieved_at':'2026-01-01T00:00:00Z','sha256':hashlib.sha256(b'test').hexdigest(),'pages':['CHAPTER 99 TEST ONLY\nSECTION 98 TEST ONLY\n99.9801. '+MEAL+'\n99.9802. '+MILES]}]
        write_index(self.path,docs)
        self.index=PolicyIndex(self.path)

    def test_lunch_cannot_become_mileage_even_with_incidental_driving(self):
        for question in ['Can I claim my lunch back today?','Evening meal on exercise?','Can I claim food after driving to exercise?']:
            result=answer(question,{}, {},self.index)
            self.assertEqual(result['intent'],'meals')
            self.assertTrue(result['hits'])
            self.assertTrue(all('meal' in h['text'].lower() for h in result['hits']))
            self.assertNotIn('motor mileage',result['hits'][0]['text'].lower())
            self.assertTrue(result['missing'])
            self.assertEqual(result['status'],'Cannot determine entitlement')

    def test_duty_mileage_retrieves_document_passage_and_exact_locator(self):
        result=answer('What is the policy for duty mileage?',{}, {},self.index)
        self.assertEqual(result['intent'],'mileage')
        self.assertIn('motor mileage',result['hits'][0]['text'])
        self.assertEqual(result['hits'][0]['paragraph'],'99.9802')
        self.assertEqual(result['hits'][0]['page'],1)
        self.assertEqual(result['hits'][0]['chapter'],'CHAPTER 99 TEST ONLY')

    def test_missing_documents_do_not_invent_citations(self):
        missing=PolicyIndex(Path(self.temp.name)/'absent.sqlite3')
        result=answer('Can I claim lunch?',{'rank':'Sergeant'}, {},missing)
        self.assertTrue(result['unavailable']);self.assertEqual(result['hits'],[])
        self.assertNotIn('paragraph',result['answer'].lower())
        self.assertIn('Sergeant',result['context'])

    def test_unrelated_question_abstains(self):
        self.assertIsNone(classify('How do I repair a dishwasher?'))
        self.assertEqual(self.index.search('How do I repair a dishwasher?'),[])

    def test_failed_refresh_does_not_destroy_existing_index(self):
        before=self.path.read_bytes()
        with patch('scripts.index_policies.fetch',side_effect=ValueError('source unavailable')):
            result=refresh(self.path.parent,['JSP 752'])
        self.assertEqual(result['state'],'unavailable')
        self.assertEqual(self.path.read_bytes(),before)

    def test_nonofficial_download_is_rejected_without_network(self):
        for url in ['http://www.gov.uk/example.pdf','https://evil.example/test.pdf','https://www.gov.uk@evil.example/test.pdf','https://www.gov.uk:8443/test.pdf']:
            with self.assertRaises(ValueError):fetch(url)

    def test_unnumbered_text_gets_page_not_invented_paragraph(self):
        hits=list(split_pages(['A real page without numbered paragraphs. '*8]))
        self.assertEqual(hits[0]['paragraph'],'')
        self.assertEqual(hits[0]['page'],1)

    def test_partial_refresh_retains_other_indexed_sources(self):
        extra={'source_id':'JSP 905','document_id':'other-fixture','title':'TEST ONLY pension','url':'https://assets.publishing.service.gov.uk/test-only-pension.pdf','retrieved_at':'2026-01-01','sha256':'test-only','pages':['Early departure payments pension eligibility qualifying service. '*8]}
        write_index(self.path,[extra],retain_existing=True)
        self.assertTrue(self.index.search('duty mileage'))
        self.assertTrue(self.index.search('early departure pension'))

    def test_corrupt_index_abstains_without_fabrication(self):
        self.path.write_bytes(b'broken index')
        self.assertEqual(self.index.search('Can I claim lunch?'),[])

    def test_pdf_fetch_parse_index_and_quote_pipeline(self):
        # A generated TEST PDF exercises the actual parser and FTS pipeline.
        # Its invented identifier is never packaged as a production citation.
        import io
        from pypdf import PdfWriter
        from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
        writer=PdfWriter();page=writer.add_blank_page(width=1200,height=900)
        font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
        page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):font})})
        stream=DecodedStreamObject();text='99.9801. '+MEAL*3
        stream.set_data(('BT /F1 12 Tf 40 700 Td ('+text+') Tj ET').encode('ascii'))
        page[NameObject('/Contents')]=writer._add_object(stream)
        output=io.BytesIO();writer.write(output)
        url='https://assets.publishing.service.gov.uk/synthetic-test-only.pdf'
        with patch('scripts.index_policies.fetch',side_effect=[(('<a href="'+url+'">TEST ONLY</a>').encode(),url),(output.getvalue(),url)]):
            result=refresh(self.path.parent,['JSP 752'])
        self.assertEqual(result['state'],'ready')
        hit=self.index.search('Can I claim my lunch?')[0]
        self.assertEqual(hit['paragraph'],'99.9801')
        self.assertIn('fictional fixture',hit['text'])
        self.assertEqual(hit['url'],url)
        self.assertEqual(len(hit['sha256']),64)

    def test_corrupt_manifest_is_reported_as_unavailable(self):
        for value in ['not json','{}','[]']:
            (self.path.parent/'manifest.json').write_text(value)
            self.assertEqual(self.index.status()['state'],'unavailable')
            self.assertIsInstance(self.index.status()['errors'][0],dict)
