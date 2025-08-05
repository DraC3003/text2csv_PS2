"""
Advanced Test Configuration UI for Medical Test System
Comprehensive interface for managing test types, custom ranges, and critical thresholds
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import time
from typing import Dict, List, Optional

class TestConfigurationFrame:
    def __init__(self, parent, db_manager):
        """Initialize advanced test configuration frame"""
        self.parent = parent
        self.db_manager = db_manager
        self.current_test_type_id = None
        
        self.setup_ui()
        self.refresh_test_types()
    
    def setup_ui(self):
        """Setup the comprehensive test configuration UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Comprehensive Test Configuration", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create main content frame (no more notebook)
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(fill='both', expand=True)
        
        # Setup all functionality in one comprehensive interface
        self.setup_comprehensive_test_config()
    
    def setup_comprehensive_test_config(self):
        """Setup comprehensive test configuration in a single interface"""
        # Create main sections
        
        # Section 1: Test Type Management (Top)
        test_type_section = ttk.LabelFrame(self.content_frame, text="Test Type Management")
        test_type_section.pack(fill='both', expand=True, pady=(0, 10))
        
        # Test type form and list
        test_content = ttk.Frame(test_type_section)
        test_content.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Left side - Basic test info
        basic_form = ttk.LabelFrame(test_content, text="Basic Test Information")
        basic_form.pack(side='left', fill='y', padx=(0, 10))
        
        self.test_form_vars = {}
        basic_fields = [
            ('test_name', 'Test Name*'),
            ('unit', 'Unit'),
            ('method', 'Method')
        ]
        
        for i, (field_name, label_text) in enumerate(basic_fields):
            ttk.Label(basic_form, text=label_text).grid(row=i, column=0, sticky='w', padx=5, pady=5)
            
            var = tk.StringVar()
            entry = ttk.Entry(basic_form, textvariable=var, width=25)
            entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
            self.test_form_vars[field_name] = var
        
        basic_form.columnconfigure(1, weight=1)
        
        # Middle - Range Configuration
        range_form = ttk.LabelFrame(test_content, text="Default & Custom Ranges")
        range_form.pack(side='left', fill='y', padx=5)
        
        range_fields = [
            ('normal_min', 'Default Normal Min'),
            ('normal_max', 'Default Normal Max'),
            ('gender_specific', 'Gender Specific?'),
            ('male_min', 'Male Normal Min'),
            ('male_max', 'Male Normal Max'),
            ('female_min', 'Female Normal Min'),
            ('female_max', 'Female Normal Max')
        ]
        
        for i, (field_name, label_text) in enumerate(range_fields):
            ttk.Label(range_form, text=label_text).grid(row=i, column=0, sticky='w', padx=5, pady=5)
            
            if field_name == 'gender_specific':
                var = tk.BooleanVar()
                check = ttk.Checkbutton(range_form, variable=var, command=self.toggle_gender_fields)
                check.grid(row=i, column=1, sticky='w', padx=5, pady=5)
                self.test_form_vars[field_name] = var
            else:
                var = tk.StringVar()
                entry = ttk.Entry(range_form, textvariable=var, width=15)
                entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
                self.test_form_vars[field_name] = var
                
                # Store entry widget reference for enabling/disabling
                if 'male_' in field_name or 'female_' in field_name:
                    if not hasattr(self, 'gender_entries'):
                        self.gender_entries = []
                    self.gender_entries.append(entry)
                    entry.configure(state='disabled')
        
        range_form.columnconfigure(1, weight=1)
        
        # Right side - Critical Thresholds
        critical_form = ttk.LabelFrame(test_content, text="Critical Thresholds")
        critical_form.pack(side='left', fill='y', padx=(10, 0))
        
        critical_fields = [
            ('critical_low', 'Critical Low'),
            ('critical_high', 'Critical High')
        ]
        
        for i, (field_name, label_text) in enumerate(critical_fields):
            ttk.Label(critical_form, text=label_text).grid(row=i, column=0, sticky='w', padx=5, pady=5)
            var = tk.StringVar()
            entry = ttk.Entry(critical_form, textvariable=var, width=15)
            entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
            self.test_form_vars[field_name] = var
        
        critical_form.columnconfigure(1, weight=1)
        
        # Buttons section
        button_frame = ttk.Frame(test_type_section)
        button_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        ttk.Button(button_frame, text="Add Test Type", command=self.add_comprehensive_test_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Test Type", command=self.update_comprehensive_test_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Test Type", command=self.delete_test_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear All Fields", command=self.clear_comprehensive_form).pack(side='left', padx=5)
        
        # Section 2: Test Types List (Bottom)
        list_section = ttk.LabelFrame(self.content_frame, text="Existing Test Types")
        list_section.pack(fill='both', expand=True)
        
        # Search functionality
        search_frame = ttk.Frame(list_section)
        search_frame.pack(fill='x', padx=20, pady=(15, 5))
        
        ttk.Label(search_frame, text="Search Test Types:").pack(side='left')
        self.test_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.test_search_var, width=30)
        search_entry.pack(side='left', padx=(10, 0))
        search_entry.bind('<KeyRelease>', self.search_test_types)
        
        # Test types tree
        tree_frame = ttk.Frame(list_section)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=(5, 15))
        
        columns = ('ID', 'Name', 'Unit', 'Normal Range', 'Critical Range', 'Method', 'Gender Specific')
        self.test_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)
        
        # Set column widths for better display
        column_widths = {
            'ID': 50,
            'Name': 150,
            'Unit': 80,
            'Normal Range': 180,  # Wider for gender-specific ranges
            'Critical Range': 120,
            'Method': 160,  # Wider for method descriptions
            'Gender Specific': 100
        }
        
        for col in columns:
            self.test_tree.heading(col, text=col)
            self.test_tree.column(col, width=column_widths.get(col, 120))
        
        test_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.test_tree.yview)
        self.test_tree.configure(yscrollcommand=test_scrollbar.set)
        
        self.test_tree.pack(side='left', fill='both', expand=True)
        test_scrollbar.pack(side='right', fill='y')
        
        self.test_tree.bind('<<TreeviewSelect>>', self.on_comprehensive_test_select)
    
    def toggle_gender_fields(self):
        """Enable or disable gender-specific range fields"""
        if hasattr(self, 'gender_entries'):
            if self.test_form_vars['gender_specific'].get():
                # Enable gender-specific fields
                for entry in self.gender_entries:
                    entry.configure(state='normal')
            else:
                # Disable and clear gender-specific fields
                for entry in self.gender_entries:
                    entry.configure(state='disabled')
                # Clear the values
                self.test_form_vars['male_min'].set('')
                self.test_form_vars['male_max'].set('')
                self.test_form_vars['female_min'].set('')
                self.test_form_vars['female_max'].set('')

    def add_comprehensive_test_type(self):
        """Add a new test type with all comprehensive data"""
        if not self.validate_comprehensive_form():
            return
            
        try:
            # Get all form values
            test_data = {key: var.get() for key, var in self.test_form_vars.items() if key != 'gender_specific'}
            
            # Add the test type to database
            self.db_manager.add_test_type(
                test_data['test_name'],
                '',  # description (removed but database may require it)
                test_data['unit'],
                float(test_data['normal_min']) if test_data['normal_min'] else None,
                float(test_data['normal_max']) if test_data['normal_max'] else None,
                'General',  # category (removed but database may require it)
                float(test_data['critical_low']) if test_data['critical_low'] else None,
                float(test_data['critical_high']) if test_data['critical_high'] else None,
                test_data.get('method', '')  # method parameter
            )
            
            # Add gender-specific ranges if enabled
            if self.test_form_vars['gender_specific'].get():
                test_type_id = self.db_manager.get_test_type_by_name(test_data['test_name'])[0]
                
                # Add male ranges
                if test_data['male_min'] and test_data['male_max']:
                    self.db_manager.add_custom_test_range(
                        test_type_id, f"Male-specific range for {test_data['test_name']}",
                        gender='Male',
                        normal_min=float(test_data['male_min']), 
                        normal_max=float(test_data['male_max'])
                    )
                
                # Add female ranges
                if test_data['female_min'] and test_data['female_max']:
                    self.db_manager.add_custom_test_range(
                        test_type_id, f"Female-specific range for {test_data['test_name']}",
                        gender='Female',
                        normal_min=float(test_data['female_min']), 
                        normal_max=float(test_data['female_max'])
                    )
            
            messagebox.showinfo("Success", f"Test type '{test_data['test_name']}' added successfully!")
            self.refresh_test_types()  # Refresh first
            self.clear_comprehensive_form()  # Then clear form
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add test type: {str(e)}")

    def update_comprehensive_test_type(self):
        """Update selected test type with comprehensive data"""
        if not self.current_test_type_id:
            messagebox.showwarning("Warning", "Please select a test type to update.")
            return
            
        if not self.validate_comprehensive_form(update=True):
            return
            
        try:
            test_data = {key: var.get() for key, var in self.test_form_vars.items() if key != 'gender_specific'}
            
            # Update the test type
            self.db_manager.update_test_type(
                self.current_test_type_id,
                test_data['test_name'],
                '',  # description (removed but database may require it)
                test_data['unit'],
                float(test_data['normal_min']) if test_data['normal_min'] else None,
                float(test_data['normal_max']) if test_data['normal_max'] else None,
                'General',  # category (removed but database may require it)
                float(test_data['critical_low']) if test_data['critical_low'] else None,
                float(test_data['critical_high']) if test_data['critical_high'] else None,
                test_data.get('method', '')  # method parameter
            )
            
            # Handle gender-specific ranges updates
            # First, remove existing gender-specific custom ranges for this test type
            try:
                existing_ranges = self.db_manager.get_custom_test_ranges(self.current_test_type_id)
                for range_data in existing_ranges:
                    if len(range_data) >= 6:
                        range_gender = range_data[5] if len(range_data) > 5 else None
                        if range_gender and range_gender.lower() in ['male', 'female']:
                            # This is a gender-specific range, remove it
                            range_id = range_data[0]
                            self.db_manager.delete_custom_test_range(range_id)
            except Exception as e:
                print(f"Warning: Could not remove existing gender ranges: {e}")
            
            # Add new gender-specific ranges if enabled
            if self.test_form_vars['gender_specific'].get():
                # Add male ranges
                if test_data['male_min'] and test_data['male_max']:
                    self.db_manager.add_custom_test_range(
                        self.current_test_type_id, f"Male-specific range for {test_data['test_name']}",
                        gender='Male',
                        normal_min=float(test_data['male_min']), 
                        normal_max=float(test_data['male_max'])
                    )
                
                # Add female ranges
                if test_data['female_min'] and test_data['female_max']:
                    self.db_manager.add_custom_test_range(
                        self.current_test_type_id, f"Female-specific range for {test_data['test_name']}",
                        gender='Female',
                        normal_min=float(test_data['female_min']), 
                        normal_max=float(test_data['female_max'])
                    )
            
            messagebox.showinfo("Success", f"Test type '{test_data['test_name']}' updated successfully!")
            
            # Force refresh by clearing the current selection first
            self.current_test_type_id = None
            
            # Small delay to ensure database transaction is complete
            self.parent.after(100, self.refresh_test_types)  # Refresh after a short delay
            self.clear_comprehensive_form()  # Then clear form
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update test type: {str(e)}")

    def validate_comprehensive_form(self, update=False):
        """Validate the comprehensive test form"""
        if not self.test_form_vars['test_name'].get().strip():
            messagebox.showerror("Error", "Test name is required.")
            return False
            
        # Validate numeric fields
        numeric_fields = ['normal_min', 'normal_max', 'critical_low', 'critical_high',
                         'male_min', 'male_max', 'female_min', 'female_max']
        
        numeric_values = {}
        for field in numeric_fields:
            value = self.test_form_vars[field].get().strip()
            if value:
                try:
                    numeric_values[field] = float(value)
                except ValueError:
                    messagebox.showerror("Error", f"{field.replace('_', ' ').title()} must be a valid number.")
                    return False
            else:
                numeric_values[field] = None
        
        # Validate normal range logic
        if numeric_values['normal_min'] is not None and numeric_values['normal_max'] is not None:
            if numeric_values['normal_min'] >= numeric_values['normal_max']:
                messagebox.showerror("Error", "Normal minimum must be less than normal maximum.")
                return False
        
        # Validate critical threshold logic
        if numeric_values['critical_low'] is not None and numeric_values['critical_high'] is not None:
            if numeric_values['critical_low'] >= numeric_values['critical_high']:
                messagebox.showerror("Error", "Critical low must be less than critical high.")
                return False
        
        # Validate critical thresholds relative to normal range
        if numeric_values['normal_min'] is not None and numeric_values['critical_low'] is not None:
            if numeric_values['critical_low'] > numeric_values['normal_min']:
                messagebox.showerror("Error", "Critical low should be below normal minimum.")
                return False
                
        if numeric_values['normal_max'] is not None and numeric_values['critical_high'] is not None:
            if numeric_values['critical_high'] < numeric_values['normal_max']:
                messagebox.showerror("Error", "Critical high should be above normal maximum.")
                return False
        
        # Validate gender-specific ranges if enabled
        if self.test_form_vars['gender_specific'].get():
            # Male range validation
            if numeric_values['male_min'] is not None and numeric_values['male_max'] is not None:
                if numeric_values['male_min'] >= numeric_values['male_max']:
                    messagebox.showerror("Error", "Male minimum must be less than male maximum.")
                    return False
            
            # Female range validation
            if numeric_values['female_min'] is not None and numeric_values['female_max'] is not None:
                if numeric_values['female_min'] >= numeric_values['female_max']:
                    messagebox.showerror("Error", "Female minimum must be less than female maximum.")
                    return False
                    
            # Ensure at least one gender range is provided
            male_provided = numeric_values['male_min'] is not None and numeric_values['male_max'] is not None
            female_provided = numeric_values['female_min'] is not None and numeric_values['female_max'] is not None
            
            if not male_provided and not female_provided:
                messagebox.showerror("Error", "When gender-specific is enabled, provide at least one complete gender range.")
                return False
        
        return True

    def clear_comprehensive_form(self):
        """Clear all form fields"""
        for var in self.test_form_vars.values():
            if isinstance(var, tk.BooleanVar):
                var.set(False)
            else:
                var.set('')
        self.current_test_type_id = None
        
        # Disable gender-specific fields
        if hasattr(self, 'gender_entries'):
            for entry in self.gender_entries:
                entry.configure(state='disabled')

    def on_comprehensive_test_select(self, event=None):
        """Handle test type selection from the comprehensive tree"""
        selection = self.test_tree.selection()
        if selection:
            item = self.test_tree.item(selection[0])
            values = item['values']
            if values:
                self.current_test_type_id = values[0]
                test_type = self.db_manager.get_test_type(self.current_test_type_id)
                if test_type:
                    self.populate_comprehensive_form(test_type)

    def populate_comprehensive_form(self, test_type):
        """Populate form with test type data"""
        # Correct indices: (test_type_id, test_name, normal_min, normal_max, unit, description, category, critical_low, critical_high, method)
        self.test_form_vars['test_name'].set(test_type[1] or '')
        self.test_form_vars['unit'].set(test_type[4] or '')  # unit at index 4
        
        # Handle critical thresholds (indices 7 and 8)
        self.test_form_vars['critical_low'].set(test_type[7] if len(test_type) > 7 and test_type[7] is not None else '')
        self.test_form_vars['critical_high'].set(test_type[8] if len(test_type) > 8 and test_type[8] is not None else '')
        
        # Handle method field (index 9)
        if 'method' in self.test_form_vars:
            self.test_form_vars['method'].set(test_type[9] if len(test_type) > 9 and test_type[9] else '')
        
        # Load gender-specific ranges if they exist
        try:
            gender_ranges = self.db_manager.get_custom_test_ranges(test_type[0])
            has_gender_ranges = False
            male_min = None
            male_max = None
            female_min = None
            female_max = None
            
            for range_data in gender_ranges:
                # range_data structure: (id, test_type_id, range_name, age_min, age_max, gender, condition_name, normal_min, normal_max, ...)
                if len(range_data) >= 9:
                    range_gender = range_data[5] if len(range_data) > 5 else None
                    range_min = range_data[7] if len(range_data) > 7 else None  # normal_min at index 7
                    range_max = range_data[8] if len(range_data) > 8 else None  # normal_max at index 8
                    
                    if range_gender and range_min is not None and range_max is not None:
                        has_gender_ranges = True
                        if range_gender.lower() == 'male':
                            male_min = range_min
                            male_max = range_max
                        elif range_gender.lower() == 'female':
                            female_min = range_min
                            female_max = range_max
            
            # If we have gender-specific ranges, prioritize them over base ranges
            if has_gender_ranges:
                # Set gender-specific range values
                self.test_form_vars['male_min'].set(male_min if male_min is not None else '')
                self.test_form_vars['male_max'].set(male_max if male_max is not None else '')
                self.test_form_vars['female_min'].set(female_min if female_min is not None else '')
                self.test_form_vars['female_max'].set(female_max if female_max is not None else '')
                
                # For display purposes, clear the default normal ranges when gender-specific ranges exist
                self.test_form_vars['normal_min'].set('')
                self.test_form_vars['normal_max'].set('')
            else:
                # Use base normal ranges if no gender-specific ranges exist
                self.test_form_vars['normal_min'].set(test_type[2] if test_type[2] is not None else '')  # normal_min at index 2
                self.test_form_vars['normal_max'].set(test_type[3] if test_type[3] is not None else '')  # normal_max at index 3
                
                # Clear gender-specific fields if no ranges found
                self.test_form_vars['male_min'].set('')
                self.test_form_vars['male_max'].set('')
                self.test_form_vars['female_min'].set('')
                self.test_form_vars['female_max'].set('')
                
        except Exception as e:
            has_gender_ranges = False
            # Use base normal ranges on error
            self.test_form_vars['normal_min'].set(test_type[2] if test_type[2] is not None else '')
            self.test_form_vars['normal_max'].set(test_type[3] if test_type[3] is not None else '')
            
            # Clear gender-specific fields on error
            self.test_form_vars['male_min'].set('')
            self.test_form_vars['male_max'].set('')
            self.test_form_vars['female_min'].set('')
            self.test_form_vars['female_max'].set('')
        
        # Set gender specific checkbox and enable/disable fields accordingly
        self.test_form_vars['gender_specific'].set(has_gender_ranges)
        self.toggle_gender_fields()

    # Test Type Management Methods
    def add_test_type(self):
        """Add a new test type - redirect to comprehensive method"""
        self.add_comprehensive_test_type()

    def update_test_type(self):
        """Update existing test type - redirect to comprehensive method"""
        self.update_comprehensive_test_type()

    def delete_test_type(self):
        """Delete selected test type"""
        if not self.current_test_type_id:
            messagebox.showwarning("Warning", "Please select a test type to delete.")
            return
        
        test_name = self.test_form_vars['test_name'].get()
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete test type '{test_name}'?\n"
                              "This will also delete all related test results and custom ranges."):
            success = self.db_manager.delete_test_type(self.current_test_type_id)
            
            if success:
                messagebox.showinfo("Success", "Test type deleted successfully!")
                self.clear_comprehensive_form()
                self.refresh_test_types()
            else:
                messagebox.showerror("Error", "Failed to delete test type.")
    
    def validate_test_form(self, update=False):
        """Validate test type form - redirect to comprehensive validation"""
        return self.validate_comprehensive_form(update)

    def clear_test_form(self):
        """Clear test type form - redirect to comprehensive form"""
        self.clear_comprehensive_form()
    
    def refresh_test_types(self):
        """Refresh test types display with comprehensive data"""
        # Clear existing items
        for item in self.test_tree.get_children():
            self.test_tree.delete(item)
        
        # Get test types
        test_types = self.db_manager.get_test_types()
        
        for test_type in test_types:
            # Handle the database return format: (test_type_id, test_name, normal_min, normal_max, unit, description, category, critical_low, critical_high, method)
            test_id = test_type[0] if len(test_type) > 0 else None
            name = test_type[1] if len(test_type) > 1 else 'Unknown'
            normal_min = test_type[2] if len(test_type) > 2 else None
            normal_max = test_type[3] if len(test_type) > 3 else None
            unit = test_type[4] if len(test_type) > 4 else 'N/A'
            description = test_type[5] if len(test_type) > 5 else ''
            category = test_type[6] if len(test_type) > 6 else 'N/A'
            critical_low = test_type[7] if len(test_type) > 7 else None
            critical_high = test_type[8] if len(test_type) > 8 else None
            method = test_type[9] if len(test_type) > 9 else 'Standard Method'
            
            # Check for gender-specific ranges and format accordingly
            try:
                gender_ranges = self.db_manager.get_custom_test_ranges(test_id)
                has_gender_specific = False
                male_range = None
                female_range = None
                
                for range_data in gender_ranges:
                    # range_data structure: (range_id, test_type_id, range_name, age_min, age_max, gender, condition_name, normal_min, normal_max, ...)
                    if len(range_data) >= 9:
                        range_gender = range_data[5] if len(range_data) > 5 else None
                        range_min = range_data[7] if len(range_data) > 7 else None  # normal_min at index 7
                        range_max = range_data[8] if len(range_data) > 8 else None  # normal_max at index 8
                        
                        if range_gender and range_min is not None and range_max is not None:
                            has_gender_specific = True
                            if range_gender.lower() == 'male':
                                male_range = f"{range_min} - {range_max}"
                            elif range_gender.lower() == 'female':
                                female_range = f"{range_min} - {range_max}"
                
                # Format the range display
                if has_gender_specific:
                    range_parts = []
                    if male_range:
                        range_parts.append(f"M: {male_range}")
                    if female_range:
                        range_parts.append(f"F: {female_range}")
                    normal_range = " | ".join(range_parts) if range_parts else f"{normal_min or 'N/A'} - {normal_max or 'N/A'}"
                    gender_specific_text = "Yes"
                else:
                    normal_range = f"{normal_min or 'N/A'} - {normal_max or 'N/A'}"
                    gender_specific_text = "No"
                    
            except Exception as e:
                # Fallback to default range if there's an error
                normal_range = f"{normal_min or 'N/A'} - {normal_max or 'N/A'}"
                gender_specific_text = "No"
            
            # Format critical range
            critical_range = f"{critical_low or 'N/A'} - {critical_high or 'N/A'}"
            
            self.test_tree.insert('', 'end', values=(
                test_id, name, unit or 'N/A', 
                normal_range, critical_range, method or 'Standard Method', gender_specific_text
            ))
    
    def search_test_types(self, event=None):
        """Search test types"""
        search_term = self.test_search_var.get().strip().lower()
        
        # Clear existing items
        for item in self.test_tree.get_children():
            self.test_tree.delete(item)
        
        # Get and filter test types
        test_types = self.db_manager.get_test_types()
        
        for test_type in test_types:
            # Handle the database return format: (test_type_id, test_name, normal_min, normal_max, unit, description, category, critical_low, critical_high, method)
            test_id = test_type[0] if len(test_type) > 0 else None
            name = test_type[1] if len(test_type) > 1 else 'Unknown'
            normal_min = test_type[2] if len(test_type) > 2 else None
            normal_max = test_type[3] if len(test_type) > 3 else None
            unit = test_type[4] if len(test_type) > 4 else 'N/A'
            description = test_type[5] if len(test_type) > 5 else ''
            category = test_type[6] if len(test_type) > 6 else 'N/A'
            critical_low = test_type[7] if len(test_type) > 7 else None
            critical_high = test_type[8] if len(test_type) > 8 else None
            method = test_type[9] if len(test_type) > 9 else 'Standard Method'
            
            # Check if search term matches (include method in search)
            if (search_term in name.lower() or 
                search_term in (unit or '').lower() or
                search_term in (method or '').lower()):
                
                # Check for gender-specific ranges and format accordingly
                try:
                    gender_ranges = self.db_manager.get_custom_test_ranges(test_id)
                    has_gender_specific = False
                    male_range = None
                    female_range = None
                    
                    for range_data in gender_ranges:
                        # range_data structure: (range_id, test_type_id, range_name, age_min, age_max, gender, condition_name, normal_min, normal_max, ...)
                        if len(range_data) >= 9:
                            range_gender = range_data[5] if len(range_data) > 5 else None
                            range_min = range_data[7] if len(range_data) > 7 else None  # normal_min at index 7
                            range_max = range_data[8] if len(range_data) > 8 else None  # normal_max at index 8
                            
                            if range_gender and range_min is not None and range_max is not None:
                                has_gender_specific = True
                                if range_gender.lower() == 'male':
                                    male_range = f"{range_min} - {range_max}"
                                elif range_gender.lower() == 'female':
                                    female_range = f"{range_min} - {range_max}"
                    
                    # Format the range display
                    if has_gender_specific:
                        range_parts = []
                        if male_range:
                            range_parts.append(f"M: {male_range}")
                        if female_range:
                            range_parts.append(f"F: {female_range}")
                        normal_range = " | ".join(range_parts) if range_parts else f"{normal_min or 'N/A'} - {normal_max or 'N/A'}"
                        gender_specific_text = "Yes"
                    else:
                        normal_range = f"{normal_min or 'N/A'} - {normal_max or 'N/A'}"
                        gender_specific_text = "No"
                        
                except Exception as e:
                    # Fallback to default range if there's an error
                    normal_range = f"{normal_min or 'N/A'} - {normal_max or 'N/A'}"
                    gender_specific_text = "No"
                
                # Format critical range
                critical_range = f"{critical_low or 'N/A'} - {critical_high or 'N/A'}"
                
                self.test_tree.insert('', 'end', values=(
                    test_id, name, unit or 'N/A',
                    normal_range, critical_range, method or 'Standard Method', gender_specific_text
                ))
    
    def on_test_type_select(self, event=None):
        """Handle test type selection - redirect to comprehensive method"""
        self.on_comprehensive_test_select(event)

    def populate_test_form(self, test_type):
        """Populate test type form - redirect to comprehensive method"""
        self.populate_comprehensive_form(test_type)
    
    # Custom Range Methods
    def add_custom_range(self):
        """Add custom range configuration"""
        if not self.range_test_var.get():
            messagebox.showwarning("Warning", "Please select a test type first.")
            return
        
        if not self.validate_range_form():
            return
        
        # Implementation for adding custom ranges
        messagebox.showinfo("Info", "Custom range functionality will be implemented.")
    
    def update_custom_range(self):
        """Update custom range configuration"""
        messagebox.showinfo("Info", "Update custom range functionality will be implemented.")
    
    def delete_custom_range(self):
        """Delete custom range configuration"""
        messagebox.showinfo("Info", "Delete custom range functionality will be implemented.")
    
    def validate_range_form(self):
        """Validate range form"""
        required_fields = ['normal_min', 'normal_max']
        
        for field in required_fields:
            if not self.range_form_vars[field].get().strip():
                messagebox.showerror("Validation Error", f"{field.replace('_', ' ').title()} is required.")
                return False
        
        try:
            float(self.range_form_vars['normal_min'].get())
            float(self.range_form_vars['normal_max'].get())
        except ValueError:
            messagebox.showerror("Validation Error", "Normal min and max must be numbers.")
            return False
        
        return True
    
    def clear_range_form(self):
        """Clear range form"""
        for var in self.range_form_vars.values():
            var.set('')
    
    def load_custom_ranges(self):
        """Load custom ranges for selected test"""
        messagebox.showinfo("Info", "Load custom ranges functionality will be implemented.")
    
    def on_range_test_select(self, event=None):
        """Handle test selection for range configuration"""
        self.load_custom_ranges()
    
    def on_condition_type_change(self, event=None):
        """Handle condition type change"""
        condition_type = self.range_form_vars['condition_type'].get()
        
        # Update condition value options based on type
        if condition_type == 'Gender':
            self.range_form_vars['condition_value'].set('Gender-based range')
        elif condition_type == 'Age Group':
            self.range_form_vars['condition_value'].set('Age-based range')
        elif condition_type == 'Age + Gender':
            self.range_form_vars['condition_value'].set('Age and gender specific')
        else:
            self.range_form_vars['condition_value'].set('')
    
    def on_range_select(self, event=None):
        """Handle range selection"""
        messagebox.showinfo("Info", "Range selection functionality will be implemented.")
    
    # Critical Thresholds Methods
    def save_critical_thresholds(self):
        """Save critical thresholds configuration"""
        if not self.critical_test_var.get():
            messagebox.showwarning("Warning", "Please select a test type first.")
            return
        
        test_name = self.critical_test_var.get()
        test_type = self.db_manager.get_test_type_by_name(test_name)
        if not test_type:
            messagebox.showerror("Error", "Test type not found.")
            return
        
        test_type_id = test_type[0]
        
        # Get threshold values
        critical_low = self.critical_form_vars['critical_low'].get().strip()
        critical_high = self.critical_form_vars['critical_high'].get().strip()
        
        # Convert to float if provided
        try:
            critical_low = float(critical_low) if critical_low else None
            critical_high = float(critical_high) if critical_high else None
        except ValueError:
            messagebox.showerror("Error", "Critical thresholds must be valid numbers.")
            return
        
        # Update test type with critical thresholds
        success = self.db_manager.update_test_type(
            test_type_id=test_type_id,
            critical_low=critical_low,
            critical_high=critical_high
        )
        
        if success:
            messagebox.showinfo("Success", "Critical thresholds saved successfully!")
            self.refresh_test_types()
        else:
            messagebox.showerror("Error", "Failed to save critical thresholds.")
    
    def load_default_thresholds(self):
        """Load default critical thresholds based on normal ranges"""
        if not self.critical_test_var.get():
            messagebox.showwarning("Warning", "Please select a test type first.")
            return
        
        test_name = self.critical_test_var.get()
        test_type = self.db_manager.get_test_type_by_name(test_name)
        if not test_type:
            messagebox.showerror("Error", "Test type not found.")
            return
        
        # Calculate default thresholds (30% beyond normal range)
        normal_min = test_type[4] if test_type[4] is not None else 0
        normal_max = test_type[5] if test_type[5] is not None else 100
        
        if normal_min is not None and normal_max is not None:
            range_width = normal_max - normal_min
            default_critical_low = normal_min - (range_width * 0.3)
            default_critical_high = normal_max + (range_width * 0.3)
            
            self.critical_form_vars['critical_low'].set(f"{default_critical_low:.2f}")
            self.critical_form_vars['critical_high'].set(f"{default_critical_high:.2f}")
            
            messagebox.showinfo("Success", "Default critical thresholds loaded!")
        else:
            messagebox.showwarning("Warning", "Cannot calculate defaults - normal range not defined.")
    
    def clear_critical_form(self):
        """Clear critical thresholds form"""
        for var in self.critical_form_vars.values():
            var.set('')
    
    def on_critical_test_select(self, event=None):
        """Handle test selection for critical thresholds"""
        test_name = self.critical_test_var.get()
        if not test_name:
            return
        
        test_type = self.db_manager.get_test_type_by_name(test_name)
        if test_type and len(test_type) > 8:
            # Load existing critical thresholds if they exist
            critical_low = test_type[7] if len(test_type) > 7 else None
            critical_high = test_type[8] if len(test_type) > 8 else None
            
            if critical_low is not None:
                self.critical_form_vars['critical_low'].set(str(critical_low))
            if critical_high is not None:
                self.critical_form_vars['critical_high'].set(str(critical_high))
