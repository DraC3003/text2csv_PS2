"""
Test Type Management UI Component
Interface for managing medical test types and their normal ranges.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

class TestTypeManagementFrame:
    def __init__(self, parent, db_manager):
        """Initialize test type management interface"""
        self.parent = parent
        self.db_manager = db_manager
        self.current_test_type_id = None
        
        self.setup_ui()
        self.refresh_test_types()
        
    def setup_ui(self):
        """Setup the test type management UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Test Type Management", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create two columns: form and list
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)
        
        # Left side - Test type form
        form_frame = ttk.LabelFrame(content_frame, text="Test Type Information")
        form_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Form fields
        self.form_vars = {}
        fields = [
            ('test_name', 'Test Name*', 'entry'),
            ('description', 'Description', 'entry'),
            ('unit', 'Unit', 'entry'),
            ('normal_min', 'Normal Range - Minimum', 'entry'),
            ('normal_max', 'Normal Range - Maximum', 'entry'),
            ('category', 'Category', 'combo')
        ]
        
        for i, (field_name, label_text, field_type) in enumerate(fields):
            # Label
            label = ttk.Label(form_frame, text=label_text)
            label.grid(row=i, column=0, sticky='w', padx=5, pady=5)
            
            # Field
            if field_type == 'entry':
                var = tk.StringVar()
                entry = ttk.Entry(form_frame, textvariable=var, width=30)
                entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
                self.form_vars[field_name] = var
            elif field_type == 'combo':
                var = tk.StringVar()
                combo = ttk.Combobox(form_frame, textvariable=var, width=27, state='readonly')
                combo['values'] = ['Blood Chemistry', 'Hematology', 'Immunology', 'Microbiology', 'Endocrinology', 'Other']
                combo.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
                self.form_vars[field_name] = var
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add Test Type", command=self.add_test_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Test Type", command=self.update_test_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Test Type", command=self.delete_test_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side='left', padx=5)
        
        # Right side - Test type list
        list_frame = ttk.LabelFrame(content_frame, text="Test Types")
        list_frame.pack(side='right', fill='both', expand=True)
        
        # Search
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        search_entry.bind('<KeyRelease>', self.search_test_types)
        
        # Test type treeview
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('Name', 'Unit', 'Min', 'Max', 'Category')
        self.test_types_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.test_types_tree.heading(col, text=col)
            self.test_types_tree.column(col, width=80)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.test_types_tree.yview)
        self.test_types_tree.configure(yscrollcommand=scrollbar.set)
        
        self.test_types_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.test_types_tree.bind('<<TreeviewSelect>>', self.on_test_type_select)
    
    def add_test_type(self):
        """Add a new test type"""
        if not self.validate_form():
            return
        
        test_name = self.form_vars['test_name'].get().strip()
        description = self.form_vars['description'].get().strip()
        unit = self.form_vars['unit'].get().strip()
        category = self.form_vars['category'].get().strip()
        
        # Handle numeric fields
        try:
            normal_min = float(self.form_vars['normal_min'].get()) if self.form_vars['normal_min'].get().strip() else None
            normal_max = float(self.form_vars['normal_max'].get()) if self.form_vars['normal_max'].get().strip() else None
        except ValueError:
            messagebox.showerror("Validation Error", "Normal range values must be numeric.")
            return
        
        success = self.db_manager.add_test_type(
            test_name=test_name,
            description=description,
            unit=unit,
            normal_min=normal_min,
            normal_max=normal_max,
            category=category
        )
        
        if success:
            messagebox.showinfo("Success", "Test type added successfully!")
            self.clear_form()
            self.refresh_test_types()
        else:
            messagebox.showerror("Error", "Failed to add test type. Test name may already exist.")
    
    def update_test_type(self):
        """Update existing test type"""
        if not self.current_test_type_id:
            messagebox.showwarning("Warning", "Please select a test type to update.")
            return
        
        if not self.validate_form(update=True):
            return
        
        description = self.form_vars['description'].get().strip()
        unit = self.form_vars['unit'].get().strip()
        category = self.form_vars['category'].get().strip()
        
        # Handle numeric fields
        try:
            normal_min = float(self.form_vars['normal_min'].get()) if self.form_vars['normal_min'].get().strip() else None
            normal_max = float(self.form_vars['normal_max'].get()) if self.form_vars['normal_max'].get().strip() else None
        except ValueError:
            messagebox.showerror("Validation Error", "Normal range values must be numeric.")
            return
        
        success = self.db_manager.update_test_type(
            test_type_id=self.current_test_type_id,
            description=description,
            unit=unit,
            normal_min=normal_min,
            normal_max=normal_max,
            category=category
        )
        
        if success:
            messagebox.showinfo("Success", "Test type updated successfully!")
            self.refresh_test_types()
        else:
            messagebox.showerror("Error", "Failed to update test type.")
    
    def delete_test_type(self):
        """Delete selected test type"""
        if not self.current_test_type_id:
            messagebox.showwarning("Warning", "Please select a test type to delete.")
            return
        
        test_name = self.form_vars['test_name'].get()
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete test type '{test_name}'?\n"
                              "This will also delete all associated test results."):
            success = self.db_manager.delete_test_type(self.current_test_type_id)
            
            if success:
                messagebox.showinfo("Success", "Test type deleted successfully!")
                self.clear_form()
                self.refresh_test_types()
            else:
                messagebox.showerror("Error", "Failed to delete test type.")
    
    def validate_form(self, update=False):
        """Validate form data"""
        required_fields = ['test_name'] if not update else []
        
        for field in required_fields:
            if not self.form_vars[field].get().strip():
                messagebox.showerror("Validation Error", f"{field.replace('_', ' ').title()} is required.")
                return False
        
        # Validate normal range
        min_val = self.form_vars['normal_min'].get().strip()
        max_val = self.form_vars['normal_max'].get().strip()
        
        if min_val and max_val:
            try:
                min_float = float(min_val)
                max_float = float(max_val)
                if min_float >= max_float:
                    messagebox.showerror("Validation Error", "Normal minimum must be less than normal maximum.")
                    return False
            except ValueError:
                messagebox.showerror("Validation Error", "Normal range values must be numeric.")
                return False
        
        return True
    
    def clear_form(self):
        """Clear all form fields"""
        for var in self.form_vars.values():
            var.set('')
        self.current_test_type_id = None
    
    def refresh_test_types(self):
        """Refresh the test types list"""
        # Clear existing items
        for item in self.test_types_tree.get_children():
            self.test_types_tree.delete(item)
        
        # Get all test types
        test_types = self.db_manager.get_test_types()
        
        for test_type in test_types:
            test_type_id, test_name, description, category, normal_min, normal_max, unit = test_type
            
            # Format display values
            min_display = f"{normal_min:.1f}" if normal_min is not None else ""
            max_display = f"{normal_max:.1f}" if normal_max is not None else ""
            unit_display = unit or ""
            category_display = category or ""
            
            self.test_types_tree.insert('', 'end', values=(
                test_name,
                unit_display,
                min_display,
                max_display,
                category_display
            ), tags=(test_type_id,))
    
    def search_test_types(self, event=None):
        """Search test types based on search term"""
        search_term = self.search_var.get().strip().lower()
        
        # Clear existing items
        for item in self.test_types_tree.get_children():
            self.test_types_tree.delete(item)
        
        # Get all test types and filter
        test_types = self.db_manager.get_test_types()
        
        for test_type in test_types:
            test_type_id, test_name, description, category, normal_min, normal_max, unit = test_type
            
            # Check if search term matches any field
            if (not search_term or 
                search_term in test_name.lower() or 
                (description and search_term in description.lower()) or
                (category and search_term in category.lower()) or
                (unit and search_term in unit.lower())):
                
                # Format display values
                min_display = f"{normal_min:.1f}" if normal_min is not None else ""
                max_display = f"{normal_max:.1f}" if normal_max is not None else ""
                unit_display = unit or ""
                category_display = category or ""
                
                self.test_types_tree.insert('', 'end', values=(
                    test_name,
                    unit_display,
                    min_display,
                    max_display,
                    category_display
                ), tags=(test_type_id,))
    
    def on_test_type_select(self, event=None):
        """Handle test type selection from tree"""
        selection = self.test_types_tree.selection()
        if selection:
            item = selection[0]
            test_type_id = self.test_types_tree.item(item)['tags'][0]
            
            # Get full test type information
            test_type_info = self.db_manager.get_test_type(test_type_id)
            if test_type_info:
                self.current_test_type_id = test_type_id
                self.populate_form(test_type_info)
    
    def populate_form(self, test_type_info):
        """Populate form with test type information"""
        test_type_id, test_name, description, category, normal_min, normal_max, unit = test_type_info
        
        field_mapping = {
            'test_name': test_name,
            'description': description or '',
            'unit': unit or '',
            'normal_min': str(normal_min) if normal_min is not None else '',
            'normal_max': str(normal_max) if normal_max is not None else '',
            'category': category or ''
        }
        
        for field, value in field_mapping.items():
            if field in self.form_vars:
                self.form_vars[field].set(value)
