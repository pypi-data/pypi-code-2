import unittest
from consume import consume

class ExampleTestCase(unittest.TestCase):
    
    def test_example(self):
        """Tests nothing really..."""
        self.assertEquals(1+1, 2)
        self.assertTrue(True)


class ConsumePackageTestCase(unittest.TestCase):
    '''Tests related to the overall consume package'''
    
    def test_global_method_lists(self):
        '''Tests the global method lists'''
        self.assertEquals(
            consume.list_valid_burntypes(),
            ['natural', 'activity']
        )
        self.assertEquals(
            consume.list_valid_combustion_stages(),
            ['flaming', 'smoldering', 'residual', 'total']
        )
        self.assertEquals(
            consume.list_valid_consumption_strata(),
            ['summary',
             'canopy',
             'woody fuels',
             'shrub',
             'nonwoody',
             'ground fuels',
             'litter-lichen-moss']
        )
        self.assertEquals(
            consume.list_valid_ecoregions(),
            ['western', 'southern', 'boreal']
        )
        self.assertEquals(
            consume.list_valid_emissions_species(),
            ['pm', 'pm10', 'pm25', 'co', 'co2', 'ch4', 'nmhc']
        )
        self.assertEquals(
            consume.list_valid_fm_types(),
            ['MEAS-Th', 'ADJ-Th', 'NFDRS-Th']
        )
        self.assertEquals(
            consume.list_valid_units(),
            ['lbs',
             'lbs_ac',
             'tons',
             'tons_ac',
             'kg',
             'kg_m^2',
             'kg_ha',
             'kg_km^2',
             'tonnes',
             'tonnes_ha',
             'tonnes_km^2']
        )


class FuelConsumptionTestCase(unittest.TestCase):
    '''Tests related to fuel consumption calculations'''
    
    def test_fuel_consumption_object_instantiation(self):
        '''Tests the instantiation of a fuel consumption object'''
        fc = consume.FuelConsumption()
        self.assertTrue(isinstance(fc, consume.FuelConsumption))
    
    def test_import_consume(self):
        '''Tests that the import of the consume module'''
        fc_obj = consume.FuelConsumption()
        fc_obj.fuelbed_fccs_ids = [1, 47]
        fc_obj.fuelbed_area_acres = [100, 200]
        fc_obj.fuelbed_ecoregion = 'western'
        fc_obj.fuel_moisture_1000hr_pct = [50, 40]
        fc_obj.fuel_moisture_duff_pct = [50, 40]
        fc_obj.canopy_consumption_pct = 25
        fc_obj.shrub_blackened_pct = 25
        fc_obj.output_units = 'kg_ha'
        results = fc_obj.results()
        
        # spot check one of the output values
        self.assertAlmostEquals(
            results['consumption']['ground fuels']['duff upper']['flaming'][0],
            896.68185123
        )
        self.assertAlmostEquals(
            results['consumption']['ground fuels']['duff upper']['flaming'][1],
            3586.72740491
        )
