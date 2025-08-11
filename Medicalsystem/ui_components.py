"""
UI Components for Medical Test System
Contains all user interface forms and widgets.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import re
from typing import Optional

class PatientForm:
    def __init__(self, parent, db_manager):
        """Initialize patient management form"""
        self.parent = parent
        self.db_manager = db_manager
        self.current_patient_id = None
        
        self.setup_ui()
        self.refresh_patient_list()
    
    def setup_ui(self):
        """Setup the patient management UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Patient Management", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create two columns: form and list
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)
        
        # Left side - Patient form
        form_frame = ttk.LabelFrame(content_frame, text="Patient Information")
        form_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Form fields
        self.form_vars = {}
        fields = [
            ('patient_id', 'Patient ID*', 'entry'),
            ('name', 'Full Name', 'entry'),
            ('age', 'Age (years) - Optional but recommended for accurate ranges', 'entry'),
            ('gender', 'Gender - Optional but recommended for accurate ranges', 'combo'),
            ('phone', 'Phone Number (Optional)', 'entry'),
            ('email', 'Email Address (Optional)', 'entry'),
            ('address', 'Address (Optional)', 'text')
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
                combo['values'] = ['Male', 'Female', 'Child', 'Baby', 'Other', 'Prefer not to say']
                combo.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
                self.form_vars[field_name] = var
            elif field_type == 'text':
                var = tk.StringVar()
                entry = ttk.Entry(form_frame, textvariable=var, width=30)
                entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
                self.form_vars[field_name] = var
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add Patient", command=self.add_patient).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Patient", command=self.update_patient).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Patient", command=self.delete_patient).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side='left', padx=5)
        
        # Right side - Patient list
        list_frame = ttk.LabelFrame(content_frame, text="Patient List")
        list_frame.pack(side='right', fill='both', expand=True)
        
        # Search
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        search_entry.bind('<KeyRelease>', self.search_patients)
        
        # Patient listbox
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.patient_listbox = tk.Listbox(listbox_frame, height=15)
        scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.patient_listbox.yview)
        self.patient_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.patient_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.patient_listbox.bind('<<ListboxSelect>>', self.on_patient_select)
    
    def add_patient(self):
        """Add a new patient"""
        if not self.validate_form():
            return
        
        patient_data = {key: var.get().strip() for key, var in self.form_vars.items()}
        
        # Split name into first_name and last_name for database compatibility
        if 'name' in patient_data and patient_data['name']:
            name_parts = patient_data['name'].split(' ', 1)
            patient_data['first_name'] = name_parts[0]
            patient_data['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
            del patient_data['name']
        
        # Remove empty optional fields
        patient_data = {k: v for k, v in patient_data.items() if v}
        
        success = self.db_manager.add_patient(**patient_data)
        
        if success:
            messagebox.showinfo("Success", "Patient added successfully!")
            self.clear_form()
            self.refresh_patient_list()
        else:
            messagebox.showerror("Error", "Failed to add patient. Patient ID may already exist.")
    
    def update_patient(self):
        """Update existing patient"""
        if not self.current_patient_id:
            messagebox.showwarning("Warning", "Please select a patient to update.")
            return
        
        if not self.validate_form(update=True):
            return
        
        patient_data = {key: var.get().strip() for key, var in self.form_vars.items() if key != 'patient_id'}
        
        # Split name into first_name and last_name for database compatibility
        if 'name' in patient_data and patient_data['name']:
            name_parts = patient_data['name'].split(' ', 1)
            patient_data['first_name'] = name_parts[0]
            patient_data['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
            del patient_data['name']
        
        patient_data = {k: v for k, v in patient_data.items() if v}
        
        success = self.db_manager.update_patient(self.current_patient_id, **patient_data)
        
        if success:
            messagebox.showinfo("Success", "Patient updated successfully!")
            self.refresh_patient_list()
        else:
            messagebox.showerror("Error", "Failed to update patient.")
    
    def delete_patient(self):
        """Delete selected patient"""
        if not self.current_patient_id:
            messagebox.showwarning("Warning", "Please select a patient to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete patient {self.current_patient_id}?\n"
                              "This will also delete all their test results."):
            success = self.db_manager.delete_patient(self.current_patient_id)
            
            if success:
                messagebox.showinfo("Success", "Patient deleted successfully!")
                self.clear_form()
                self.refresh_patient_list()
            else:
                messagebox.showerror("Error", "Failed to delete patient.")
    
    def validate_form(self, update=False):
        """Validate form data"""
        required_fields = ['patient_id'] if not update else []
        
        for field in required_fields:
            if not self.form_vars[field].get().strip():
                messagebox.showerror("Validation Error", f"{field.replace('_', ' ').title()} is required.")
                return False
        
        # Validate age format
        age = self.form_vars['age'].get().strip()
        if age:
            try:
                age_val = int(age)
                if age_val < 0 or age_val > 150:
                    messagebox.showerror("Validation Error", "Age must be between 0 and 150 years.")
                    return False
            except ValueError:
                messagebox.showerror("Validation Error", "Age must be a valid number.")
                return False
        
        # Validate email format
        email = self.form_vars['email'].get().strip()
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messagebox.showerror("Validation Error", "Please enter a valid email address.")
            return False
        
        return True
    
    def clear_form(self):
        """Clear all form fields"""
        for var in self.form_vars.values():
            var.set('')
        self.current_patient_id = None
    
    def refresh_patient_list(self):
        """Refresh the patient list"""
        self.patient_listbox.delete(0, tk.END)
        patients = self.db_manager.get_all_patients()
        
        for patient in patients:
            display_text = f"{patient[0]} - {patient[1]} {patient[2]}"
            self.patient_listbox.insert(tk.END, display_text)
    
    def search_patients(self, event=None):
        """Search patients based on search term"""
        search_term = self.search_var.get().strip()
        
        if search_term:
            patients = self.db_manager.search_patients(search_term)
        else:
            patients = self.db_manager.get_all_patients()
        
        self.patient_listbox.delete(0, tk.END)
        for patient in patients:
            display_text = f"{patient[0]} - {patient[1]} {patient[2]}"
            self.patient_listbox.insert(tk.END, display_text)
    
    def on_patient_select(self, event=None):
        """Handle patient selection from list"""
        selection = self.patient_listbox.curselection()
        if selection:
            selected_text = self.patient_listbox.get(selection[0])
            patient_id = selected_text.split(' - ')[0]
            
            patient_info = self.db_manager.get_patient(patient_id)
            if patient_info:
                self.current_patient_id = patient_id
                self.populate_form(patient_info)
    
    def populate_form(self, patient_info):
        """Populate form with patient information"""
        # Combine first_name and last_name into a single name field
        first_name = patient_info[1] or ''
        last_name = patient_info[2] or ''
        full_name = f"{first_name} {last_name}".strip()
        
        field_mapping = {
            'patient_id': patient_info[0],
            'name': full_name,
            'age': patient_info[9] if len(patient_info) > 9 and patient_info[9] is not None else '',
            'gender': patient_info[4] or '',
            'phone': patient_info[5] or '',
            'email': patient_info[6] or '',
            'address': patient_info[7] or ''
        }
        
        for field, value in field_mapping.items():
            if field in self.form_vars:
                # Handle phone number formatting
                if field == 'phone' and value:
                    # Convert phone to string without decimal if it's numeric
                    try:
                        # If it's a float, convert to int first to remove decimal
                        if isinstance(value, float):
                            value = str(int(value))
                        else:
                            value = str(value)
                    except (ValueError, TypeError):
                        value = str(value)
                else:
                    value = str(value)
                self.form_vars[field].set(value)


class TestResultForm:
    def __init__(self, parent, db_manager):
        """Initialize test result management form"""
        self.parent = parent
        self.db_manager = db_manager
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Setup the test result management UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Test Result Management", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Form section
        form_frame = ttk.LabelFrame(main_frame, text="Add Test Result")
        form_frame.pack(fill='x', pady=(0, 20))
        
        # Form fields
        self.form_vars = {}
        
        # Patient selection
        ttk.Label(form_frame, text="Patient:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.patient_var = tk.StringVar()
        self.patient_combo = ttk.Combobox(form_frame, textvariable=self.patient_var, width=40, state='readonly')
        self.patient_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # Test type selection
        ttk.Label(form_frame, text="Test Type:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.test_type_var = tk.StringVar()
        self.test_type_combo = ttk.Combobox(form_frame, textvariable=self.test_type_var, width=40, state='readonly')
        self.test_type_combo.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        # Test value
        ttk.Label(form_frame, text="Test Value:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.test_value_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.test_value_var, width=40).grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        # Test date
        ttk.Label(form_frame, text="Test Date (YYYY-MM-DD):").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.test_date_var = tk.StringVar()
        self.test_date_var.set(datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(form_frame, textvariable=self.test_date_var, width=40).grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        
        # Lab technician
        ttk.Label(form_frame, text="Lab Technician:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.lab_tech_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.lab_tech_var, width=40).grid(row=4, column=1, sticky='ew', padx=5, pady=5)
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=5, column=0, sticky='w', padx=5, pady=5)
        self.notes_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.notes_var, width=40).grid(row=5, column=1, sticky='ew', padx=5, pady=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add Test Result", command=self.add_test_result).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Refresh Data", command=self.refresh_data).pack(side='left', padx=5)
        
        # Results display section
        results_frame = ttk.LabelFrame(main_frame, text="All Test Results")
        results_frame.pack(fill='both', expand=True)
        
        # Critical alerts frame
        self.alerts_frame = ttk.Frame(results_frame)
        self.alerts_frame.pack(fill='x', padx=5, pady=5)
        
        self.alerts_label = ttk.Label(self.alerts_frame, text="", font=('Arial', 10, 'bold'))
        self.alerts_label.pack()
        
        # Treeview for results
        columns = ('ID', 'Patient', 'Test', 'Value', 'Unit', 'Date', 'Status')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10)
        
        # Configure color tags for critical values
        self.results_tree.tag_configure('critical', background='#ffcccc', foreground='red')  # Light red background
        self.results_tree.tag_configure('abnormal', background='#fff2cc', foreground='orange')  # Light yellow background
        self.results_tree.tag_configure('normal', background='#ccffcc', foreground='green')  # Light green background
        self.results_tree.tag_configure('unconfigured', background='#e6ccff', foreground='purple')  # Light purple background
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)
    
    def refresh_data(self):
        """Refresh patient and test type data"""
        # Refresh patients
        patients = self.db_manager.get_all_patients()
        patient_list = [f"{p[1]} {p[2]} (ID: {p[0]})" for p in patients]
        self.patient_combo['values'] = patient_list
        
        # Refresh test types
        test_types = self.db_manager.get_test_types()
        test_type_list = [f"{t[1]} ({t[4]} {t[5] or ''})" for t in test_types]
        self.test_type_combo['values'] = test_type_list
        
        # Refresh results display
        self.refresh_results_display()
    
    def add_test_result(self):
        """Add a new test result"""
        if not self.validate_test_form():
            return
        
        # Extract patient ID
        patient_text = self.patient_var.get()
        patient_id = patient_text.split("ID: ")[1].rstrip(")")
        
        # Extract test type ID
        test_type_text = self.test_type_var.get()
        test_type_name = test_type_text.split(" (")[0]
        test_type = self.db_manager.get_test_type_by_name(test_type_name)
        test_type_id = test_type[0]
        
        # Get form values
        test_value = float(self.test_value_var.get())
        test_date = self.test_date_var.get()
        lab_tech = self.lab_tech_var.get().strip() or None
        notes = self.notes_var.get().strip() or None
        
        success = self.db_manager.add_test_result(
            patient_id=patient_id,
            test_type_id=test_type_id,
            test_value=test_value,
            test_date=test_date,
            lab_technician=lab_tech,
            notes=notes
        )
        
        if success:
            messagebox.showinfo("Success", "Test result added successfully!")
            self.clear_form()
            self.refresh_results_display()
        else:
            messagebox.showerror("Error", "Failed to add test result.")
    
    def validate_test_form(self):
        """Validate test result form"""
        if not self.patient_var.get():
            messagebox.showerror("Validation Error", "Please select a patient.")
            return False
        
        if not self.test_type_var.get():
            messagebox.showerror("Validation Error", "Please select a test type.")
            return False
        
        try:
            float(self.test_value_var.get())
        except ValueError:
            messagebox.showerror("Validation Error", "Test value must be a number.")
            return False
        
        try:
            datetime.strptime(self.test_date_var.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Validation Error", "Test date must be in YYYY-MM-DD format.")
            return False
        
        return True
    
    def clear_form(self):
        """Clear test result form"""
        self.patient_var.set('')
        self.test_type_var.set('')
        self.test_value_var.set('')
        self.test_date_var.set(datetime.now().strftime('%Y-%m-%d'))
        self.lab_tech_var.set('')
        self.notes_var.set('')
    
    def refresh_results_display(self):
        """Refresh the test results display"""
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Get all patients and their recent results
        patients = self.db_manager.get_all_patients()
        
        critical_count = 0
        abnormal_count = 0
        unconfigured_count = 0
        
        for patient in patients:  # Show ALL patients (removed limit)
            patient_id = patient[0]
            patient_name = f"{patient[1]} {patient[2]}"
            
            # Get patient age and gender for adjustments
            age = patient[9] if len(patient) > 9 and patient[9] is not None else None
            gender = patient[4] if patient[4] else None
            
            results = self.db_manager.get_patient_test_results(patient_id)
            
            for result in results:  # Show ALL results per patient (removed limit)
                result_id, _, test_name, test_value, normal_min, normal_max, unit, test_date, _, _ = result
                
                # Get age/gender adjusted ranges
                range_info = self.db_manager.get_age_gender_adjusted_range(test_name, age, gender)
                if range_info['normal_min'] is not None and range_info['normal_max'] is not None:
                    normal_min, normal_max = range_info['normal_min'], range_info['normal_max']
                
                # Get critical thresholds
                critical_low = range_info.get('critical_low')
                critical_high = range_info.get('critical_high')
                
                # Determine status with critical threshold checks
                status = "Normal"
                status_color = ""
                
                # Check if ranges are configured
                if normal_min is None or normal_max is None:
                    status = "❓ NEEDS CONFIG"
                    status_color = "purple"
                # Check critical thresholds first (highest priority)
                elif critical_low is not None and test_value <= critical_low:
                    status = "🚨 CRITICAL LOW"
                    status_color = "red"
                elif critical_high is not None and test_value >= critical_high:
                    status = "🚨 CRITICAL HIGH"
                    status_color = "red"
                # Then check normal ranges
                elif test_value < normal_min:
                    status = "⚠️ Low"
                    status_color = "orange"
                elif test_value > normal_max:
                    status = "⚠️ High"
                    status_color = "orange"
                else:
                    status = "✅ Normal"
                    status_color = "green"
                
                display_name = f"{patient_name} (Age: {age if age else 'N/A'})"
                
                # Determine tag based on status
                tag = ''
                if 'NEEDS CONFIG' in status:
                    tag = 'unconfigured'
                    unconfigured_count += 1
                elif 'CRITICAL' in status:
                    tag = 'critical'
                    critical_count += 1
                elif 'Low' in status or 'High' in status:
                    tag = 'abnormal'
                    abnormal_count += 1
                elif 'Normal' in status:
                    tag = 'normal'
                
                item_id = self.results_tree.insert('', 'end', values=(
                    result_id,
                    display_name,
                    test_name,
                    f"{test_value:.2f}",
                    unit or '',
                    test_date,
                    status
                ), tags=(tag,))
        
        # Update alerts display
        self.update_alerts_display(critical_count, abnormal_count, unconfigured_count)
    
    def update_alerts_display(self, critical_count, abnormal_count, unconfigured_count):
        """Update the critical alerts display"""
        if critical_count > 0:
            alert_text = f"🚨 {critical_count} critical result(s) - immediate attention needed"
            self.alerts_label.config(text=alert_text, foreground='red')
        elif unconfigured_count > 0:
            alert_text = f"❓ {unconfigured_count} test type(s) need configuration"
            self.alerts_label.config(text=alert_text, foreground='purple')
        elif abnormal_count > 0:
            alert_text = f"⚠️ {abnormal_count} abnormal result(s)"
            self.alerts_label.config(text=alert_text, foreground='orange')
        else:
            self.alerts_label.config(text="✅ All results normal", foreground='green')


class DataImportFrame:
    def __init__(self, parent, data_processor):
        """Initialize data import frame"""
        self.parent = parent
        self.data_processor = data_processor
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the data import UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="CSV Data Import", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection")
        file_frame.pack(fill='x', pady=(0, 20))
        
        self.file_path_var = tk.StringVar()
        ttk.Label(file_frame, text="CSV File:").pack(anchor='w', padx=5, pady=5)
        
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Entry(file_select_frame, textvariable=self.file_path_var, width=60).pack(side='left', fill='x', expand=True)
        ttk.Button(file_select_frame, text="Browse", command=self.browse_file).pack(side='right', padx=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill='x', padx=5, pady=10)
        
        ttk.Button(button_frame, text="Preview Data", command=self.preview_data).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Import Data", command=self.import_data).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Generate Template", command=self.generate_template).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Refresh Views", command=self.refresh_all_views).pack(side='left', padx=5)
        
        # Options section
        options_frame = ttk.LabelFrame(main_frame, text="Import Options")
        options_frame.pack(fill='x', pady=(0, 20))
        
        self.update_existing_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Update existing patient information", 
                       variable=self.update_existing_var).pack(anchor='w', padx=5, pady=5)
        
        self.check_duplicates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Skip duplicate test results (recommended)", 
                       variable=self.check_duplicates_var).pack(anchor='w', padx=5, pady=(0, 5))
        
        # Preview/Results section
        preview_frame = ttk.LabelFrame(main_frame, text="Preview/Results")
        preview_frame.pack(fill='both', expand=True)
        
        # Text widget for preview
        self.preview_text = tk.Text(preview_frame, height=15, wrap=tk.WORD)
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient='vertical', command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        preview_scrollbar.pack(side='right', fill='y', pady=5)
    
    def browse_file(self):
        """Browse for CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def preview_data(self):
        """Preview the CSV data"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select a CSV file first.")
            return
        
        success, message, preview_df = self.data_processor.preview_csv_data(file_path)
        
        self.preview_text.delete(1.0, tk.END)
        
        if success:
            # Show preview
            self.preview_text.insert(tk.END, f"Preview of {file_path}:\n\n")
            self.preview_text.insert(tk.END, str(preview_df.to_string(index=False)))
            
            # Show import summary
            summary = self.data_processor.get_import_summary(file_path)
            if summary['valid']:
                summary_text = f"\n\nImport Summary:\n"
                summary_text += f"Total rows: {summary['total_rows']}\n"
                summary_text += f"Valid rows: {summary['valid_rows']}\n"
                summary_text += f"Unique patients: {summary['unique_patients']}\n"
                summary_text += f"Unique test types: {summary['unique_test_types']}\n"
                summary_text += f"Range warnings: {summary['range_warnings']}\n"
                
                if summary['warnings_detail']:
                    summary_text += "\nSample warnings:\n"
                    for warning in summary['warnings_detail']:
                        summary_text += f"- {warning['patient_id']}: {warning['test_name']} = {warning['test_value']} ({warning['status']})\n"
                
                self.preview_text.insert(tk.END, summary_text)
        else:
            self.preview_text.insert(tk.END, f"Error: {message}")
    
    def import_data(self):
        """Import the CSV data"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select a CSV file first.")
            return
        
        update_existing = self.update_existing_var.get()
        check_duplicates = self.check_duplicates_var.get()
        
        try:
            success, message, stats = self.data_processor.import_csv_data(file_path, update_existing, check_duplicates)
            
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"Import Results:\n\n{message}")
            
            if success:
                messagebox.showinfo("Success", "Data imported successfully!")
            else:
                messagebox.showerror("Error", f"Import failed: {message}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {str(e)}")
    
    def generate_template(self):
        """Generate a CSV template file"""
        file_path = filedialog.asksaveasfilename(
            title="Save CSV Template",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            success = self.data_processor.generate_csv_template(file_path)
            if success:
                messagebox.showinfo("Success", f"Template saved to: {file_path}")
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(tk.END, f"CSV template generated: {file_path}\n\n")
                self.preview_text.insert(tk.END, "Template includes sample data with the following columns:\n")
                self.preview_text.insert(tk.END, "- patient_id (required)\n")
                self.preview_text.insert(tk.END, "- name (full patient name)\n")
                self.preview_text.insert(tk.END, "- age (patient age in years)\n")
                self.preview_text.insert(tk.END, "- gender (Male/Female/Other)\n")
                self.preview_text.insert(tk.END, "- phone (phone number)\n")
                self.preview_text.insert(tk.END, "- test_name (required - name of the test)\n")
                self.preview_text.insert(tk.END, "- test_value (required - numeric test result)\n")
                self.preview_text.insert(tk.END, "- unit (measurement unit, e.g., mg/dL)\n")
                self.preview_text.insert(tk.END, "- notes (optional comments)\n")
                self.preview_text.insert(tk.END, "- date (test date in YYYY-MM-DD format)\n\n")
                self.preview_text.insert(tk.END, "Note: This imports both patient information and test results.\n")
                self.preview_text.insert(tk.END, "Patient records will be created/updated automatically.")
            else:
                messagebox.showerror("Error", "Failed to generate template.")
    
    def refresh_all_views(self):
        """Refresh all data views in the application after import"""
        try:
            # Get the main application window and refresh all tabs
            main_window = self.parent
            while main_window.master:
                main_window = main_window.master
            
            # Find and refresh patient form if it exists
            for child in main_window.winfo_children():
                if hasattr(child, 'winfo_children'):
                    for notebook in child.winfo_children():
                        if hasattr(notebook, 'tabs'):
                            # This is likely our notebook widget
                            for tab_id in notebook.tabs():
                                tab_frame = notebook.nametowidget(tab_id)
                                for widget in tab_frame.winfo_children():
                                    # Check if this widget has refresh methods
                                    if hasattr(widget, 'refresh_patient_list'):
                                        widget.refresh_patient_list()
                                    if hasattr(widget, 'refresh_data'):
                                        widget.refresh_data()
                                    if hasattr(widget, 'refresh_results_display'):
                                        widget.refresh_results_display()
            
            # Show confirmation message
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "All data views refreshed successfully!\n\n")
            self.preview_text.insert(tk.END, "Check the Patient Management and Test Results tabs to see updated data.")
            
            messagebox.showinfo("Success", "All data views refreshed! Check other tabs to see updated patient and test result data.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh views: {str(e)}")
