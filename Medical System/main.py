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
from test_configuration_ui import TestConfigurationFrame

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
        notebook.add(import_frame, text="Flexible CSV Import")
        self.import_form = FlexibleDataImportFrame(import_frame, self.data_processor)
        
        # Reports Tab
        reports_frame = ttk.Frame(notebook)
        notebook.add(reports_frame, text="Reports")
        self.setup_reports_tab(reports_frame)
        
        # Test Configuration Tab (replaces old Test Types tab)
        test_config_frame = ttk.Frame(notebook)
        notebook.add(test_config_frame, text="Test Configuration")
        self.test_configuration = TestConfigurationFrame(test_config_frame, self.db_manager)
        
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
            dob = patient[3]
            gender = patient[4] or 'N/A'
            phone = patient[5] or 'N/A'
            
            # Calculate age
            age = self.db_manager.calculate_age(dob) if dob else 'N/A'
            
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
                
                # Calculate age and gender for display
                dob = patient[3]
                gender = patient[4] or 'N/A'
                age = self.db_manager.calculate_age(dob) if dob else 'N/A'
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
    
    def extract_patient_id(self, patient_string):
        """Extract patient ID from the combo box string"""
        return patient_string.split("ID: ")[1].rstrip(")")
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MedicalTestSystem()
    app.run()
