from datetime import date
import unittest
import profile_backup as backup

class BackupTests(unittest.TestCase):
    def test_encrypted_file_survives_new_session_and_excludes_sensitive_free_text(self):
        profile={'rank':'Sergeant','service':'British Army','years':12,'join_date':date(2010,1,1),'posting_location':'DO NOT SAVE','trade':'DO NOT SAVE','dependent_count':2}
        data=backup.save(profile,[{'label':'MPAR','date':date(2030,1,1)}],'a sufficiently long test password')
        self.assertNotIn(b'Sergeant',data)
        restored=backup.load(data,'a sufficiently long test password')
        self.assertEqual(restored['profile']['join_date'],date(2010,1,1))
        self.assertEqual(restored['events'][0]['label'],'MPAR')
        self.assertNotIn('posting_location',restored['profile'])
        self.assertNotIn('trade',restored['profile'])

    def test_wrong_password_and_tampering_are_rejected(self):
        data=backup.save({'rank':'Sergeant'},[],'a sufficiently long test password')
        for wrong in [data[:-3]+b'xxx',data]:
            with self.assertRaises(ValueError):backup.load(wrong,'incorrect password')

    def test_import_rejects_invalid_profile_before_replacing_state(self):
        for profile in [{'rank':'Made up rank'}, {'years':None}, {'dob':'2080-01-01'}, {'dependent_count':999}, {'years':float('nan')},{'service_number':'not permitted'},{'dob':'2015-01-01','join_date':'2010-01-01'}]:
            with self.assertRaises(ValueError):backup.validate({'version':1,'profile':profile,'events':[]})

    def test_explicit_strong_password_required(self):
        with self.assertRaises(ValueError):backup.save({},[],'short')

    def test_supported_reserve_scheme_and_accommodation_are_preserved(self):
        data=backup.save({'pension_schemes':['RFPS 05'],'accommodation_type':'Private rented','rank_history':[{'rank':'Sergeant','date':'2020-01-01','note':'excluded free text'}]},[],'a sufficiently long test password')
        profile=backup.load(data,'a sufficiently long test password')['profile']
        self.assertEqual(profile['pension_schemes'],['RFPS 05'])
        self.assertEqual(profile['accommodation_type'],'Private rented')
        self.assertNotIn('note',profile['rank_history'][0])
