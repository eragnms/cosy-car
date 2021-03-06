# -*- coding: utf-8 -*-

import unittest
import logging
from unittest.mock import patch
import configparser

from cosycar.constants import Constants
from cosycar.sections import Sections
from cosycar.sections import Engine
from cosycar.sections import Compartment
from cosycar.sections import Windscreen

CFG_FILE = 'tests/data/cosycar_template.cfg'


class CarSectionTests(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(
            filename='tests/data/cosycar.log',
            level='DEBUG',
            format=Constants.log_format)
        self._config = configparser.ConfigParser()
        self._config.read(CFG_FILE)

    def tearDown(self):
        pass

    @patch('configparser.ConfigParser.getboolean')
    def test_check_in_use(self, getboolean_mock):
        sections = Sections(CFG_FILE)
        section = 'SECTION_ENGINE'
        sections.check_in_use(section)
        getboolean_mock.assert_any_call(section, 'in_use')

    @patch('configparser.ConfigParser.get')
    def test_get_heater_name(self, get_mock):
        sections = Sections(CFG_FILE)
        section = 'SECTION_ENGINE'
        sections.get_heater_name(section)
        get_mock.assert_any_call(section, 'heater')

    @patch('cosycar.sections.Sections._read_config')
    def test_get_heaterdata(self, read_config_mock):
        read_config_mock.return_value = self._config
        sections = Sections(CFG_FILE)
        heater_name = 'block_heater'
        power = sections.get_heater_power(heater_name)
        self.assertEqual(power, 1000)

    @patch('cosycar.sections.Sections._read_config')
    def test_get_heater_power_2(self, read_config_mock):
        read_config_mock.return_value = self._config
        sections = Sections(CFG_FILE)
        heater_name = 'compartment_heater_1'
        power = sections.get_heater_power(heater_name)
        self.assertEqual(power, 1500)

    @patch('cosycar.sections.Sections._read_config')
    def test_get_heater_zwave_id(self, read_config_mock):
        read_config_mock.return_value = self._config
        sections = Sections(CFG_FILE)
        heater_name = 'compartment_heater_1'
        zwave_id = sections.get_heater_zwave_id(heater_name)
        self.assertEqual(zwave_id, 14)

    @patch('cosycar.sections.Sections._read_config')
    def test_get_heater_zwave_id_2(self, read_config_mock):
        read_config_mock.return_value = self._config
        sections = Sections(CFG_FILE)
        heater_name = 'block_heater'
        zwave_id = sections.get_heater_zwave_id(heater_name)
        self.assertEqual(zwave_id, 21)

    @patch('cosycar.sections.Sections._read_config')
    def test_get_heater_zwave_id_none(self, read_config_mock):
        read_config_mock.return_value = self._config
        sections = Sections(CFG_FILE)
        heater_name = '"compartment_heater_111"'
        zwave_id = sections.get_heater_zwave_id(heater_name)
        self.assertIsNone(zwave_id)

    def test_find_required_energy_engine_1(self):
        section = Engine(CFG_FILE)
        weather = {'temperature': 10}
        section.weather = weather
        energy = section.find_req_energy()
        self.assertEqual(energy, 500)

    def test_find_required_energy_engine_2(self):
        section = Engine(CFG_FILE)
        weather = {'temperature': 1}
        section.weather = weather
        energy = section.find_req_energy()
        self.assertEqual(energy, 833)

    def test_find_required_energy_engine_3(self):
        section = Engine(CFG_FILE)
        weather = {'temperature': 6.5}
        section.weather = weather
        energy = section.find_req_energy()
        self.assertEqual(energy, 500)

    def test_find_required_energy_engine_4(self):
        section = Engine(CFG_FILE)
        weather = {'temperature': -14.7}
        section.weather = weather
        energy = section.find_req_energy()
        self.assertEqual(energy, 2000)

    def test_find_required_energy_engine_5(self):
        section = Engine(CFG_FILE)
        weather = {'temperature': -9.9}
        section.weather = weather
        energy = section.find_req_energy()
        self.assertEqual(energy, 1830)

    def test_find_required_energy_compartment_1(self):
        section = Compartment(CFG_FILE)
        weather = {'temperature': 10}
        section.weather = weather
        energy = section.find_req_energy()
        self.assertEqual(energy, 233)

    def test_find_required_energy_compartment_2(self):
        section = Compartment(CFG_FILE)
        weather = {'temperature': -12.6}
        section.weather = weather
        energy = section.find_req_energy()
        self.assertEqual(energy, 1400)

    def test_find_required_energy_compartment_3(self):
        section = Compartment(CFG_FILE)
        weather = {'temperature': -17.6}
        section.weather = weather
        energy = section.find_req_energy()
        self.assertEqual(energy, 1400)

    def test_find_required_energy_compartment_4(self):
        section = Compartment(CFG_FILE)
        weather = {'temperature': 11.6}
        section.weather = weather
        energy = section.find_req_energy()
        self.assertEqual(energy, 0)

    def test_find_required_energy_compartment_5(self):
        section = Compartment(CFG_FILE)
        weather = {'temperature': 7.7}
        section.weather = weather
        energy = section.find_req_energy()
        self.assertEqual(energy, 233)

    def test_find_required_energy_compartment_6(self):
        section = Compartment(CFG_FILE)
        weather = {'temperature': -8.3}
        section.weather = weather
        energy = section.find_req_energy()
        self.assertEqual(energy, 1166)

    @patch('cosycar.sections.Switch')
    @patch('cosycar.sections.Switch.is_on')
    @patch('cosycar.sections.Switch.turn_off')
    @patch('cosycar.sections.Switch.turn_on')
    def test_should_be_on_currently_off(
            self,
            mock_turn_on,
            mock_turn_off,
            mock_is_on,
            switch_mock, ):
        section = Engine(CFG_FILE)
        section.minutes_to_next_event = 10
        section.req_energy = 100
        section.heater_power = 200
        mock_is_on.return_value = False
        switch_should_be_on = section.should_be_on()
        self.assertTrue(switch_should_be_on)

    @patch('cosycar.sections.Switch')
    @patch('cosycar.sections.Switch.is_on')
    @patch('cosycar.sections.Switch.turn_off')
    @patch('cosycar.sections.Switch.turn_on')
    def test_should_be_on_currently_on(
            self,
            mock_turn_on,
            mock_turn_off,
            mock_is_on,
            mock_switch):
        section = Engine(CFG_FILE)
        section.minutes_to_next_event = 10
        section.req_energy = 100
        section.heater_power = 200
        mock_is_on.return_value = True
        switch_should_be_on = section.should_be_on()
        self.assertTrue(switch_should_be_on)

    @patch('cosycar.sections.Switch')
    @patch('cosycar.sections.Switch.is_on')
    @patch('cosycar.sections.Switch.turn_off')
    @patch('cosycar.sections.Switch.turn_on')
    def test_should_be_off_currently_on(
            self,
            mock_turn_on,
            mock_turn_off,
            mock_is_on,
            switch_mock, ):
        section = Engine(CFG_FILE)
        section.minutes_to_next_event = 40
        section.req_energy = 100
        section.heater_power = 200
        mock_is_on.return_value = True
        switch_should_be_on = section.should_be_on()
        self.assertFalse(switch_should_be_on)

    def test_available_sections_engine(self):
        sections = Sections(CFG_FILE)
        available = sections.available_sections()
        self.assertIsInstance(available[0], Engine)

    def test_available_sections_compartment(self):
        sections = Sections(CFG_FILE)
        available = sections.available_sections()
        self.assertIsInstance(available[1], Compartment)

    def test_available_sections_windscreen(self):
        sections = Sections(CFG_FILE)
        available = sections.available_sections()
        self.assertIsInstance(available[2], Windscreen)


if __name__ == '__main__':
    unittest.main()
