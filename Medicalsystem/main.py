"""
Medical Test Data Management System
A comprehensive system for managing patient test results with import, storage, and reporting capabilities.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import pandas as pd
import os
from datetime import datetime
from database_manager import DatabaseManager
from data_processor import DataProcessor
from report_generator import ReportGenerator
from ui_components import PatientForm, TestResultForm, DataImportFrame
from flexible_import_ui import FlexibleDataImportFrame

class MedicalTestSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Medical Test Data Management System")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.data_processor = DataProcessor(self.db_manager)
        self.report_generator = ReportGenerator(self.db_manager)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Patient Management Tab
        patient_frame = ttk.Frame(notebook)
        notebook.add(patient_frame, text="Patient Management")
        self.patient_form = PatientForm(patient_frame, self.db_manager)
        
        # Test Results Tab
        test_frame = ttk.Frame(notebook)
        notebook.add(test_frame, text="Test Results")
        self.test_form = TestResultForm(test_frame, self.db_manager)
        
        # Data Import Tab
        import_frame = ttk.Frame(notebook)
        notebook.add(import_frame, text="Medical Data Import")
        self.import_form = FlexibleDataImportFrame(import_frame, self.data_processor)
        
        # Reports Tab
        reports_frame = ttk.Frame(notebook)
        notebook.add(reports_frame, text="Reports")
        self.setup_reports_tab(reports_frame)
        
        # Simple Test Types Tab (NEW CLEAN VERSION)
        test_types_frame = ttk.Frame(notebook)
        notebook.add(test_types_frame, text="Test Types")
        self.setup_simple_test_types_tab(test_types_frame)
        
    def setup_reports_tab(self, parent):
        """Setup the reports generation tab"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Initialize search and selection variables
        self.current_patient_id = None
        
        # Title
        title_label = ttk.Label(main_frame, text="Report Generation", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Excel Report Section
        excel_frame = ttk.LabelFrame(main_frame, text="Excel Reports")
        excel_frame.pack(fill='x', pady=(0, 20))
        
        excel_info = ttk.Label(excel_frame, 
                              text="Generate comprehensive Excel reports with color-coded test results for all patients")
        excel_info.pack(padx=10, pady=5)
        
        excel_btn = ttk.Button(excel_frame, text="Generate Excel Report for ALL Patients",
                              command=self.generate_all_patients_excel_report)
        excel_btn.pack(pady=10)
        
        # PDF Report Section (Individual Patient)
        pdf_frame = ttk.LabelFrame(main_frame, text="PDF Patient Reports")
        pdf_frame.pack(fill='x', pady=(0, 20))
        
        # Patient search and selection for PDF
        selection_frame = ttk.Frame(pdf_frame)
        selection_frame.pack(fill='x', padx=10, pady=5)
        
        # Search section
        search_frame = ttk.Frame(selection_frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="Search Patients:").pack(anchor='w')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_entry.pack(fill='x', pady=5)
        
        ttk.Label(search_frame, text="Search by Name, ID, or Phone", 
                 font=('Arial', 8), foreground='gray').pack(anchor='w')
        
        # Results section
        results_frame = ttk.Frame(selection_frame)
        results_frame.pack(fill='both', expand=True)
        
        ttk.Label(results_frame, text="Select Patient:").pack(anchor='w')
        
        # Create treeview for patient results
        columns = ('ID', 'Name', 'Phone', 'Gender', 'Age')
        self.patient_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.patient_tree.heading(col, text=col)
            self.patient_tree.column(col, width=100)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.patient_tree.yview)
        self.patient_tree.configure(yscrollcommand=scrollbar.set)
        
        self.patient_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.patient_tree.bind('<<TreeviewSelect>>', self.on_patient_select)
        
        # Selected patient info
        self.selected_patient_var = tk.StringVar()
        selected_frame = ttk.Frame(selection_frame)
        selected_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(selected_frame, text="Selected Patient:").pack(anchor='w')
        selected_label = ttk.Label(selected_frame, textvariable=self.selected_patient_var,
                                  font=('Arial', 10, 'bold'), foreground='blue')
        selected_label.pack(anchor='w', pady=(0, 5))
        
        refresh_btn = ttk.Button(selected_frame, text="Refresh Patient List",
                               command=self.refresh_patient_list)
        refresh_btn.pack(pady=5)
        
        patient_btn = ttk.Button(pdf_frame, text="Generate PDF Patient Summary",
                               command=self.generate_patient_summary)
        patient_btn.pack(pady=10)
        
        # Load initial data
        self.refresh_patient_list()
        
    def refresh_patient_list(self):
        """Refresh the patient list in the treeview"""
        # Clear existing items
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)
        
        # Get all patients
        patients = self.db_manager.get_all_patients()
        
        # Populate treeview
        for patient in patients:
            patient_id = patient[0]
            first_name = patient[1] or ''
            last_name = patient[2] or ''
            full_name = f"{first_name} {last_name}".strip()
            age = patient[9] if len(patient) > 9 and patient[9] is not None else 'N/A'  # Use age field at position 9
            gender = patient[4] or 'N/A'
            phone = patient[5] or 'N/A'
            
            self.patient_tree.insert('', 'end', values=(
                patient_id, full_name, phone, gender, age
            ))
        
        # Clear search and selection
        self.search_var.set('')
        self.selected_patient_var.set('No patient selected')
        self.current_patient_id = None
    
    def on_search_change(self, *args):
        """Handle search input changes"""
        search_term = self.search_var.get().lower().strip()
        
        # Clear existing items
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)
        
        if not search_term:
            # Show all patients if search is empty
            self.refresh_patient_list()
            return
        
        # Get all patients and filter
        patients = self.db_manager.get_all_patients()
        
        for patient in patients:
            patient_id = str(patient[0])
            first_name = (patient[1] or '').lower()
            last_name = (patient[2] or '').lower()
            full_name = f"{first_name} {last_name}".strip()
            phone = (patient[5] or '').lower()
            
            # Check if search term matches any field
            if (search_term in patient_id or 
                search_term in first_name or 
                search_term in last_name or 
                search_term in full_name or 
                search_term in phone):
                
                # Get age and gender for display
                gender = patient[4] or 'N/A'
                age = patient[9] if len(patient) > 9 and patient[9] is not None else 'N/A'  # Use age field at position 9
                display_name = f"{patient[1] or ''} {patient[2] or ''}".strip()
                
                self.patient_tree.insert('', 'end', values=(
                    patient[0], display_name, patient[5] or 'N/A', gender, age
                ))
    
    def on_patient_select(self, event=None):
        """Handle patient selection from treeview"""
        selection = self.patient_tree.selection()
        if selection:
            item = self.patient_tree.item(selection[0])
            values = item['values']
            if values:
                self.current_patient_id = values[0]
                patient_name = values[1]
                self.selected_patient_var.set(f"{patient_name} (ID: {self.current_patient_id})")
        else:
            self.current_patient_id = None
            self.selected_patient_var.set('No patient selected')
        
    def generate_all_patients_excel_report(self):
        """Generate Excel report for ALL patients with color coding"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save Excel Report for All Patients"
        )
        
        if filename:
            try:
                self.report_generator.generate_all_patients_excel_report(filename)
                messagebox.showinfo("Success", f"Excel report for all patients generated: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
                
    def generate_excel_report(self):
        """Generate Excel report for selected patient (deprecated - kept for compatibility)"""
        if not hasattr(self, 'current_patient_id') or not self.current_patient_id:
            messagebox.showwarning("Warning", "Please select a patient first.")
            return
            
        patient_id = self.current_patient_id
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save Excel Report"
        )
        
        if filename:
            try:
                self.report_generator.generate_excel_report(patient_id, filename)
                messagebox.showinfo("Success", f"Excel report generated: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
                
    def generate_patient_summary(self):
        """Generate patient summary report"""
        if not hasattr(self, 'current_patient_id') or not self.current_patient_id:
            messagebox.showwarning("Warning", "Please select a patient first.")
            return
            
        patient_id = self.current_patient_id
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Patient Summary"
        )
        
        if filename:
            try:
                self.report_generator.generate_patient_summary(patient_id, filename)
                messagebox.showinfo("Success", f"Patient summary generated: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate summary: {str(e)}")
    
    def setup_simple_test_types_tab(self, parent):
        """Setup a simple test types management tab"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        ttk.Label(main_frame, text="Test Types", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Add test type frame
        add_frame = ttk.LabelFrame(main_frame, text="Add Test Type")
        add_frame.pack(fill='x', pady=10)
        
        # Form fields
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(padx=10, pady=10)
        
        ttk.Label(form_frame, text="Test Name:").grid(row=0, column=0, sticky='w', padx=5)
        self.test_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.test_name_var, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Unit:").grid(row=0, column=2, sticky='w', padx=5)
        self.unit_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.unit_var, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Label(form_frame, text="Normal Min:").grid(row=1, column=0, sticky='w', padx=5)
        self.min_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.min_var, width=10).grid(row=1, column=1, padx=5)
        
        ttk.Label(form_frame, text="Normal Max:").grid(row=1, column=2, sticky='w', padx=5)
        self.max_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.max_var, width=10).grid(row=1, column=3, padx=5)
        
        ttk.Label(form_frame, text="Critical Low:").grid(row=2, column=0, sticky='w', padx=5)
        self.critical_low_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.critical_low_var, width=10).grid(row=2, column=1, padx=5)
        
        ttk.Label(form_frame, text="Critical High:").grid(row=2, column=2, sticky='w', padx=5)
        self.critical_high_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.critical_high_var, width=10).grid(row=2, column=3, padx=5)
        
        ttk.Label(form_frame, text="Gender:").grid(row=3, column=0, sticky='w', padx=5)
        self.gender_var = tk.StringVar(value="Both")
        gender_combo = ttk.Combobox(form_frame, textvariable=self.gender_var, values=["Both", "Male", "Female", "Child", "Baby"], width=10)
        gender_combo.grid(row=3, column=1, padx=5)
        gender_combo.state(['readonly'])
        
        ttk.Label(form_frame, text="Method:").grid(row=3, column=2, sticky='w', padx=5)
        self.method_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.method_var, width=15).grid(row=3, column=3, padx=5)
        
        # Add button
        ttk.Button(form_frame, text="Add Test Type", command=self.add_test_type).grid(row=4, column=0, columnspan=4, pady=10)
        
        # Current test types list
        list_frame = ttk.LabelFrame(main_frame, text="Test Types")
        list_frame.pack(fill='both', expand=True, pady=10)
        
        # Treeview for test types
        columns = ('Name', 'Unit', 'Normal Min', 'Normal Max', 'Critical Low', 'Critical High', 'Method')
        self.test_types_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.test_types_tree.heading(col, text=col)
            if col == 'Method':
                self.test_types_tree.column(col, width=100)
            else:
                self.test_types_tree.column(col, width=80)
        
        self.test_types_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Double-click to edit
        self.test_types_tree.bind('<Double-1>', lambda e: self.edit_test_type())
        
        # Buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="Refresh", command=self.refresh_test_types).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Edit", command=self.edit_test_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_test_type).pack(side='left', padx=5)
        
        # Load initial data
        self.refresh_test_types()
    
    def add_test_type(self):
        """Add a new test type with optional gender-specific ranges"""
        try:
            name = self.test_name_var.get().strip()
            unit = self.unit_var.get().strip()
            min_val = float(self.min_var.get()) if self.min_var.get().strip() else None
            max_val = float(self.max_var.get()) if self.max_var.get().strip() else None
            critical_low = float(self.critical_low_var.get()) if self.critical_low_var.get().strip() else None
            critical_high = float(self.critical_high_var.get()) if self.critical_high_var.get().strip() else None
            gender = self.gender_var.get()
            method = self.method_var.get().strip() or None
            
            if not name:
                messagebox.showerror("Error", "Test name is required")
                return
            
            # First, add the base test type (or get existing one)
            test_type = self.db_manager.get_test_type_by_name(name)
            if not test_type:
                success = self.db_manager.add_test_type(
                    test_name=name,
                    unit=unit,
                    normal_min=None if gender != "Both" else min_val,  # Only set base ranges if "Both"
                    normal_max=None if gender != "Both" else max_val,
                    critical_low=None if gender != "Both" else critical_low,
                    critical_high=None if gender != "Both" else critical_high,
                    method=method,
                    description=f"Test: {name}"
                )
                if not success:
                    messagebox.showerror("Error", "Failed to add test type")
                    return
                test_type = self.db_manager.get_test_type_by_name(name)
            
            # If gender-specific, add custom range
            if gender != "Both" and test_type:
                range_name = f"{name} - {gender}"
                success = self.db_manager.add_custom_test_range(
                    test_type_id=test_type[0],
                    range_name=range_name,
                    gender=gender,
                    normal_min=min_val,
                    normal_max=max_val,
                    critical_low=critical_low,
                    critical_high=critical_high,
                    notes=f"Gender-specific range for {gender}"
                )
                if not success:
                    messagebox.showerror("Error", "Failed to add gender-specific range")
                    return
            
            messagebox.showinfo("Success", f"Added '{name}' successfully")
            # Clear form
            self.test_name_var.set("")
            self.unit_var.set("")
            self.min_var.set("")
            self.max_var.set("")
            self.critical_low_var.set("")
            self.critical_high_var.set("")
            self.gender_var.set("Both")
            self.method_var.set("")
            self.refresh_test_types()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
    
    def refresh_test_types(self):
        """Refresh the test types list including gender-specific ranges"""
        # Clear existing items
        for item in self.test_types_tree.get_children():
            self.test_types_tree.delete(item)
        
        # Load test types
        test_types = self.db_manager.get_test_types()
        for test_type in test_types:
            # test_type: (test_type_id, test_name, normal_min, normal_max, unit, description, category, critical_low, critical_high, method)
            test_type_id = test_type[0]
            name = test_type[1]
            unit = test_type[4] or ""
            min_val = test_type[2] if test_type[2] is not None else ""
            max_val = test_type[3] if test_type[3] is not None else ""
            critical_low = test_type[7] if len(test_type) > 7 and test_type[7] is not None else ""
            critical_high = test_type[8] if len(test_type) > 8 and test_type[8] is not None else ""
            method = test_type[9] if len(test_type) > 9 and test_type[9] else "Standard Method"
            
            # Add base test type (if it has ranges)
            if min_val or max_val:
                display_name = f"{name} (Both)"
                self.test_types_tree.insert('', 'end', values=(display_name, unit, min_val, max_val, critical_low, critical_high, method))
            elif not min_val and not max_val:
                # Check for gender-specific ranges
                custom_ranges = self.db_manager.get_custom_test_ranges(test_type_id)
                if not custom_ranges:
                    # Show test type without ranges
                    self.test_types_tree.insert('', 'end', values=(name, unit, "", "", "", "", method))
            
            # Add gender-specific custom ranges
            custom_ranges = self.db_manager.get_custom_test_ranges(test_type_id)
            for custom_range in custom_ranges:
                # custom_range: (range_id, test_type_id, range_name, age_min, age_max, gender, condition_name, 
                #                normal_min, normal_max, critical_low, critical_high, notes, is_active, test_name, unit)
                if len(custom_range) >= 14 and custom_range[12]:  # is_active check
                    gender = custom_range[5] if custom_range[5] else "Both"
                    range_min = custom_range[7] if custom_range[7] is not None else ""
                    range_max = custom_range[8] if custom_range[8] is not None else ""
                    range_critical_low = custom_range[9] if custom_range[9] is not None else ""
                    range_critical_high = custom_range[10] if custom_range[10] is not None else ""
                    
                    display_name = f"{name} ({gender})"
                    self.test_types_tree.insert('', 'end', values=(display_name, unit, range_min, range_max, range_critical_low, range_critical_high, method))
    
    def edit_test_type(self):
        """Edit selected test type or custom range"""
        selection = self.test_types_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a test type to edit")
            return
        
        item = self.test_types_tree.item(selection[0])
        values = item['values']
        display_name = values[0]
        
        # Parse display name to get test name and gender
        if " (" in display_name and display_name.endswith(")"):
            test_name = display_name.split(" (")[0]
            gender_part = display_name.split(" (")[1][:-1]  # Remove closing parenthesis
        else:
            test_name = display_name
            gender_part = "Both"
        
        # Get the test type from database
        test_type = self.db_manager.get_test_type_by_name(test_name)
        if not test_type:
            messagebox.showerror("Error", "Test type not found")
            return
        
        # Check if this is a custom range or base test type
        is_custom_range = gender_part in ["Male", "Female"]
        custom_range_data = None
        
        if is_custom_range:
            # Find the custom range
            custom_ranges = self.db_manager.get_custom_test_ranges(test_type[0])
            for custom_range in custom_ranges:
                if custom_range[5] == gender_part:  # gender field
                    custom_range_data = custom_range
                    break
            
            if not custom_range_data:
                messagebox.showerror("Error", "Custom range not found")
                return
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit {display_name}")
        edit_window.geometry("400x350")
        edit_window.resizable(False, False)
        
        # Center the window
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Form frame
        form_frame = ttk.Frame(edit_window)
        form_frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Title
        ttk.Label(form_frame, text=f"Editing: {display_name}", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Use custom range data if available, otherwise base test type data
        data_source = custom_range_data if is_custom_range else test_type
        
        # Form fields with current values
        ttk.Label(form_frame, text="Unit:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        unit_var = tk.StringVar(value=test_type[4] or "")  # Unit always from base test type
        ttk.Entry(form_frame, textvariable=unit_var, width=15).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Normal Min:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        if is_custom_range:
            min_val = str(data_source[7]) if data_source[7] is not None else ""
        else:
            min_val = str(data_source[2]) if data_source[2] is not None else ""
        min_var = tk.StringVar(value=min_val)
        ttk.Entry(form_frame, textvariable=min_var, width=15).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Normal Max:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        if is_custom_range:
            max_val = str(data_source[8]) if data_source[8] is not None else ""
        else:
            max_val = str(data_source[3]) if data_source[3] is not None else ""
        max_var = tk.StringVar(value=max_val)
        ttk.Entry(form_frame, textvariable=max_var, width=15).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Critical Low:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        if is_custom_range:
            critical_low_val = str(data_source[9]) if data_source[9] is not None else ""
        else:
            critical_low_val = str(data_source[7]) if len(data_source) > 7 and data_source[7] is not None else ""
        critical_low_var = tk.StringVar(value=critical_low_val)
        ttk.Entry(form_frame, textvariable=critical_low_var, width=15).grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Critical High:").grid(row=5, column=0, sticky='w', padx=5, pady=5)
        if is_custom_range:
            critical_high_val = str(data_source[10]) if data_source[10] is not None else ""
        else:
            critical_high_val = str(data_source[8]) if len(data_source) > 8 and data_source[8] is not None else ""
        critical_high_var = tk.StringVar(value=critical_high_val)
        ttk.Entry(form_frame, textvariable=critical_high_var, width=15).grid(row=5, column=1, padx=5, pady=5)
        
        # Gender dropdown (editable)
        ttk.Label(form_frame, text="Gender:").grid(row=6, column=0, sticky='w', padx=5, pady=5)
        gender_var = tk.StringVar(value=gender_part)
        gender_dropdown = ttk.Combobox(form_frame, textvariable=gender_var, values=["Both", "Male", "Female", "Child", "Baby"], 
                                     state="readonly", width=12)
        gender_dropdown.grid(row=6, column=1, sticky='w', padx=5, pady=5)
        
        # Method field
        ttk.Label(form_frame, text="Method:").grid(row=7, column=0, sticky='w', padx=5, pady=5)
        # Get current method from test type data
        current_method = test_type[9] if len(test_type) > 9 and test_type[9] else ""
        method_var = tk.StringVar(value=current_method)
        ttk.Entry(form_frame, textvariable=method_var, width=15).grid(row=7, column=1, padx=5, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        def save_changes():
            try:
                unit = unit_var.get().strip()
                min_val = float(min_var.get()) if min_var.get().strip() else None
                max_val = float(max_var.get()) if max_var.get().strip() else None
                critical_low = float(critical_low_var.get()) if critical_low_var.get().strip() else None
                critical_high = float(critical_high_var.get()) if critical_high_var.get().strip() else None
                new_gender = gender_var.get()
                method = method_var.get().strip() or None
                
                # Handle gender change logic
                if new_gender != gender_part:
                    # Gender has changed - need to handle data migration
                    
                    if is_custom_range:
                        # Currently a custom range, check new gender
                        if new_gender == "Both":
                            # Move from custom range to base test type
                            # Update base test type with current values
                            success = self.db_manager.update_test_type(
                                test_type_id=test_type[0],
                                test_name=test_name,
                                unit=unit,
                                normal_min=min_val,
                                normal_max=max_val,
                                critical_low=critical_low,
                                critical_high=critical_high,
                                method=method,
                                description=test_type[5]
                            )
                            # Delete the custom range
                            if success:
                                self.db_manager.delete_custom_test_range(custom_range_data[0])
                        else:
                            # Change from one gender to another gender (Male <-> Female)
                            success = self.db_manager.update_custom_test_range(
                                range_id=custom_range_data[0],
                                gender=new_gender,
                                normal_min=min_val,
                                normal_max=max_val,
                                critical_low=critical_low,
                                critical_high=critical_high
                            )
                            # Also update base test type unit
                            self.db_manager.update_test_type(
                                test_type_id=test_type[0],
                                test_name=test_name,
                                unit=unit,
                                normal_min=test_type[2],
                                normal_max=test_type[3],
                                critical_low=test_type[7] if len(test_type) > 7 else None,
                                critical_high=test_type[8] if len(test_type) > 8 else None,
                                method=method,
                                description=test_type[5]
                            )
                    else:
                        # Currently base test type (Both), moving to gender-specific
                        if new_gender in ["Male", "Female"]:
                            # Create new custom range
                            range_name = f"{test_name} - {new_gender}"
                            success = self.db_manager.add_custom_test_range(
                                test_type_id=test_type[0],
                                range_name=range_name,
                                gender=new_gender,
                                normal_min=min_val,
                                normal_max=max_val,
                                critical_low=critical_low,
                                critical_high=critical_high,
                                notes=f"Gender-specific range for {new_gender}"
                            )
                            # Clear base test type ranges but keep unit
                            if success:
                                self.db_manager.update_test_type(
                                    test_type_id=test_type[0],
                                    test_name=test_name,
                                    unit=unit,
                                    normal_min=None,
                                    normal_max=None,
                                    critical_low=None,
                                    critical_high=None,
                                    method=method,
                                    description=test_type[5]
                                )
                        else:
                            # Staying as "Both"
                            success = self.db_manager.update_test_type(
                                test_type_id=test_type[0],
                                test_name=test_name,
                                unit=unit,
                                normal_min=min_val,
                                normal_max=max_val,
                                critical_low=critical_low,
                                critical_high=critical_high,
                                method=method,
                                description=test_type[5]
                            )
                else:
                    # Gender hasn't changed - normal update
                    if is_custom_range:
                        # Update custom range
                        success = self.db_manager.update_custom_test_range(
                            range_id=custom_range_data[0],
                            normal_min=min_val,
                            normal_max=max_val,
                            critical_low=critical_low,
                            critical_high=critical_high
                        )
                        # Also update base test type unit
                        self.db_manager.update_test_type(
                            test_type_id=test_type[0],
                            test_name=test_name,
                            unit=unit,
                            normal_min=test_type[2],
                            normal_max=test_type[3],
                            critical_low=test_type[7] if len(test_type) > 7 else None,
                            critical_high=test_type[8] if len(test_type) > 8 else None,
                            method=method,
                            description=test_type[5]
                        )
                    else:
                        # Update base test type
                        success = self.db_manager.update_test_type(
                            test_type_id=test_type[0],
                            test_name=test_name,
                            unit=unit,
                            normal_min=min_val,
                            normal_max=max_val,
                            critical_low=critical_low,
                            critical_high=critical_high,
                            method=method,
                            description=test_type[5]
                        )
                
                if success:
                    messagebox.showinfo("Success", f"Updated test type successfully")
                    edit_window.destroy()
                    self.refresh_test_types()
                else:
                    messagebox.showerror("Error", "Failed to update test type")
                    
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
        
        ttk.Button(button_frame, text="Save", command=save_changes).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side='left', padx=5)
    
    def delete_test_type(self):
        """Delete selected test type"""
        selection = self.test_types_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a test type")
            return
        
        item = self.test_types_tree.item(selection[0])
        test_name = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete '{test_name}'?"):
            test_type = self.db_manager.get_test_type_by_name(test_name)
            if test_type:
                success = self.db_manager.delete_test_type(test_type[0])
                if success:
                    messagebox.showinfo("Success", f"Deleted '{test_name}'")
                    self.refresh_test_types()
                else:
                    messagebox.showerror("Error", "Failed to delete")
    
    def extract_patient_id(self, patient_string):
        """Extract patient ID from the combo box string"""
        return patient_string.split("ID: ")[1].rstrip(")")
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MedicalTestSystem()
    app.run()
