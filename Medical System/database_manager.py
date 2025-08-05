"""
Database Manager for Medical Test System
Handles all database operations including patient records and test results.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "medical_test_data.db"):
        """Initialize database manager and create tables if they don't exist"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Patients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id TEXT PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    date_of_birth DATE,
                    gender TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Test types table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_types (
                    test_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT UNIQUE NOT NULL,
                    normal_min REAL,
                    normal_max REAL,
                    unit TEXT,
                    description TEXT,
                    category TEXT
                )
            ''')
            
            # Add category column if it doesn't exist (for existing databases)
            try:
                cursor.execute('ALTER TABLE test_types ADD COLUMN category TEXT')
                conn.commit()
            except sqlite3.OperationalError:
                # Column already exists
                pass
            
            # Add critical threshold columns if they don't exist
            try:
                cursor.execute('ALTER TABLE test_types ADD COLUMN critical_low REAL')
                conn.commit()
            except sqlite3.OperationalError:
                # Column already exists
                pass
                
            try:
                cursor.execute('ALTER TABLE test_types ADD COLUMN critical_high REAL')
                conn.commit()
            except sqlite3.OperationalError:
                # Column already exists
                pass
                
            try:
                cursor.execute('ALTER TABLE test_types ADD COLUMN method TEXT')
                conn.commit()
            except sqlite3.OperationalError:
                # Column already exists
                pass
            
            # Test results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_results (
                    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT NOT NULL,
                    test_type_id INTEGER NOT NULL,
                    test_value REAL NOT NULL,
                    test_date DATE NOT NULL,
                    lab_technician TEXT,
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
                    FOREIGN KEY (test_type_id) REFERENCES test_types (test_type_id)
                )
            ''')
            
            # Custom test ranges table for age/gender/condition-specific ranges
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_test_ranges (
                    range_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_type_id INTEGER NOT NULL,
                    range_name TEXT NOT NULL,
                    age_min INTEGER,
                    age_max INTEGER,
                    gender TEXT,
                    condition_name TEXT,
                    normal_min REAL,
                    normal_max REAL,
                    critical_low REAL,
                    critical_high REAL,
                    is_active BOOLEAN DEFAULT 1,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (test_type_id) REFERENCES test_types (test_type_id)
                )
            ''')
            
            # Lab settings table for custom configurations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lab_settings (
                    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_name TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    setting_type TEXT DEFAULT 'text',
                    description TEXT,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert default test types
            self.insert_default_test_types()
            
            conn.commit()
    
    def insert_default_test_types(self):
        """Insert common medical test types with normal ranges - currently disabled for mast ekdum saaf start"""
        # Starting with clean slate - no default test types
        # Users can add their own test types through the Test Configuration interface
        
        # If you want to re-enable default test types, uncomment the code below:
        """
        default_tests = [
            ("Hemoglobin", 12.0, 16.0, "g/dL", "Blood hemoglobin level"),
            ("White Blood Cell Count", 4000, 11000, "cells/μL", "WBC count"),
            ("Platelet Count", 150000, 450000, "cells/μL", "Platelet count"),
            ("Blood Glucose", 70, 100, "mg/dL", "Fasting blood glucose"),
            ("Cholesterol Total", 0, 200, "mg/dL", "Total cholesterol"),
            ("HDL Cholesterol", 40, 100, "mg/dL", "High-density lipoprotein"),
            ("LDL Cholesterol", 0, 100, "mg/dL", "Low-density lipoprotein"),
            ("Triglycerides", 0, 150, "mg/dL", "Serum triglycerides"),
            ("Creatinine", 0.6, 1.2, "mg/dL", "Serum creatinine"),
            ("Blood Urea Nitrogen", 7, 20, "mg/dL", "BUN level"),
            ("ALT", 7, 40, "U/L", "Alanine aminotransferase"),
            ("AST", 8, 40, "U/L", "Aspartate aminotransferase"),
            ("Blood Pressure Systolic", 90, 120, "mmHg", "Systolic blood pressure"),
            ("Blood Pressure Diastolic", 60, 80, "mmHg", "Diastolic blood pressure"),
            ("Heart Rate", 60, 100, "bpm", "Resting heart rate")
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for test in default_tests:
                cursor.execute('''
                    INSERT OR IGNORE INTO test_types 
                    (test_name, normal_min, normal_max, unit, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', test)
        """
        pass  # Do nothing - clean slate
    
    def add_patient(self, patient_id: str, first_name: str = None, last_name: str = None, 
                   date_of_birth: str = None, gender: str = None, 
                   phone: str = None, email: str = None, address: str = None) -> bool:
        """Add a new patient to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO patients 
                    (patient_id, first_name, last_name, date_of_birth, gender, phone, email, address)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (patient_id, first_name, last_name, date_of_birth, gender, phone, email, address))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False  # Patient ID already exists
    
    def get_patient(self, patient_id: str) -> Optional[Tuple]:
        """Get patient information by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
            return cursor.fetchone()
    
    def get_all_patients(self) -> List[Tuple]:
        """Get all patients from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM patients ORDER BY last_name, first_name')
            return cursor.fetchall()
    
    def update_patient(self, patient_id: str, **kwargs) -> bool:
        """Update patient information"""
        if not kwargs:
            return False
            
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [patient_id]
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    UPDATE patients SET {set_clause} WHERE patient_id = ?
                ''', values)
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def add_test_result(self, patient_id: str, test_type_id: int, test_value: float, 
                       test_date: str, lab_technician: str = None, notes: str = None, 
                       check_duplicates: bool = True) -> bool:
        """
        Add a new test result
        
        Args:
            patient_id: Patient identifier
            test_type_id: Test type identifier  
            test_value: Test value
            test_date: Test date
            lab_technician: Lab technician name (optional)
            notes: Additional notes (optional)
            check_duplicates: Whether to check for duplicates before adding (default: True)
            
        Returns:
            True if added successfully, False if duplicate found or error occurred
        """
        try:
            # Check for duplicates if requested
            if check_duplicates:
                if self.check_duplicate_test_result(patient_id, test_type_id, test_value, test_date):
                    return False  # Duplicate found, don't add
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO test_results 
                    (patient_id, test_type_id, test_value, test_date, lab_technician, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (patient_id, test_type_id, test_value, test_date, lab_technician, notes))
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def check_duplicate_test_result(self, patient_id: str, test_type_id: int, test_value: float, 
                                   test_date: str, tolerance_minutes: int = 30) -> bool:
        """
        Check if a similar test result already exists for the same patient.
        
        Args:
            patient_id: Patient identifier
            test_type_id: Test type identifier
            test_value: Test value to check
            test_date: Test date to check
            tolerance_minutes: Time tolerance in minutes for considering records as duplicates
            
        Returns:
            True if a duplicate is found, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Convert test_date to datetime for comparison if it's a string
                if isinstance(test_date, str):
                    try:
                        test_datetime = datetime.strptime(test_date, '%Y-%m-%d')
                        test_date_str = test_date
                    except ValueError:
                        try:
                            test_datetime = datetime.strptime(test_date, '%Y-%m-%d %H:%M:%S')
                            test_date_str = test_datetime.strftime('%Y-%m-%d')
                        except ValueError:
                            # If date parsing fails, use exact string match
                            test_date_str = test_date
                            test_datetime = None
                else:
                    test_datetime = test_date
                    test_date_str = test_date.strftime('%Y-%m-%d')
                
                # Check for exact matches first (same patient, test type, value, and date)
                cursor.execute('''
                    SELECT COUNT(*) FROM test_results 
                    WHERE patient_id = ? AND test_type_id = ? AND test_value = ? AND test_date = ?
                ''', (patient_id, test_type_id, test_value, test_date_str))
                
                exact_count = cursor.fetchone()[0]
                if exact_count > 0:
                    return True
                
                # If we have datetime information, check for near-duplicate times
                if test_datetime and tolerance_minutes > 0:
                    # Calculate time range for near-duplicates
                    from datetime import timedelta
                    start_time = test_datetime - timedelta(minutes=tolerance_minutes)
                    end_time = test_datetime + timedelta(minutes=tolerance_minutes)
                    
                    start_date_str = start_time.strftime('%Y-%m-%d')
                    end_date_str = end_time.strftime('%Y-%m-%d')
                    
                    # Check for near-duplicates within time tolerance
                    cursor.execute('''
                        SELECT COUNT(*) FROM test_results 
                        WHERE patient_id = ? AND test_type_id = ? AND test_value = ? 
                        AND test_date BETWEEN ? AND ?
                    ''', (patient_id, test_type_id, test_value, start_date_str, end_date_str))
                    
                    near_count = cursor.fetchone()[0]
                    if near_count > 0:
                        return True
                
                return False
                
        except sqlite3.Error:
            # If there's a database error, assume no duplicate to allow import
            return False
    
    def get_patient_test_results(self, patient_id: str) -> List[Tuple]:
        """Get all test results for a specific patient"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tr.result_id, tr.patient_id, tt.test_name, tr.test_value, 
                       tt.normal_min, tt.normal_max, tt.unit, tr.test_date,
                       tr.lab_technician, tr.notes
                FROM test_results tr
                JOIN test_types tt ON tr.test_type_id = tt.test_type_id
                WHERE tr.patient_id = ?
                ORDER BY tr.test_date DESC
            ''', (patient_id,))
            return cursor.fetchall()
    
    def get_patient_test_results_with_method(self, patient_id: str) -> List[Tuple]:
        """Get all test results for a specific patient including method information"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tr.result_id, tr.patient_id, tt.test_name, tr.test_value, 
                       tt.normal_min, tt.normal_max, tt.unit, tr.test_date,
                       tr.lab_technician, tr.notes, tt.method
                FROM test_results tr
                JOIN test_types tt ON tr.test_type_id = tt.test_type_id
                WHERE tr.patient_id = ?
                ORDER BY tr.test_date DESC
            ''', (patient_id,))
            return cursor.fetchall()
    
    def get_test_types(self) -> List[Tuple]:
        """Get all available test types"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT test_type_id, test_name, normal_min, normal_max, unit, description, category,
                       critical_low, critical_high, method 
                FROM test_types ORDER BY test_name
            ''')
            return cursor.fetchall()
    
    def get_test_type_by_name(self, test_name: str) -> Optional[Tuple]:
        """Get test type by name"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT test_type_id, test_name, normal_min, normal_max, unit, description, category,
                       critical_low, critical_high, method 
                FROM test_types WHERE test_name = ?
            ''', (test_name,))
            return cursor.fetchone()
    
    def add_test_type(self, test_name: str, description: str = None,
                     unit: str = None, normal_min: float = None, 
                     normal_max: float = None, category: str = None,
                     critical_low: float = None, critical_high: float = None,
                     method: str = None) -> bool:
        """Add a new test type with critical thresholds and method"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # First, ensure critical threshold columns exist
                try:
                    cursor.execute('ALTER TABLE test_types ADD COLUMN critical_low REAL')
                except sqlite3.OperationalError:
                    pass  # Column already exists
                try:
                    cursor.execute('ALTER TABLE test_types ADD COLUMN critical_high REAL')
                except sqlite3.OperationalError:
                    pass  # Column already exists
                try:
                    cursor.execute('ALTER TABLE test_types ADD COLUMN method TEXT')
                except sqlite3.OperationalError:
                    pass  # Column already exists
                
                cursor.execute('''
                    INSERT INTO test_types (test_name, description, unit, normal_min, normal_max, 
                                          category, critical_low, critical_high, method)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (test_name, description, unit, normal_min, normal_max, category, critical_low, critical_high, method))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False  # Test name already exists
    
    def delete_patient(self, patient_id: str) -> bool:
        """Delete a patient and all their test results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Delete test results first (foreign key constraint)
                cursor.execute('DELETE FROM test_results WHERE patient_id = ?', (patient_id,))
                # Delete patient
                cursor.execute('DELETE FROM patients WHERE patient_id = ?', (patient_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def delete_test_result(self, result_id: int) -> bool:
        """Delete a specific test result"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM test_results WHERE result_id = ?', (result_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def get_test_type_by_id(self, test_type_id: int) -> Optional[Tuple]:
        """Get test type by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT test_type_id, test_name, normal_min, normal_max, unit, description, category,
                       critical_low, critical_high, method 
                FROM test_types WHERE test_type_id = ?
            ''', (test_type_id,))
            return cursor.fetchone()
    
    def get_test_type(self, test_type_id: int) -> Optional[Tuple]:
        """Get test type by ID (alias for get_test_type_by_id)"""
        return self.get_test_type_by_id(test_type_id)
    
    def update_test_type(self, test_type_id: int, test_name: Optional[str] = None,
                        description: Optional[str] = None, 
                        unit: Optional[str] = None, normal_min: Optional[float] = None,
                        normal_max: Optional[float] = None, category: Optional[str] = None,
                        critical_low: Optional[float] = None, critical_high: Optional[float] = None,
                        method: Optional[str] = None) -> bool:
        """Update an existing test type with critical thresholds and method"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Ensure critical threshold columns exist
                try:
                    cursor.execute('ALTER TABLE test_types ADD COLUMN critical_low REAL')
                except sqlite3.OperationalError:
                    pass
                try:
                    cursor.execute('ALTER TABLE test_types ADD COLUMN critical_high REAL')
                except sqlite3.OperationalError:
                    pass
                try:
                    cursor.execute('ALTER TABLE test_types ADD COLUMN method TEXT')
                except sqlite3.OperationalError:
                    pass
                
                cursor.execute('''
                    UPDATE test_types 
                    SET test_name = ?, description = ?, unit = ?, normal_min = ?, normal_max = ?, 
                        category = ?, critical_low = ?, critical_high = ?, method = ?
                    WHERE test_type_id = ?
                ''', (test_name, description, unit, normal_min, normal_max, category, critical_low, critical_high, method, test_type_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False
    
    def delete_test_type(self, test_type_id: int) -> bool:
        """Delete a test type and all associated test results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # First delete all test results of this type
                cursor.execute('DELETE FROM test_results WHERE test_type_id = ?', (test_type_id,))
                # Then delete the test type
                cursor.execute('DELETE FROM test_types WHERE test_type_id = ?', (test_type_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def get_critical_thresholds(self, test_name: str) -> Optional[dict]:
        """Get critical thresholds for a test type (placeholder for future enhancement)"""
        # This would be implemented when critical thresholds table is added
        return None
    
    def search_patients(self, search_term: str) -> List[Tuple]:
        """Search patients by name or ID"""
        search_pattern = f"%{search_term}%"
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM patients 
                WHERE patient_id LIKE ? OR first_name LIKE ? OR last_name LIKE ?
                ORDER BY last_name, first_name
            ''', (search_pattern, search_pattern, search_pattern))
            return cursor.fetchall()
    
    def get_database_stats(self) -> dict:
        """Get basic statistics about the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Count patients
            cursor.execute('SELECT COUNT(*) FROM patients')
            patient_count = cursor.fetchone()[0]
            
            # Count test results
            cursor.execute('SELECT COUNT(*) FROM test_results')
            result_count = cursor.fetchone()[0]
            
            # Count test types
            cursor.execute('SELECT COUNT(*) FROM test_types')
            test_type_count = cursor.fetchone()[0]
            
            return {
                'patients': patient_count,
                'test_results': result_count,
                'test_types': test_type_count
            }
    
    def get_patient_demographics_summary(self, patient_id: str) -> dict:
        """Get a summary of patient demographics with missing value indicators"""
        patient_info = self.get_patient(patient_id)
        if not patient_info:
            return None
            
        age = self.calculate_age(patient_info[3]) if patient_info[3] else None
        gender = patient_info[4] if patient_info[4] else None
        
        return {
            'patient_id': patient_info[0],
            'first_name': patient_info[1] or 'Not provided',
            'last_name': patient_info[2] or 'Not provided',
            'date_of_birth': patient_info[3] or 'Not provided',
            'age': age,
            'age_display': f"{age} years" if age is not None else "Unknown (no birth date)",
            'gender': gender or 'Not specified',
            'has_age': age is not None,
            'has_gender': gender is not None,
            'demographic_completeness': self._assess_demographic_completeness(age, gender)
        }
    
    def _assess_demographic_completeness(self, age: Optional[int], gender: Optional[str]) -> dict:
        """Assess how complete the demographic information is for medical interpretation"""
        completeness = {
            'score': 0,  # 0-100 score
            'level': 'poor',  # poor, fair, good, excellent
            'missing': [],
            'recommendations': []
        }
        
        if age is not None:
            completeness['score'] += 50
        else:
            completeness['missing'].append('age')
            completeness['recommendations'].append('Add date of birth for age-specific normal ranges')
            
        if gender is not None:
            completeness['score'] += 50
        else:
            completeness['missing'].append('gender')
            completeness['recommendations'].append('Add gender for gender-specific normal ranges')
        
        # Determine level
        if completeness['score'] >= 100:
            completeness['level'] = 'excellent'
        elif completeness['score'] >= 50:
            completeness['level'] = 'good'
        elif completeness['score'] >= 25:
            completeness['level'] = 'fair'
        else:
            completeness['level'] = 'poor'
            
        return completeness
    
    def calculate_age(self, date_of_birth: str) -> Optional[int]:
        """Calculate age from date of birth"""
        if not date_of_birth:
            return None
        try:
            from datetime import datetime
            birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d')
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age
        except:
            return None
    
    def get_age_gender_adjusted_range(self, test_name: str, age: Optional[int], gender: Optional[str], condition: Optional[str] = None) -> dict:
        """Get age and gender adjusted normal ranges for medical tests"""
        # First, try to get a custom range that matches the patient characteristics
        custom_range = self.get_best_matching_range(test_name, age, gender, condition)
        
        # Get the base test type for fallback values
        test_type = self.get_test_type_by_name(test_name)
        if not test_type:
            return {
                'normal_min': None,
                'normal_max': None,
                'critical_low': None,
                'critical_high': None,
                'source': 'No range found',
                'age_adjusted': False,
                'gender_adjusted': False
            }
        
        # Extract base test type values 
        # test_type: (test_type_id, test_name, normal_min, normal_max, unit, description, category, critical_low, critical_high, method)
        base_min, base_max = test_type[2], test_type[3]  # normal_min, normal_max
        base_critical_low = test_type[7] if len(test_type) > 7 else None  # critical_low
        base_critical_high = test_type[8] if len(test_type) > 8 else None  # critical_high
        
        if custom_range:
            # Use custom range for normal values, but fall back to base for critical if not defined
            custom_critical_low = custom_range.get('critical_low')
            custom_critical_high = custom_range.get('critical_high')
            
            # Use custom critical thresholds if available, otherwise use base test type critical thresholds
            final_critical_low = custom_critical_low if custom_critical_low is not None else base_critical_low
            final_critical_high = custom_critical_high if custom_critical_high is not None else base_critical_high
            
            return {
                'normal_min': custom_range['normal_min'],
                'normal_max': custom_range['normal_max'],
                'critical_low': final_critical_low,
                'critical_high': final_critical_high,
                'source': f"Custom range: {custom_range['range_name']}",
                'age_adjusted': age is not None,
                'gender_adjusted': gender is not None
            }
        
        # Age and gender specific adjustments (fallback system)
        adjustments = {
            "Hemoglobin": {
                "Male": {"adult": (13.8, 17.2), "child": (11.0, 16.0), "elderly": (13.0, 16.8)},
                "Female": {"adult": (12.1, 15.1), "child": (11.0, 16.0), "elderly": (11.7, 15.5)}
            },
            "Creatinine": {
                "Male": {"adult": (0.7, 1.3), "child": (0.3, 0.7), "elderly": (0.8, 1.4)},
                "Female": {"adult": (0.6, 1.1), "child": (0.3, 0.7), "elderly": (0.6, 1.2)}
            },
            "HDL Cholesterol": {
                "Male": {"adult": (40, 100), "child": (35, 100), "elderly": (40, 100)},
                "Female": {"adult": (50, 100), "child": (35, 100), "elderly": (50, 100)}
            },
            "Heart Rate": {
                "all": {
                    "infant": (100, 160), "child": (70, 120), "teen": (60, 100), 
                    "adult": (60, 100), "elderly": (60, 100)
                }
            },
            "Blood Pressure Systolic": {
                "all": {
                    "child": (80, 110), "teen": (100, 120), "adult": (90, 120), 
                    "elderly": (90, 140)
                }
            }
        }
        
        # Track if we made adjustments
        age_adjusted = False
        gender_adjusted = False
        source_info = "Base range"
        
        if test_name in adjustments:
            test_adj = adjustments[test_name]
            
            # Determine age group - use adult as default if age is unknown
            age_group = "adult"  # Default fallback
            if age is not None:
                if age < 2:
                    age_group = "infant"
                elif age < 13:
                    age_group = "child"
                elif age < 18:
                    age_group = "teen"
                elif age >= 65:
                    age_group = "elderly"
                age_adjusted = True
            
            # Get gender-specific or general ranges
            if gender and gender in test_adj:
                if age_group in test_adj[gender]:
                    adj_min, adj_max = test_adj[gender][age_group]
                    gender_adjusted = True
                    if age_adjusted:
                        source_info = f'Age/gender adjusted ({age_group}, {gender})'
                    else:
                        source_info = f'Gender adjusted (assumed adult, {gender})'
                    return {
                        'normal_min': adj_min,
                        'normal_max': adj_max,
                        'critical_low': base_critical_low,
                        'critical_high': base_critical_high,
                        'source': source_info,
                        'age_adjusted': age_adjusted,
                        'gender_adjusted': gender_adjusted
                    }
            elif "all" in test_adj and age_group in test_adj["all"]:
                adj_min, adj_max = test_adj["all"][age_group]
                if age_adjusted:
                    source_info = f'Age adjusted ({age_group})'
                else:
                    source_info = f'General range (assumed adult)'
                return {
                    'normal_min': adj_min,
                    'normal_max': adj_max,
                    'critical_low': base_critical_low,
                    'critical_high': base_critical_high,
                    'source': source_info,
                    'age_adjusted': age_adjusted,
                    'gender_adjusted': gender_adjusted
                }
        
        # Return base ranges if no specific adjustment found
        return {
            'normal_min': base_min,
            'normal_max': base_max,
            'critical_low': base_critical_low,
            'critical_high': base_critical_high,
            'source': 'Base range',
            'age_adjusted': False,
            'gender_adjusted': False
        }
    
    def add_custom_test_range(self, test_type_id: int, range_name: str, 
                             age_min: int = None, age_max: int = None, 
                             gender: str = None, condition_name: str = None,
                             normal_min: float = None, normal_max: float = None,
                             critical_low: float = None, critical_high: float = None,
                             notes: str = None) -> bool:
        """Add a custom test range for specific demographics or conditions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO custom_test_ranges 
                    (test_type_id, range_name, age_min, age_max, gender, condition_name,
                     normal_min, normal_max, critical_low, critical_high, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (test_type_id, range_name, age_min, age_max, gender, condition_name,
                      normal_min, normal_max, critical_low, critical_high, notes))
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def get_custom_test_ranges(self, test_type_id: int = None) -> List[Tuple]:
        """Get custom test ranges, optionally filtered by test type"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if test_type_id:
                cursor.execute('''
                    SELECT ctr.*, tt.test_name 
                    FROM custom_test_ranges ctr
                    JOIN test_types tt ON ctr.test_type_id = tt.test_type_id
                    WHERE ctr.test_type_id = ? AND ctr.is_active = 1
                    ORDER BY ctr.range_name
                ''', (test_type_id,))
            else:
                cursor.execute('''
                    SELECT ctr.*, tt.test_name 
                    FROM custom_test_ranges ctr
                    JOIN test_types tt ON ctr.test_type_id = tt.test_type_id
                    WHERE ctr.is_active = 1
                    ORDER BY tt.test_name, ctr.range_name
                ''')
            return cursor.fetchall()
    
    def update_custom_test_range(self, range_id: int, **kwargs) -> bool:
        """Update a custom test range"""
        if not kwargs:
            return False
            
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [range_id]
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    UPDATE custom_test_ranges SET {set_clause} WHERE range_id = ?
                ''', values)
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def delete_custom_test_range(self, range_id: int) -> bool:
        """Deactivate a custom test range (soft delete)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE custom_test_ranges SET is_active = 0 WHERE range_id = ?', (range_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def get_best_matching_range(self, test_name: str, age: int = None, gender: str = None, 
                               condition: str = None) -> Optional[dict]:
        """Get the best matching custom range based on patient characteristics"""
        test_type = self.get_test_type_by_name(test_name)
        if not test_type:
            return None
        
        test_type_id = test_type[0]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build query based on available patient characteristics
            conditions = ['ctr.test_type_id = ?', 'ctr.is_active = 1']
            params = [test_type_id]
            
            if age is not None:
                conditions.append('(ctr.age_min IS NULL OR ctr.age_min <= ?)')
                conditions.append('(ctr.age_max IS NULL OR ctr.age_max >= ?)')
                params.extend([age, age])
            
            if gender:
                conditions.append('(ctr.gender IS NULL OR ctr.gender = ?)')
                params.append(gender)
            
            if condition:
                conditions.append('(ctr.condition_name IS NULL OR ctr.condition_name = ?)')
                params.append(condition)
            
            # Order by specificity (most specific first)
            order_clause = '''
                ORDER BY 
                    (CASE WHEN ctr.condition_name IS NOT NULL THEN 4 ELSE 0 END) +
                    (CASE WHEN ctr.gender IS NOT NULL THEN 2 ELSE 0 END) +
                    (CASE WHEN ctr.age_min IS NOT NULL OR ctr.age_max IS NOT NULL THEN 1 ELSE 0 END) DESC,
                    ctr.range_name
            '''
            
            query = f'''
                SELECT ctr.*, tt.test_name
                FROM custom_test_ranges ctr
                JOIN test_types tt ON ctr.test_type_id = tt.test_type_id
                WHERE {' AND '.join(conditions)}
                {order_clause}
                LIMIT 1
            '''
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            if result:
                # Convert tuple to dictionary
                columns = ['range_id', 'test_type_id', 'range_name', 'age_min', 'age_max', 
                          'gender', 'condition_name', 'normal_min', 'normal_max', 
                          'critical_low', 'critical_high', 'is_active', 'created_date', 
                          'notes', 'test_name']
                return dict(zip(columns, result))
            
            return None
    
    def add_lab_setting(self, setting_name: str, setting_value: str, 
                       setting_type: str = 'text', description: str = None) -> bool:
        """Add or update a lab setting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO lab_settings 
                    (setting_name, setting_value, setting_type, description, updated_date)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (setting_name, setting_value, setting_type, description))
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def get_lab_setting(self, setting_name: str) -> Optional[str]:
        """Get a lab setting value"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT setting_value FROM lab_settings WHERE setting_name = ?', (setting_name,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_all_lab_settings(self) -> List[Tuple]:
        """Get all lab settings"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT setting_name, setting_value, setting_type, description, updated_date 
                FROM lab_settings ORDER BY setting_name
            ''')
            return cursor.fetchall()
    
    def export_custom_ranges_to_json(self, file_path: str) -> bool:
        """Export custom test ranges to JSON file"""
        try:
            import json
            
            ranges_data = {}
            custom_ranges = self.get_custom_test_ranges()
            
            for range_row in custom_ranges:
                range_id, test_type_id, range_name, age_min, age_max, gender, condition_name, \
                normal_min, normal_max, critical_low, critical_high, is_active, created_date, notes, test_name = range_row
                
                if test_name not in ranges_data:
                    ranges_data[test_name] = []
                
                ranges_data[test_name].append({
                    'range_name': range_name,
                    'age_min': age_min,
                    'age_max': age_max,
                    'gender': gender,
                    'condition_name': condition_name,
                    'normal_min': normal_min,
                    'normal_max': normal_max,
                    'critical_low': critical_low,
                    'critical_high': critical_high,
                    'notes': notes
                })
            
            with open(file_path, 'w') as f:
                json.dump(ranges_data, f, indent=2, default=str)
            
            return True
        except Exception:
            return False
    
    def import_custom_ranges_from_json(self, file_path: str) -> bool:
        """Import custom test ranges from JSON file"""
        try:
            import json
            
            with open(file_path, 'r') as f:
                ranges_data = json.load(f)
            
            for test_name, ranges in ranges_data.items():
                test_type = self.get_test_type_by_name(test_name)
                if not test_type:
                    continue
                
                test_type_id = test_type[0]
                
                for range_config in ranges:
                    self.add_custom_test_range(
                        test_type_id=test_type_id,
                        range_name=range_config.get('range_name'),
                        age_min=range_config.get('age_min'),
                        age_max=range_config.get('age_max'),
                        gender=range_config.get('gender'),
                        condition_name=range_config.get('condition_name'),
                        normal_min=range_config.get('normal_min'),
                        normal_max=range_config.get('normal_max'),
                        critical_low=range_config.get('critical_low'),
                        critical_high=range_config.get('critical_high'),
                        notes=range_config.get('notes')
                    )
            
            return True
        except Exception:
            return False
