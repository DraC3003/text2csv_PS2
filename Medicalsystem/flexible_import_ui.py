"""
Flexible Data Import UI Component
Enhanced interface for importing CSV files with intelligent column mapping.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from typing import Dict, Optional, List
from flexible_data_processor import FlexibleDataProcessor

class FlexibleDataImportFrame:
    def __init__(self, parent, data_processor):
        """Initialize flexible data import interface"""
        self.parent = parent
        self.data_processor = data_processor
        self.flexible_processor = FlexibleDataProcessor(data_processor.db_manager)
        
        self.current_file_path = None
        self.preview_data = None
        self.detected_mapping = {}
        self.manual_mapping = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the flexible import user interface"""
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Medical Test Data Import", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                               text="Import patient information and test results from CSV files with automatic column detection",
                               font=('Arial', 10))
        instructions.pack(pady=(0, 15))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="Step 1: Select CSV File")
        file_frame.pack(fill='x', pady=(0, 15))
        
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill='x', padx=10, pady=10)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var, 
                                   state='readonly', width=60)
        self.file_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(file_select_frame, text="Browse", command=self.browse_file)
        browse_btn.pack(side='right')
        
        # Encoding selection
        encoding_frame = ttk.Frame(file_frame)
        encoding_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Label(encoding_frame, text="File Encoding:").pack(side='left')
        self.encoding_var = tk.StringVar(value='utf-8')
        encoding_combo = ttk.Combobox(encoding_frame, textvariable=self.encoding_var,
                                     values=['utf-8', 'latin-1', 'cp1252', 'iso-8859-1'],
                                     width=15, state='readonly')
        encoding_combo.pack(side='left', padx=(10, 0))
        
        analyze_btn = ttk.Button(encoding_frame, text="Analyze File", 
                               command=self.analyze_file)
        analyze_btn.pack(side='right')
        
        # Column mapping section
        mapping_frame = ttk.LabelFrame(main_frame, text="Step 2: Verify Column Mapping")
        mapping_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Mapping controls
        mapping_controls = ttk.Frame(mapping_frame)
        mapping_controls.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(mapping_controls, text="Auto-detected mappings (click to modify):").pack(anchor='w')
        
        # Mapping treeview
        self.mapping_tree = ttk.Treeview(mapping_frame, columns=('Standard Field', 'Detected Column', 'Sample Data'), 
                                        show='headings', height=8)
        
        self.mapping_tree.heading('Standard Field', text='Standard Field')
        self.mapping_tree.heading('Detected Column', text='Detected Column')
        self.mapping_tree.heading('Sample Data', text='Sample Data')
        
        self.mapping_tree.column('Standard Field', width=150)
        self.mapping_tree.column('Detected Column', width=200)
        self.mapping_tree.column('Sample Data', width=150)
        
        # Scrollbar for mapping tree
        mapping_scrollbar = ttk.Scrollbar(mapping_frame, orient='vertical', 
                                         command=self.mapping_tree.yview)
        self.mapping_tree.configure(yscrollcommand=mapping_scrollbar.set)
        
        mapping_tree_frame = ttk.Frame(mapping_frame)
        mapping_tree_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.mapping_tree.pack(side='left', fill='both', expand=True)
        mapping_scrollbar.pack(side='right', fill='y')
        
        # Manual mapping controls
        manual_frame = ttk.Frame(mapping_frame)
        manual_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Label(manual_frame, text="Manual column assignment:").pack(anchor='w')
        
        manual_controls = ttk.Frame(manual_frame)
        manual_controls.pack(fill='x', pady=(5, 0))
        
        ttk.Label(manual_controls, text="Field:").pack(side='left')
        self.field_var = tk.StringVar()
        field_combo = ttk.Combobox(manual_controls, textvariable=self.field_var,
                                  values=['patient_id', 'name', 'age', 'gender', 'phone', 
                                         'test_name', 'test_value', 'unit', 'notes', 'date'],
                                  width=15, state='readonly')
        field_combo.pack(side='left', padx=(5, 10))
        
        ttk.Label(manual_controls, text="Column:").pack(side='left')
        self.column_var = tk.StringVar()
        self.column_combo = ttk.Combobox(manual_controls, textvariable=self.column_var,
                                        width=20, state='readonly')
        self.column_combo.pack(side='left', padx=(5, 10))
        
        update_mapping_btn = ttk.Button(manual_controls, text="Update Mapping",
                                       command=self.update_manual_mapping)
        update_mapping_btn.pack(side='left', padx=(10, 0))
        
        # Preview section
        preview_frame = ttk.LabelFrame(main_frame, text="Step 3: Preview Data")
        preview_frame.pack(fill='x', pady=(0, 15))
        
        self.preview_text = tk.Text(preview_frame, height=6, wrap='none')
        preview_scrollbar_y = ttk.Scrollbar(preview_frame, orient='vertical', 
                                           command=self.preview_text.yview)
        preview_scrollbar_x = ttk.Scrollbar(preview_frame, orient='horizontal', 
                                           command=self.preview_text.xview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar_y.set,
                                   xscrollcommand=preview_scrollbar_x.set)
        
        preview_text_frame = ttk.Frame(preview_frame)
        preview_text_frame.pack(fill='x', padx=10, pady=10)
        
        self.preview_text.pack(side='left', fill='both', expand=True)
        preview_scrollbar_y.pack(side='right', fill='y')
        preview_scrollbar_x.pack(side='bottom', fill='x')
        
        # Import section
        import_frame = ttk.LabelFrame(main_frame, text="Step 4: Import Data")
        import_frame.pack(fill='x')
        
        import_controls = ttk.Frame(import_frame)
        import_controls.pack(fill='x', padx=10, pady=10)
        
        # Import options
        options_frame = ttk.Frame(import_controls)
        options_frame.pack(fill='x', pady=(0, 10))
        
        # Duplicate detection option
        self.check_duplicates_var = tk.BooleanVar(value=True)
        duplicate_check = ttk.Checkbutton(options_frame, 
                                         text="Skip duplicate records (recommended)",
                                         variable=self.check_duplicates_var)
        duplicate_check.pack(side='left')
        
        # Help text for duplicate detection
        help_label = ttk.Label(options_frame, 
                              text="Duplicates: Same patient, test type, value, and date",
                              foreground='gray')
        help_label.pack(side='left', padx=(10, 0))
        
        # Status and buttons frame
        status_frame = ttk.Frame(import_controls)
        status_frame.pack(fill='x')
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to import")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side='left')
        
        # Import buttons
        button_frame = ttk.Frame(status_frame)
        button_frame.pack(side='right')
        
        validate_btn = ttk.Button(button_frame, text="Validate Data", 
                                 command=self.validate_data)
        validate_btn.pack(side='left', padx=(0, 10))
        
        import_btn = ttk.Button(button_frame, text="Import Data", 
                               command=self.import_data)
        import_btn.pack(side='left')
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(import_frame, variable=self.progress_var,
                                           maximum=100)
        self.progress_bar.pack(fill='x', padx=10, pady=(0, 10))
    
    def browse_file(self):
        """Browse for CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.current_file_path = file_path
            self.status_var.set("File selected. Click 'Analyze File' to proceed.")
    
    def analyze_file(self):
        """Analyze the selected CSV file and detect column mappings"""
        if not self.current_file_path:
            messagebox.showwarning("Warning", "Please select a CSV file first.")
            return
        
        self.status_var.set("Analyzing file...")
        self.progress_var.set(20)
        
        try:
            # Analyze the file
            success, message, preview_df, detected_mapping = self.flexible_processor.preview_csv_with_mapping(
                self.current_file_path, 
                self.encoding_var.get()
            )
            
            self.progress_var.set(60)
            
            if not success:
                messagebox.showerror("Error", f"Failed to analyze file: {message}")
                self.progress_var.set(0)
                return
            
            # Store results
            self.preview_data = preview_df
            self.detected_mapping = detected_mapping or {}
            self.manual_mapping = self.detected_mapping.copy()
            
            # Update column combo box
            if preview_df is not None:
                self.column_combo['values'] = list(preview_df.columns)
            
            # Update mapping display
            self.update_mapping_display()
            
            # Update preview
            self.update_preview()
            
            self.progress_var.set(100)
            self.status_var.set(f"Analysis complete. {message}")
            
            # Reset progress after a moment
            self.parent.after(2000, lambda: self.progress_var.set(0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error analyzing file: {str(e)}")
            self.progress_var.set(0)
            self.status_var.set("Analysis failed")
    
    def update_mapping_display(self):
        """Update the mapping tree view"""
        # Clear existing items
        for item in self.mapping_tree.get_children():
            self.mapping_tree.delete(item)
        
        # Add current mappings
        for standard_field, detected_column in self.manual_mapping.items():
            sample_data = ""
            if self.preview_data is not None and detected_column in self.preview_data.columns:
                sample_values = self.preview_data[detected_column].dropna().head(3)
                sample_data = ", ".join([str(val) for val in sample_values])
                if len(sample_data) > 30:
                    sample_data = sample_data[:27] + "..."
            
            self.mapping_tree.insert('', 'end', values=(standard_field, detected_column, sample_data))
        
        # Add unmapped essential fields
        essential_fields = ['patient_id', 'test_value']
        for field in essential_fields:
            if field not in self.manual_mapping:
                self.mapping_tree.insert('', 'end', values=(field, "NOT MAPPED", "❌ Required"))
    
    def update_manual_mapping(self):
        """Update manual column mapping"""
        field = self.field_var.get()
        column = self.column_var.get()
        
        if not field or not column:
            messagebox.showwarning("Warning", "Please select both field and column.")
            return
        
        # Update mapping
        self.manual_mapping[field] = column
        
        # Update display
        self.update_mapping_display()
        self.update_preview()
        
        # Clear selections
        self.field_var.set('')
        self.column_var.set('')
        
        self.status_var.set(f"Updated mapping: {field} → {column}")
    
    def update_preview(self):
        """Update the data preview"""
        if self.preview_data is None:
            return
        
        # Create mapped preview
        try:
            mapped_df = self.flexible_processor.clean_and_convert_data(
                self.preview_data, 
                self.manual_mapping
            )
            
            # Show preview in text widget
            self.preview_text.delete(1.0, tk.END)
            
            if mapped_df.empty:
                self.preview_text.insert(tk.END, "No data to preview with current mapping.")
            else:
                # Format the preview
                preview_text = "Mapped Data Preview (first 5 rows):\n"
                preview_text += "=" * 60 + "\n\n"
                
                # Show column headers
                headers = list(mapped_df.columns)
                preview_text += " | ".join(f"{h:12}" for h in headers) + "\n"
                preview_text += "-" * (len(headers) * 15) + "\n"
                
                # Show data rows
                for i, (_, row) in enumerate(mapped_df.head(5).iterrows()):
                    row_text = " | ".join(f"{str(val)[:12]:12}" for val in row)
                    preview_text += row_text + "\n"
                
                self.preview_text.insert(tk.END, preview_text)
                
        except Exception as e:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"Preview error: {str(e)}")
    
    def validate_data(self):
        """Validate the data before import"""
        if not self.preview_data is not None:
            messagebox.showwarning("Warning", "Please analyze a file first.")
            return
        
        self.status_var.set("Validating data...")
        self.progress_var.set(30)
        
        try:
            # Clean and validate data
            cleaned_df = self.flexible_processor.clean_and_convert_data(
                self.preview_data, 
                self.manual_mapping
            )
            
            is_valid, errors, final_df = self.flexible_processor.validate_processed_data(cleaned_df)
            
            self.progress_var.set(100)
            
            # Show validation results
            if is_valid:
                message = f"✅ Data validation passed!\n\n"
                message += f"Total rows: {len(final_df)}\n"
                message += f"Valid patients: {final_df['patient_id'].nunique() if 'patient_id' in final_df.columns else 'Unknown'}\n"
                
                if errors:
                    message += f"\nWarnings:\n" + "\n".join(f"• {error}" for error in errors)
                
                messagebox.showinfo("Validation Results", message)
                self.status_var.set("Validation passed. Ready to import.")
            else:
                message = f"❌ Data validation failed!\n\n"
                message += "Errors:\n" + "\n".join(f"• {error}" for error in errors)
                messagebox.showerror("Validation Results", message)
                self.status_var.set("Validation failed. Please fix mapping.")
            
            # Reset progress
            self.parent.after(2000, lambda: self.progress_var.set(0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Validation error: {str(e)}")
            self.progress_var.set(0)
            self.status_var.set("Validation failed")
    
    def import_data(self):
        """Import the data into the database"""
        if not self.preview_data is not None:
            messagebox.showwarning("Warning", "Please analyze a file first.")
            return
        
        # Confirm import
        if not messagebox.askyesno("Confirm Import", 
                                  "Are you sure you want to import this data into the database?"):
            return
        
        self.status_var.set("Importing data...")
        self.progress_var.set(10)
        
        try:
            success, message, imported_count = self.flexible_processor.import_flexible_csv(
                self.current_file_path,
                self.manual_mapping,
                self.encoding_var.get(),
                self.check_duplicates_var.get()
            )
            
            self.progress_var.set(100)
            
            if success:
                messagebox.showinfo("Import Complete", 
                                   f"Successfully imported {imported_count} rows.\n\n{message}")
                self.status_var.set(f"Import complete: {imported_count} rows imported")
                
                # Clear the form
                self.clear_form()
            else:
                messagebox.showerror("Import Failed", f"Import failed: {message}")
                self.status_var.set("Import failed")
            
            # Reset progress
            self.parent.after(3000, lambda: self.progress_var.set(0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Import error: {str(e)}")
            self.progress_var.set(0)
            self.status_var.set("Import failed")
    
    def clear_form(self):
        """Clear the form and reset to initial state"""
        self.file_path_var.set("")
        self.current_file_path = None
        self.preview_data = None
        self.detected_mapping = {}
        self.manual_mapping = {}
        
        # Clear mapping tree
        for item in self.mapping_tree.get_children():
            self.mapping_tree.delete(item)
        
        # Clear preview
        self.preview_text.delete(1.0, tk.END)
        
        # Reset combos
        self.field_var.set('')
        self.column_var.set('')
        self.column_combo['values'] = []
        
        # Reset status
        self.status_var.set("Ready to import")
        self.progress_var.set(0)
