"""
Test Identifier - Identifies which test type each record belongs to
"""

import logging

class TestIdentifier:
    def __init__(self, test_mappings):
        self.test_mappings = test_mappings
        self.logger = logging.getLogger(__name__)
        
        # Build reverse lookup for test identifiers
        self.identifier_map = {}
        for test_key, config in test_mappings.items():
            identifiers = config.get('test_type_identifier', [])
            if isinstance(identifiers, str):
                identifiers = [identifiers]
            
            for identifier in identifiers:
                self.identifier_map[identifier.lower()] = test_key
    
    def identify_test(self, record):
        """
        Identify test type from record
        Expected format: [PatientID, TestName, Age, Gender, Reading, ...]
        """
        if len(record) < 2:
            self.logger.warning("Record too short to identify test type")
            return None
            
        test_name = record[1].strip().lower()
        
        # Direct lookup
        if test_name in self.identifier_map:
            identified_test = self.identifier_map[test_name]
            self.logger.debug(f"Identified test '{test_name}' as '{identified_test}'")
            return identified_test
        
        # Partial matching
        for identifier, test_key in self.identifier_map.items():
            if identifier in test_name or test_name in identifier:
                self.logger.debug(f"Partial match: '{test_name}' matched with '{identifier}' -> '{test_key}'")
                return test_key
        
        # Log unrecognized test types for future configuration
        self.logger.warning(f"Unrecognized test type: '{test_name}'. Available types: {list(self.identifier_map.keys())}")
        return None
    
    def get_available_tests(self):
        """Get list of all available test types"""
        return list(self.test_mappings.keys())
    
    def get_test_identifiers(self, test_key):
        """Get all identifiers for a specific test"""
        if test_key in self.test_mappings:
            return self.test_mappings[test_key].get('test_type_identifier', [])
        return []
