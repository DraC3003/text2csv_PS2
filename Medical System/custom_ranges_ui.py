"""
Custom Test Ranges Management UI
Allows healthcare professionals to create and manage custom normal ranges for tests.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from typing import Optional

class CustomRangesForm:
    def __init__(self, parent, db_manager):
        """Initialize custom ranges management form"""
        self.parent = parent
        self.db_manager = db_manager
        self.current_range_id = None
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Setup the custom ranges management UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Custom Test Ranges Management", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create paned window for split layout
        paned_window = ttk.PanedWindow(main_frame, orient='horizontal')
        paned_window.pack(fill='both', expand=True)
        
        # Left side - Range list and import/export
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # Right side - Range editor
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)
        
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)
    
    def setup_left_panel(self, parent):
        """Setup the left panel with range list and controls"""
        # Controls section
        controls_frame = ttk.LabelFrame(parent, text="Range Management")
        controls_frame.pack(fill='x', padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="New Range", command=self.new_range).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Delete", command=self.delete_range).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_ranges_list).pack(side='left', padx=2)
        
        # Import/Export section
        io_frame = ttk.LabelFrame(parent, text="Import/Export")
        io_frame.pack(fill='x', padx=5, pady=5)
        
        io_button_frame = ttk.Frame(io_frame)
        io_button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(io_button_frame, text="Export to JSON", command=self.export_ranges).pack(side='left', padx=2)
        ttk.Button(io_button_frame, text="Import from JSON", command=self.import_ranges).pack(side='left', padx=2)
        
        # Ranges list
        list_frame = ttk.LabelFrame(parent, text="Custom Ranges")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview for ranges
        columns = ('Test', 'Range Name', 'Age', 'Gender', 'Condition')
        self.ranges_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.ranges_tree.heading(col, text=col)
            self.ranges_tree.column(col, width=80)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.ranges_tree.yview)
        self.ranges_tree.configure(yscrollcommand=scrollbar.set)
        
        self.ranges_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)
        
        self.ranges_tree.bind('<<TreeviewSelect>>', self.on_range_select)
    
    def setup_right_panel(self, parent):
        """Setup the right panel with range editor"""
        editor_frame = ttk.LabelFrame(parent, text="Range Editor")
        editor_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Form fields
        self.form_vars = {}
        
        # Test selection
        ttk.Label(editor_frame, text="Test Type:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.test_var = tk.StringVar()
        self.test_combo = ttk.Combobox(editor_frame, textvariable=self.test_var, width=30, state='readonly')
        self.test_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # Range name
        ttk.Label(editor_frame, text="Range Name:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.range_name_var = tk.StringVar()
        ttk.Entry(editor_frame, textvariable=self.range_name_var, width=30).grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        # Age range
        ttk.Label(editor_frame, text="Age Range:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        age_frame = ttk.Frame(editor_frame)
        age_frame.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        self.age_min_var = tk.StringVar()
        self.age_max_var = tk.StringVar()
        ttk.Entry(age_frame, textvariable=self.age_min_var, width=10).pack(side='left')
        ttk.Label(age_frame, text=" to ").pack(side='left')
        ttk.Entry(age_frame, textvariable=self.age_max_var, width=10).pack(side='left')
        ttk.Label(age_frame, text=" years (optional)").pack(side='left')
        
        # Gender
        ttk.Label(editor_frame, text="Gender:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(editor_frame, textvariable=self.gender_var, width=30, state='readonly')
        gender_combo['values'] = ['', 'Male', 'Female', 'Other']
        gender_combo.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        
        # Condition
        ttk.Label(editor_frame, text="Condition:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.condition_var = tk.StringVar()
        ttk.Entry(editor_frame, textvariable=self.condition_var, width=30).grid(row=4, column=1, sticky='ew', padx=5, pady=5)
        
        # Normal range
        ttk.Label(editor_frame, text="Normal Range:").grid(row=5, column=0, sticky='w', padx=5, pady=5)
        normal_frame = ttk.Frame(editor_frame)
        normal_frame.grid(row=5, column=1, sticky='ew', padx=5, pady=5)
        
        self.normal_min_var = tk.StringVar()
        self.normal_max_var = tk.StringVar()
        ttk.Entry(normal_frame, textvariable=self.normal_min_var, width=10).pack(side='left')
        ttk.Label(normal_frame, text=" to ").pack(side='left')
        ttk.Entry(normal_frame, textvariable=self.normal_max_var, width=10).pack(side='left')
        
        # Critical thresholds
        ttk.Label(editor_frame, text="Critical Low:").grid(row=6, column=0, sticky='w', padx=5, pady=5)
        self.critical_low_var = tk.StringVar()
        ttk.Entry(editor_frame, textvariable=self.critical_low_var, width=30).grid(row=6, column=1, sticky='ew', padx=5, pady=5)
        
        ttk.Label(editor_frame, text="Critical High:").grid(row=7, column=0, sticky='w', padx=5, pady=5)
        self.critical_high_var = tk.StringVar()
        ttk.Entry(editor_frame, textvariable=self.critical_high_var, width=30).grid(row=7, column=1, sticky='ew', padx=5, pady=5)
        
        # Notes
        ttk.Label(editor_frame, text="Notes:").grid(row=8, column=0, sticky='w', padx=5, pady=5)
        self.notes_var = tk.StringVar()
        ttk.Entry(editor_frame, textvariable=self.notes_var, width=30).grid(row=8, column=1, sticky='ew', padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(editor_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save Range", command=self.save_range).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side='left', padx=5)
        
        # Configure grid weights
        editor_frame.columnconfigure(1, weight=1)
    
    def refresh_data(self):
        """Refresh test types and ranges data"""
        # Refresh test types
        test_types = self.db_manager.get_test_types()
        test_type_list = [t[1] for t in test_types]  # test_name
        self.test_combo['values'] = test_type_list
        
        # Refresh ranges list
        self.refresh_ranges_list()
    
    def refresh_ranges_list(self):
        """Refresh the custom ranges list"""
        # Clear existing items
        for item in self.ranges_tree.get_children():
            self.ranges_tree.delete(item)
        
        # Get all custom ranges
        ranges = self.db_manager.get_custom_test_ranges()
        
        for range_data in ranges:
            range_id, test_type_id, range_name, age_min, age_max, gender, condition_name, \
            normal_min, normal_max, critical_low, critical_high, is_active, created_date, notes, test_name = range_data
            
            # Format age range
            age_display = ""
            if age_min is not None or age_max is not None:
                if age_min is not None and age_max is not None:
                    age_display = f"{age_min}-{age_max}"
                elif age_min is not None:
                    age_display = f"{age_min}+"
                elif age_max is not None:
                    age_display = f"≤{age_max}"
            
            self.ranges_tree.insert('', 'end', values=(
                test_name,
                range_name,
                age_display,
                gender or '',
                condition_name or ''
            ), tags=(range_id,))
    
    def on_range_select(self, event=None):
        """Handle range selection from list"""
        selection = self.ranges_tree.selection()
        if selection:
            item = self.ranges_tree.item(selection[0])
            range_id = item['tags'][0] if item['tags'] else None
            
            if range_id:
                self.load_range(range_id)
    
    def load_range(self, range_id):
        """Load a range into the editor"""
        ranges = self.db_manager.get_custom_test_ranges()
        
        for range_data in ranges:
            if range_data[0] == range_id:  # range_id is first column
                self.current_range_id = range_id
                
                range_id, test_type_id, range_name, age_min, age_max, gender, condition_name, \
                normal_min, normal_max, critical_low, critical_high, is_active, created_date, notes, test_name = range_data
                
                # Populate form
                self.test_var.set(test_name)
                self.range_name_var.set(range_name or '')
                self.age_min_var.set(str(age_min) if age_min is not None else '')
                self.age_max_var.set(str(age_max) if age_max is not None else '')
                self.gender_var.set(gender or '')
                self.condition_var.set(condition_name or '')
                self.normal_min_var.set(str(normal_min) if normal_min is not None else '')
                self.normal_max_var.set(str(normal_max) if normal_max is not None else '')
                self.critical_low_var.set(str(critical_low) if critical_low is not None else '')
                self.critical_high_var.set(str(critical_high) if critical_high is not None else '')
                self.notes_var.set(notes or '')
                break
    
    def new_range(self):
        """Create a new range"""
        self.clear_form()
        self.current_range_id = None
    
    def clear_form(self):
        """Clear all form fields"""
        self.test_var.set('')
        self.range_name_var.set('')
        self.age_min_var.set('')
        self.age_max_var.set('')
        self.gender_var.set('')
        self.condition_var.set('')
        self.normal_min_var.set('')
        self.normal_max_var.set('')
        self.critical_low_var.set('')
        self.critical_high_var.set('')
        self.notes_var.set('')
        self.current_range_id = None
    
    def save_range(self):
        """Save the current range"""
        if not self.validate_form():
            return
        
        # Get test type ID
        test_name = self.test_var.get()
        test_type = self.db_manager.get_test_type_by_name(test_name)
        if not test_type:
            messagebox.showerror("Error", "Please select a valid test type.")
            return
        
        test_type_id = test_type[0]
        
        # Prepare data
        range_data = {
            'range_name': self.range_name_var.get().strip(),
            'age_min': int(self.age_min_var.get()) if self.age_min_var.get().strip() else None,
            'age_max': int(self.age_max_var.get()) if self.age_max_var.get().strip() else None,
            'gender': self.gender_var.get().strip() or None,
            'condition_name': self.condition_var.get().strip() or None,
            'normal_min': float(self.normal_min_var.get()) if self.normal_min_var.get().strip() else None,
            'normal_max': float(self.normal_max_var.get()) if self.normal_max_var.get().strip() else None,
            'critical_low': float(self.critical_low_var.get()) if self.critical_low_var.get().strip() else None,
            'critical_high': float(self.critical_high_var.get()) if self.critical_high_var.get().strip() else None,
            'notes': self.notes_var.get().strip() or None
        }
        
        if self.current_range_id:
            # Update existing range
            success = self.db_manager.update_custom_test_range(self.current_range_id, **range_data)
            action = "updated"
        else:
            # Create new range
            success = self.db_manager.add_custom_test_range(test_type_id, **range_data)
            action = "created"
        
        if success:
            messagebox.showinfo("Success", f"Custom range {action} successfully!")
            self.clear_form()
            self.refresh_ranges_list()
        else:
            messagebox.showerror("Error", f"Failed to {action.split()[0]} custom range.")
    
    def delete_range(self):
        """Delete the selected range"""
        selection = self.ranges_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a range to delete.")
            return
        
        item = self.ranges_tree.item(selection[0])
        range_id = item['tags'][0] if item['tags'] else None
        
        if range_id and messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this custom range?"):
            success = self.db_manager.delete_custom_test_range(range_id)
            
            if success:
                messagebox.showinfo("Success", "Custom range deleted successfully!")
                self.clear_form()
                self.refresh_ranges_list()
            else:
                messagebox.showerror("Error", "Failed to delete custom range.")
    
    def validate_form(self):
        """Validate form data"""
        if not self.test_var.get():
            messagebox.showerror("Validation Error", "Please select a test type.")
            return False
        
        if not self.range_name_var.get().strip():
            messagebox.showerror("Validation Error", "Please enter a range name.")
            return False
        
        # Validate numeric fields
        numeric_fields = [
            (self.age_min_var, "Age Min"),
            (self.age_max_var, "Age Max"),
            (self.normal_min_var, "Normal Min"),
            (self.normal_max_var, "Normal Max"),
            (self.critical_low_var, "Critical Low"),
            (self.critical_high_var, "Critical High")
        ]
        
        for var, field_name in numeric_fields:
            value = var.get().strip()
            if value:
                try:
                    if "Age" in field_name:
                        int(value)
                    else:
                        float(value)
                except ValueError:
                    messagebox.showerror("Validation Error", f"{field_name} must be a valid number.")
                    return False
        
        # Validate age range
        age_min = self.age_min_var.get().strip()
        age_max = self.age_max_var.get().strip()
        if age_min and age_max:
            try:
                if int(age_min) >= int(age_max):
                    messagebox.showerror("Validation Error", "Age minimum must be less than age maximum.")
                    return False
            except ValueError:
                pass  # Already handled above
        
        # Validate normal range
        normal_min = self.normal_min_var.get().strip()
        normal_max = self.normal_max_var.get().strip()
        if normal_min and normal_max:
            try:
                if float(normal_min) >= float(normal_max):
                    messagebox.showerror("Validation Error", "Normal minimum must be less than normal maximum.")
                    return False
            except ValueError:
                pass  # Already handled above
        
        return True
    
    def export_ranges(self):
        """Export custom ranges to JSON"""
        file_path = filedialog.asksaveasfilename(
            title="Export Custom Ranges",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            success = self.db_manager.export_custom_ranges_to_json(file_path)
            if success:
                messagebox.showinfo("Success", f"Custom ranges exported to: {file_path}")
            else:
                messagebox.showerror("Error", "Failed to export custom ranges.")
    
    def import_ranges(self):
        """Import custom ranges from JSON"""
        file_path = filedialog.askopenfilename(
            title="Import Custom Ranges",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            if messagebox.askyesno("Confirm Import", 
                                  "This will add new custom ranges from the JSON file. Continue?"):
                success = self.db_manager.import_custom_ranges_from_json(file_path)
                if success:
                    messagebox.showinfo("Success", "Custom ranges imported successfully!")
                    self.refresh_ranges_list()
                else:
                    messagebox.showerror("Error", "Failed to import custom ranges.")
